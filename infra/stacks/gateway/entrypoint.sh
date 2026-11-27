#!/bin/sh
# Porte d'entree par VPS — version multi-relais.
#
# - Interface WireGuard `wg0` (noyau), un seul pair : le VPS.
# - Pare-feu : sur wg0, seuls les ports declares dans GATEWAY_RELAYS sont acceptes.
# - Relais : un socat par entree, ecoutant sur l'adresse du tunnel uniquement,
#   sous un utilisateur non root.
#
# GATEWAY_RELAYS : liste "port:hote:port_amont" separee par des espaces.
#   ex. "3000:frontend:3000 3002:nextcloud:80 3003:garage:3900"
# GATEWAY_UPSTREAM reste supporte (equivaut a "3000:$GATEWAY_UPSTREAM").
set -eu

fail() { echo "gateway: $*" >&2; exit 1; }

: "${GATEWAY_PRIVATE_KEY:?GATEWAY_PRIVATE_KEY manquant (cle privee WireGuard : wg genkey)}"
: "${GATEWAY_PEER_PUBLIC_KEY:?GATEWAY_PEER_PUBLIC_KEY manquant (cle publique WireGuard du VPS)}"
: "${GATEWAY_ENDPOINT:?GATEWAY_ENDPOINT manquant (hote:port WireGuard du VPS)}"
ADDRESS="${GATEWAY_ADDRESS:?GATEWAY_ADDRESS manquant (adresse de la gateway dans le tunnel)}"
PEER="${GATEWAY_PEER_ADDRESS:?GATEWAY_PEER_ADDRESS manquant (adresse du VPS dans le tunnel)}"
RELAYS="${GATEWAY_RELAYS:-3000:${GATEWAY_UPSTREAM:-frontend:3000}}"

case "$ADDRESS$PEER" in *[!0-9.]*) fail "adresses de tunnel invalides" ;; esac

# --- validation avant toute action reseau ------------------------------------
for r in $RELAYS; do
  port="${r%%:*}"
  upstream="${r#*:}"
  host="${upstream%:*}"
  upstream_port="${upstream##*:}"
  case "$port" in ''|*[!0-9]*) fail "port de relais invalide : $r" ;; esac
  # Caracteres stricts : une virgule ou un deux-points de plus passerait des
  # options a socat (adresse TCP:hote:port,option=...).
  case "$upstream" in *:*) : ;; *) fail "amont invalide (attendu hote:port) : $r" ;; esac
  case "$host" in ''|*[!a-zA-Z0-9.-]*) fail "hote amont invalide : $r" ;; esac
  case "$upstream_port" in ''|*[!0-9]*) fail "port amont invalide : $r" ;; esac
done

# --- tunnel -------------------------------------------------------------------
ip link del wg0 2>/dev/null || true
ip link add wg0 type wireguard
umask 077
printf '%s' "$GATEWAY_PRIVATE_KEY" > /run/wg.key
wg set wg0 private-key /run/wg.key \
  peer "$GATEWAY_PEER_PUBLIC_KEY" endpoint "$GATEWAY_ENDPOINT" \
  allowed-ips "$PEER/32" persistent-keepalive 25
rm -f /run/wg.key
ip address add "$ADDRESS/32" peer "$PEER/32" dev wg0
ip link set mtu 1420 up dev wg0

# --- pare-feu -----------------------------------------------------------------
iptables -F INPUT
for r in $RELAYS; do
  iptables -A INPUT -i wg0 -p tcp --dport "${r%%:*}" -d "$ADDRESS" -j ACCEPT
done
iptables -A INPUT -i wg0 -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -i wg0 -j DROP
iptables -P FORWARD DROP

# --- relais ---------------------------------------------------------------------
# Un socat par relais. Si l'un meurt, le conteneur sort en erreur et
# `restart: unless-stopped` le relance : pas de relais silencieusement mort.
PIDS=""
for r in $RELAYS; do
  port="${r%%:*}"
  upstream="${r#*:}"
  echo "gateway: relais $ADDRESS:$port -> $upstream"
  socat -d TCP-LISTEN:"$port",bind="$ADDRESS",fork,reuseaddr,su=relay TCP:"$upstream" &
  PIDS="$PIDS $!"
done

echo "gateway: tunnel wg0 $ADDRESS <-> $PEER via $GATEWAY_ENDPOINT"

terminate() {
  # shellcheck disable=SC2086
  kill $PIDS 2>/dev/null || true
  wait
  exit 0
}
trap terminate TERM INT

while :; do
  for p in $PIDS; do
    kill -0 "$p" 2>/dev/null || fail "relais mort (pid $p) — sortie pour redemarrage"
  done
  sleep 5
done
