#!/bin/sh
# Role applicatif NON superutilisateur, utilise par api et worker.
# Le superutilisateur POSTGRES_USER reste confine au conteneur db : il n'est
# transmis a aucun service applicatif (un superutilisateur peut executer des
# commandes systeme via COPY ... FROM PROGRAM).
#
# Joue automatiquement a l'initialisation d'un volume neuf
# (docker-entrypoint-initdb.d). Idempotent : `./scripts/dev.sh db-roles` le
# rejoue sur un volume existant et resynchronise le mot de passe.
#
# Le schema applicatif porte le nom du role : il n'entre que dans le
# search_path de ce role ("$user", public). Un schema au nom du
# superutilisateur passerait devant public dans SON search_path, et le role
# applicatif pourrait y masquer une fonction TimescaleDB (escalade de droits).
# Pour la meme raison : ne jamais faire de DML en superutilisateur sur les
# tables applicatives (leurs triggers s'executeraient avec ses droits).
set -eu
: "${APP_DB_USER:?APP_DB_USER manquant}"
: "${APP_DB_PASSWORD:?APP_DB_PASSWORD manquant}"
if [ "$APP_DB_USER" = "$POSTGRES_USER" ]; then
  echo "10-app-role : APP_DB_USER doit differer de POSTGRES_USER" >&2
  exit 1
fi

# Les secrets passent par l'environnement (\getenv), pas par la ligne de
# commande de psql, et une erreur ne journalise pas la requete fautive.
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<'SQL'
SET search_path = pg_catalog;
SET log_min_error_statement = panic;
\getenv app_user APP_DB_USER
\getenv app_pw APP_DB_PASSWORD
\getenv db POSTGRES_DB

SELECT format('CREATE ROLE %I LOGIN', :'app_user')
 WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = :'app_user') \gexec
ALTER ROLE :"app_user" WITH LOGIN PASSWORD :'app_pw'
      NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;

REVOKE ALL ON DATABASE :"db" FROM PUBLIC;
GRANT CONNECT, TEMPORARY ON DATABASE :"db" TO :"app_user";

-- Le role applicatif possede son schema (tables creees par les migrations)
-- mais ne peut rien creer dans public, ou vivent les fonctions TimescaleDB.
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
CREATE SCHEMA IF NOT EXISTS :"app_user" AUTHORIZATION :"app_user";
SQL
echo "10-app-role : role $APP_DB_USER pret (non superutilisateur, schema $APP_DB_USER)"
