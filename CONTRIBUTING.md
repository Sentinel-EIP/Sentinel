# Contribuer a Sentinel

## Demarrer

```bash
git clone <depot> && cd SentinelEIP
cp .env.example .env          # remplir POSTGRES_PASSWORD et API_SECRET_KEY
./scripts/dev.sh up
```

| Service  | URL                          |
| -------- | ---------------------------- |
| API      | http://localhost:8000/docs   |
| ML       | http://localhost:8100/docs   |
| Frontend | http://localhost:5173        |
| Postgres | localhost:5432               |

Commandes : `up`, `down`, `logs [service]`, `ps`, `migrate`, `revision "msg"`,
`seed`, `test`, `lint`, `shell [service]`, `reset`.

## Branches

- `main` — production, protegee, build rouge interdit
- `dev` — integration, cible par defaut des PR
- `feat/<scope>-<sujet>`, `fix/<scope>-<sujet>`

## Commits

Conventional Commits, verifies par `commitlint`. Le scope est **obligatoire**.

```
feat(risk): ajoute le plafond de pertes consecutives
fix(api): corrige le code 500 sur symbole inconnu
```

Scopes autorises : `frontend`, `api`, `auth`, `db`, `model`, `data`,
`strategy`, `broker`, `risk`, `core`, `infra`, `config`, `ci`, `cd`, `docs`,
`deps`, `repo`.

## Definition of Done

Une fonctionnalite est terminee quand :

- ses tests unitaires existent et passent ;
- ses cas d'erreur sont verifies ;
- son impact risque est couvert par un test ;
- la CI est verte, sans exception.

Seuils de couverture : backend >= 70 % (modules risque et execution >= 90 %),
frontend >= 60 %.

## Regles produit non negociables

Elles proviennent du dossier technique et du design system, et s'appliquent au
code comme a l'interface :

1. **Aucune prediction de direction.** Le service ML produit des amplitudes,
   des regimes et des scores — jamais une fleche haussiere ni un signal
   d'achat.
2. **Tout score affiche porte sa fiabilite historique mesuree.**
3. **`risk-critical` (rouge) est reserve au depassement d'un seuil de risque.**
   Un chiffre negatif ordinaire s'ecrit en `value-negative`.
4. **L'etat "perime" se declenche sur le heartbeat de la connexion**, jamais
   sur l'absence de variation d'un prix.
5. **Durcir une regle de risque est immediat ; l'assouplir attend 24 h.**

## Secrets

Jamais dans le depot. `gitleaks` tourne sur chaque PR. Les variables passent
par `.env`, documente dans `.env.example`.
