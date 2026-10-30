# Politique de tests — SENTINEL

## 1) Objectif

Garantir que chaque évolution de SENTINEL préserve :
- la fiabilité technique,
- la robustesse des signaux,
- la sécurité,
- la gouvernance du risque.

## 2) Portée des tests

### 2.1 Backend (Python/FastAPI)

- Tests unitaires : logique métier, règles du risk-governor, calculs de signaux
- Tests intégration : API + PostgreSQL/Timescale + Redis + Celery
- Tests contract : schéma API (OpenAPI), codes erreur, validation payloads

### 2.2 IA/ML

- Tests de validation de données (intégrité, trous, outliers)
- Tests de non-régression modèles sur datasets de référence
- Tests de stabilité des scores de confiance
- Tests de dérive (drift) simples avec seuil d'alerte

### 2.3 Frontend

- Tests unitaires composants critiques (dashboard, alertes, contrôle risque)
- Tests intégration UI-API
- Tests end-to-end parcours critiques (connexion, consultation signaux, arrêt urgence)

### 2.4 Infrastructure

- Tests de démarrage compose (health checks)
- Tests de résilience (redémarrage service, indisponibilité Redis/DB)
- Tests de migration base de données

## 3) Niveaux de tests et seuils cibles

### 3.1 Couverture

- Backend global : >= 70% (objectif 80% à terme)
- Modules critiques risque/exécution : >= 90%
- Frontend global : >= 60% (objectif 75% à terme)

### 3.2 Qualité minimale avant merge

- 100% des tests critiques passent
- 0 test flaky accepté sur pipeline principal
- 0 régression sur scénarios de risque prioritaires

### 3.3 Sécurité

- 0 secret exposé
- 0 vulnérabilité critique ouverte sans dérogation
- CVE hautes corrigées sous 7 jours max

## 4) Test strategy par étape du cycle CI/CD

### 4.1 Sur pull request

- lint + format check
- tests unitaires
- tests intégration minimaux
- scan sécurité rapide

### 4.2 Sur merge develop

- suite complète unit + intégration
- tests non-régression IA
- build images + scan conteneurs

### 4.3 Sur release candidate

- e2e complet
- test charge léger (smoke perf)
- tests résilience essentiels

### 4.4 Avant production

- test rollback
- test runbook incident critique
- validation manuelle gouverneur de risque

## 5) Jeux de données de test

- Dataset historique stable et versionné pour non-régression
- Dataset bruités/dégradés pour tester robustesse
- Données synthétiques pour cas limites (flash crash, spread anormal)

Règles :
- jamais de clé API réelle dans les jeux de tests
- anonymisation obligatoire si données externes sensibles

## 6) Gouvernance des échecs

- Build rouge sur branche principale interdit
- En cas de test flaky : ticket obligatoire, correction prioritaire
- En cas de régression risque : blocage release jusqu'à correction

## 7) Outils recommandés

- Backend : pytest, pytest-cov, hypothesis
- Frontend : vitest/jest + playwright
- API contract : schemathesis
- Sécurité : bandit, semgrep, pip-audit, trivy, gitleaks

## 8) Definition of Done tests

Une fonctionnalité est considérée terminée quand :
- ses tests unitaires existent et passent,
- ses cas d'erreur sont vérifiés,
- son impact risque est couvert,
- son comportement est tracé dans les dashboards de test,
- la CI est verte sans exception.
