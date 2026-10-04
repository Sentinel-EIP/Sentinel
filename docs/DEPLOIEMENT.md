# Deploiement des services cloud

Ordre imperatif. Chaque etape suppose la precedente reussie.

Les valeurs propres a l'infrastructure (domaines, hote SSH, adresses du
tunnel, reseau Traefik) ne sont pas dans le depot : elles vivent dans les
`.env` locaux, documentes par :

- `infra/stacks/cloud/.env.example` — poste fixe, stack cloud ;
- `infra/vps/relays/.env.example` — VPS, relais Traefik ;
- `scripts/backup-cloud.env.example` — poste fixe, sauvegardes.

Ci-dessous, `$NC_DOMAIN` et `$S3_DOMAIN` designent les valeurs de ces
fichiers, `$VPS_SSH` l'hote SSH du VPS, `$GATEWAY_REPO` le depot de la gateway
et `$SENTINEL_REPO` la racine de ce depot.

## Prerequis

- Migration Docker Desktop -> Docker natif WSL2 **terminee et validee**
  (un redemarrage Windows sans ouverture de session doit laisser la gateway
  joignable)
- Enregistrements DNS de type A vers l'IP du VPS pour `$NC_DOMAIN` et
  `$S3_DOMAIN`, en DNS only
- Le tunnel WireGuard de la gateway fonctionne (`sudo wg show` sur le VPS)

## 1. Poste fixe — reseau partage

Le reseau doit exister avant que la gateway tente de s'y attacher. Son
sous-reseau est fixe : Nextcloud ne fait confiance qu'a lui pour
`X-Forwarded-For` (`EDGE_SUBNET` dans `infra/stacks/cloud/.env`).

```bash
docker network create --subnet 172.30.255.0/24 sentinel-edge   # = EDGE_SUBNET
```

Reseau deja cree sans sous-reseau explicite : lire le sien avec
`docker network inspect sentinel-edge -f '{{(index .IPAM.Config 0).Subnet}}'`
et le reporter dans `EDGE_SUBNET`.

## 2. Poste fixe — stack cloud

```bash
cd infra/stacks/cloud
cp .env.example .env && chmod 600 .env
for i in 1 2 3; do openssl rand -hex 24; done   # NC_ADMIN, NC_DB, NC_REDIS
openssl rand -hex 32                            # GARAGE_RPC_SECRET
nano .env      # + domaines et NC_ADMIN_USER
docker compose up -d
docker compose logs -f nextcloud
./garage-init.sh 200G     # une fois : buckets et cles S3 ; capacite du disque
```

`garage-init.sh` affiche les deux cles S3 (`sentinel-app` en lecture/ecriture,
`sentinel-backup` en lecture seule) : les ranger aussitot dans le gestionnaire
de mots de passe.

Le premier demarrage de Nextcloud prend 2 a 5 minutes : il installe la base
et les applications par defaut. Attendre le healthcheck avant de continuer.

Garage n'a pas de console web : il s'administre en ligne de commande,
`docker compose exec garage /garage status` (ou `bucket list`, `key list`...).
Son API S3 repond aussi sur `http://127.0.0.1:${GARAGE_S3_PORT:-3900}`, depuis
le poste fixe uniquement (rclone des sauvegardes). Region S3 : `garage`.

## 3. Poste fixe — gateway

Voir `infra/stacks/gateway/README.md`. En resume : remplacer l'entrypoint,
ajouter `GATEWAY_RELAYS` et le reseau `sentinel-edge` au service, passer
`mem_limit` a 192m, puis :

```bash
cd "$GATEWAY_REPO"
docker compose --profile gateway up -d --build gateway
docker compose logs gateway | tail -20
```

## 4. VPS — relais

```bash
ssh "$VPS_SSH"
mkdir -p ~/docker/nextcloud-relay ~/docker/s3-relay
# copier infra/vps/relays/.env.example en ~/docker/relays.env et le remplir,
# puis chaque infra/vps/relays/<s>/docker-compose.yml dans ~/docker/<s>-relay/
for s in nextcloud s3; do
  (cd ~/docker/$s-relay && docker compose --env-file ~/docker/relays.env up -d)
done
docker logs traefik --tail 30
```

Verifier qu'aucune erreur de routeur n'apparait, et que les services deja
heberges sur le VPS repondent toujours.

**Si d'anciens relais MinIO ont deja ete deployes** (`minio-relay`,
`minio-console-relay`), les retirer :

```bash
for r in minio-relay minio-console-relay; do
  [ -d ~/docker/$r ] && (cd ~/docker/$r && docker compose down) && rm -r ~/docker/$r
done
```

puis supprimer l'enregistrement DNS de la console. Cote poste fixe, retirer
`3003:minio:9000` et `3004:minio:9001` de `GATEWAY_RELAYS` s'ils sont
surcharges dans le `.env` du depot de la gateway, et redeployer la gateway.

## 5. Validation

```bash
curl -I "https://$NC_DOMAIN"
curl -s -o /dev/null -w '%{http_code}\n' "https://$S3_DOMAIN/"   # 403 attendu : S3 sans signature
```

Puis ouvrir `https://$NC_DOMAIN` et se connecter avec `NC_ADMIN_USER`.

**Immediatement apres la premiere connexion** : Parametres > Administration >
Securite, et Parametres > Partage — desactiver le partage public par lien si
l'equipe n'en a pas besoin. Creer ensuite un compte par membre de l'equipe.

## 6. Sauvegardes

Ces services ne sont PAS couverts par le script du VPS : ils tournent sur le
poste fixe. Voir `docs/SAUVEGARDES.md`.

## Ports du tunnel

| Port | Service                      | Expose sur Internet |
| ---- | ---------------------------- | ------------------- |
| 3000 | frontend du depot gateway    | oui                 |
| 3001 | _libre_                      | —                   |
| 3002 | Nextcloud                    | oui, `$NC_DOMAIN`   |
| 3003 | Garage, API S3               | oui, `$S3_DOMAIN`   |
| —    | Garage, RPC (3901)           | non, jamais publie  |
