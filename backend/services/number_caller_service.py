"""
Number Caller Service — manages server-authoritative number calling for Bingo games.
"""

import asyncio
import secrets
from typing import Optional, Set
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.bingo_models import CalledNumber, BingoGame, GameStatus
from backend.repositories.bingo_game_repository import BingoGameRepository
from backend.repositories.called_number_repository import CalledNumberRepository
from backend.services.cartela_generator_service import CartelaGeneratorService
from backend.core.config import settings
from backend.core.logging import get_logger

logger = get_logger(__name__)


class NumberCallerService:
    """Server-authoritative number caller for Bingo games."""

    MIN_NUMBER = 1
    MAX_NUMBER = 75

    def __init__(self, session: AsyncSession):
        self.session = session
        self.game_repo = BingoGameRepository(session)
        self.called_number_repo = CalledNumberRepository(session)
        self.cartela_generator = CartelaGeneratorService()

    async def call_next_number(self, game_id: int) -> Optional[CalledNumber]:
        """
        Call the next random number for a game.
        
        Args:
            game_id: Game ID
            
        Returns:
            CalledNumber instance or None if all numbers called
            
        Raises:
            ValueError: If game is not in PLAYING status
        """
        async with self.session.begin_nested():
            # Lock game for update
            from sqlalchemy import select
            result = await self.session.execute(
                select(BingoGame).where(BingoGame.id == game_id).with_for_update()
            )
            game = result.scalar_one_or_none()
            
            if not game:
                raise ValueError("Game not found")
            
            if game.status != GameStatus.PLAYING:
                raise ValueError(f"Cannot call numbers for game in status {game.status}")
            
            # Get all called numbers
            called_numbers_list = await self.called_number_repo.get_called_numbers_by_game(game_id)
            called_set = {cn.number for cn in called_numbers_list}
            
            # Check if all numbers have been called
            if len(called_set) >= 75:
                logger.warning("All 75 numbers have been called", game_id=game_id)
                return None
            
            # Get available numbers
            available = [n for n in range(self.MIN_NUMBER, self.MAX_NUMBER + 1) if n not in called_set]
            
            if not available:
                return None
            
            # Select random number using cryptographically secure random
            number = available[secrets.randbelow(len(available))]
            
            # Get column letter
            column_letter = self.cartela_generator.get_column_letter(number)
            
            # Determine sequence
            sequence = len(called_set) + 1
            
            # Create called number record
            called_number = CalledNumber(
                game_id=game_id,
                number=number,
                sequence=sequence,
                column_letter=column_letter,
            )
            self.session.add(called_number)
            
            # Update game
            game.current_number = number
            game.numbers_called_count = sequence
            
            await self.session.flush()
            await self.session.refresh(called_number)

        logger.info(
            "Number called",
            game_id=game_id,
            number=number,
            column_letter=column_letter,
            sequence=sequence,
        )

        return called_number

    async def get_available_numbers(self, game_id: int) -> Set[int]:
        """
        Get set of numbers not yet called for a game.
        
        Args:
            game_id: Game ID
            
        Returns:
            Set of available numbers
        """
        called_numbers = await self.called_number_repo.get_called_numbers_by_game(game_id)
        called_set = {cn.number for cn in called_numbers}
        
        all_numbers = set(range(self.MIN_NUMBER, self.MAX_NUMBER + 1))
        return all_numbers - called_set

    async def get_called_numbers_set(self, game_id: int) -> Set[int]:
        """
        Get set of all called numbers for a game.
        
        Args:
            game_id: Game ID
            
        Returns:
            Set of called numbers
        """
        called_numbers = await self.called_number_repo.get_called_numbers_by_game(game_id)
        return {cn.number for cn in called_numbers}
