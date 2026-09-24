#!/usr/bin/env bash
# Sauvegarde des services cloud du poste fixe vers un remote rclone (B2).
#
#   backup-cloud.sh            quotidien : bases + configs
#   backup-cloud.sh --full     hebdomadaire : + fichiers utilisateurs
#   backup-cloud.sh --dry-run  n'ecrit rien
#
# Configuration : $BACKUP_CONFIG, par defaut ~/backup/backup-cloud.env
# (modele : scripts/backup-cloud.env.example).
#
# Tout ce qui est archive ici est chiffre avec age AVANT d'etre ecrit sur
# disque puis envoye : dump de la base, config Nextcloud (elle contient le mot
# de passe de la base et le secret d'instance), fichier .env, fichiers
# utilisateurs. La cle privee age ne doit pas etre sur ce poste.
# Seule exception : la synchro des buckets MinIO, envoyee telle quelle (voir plus bas).
set -uo pipefail

DRY=0; FULL=0
for a in "$@"; do
  [ "$a" = "--dry-run" ] && DRY=1
  [ "$a" = "--full" ] && FULL=1
done

CONFIG="${BACKUP_CONFIG:-$HOME/backup/backup-cloud.env}"
# shellcheck source=/dev/null
[ -f "$CONFIG" ] && . "$CONFIG"

WORK="${BACKUP_WORK:-$HOME/backup}"
STAGE="$WORK/stage-cloud"
LOG="$WORK/backup-cloud.log"
KEEP_LOCAL_DAYS=2
KEEP_REMOTE_DAYS=30

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
DAY="$(date -u +%Y/%m/%d)"
mkdir -p "$STAGE"
exec > >(tee -a "$LOG") 2>&1
echo "===== $STAMP  cloud (dry-run=$DRY full=$FULL) ====="

die() { echo "ARRET : $*"; exit 1; }

# ----------------------------------------------- configuration et chiffrement
# Aucune valeur par defaut : sans configuration complete, rien ne part.
[ -n "${BACKUP_REMOTE:-}" ]  || die "BACKUP_REMOTE manquant (voir $CONFIG)"
[ -n "${AGE_RECIPIENT:-}" ]  || die "AGE_RECIPIENT manquant (voir $CONFIG)"
[ -n "${CLOUD_ENV_FILE:-}" ] || die "CLOUD_ENV_FILE manquant (voir $CONFIG)"
REMOTE="$BACKUP_REMOTE"
command -v age >/dev/null || die "age introuvable : sudo apt install age"
printf 'test' | age -r "$AGE_RECIPIENT" >/dev/null 2>&1 \
  || die "AGE_RECIPIENT n'est pas une cle publique age valide"

FAILED=0
note_fail() { echo "ECHEC : $*"; FAILED=1; }

# Chiffre la sortie standard d'une commande vers $STAGE/<nom>.age.
# Le fichier partiel est supprime en cas d'echec, la taille est affichee sinon.
save_encrypted() {
  local out="$STAGE/$1.age"; shift
  if "$@" | age -r "$AGE_RECIPIENT" > "$out"; then
    echo "   ok, $(numfmt --to=iec "$(stat -c%s "$out")") chiffres"
    return 0
  fi
  rm -f "$out"
  return 1
}

# Nom reel d'un volume monte dans le conteneur Nextcloud. Compose prefixe les
# volumes par le nom du projet : on le lit sur le conteneur plutot que de le
# deviner (un `docker run -v nom:` errone creerait un volume vide).
nc_volume() {
  docker inspect -f "{{range .Mounts}}{{if eq .Destination \"$1\"}}{{.Name}}{{end}}{{end}}" \
    cloud-nextcloud 2>/dev/null
}

dump_db() {
  docker exec cloud-nextcloud-db sh -c 'pg_dumpall -U "$POSTGRES_USER" --clean --if-exists' \
    2>/dev/null | gzip
}
tar_volume() {   # tar_volume <volume> <chemin dans le volume>
  docker run --rm -v "$1":/src:ro alpine tar czf - -C /src "$2" 2>/dev/null
}
tar_env() {
  tar czf - -C "$(dirname "$CLOUD_ENV_FILE")" "$(basename "$CLOUD_ENV_FILE")"
}

# ------------------------------------------------------- base Nextcloud
if docker ps --format '{{.Names}}' | grep -qx cloud-nextcloud-db; then
  echo "-- dump de la base nextcloud"
  if [ "$DRY" = "1" ]; then
    echo "[dry-run] pg_dumpall | age -> $STAGE/nextcloud-db-$STAMP.sql.gz.age"
  elif save_encrypted "nextcloud-db-$STAMP.sql.gz" dump_db; then
    sz=$(stat -c%s "$STAGE/nextcloud-db-$STAMP.sql.gz.age")
    if [ "$sz" -lt 1000 ]; then
      note_fail "dump suspect ($sz octets)"
      rm -f "$STAGE/nextcloud-db-$STAMP.sql.gz.age"
    fi
  else
    note_fail "pg_dumpall nextcloud"
  fi
