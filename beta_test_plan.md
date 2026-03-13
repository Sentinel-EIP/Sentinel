# PLAN DE TEST BETA - SENTINEL

## 1. Contexte du Projet

### Contexte

Les systemes automatises d'investissement se democratisent rapidement grace a l'IA et aux plateformes de trading accessibles au grand public. Cependant, ces solutions presentent plusieurs limites :
- Fonctionnement souvent opaque ("boite noire")
- Dependance a des infrastructures cloud
- Optimisation centree sur la performance plutot que la gestion du risque
- Perte de controle pour l'utilisateur

### Objectifs

Sentinel est un systeme d'IA local d'aide et d'execution d'investissement concu pour :
- Analyser les marches financiers via plusieurs modeles d'IA specialises
- Synthetiser ces analyses en signaux comprehensibles
- Proposer ou executer des decisions disciplinees
- Maintenir un controle utilisateur permanent

**Philosophie** : Privilegier la survie du capital face aux differentes conditions de marche plutot que la recherche d'une performance maximale.

### Architecture

Sentinel repose sur une architecture modulaire separant clairement :
1. **Collecte de donnees** : Prix de marche (OHLCV), volumes, indicateurs techniques
2. **Analyse IA** : Modeles specialises (tendances, volatilite, anomalies, stress)
3. **Synthese des signaux** : Agregation des analyses en recommandations
4. **Gouverneur de risque** : Supervision et limitation des risques
5. **Execution** : Application des decisions selon les contraintes definies
6. **Interface utilisateur** : Controle et suivi via navigateur web local

---

## 2. Roles Utilisateurs

Les roles suivants seront impliques dans les tests beta.

| Nom du Role | Description |
|-------------|-------------|
| Admin | Un administrateur gere la configuration systeme, les connexions API, la configuration des sources de donnees et les parametres techniques avances |
| Utilisateur Standard | Un utilisateur regulier qui peut configurer les parametres de risque, consulter les analyses de marche, surveiller les positions, recevoir des alertes et controler les operations du systeme |

---

## 3. Tableau des Fonctionnalites

Toutes les fonctionnalites listees seront demonstrees lors de la presentation beta.

### 3.1 Configuration et Demarrage

| ID | Role Utilisateur | Nom de la Fonctionnalite | Description Courte |
|----|------------------|--------------------------|---------------------|
| F1 | Admin | Configurer les connexions de donnees | Parametrer les sources de donnees de marche et les connexions API pour les flux de prix |
| F2 | Utilisateur Standard | Definir les parametres de risque | Configurer le drawdown maximal, l'exposition maximale et les seuils d'alerte |
| F3 | Utilisateur Standard | Selectionner le mode operatoire | Choisir entre mode analyse seule, paper trading ou trading reel supervise |

### 3.2 Collecte et Visualisation des Donnees

| ID | Role Utilisateur | Nom de la Fonctionnalite | Description Courte |
|----|------------------|--------------------------|---------------------|
| F4 | Utilisateur Standard | Visualiser les donnees de marche | Afficher les prix OHLCV et volumes en temps reel pour les actifs surveilles |
| F5 | Utilisateur Standard | Consulter les indicateurs techniques | Afficher les indicateurs techniques calcules localement sur l'interface |

### 3.3 Analyse IA

| ID | Role Utilisateur | Nom de la Fonctionnalite | Description Courte |
|----|------------------|--------------------------|---------------------|
| F6 | Utilisateur Standard | Analyser les tendances de marche | Obtenir l'analyse de tendance generee par l'IA (haussiere/baissiere/neutre) |
| F7 | Utilisateur Standard | Evaluer le regime de volatilite | Visualiser l'evaluation du niveau de volatilite actuel du marche |
| F8 | Utilisateur Standard | Consulter le signal synthetise | Afficher le signal agrege (achat/vente/attente) issu des analyses combinees |

### 3.4 Gouvernance du Risque

| ID | Role Utilisateur | Nom de la Fonctionnalite | Description Courte |
|----|------------------|--------------------------|---------------------|
| F9 | Utilisateur Standard | Surveiller le drawdown en cours | Visualiser en temps reel le drawdown par rapport au seuil maximal defini |
| F10 | Utilisateur Standard | Recevoir les alertes de risque | Etre notifie lorsqu'un seuil de risque est atteint ou depasse |
| F11 | Utilisateur Standard | Forcer le passage en mode cash | Declencher manuellement la cloture de toutes les positions ouvertes |

