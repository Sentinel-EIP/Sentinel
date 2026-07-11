# INNOVATION TRACK - PLAN D'ACTION

## SENTINEL - Projet Innovant Epitech (Tech4)

---

# 1. Contexte

## Origine du Projet

Sentinel est ne de l'observation que les systemes d'investissement automatises deviennent de plus en plus accessibles au grand public, mais que la plupart des solutions souffrent de defauts critiques : opacite (systemes "boite noire"), dependance au cloud, optimisation centree sur la performance au detriment de la gestion du risque, et perte de controle pour l'utilisateur.

Ce projet est ne de la volonte de creer une alternative qui privilegie la transparence, le controle utilisateur et la preservation du capital plutot que la performance maximale.

## Probleme Identifie

Les solutions d'investissement automatise actuelles presentent plusieurs limites :
- **Fonctionnement opaque** : Les utilisateurs ne peuvent pas comprendre comment les decisions sont prises
- **Dependance au cloud** : Les donnees et l'execution reposent sur des infrastructures externes
- **Obsession de la performance** : Les systemes sont optimises pour les rendements plutot que la gestion du risque
- **Perte de controle** : Les utilisateurs ne peuvent pas intervenir ou comprendre le comportement du systeme
- **Trading emotionnel** : Les emotions humaines menent a de mauvaises decisions d'investissement

## Solution Proposee

Sentinel est un **systeme d'IA local d'aide et d'execution d'investissement** qui :
- Analyse les marches financiers via plusieurs modeles d'IA specialises
- Synthetise les analyses en signaux comprehensibles
- Propose ou execute des decisions disciplinees
- Maintient un controle utilisateur permanent
- Fonctionne entierement en local (aucune dependance au cloud)

**Philosophie fondamentale** : Privilegier la survie du capital face aux differentes conditions de marche plutot que la recherche d'une performance maximale.

## Objectif du Projet

L'objectif principal est de demontrer la faisabilite d'un systeme d'IA financiere discipline, explicable et centre sur la robustesse, qui elimine le principal facteur de risque en investissement : les emotions humaines.

## Track Choisi

**Track Solution** - Sentinel est une solution technologique repondant a un probleme clairement identifie pour une base d'utilisateurs definie (investisseurs individuels recherchant une assistance automatisee a l'investissement transparente et controlee).

## Entites Externes

Actuellement, le projet est developpe en interne par l'equipe. Des partenariats futurs pourraient inclure :
- Fournisseurs de donnees financieres (pour les API de donnees de marche)
- Beta testeurs de la communaute d'investissement
- Experts en technologie financiere pour la validation

---

# 2. Specifications Techniques

## Stack Technologique

### Backend
| Composant | Technologie | Objectif |
|-----------|-------------|----------|
| Moteur Principal | Python | Modeles IA, traitement des donnees, synthese des signaux |
| Framework API | FastAPI | API RESTful pour la communication frontend |
| Base de Donnees | PostgreSQL + TimescaleDB | Stockage des donnees historiques, optimisation series temporelles |
| File de Taches | Celery + Redis | Traitement asynchrone, taches planifiees |

### IA/ML
| Composant | Technologie | Objectif |
|-----------|-------------|----------|
| Framework ML | PyTorch / scikit-learn | Entrainement et inference des modeles |
| Analyse Technique | TA-Lib / pandas-ta | Calcul des indicateurs techniques |
| Traitement Donnees | Pandas / NumPy | Manipulation et analyse des donnees |

### Frontend
| Composant | Technologie | Objectif |
|-----------|-------------|----------|
| Framework Web | React / Next.js | Interface utilisateur |
| Graphiques | TradingView Lightweight Charts | Visualisation des donnees de marche |
| Gestion d'Etat | Zustand / Redux | Etat de l'application |

### Infrastructure
| Composant | Technologie | Objectif |
|-----------|-------------|----------|
| Conteneurisation | Docker | Deploiement local |
| Orchestration | Docker Compose | Gestion multi-services |
| Reverse Proxy | Nginx | Serveur web local |

---

## User Stories

### US1 - Configuration Systeme

