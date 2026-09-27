# Innovation track — Plan d'action

SENTINEL — projet innovant Epitech (Tech4)

## 1. Contexte

### Origine du projet

SENTINEL est né de l'observation que les systèmes d'investissement automatisés deviennent de plus en plus accessibles au grand public, mais que la plupart des solutions souffrent de défauts critiques : opacité (systèmes « boîte noire »), dépendance au cloud, optimisation centrée sur la performance au détriment de la gestion du risque, et perte de contrôle pour l'utilisateur.

Ce projet est né de la volonté de créer une alternative qui privilégie la transparence, le contrôle utilisateur et la préservation du capital plutôt que la performance maximale.

### Problème identifié

Les solutions d'investissement automatisé actuelles présentent plusieurs limites :
- **Fonctionnement opaque** : les utilisateurs ne peuvent pas comprendre comment les décisions sont prises
- **Dépendance au cloud** : les données et l'exécution reposent sur des infrastructures externes
- **Obsession de la performance** : les systèmes sont optimisés pour les rendements plutôt que la gestion du risque
- **Perte de contrôle** : les utilisateurs ne peuvent pas intervenir ou comprendre le comportement du système
- **Trading émotionnel** : les émotions humaines mènent à de mauvaises décisions d'investissement

### Solution proposée

SENTINEL est un **système d'IA local d'aide et d'exécution d'investissement** qui :
- Analyse les marchés financiers via plusieurs modèles d'IA spécialisés
- Synthétise les analyses en signaux compréhensibles
- Propose ou exécute des décisions disciplinées
- Maintient un contrôle utilisateur permanent
- Fonctionne entièrement en local (aucune dépendance au cloud)

**Philosophie fondamentale** : privilégier la survie du capital face aux différentes conditions de marché plutôt que la recherche d'une performance maximale.

### Objectif du projet

L'objectif principal est de démontrer la faisabilité d'un système d'IA financière discipliné, explicable et centré sur la robustesse, qui élimine le principal facteur de risque en investissement : les émotions humaines.

### Track choisi

**Track Solution** — SENTINEL est une solution technologique répondant à un problème clairement identifié pour une base d'utilisateurs définie (investisseurs individuels recherchant une assistance automatisée à l'investissement transparente et contrôlée).

### Entités externes

Actuellement, le projet est développé en interne par l'équipe. Des partenariats futurs pourraient inclure :
- Fournisseurs de données financières (pour les API de données de marché)
- Bêta-testeurs de la communauté d'investissement
- Experts en technologie financière pour la validation

## 2. Spécifications techniques

### Stack technologique

**Backend**

| Composant | Technologie | Objectif |
|-----------|-------------|----------|
| Moteur principal | Python | Modèles IA, traitement des données, synthèse des signaux |
| Framework API | FastAPI | API RESTful pour la communication frontend |
| Base de données | PostgreSQL + TimescaleDB | Stockage des données historiques, optimisation séries temporelles |
| File de tâches | Celery + Redis | Traitement asynchrone, tâches planifiées |

**IA/ML**

| Composant | Technologie | Objectif |
|-----------|-------------|----------|
| Framework ML | PyTorch / scikit-learn | Entraînement et inférence des modèles |
| Analyse technique | TA-Lib / pandas-ta | Calcul des indicateurs techniques |
| Traitement données | Pandas / NumPy | Manipulation et analyse des données |

**Frontend**

| Composant | Technologie | Objectif |
|-----------|-------------|----------|
| Framework web | React / Next.js | Interface utilisateur |
| Graphiques | TradingView Lightweight Charts | Visualisation des données de marché |
| Gestion d'état | Zustand / Redux | État de l'application |

**Infrastructure**

| Composant | Technologie | Objectif |
|-----------|-------------|----------|
| Conteneurisation | Docker | Déploiement local |
| Orchestration | Docker Compose | Gestion multi-services |
| Reverse proxy | Nginx | Serveur web local |

### User stories

**US1 — Configuration système**

