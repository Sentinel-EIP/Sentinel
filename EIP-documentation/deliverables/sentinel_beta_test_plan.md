# Plan de test bêta — SENTINEL

## 1. Contexte du projet

### Contexte

Les systèmes automatisés d'investissement se démocratisent rapidement grâce à l'IA et aux plateformes de trading accessibles au grand public. Cependant, ces solutions présentent plusieurs limites :
- Fonctionnement souvent opaque (« boîte noire »)
- Dépendance à des infrastructures cloud
- Optimisation centrée sur la performance plutôt que la gestion du risque
- Perte de contrôle pour l'utilisateur

### Objectifs

Sentinel est un système d'IA local d'aide et d'exécution d'investissement conçu pour :
- Analyser les marchés financiers via plusieurs modèles d'IA spécialisés
- Synthétiser ces analyses en signaux compréhensibles
- Proposer ou exécuter des décisions disciplinées
- Maintenir un contrôle utilisateur permanent

**Philosophie** : privilégier la survie du capital face aux différentes conditions de marché plutôt que la recherche d'une performance maximale.

### Architecture

Sentinel repose sur une architecture modulaire séparant clairement :
1. **Collecte de données** : prix de marché (OHLCV), volumes, indicateurs techniques
2. **Analyse IA** : modèles spécialisés (tendances, volatilité, anomalies, stress)
3. **Synthèse des signaux** : agrégation des analyses en recommandations
4. **Gouverneur de risque** : supervision et limitation des risques
5. **Exécution** : application des décisions selon les contraintes définies
6. **Interface utilisateur** : contrôle et suivi via navigateur web local

## 2. Rôles utilisateurs

Les rôles suivants seront impliqués dans les tests bêta.

| Nom du rôle | Description |
|-------------|-------------|
| Admin | Un administrateur gère la configuration système, les connexions API, la configuration des sources de données et les paramètres techniques avancés |
| Utilisateur Standard | Un utilisateur régulier qui peut configurer les paramètres de risque, consulter les analyses de marché, surveiller les positions, recevoir des alertes et contrôler les opérations du système |

## 3. Tableau des fonctionnalités

Toutes les fonctionnalités listées seront démontrées lors de la présentation bêta.

### 3.1 Configuration et démarrage

| ID | Rôle utilisateur | Nom de la fonctionnalité | Description courte |
|----|------------------|--------------------------|---------------------|
| F1 | Admin | Configurer les connexions de données | Paramétrer les sources de données de marché et les connexions API pour les flux de prix |
| F2 | Utilisateur Standard | Définir les paramètres de risque | Configurer le drawdown maximal, l'exposition maximale et les seuils d'alerte |
| F3 | Utilisateur Standard | Sélectionner le mode opératoire | Choisir entre mode analyse seule, paper trading ou trading réel supervisé |

### 3.2 Collecte et visualisation des données

| ID | Rôle utilisateur | Nom de la fonctionnalité | Description courte |
|----|------------------|--------------------------|---------------------|
| F4 | Utilisateur Standard | Visualiser les données de marché | Afficher les prix OHLCV et volumes en temps réel pour les actifs surveillés |
| F5 | Utilisateur Standard | Consulter les indicateurs techniques | Afficher les indicateurs techniques calculés localement sur l'interface |

### 3.3 Analyse IA

| ID | Rôle utilisateur | Nom de la fonctionnalité | Description courte |
|----|------------------|--------------------------|---------------------|
| F6 | Utilisateur Standard | Analyser les tendances de marché | Obtenir l'analyse de tendance générée par l'IA (haussière/baissière/neutre) |
| F7 | Utilisateur Standard | Évaluer le régime de volatilité | Visualiser l'évaluation du niveau de volatilité actuel du marché |
| F8 | Utilisateur Standard | Consulter le signal synthétisé | Afficher le signal agrégé (achat/vente/attente) issu des analyses combinées |

### 3.4 Gouvernance du risque

| ID | Rôle utilisateur | Nom de la fonctionnalité | Description courte |
|----|------------------|--------------------------|---------------------|
| F9 | Utilisateur Standard | Surveiller le drawdown en cours | Visualiser en temps réel le drawdown par rapport au seuil maximal défini |
| F10 | Utilisateur Standard | Recevoir les alertes de risque | Être notifié lorsqu'un seuil de risque est atteint ou dépassé |
| F11 | Utilisateur Standard | Forcer le passage en mode cash | Déclencher manuellement la clôture de toutes les positions ouvertes |