| ID | User Story | Criteres d'Acceptation |
|----|------------|------------------------|
| US1.1 | En tant qu'admin, je veux configurer les connexions aux sources de donnees pour que le systeme puisse recevoir les donnees de marche | Identifiants API sauvegardes, statut de connexion affiche, flux de donnees confirme |
| US1.2 | En tant qu'utilisateur, je veux selectionner les actifs a surveiller pour me concentrer sur mes interets d'investissement | Liste d'actifs configurable, changements appliques immediatement |
| US1.3 | En tant qu'utilisateur, je veux definir mes parametres de risque pour que le systeme respecte ma tolerance au risque | Limite de drawdown, limite d'exposition et seuils d'alerte configurables |
| US1.4 | En tant qu'utilisateur, je veux choisir mon mode operatoire pour utiliser le systeme selon mes besoins | Modes analyse seule, paper trading ou trading reel selectionnables |

### US2 - Donnees de Marche et Visualisation

| ID | User Story | Criteres d'Acceptation |
|----|------------|------------------------|
| US2.1 | En tant qu'utilisateur, je veux voir les donnees de marche en temps reel pour comprendre les conditions actuelles | Donnees OHLCV affichees, rafraichissement auto, latence < 3s |
| US2.2 | En tant qu'utilisateur, je veux voir les indicateurs techniques pour valider l'analyse du systeme | Plusieurs indicateurs affiches (RSI, MACD, Bollinger, etc.) |
| US2.3 | En tant qu'utilisateur, je veux consulter les graphiques historiques pour analyser les patterns passes | Graphiques zoomables, plusieurs timeframes disponibles |

### US3 - Analyse IA

| ID | User Story | Criteres d'Acceptation |
|----|------------|------------------------|
| US3.1 | En tant qu'utilisateur, je veux voir l'analyse de tendance pour comprendre la direction du marche | Classification haussiere/baissiere/neutre avec niveau de confiance |
| US3.2 | En tant qu'utilisateur, je veux voir le regime de volatilite pour comprendre les conditions du marche | Classification basse/moyenne/haute/extreme affichee |
| US3.3 | En tant qu'utilisateur, je veux voir le signal synthetise pour connaitre la recommandation du systeme | Signal achat/vente/attente avec explication du raisonnement |
| US3.4 | En tant qu'utilisateur, je veux comprendre pourquoi un signal a ete genere pour faire confiance au systeme | Facteurs de decision listes, contributions des modeles visibles |

### US4 - Gestion du Risque

| ID | User Story | Criteres d'Acceptation |
|----|------------|------------------------|
| US4.1 | En tant qu'utilisateur, je veux surveiller mon drawdown actuel pour connaitre mon exposition au risque | Pourcentage de drawdown temps reel vs maximum autorise |
| US4.2 | En tant qu'utilisateur, je veux recevoir des alertes quand les seuils de risque sont atteints pour agir | Notifications push, alertes visuelles, email optionnel |
| US4.3 | En tant qu'utilisateur, je veux forcer le mode cash pour sortir de toutes les positions immediatement | Sortie d'urgence en un clic, toutes les positions cloturees |
| US4.4 | En tant qu'utilisateur, je veux que le systeme reduise automatiquement l'exposition en haute volatilite pour proteger mon capital | Dimensionnement automatique des positions base sur le regime de volatilite |

### US5 - Operations de Trading

| ID | User Story | Criteres d'Acceptation |
|----|------------|------------------------|
| US5.1 | En tant qu'utilisateur, je veux executer des trades en paper trading pour tester les strategies sans argent reel | Portefeuille virtuel, simulation d'execution realiste |
| US5.2 | En tant qu'utilisateur, je veux voir mes positions ouvertes pour connaitre mon exposition actuelle | Actif, quantite, prix d'entree, P&L actuel affiches |
| US5.3 | En tant qu'utilisateur, je veux acceder a l'historique des decisions pour revoir les actions passees | Journal complet avec timestamps, signaux et resultats |
| US5.4 | En tant qu'utilisateur, je veux voir les metriques de performance pour evaluer l'efficacite du systeme | Taux de reussite, ratio de Sharpe, drawdown max, rendement total |

### US6 - Controle Systeme

| ID | User Story | Criteres d'Acceptation |
|----|------------|------------------------|
| US6.1 | En tant qu'utilisateur, je veux arreter le systeme immediatement pour empecher des actions non souhaitees | Arret d'urgence en un clic, confirmation de l'arret |
| US6.2 | En tant qu'utilisateur, je veux verifier l'etat du systeme pour savoir que tous les modules fonctionnent | Tableau de bord de sante des modules, notifications d'erreur |
| US6.3 | En tant qu'utilisateur, je veux exporter mes donnees pour les analyser en externe | Export CSV/JSON des trades, signaux et performance |

