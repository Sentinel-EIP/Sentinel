# Sauvegardes des services cloud

Les services cloud tournent sur le **poste fixe**, pas sur le VPS. Le script
de sauvegarde du VPS ne les couvre donc pas.

Une sauvegarde sur la machine qu'elle sauvegarde n'est pas une sauvegarde :
ce script pousse vers le meme Backblaze B2 que le VPS.

## Installation sur le poste fixe

```bash
# rclone, meme remote que sur le VPS
curl https://rclone.org/install.sh | sudo bash
rclone config      # remote "b2", backend b2, memes keyID / applicationKey
rclone lsd b2:

# age, pour chiffrer les archives avant envoi
sudo apt install age
```

## Cle de chiffrement

La paire de cles age se genere **hors du poste fixe** : si le poste est
compromis ou perdu, les sauvegardes doivent rester illisibles et restaurables.

```bash
age-keygen -o sentinel-backup.key     # cle privee : gestionnaire de mots de passe
age-keygen -y sentinel-backup.key     # cle publique age1... -> AGE_RECIPIENT
```

Seule la cle **publique** va sur le poste fixe.

## Script

`scripts/backup-cloud.sh` du depot. Le poser dans `~/backup/` sur le poste
fixe, `chmod 700`, puis :

```bash
cp scripts/backup-cloud.env.example ~/backup/backup-cloud.env
chmod 600 ~/backup/backup-cloud.env
nano ~/backup/backup-cloud.env        # BACKUP_REMOTE, AGE_RECIPIENT, CLOUD_ENV_FILE
~/backup/backup-cloud.sh --dry-run
```

Sans configuration complete, ou sans `age`, le script s'arrete avant de
produire la moindre archive.

Ce qu'il sauvegarde :

| Element                 | Methode                              | Volumetrie |
| ----------------------- | ------------------------------------ | ---------- |
| Base Nextcloud          | pg_dumpall, chiffre age              | faible     |
| Fichiers Nextcloud      | tar du volume, chiffre age, **hebdomadaire** | peut etre lourde |
| Config Nextcloud        | tar de config/, chiffre age          | faible     |
| Fichier .env            | tar, chiffre age                     | faible     |
| Buckets MinIO           | rclone sync direct vers B2, **non chiffre** (1) | variable   |

(1) Choix assume : les buckets peuvent contenir des pieces jointes. Pour les
chiffrer, declarer un remote rclone `crypt` au-dessus de B2 et le viser a la
place de `$BACKUP_REMOTE/minio/`.

Les archives sont chiffrees en flux : aucune version en clair n'est ecrite
sur le disque du poste fixe. Seuls les fichiers `*.age` sont envoyes ; ceux
d'un envoi rate la veille repartent au passage suivant.

Les fichiers utilisateurs sont sauvegardes **une fois par semaine** et non
chaque nuit : une archive complete quotidienne saturerait les 10 Go gratuits
de B2 en quelques jours. Les bases, elles, partent toutes les nuits.

## Cron

```
0 3 * * *   $HOME/backup/backup-cloud.sh
0 4 * * 0   $HOME/backup/backup-cloud.sh --full
```

## Restauration — a tester une fois

Une sauvegarde jamais restauree n'est pas une sauvegarde. Recuperer un dump
et le restaurer dans un Postgres jetable pour verifier qu'il est lisible :

```bash
rclone copy "$BACKUP_REMOTE/<AAAA>/<MM>/<JJ>/" ./restore/
age -d -i sentinel-backup.key restore/nextcloud-db-<STAMP>.sql.gz.age | gunzip > dump.sql
age -d -i sentinel-backup.key restore/env-<STAMP>.tgz.age | tar tzf -
```