### 3.5 Execution et Suivi

| ID | Role Utilisateur | Nom de la Fonctionnalite | Description Courte |
|----|------------------|--------------------------|---------------------|
| F12 | Utilisateur Standard | Executer des operations paper trading | Realiser des operations virtuelles sans engager de capital reel |
| F13 | Utilisateur Standard | Consulter les positions ouvertes | Afficher l'etat actuel des positions (actif, quantite, P&L) |
| F14 | Utilisateur Standard | Acceder a l'historique des decisions | Consulter le journal des decisions passees avec leur justification |

### 3.6 Controle Systeme

| ID | Role Utilisateur | Nom de la Fonctionnalite | Description Courte |
|----|------------------|--------------------------|---------------------|
| F15 | Utilisateur Standard | Arreter le systeme en urgence | Stopper toute activite du systeme en un clic |
| F16 | Utilisateur Standard | Verifier l'etat du systeme | Verifier que tous les modules (collecte, analyse, risque) fonctionnent correctement |

---

## 4. Criteres de Succes

| ID | Critere de Succes Cle | Indicateur/Metrique | Resultat |
|----|----------------------|---------------------|----------|
| F1 | Le systeme se connecte a la source de donnees et recoit les prix | Connexion etablie en < 5s, donnees recues chaque minute | Atteint |
| F2 | Les parametres de risque sont sauvegardes et appliques correctement | 10 configurations testees, 0 echec de sauvegarde | Atteint |
| F3 | Le changement de mode est effectif immediatement | Temps de basculement < 2s, 10 tests, 0 echec | Atteint |
| F4 | Les donnees de marche s'affichent et se mettent a jour automatiquement | Rafraichissement auto, latence < 3s sur 20 tests | Atteint |
| F5 | Les indicateurs techniques sont calcules et affiches correctement | Comparaison avec calcul manuel sur 5 periodes, ecart < 0.1% | Atteint |
| F6 | L'analyse de tendance est generee et coherente avec les conditions du marche | Analyse disponible en < 10s apres demande, 15 tests | Atteint |
| F7 | Le regime de volatilite est identifie correctement | Classification coherente sur 10 scenarios de test | Partiellement atteint (8/10) |
| F8 | Le signal synthetise est disponible et comprehensible | Signal affiche avec niveau de confiance, 100% des cas testes | Atteint |
| F9 | Le drawdown est calcule en temps reel et affiche | Mise a jour chaque seconde, precision 0.01% | Atteint |
| F10 | Les alertes sont declenchees quand les seuils sont atteints | 5 simulations de depassement, 5 alertes recues | Atteint |
| F11 | Le mode cash cloture toutes les positions ouvertes | Test avec 3 positions ouvertes, 100% cloturees en < 5s | Atteint |
| F12 | Les operations paper trading sont enregistrees sans erreur | 20 operations simulees, 0 erreur d'enregistrement | Atteint |
| F13 | Les positions ouvertes sont affichees avec P&L actualise | Mise a jour temps reel, ecart P&L < 0.01% vs calcul manuel | Atteint |
| F14 | L'historique des decisions est complet et accessible | Toutes les decisions des 7 derniers jours accessibles | Atteint |
| F15 | L'arret d'urgence stoppe toutes les activites | Temps d'arret < 1s, aucune operation executee apres arret | Atteint |
| F16 | L'etat du systeme reflete correctement le statut de chaque module | Simulation de panne d'un module detectee en < 5s | Partiellement atteint (7s moy) |

---

## 5. Resume

Ce Plan de Test Beta couvre les fonctionnalites essentielles de Sentinel pour la version beta :
- **16 fonctionnalites** couvrant l'ensemble du flux utilisateur
- **2 roles utilisateurs** (Utilisateur Standard et Admin)
- **Criteres de succes quantifiables** pour chaque fonctionnalite

Le scope beta se concentre sur :
1. Collecte et visualisation des donnees de marche
2. Analyse IA avec detection de tendances et volatilite
3. Gouvernance du risque avec alertes et controle du drawdown
4. Paper trading pour la validation sans risque reel
5. Controle total de l'utilisateur sur le systeme

Les fonctionnalites avancees (trading reel, modeles IA supplementaires, backtesting automatise) sont exclues de ce scope beta et seront implementees dans les versions ulterieures.