else
  note_fail "conteneur cloud-nextcloud-db absent"
fi

HTML_VOL="$(nc_volume /var/www/html)"
DATA_VOL="$(nc_volume /var/www/html/data)"

# ------------------------------------------- configuration Nextcloud
echo "-- config nextcloud"
if [ -z "$HTML_VOL" ]; then
  note_fail "volume /var/www/html introuvable (conteneur cloud-nextcloud absent ?)"
elif [ "$DRY" = "1" ]; then
  echo "[dry-run] tar $HTML_VOL:config | age -> $STAGE/nextcloud-config-$STAMP.tgz.age"
else
  save_encrypted "nextcloud-config-$STAMP.tgz" tar_volume "$HTML_VOL" config \
    || note_fail "tar config nextcloud"
fi

# --------------------------------- fichiers utilisateurs (hebdomadaire)
if [ "$FULL" = "1" ]; then
  echo "-- fichiers utilisateurs nextcloud (complet)"
  if [ -z "$DATA_VOL" ]; then
    note_fail "volume /var/www/html/data introuvable (conteneur cloud-nextcloud absent ?)"
  elif [ "$DRY" = "1" ]; then
    echo "[dry-run] tar $DATA_VOL | age -> $STAGE/nextcloud-data-$STAMP.tgz.age"
  else
    save_encrypted "nextcloud-data-$STAMP.tgz" tar_volume "$DATA_VOL" . \
      || note_fail "tar data nextcloud"
  fi
else
  echo "-- fichiers utilisateurs : ignores (lancer avec --full)"
fi

# ------------------------------------------------------------- .env
echo "-- fichier .env de la stack cloud"
# Droits trop larges : signale en echec, mais sauvegarde quand meme (chiffree).
# Pas de correction automatique : ce fichier n'appartient pas a ce script.
if [ -f "$CLOUD_ENV_FILE" ]; then
  case "$(ls -l "$CLOUD_ENV_FILE")" in
    -rw-------*|-r--------*) ;;
    *) note_fail "$CLOUD_ENV_FILE lisible par d'autres comptes : chmod 600 \"$CLOUD_ENV_FILE\"" ;;
  esac
fi
if [ ! -f "$CLOUD_ENV_FILE" ]; then
  note_fail "$CLOUD_ENV_FILE introuvable"
elif [ "$DRY" = "1" ]; then
  echo "[dry-run] tar $CLOUD_ENV_FILE | age -> $STAGE/env-$STAMP.tgz.age"
else
  save_encrypted "env-$STAMP.tgz" tar_env || note_fail "tar .env"
fi

# ------------------------------------------------------ envoi vers B2
# Seuls les fichiers chiffres partent : un fichier en clair laisse dans $STAGE
# par une ancienne version du script n'est jamais envoye. Les .age des jours
# precedents encore en stage sont renvoyes, ce qui rattrape un envoi rate.
if [ -n "$(find "$STAGE" -maxdepth 1 -type f ! -name '*.age' -print -quit)" ]; then
  echo "   ATTENTION : fichiers non chiffres dans $STAGE (ignores, a supprimer)"
fi
echo "-- envoi vers $REMOTE/$DAY/"
if [ "$DRY" = "1" ]; then
  echo "[dry-run] rclone copy $STAGE (*.age) -> $REMOTE/$DAY/"
else
  rclone copy "$STAGE" "$REMOTE/$DAY/" --include "*.age" \
    --transfers 2 --stats-one-line \
    || note_fail "rclone copy"
fi

# ------------------------- buckets MinIO : sync direct, pas de tar
# Evite de dupliquer des giga-octets a chaque passage. NON CHIFFRE : choix
# assume et documente (docs/SAUVEGARDES.md) ; les buckets peuvent contenir des
# pieces jointes. Pour chiffrer, remplacer la cible par un remote rclone "crypt".
echo "-- sync des buckets minio"
if [ "$DRY" = "1" ]; then
  echo "[dry-run] rclone sync minio: -> $REMOTE/minio/"
elif rclone lsd minio: >/dev/null 2>&1; then
  rclone sync minio: "$REMOTE/minio/" --transfers 4 --stats-one-line \
    || note_fail "rclone sync minio"
else
  echo "   remote rclone 'minio' non configure — voir docs/SAUVEGARDES.md"
fi

# -------------------------------------------------------- retention
[ "$DRY" = "0" ] && find "$STAGE" -type f -mtime +"$KEEP_LOCAL_DAYS" -delete
echo "-- purge distante au-dela de $KEEP_REMOTE_DAYS jours"
if [ "$DRY" = "0" ]; then
  rclone delete --min-age "${KEEP_REMOTE_DAYS}d" "$REMOTE/$(date -u +%Y)" 2>/dev/null || true
fi

echo "-- disque : $(df -h / | awk 'NR==2{print $5" utilise, "$4" libre"}')"
[ "$FAILED" = "1" ] && { echo "===== TERMINE AVEC DES ECHECS ====="; exit 1; }
echo "===== $STAMP  termine sans erreur ====="
