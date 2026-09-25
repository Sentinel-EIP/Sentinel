# Ecarts connus

Limites et dettes connues, acceptees en connaissance de cause ou en attente
d'une decision. Chaque entree dit comment l'ecart se manifeste, pour qu'on le
reconnaisse le jour ou il se produit. Retirer une entree quand elle est traitee.

Derniere revue : 2026-09-25.

## E1 — Volume de modeles cree par une autre image (droits root)

- **Symptome** : le service ML prod refuse de demarrer avec
  `RuntimeError: /models n'est pas inscriptible par l'uid 10002 (...)`.
- **Cause** : avant l'introduction du volume `ml-models-dev`, le ML de dev
  (root) partageait le volume `ml-models` de la prod (uid 10002, depuis le
  premier commit des images) et y laissait des fichiers root. Tout volume cree
  ou touche par une image root a le meme effet.
- **Correctif, une fois par volume concerne** :
  ```bash
  docker run --rm -v <projet>_ml-models:/models alpine chown -R 10002:10002 /models
  ```
  (`sentineleip_ml-models` sur le poste qui a servi au squelette.)
- **Prevention en place** : le dev utilise desormais son propre volume
  (`ml-models-dev`), et le ML verifie au demarrage que ses caches sont
  inscriptibles (`check_model_cache`, `ml/app/main.py`) : l'erreur survient au
  demarrage, avec sa cause, et non au premier telechargement de modele.

## E2 — `torch.compile` indisponible

- **Symptome** : `InvalidCxxCompiler ... g++` a l'appel de `torch.compile`,
  en dev comme en prod.
- **Cause** : les images ML ne contiennent aucun compilateur, volontairement
  (surface d'attaque, CVE). L'inference classique n'en a pas besoin.
- **A traiter quand** : un modele en aura besoin. Ajouter alors une etape
  dediee avec compilateur, sans la mettre dans l'image prod servie.

## E3 — Image de base de donnees tierce non corrigee

- **Constat** (Trivy v0.70.0, 2026-09-25) : `timescale/timescaledb:latest-pg16`
  porte 70 vulnerabilites HIGH/CRITICAL corrigeables. 69 sont dans des binaires
  Go embarques (`gosu`, `timescaledb-tune`, `timescaledb-parallel-copy`), une
  dans `libexpat`.
- **Exposition** : faible. La base n'est sur aucun reseau publie (`data` est
  `internal`) ; ces binaires servent a l'initialisation ou sont inutilises.
- **Controle** : le job CI `images-tierces` scanne toutes les images tierces
  (liste derivee de la compose) et publie le resultat dans le resume du run,
  **sans bloquer** tant que cet ecart est ouvert.
- **Pistes** : image derivee (`apk upgrade`, retrait des outils inutilises,
  execution en uid 70 pour se passer de `gosu`, parametres memoire explicites
  a la place de `timescaledb-tune`), tag precis et digest. Le scan deviendra
  alors bloquant.

## E4 — Stack cloud exposee sur Internet sans controle bloquant

- **Constat** (Trivy v0.70.0, 2026-09-25) :
  - `nextcloud:30-apache` est en fin de vie : 1 180 vulnerabilites
    HIGH/CRITICAL corrigeables ;
  - `minio/minio:latest` et `minio/mc:latest` ne sont plus publiques
    (`UNAUTHORIZED`) : la stack ne peut plus etre redeployee de zero, et le
    projet MinIO est archive ;
  - `postgres:16-alpine` : 22 (binaire `gosu`).
- **Exposition** : forte. Nextcloud et l'API S3 sont publies sur Internet par
  les relais du VPS.
- **Controle** : ports verifies (127.0.0.1 uniquement, derives de la compose),
  images scannees en rapport, non bloquant.
- **Decision a prendre** : mettre Nextcloud a jour, remplacer MinIO, ou sortir
  cette stack du depot produit.

## E5 — Anciennes valeurs d'infrastructure accessibles par SHA

- Le commit `861e515`, reecrit, reste accessible sur GitHub par son SHA
  (domaines, hote SSH, adressage du tunnel). Aucun secret n'y figure (gitleaks).
- **Correctif** : demande de purge au support GitHub (« remove sensitive data »).
  Considerer ces valeurs comme exposees.

## E6 — Dependances non verrouillees

- Aucun lockfile Python (`>=` partout, torch non declare dans
  `ml/pyproject.toml`) : builds non reproductibles, versions vulnerables
  admissibles.
- L'etape `pip-audit` de la CI n'audite rien (`|| true`).
- Frontend : vitest 2 installe un vite 5 a cote de vite 6 ; `npm audit` releve
  2 CRITICAL et 1 HIGH, uniquement en dependances de dev. ESLint 9 est en fin de
  vie.

## E7 — Images de base par tag mobile

- `python:3.11-slim`, `node:22-alpine`, `nginxinc/nginx-unprivileged:stable-alpine`,
  `timescale/timescaledb:latest-pg16`, `redis:7-alpine` : pas de digest, pas de
  Dependabot. Deux builds du meme commit peuvent differer.
- L'`apk upgrade` des images nginx est non reproductible par construction
  (compromis assume : il applique les correctifs publies depuis l'image de base).
- `wagoid/commitlint-github-action` est epinglee par SHA, mais execute l'image
  Docker `wagoid/commitlint-github-action:6.2.1`, referencee par tag.

## E8 — Branches `main` et `dev` non protegees

- Les regles de PR du dossier (review obligatoire, CI verte avant merge) ne
  sont pas imposees : l'API GitHub renvoie `protected: false` pour `main` et
  `dev`, et `main` a deja ete reecrite (force-push).
- Le squash merge n'est pas impose non plus : c'est pourquoi la CI verifie a
  la fois le titre de la PR et chacun de ses commits.
- **Correctif** (administrateur du depot) : regle de protection ou ruleset sur
  `main` et `dev`, avec review requise, jobs de CI requis et squash merge seul.

## E9 — Dossier technique a mettre a jour

Le depot s'ecarte volontairement du dossier sur ces points ; le dossier doit
suivre, ou le depot revenir en arriere :

- branche d'integration `dev` (dossier : `develop`) ; prefixes `feat/`, `fix/`
  (dossier : `feature/`) ;
- design system v1.2 (`frontend/src/styles/tokens.css`) absent du dossier ;
- regles d'equipe 5 et 6 de CONTRIBUTING (fiabilite historique mesuree,
  assouplissement d'une regle de risque differe de 24 h) ;
- build des images, scan Trivy et smoke **en PR** (dossier : au merge sur
  develop, `sentinel_testing_policy.md` 4.2) : la chaine de PR depasse les
  15 min visees (`sentinel_deployment_cicd_plan.md` section 10), et l'image ML
  est construite deux fois (build puis smoke). Piste : le smoke reutilise les
  images du build (cache gha), ou le build repasse au merge.