| ID | User story | Critères d'acceptation |
|----|------------|------------------------|
| US1.1 | En tant qu'admin, je veux configurer les connexions aux sources de données pour que le système puisse recevoir les données de marché | Identifiants API sauvegardés, statut de connexion affiché, flux de données confirmé |
| US1.2 | En tant qu'utilisateur, je veux sélectionner les actifs à surveiller pour me concentrer sur mes intérêts d'investissement | Liste d'actifs configurable, changements appliqués immédiatement |
| US1.3 | En tant qu'utilisateur, je veux définir mes paramètres de risque pour que le système respecte ma tolérance au risque | Limite de drawdown, limite d'exposition et seuils d'alerte configurables |
| US1.4 | En tant qu'utilisateur, je veux choisir mon mode opératoire pour utiliser le système selon mes besoins | Modes analyse seule, paper trading ou trading réel sélectionnables |

**US2 — Données de marché et visualisation**

| ID | User story | Critères d'acceptation |
|----|------------|------------------------|
| US2.1 | En tant qu'utilisateur, je veux voir les données de marché en temps réel pour comprendre les conditions actuelles | Données OHLCV affichées, rafraîchissement auto, latence < 3s |
| US2.2 | En tant qu'utilisateur, je veux voir les indicateurs techniques pour valider l'analyse du système | Plusieurs indicateurs affichés (RSI, MACD, Bollinger, etc.) |
| US2.3 | En tant qu'utilisateur, je veux consulter les graphiques historiques pour analyser les patterns passés | Graphiques zoomables, plusieurs timeframes disponibles |

**US3 — Analyse IA**

| ID | User story | Critères d'acceptation |
|----|------------|------------------------|
| US3.1 | En tant qu'utilisateur, je veux voir l'analyse de tendance pour comprendre la direction du marché | Classification haussière/baissière/neutre avec niveau de confiance |
| US3.2 | En tant qu'utilisateur, je veux voir le régime de volatilité pour comprendre les conditions du marché | Classification basse/moyenne/haute/extrême affichée |
| US3.3 | En tant qu'utilisateur, je veux voir le signal synthétisé pour connaître la recommandation du système | Signal achat/vente/attente avec explication du raisonnement |
| US3.4 | En tant qu'utilisateur, je veux comprendre pourquoi un signal a été généré pour faire confiance au système | Facteurs de décision listés, contributions des modèles visibles |

**US4 — Gestion du risque**

| ID | User story | Critères d'acceptation |
|----|------------|------------------------|
| US4.1 | En tant qu'utilisateur, je veux surveiller mon drawdown actuel pour connaître mon exposition au risque | Pourcentage de drawdown temps réel vs maximum autorisé |
| US4.2 | En tant qu'utilisateur, je veux recevoir des alertes quand les seuils de risque sont atteints pour agir | Notifications push, alertes visuelles, email optionnel |
| US4.3 | En tant qu'utilisateur, je veux forcer le mode cash pour sortir de toutes les positions immédiatement | Sortie d'urgence en un clic, toutes les positions clôturées |
| US4.4 | En tant qu'utilisateur, je veux que le système réduise automatiquement l'exposition en haute volatilité pour protéger mon capital | Dimensionnement automatique des positions basé sur le régime de volatilité |

**US5 — Opérations de trading**

| ID | User story | Critères d'acceptation |
|----|------------|------------------------|
| US5.1 | En tant qu'utilisateur, je veux exécuter des trades en paper trading pour tester les stratégies sans argent réel | Portefeuille virtuel, simulation d'exécution réaliste |
| US5.2 | En tant qu'utilisateur, je veux voir mes positions ouvertes pour connaître mon exposition actuelle | Actif, quantité, prix d'entrée, P&L actuel affichés |
| US5.3 | En tant qu'utilisateur, je veux accéder à l'historique des décisions pour revoir les actions passées | Journal complet avec timestamps, signaux et résultats |
| US5.4 | En tant qu'utilisateur, je veux voir les métriques de performance pour évaluer l'efficacité du système | Taux de réussite, ratio de Sharpe, drawdown max, rendement total |

**US6 — Contrôle système**

| ID | User story | Critères d'acceptation |
|----|------------|------------------------|
| US6.1 | En tant qu'utilisateur, je veux arrêter le système immédiatement pour empêcher des actions non souhaitées | Arrêt d'urgence en un clic, confirmation de l'arrêt |
| US6.2 | En tant qu'utilisateur, je veux vérifier l'état du système pour savoir que tous les modules fonctionnent | Tableau de bord de santé des modules, notifications d'erreur |
| US6.3 | En tant qu'utilisateur, je veux exporter mes données pour les analyser en externe | Export CSV/JSON des trades, signaux et performance |

