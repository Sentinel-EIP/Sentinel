# Présentation initiale du projet

> [!WARNING]
> Cette présentation date du lancement du projet, avant le recentrage du 30 août 2026. Depuis, la vision validée fait de Sentinel un outil d'accompagnement visuel et de prévention, pas un robot de trading automatique, et l'exécution des trades est repoussée après le MVP. La vision à jour est dans la page « Vision et périmètre du MVP » de l'espace Outline de l'équipe.

Sentinel est un système d’IA local d’aide et d’exécution d’investissement, conçu pour analyser les marchés financiers de manière disciplinée, compréhensible et contrôlable par l’utilisateur.

Aujourd’hui, beaucoup de systèmes d'investissement automatisé promettent des performances irréalistes, reposent sur des boîtes noires ou exposent inutilement le capital. Résultat : perte de contrôle, sur-optimisation et risques mal maîtrisés.

Sentinel prend le contre-pied.

L’objectif n’est pas de « battre le marché », mais de survivre aux marchés, quels que soient leurs régimes.

## À propos de nous

Sentinel est un système d’IA local d’aide et d’exécution d’investissement qui analyse les marchés de façon disciplinée, transparente et sous le contrôle de l’utilisateur. Contrairement aux solutions automatisées opaques et orientées performance à tout prix, Sentinel privilégie la maîtrise du risque et la robustesse. Son objectif n’est pas de battre le marché, mais d’y survivre, quels que soient les régimes.

## Contexte et problématique

Les systèmes automatisés d’investissement se démocratisent rapidement, notamment grâce à l’IA et aux plateformes de trading accessibles au grand public. Cependant, ces solutions présentent plusieurs limites :

- fonctionnement souvent opaque (« boîte noire ») ;
- dépendance à des infrastructures cloud ;
- optimisation centrée sur la performance plutôt que la gestion du risque ;
- perte de contrôle pour l’utilisateur.

Ce projet s’inscrit dans une démarche visant à proposer une alternative plus transparente, contrôlable et orientée robustesse.

## Vision

L’objectif du projet Sentinel est de concevoir un système local capable :

- d’analyser les marchés financiers via plusieurs modèles d’IA spécialisés ;
- de synthétiser ces analyses en signaux compréhensibles ;
- de proposer ou exécuter des décisions disciplinées ;
- tout en maintenant un contrôle utilisateur permanent.

La philosophie du projet est de privilégier la survie du capital face aux différentes conditions de marché plutôt que la recherche d’une performance maximale.

## Mission

Sentinel a pour objectif de supprimer le principal facteur de risque en investissement : le facteur humain et ses émotions, en confiant l’analyse et l’exécution à une IA disciplinée, tout en conservant un contrôle humain total.

## Ça existe déjà ?

Plusieurs solutions existent déjà dans le domaine.

### Bots de trading automatisés

Ils offrent plus de flexibilité mais nécessitent souvent des compétences techniques importantes et restent orientés performance. Sentinel se distingue par :

- une exécution locale ;
- une gouvernance forte du risque ;
- une architecture explicable ;
- une priorité donnée à la robustesse.

### Robo-advisors

Ils proposent une automatisation simplifiée de l’investissement mais restent souvent peu transparents et dépendants d’infrastructures externes.

## Architecture modulaire

Sentinel repose sur une architecture modulaire séparant clairement :

- la collecte de données de marché ;
- l’analyse par modèles IA spécialisés ;
- la synthèse des signaux ;
- l’exécution des décisions ;
- un gouverneur de risque supervisant l’ensemble.

Cette séparation vise à améliorer la lisibilité du système, limiter les biais décisionnels et renforcer la sécurité.

## Collecte et gestion des données

Le système collecte différents types de données :

- prix de marché (OHLCV) ;
- volumes ;
- indicateurs techniques calculés localement ;
- éventuellement flux macroéconomiques ou news.

Les données sont stockées localement afin de garantir :

- indépendance vis-à-vis du cloud ;
- confidentialité ;
- traçabilité complète des décisions.

## Modèles d'IA analystes

Plusieurs modèles spécialisés sont utilisés pour analyser l’état du marché :

- détection de tendances ;
- identification de régimes de volatilité ;
- détection d’anomalies statistiques ;
- évaluation du stress global du marché.

Ces modèles n’ont pas vocation à prendre des décisions directes, mais à fournir une description structurée du contexte.

## Gouverneur de risque

Le gouverneur de risque constitue un élément central du système. Il peut notamment :

- limiter le drawdown maximal ;
- réduire l’exposition en cas de volatilité excessive ;
- suspendre automatiquement le trading ;
- forcer un passage en mode cash.

Ce module garantit que l’exécution reste toujours dans un cadre maîtrisé.

## Interface utilisateur

Sentinel intègre une interface locale accessible via navigateur. Elle permet :

- le suivi de l’état du marché et du système ;
- la consultation des positions ouvertes ;
- l’accès à l’historique des décisions ;
- l’ajustement des paramètres de risque ;
- l’arrêt immédiat du système si nécessaire.

L’utilisateur conserve ainsi un contrôle permanent.

## Cas d’utilisation

| Mode | Principe |
|---|---|
| Analyse seule | Surveillance du marché sans exécution automatique |
| Paper trading | Simulation d’investissement sans engagement réel |
| Trading réel encadré | Exécution disciplinée sous contraintes de risque définies |

Cette modularité permet une adoption progressive du système.

## Validation et méthodologie

La validation du système repose sur :

- backtesting sur données historiques ;
- simulations en paper trading ;
- analyse des métriques de robustesse.

Les indicateurs suivis incluent notamment :

- drawdown ;
- ratio gain/perte ;
- fréquence de trading ;
- performance selon différents régimes de marché.

## Limites du projet

Certaines limites sont reconnues :

- absence de garantie de performance ;
- dépendance à la qualité des données ;
- complexité inhérente aux marchés financiers ;
- risque d’overfitting des modèles.

Le projet est avant tout expérimental et pédagogique.

## Planning prévisionnel

Le projet est structuré en plusieurs phases :

- recherche bibliographique et conception ;
- développement des modules IA ;
- mise en place de l’architecture logicielle ;
- développement de l’interface utilisateur ;
- tests, validation et documentation.

## Livrables attendus

Les livrables incluent :

- le code source complet du système ;
- une documentation technique détaillée ;
- une interface fonctionnelle ;
- des résultats de backtesting ;
- un rapport scientifique complet.

## Conclusion

Sentinel propose une approche prudente de l’automatisation de l’investissement, privilégiant :

- transparence ;
- contrôle utilisateur ;
- gestion stricte du risque ;
- autonomie locale.

Ce projet vise à démontrer la faisabilité d’un système d’IA financière discipliné, explicable et centré sur la robustesse.
