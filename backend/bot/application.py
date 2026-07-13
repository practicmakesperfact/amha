"""
Bot application factory.
Assembles all handlers and configures the PTB Application.
"""

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.handlers.dispatcher import message_dispatcher
from backend.handlers.register_handler import contact_handler
from backend.handlers.start_handler import start_handler
from backend.handlers.admin_handler import admin_callback_handler

logger = get_logger(__name__)


async def post_init(application: Application) -> None:
    """Initialize DB and Redis connection."""
    from backend.database.session import get_engine
    from backend.core.redis import get_redis
    get_engine()
    await get_redis()
    logger.info("Application post_init hooks completed")


async def post_stop(application: Application) -> None:
    """Close DB and Redis connection."""
    from backend.database.session import close_engine
    from backend.core.redis import close_redis
    await close_redis()
    await close_engine()
    logger.info("Application post_stop hooks completed")


def build_application() -> Application:
    """
    Build and configure the python-telegram-bot Application.
    All handlers are registered here.
    """
    application = (
        Application.builder()
        .token(settings.TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .post_stop(post_stop)
        .build()
    )

    # ── Command handlers ───────────────────────────────────────────────────
    application.add_handler(CommandHandler("start", start_handler))

    # ── Contact handler (for registration) ────────────────────────────────
    application.add_handler(
        MessageHandler(filters.CONTACT, contact_handler)
    )

    # ── Admin callback query handler ───────────────────────────────────────
    application.add_handler(
        CallbackQueryHandler(admin_callback_handler, pattern=r"^admin:")
    )

    # ── General message dispatcher (menu buttons + FSM states) ────────────
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_dispatcher)
    )

    # ── Error handler ──────────────────────────────────────────────────────
    application.add_error_handler(_global_error_handler)

    logger.info("Bot application built successfully")
    return application


async def _global_error_handler(update: object, context) -> None:
    """Global error handler — logs all unhandled exceptions."""
    logger.error(
        "Unhandled exception in bot",
        error=str(context.error),
        update=str(update)[:200] if update else "N/A",
        exc_info=context.error,
    )
