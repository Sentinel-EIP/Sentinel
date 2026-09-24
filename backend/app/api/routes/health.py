"""Sondes de sante. /health pour Docker, /health/ready pour la CI et le proxy."""
import httpx
from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import engine

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Le processus repond. Ne teste aucune dependance."""
    return {"status": "ok"}


@router.get("/health/ready")
async def ready() -> dict[str, object]:
    """Teste les dependances : base, service ML."""
    checks: dict[str, str] = {}

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:  # noqa: BLE001
        checks["database"] = f"error: {type(exc).__name__}"

    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get(f"{get_settings().ML_SERVICE_URL}/health")
            checks["ml"] = "ok" if r.status_code == 200 else f"http {r.status_code}"
    except Exception as exc:  # noqa: BLE001
        checks["ml"] = f"error: {type(exc).__name__}"

    healthy = all(v == "ok" for v in checks.values())
    return {"status": "ok" if healthy else "degraded", "checks": checks}
