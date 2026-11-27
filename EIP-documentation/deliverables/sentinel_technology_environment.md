# Environnement technologique — SENTINEL

## 1) Vision technique

Sentinel est conçu comme une plateforme locale-first, modulaire et explicable pour l'aide à la décision et l'exécution disciplinée en investissement.

Objectifs techniques :
- robustesse et maîtrise du risque,
- traçabilité complète des données et décisions,
- indépendance maximale vis-à-vis du cloud,
- déploiement reproductible sur poste local ou serveur dédié.

## 2) Stack cible

### 2.1 Backend

- Python 3.11+
- FastAPI (API REST)
- Uvicorn/Gunicorn
- Celery (jobs asynchrones)

### 2.2 Data et stockage

- PostgreSQL 16+
- Extension TimescaleDB (séries temporelles)
- Redis (cache/broker)

### 2.3 IA/ML

- PyTorch
- scikit-learn
- pandas, numpy
- TA-Lib ou pandas-ta pour indicateurs techniques

### 2.4 Frontend

- React ou Next.js
- TradingView Lightweight Charts
- Zustand ou Redux

### 2.5 Infra locale

- Docker
- Docker Compose
- Nginx reverse proxy

### 2.6 Observabilité

- Prometheus (métriques)
- Grafana (dashboards)
- Loki + Promtail (logs)

## 3) Topologie logique des modules

### Couche 1 — Ingestion

- collecteurs OHLCV/volumes/news
- validation et normalisation des flux

### Couche 2 — Analyse

- moteur indicateurs techniques
- modèles IA spécialisés (tendance, volatilité, anomalies, stress)

### Couche 3 — Décision

- synthèse des signaux
- explication des décisions

### Couche 4 — Protection

- risk-governor (drawdown, exposition, suspension, mode cash)

### Couche 5 — Exécution

- paper trading
- exécution réelle encadrée (phase ultérieure)

### Couche 6 — Présentation

- API et interface web locale
- supervision et commandes utilisateur

## 4) Environnements

### 4.1 Local Dev

- usage développeur individuel
- compose minimal (api, db, redis, ui)
- données de test

### 4.2 Shared Dev

- environnement équipe
- déploiement automatique depuis develop
- tests intégration continus

### 4.3 Staging

- miroir de la production
- validation release candidates
- tests e2e et rollback

### 4.4 Production

- exécution stable
- contrôle strict des changements
- sauvegardes et alerting actifs

## 5) Exigences système (base)

### 5.1 Poste de dev

- CPU 4 cœurs minimum
- RAM 16 Go recommandé
- SSD 20 Go libres minimum
- Linux recommandé, macOS/Windows possibles avec Docker

### 5.2 Serveur dédié (staging/prod)

- CPU 8 cœurs
- RAM 32 Go
- SSD NVMe 200 Go
- sauvegardes quotidiennes + rétention 30 jours

## 6) Sécurité et conformité

- secrets hors dépôt Git
- chiffrement des communications internes sensibles
- principle of least privilege sur comptes et services
- journalisation des actions critiques
- scans de sécurité automatisés en CI

## 7) Standards engineering

- style guides backend/frontend formalisés
- conventions de commits (Conventional Commits)
- revues de code obligatoires
- définitions de done incluant tests et observabilité

## 8) Évolution prévue

Court terme :
- architecture compose stable et industrialisée

Moyen terme :
- orchestration k3s/kubernetes si charge et équipe augmentent

Long terme :
- fédération multi-brokers
- moteur de backtesting distribué
- extension de la couche explicabilité IA
