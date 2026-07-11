# Environnement Technologique - Sentinel

## 1) Vision technique

Sentinel est concu comme une plateforme locale-first, modulaire et explicable pour l aide a la decision et l execution disciplinee en investissement.

Objectifs techniques :
- robustesse et maitrise du risque,
- tracabilite complete des donnees et decisions,
- independance maximale vis-a-vis du cloud,
- deploiement reproductible sur poste local ou serveur dedie.

---

## 2) Stack cible

### 2.1 Backend

- Python 3.11+
- FastAPI (API REST)
- Uvicorn/Gunicorn
- Celery (jobs asynchrones)

### 2.2 Data et stockage

- PostgreSQL 16+
- Extension TimescaleDB (series temporelles)
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

### 2.6 Observabilite

- Prometheus (metriques)
- Grafana (dashboards)
- Loki + Promtail (logs)

---

## 3) Topologie logique des modules

### Couche 1 - Ingestion

- collecteurs OHLCV/volumes/news
- validation et normalisation des flux

### Couche 2 - Analyse

- moteur indicateurs techniques
- modeles IA specialises (tendance, volatilite, anomalies, stress)

### Couche 3 - Decision

- synthese des signaux
- explication des decisions

### Couche 4 - Protection

- risk-governor (drawdown, exposition, suspension, mode cash)

### Couche 5 - Execution

- paper trading
- execution reel encadree (phase ulterieure)

### Couche 6 - Presentation

- API et interface web locale
- supervision et commandes utilisateur

---

## 4) Environnements

### 4.1 Local Dev

- usage developpeur individuel
- compose minimal (api, db, redis, ui)
- donnees de test

### 4.2 Shared Dev

- environnement equipe
- deploiement automatique depuis develop
- tests integration continus

### 4.3 Staging

- miroir de la production
- validation release candidates
- tests e2e et rollback

### 4.4 Production

- execution stable
- controle strict des changements
- sauvegardes et alerting actifs

---

## 5) Exigences systeme (base)

### 5.1 Poste de dev

- CPU 4 coeurs minimum
- RAM 16 Go recommande
- SSD 20 Go libres minimum
- Linux recommande, macOS/Windows possibles avec Docker

### 5.2 Serveur dedie (staging/prod)

- CPU 8 coeurs
- RAM 32 Go
- SSD NVMe 200 Go
- sauvegardes quotidiennes + retention 30 jours

---

## 6) Securite et conformite

- secrets hors depot Git
- chiffrement des communications internes sensibles
- principle of least privilege sur comptes et services
- journalisation des actions critiques
- scans de securite automatises en CI

---

## 7) Standards engineering

- style guides backend/frontend formalises
- conventions de commits (Conventional Commits)
- revues de code obligatoires
- definitions de done incluant tests et observabilite

---

## 8) Evolution prevue

Court terme :
- architecture compose stable et industrialisee

Moyen terme :
- orchestration k3s/kubernetes si charge et equipe augmentent

Long terme :
- federation multi-brokers
- moteur de backtesting distribue
- extension de la couche explicabilite IA
