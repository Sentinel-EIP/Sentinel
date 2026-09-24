# Sentinel

**Plateforme d'aide a la decision d'investissement, locale-first et orientee risque**

Sentinel est un projet EIP centre sur la robustesse, la transparence et le
controle utilisateur. Le projet combine :

- analyse de marche (indicateurs techniques + modeles IA),
- synthese de signaux comprehensibles,
- gouvernance stricte du risque (drawdown, exposition, mode cash),
- execution progressive (analyse seule -> paper trading -> execution reelle encadree).

## Fonctionnalites cles

- **Architecture modulaire** : ingestion donnees, analyse IA, synthese, risk governor, execution, interface.
- **Approche local-first** : limitation de la dependance cloud et meilleure maitrise des donnees.
- **IA explicable** : recommandations tracables et auditables.
- **Resilience** : mode degrade et continuite de service en cas de panne d'un module.

## Demarrage rapide

```bash
cp .env.example .env    # remplir POSTGRES_PASSWORD et API_SECRET_KEY
./scripts/dev.sh up
```

API sur http://localhost:8000/docs, frontend sur http://localhost:5173.
Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour les commandes et conventions.

## Stack

| Couche        | Technologies                                        |
| ------------- | --------------------------------------------------- |
| Backend       | Python 3.11, FastAPI, SQLModel, Alembic, Celery      |
| Donnees       | PostgreSQL 16 + TimescaleDB, Redis                   |
| IA / ML       | PyTorch, scikit-learn, pandas-ta, transformers       |
| Frontend      | React 19, Vite, Zustand, TradingView Lightweight Charts |
| Infra         | Docker, Docker Compose, Nginx                        |
| Observabilite | Prometheus, Grafana, Loki (phase ulterieure)         |

## Structure du repository

```
backend/     API FastAPI, workers Celery, migrations   (api, auth, db, core, risk)
ml/          service des modeles IA, image separee     (model, data)
frontend/    interface React + design system v1.2      (frontend)
infra/       Dockerfiles, configuration Nginx          (infra, config)
scripts/     dev.sh, point d'entree unique             (infra)
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
| Shared Dev    | equipe, deploiement auto depuis `develop`   |
| Staging       | miroir de production, validation des RC     |
| Production    | execution stable, sauvegardes et alerting   |
