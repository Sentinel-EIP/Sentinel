"""Configuration centralisee. Aucune valeur en dur ailleurs dans le code."""

from functools import lru_cache
from typing import Literal
from urllib.parse import quote

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENVIRONMENT: Literal["local", "shared-dev", "staging", "production"] = "local"
    LOG_LEVEL: str = "INFO"

    # Role APPLICATIF (la compose y met APP_DB_USER), jamais le superutilisateur.
    POSTGRES_USER: str = "sentinel_app"
    POSTGRES_PASSWORD: str = ""  # role applicatif : APP_DB_PASSWORD, exige par la compose
    POSTGRES_DB: str = "sentinel"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""

    API_SECRET_KEY: str = ""
    API_CORS_ORIGINS: str = "http://localhost:5173"
    ML_SERVICE_URL: str = "http://ml:8100"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{quote(self.POSTGRES_USER, safe='')}"
            f":{quote(self.POSTGRES_PASSWORD, safe='')}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def redis_url(self) -> str:
        auth = f":{quote(self.REDIS_PASSWORD, safe='')}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.API_CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
