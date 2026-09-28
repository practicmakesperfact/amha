"""
FastAPI application — serves both the Telegram webhook and admin REST API.
"""

import hmac
import hashlib
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request, status
from telegram import Update

from backend.bot.application import build_application
from backend.core.config import settings
from backend.core.logging import configure_logging, get_logger
from backend.core.redis import close_redis, get_redis
from backend.database.session import close_engine, get_engine, get_session_factory

logger = get_logger(__name__)

# Global application instance
_bot_application = None
_auto_number_caller = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup and shutdown lifecycle."""
    global _bot_application, _auto_number_caller

    configure_logging()
    logger.info("AMHABINGO Bot starting up", environment=settings.ENVIRONMENT)

    # Initialize DB engine (creates connection pool)
    get_engine()

    # Initialize Redis
    await get_redis()

    # Build and initialize the bot application
    _bot_application = build_application()
    await _bot_application.initialize()

    # Set webhook if URL is configured, otherwise use polling
    if settings.TELEGRAM_WEBHOOK_URL:
        await _bot_application.bot.set_webhook(
            url=f"{settings.TELEGRAM_WEBHOOK_URL}/webhook",
            secret_token=settings.TELEGRAM_WEBHOOK_SECRET or "",
            allowed_updates=["message", "callback_query"],
        )
        logger.info("Webhook set", url=settings.TELEGRAM_WEBHOOK_URL)
    else:
        logger.info("No webhook URL configured — use polling mode (run_polling)")

    await _bot_application.start()
    logger.info("Bot application started")

    # Start automatic number caller for bingo games
    try:
        from backend.services.auto_number_caller_service import get_auto_caller
        from backend.services.game_engine_service import GameEngineService
        from backend.repositories.bingo_game_repository import BingoGameRepository
        from backend.repositories.game_player_repository import GamePlayerRepository
        from backend.repositories.cartela_repository import CartelaRepository
        from backend.repositories.called_number_repository import CalledNumberRepository
        from backend.repositories.game_event_repository import GameEventRepository
        from backend.services.redis_game_state_service import RedisGameStateService
        
        # Create game engine instance
        session_factory = get_session_factory()
        async with session_factory() as session:
            game_engine = GameEngineService(
                bingo_game_repo=BingoGameRepository(session),
                game_player_repo=GamePlayerRepository(session),
                cartela_repo=CartelaRepository(session),
                called_number_repo=CalledNumberRepository(session),
                game_event_repo=GameEventRepository(session),
                redis_service=RedisGameStateService(),
            )
            
            _auto_number_caller = get_auto_caller()
            _auto_number_caller.start(game_engine)
            logger.info("Automatic number caller started")
    except Exception as e:
        logger.error(f"Failed to start automatic number caller: {e}", exc_info=True)

    yield

    # Shutdown
    logger.info("Shutting down...")
    
    # Stop automatic number caller
    if _auto_number_caller:
        _auto_number_caller.stop()
        logger.info("Automatic number caller stopped")
    
    if _bot_application:
        await _bot_application.stop()
        await _bot_application.shutdown()
    await close_redis()
    await close_engine()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title="AMHABINGO Bot API",
        description="Backend API for AMHABINGO Telegram Bot",
        version="1.0.0",
        lifespan=lifespan,
    )

    # ── Webhook endpoint ───────────────────────────────────────────────────

    @app.post("/webhook")
    async def telegram_webhook(request: Request):
        """Receive Telegram updates via webhook."""
        # Verify webhook secret if configured
        if settings.TELEGRAM_WEBHOOK_SECRET:
            token_header = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
            if token_header != settings.TELEGRAM_WEBHOOK_SECRET:
                logger.warning("Invalid webhook secret token")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid secret token",
                )

        body = await request.json()
        update = Update.de_json(body, _bot_application.bot)

        if update is None:
            return {"ok": True}

        await _bot_application.process_update(update)
        return {"ok": True}

    # ── Health check ───────────────────────────────────────────────────────

    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "service": "amhabingo-bot",
            "version": "1.0.0",
        }

    # ── Include admin router ───────────────────────────────────────────────
    from backend.admin.router import admin_router

    app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])

    # ── Include bingo routes ───────────────────────────────────────────────
    from backend.api.bingo_routes import router as bingo_router
    from backend.api.admin_bingo_routes import router as admin_bingo_router
    from backend.websocket.bingo_websocket import router as ws_bingo_router

    app.include_router(bingo_router)
    app.include_router(admin_bingo_router, prefix="/api")
    app.include_router(ws_bingo_router)

    return app


app = create_app()
