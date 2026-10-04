#!/usr/bin/env bash
# Initialise Garage, une seule fois, apres le premier `docker compose up -d` :
# role du noeud unique, buckets, et deux cles d'acces.
#   - sentinel-app    : lecture/ecriture, pour les applications ;
#   - sentinel-backup : lecture seule, pour rclone (scripts/backup-cloud.sh).
# Les secrets des cles ne s'affichent qu'ici : les ranger aussitot dans le
# gestionnaire de mots de passe (retrouvables avec `garage key info --show-secret`).
#
#   ./garage-init.sh [capacite]      capacite annoncee du noeud, defaut 100G
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

CAPACITY="${1:-100G}"
BUCKETS="sentinel-models sentinel-datasets sentinel-artifacts"
# Surchargeable pour les tests : GARAGE_CMD="docker exec <conteneur> /garage"
read -r -a GARAGE <<< "${GARAGE_CMD:-docker compose exec -T garage /garage}"
garage() { "${GARAGE[@]}" "$@"; }

first="${BUCKETS%% *}"
if garage bucket info "$first" > /dev/null 2>&1; then
  echo "Garage deja initialise (bucket $first present) : rien a faire."
  exit 0
fi

node="$(garage node id -q | cut -d@ -f1)"
echo "-- role du noeud ${node:0:16} (capacite $CAPACITY)"
garage layout assign -z poste-fixe -c "$CAPACITY" "$node"
garage layout apply --version 1

garage key create sentinel-app
garage key create sentinel-backup
for b in $BUCKETS; do
  echo "-- bucket $b"
  garage bucket create "$b"
  garage bucket allow --read --write --owner "$b" --key sentinel-app
  garage bucket allow --read "$b" --key sentinel-backup
done

echo
echo "Garage pret. Garage ne versionne pas les objets : l'historique vient des"
echo "sauvegardes (docs/SAUVEGARDES.md)."
