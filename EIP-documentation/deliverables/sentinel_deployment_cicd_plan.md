# Plan CI/CD et Infrastructure - Sentinel

## 1) Objectif

Mettre en place une chaine CI/CD fiable et une infrastructure locale-first permettant a Sentinel de :
- livrer rapidement sans casser la production,
- garantir la tracabilite des decisions et des versions,
- renforcer la robustesse (priorite risque, pas performance brute),
- conserver le controle utilisateur et la maitrise des couts.

---

## 2) Hypotheses de stack (peut etre qu'on vas evoluer niveau techno)

- Backend API : FastAPI (Python)
- IA/ML : PyTorch, scikit-learn, pandas, numpy
- Frontend : React ou Next.js
- Base de donnees : PostgreSQL + TimescaleDB
- Asynchrone : Celery + Redis
- Reverse proxy : Nginx
- Conteneurisation : Docker + Docker Compose

---

## 3) Architecture cible

### 3.1 Services applicatifs

- data-ingestor : collecte OHLCV, volumes, news/eventuels flux macro
- indicator-engine : calcul d indicateurs techniques localement
- ai-analysts : modeles tendance/volatilite/anomalies/stress
- signal-synthesizer : agrege les sorties IA en signal comprehensible
- risk-governor : garde-fous (drawdown, reduction exposition, mode cash)
- execution-gateway : paper trading puis trading reel encadre
- api-gateway : API REST pour le frontend
- web-ui : interface locale navigateur

### 3.2 Services plateforme

- postgres-timescale : stockage historique et donnees metiers
- redis : broker Celery + cache
- nginx : reverse proxy + terminaison TLS locale
- monitoring : Prometheus + Grafana
- logs : Loki + Promtail (ou ELK selon contraintes)

### 3.3 Principe d isolation

- 1 service = 1 conteneur
- reseau Docker interne prive
- volumes persistants pour donnees critiques
- aucun secret dans le code source

---

## 4) Strategie Git et gouvernance de code

### 4.1 Branching model

- main : branche production
- develop : integration continue
- feature/* : nouvelles fonctionnalites
- hotfix/* : correctifs urgents production
- release/* : preparation de version
- staging/* : pre-production

### 4.2 Regles PR

- minimum 1 review obligatoire
- CI verte obligatoire avant merge
- squashed merge sur develop et main
- Conventional Commits

### 4.3 Versioning

- SemVer : MAJOR.MINOR.PATCH
- release candidate : tags -rc
- changelog genere automatiquement a partir des commits

---

## 5) Plan CI (integration continue)

Declencheurs :
- pull_request sur develop et main
- push sur develop

Etapes CI :

1. Validation rapide
- format/lint backend et frontend
- type checking
- verification schema de config

2. Tests
- unit tests backend
- unit tests frontend
- integration tests (API + DB + Redis)
- smoke test du pipeline de donnees
- smoke test risk-governor

3. Qualite IA
- test de derive simple sur dataset de reference
- test de stabilite signal (non-regression)
- seuils de performance minimaux

4. Securite
- scan de secrets (gitleaks)
- scan dependances (pip-audit, npm audit)
- scan image conteneur (trivy)

5. Build et artefacts
- build images Docker versionnees
- generation SBOM
- publication artefacts (rapports tests, couverture, scans)

Quality gates minimaux :
- tous les tests critiques passent
- couverture globale >= 70% (progressive vers 80%)
- aucun secret detecte
- aucune vulnerabilite critique non justifiee

---

## 6) Plan CD (deploiement continu)

### 6.1 Environnements

- local-dev : developpement individuel (compose)
- shared-dev : environnement equipe auto-deploy
- staging : pre-production proche prod
- prod : execution reelle controlee

### 6.2 Strategie de deploiement

release/* ou avec tag  -> deploy dans staging
tag stable sur main -> deploy prod apres approbation manuelle

### 6.3 Sequence de deploiement

1. pull image versionnee
2. migration base (Alembic) avec verrou de securite
3. demarrage progressif des services
4. health checks applicatifs et metiers

### 6.4 Rollback

- conserver N images precedentes
- rollback automatique si health check KO
- rollback manuel possible en 1 commande (1 script)
- procedure ecrite et testee (game day mensuel)

---

## 7) Infrastructure as Code et configuration

### 7.1 Depot infra (a regarder encore)

Mono-repo avec dossier infra

Arborescence conseillee :

- .github/workflows/
- infra/docker/
- infra/compose/
- infra/nginx/
- infra/monitoring/
- scripts/
- app/

### 7.2 Secrets et variables

- fichier .env.example versionne
- secrets reels hors Git (Vault, 1Password, Doppler, ou SOPS)
- rotation planifiee des cles API
- chiffrement au repos des secrets locaux

---

## 8) Observabilite, SLO et exploitation

### 8.1 Metriques techniques

- disponibilite API
- latence endpoints critiques
- taux d erreur 5xx
- temps de traitement des jobs Celery

### 8.2 Metriques metier

- frequence signaux
- ecart entre signal et execution

### 8.3 Alerting

- seuil drawdown critique depasse
- echec ingestion donnees > X minutes
- desynchronisation modules IA / risk-governor
- erreur d execution repetee

---

## 9) Roadmap de mise en oeuvre (12 semaines)

### Phase 0 (S1-S2) - Fondations

- finaliser conventions Git, PR templates, codeowners
- definir environnements et naming
- creer base Docker Compose multi-services

### Phase 1 (S3-S4) - CI Baseline

- lint + unit tests + integration tests
- couverture et rapports automatiques
- quality gates minimaux

### Phase 2 (S5-S6) - Securite et conformite

- scans secrets/dependances/images
- SBOM et politique de correction
- signature des images

### Phase 3 (S7-S8) - CD Dev/Staging

- deploiement auto shared-dev et staging
- migrations automatisees + health checks
- rollback script et validation

### Phase 4 (S9-S10) - Hardening Production

- approvals manuelles prod
- runbooks incidents et astreinte legere
- tests de reprise et scenarios de panne

### Phase 5 (S11-S12) - Observabilite complete

- dashboards Grafana (tech + metier)
- alerting structure
- exercice game day de bout en bout

---

## 10) Definition of Done CI/CD

Le dispositif est considere operationnel quand :
- toute PR passe par CI complete en moins de 15 min,
- tout deploiement staging est automatisable sans action manuelle,
- le deploiement prod est reproductible, trace et reversible,
- les alertes critiques sont testees et actionnables,
- un incident type est resolu via runbook en moins de 30 min.

---

## 11) Prochaines actions immediates

1. Creer les workflows CI de base (backend/frontend/securite)
2. Ajouter la stack compose complete avec healthchecks
3. Definir les seuils de tests et de qualite obligatoires
4. Creer le pipeline CD shared-dev puis staging
5. Ecrire et tester la procedure de rollback
