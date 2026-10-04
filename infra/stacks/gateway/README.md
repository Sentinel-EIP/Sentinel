# Gateway — modifications a apporter au depot de la gateway

La gateway WireGuard vit dans un autre depot, note `$GATEWAY_REPO` ci-dessous ;
`$SENTINEL_REPO` designe la racine de ce depot-ci.
Trois changements y sont necessaires pour exposer les nouveaux services.

## 1. Remplacer l'entrypoint

```bash
cd "$GATEWAY_REPO"
cp infra/gateway/entrypoint.sh infra/gateway/entrypoint.sh.bak
cp "$SENTINEL_REPO/infra/stacks/gateway/entrypoint.sh" infra/gateway/entrypoint.sh
chmod +x infra/gateway/entrypoint.sh
```

Il generalise le relais unique en liste `GATEWAY_RELAYS` et ajoute un
superviseur : un socat mort fait sortir le conteneur, qui redemarre.
L'ancien comportement est conserve si seul `GATEWAY_UPSTREAM` est defini.

`GATEWAY_ADDRESS` et `GATEWAY_PEER_ADDRESS` n'ont plus de valeur par defaut :
les renseigner dans le `.env` du depot de la gateway, sinon le conteneur refuse
de demarrer.

## 2. Modifier le service `gateway` dans docker-compose.yml

```yaml
  gateway:
    profiles: [gateway]
    build:
      context: .
      dockerfile: infra/docker/Dockerfile.gateway
    # conserver ici la ligne `image:` existante du service
    restart: unless-stopped
    environment:
      GATEWAY_PRIVATE_KEY: ${GATEWAY_PRIVATE_KEY:-}
      GATEWAY_PEER_PUBLIC_KEY: ${GATEWAY_PEER_PUBLIC_KEY:-}
      GATEWAY_ENDPOINT: ${GATEWAY_ENDPOINT:-}
      # Vides par defaut : c'est l'entrypoint qui refuse de demarrer sans elles
      # (un :? ferait echouer toutes les commandes compose, meme hors profil).
      GATEWAY_ADDRESS: ${GATEWAY_ADDRESS:-}
      GATEWAY_PEER_ADDRESS: ${GATEWAY_PEER_ADDRESS:-}
      # NOUVEAU — remplace GATEWAY_UPSTREAM
      GATEWAY_RELAYS: >-
        ${GATEWAY_RELAYS:-3000:frontend:3000
        3002:nextcloud:80
        3003:garage:3900}
    cap_drop: [ALL]
    cap_add: [NET_ADMIN, SETUID, SETGID]
    sysctls:
      net.ipv4.ip_forward: "0"
    depends_on:
      frontend:
        condition: service_healthy
    networks: [edge, sentinel-edge]     # <-- ajout du reseau partage
    mem_limit: ${GATEWAY_MEM:-192m}     # <-- 64m devient juste avec 3 relais
    cpus: ${GATEWAY_CPUS:-0.5}
    logging: *logging
```

Et en bas du fichier :

```yaml
networks:
  edge:
  app:
  data:
  sentinel-edge:
    external: true      # cree par la stack cloud
```

Le port 3001 reste libre. Seule l'API S3 de Garage (3900) est relayee : son
RPC (3901) ne l'est jamais, et Garage n'a pas de console web.

## 3. Assouplir check-isolation.sh

`scripts/check-isolation.sh` verifie que la gateway n'est que sur `edge`.
Elle est maintenant aussi sur `sentinel-edge`. Autoriser ce reseau
explicitement, avec un commentaire justifiant l'exception — ne pas
supprimer le controle.

## Verification

```bash
docker network create --subnet "$EDGE_SUBNET" sentinel-edge   # avant tout, si absent
cd "$SENTINEL_REPO/infra/stacks/cloud" && docker compose up -d
cd "$GATEWAY_REPO" && docker compose --profile gateway up -d --build gateway
docker compose logs gateway | tail -20
```

Attendu (`<adresse>` = `GATEWAY_ADDRESS`) :

```
gateway: relais <adresse>:3000 -> frontend:3000
gateway: relais <adresse>:3002 -> nextcloud:80
gateway: relais <adresse>:3003 -> garage:3900
```

Puis le test de la gateway de son depot doit rester vert.
