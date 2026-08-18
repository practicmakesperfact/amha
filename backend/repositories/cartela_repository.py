"""
Cartela repository — database operations for Cartela model.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.bingo_models import Cartela
from backend.repositories.base import BaseRepository


class CartelaRepository(BaseRepository[Cartela]):
    model = Cartela

    async def get_by_game_and_user(self, game_id: int, user_id: int) -> Optional[Cartela]:
        """Get cartela by game and user."""
        result = await self.session.execute(
            select(Cartela)
            .where(Cartela.game_id == game_id, Cartela.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_cartela_number(self, cartela_number: str) -> Optional[Cartela]:
        """Get cartela by cartela number."""
        result = await self.session.execute(
            select(Cartela)
            .where(Cartela.cartela_number == cartela_number)
        )
        return result.scalar_one_or_none()

    async def get_cartelas_by_game(self, game_id: int) -> list[Cartela]:
        """Get all cartelas for a game."""
        result = await self.session.execute(
            select(Cartela)
            .where(Cartela.game_id == game_id)
            .order_by(Cartela.created_at)
        )
        return list(result.scalars().all())

    async def get_cartelas_by_user(self, user_id: int) -> list[Cartela]:
        """Get all cartelas for a user."""
        result = await self.session.execute(
            select(Cartela)
            .where(Cartela.user_id == user_id)
            .order_by(Cartela.created_at.desc())
        )
        return list(result.scalars().all())
