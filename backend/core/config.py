"""
Core configuration module for AMHABINGO Bot.
Loads settings from environment variables with validation.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Telegram ──────────────────────────────────────────────
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_WEBHOOK_URL: Optional[str] = None
    TELEGRAM_WEBHOOK_SECRET: Optional[str] = None

    # ── PostgreSQL ────────────────────────────────────────────
    DATABASE_URL: str  # asyncpg DSN: postgresql+asyncpg://user:pass@host/db

    # ── Redis ─────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Admin / Business Logic ────────────────────────────────
    TELEBIRR_RECEIVER_NUMBER: str = "0909425014"
    SUPPORT_CHANNEL_URL: str = "https://t.me/amhabingosupport_team"
    BOT_USERNAME: str = "AMHABINGOBOT"
    ADMIN_TELEGRAM_IDS: list[int] = []  # list of admin Telegram user IDs

    # ── Limits ────────────────────────────────────────────────
    MIN_DEPOSIT_AMOUNT: float = 10.0
    MIN_WITHDRAWAL_AMOUNT: float = 50.0
    MIN_TRANSFER_AMOUNT: float = 10.0

    # ── Rate Limiting ─────────────────────────────────────────
    RATE_LIMIT_MAX_REQUESTS: int = 30
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # ── App ───────────────────────────────────────────────────
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "production"

    # ── Mini App ──────────────────────────────────────────────
    MINI_APP_URL: Optional[str] = None  # Set this when Mini App is ready


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
