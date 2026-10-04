# Contribuer a Sentinel

## Demarrer

```bash
git clone <depot> && cd SentinelEIP
cp .env.example .env
for v in POSTGRES_PASSWORD APP_DB_PASSWORD REDIS_PASSWORD API_SECRET_KEY; do
  sed -i "s/^$v=$/$v=$(openssl rand -hex 32)/" .env
done
./scripts/dev.sh up            # l'api applique les migrations a son demarrage
```

Un secret vide fait echouer `docker compose` avec un message explicite.
Ensuite, creer un compte depuis le frontend ; dans `/docs`, le bouton
**Authorize** prend le jeton renvoye par `POST /auth/login`.

| Service  | URL                          |
| -------- | ---------------------------- |
| API      | http://localhost:8000/docs   |
| ML       | http://localhost:8100/docs   |
| Frontend | http://localhost:5173        |
| Postgres | `./scripts/dev.sh psql` (non publie) |

Tous les ports sont publies sur 127.0.0.1. Postgres et Redis ne sont pas
publies du tout, meme en dev : `./scripts/dev.sh psql` ouvre un psql avec le
role applicatif, `docker compose exec redis redis-cli` un client Redis
(authentifie via `REDISCLI_AUTH`). Sous Docker Desktop, l'hote ne voit pas les
IP des conteneurs : un tunnel SSH vers db n'a rien a viser.

Le schema Postgres porte le nom du role applicatif, et c'est une contrainte de
securite : ne pas le renommer, voir
[ADR 0001](docs/adr/0001-schema-applicatif-postgres.md). Les migrations
tournent avec ce role (`env.py` refuse le superutilisateur) ; un modele
SQLModel modifie s'accompagne d'une migration (`./scripts/dev.sh revision
"..."`), sinon `alembic check` fait echouer le smoke test de la CI.

**`.env` existant** (cree avant le role applicatif) : `docker compose` refuse de
demarrer tant que `APP_DB_PASSWORD` et `REDIS_PASSWORD` manquent. Les ajouter a
la main (`openssl rand -hex 32`), avec `APP_DB_USER=sentinel_app`, et verifier
que la ligne `API_SECRET_KEY=` ne porte pas de commentaire en fin de ligne : il
deviendrait la cle. `./scripts/dev.sh up` cree ensuite le role sur le volume
existant (`./scripts/dev.sh db-roles` le fait a la demande).

Commandes : `up`, `down`, `logs [service]`, `ps`, `migrate`, `revision "msg"`,
`test`, `lint`, `shell [service]`, `psql`, `db-roles`, `reset`.

## Branches et pull requests

Modele du dossier technique (`sentinel_deployment_cicd_plan.md`, section 4),
avec deux adaptations assumees, a reporter dans le dossier (voir
[ECARTS](docs/ECARTS.md), E9) : `dev` au lieu de `develop`, et `feat/`, `fix/`
(alignes sur les types de commit) au lieu de `feature/`.

- `main` — production ; build rouge interdit
- `dev` — integration, cible par defaut des PR
- `feat/<scope>-<sujet>`, `fix/<scope>-<sujet>` — travail courant
- `hotfix/*` — correctif urgent de production
- `release/*` — preparation de version (SemVer, tags `-rc`)
- `staging/*` — pre-production

Regles de PR (dossier, 4.2) : au moins une review, CI verte, squash merge sur
`dev` et `main`. Ces regles ne sont **pas encore imposees** par GitHub : `main`
et `dev` ne sont pas protegees (ECARTS, E8).

## Verifier avant de commiter et de pousser

```bash
scripts/verifier.sh                        # backend, ml, frontend, commits
scripts/verifier.sh message msg.txt && git commit -F msg.txt
scripts/verifier.sh titre "feat(api): ..." # titre de PR, avant de l'ouvrir
```