---

## Jalons

### Jalon 1 : Fondation (T1 2026)

**Objectifs :**
- [ ] Completer l'infrastructure de collecte de donnees
- [ ] Implementer le calcul des indicateurs techniques de base
- [ ] Developper le schema de base de donnees et le stockage
- [ ] Creer les endpoints API de base
- [ ] Construire une UI minimale pour la visualisation des donnees

**Livrables :**
- Pipeline de donnees fonctionnel pour au moins 3 paires d'actifs
- Indicateurs techniques affiches sur les graphiques
- Documentation API REST basique

---

### Jalon 2 : Integration des Modeles IA (T2 2026)

**Objectifs :**
- [ ] Entrainer et deployer le modele de detection de tendance
- [ ] Entrainer et deployer le classificateur de regime de volatilite
- [ ] Implementer le moteur de synthese des signaux
- [ ] Creer la couche d'explicabilite des decisions
- [ ] Integrer les modeles avec l'API

**Livrables :**
- 3 modeles IA fonctionnels avec precision documentee
- Generation de signaux avec scores de confiance
- Fonctionnalite d'explication des decisions

---

### Jalon 3 : Gouverneur de Risque (T3 2026)

**Objectifs :**
- [ ] Implementer le systeme de surveillance du drawdown
- [ ] Construire la logique de reduction automatique d'exposition
- [ ] Creer le systeme de notification d'alertes
- [ ] Developper la fonctionnalite d'arret d'urgence
- [ ] Implementer le moteur de paper trading

**Livrables :**
- Module de gestion du risque complet
- Paper trading avec simulation realiste
- Systeme d'alertes (in-app + email optionnel)

---

### Jalon 4 : Interface Utilisateur et Experience (T4 2026)

**Objectifs :**
- [ ] Completer le tableau de bord avec toutes les fonctionnalites
- [ ] Implementer le design responsive
- [ ] Ajouter la persistance des preferences utilisateur
- [ ] Creer le flux d'onboarding
- [ ] Realiser les tests d'utilisabilite

**Livrables :**
- UI prete pour la production
- Documentation utilisateur
- Rapport de test d'utilisabilite avec ameliorations

---

### Jalon 5 : Validation et Lancement (T1 2027)

**Objectifs :**
- [ ] Backtesting extensif sur donnees historiques
- [ ] Tests beta avec de vrais utilisateurs
- [ ] Optimisation des performances
- [ ] Audit de securite
- [ ] Documentation complete

**Livrables :**
- Rapport des resultats de backtesting
- Analyse des retours beta testeurs
- Build de production optimise
- Documentation technique complete

---

# 3. Specifications Non Techniques

## Track Selectionne : Solution

### Sujets Obligatoires

#### 1. Developper et Retenir une Communaute d'Utilisateurs

**Intention :**
Construire une communaute d'early adopters est essentiel pour le succes de Sentinel. Puisque le projet cible des investisseurs individuels soucieux de transparence et de controle, nous devons identifier et engager des utilisateurs qui partagent ces valeurs.

**Plan d'Action :**

1. **Construire une base d'early adopters**
   - Creer une landing page expliquant la philosophie et la proposition de valeur unique de Sentinel
   - Lancer une liste d'attente pour l'acces beta
   - Cibler les communautes : r/algotrading, r/investing, Hacker News, communautes indie hackers
   - Objectif : 100 inscriptions sur la liste d'attente avant le lancement beta

2. **Organiser des sessions de test et feedback**
   - Appels video mensuels avec les beta testeurs (5-10 utilisateurs par session)
   - Mecanisme de feedback in-app pour les rapports de bugs et suggestions
   - Formulaires de feedback structures apres chaque jalon
   - Roadmap publique influencee par les votes de la communaute

3. **Engagement communautaire**
   - Serveur Discord pour les discussions en temps reel
   - Newsletter mensuelle avec les mises a jour de developpement
   - Developpement transparent : changelog public, discussions ouvertes sur les decisions de design

**Objectifs :**
- 50+ beta testeurs actifs d'ici T3 2026
- Taux de retention de 80% parmi les early adopters
- Priorisation des fonctionnalites guidee par la communaute

---

#### 2. Travailler sur l'Experience Utilisateur

