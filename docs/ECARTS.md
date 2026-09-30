# Ecarts connus

Limites et dettes connues, acceptees en connaissance de cause ou en attente
d'une decision. Chaque entree dit comment l'ecart se manifeste, pour qu'on le
reconnaisse le jour ou il se produit. Retirer une entree quand elle est traitee.

Dernière revue : 2026-09-27.

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
  (`sentineleip_ml-models` sur le poste qui a servi au squelette : fait le
  2026-09-25, le volume etait vide.)
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
  **sans bloquer** : on ne bloque pas la CI sur des binaires embarques dans une
  image officielle qu'on ne controle pas.
- **Pour rendre le scan bloquant un jour** :
  1. Image derivee `infra/docker/Dockerfile.db`, `FROM` un tag precis
     (`timescale/timescaledb:<version>-pg16`) epingle par digest, avec
     `apk upgrade --no-cache` (corrige `libexpat`).
  2. Retirer ce qui ne sert pas a l'execution :
     - `timescaledb-parallel-copy` : outil d'import en ligne de commande,
       inutilise ;
     - `timescaledb-tune` : ne tourne qu'a l'initialisation ; le remplacer par
       `NO_TS_TUNE=true` et des parametres memoire explicites (`-c
       shared_buffers=...`), de toute facon necessaires des qu'on posera un
       `mem_limit` ;
     - `gosu` : l'entrypoint ne s'en sert que s'il demarre en root. Lancer db en
       `user: "70:70"` (valide pendant l'audit, sans capacite, volumes
       existants compris), puis retirer le binaire.
  3. Remplacer `image:` par `build:` dans la compose : l'inventaire fait passer
     l'image d'office des images tierces (rapport) aux images construites
     (build + Trivy **bloquant**), sans aucune liste a modifier.
  4. Pour une vulnerabilite corrigeable mais sans objet, une entree
     `.trivyignore.yaml` justifiee, avec date d'expiration (`expired_at`),
     plutot qu'une exception permanente.
  5. Critere de sortie : 0 HIGH/CRITICAL corrigeable sur l'image derivee.
     `redis:7-alpine` y est deja et pourra suivre le meme chemin.

## E4 — Stack cloud (`infra/stacks/cloud`) : inutilisable en l'etat

Jamais deployee : rien a corriger en urgence, mais elle ne peut pas l'etre
telle quelle. A reprendre avant son premier deploiement. Constats du
2026-09-25 (Trivy v0.70.0, registres interroges directement).

### Nextcloud

- `nextcloud:30-apache` est en fin de vie : 1 180 vulnerabilites HIGH/CRITICAL
  corrigeables.
- Versions maintenues : 33 (fin de vie 2027-02), 34 (2027-06), 35 (sortie le
  2026-09-16, fin de vie 2027-09). Une majeure tous les quatre mois, un an de
  support chacune.
- **Choix retenu (2026-09-25) : Nextcloud 35**, sur le dernier tag de
  correctif (`35.0.1-apache` au 2026-09-25), epingle par digest. Premiere
  installation, donc aucune montee de version a enchainer ; c'est la fenetre
  de support la plus longue. Alternative ecartee : 34 (`34.0.4`), plus
  eprouvee mais supportee trois mois de moins.
- Ensuite, monter d'une majeure a la fois (Nextcloud n'en saute pas), au
  rythme des sorties.
- A verifier au deploiement : prerequis de la 35 (versions de PostgreSQL et de
  Redis supportees) face a `postgres:16-alpine` et `redis:7-alpine`.

### MinIO : plus d'images publiques

- MinIO a cesse de publier ses images communautaires en octobre 2025, puis a
  archive son depot en 2026. Docker Hub a supprime l'espace `minio` en
  septembre 2026 (`hub.docker.com/v2/repositories/minio/minio` : 404). Sur
  quay.io, les images communautaires sont gelees depuis le 2025-09-07, sans
  correctif, et un pull anonyme de `quay.io/minio/minio:latest` est refuse (401).
- `minio/minio:latest` et `minio/mc:latest` ne se telechargent donc plus : la
  stack ne demarre pas.