### Jalons

**Jalon 1 : Fondation (T1 2026)**

**Objectifs :**
- [ ] Compléter l'infrastructure de collecte de données
- [ ] Implémenter le calcul des indicateurs techniques de base
- [ ] Développer le schéma de base de données et le stockage
- [ ] Créer les endpoints API de base
- [ ] Construire une UI minimale pour la visualisation des données

**Livrables :**
- Pipeline de données fonctionnel pour au moins 3 paires d'actifs
- Indicateurs techniques affichés sur les graphiques
- Documentation API REST basique

**Jalon 2 : Intégration des modèles IA (T2 2026)**

**Objectifs :**
- [ ] Entraîner et déployer le modèle de détection de tendance
- [ ] Entraîner et déployer le classificateur de régime de volatilité
- [ ] Implémenter le moteur de synthèse des signaux
- [ ] Créer la couche d'explicabilité des décisions
- [ ] Intégrer les modèles avec l'API

**Livrables :**
- 3 modèles IA fonctionnels avec précision documentée
- Génération de signaux avec scores de confiance
- Fonctionnalité d'explication des décisions

**Jalon 3 : Gouverneur de risque (T3 2026)**

**Objectifs :**
- [ ] Implémenter le système de surveillance du drawdown
- [ ] Construire la logique de réduction automatique d'exposition
- [ ] Créer le système de notification d'alertes
- [ ] Développer la fonctionnalité d'arrêt d'urgence
- [ ] Implémenter le moteur de paper trading

**Livrables :**
- Module de gestion du risque complet
- Paper trading avec simulation réaliste
- Système d'alertes (in-app + email optionnel)

**Jalon 4 : Interface utilisateur et expérience (T4 2026)**

**Objectifs :**
- [ ] Compléter le tableau de bord avec toutes les fonctionnalités
- [ ] Implémenter le design responsive
- [ ] Ajouter la persistance des préférences utilisateur
- [ ] Créer le flux d'onboarding
- [ ] Réaliser les tests d'utilisabilité

**Livrables :**
- UI prête pour la production
- Documentation utilisateur
- Rapport de test d'utilisabilité avec améliorations

**Jalon 5 : Validation et lancement (T1 2027)**

**Objectifs :**
- [ ] Backtesting extensif sur données historiques
- [ ] Tests bêta avec de vrais utilisateurs
- [ ] Optimisation des performances
- [ ] Audit de sécurité
- [ ] Documentation complète

**Livrables :**
- Rapport des résultats de backtesting
- Analyse des retours bêta-testeurs
- Build de production optimisé
- Documentation technique complète

## 3. Spécifications non techniques

Track sélectionné : Solution

### Sujets obligatoires

**1. Développer et retenir une communauté d'utilisateurs**

**Intention :**
Construire une communauté d'early adopters est essentiel pour le succès de SENTINEL. Puisque le projet cible des investisseurs individuels soucieux de transparence et de contrôle, nous devons identifier et engager des utilisateurs qui partagent ces valeurs.

**Plan d'action :**

1. **Construire une base d'early adopters**
   - Créer une landing page expliquant la philosophie et la proposition de valeur unique de SENTINEL
   - Lancer une liste d'attente pour l'accès bêta
   - Cibler les communautés : r/algotrading, r/investing, Hacker News, communautés indie hackers
   - Objectif : 100 inscriptions sur la liste d'attente avant le lancement bêta

2. **Organiser des sessions de test et feedback**
   - Appels vidéo mensuels avec les bêta-testeurs (5-10 utilisateurs par session)
   - Mécanisme de feedback in-app pour les rapports de bugs et suggestions
   - Formulaires de feedback structurés après chaque jalon
   - Roadmap publique influencée par les votes de la communauté

3. **Engagement communautaire**
   - Serveur Discord pour les discussions en temps réel
   - Newsletter mensuelle avec les mises à jour de développement
   - Développement transparent : changelog public, discussions ouvertes sur les décisions de design

**Objectifs :**
- 50+ bêta-testeurs actifs d'ici T3 2026
- Taux de rétention de 80% parmi les early adopters
- Priorisation des fonctionnalités guidée par la communauté

**2. Travailler sur l'expérience utilisateur**

