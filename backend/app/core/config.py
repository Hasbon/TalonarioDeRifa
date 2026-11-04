from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_database_url(url: str) -> str:
    """Heroku Postgres delivers postgres://; SQLAlchemy + psycopg need postgresql+psycopg://."""
    if url.startswith("postgres://"):
        url = "postgresql://" + url.removeprefix("postgres://")
    if url.startswith("postgresql://") and not url.startswith("postgresql+"):
        url = "postgresql+psycopg://" + url.removeprefix("postgresql://")
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "sqlite:///./rifa_dev.db"
    SECRET_KEY: str = "dev-only-change-in-production-use-long-secret"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    PUBLIC_BASE_URL: str = "http://localhost:5173"
    TIMEZONE: str = "America/Bogota"
    LOGIN_RATE_LIMIT: str = "10/minute"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _normalize_database_url(cls, value: object) -> object:
        if isinstance(value, str):
            return normalize_database_url(value)
        return value

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
