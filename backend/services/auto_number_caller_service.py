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
        """Call numbers for all PLAYING games and check time limits."""
        if not self.game_engine:
            return

        from backend.database.session import get_session_factory
        
        try:
            factory = get_session_factory()
            async with factory() as session:
                from backend.repositories.bingo_game_repository import BingoGameRepository
                game_repo = BingoGameRepository(session)
                
                # Get all PLAYING games
                games = await game_repo.get_games_by_status(GameStatus.PLAYING)

                for game in games:
                    try:
                        # Check if game has exceeded 5 minute time limit
                        if game.started_at:
                            from datetime import datetime, timezone
                            now = datetime.now(timezone.utc)
                            elapsed_seconds = (now - game.started_at).total_seconds()
                            max_duration = 5 * 60  # 5 minutes in seconds
                            
                            if elapsed_seconds >= max_duration:
                                # Time limit exceeded
                                logger.warning(
                                    f"Game {game.id} exceeded 5 minute limit "
                                    f"({elapsed_seconds:.0f}s), checking for winners"
                                )
                                
                                async with session.begin():
                                    from backend.repositories.game_player_repository import GamePlayerRepository
                                    from backend.services.game_engine_service import GameEngineService
                                    
                                    player_repo = GamePlayerRepository(session)
                                    winners = await player_repo.get_winners_by_game(game.id)
                                    
                                    if not winners:
                                        # No winners - house wins!
                                        engine = GameEngineService(session)
                                        await engine._handle_no_winner_house_wins(game.id)
                                        await session.commit()
                                        logger.info(f"Game {game.id} finished - house wins (time limit)")
                                    else:
                                        # Has winners - already finished
                                        logger.info(f"Game {game.id} already has winners, skipping")
                                
                                continue
                        
                        # Call next number using the game engine
                        async with session.begin():
                            from backend.services.game_engine_service import GameEngineService
                            engine = GameEngineService(session)
                            called_number, new_winners = await engine.call_number_and_check_winners(game.id)
                            await session.commit()
                            
                            if called_number:
                                logger.info(
                                    f"Auto-called number {called_number.number} for game {game.id}"
                                )
                            
                            if new_winners:
                                logger.info(
                                    f"Winners found in game {game.id}: {len(new_winners)} player(s)"
                                )

                    except Exception as e:
                        logger.error(
                            f"Error processing game {game.id}: {e}",
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
