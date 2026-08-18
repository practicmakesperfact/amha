"""
Called Number repository — database operations for CalledNumber model.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.bingo_models import CalledNumber
from backend.repositories.base import BaseRepository


class CalledNumberRepository(BaseRepository[CalledNumber]):
    model = CalledNumber

    async def get_by_game_and_number(self, game_id: int, number: int) -> Optional[CalledNumber]:
        """Check if a number has been called in a game."""
        result = await self.session.execute(
            select(CalledNumber)
            .where(CalledNumber.game_id == game_id, CalledNumber.number == number)
        )
        return result.scalar_one_or_none()

    async def get_called_numbers_by_game(self, game_id: int) -> list[CalledNumber]:
        """Get all called numbers for a game, ordered by sequence."""
        result = await self.session.execute(
            select(CalledNumber)
            .where(CalledNumber.game_id == game_id)
            .order_by(CalledNumber.sequence)
        )
        return list(result.scalars().all())

    async def get_latest_called_number(self, game_id: int) -> Optional[CalledNumber]:
        """Get the most recently called number for a game."""
        result = await self.session.execute(
            select(CalledNumber)
            .where(CalledNumber.game_id == game_id)
            .order_by(CalledNumber.sequence.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
