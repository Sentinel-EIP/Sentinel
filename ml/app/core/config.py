from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    LOG_LEVEL: str = "INFO"
    ML_MODEL_CACHE: str = "/models"


@lru_cache
def get_settings() -> Settings:
    return Settings()
