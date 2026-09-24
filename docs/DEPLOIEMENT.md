# Deploiement des services cloud

Ordre imperatif. Chaque etape suppose la precedente reussie.

Les valeurs propres a l'infrastructure (domaines, hote SSH, adresses du
tunnel, reseau Traefik) ne sont pas dans le depot : elles vivent dans les
`.env` locaux, documentes par :

- `infra/stacks/cloud/.env.example` — poste fixe, stack cloud ;
- `infra/vps/relays/.env.example` — VPS, relais Traefik ;
- `scripts/backup-cloud.env.example` — poste fixe, sauvegardes.

Ci-dessous, `$NC_DOMAIN` et `$MINIO_DOMAIN` designent les valeurs de ces
fichiers, `$VPS_SSH` l'hote SSH du VPS, `$GATEWAY_REPO` le depot de la gateway
et `$SENTINEL_REPO` la racine de ce depot.

## Prerequis

- Migration Docker Desktop -> Docker natif WSL2 **terminee et validee**
  (un redemarrage Windows sans ouverture de session doit laisser la gateway
  joignable)
- Enregistrements DNS de type A vers l'IP du VPS pour `$NC_DOMAIN` et
  `$MINIO_DOMAIN`, en DNS only
- Le tunnel WireGuard de la gateway fonctionne (`sudo wg show` sur le VPS)

## 1. Poste fixe — reseau partage

Le reseau doit exister avant que la gateway tente de s'y attacher.

```bash
docker network create sentinel-edge
```

## 2. Poste fixe — stack cloud

```bash
cd infra/stacks/cloud
cp .env.example .env && chmod 600 .env
for i in 1 2 3 4; do openssl rand -hex 24; done   # un par champ *_PASSWORD
nano .env      # + domaines, NC_ADMIN_USER et MINIO_ROOT_USER
docker compose up -d
docker compose logs -f nextcloud
```

Le premier demarrage de Nextcloud prend 2 a 5 minutes : il installe la base
et les applications par defaut. Attendre le healthcheck avant de continuer.

La console MinIO n'est pas publiee sur Internet : elle repond sur
`http://127.0.0.1:${MINIO_CONSOLE_PORT:-9001}` depuis le poste fixe uniquement.

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
mkdir -p ~/docker/nextcloud-relay ~/docker/minio-relay
# copier infra/vps/relays/.env.example en ~/docker/relays.env et le remplir,
# puis chaque infra/vps/relays/<s>/docker-compose.yml dans ~/docker/<s>-relay/
for s in nextcloud minio; do
  (cd ~/docker/$s-relay && docker compose --env-file ~/docker/relays.env up -d)
done
docker logs traefik --tail 30
```

Verifier qu'aucune erreur de routeur n'apparait, et que les services deja
heberges sur le VPS repondent toujours.

**Si le relais `minio-console` a deja ete deploye**, le retirer :

```bash
cd ~/docker/minio-console-relay && docker compose down && cd && rm -r ~/docker/minio-console-relay
```

puis supprimer l'enregistrement DNS correspondant. Cote poste fixe, retirer
`3004:minio:9001` de `GATEWAY_RELAYS` s'il est surcharge dans le `.env` du
depot de la gateway, et redeployer la gateway : sinon la console reste
joignable par le tunnel.

## 5. Validation

```bash
curl -I "https://$NC_DOMAIN"
curl -I "https://$MINIO_DOMAIN/minio/health/live"
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
| 3003 | MinIO API                    | oui, `$MINIO_DOMAIN`|
| —    | MinIO console                | non, 127.0.0.1 seulement |
