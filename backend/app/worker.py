"""Jobs asynchrones : ingestion OHLCV, collecte news, recalculs batch.

Le service `scheduler` (celery beat) declenche les taches periodiques ; le
service `worker` les execute.
"""

from datetime import UTC, datetime
from typing import Any

import httpx
from celery import Celery
from celery.signals import worker_ready

from app.core.config import get_settings
from app.core.logging import configure_logging, log

settings = get_settings()
configure_logging()

celery_app = Celery("sentinel", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,  # un worker qui meurt ne perd pas la tache
    worker_prefetch_multiplier=1,
    beat_schedule={
        # Bougies 1h : un passage tous les quarts d'heure suffit a rester a jour.
        "collect-candles": {"task": "sentinel.collect_candles", "schedule": 15 * 60.0},
    },
)


@worker_ready.connect
def collect_on_start(**_: Any) -> None:
    """Premiere collecte des le demarrage du worker, sans attendre le planificateur."""
    celery_app.send_task("sentinel.collect_candles")


@celery_app.task(name="sentinel.ping")
def ping() -> str:
    return "pong"


@celery_app.task(name="sentinel.collect_candles")
def collect_candles() -> dict[str, int]:
    """Collecte chaque symbole et chaque timeframe configures.

    Un symbole en erreur (Binance indisponible, symbole inconnu) n'empeche pas
    les autres : l'erreur est journalisee, le prochain passage reprend.
    """
    # Imports differes : le scheduler importe ce module sans acces a la base.
    from sqlmodel import Session

    from app.db.session import engine
    from app.services.market import collect

    now = datetime.now(UTC)
    written: dict[str, int] = {}
    with (
        Session(engine) as session,
        httpx.Client(base_url=settings.BINANCE_BASE_URL, timeout=10) as client,
    ):
        for symbol in settings.market_symbols:
            for timeframe in settings.market_timeframes:
                key = f"{symbol}:{timeframe}"
                try:
                    written[key] = collect(
                        session, client, symbol, timeframe, now, settings.MARKET_BACKFILL_DAYS
                    )
                except Exception as exc:  # noqa: BLE001
                    session.rollback()
                    log.warning("market.collect_failed", key=key, error=type(exc).__name__)
                    written[key] = -1
    log.info("market.collected", **written)
    return written
