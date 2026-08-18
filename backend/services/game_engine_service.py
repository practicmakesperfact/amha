"""
Game Engine Service — orchestrates complete Bingo game lifecycle.
"""

import json
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.bingo_models import (
    BingoGame,
    GamePlayer,
    GameStatus,
    PlayerStatus,
    GameEventType,
)
from backend.repositories.bingo_game_repository import BingoGameRepository
from backend.repositories.game_player_repository import GamePlayerRepository
from backend.repositories.called_number_repository import CalledNumberRepository
from backend.services.number_caller_service import NumberCallerService
from backend.services.winner_validator_service import WinnerValidatorService
from backend.services.prize_distribution_service import PrizeDistributionService
from backend.services.game_state_service import GameStateService
from backend.core.logging import get_logger

logger = get_logger(__name__)


class GameEngineService:
    """Orchestrates complete game lifecycle and winner processing."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.game_repo = BingoGameRepository(session)
        self.player_repo = GamePlayerRepository(session)
        self.called_number_repo = CalledNumberRepository(session)
        self.number_caller = NumberCallerService(session)
        self.winner_validator = WinnerValidatorService()
        self.prize_distributor = PrizeDistributionService(session)
        self.state_service = GameStateService()

    async def start_game(self, game_id: int) -> BingoGame:
        """
        Start a game if requirements are met.
        
        Args:
            game_id: Game ID
            
        Returns:
            Updated BingoGame
            
        Raises:
            ValueError: If game cannot be started
        """
        async with self.session.begin_nested():
            from sqlalchemy import select
            
            # Lock game for update
            result = await self.session.execute(
                select(BingoGame).where(BingoGame.id == game_id).with_for_update()
            )
            game = result.scalar_one_or_none()
            
            if not game:
                raise ValueError("Game not found")
            
            if game.status != GameStatus.WAITING:
                raise ValueError(f"Cannot start game in status {game.status}")
            
            # Check minimum players
            player_count = await self.player_repo.get_active_players_count(game_id)
            if player_count < game.min_players:
                raise ValueError(
                    f"Need at least {game.min_players} players (current: {player_count})"
                )
            
            # Update game status
            game.status = GameStatus.PLAYING
            game.started_at = datetime.utcnow()
            
            # Log event
            from backend.models.bingo_models import GameEvent
            event = GameEvent(
                game_id=game_id,
                event_type=GameEventType.GAME_STARTED,
                description=f"Game started with {player_count} players",
            )
            self.session.add(event)
            
            await self.session.flush()
            await self.session.refresh(game)
        
        # Update Redis state
        await self.state_service.set_game_state(
            game_id=game_id,
            status=game.status.value,
            player_count=player_count,
            prize_pool=game.prize_pool,
        )
        
        # Publish event
        await self.state_service.publish_event(
            game_id=game_id,
            event_type="GAME_STARTED",
            event_data={"player_count": player_count},
        )
        
        logger.info("Game started", game_id=game_id, player_count=player_count)
        return game

    async def call_number_and_check_winners(self, game_id: int) -> Optional[List[GamePlayer]]:
        """
        Call next number and check for winners.
        
        Args:
            game_id: Game ID
            
        Returns:
            List of new winners (if any)
        """
        # Call next number
        called_number = await self.number_caller.call_next_number(game_id)
        
        if not called_number:
            logger.warning("No more numbers to call", game_id=game_id)
            return None
        
        # Add to Redis
        await self.state_service.add_called_number(game_id, called_number.number)
        
        # Update game state
        game = await self.game_repo.get_by_id(game_id)
        if game:
            player_count = await self.player_repo.get_active_players_count(game_id)
            await self.state_service.set_game_state(
                game_id=game_id,
                status=game.status.value,
                current_number=called_number.number,
                numbers_called_count=called_number.sequence,
                player_count=player_count,
                prize_pool=game.prize_pool,
            )
        
        # Publish number called event
        await self.state_service.publish_event(
            game_id=game_id,
            event_type="NUMBER_CALLED",
            event_data={
                "number": called_number.number,
                "column_letter": called_number.column_letter,
                "sequence": called_number.sequence,
            },
        )
        
        # Check for winners
        winners = await self.check_for_winners(game_id)
        
        return winners

    async def check_for_winners(self, game_id: int) -> List[GamePlayer]:
        """
        Check all active players for winning conditions.
        
        Args:
            game_id: Game ID
            
        Returns:
            List of new winners
        """
        # Get all called numbers
        called_numbers_set = await self.number_caller.get_called_numbers_set(game_id)
        
        # Get all active players
        players = await self.player_repo.get_players_by_game(game_id)
        active_players = [
            p for p in players
            if p.status in [PlayerStatus.JOINED, PlayerStatus.ACTIVE]
            and not p.is_winner
        ]
        
        new_winners = []
        
        for player in active_players:
            # Get player's cartela
            if not player.cartela_id:
                continue
            
            from backend.repositories.cartela_repository import CartelaRepository
            cartela_repo = CartelaRepository(self.session)
            cartela = await cartela_repo.get_by_id(player.cartela_id)
            
            if not cartela:
                continue
            
            # Validate winner
            is_winner, win_pattern = self.winner_validator.validate_winner(
                cartela_json=cartela.numbers,
                called_numbers=called_numbers_set,
            )
            
            if is_winner:
                # Mark as winner
                async with self.session.begin_nested():
                    player.is_winner = True
                    player.status = PlayerStatus.WINNER
                    player.win_pattern = win_pattern
                    await self.session.flush()
                
                new_winners.append(player)
                
                logger.info(
                    "Winner detected",
                    game_id=game_id,
                    user_id=player.user_id,
                    pattern=win_pattern.value,
                )
        
        # If we have winners, process prizes
        if new_winners:
            await self.process_winners(game_id, new_winners)
        
        return new_winners

    async def process_winners(self, game_id: int, new_winners: List[GamePlayer]) -> None:
        """
        Process winners: assign positions, pay prizes, finish game.
        
        Args:
            game_id: Game ID
            new_winners: List of new winners
        """
        # Get all winners (including previously declared)
        all_winners = await self.player_repo.get_winners_by_game(game_id)
        
        # Assign winning positions
        async with self.session.begin_nested():
            for idx, winner in enumerate(new_winners):
                position = len(all_winners) - len(new_winners) + idx + 1
                winner.winning_position = position
            await self.session.flush()
        
        # Distribute prizes
        try:
            await self.prize_distributor.distribute_prizes(game_id)
        except Exception as e:
            logger.error("Failed to distribute prizes", error=str(e), game_id=game_id)
        
        # Publish winner events
        for winner in new_winners:
            await self.state_service.publish_event(
                game_id=game_id,
                event_type="WINNER_DECLARED",
                event_data={
                    "user_id": winner.user_id,
                    "winning_position": winner.winning_position,
                    "win_pattern": winner.win_pattern.value if winner.win_pattern else None,
                    "prize_amount": winner.prize_amount,
                },
            )
        
        # Check if game should finish (e.g., first winner = game over)
        # For now, continue until manually finished or all numbers called
        # You can customize this logic based on game rules

    async def finish_game(self, game_id: int) -> BingoGame:
        """
        Finish a game.
        
        Args:
            game_id: Game ID
            
        Returns:
            Updated BingoGame
        """
        async with self.session.begin_nested():
            from sqlalchemy import select
            
            result = await self.session.execute(
                select(BingoGame).where(BingoGame.id == game_id).with_for_update()
            )
            game = result.scalar_one_or_none()
            
            if not game:
                raise ValueError("Game not found")
            
            if game.status not in [GameStatus.PLAYING, GameStatus.PAUSED]:
                raise ValueError(f"Cannot finish game in status {game.status}")
            
            # Update status
            game.status = GameStatus.FINISHED
            game.finished_at = datetime.utcnow()
            
            # Log event
            from backend.models.bingo_models import GameEvent
            event = GameEvent(
                game_id=game_id,
                event_type=GameEventType.GAME_FINISHED,
                description="Game finished",
            )
            self.session.add(event)
            
            await self.session.flush()
            await self.session.refresh(game)
        
        # Update Redis
        await self.state_service.set_game_state(
            game_id=game_id,
            status=game.status.value,
            current_number=game.current_number,
            numbers_called_count=game.numbers_called_count,
            prize_pool=game.prize_pool,
        )
        
        # Publish event
        winners = await self.player_repo.get_winners_by_game(game_id)
        await self.state_service.publish_event(
            game_id=game_id,
            event_type="GAME_FINISHED",
            event_data={
                "winner_count": len(winners),
                "winners": [
                    {
                        "user_id": w.user_id,
                        "position": w.winning_position,
                        "prize": w.prize_amount,
                    }
                    for w in winners
                ],
            },
        )
        
        logger.info("Game finished", game_id=game_id, winners=len(winners))
        return game

    async def pause_game(self, game_id: int) -> BingoGame:
        """Pause a playing game."""
        async with self.session.begin_nested():
            game = await self.game_repo.update_status(game_id, GameStatus.PAUSED)
            if game:
                game.paused_at = datetime.utcnow()
                await self.session.flush()
        
        if game:
            await self.state_service.set_game_state(
                game_id=game_id,
                status=game.status.value,
                current_number=game.current_number,
                numbers_called_count=game.numbers_called_count,
            )
            
            await self.state_service.publish_event(
                game_id=game_id,
                event_type="GAME_PAUSED",
                event_data={},
            )
        
        return game

    async def resume_game(self, game_id: int) -> BingoGame:
        """Resume a paused game."""
        async with self.session.begin_nested():
            game = await self.game_repo.update_status(game_id, GameStatus.PLAYING)
            await self.session.flush()
        
        if game:
            await self.state_service.set_game_state(
                game_id=game_id,
                status=game.status.value,
                current_number=game.current_number,
                numbers_called_count=game.numbers_called_count,
            )
            
            await self.state_service.publish_event(
                game_id=game_id,
                event_type="GAME_RESUMED",
                event_data={},
            )
        
        return game
