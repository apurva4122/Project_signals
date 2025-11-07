"""Application settings and configuration helpers."""

from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseModel):
    url: str = Field(default="postgresql+asyncpg://signals:signals@localhost:5432/signals")
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20


class RedisSettings(BaseModel):
    url: str = Field(default="redis://localhost:6379/0")
    stream_name: str = "signals-stream"


class WebhookSecrets(BaseModel):
    chartink_token: str | None = None
    tradingview_token: str | None = None
    hmac_secret: str | None = None


class AppSettings(BaseSettings):
    """Base application settings loaded from environment variables or .env"""

    model_config = SettingsConfigDict(env_file=('.env', '.env.local'), env_prefix="PROJECT_SIGNALS_", extra="allow")

    api_title: str = "Project Signals API"
    api_description: str = (
        "Paper trading and backtesting platform for Indian equities, futures, and options."
    )
    api_version: str = "0.1.0"
    environment: str = "development"
    docs_url: str | None = "/docs"
    redoc_url: str | None = "/redoc"
    openapi_url: str = "/openapi.json"
    enable_cors: bool = True
    allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173", "http://localhost:3000"])

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    webhook_secrets: WebhookSecrets = Field(default_factory=WebhookSecrets)

    data_path: Path = Field(default=Path("data"))
    historical_cache_path: Path = Field(default=Path("data/cache"))
    strategy_path: Path = Field(default=Path("backend/strategies"))


Settings = Annotated[AppSettings, "Application settings singleton"]


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Return cached application settings"""

    return AppSettings()