**Intention :**
Un outil financier doit être intuitif et digne de confiance. Les utilisateurs doivent se sentir confiants dans leur compréhension du système et maintenir un sentiment de contrôle en permanence.

**Plan d'action :**

1. **Identifier et améliorer les fonctionnalités moins fluides**
   - Implémenter des analytics pour suivre le flux utilisateur (temps sur page, patterns de clics)
   - Réaliser des tests A/B sur les interfaces critiques (tableau de bord, paramètres de risque)
   - Identifier les points de friction via des interviews utilisateurs
   - Améliorations itératives basées sur les données

2. **Optimiser le design produit**
   - Système de design avec couleurs, typographie et composants cohérents
   - Design mobile-responsive pour le suivi en déplacement
   - Conformité accessibilité (WCAG 2.1 AA)
   - Hiérarchie visuelle claire priorisant les informations critiques (alertes de risque, positions actuelles)

3. **Expérience d'onboarding**
   - Assistant de configuration étape par étape pour les nouveaux utilisateurs
   - Tutoriels interactifs pour les fonctionnalités clés
   - Divulgation progressive : commencer simple, révéler la complexité selon les besoins

**Objectifs :**
- Taux de complétion des tâches > 90% pour les workflows principaux
- Score System Usability Scale (SUS) > 75
- Temps jusqu'à la première action significative < 5 minutes

### Sujets optionnels (sélection : 2)

**3. Optimiser les relations avec l'audience cible**

**Intention :**
Comprendre nos utilisateurs en profondeur nous permet de construire des fonctionnalités qui comptent vraiment et de communiquer efficacement sur la valeur du projet.

**Plan d'action :**

1. **Implémenter des mécanismes pour comprendre les utilisateurs finaux**
   - Personas utilisateurs basés sur les interviews de bêta-testeurs
   - Enquêtes régulières (NPS trimestriel, satisfaction des fonctionnalités)
   - Analytics d'usage pour comprendre les patterns de comportement
   - Interviews individuelles avec les utilisateurs avancés

2. **Communication régulière sur les améliorations**
   - Changelog public à chaque release
   - Modal « Nouveautés » pour les mises à jour significatives
   - Digest email mensuel avec améliorations et conseils
   - Mises à jour sur les réseaux sociaux sur la progression du développement

**Objectifs :**
- Score NPS > 40
- Taux de réponse aux demandes de fonctionnalités : accusé de réception sous 48h
- Engagement utilisateur actif mensuel > 60%

**4. Renforcer la crédibilité et développer la réputation**

**Intention :**
En tant qu'outil financier, SENTINEL doit établir la confiance par la transparence, la compétence démontrée et la reconnaissance de la communauté.

**Plan d'action :**

1. **Participer à des événements et conférences**
   - Présenter aux showcases et demo days Epitech
   - Soumettre aux conférences fintech/IA (sessions posters, démos)
   - Participer aux hackathons pertinents
   - S'engager dans des webinaires en ligne sur le trading algorithmique

2. **Publier des démonstrations et études de cas**
   - Résultats de backtesting détaillés avec méthodologie
   - Articles de blog expliquant l'architecture du système et les décisions de design
   - Démonstrations vidéo des fonctionnalités clés
   - Études de cas de bêta-testeurs (données de performance anonymisées)

3. **Leadership d'opinion**
   - Articles techniques sur l'IA en finance
   - Contributions open-source (bibliothèques, outils développés pour SENTINEL)
   - Engagement dans les communautés en ligne pertinentes

**Objectifs :**
- 3+ présentations à des conférences/événements d'ici T4 2026
- 5+ études de cas/démonstrations publiées
- Présence reconnue dans les communautés de trading algorithmique

## Résumé

Ce plan d'action trace le chemin de SENTINEL à travers Tech4 avec :
- **Des jalons techniques clairs** couvrant l'infrastructure de données, l'intégration IA, la gestion du risque, l'UX et la validation
- **Des user stories détaillées** couvrant toutes les fonctionnalités du système
- **Des objectifs non techniques centrés sur la communauté** assurant l'engagement utilisateur et l'adéquation produit-marché

Le projet suit le **track Solution**, se concentrant sur la construction d'une communauté d'utilisateurs, l'optimisation de l'expérience, la compréhension de l'audience cible et l'établissement de la crédibilité dans l'espace fintech.
