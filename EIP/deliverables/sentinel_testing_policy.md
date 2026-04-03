# Politique de Tests - Sentinel

## 1) Objectif

Garantir que chaque evolution de Sentinel preserve :
- la fiabilite technique,
- la robustesse des signaux,
- la securite,
- la gouvernance du risque.

---

## 2) Portee des tests

### 2.1 Backend (Python/FastAPI)

- Tests unitaires : logique metier, regles du risk-governor, calculs de signaux
- Tests integration : API + PostgreSQL/Timescale + Redis + Celery
- Tests contract : schema API (OpenAPI), codes erreur, validation payloads

### 2.2 IA/ML

- Tests de validation de donnees (integrite, trous, outliers)
- Tests de non-regression modeles sur datasets de reference
- Tests de stabilite des scores de confiance
- Tests de derive (drift) simples avec seuil d alerte

### 2.3 Frontend

- Tests unitaires composants critiques (dashboard, alertes, controle risque)
- Tests integration UI-API
- Tests end-to-end parcours critiques (connexion, consultation signaux, arret urgence)

### 2.4 Infrastructure

- Tests de demarrage compose (health checks)
- Tests de resilience (redemarrage service, indisponibilite Redis/DB)
- Tests de migration base de donnees

---

## 3) Niveaux de tests et seuils cibles

### 3.1 Couverture

- Backend global : >= 70% (objectif 80% a terme)
- Modules critiques risque/execution : >= 90%
- Frontend global : >= 60% (objectif 75% a terme)

### 3.2 Qualite minimale avant merge

- 100% des tests critiques passent
- 0 test flaky accepte sur pipeline principal
- 0 regression sur scenarios de risque prioritaires

### 3.3 Securite

- 0 secret expose
- 0 vulnerabilite critique ouverte sans derogation
- CVE hautes corrigees sous 7 jours max

---

## 4) Test Strategy par etape du cycle CI/CD

### 4.1 Sur Pull Request

- lint + format check
- tests unitaires
- tests integration minimaux
- scan securite rapide

### 4.2 Sur merge develop

- suite complete unit + integration
- tests non-regression IA
- build images + scan conteneurs

### 4.3 Sur release candidate

- e2e complet
- test charge leger (smoke perf)
- tests resilience essentiels

### 4.4 Avant production

- test rollback
- test runbook incident critique
- validation manuelle gouverneur de risque

---

## 5) Jeux de donnees de test

- Dataset historique stable et versionne pour non-regression
- Dataset bruites/degrades pour tester robustesse
- Donnees synthetiques pour cas limites (flash crash, spread anormal)

Regles :
- jamais de cle API reelle dans les jeux de tests
- anonymisation obligatoire si donnees externes sensibles

---

## 6) Gouvernance des echecs

- Build rouge sur branche principale interdit
- En cas de test flaky : ticket obligatoire, correction prioritaire
- En cas de regression risque : blocage release jusqu a correction

---

## 7) Outils recommandes

- Backend : pytest, pytest-cov, hypothesis
- Frontend : vitest/jest + playwright
- API contract : schemathesis
- Securite : bandit, semgrep, pip-audit, trivy, gitleaks

---

## 8) Definition of Done tests

Une fonctionnalite est consideree terminee quand :
- ses tests unitaires existent et passent,
- ses cas d erreur sont verifies,
- son impact risque est couvert,
- son comportement est trace dans les dashboards de test,
- la CI est verte sans exception.
