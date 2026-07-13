"""
Polling entrypoint for local development.
Run this file directly instead of the FastAPI server when you don't have
a public HTTPS URL for webhooks.

Usage:
    python -m backend.run_polling
"""

import asyncio

from backend.core.config import settings
from backend.core.logging import configure_logging, get_logger
from backend.core.redis import close_redis, get_redis
from backend.database.session import close_engine, get_engine
from backend.bot.application import build_application

configure_logging()
logger = get_logger(__name__)


def main() -> None:
    logger.info(
        "Starting AMHABINGO Bot in POLLING mode",
        environment=settings.ENVIRONMENT,
    )

    # Build and run the application
    application = build_application()

    logger.info("Bot polling starting — press Ctrl+C to stop")
    application.run_polling(
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True,
        close_loop=True,
    )
    logger.info("Bot stopped")


if __name__ == "__main__":
    main()
