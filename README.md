# SENTINEL

**Plateforme d'aide à la décision d'investissement, locale-first et orientée risque**


Sentinel est un projet EIP centre sur la robustesse, la transparence et le
controle utilisateur. Le projet combine :

- analyse de marche (indicateurs techniques + modeles IA),
- synthese de signaux comprehensibles,
- gouvernance stricte du risque (drawdown, exposition, mode cash),
- exécution progressive (analyse seule -> paper trading -> exécution réelle encadrée).

## Fonctionnalités clés

- **Architecture modulaire** : ingestion données, analyse IA, synthèse, risk governor, exécution, interface.
- **Approche local-first** : limitation de la dépendance cloud et meilleure maîtrise des données.
- **IA explicable** : recommandations traçables et auditables.
- **Résilience** : mode dégradé et continuité de service en cas de panne d'un module.

## Demarrage rapide

```bash
cp .env.example .env
for v in POSTGRES_PASSWORD APP_DB_PASSWORD REDIS_PASSWORD API_SECRET_KEY; do
  sed -i "s/^$v=$/$v=$(openssl rand -hex 32)/" .env
done
./scripts/dev.sh up            # l'api applique les migrations a son demarrage
```

API sur http://localhost:8000/docs, frontend sur http://localhost:5173 : creer
un compte depuis l'ecran de connexion. Les bougies BTCEUR et ETHEUR arrivent
dans la minute (collecte au demarrage du worker, puis tous les quarts d'heure).
Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour les commandes et conventions.

## API

Toutes les routes, sauf `/health*` et `/auth/*`, exigent un jeton
(`Authorization: Bearer ...`, obtenu par `/auth/login`).

| Route                         | Role                                              |
| ----------------------------- | ------------------------------------------------- |
| `POST /auth/register`, `/auth/login` | inscription, connexion (JWT)               |
| `GET /users/me`, `/users/me/activity` | compte et journal d'actions               |
| `GET /market/symbols`, `/market/candles` | historique de marche (TimescaleDB)     |
| `POST /analysis/volatility`   | cone de volatilite (service ML), enregistre       |
| `GET /analysis/results`       | historique des resultats IA                       |
| `GET /risk/summary`, `/alerts` | volatilite, drawdowns, alertes de seuil          |

Services : `api`, `worker` (collecte, jobs), `scheduler` (planification),
`ml` (modeles), `db` (PostgreSQL + TimescaleDB), `redis`, `frontend`, `proxy`.

## Stack

| Couche        | Technologies                                        |
| ------------- | --------------------------------------------------- |
| Backend       | Python 3.11, FastAPI, SQLModel, Alembic, Celery      |
| Donnees       | PostgreSQL 16 + TimescaleDB, Redis                   |
| IA / ML       | PyTorch, scikit-learn, ta, transformers              |
| Frontend      | React 19, Vite, Zustand, TradingView Lightweight Charts |
| Infra         | Docker, Docker Compose, Nginx                        |
| Observabilite | Prometheus, Grafana, Loki (phase ulterieure)         |

## Structure du repository

```
backend/     API FastAPI, workers Celery, migrations   (api, auth, db, core, risk)
ml/          service des modeles IA, image separee     (model, data)
frontend/    interface React + design system v1.2      (frontend)
infra/       Dockerfiles, configuration Nginx          (infra, config)
scripts/     dev.sh, point d'entree unique ; ci/        (infra)
docs/        adr/, deploiement, sauvegardes, ECARTS.md  (docs)
.github/     CI : lint, tests, securite, build         (ci, cd)
EIP-documentation/
  deliverables/        livrables rediges du projet
  workshops/guides/    supports atelier en markdown
  workshops/pdfs/      PDFs de reference et supports officiels
  context/             contexte projet
```

Le service ML est volontairement separe du backend : ses dependances pesent
environ 2 Go, et les melanger imposerait ce poids a chaque rebuild de l'API.

## Environnements

| Environnement | Usage                                      |
| ------------- | ------------------------------------------ |
| Local Dev     | poste developpeur, `docker-compose.dev.yml` |
| Shared Dev    | equipe, deploiement auto depuis `dev`       |
| Staging       | miroir de production, validation des RC     |
| Production    | execution stable, sauvegardes et alerting   |


La documentation est centralisée dans `EIP-documentation/` :
- `EIP-documentation/deliverables/` : livrables rédigés du projet
- `EIP-documentation/workshops/guides/` : supports atelier en markdown
- `EIP-documentation/workshops/pdfs/` : PDFs de référence et supports officiels
- `EIP-documentation/context/` : contexte projet