**Intention :**
Un outil financier doit etre intuitif et digne de confiance. Les utilisateurs doivent se sentir confiants dans leur comprehension du systeme et maintenir un sentiment de controle en permanence.

**Plan d'Action :**

1. **Identifier et ameliorer les fonctionnalites moins fluides**
   - Implementer des analytics pour suivre le flux utilisateur (temps sur page, patterns de clics)
   - Realiser des tests A/B sur les interfaces critiques (tableau de bord, parametres de risque)
   - Identifier les points de friction via des interviews utilisateurs
   - Ameliorations iteratives basees sur les donnees

2. **Optimiser le design produit**
   - Systeme de design avec couleurs, typographie et composants coherents
   - Design mobile-responsive pour le suivi en deplacement
   - Conformite accessibilite (WCAG 2.1 AA)
   - Hierarchie visuelle claire priorisant les informations critiques (alertes de risque, positions actuelles)

3. **Experience d'onboarding**
   - Assistant de configuration etape par etape pour les nouveaux utilisateurs
   - Tutoriels interactifs pour les fonctionnalites cles
   - Divulgation progressive : commencer simple, reveler la complexite selon les besoins

**Objectifs :**
- Taux de completion des taches > 90% pour les workflows principaux
- Score System Usability Scale (SUS) > 75
- Temps jusqu'a la premiere action significative < 5 minutes

---

### Sujets Optionnels (Selection : 2)

#### 3. Optimiser les Relations avec l'Audience Cible

**Intention :**
Comprendre nos utilisateurs en profondeur nous permet de construire des fonctionnalites qui comptent vraiment et de communiquer efficacement sur la valeur du projet.

**Plan d'Action :**

1. **Implementer des mecanismes pour comprendre les utilisateurs finaux**
   - Personas utilisateurs bases sur les interviews de beta testeurs
   - Enquetes regulieres (NPS trimestriel, satisfaction des fonctionnalites)
   - Analytics d'usage pour comprendre les patterns de comportement
   - Interviews individuelles avec les utilisateurs avances

2. **Communication reguliere sur les ameliorations**
   - Changelog public a chaque release
   - Modal "Nouveautes" pour les mises a jour significatives
   - Digest email mensuel avec ameliorations et conseils
   - Mises a jour sur les reseaux sociaux sur la progression du developpement

**Objectifs :**
- Score NPS > 40
- Taux de reponse aux demandes de fonctionnalites : accusé de reception sous 48h
- Engagement utilisateur actif mensuel > 60%

---

#### 4. Renforcer la Credibilite et Developper la Reputation

**Intention :**
En tant qu'outil financier, Sentinel doit etablir la confiance par la transparence, la competence demontree et la reconnaissance de la communaute.

**Plan d'Action :**

1. **Participer a des evenements et conferences**
   - Presenter aux showcases et demo days Epitech
   - Soumettre aux conferences fintech/IA (sessions posters, demos)
   - Participer aux hackathons pertinents
   - S'engager dans des webinaires en ligne sur le trading algorithmique

2. **Publier des demonstrations et etudes de cas**
   - Resultats de backtesting detailles avec methodologie
   - Articles de blog expliquant l'architecture du systeme et les decisions de design
   - Demonstrations video des fonctionnalites cles
   - Etudes de cas de beta testeurs (donnees de performance anonymisees)

3. **Leadership d'opinion**
   - Articles techniques sur l'IA en finance
   - Contributions open-source (bibliotheques, outils developpes pour Sentinel)
   - Engagement dans les communautes en ligne pertinentes

**Objectifs :**
- 3+ presentations a des conferences/evenements d'ici T4 2026
- 5+ etudes de cas/demonstrations publiees
- Presence reconnue dans les communautes de trading algorithmique

---

## Resume

Ce plan d'action trace le chemin de Sentinel a travers Tech4 avec :
- **Des jalons techniques clairs** couvrant l'infrastructure de donnees, l'integration IA, la gestion du risque, l'UX et la validation
- **Des user stories detaillees** couvrant toutes les fonctionnalites du systeme
- **Des objectifs non techniques centres sur la communaute** assurant l'engagement utilisateur et l'adequation produit-marche

Le projet suit le **track Solution**, se concentrant sur la construction d'une communaute d'utilisateurs, l'optimisation de l'experience, la comprehension de l'audience cible et l'etablissement de la credibilite dans l'espace fintech.