- **Choix retenu (2026-09-25) : Garage** (Deuxfleurs, AGPL-3.0, compatible
  S3 ; v2.4.1 du 2026-09-08, images publiees en continu). Suffisant pour un
  stockage interne a quatre, sans recompiler un service expose. **Sous reserve
  des verifications ci-dessous, a faire au deploiement de la stack cloud.**
- Alternatives ecartees :
  - SeaweedFS (Apache-2.0, 4.47 du 2026-09-14) : repli possible si une
    verification echoue, a rediscuter le cas echeant ;
  - recompiler MinIO depuis ses sources archivees, ou une reconstruction
    tierce : plus aucun correctif amont, pour un service expose ;
  - se passer de stockage objet.
- **A verifier au deploiement, avec Garage** :
  - versionnement des objets, aujourd'hui active par `minio-init` sur
    `sentinel-models` : pris en charge, ou a remplacer (par exemple par un
    bucket d'historique) ;
  - creation des buckets et des cles d'acces, qui remplace `minio-init` et
    `mc` ;
  - compatibilite S3 des clients prevus : rclone (`scripts/backup-cloud.sh`,
    remote `minio:` a renommer) et les futurs clients applicatifs ;
  - administration sans la console MinIO (CLI `garage`, ou interface
    d'administration) ;
  - relais VPS et DNS `s3.*` : port et en-tetes attendus par Garage.

### Le reste de la stack

- `postgres:16-alpine` : 22 vulnerabilites, toutes dans `gosu` (meme cas que
  E3). `redis:7-alpine` et `alpine/socat` (relais) : 0.
- **Exposition, une fois deployee** : forte. Nextcloud et l'API S3 sont
  publies sur Internet par les relais du VPS.
- **Controle actuel** : ports verifies (127.0.0.1 uniquement, derives de la
  compose) ; images scannees en rapport, non bloquant.

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
- `wagoid/commitlint-github-action`, encore utilisee par `mirror.yml`, est
  epinglee par SHA mais execute l'image Docker
  `wagoid/commitlint-github-action:6.2.1`, referencee par tag. La CI des PR n'en
  depend plus : elle lance `scripts/verifier.sh commits`, commitlint 19.8.1.

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

## E10 — Signal d'achat ou non : tranché, en attente de validation

**Tranché le 2026-09-27 par Jules**, dans le positionnement du produit (page
« Positionnement SENTINEL » de l'espace Outline de l'équipe) : **Sentinel
prédit et sécurise à l'action.** La position B l'emporte : le produit analyse
le marché et fournit une analyse directionnelle assortie d'un niveau de
confiance (US3.1, US3.3), puis évalue l'action que le trader s'apprête à
prendre et ajuste la protection.

**Reste à faire** : valider la décision avec Aurel et la présenter au mentor
le 2026-09-30, puis retirer cette entrée.

### Ce qui en découle pour le dépôt

- Le service ML peut produire une direction, toujours avec sa fiabilité
  historique mesurée et son explication (US3.4) ; le signal-synthesizer du
  dossier technique a sa place.
- La vue Signal du framework est cohérente avec la décision, et le plan de
  test bêta (F6, F8) reste valable.
- Deux garde-fous viennent avec la décision : le niveau de confiance affiché
  est mesuré, pas décoré ; la distinction entre analyse et recommandation
  personnalisée reste lisible, avec un cadrage juridique avant l'ouverture de
  la bêta.
- Couleurs, tranché le 2026-09-30 par Jules : la charte de marque (page
  « Identité de marque » de l'espace Outline) fait foi. Le rouge est réservé
  au risque, et une variation négative en relève directement : la baisse
  s'affiche en rouge, la hausse en vert ; les graphiques en bougies restent
  monochromes. Reste à aligner la règle 3 de CONTRIBUTING et le design system
  v1.2, qui disent encore « aucun rouge ni vert réflexe sur les prix ».

### Positions qui étaient en présence

- **Position A**, aucune direction ni signal d'achat : ancienne règle 1 de
  CONTRIBUTING, ancienne docstring du service ML, contrat de
  `/volatility/cone`, design system v1.2.
- **Position B**, signal synthétisé achat / vente / attente : dossier
  technique (US3.1, US3.3, US3.4 ; plan de test bêta, F6 et F8 ; plan CI/CD,
  section 3).
