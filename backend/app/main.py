from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.routes import auth, health, users
from app.core.config import get_settings
from app.core.errors import install_error_handlers
from app.core.logging import configure_logging, log
from app.core.security import check_secret_key

configure_logging()
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    check_secret_key()
    log.info("api.startup", environment=settings.ENVIRONMENT)
    yield


app = FastAPI(
    title="Sentinel API",
    version="0.1.0",
    description="Aide a la decision d'investissement, locale-first et orientee risque.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

install_error_handlers(app)
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)

# /metrics : scrape interne par Prometheus (api:8000/metrics), jamais expose par
# le proxy (infra/nginx/nginx.conf). Sous gunicorn, les compteurs des workers
# sont agreges via PROMETHEUS_MULTIPROC_DIR (gunicorn.conf.py).
Instrumentator().instrument(app).expose(app, include_in_schema=False)
