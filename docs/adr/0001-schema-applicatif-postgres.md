# ADR 0001 — Role applicatif Postgres et nommage de son schema

- Statut : accepte
- Date : 2026-09-24
- Fichiers concernes : `infra/db/init/10-app-role.sh`, `docker-compose.yml`

## Contexte

L'API et le worker se connectent a Postgres avec un role applicatif
(`APP_DB_USER`, `sentinel_app` par defaut), jamais avec le superutilisateur
`POSTGRES_USER`. Un superutilisateur peut executer des commandes systeme
(`COPY ... FROM PROGRAM`) : une injection SQL cote API deviendrait une
execution de code dans le conteneur db.

Le role applicatif a besoin d'un schema a lui, pour que les migrations y
creent les tables. Les fonctions TimescaleDB (`time_bucket`,
`create_hypertable`...) vivent dans `public`.

## Le piege

Le `search_path` par defaut de Postgres est `"$user", public` : chaque role
cherche d'abord dans le schema qui porte son nom, puis dans `public`.

Si le schema applicatif porte **le nom du superutilisateur** (par exemple
`sentinel`, nom logique du projet), il passe devant `public` dans le
`search_path` de l'admin. Le role applicatif, proprietaire de ce schema, peut
alors y creer une fonction `time_bucket` qui masque celle de TimescaleDB et
execute `ALTER ROLE sentinel_app SUPERUSER`. Le premier appel a
`time_bucket` tape par un admin declenche l'escalade.

Ce scenario a ete reproduit sur la premiere version du script, qui nommait
le schema `sentinel`. Il suffit d'une injection SQL cote API pour poser le
piege.

## Decision

Trois barrieres independantes :

1. **Le schema applicatif porte le nom du role applicatif.** Il n'entre que
   dans le `search_path` de ce role (`"$user"`), jamais dans celui de l'admin.
2. **Le `search_path` du superutilisateur est fige a `public`**, sans
   `"$user"` : meme un schema au nom de l'admin ne serait pas consulte.
3. **Le script d'init verifie l'invariant** et echoue si un schema porte le
   nom d'un superutilisateur tout en appartenant a un role non
   superutilisateur. Il tourne a chaque `./scripts/dev.sh up` et dans le smoke
   test de la CI.

Le role applicatif n'a aucun droit `CREATE` sur `public` ni sur la base : il ne
peut creer ni fonction dans `public`, ni nouveau schema.

## Consequences

- **Ne pas renommer le schema** « proprement » en `sentinel` ou `app`, ni le
  sortir du nom du role. Le nom est une contrainte de securite, pas un choix
  esthetique. Si un autre nom est vraiment necessaire, il doit differer de
  tout superutilisateur, et l'invariant du script doit rester en place.
- **Ne jamais faire d'INSERT, UPDATE ou DELETE en superutilisateur sur les
  tables applicatives** : leurs triggers, ecrits par le role applicatif,
  s'executeraient avec les droits de l'appelant. Pour manipuler les donnees :
  `./scripts/dev.sh psql`, qui se connecte avec le role applicatif.
- Un `ALTER SCHEMA ... RENAME` dans une migration future ne serait detecte
  qu'au prochain `dev.sh up` ou smoke test : toute migration qui touche aux
  schemas doit citer cet ADR en revue.
