#!/usr/bin/env bash
# Point d'entree unique pour l'environnement de developpement.
#   ./scripts/dev.sh up|down|logs|ps|migrate|seed|test|lint|shell|reset
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."
COMPOSE="docker compose -f docker-compose.yml -f docker-compose.dev.yml"

[ -f .env ] || { echo "Absence de .env — copier .env.example puis le remplir."; exit 1; }

case "${1:-help}" in
  up)
    $COMPOSE up -d --build
    echo
    echo "  API      http://localhost:8000/docs"
    echo "  ML       http://localhost:8100/docs"
    echo "  Front    http://localhost:5173"
    ;;
  down)    $COMPOSE down ;;
  logs)    $COMPOSE logs -f "${2:-}" ;;
  ps)      $COMPOSE ps ;;
  migrate) $COMPOSE exec api alembic upgrade head ;;
  revision)
    [ -n "${2:-}" ] || { echo "Usage : ./scripts/dev.sh revision \"message\""; exit 1; }
    $COMPOSE exec api alembic revision --autogenerate -m "$2"
    ;;
  seed)    $COMPOSE exec api python -m app.seed ;;
  test)
    $COMPOSE exec api pytest
    $COMPOSE exec ml pytest
    $COMPOSE exec frontend npm run test
    ;;
  lint)
    $COMPOSE exec api ruff check . && $COMPOSE exec api mypy app
    $COMPOSE exec ml ruff check .
    $COMPOSE exec frontend npm run lint
    ;;
  shell)   $COMPOSE exec "${2:-api}" bash ;;
  reset)
    read -rp "Supprimer TOUTES les donnees locales (db, redis, modeles) ? [oui/N] " ok
    [ "$ok" = "oui" ] && $COMPOSE down -v || echo "annule"
    ;;
  *)
    sed -n '2,4p' "$0"
    ;;
esac
