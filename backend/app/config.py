from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    ENVIRONMENT: Literal["dev", "prod", "development", "production"] = "development"
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/cronos",
        min_length=1,
    )
    SECRET_KEY: str = Field(
        default="change-me-with-at-least-32-chars",
        min_length=32,
    )
    TOKEN_EXPIRY: int = Field(default=3600, ge=60)
    REFRESH_TOKEN_EXPIRY: int = Field(default=604800, ge=300)
    SQLALCHEMY_ECHO: bool = False

    BACKEND_URL: str = "http://localhost:8000"
    CORS_DEV_ORIGIN: str = "https://localhost:5173"
    CORS_LOCAL_ORIGIN: str = "http://localhost:5173"
    CORS_VERCEL_REGEX: str = r"https://.*\.vercel\.app"

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        if not value.startswith("postgresql+asyncpg://"):
            raise ValueError("DATABASE_URL must start with 'postgresql+asyncpg://'")
        return value

    @property
    def environment_label(self) -> str:
        if self.ENVIRONMENT in {"dev", "development"}:
            return "development"
        return "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
