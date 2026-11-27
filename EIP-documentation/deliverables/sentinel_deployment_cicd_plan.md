# Plan CI/CD et infrastructure — SENTINEL

## 1) Objectif

Mettre en place une chaîne CI/CD fiable et une infrastructure locale-first permettant à Sentinel de :
- livrer rapidement sans casser la production,
- garantir la traçabilité des décisions et des versions,
- renforcer la robustesse (priorité risque, pas performance brute),
- conserver le contrôle utilisateur et la maîtrise des coûts.

## 2) Hypothèses de stack (peut-être qu'on va évoluer niveau techno)

- Backend API : FastAPI (Python)
- IA/ML : PyTorch, scikit-learn, pandas, numpy
- Frontend : React ou Next.js
- Base de données : PostgreSQL + TimescaleDB
- Asynchrone : Celery + Redis
- Reverse proxy : Nginx
- Conteneurisation : Docker + Docker Compose

## 3) Architecture cible

### 3.1 Services applicatifs

- data-ingestor : collecte OHLCV, volumes, news/éventuels flux macro
- indicator-engine : calcul d'indicateurs techniques localement
- ai-analysts : modèles tendance/volatilité/anomalies/stress
- signal-synthesizer : agrège les sorties IA en signal compréhensible
- risk-governor : garde-fous (drawdown, réduction exposition, mode cash)
- execution-gateway : paper trading puis trading réel encadré
- api-gateway : API REST pour le frontend
- web-ui : interface locale navigateur

### 3.2 Services plateforme

- postgres-timescale : stockage historique et données métiers
- redis : broker Celery + cache
- nginx : reverse proxy + terminaison TLS locale
- monitoring : Prometheus + Grafana
- logs : Loki + Promtail (ou ELK selon contraintes)

### 3.3 Principe d'isolation

- 1 service = 1 conteneur
- réseau Docker interne privé
- volumes persistants pour données critiques
- aucun secret dans le code source

## 4) Stratégie Git et gouvernance de code

### 4.1 Branching model

- main : branche production
- develop : intégration continue
- feature/* : nouvelles fonctionnalités
- hotfix/* : correctifs urgents production
- release/* : préparation de version
- staging/* : pré-production

### 4.2 Règles PR

- minimum 1 review obligatoire
- CI verte obligatoire avant merge
- squashed merge sur develop et main
- Conventional Commits

### 4.3 Versioning

- SemVer : MAJOR.MINOR.PATCH
- release candidate : tags -rc
- changelog généré automatiquement à partir des commits

## 5) Plan CI (intégration continue)

Déclencheurs :
- pull_request sur develop et main
- push sur develop

Étapes CI :

1. Validation rapide
- format/lint backend et frontend
- type checking
- vérification schéma de config

2. Tests
- unit tests backend
- unit tests frontend
- integration tests (API + DB + Redis)
- smoke test du pipeline de données
- smoke test risk-governor

3. Qualité IA
- test de dérive simple sur dataset de référence
- test de stabilité signal (non-régression)
- seuils de performance minimaux

4. Sécurité
- scan de secrets (gitleaks)
- scan dépendances (pip-audit, npm audit)
- scan image conteneur (trivy)

5. Build et artefacts
- build images Docker versionnées
- génération SBOM
- publication artefacts (rapports tests, couverture, scans)

Quality gates minimaux :
- tous les tests critiques passent
- couverture globale >= 70% (progressive vers 80%)
- aucun secret détecté
- aucune vulnérabilité critique non justifiée

## 6) Plan CD (déploiement continu)

### 6.1 Environnements

- local-dev : développement individuel (compose)
- shared-dev : environnement équipe auto-deploy
- staging : pré-production proche prod
- prod : exécution réelle contrôlée

### 6.2 Stratégie de déploiement

release/* ou avec tag  -> deploy dans staging
tag stable sur main -> deploy prod après approbation manuelle

### 6.3 Séquence de déploiement

1. pull image versionnée
2. migration base (Alembic) avec verrou de sécurité
3. démarrage progressif des services
4. health checks applicatifs et métiers

### 6.4 Rollback

- conserver N images précédentes
- rollback automatique si health check KO
- rollback manuel possible en 1 commande (1 script)
- procédure écrite et testée (game day mensuel)

## 7) Infrastructure as Code et configuration

### 7.1 Dépôt infra (à regarder encore)

Mono-repo avec dossier infra

Arborescence conseillée :

- .github/workflows/
- infra/docker/
- infra/compose/
- infra/nginx/
- infra/monitoring/
- scripts/
- app/

### 7.2 Secrets et variables

- fichier .env.example versionné
- secrets réels hors Git (Vault, 1Password, Doppler, ou SOPS)
- rotation planifiée des clés API
- chiffrement au repos des secrets locaux

## 8) Observabilité, SLO et exploitation

### 8.1 Métriques techniques

- disponibilité API
- latence endpoints critiques
- taux d'erreur 5xx
- temps de traitement des jobs Celery

### 8.2 Métriques métier

- fréquence signaux
- écart entre signal et exécution

### 8.3 Alerting

- seuil drawdown critique dépassé
- échec ingestion données > X minutes
- désynchronisation modules IA / risk-governor
- erreur d'exécution répétée

## 9) Roadmap de mise en œuvre (12 semaines)

### Phase 0 (S1-S2) — Fondations

- finaliser conventions Git, PR templates, codeowners
- définir environnements et naming
- créer base Docker Compose multi-services

### Phase 1 (S3-S4) — CI baseline

- lint + unit tests + integration tests
- couverture et rapports automatiques
- quality gates minimaux

### Phase 2 (S5-S6) — Sécurité et conformité

- scans secrets/dépendances/images
- SBOM et politique de correction
- signature des images

### Phase 3 (S7-S8) — CD dev/staging

- déploiement auto shared-dev et staging
- migrations automatisées + health checks
- rollback script et validation

### Phase 4 (S9-S10) — Hardening production

- approvals manuelles prod
- runbooks incidents et astreinte légère
- tests de reprise et scénarios de panne

### Phase 5 (S11-S12) — Observabilité complète

- dashboards Grafana (tech + métier)
- alerting structuré
- exercice game day de bout en bout

## 10) Definition of Done CI/CD

Le dispositif est considéré opérationnel quand :
- toute PR passe par CI complète en moins de 15 min,
- tout déploiement staging est automatisable sans action manuelle,
- le déploiement prod est reproductible, tracé et réversible,
- les alertes critiques sont testées et actionnables,
- un incident type est résolu via runbook en moins de 30 min.

## 11) Prochaines actions immédiates

1. Créer les workflows CI de base (backend/frontend/sécurité)
2. Ajouter la stack compose complète avec healthchecks
3. Définir les seuils de tests et de qualité obligatoires
4. Créer le pipeline CD shared-dev puis staging
5. Écrire et tester la procédure de rollback