Memes etapes et meme environnement que la CI, qui lance d'ailleurs ce script
pour les commits. Chaque commit de la branche depuis `origin/dev` passe
commitlint avec la configuration du depot. Le script lance tout, affiche
chaque partie en vert ou en rouge, et sort en echec si une seule echoue :
`scripts/verifier.sh && git commit ...` ne commite jamais sur du rouge. Ne
jamais filtrer sa sortie avant le `&&` (`... | tail -1 && git commit`) : le
filtre rendrait son propre code. Une partie seulement : `scripts/verifier.sh
backend frontend`. Tout tourne dans des conteneurs, depot en lecture seule.
Son meta-test, `scripts/verifier-autotest.sh`, tourne en CI.

## Commits

Conventional Commits, verifies par `commitlint`. Le scope est **obligatoire**.
Avec le squash merge, c'est le **titre de la PR** qui devient le commit de
`dev` : il est verifie lui aussi, et reverifie a chaque renommage.

```
feat(risk): ajoute le plafond de pertes consecutives
fix(api): corrige le code 500 sur symbole inconnu
```

Scopes autorises : `frontend`, `api`, `auth`, `db`, `model`, `data`,
`strategy`, `broker`, `risk`, `core`, `infra`, `config`, `ci`, `cd`, `docs`,
`deps`, `repo`.

## Definition of Done

Une fonctionnalite est terminee quand :

- ses tests unitaires existent et passent ;
- ses cas d'erreur sont verifies ;
- son impact risque est couvert par un test ;
- son comportement est observable (metriques `/metrics`, logs structures) et
  trace dans les dashboards de test (`sentinel_testing_policy.md`, section 8) ;
- la CI est verte, sans exception.

Seuils de couverture, appliques par la CI : backend >= 70 % au global, et
>= 90 % pour chaque paquet critique declare dans `backend/pyproject.toml`
(`[tool.sentinel]`, aujourd'hui `app/risk` et `app/execution`) ; frontend
>= 60 % (`frontend/vite.config.ts`). Un nouveau module critique s'ajoute a
cette liste, pas ailleurs.

## Regles produit

Chaque regle indique sa source ; en cas de doute, le dossier technique fait foi.

**Issues du dossier technique** (`sentinel_solution_track_action_plan.md`,
US1.4 et US3.x ; `sentinel_technology_environment.md`, couches 4 et 5) :

1. **Nature des sorties : en suspens, a trancher en equipe.** Le dossier
   demande une tendance (US3.1) et un signal achat / vente / attente (US3.3) ;
   l'ancienne regle de ce fichier l'interdisait. Les deux positions sont
   exposees dans [ECARTS](docs/ECARTS.md), E10. En attendant, toute sortie
   affichee porte son niveau de confiance et son explication (US3.4), point
   commun aux deux positions.
2. **Le risk-governor a le dernier mot.** Aucun ordre ne part sans passer par
   ses garde-fous (drawdown, exposition, suspension, mode cash : couche 4), et
   l'execution est progressive : analyse seule, paper trading, puis reel
   encadre (US1.4, couche 5).

**Issues du design system v1.2** (`frontend/src/styles/tokens.css`, absent du
dossier) :

3. **`risk-critical` (rouge) est reserve au depassement d'un seuil de risque.**
   Un chiffre negatif ordinaire s'ecrit en `value-negative` ; aucun rouge ni
   vert reflexe sur les prix.
4. **L'etat « perime » se declenche sur le heartbeat de la connexion**, jamais
   sur l'absence de variation d'un prix.

**Decisions d'equipe absentes du dossier**, a y reporter ou a abandonner
(ECARTS, E9) :

5. **Tout score affiche porte sa fiabilite historique mesuree**, au-dela du
   simple niveau de confiance demande par le dossier.
6. **Durcir une regle de risque est immediat ; l'assouplir attend 24 h.**
   Les seuils d'alerte sont aujourd'hui fixes dans le code
   (`backend/app/risk/alerts.py`) : la regle s'appliquera quand ils deviendront
   reglables.

## Ecarts connus

Les limites acceptees ou en attente de decision sont dans
[docs/ECARTS.md](docs/ECARTS.md), avec leur symptome : si quelque chose casse
de facon inexpliquee, commencer par la. Ajouter une entree plutot que de
laisser un contournement sans trace.

## Secrets

Jamais dans le depot. `gitleaks` tourne sur chaque PR. Les variables passent
par `.env`, documente dans `.env.example`.
