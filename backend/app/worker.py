"""Jobs asynchrones : ingestion OHLCV, collecte news, recalculs batch."""
from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery("sentinel", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,          # un worker qui meurt ne perd pas la tache
    worker_prefetch_multiplier=1,
)


@celery_app.task(name="sentinel.ping")
def ping() -> str:
    return "pong"
