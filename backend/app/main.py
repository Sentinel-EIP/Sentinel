from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.routes import health
from app.core.config import get_settings
from app.core.logging import configure_logging, log

configure_logging()
settings = get_settings()

app = FastAPI(
    title="Sentinel API",
    version="0.1.0",
    description="Aide a la decision d'investissement, locale-first et orientee risque.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)

# /metrics : scrape interne par Prometheus (api:8000/metrics), jamais expose par
# le proxy (infra/nginx/nginx.conf). Sous gunicorn, les compteurs des workers
# sont agreges via PROMETHEUS_MULTIPROC_DIR (gunicorn.conf.py).
Instrumentator().instrument(app).expose(app, include_in_schema=False)


@app.on_event("startup")
def on_startup() -> None:
    log.info("api.startup", environment=settings.ENVIRONMENT)
