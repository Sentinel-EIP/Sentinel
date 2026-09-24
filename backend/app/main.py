from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


@app.on_event("startup")
def on_startup() -> None:
    log.info("api.startup", environment=settings.ENVIRONMENT)