### 3.5 Exécution et suivi

| ID | Rôle utilisateur | Nom de la fonctionnalité | Description courte |
|----|------------------|--------------------------|---------------------|
| F12 | Utilisateur Standard | Exécuter des opérations paper trading | Réaliser des opérations virtuelles sans engager de capital réel |
| F13 | Utilisateur Standard | Consulter les positions ouvertes | Afficher l'état actuel des positions (actif, quantité, P&L) |
| F14 | Utilisateur Standard | Accéder à l'historique des décisions | Consulter le journal des décisions passées avec leur justification |

### 3.6 Contrôle système

| ID | Rôle utilisateur | Nom de la fonctionnalité | Description courte |
|----|------------------|--------------------------|---------------------|
| F15 | Utilisateur Standard | Arrêter le système en urgence | Stopper toute activité du système en un clic |
| F16 | Utilisateur Standard | Vérifier l'état du système | Vérifier que tous les modules (collecte, analyse, risque) fonctionnent correctement |

## 4. Critères de succès

| ID | Critère de succès clé | Indicateur/Métrique | Résultat |
|----|----------------------|---------------------|----------|
| F1 | Le système se connecte à la source de données et reçoit les prix | Connexion établie en < 5s, données reçues chaque minute | Atteint |
| F2 | Les paramètres de risque sont sauvegardés et appliqués correctement | 10 configurations testées, 0 échec de sauvegarde | Atteint |
| F3 | Le changement de mode est effectif immédiatement | Temps de basculement < 2s, 10 tests, 0 échec | Atteint |
| F4 | Les données de marché s'affichent et se mettent à jour automatiquement | Rafraîchissement auto, latence < 3s sur 20 tests | Atteint |
| F5 | Les indicateurs techniques sont calculés et affichés correctement | Comparaison avec calcul manuel sur 5 périodes, écart < 0.1% | Atteint |
| F6 | L'analyse de tendance est générée et cohérente avec les conditions du marché | Analyse disponible en < 10s après demande, 15 tests | Atteint |
| F7 | Le régime de volatilité est identifié correctement | Classification cohérente sur 10 scénarios de test | Partiellement atteint (8/10) |
| F8 | Le signal synthétisé est disponible et compréhensible | Signal affiché avec niveau de confiance, 100% des cas testés | Atteint |
| F9 | Le drawdown est calculé en temps réel et affiché | Mise à jour chaque seconde, précision 0.01% | Atteint |
| F10 | Les alertes sont déclenchées quand les seuils sont atteints | 5 simulations de dépassement, 5 alertes reçues | Atteint |
| F11 | Le mode cash clôture toutes les positions ouvertes | Test avec 3 positions ouvertes, 100% clôturées en < 5s | Atteint |
| F12 | Les opérations paper trading sont enregistrées sans erreur | 20 opérations simulées, 0 erreur d'enregistrement | Atteint |
| F13 | Les positions ouvertes sont affichées avec P&L actualisé | Mise à jour temps réel, écart P&L < 0.01% vs calcul manuel | Atteint |
| F14 | L'historique des décisions est complet et accessible | Toutes les décisions des 7 derniers jours accessibles | Atteint |
| F15 | L'arrêt d'urgence stoppe toutes les activités | Temps d'arrêt < 1s, aucune opération exécutée après arrêt | Atteint |
| F16 | L'état du système reflète correctement le statut de chaque module | Simulation de panne d'un module détectée en < 5s | Partiellement atteint (7s moy) |

## 5. Résumé

Ce plan de test bêta couvre les fonctionnalités essentielles de Sentinel pour la version bêta :
- **16 fonctionnalités** couvrant l'ensemble du flux utilisateur
- **2 rôles utilisateurs** (Utilisateur Standard et Admin)
- **Critères de succès quantifiables** pour chaque fonctionnalité

Le scope bêta se concentre sur :
1. Collecte et visualisation des données de marché
2. Analyse IA avec détection de tendances et volatilité
3. Gouvernance du risque avec alertes et contrôle du drawdown
4. Paper trading pour la validation sans risque réel
5. Contrôle total de l'utilisateur sur le système

Les fonctionnalités avancées (trading réel, modèles IA supplémentaires, backtesting automatisé) sont exclues de ce scope bêta et seront implémentées dans les versions ultérieures.
