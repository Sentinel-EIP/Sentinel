"""Sondes de sante. /health pour Docker, /health/ready pour la CI et le proxy."""

import httpx
from fastapi import APIRouter, Response, status
from sqlalchemy import text
from starlette.concurrency import run_in_threadpool

from app.core.config import get_settings
from app.core.logging import log
from app.db.session import engine

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Le processus repond. Ne teste aucune dependance."""
    return {"status": "ok"}


def _check_database() -> None:
    # Synchrone (psycopg) : appele dans un thread pour ne pas bloquer la boucle.
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))


@router.get("/health/ready")
async def ready(response: Response) -> dict[str, object]:
    """Teste les dependances : base, service ML.

    503 si une dependance manque. Le detail de l'erreur part dans les logs,
    jamais dans la reponse : la route est publique via le proxy.
    """
    checks: dict[str, str] = {}

    try:
        await run_in_threadpool(_check_database)
        checks["database"] = "ok"
    except Exception as exc:  # noqa: BLE001
        log.warning("health.database", error=type(exc).__name__)
        checks["database"] = "error"

    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get(f"{get_settings().ML_SERVICE_URL}/health")
        if r.status_code != 200:
            log.warning("health.ml", status_code=r.status_code)
        checks["ml"] = "ok" if r.status_code == 200 else "error"
    except Exception as exc:  # noqa: BLE001
        log.warning("health.ml", error=type(exc).__name__)
        checks["ml"] = "error"

    healthy = all(v == "ok" for v in checks.values())
    if not healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {"status": "ok" if healthy else "degraded", "checks": checks}
