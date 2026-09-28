"""
Automatic Number Caller Service - Background task for calling numbers automatically.
"""

import asyncio
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.core.config import get_settings
from backend.core.logging import get_logger
from backend.services.game_engine_service import GameEngineService
from backend.models.bingo_models import GameStatus

logger = get_logger(__name__)
settings = get_settings()


class AutoNumberCallerService:
    """
    Automatic number caller service using APScheduler.
    Calls numbers for all PLAYING games at configured interval.
    """

    def __init__(self):
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.is_running = False
        self.game_engine: Optional[GameEngineService] = None

    def start(self, game_engine: GameEngineService):
        """Start the automatic number caller."""
        if self.is_running:
            logger.warning("Auto number caller already running")
            return

        self.game_engine = game_engine
        self.scheduler = AsyncIOScheduler()
        
        # Schedule number calling task
        self.scheduler.add_job(
            self._call_numbers_for_active_games,
            trigger=IntervalTrigger(seconds=settings.BINGO_NUMBER_INTERVAL_SECONDS),
            id="auto_number_caller",
            replace_existing=True,
            max_instances=1,
        )
        
        self.scheduler.start()
        self.is_running = True
        logger.info(
            f"Auto number caller started (interval: {settings.BINGO_NUMBER_INTERVAL_SECONDS}s)"
        )

    def stop(self):
        """Stop the automatic number caller."""
        if not self.is_running or not self.scheduler:
            return

        self.scheduler.shutdown(wait=False)
        self.is_running = False
        self.scheduler = None
        logger.info("Auto number caller stopped")

    async def _call_numbers_for_active_games(self):
        """Call numbers for all PLAYING games."""
        if not self.game_engine:
            return

        try:
            # Get all PLAYING games
            games = await self.game_engine.bingo_game_repo.get_games_by_status(
                GameStatus.PLAYING
            )

            for game in games:
                try:
                    # Check if game still has numbers to call
                    state = await self.game_engine.redis_service.get_game_state(game.id)
                    
                    if not state:
                        logger.warning(f"No Redis state for game {game.id}, skipping")
                        continue

                    available_numbers = state.get("available_numbers", [])
                    
                    if not available_numbers:
                        # No more numbers to call, finish game
                        logger.info(f"Game {game.id} has no more numbers, finishing")
                        await self.game_engine.finish_game(game.id)
                        continue

                    # Call next number
                    result = await self.game_engine.call_number(game.id)
                    
                    if result:
                        logger.info(
                            f"Auto-called number {result['number']} "
                            f"({result['column']}) for game {game.id}"
                        )

                except Exception as e:
                    logger.error(
                        f"Error calling number for game {game.id}: {e}",
                        exc_info=True
                    )
                    continue

        except Exception as e:
            logger.error(f"Error in auto number caller: {e}", exc_info=True)


# Global instance
_auto_caller: Optional[AutoNumberCallerService] = None


def get_auto_caller() -> AutoNumberCallerService:
    """Get the global auto number caller instance."""
    global _auto_caller
    if _auto_caller is None:
        _auto_caller = AutoNumberCallerService()
    return _auto_caller
