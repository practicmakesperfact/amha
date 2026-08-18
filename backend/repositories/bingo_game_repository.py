"""
Bingo Game repository — database operations for BingoGame model.
"""

from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models.bingo_models import BingoGame, GameStatus
from backend.repositories.base import BaseRepository


class BingoGameRepository(BaseRepository[BingoGame]):
    model = BingoGame

    async def get_by_game_number(self, game_number: str) -> Optional[BingoGame]:
        """Get game by game number."""
        result = await self.session.execute(
            select(BingoGame).where(BingoGame.game_number == game_number)
        )
        return result.scalar_one_or_none()

    async def get_with_players(self, game_id: int) -> Optional[BingoGame]:
        """Get game with players eagerly loaded."""
        result = await self.session.execute(
            select(BingoGame)
            .options(selectinload(BingoGame.players))
            .where(BingoGame.id == game_id)
        )
        return result.scalar_one_or_none()

    async def get_active_games(self, skip: int = 0, limit: int = 100) -> list[BingoGame]:
        """Get all non-finished games."""
        result = await self.session.execute(
            select(BingoGame)
            .where(BingoGame.status.in_([GameStatus.WAITING, GameStatus.STARTING, GameStatus.PLAYING, GameStatus.PAUSED]))
            .order_by(BingoGame.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_waiting_games(self, skip: int = 0, limit: int = 100) -> list[BingoGame]:
        """Get games in WAITING status."""
        result = await self.session.execute(
            select(BingoGame)
            .where(BingoGame.status == GameStatus.WAITING)
            .order_by(BingoGame.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_all_games(self, skip: int = 0, limit: int = 100) -> list[BingoGame]:
        """Get all games with pagination."""
        result = await self.session.execute(
            select(BingoGame)
            .order_by(BingoGame.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_status(self, game_id: int, new_status: GameStatus) -> Optional[BingoGame]:
        """Update game status with row locking."""
        result = await self.session.execute(
            select(BingoGame).where(BingoGame.id == game_id).with_for_update()
        )
        game = result.scalar_one_or_none()
        if game:
            game.status = new_status
            await self.session.flush()
            await self.session.refresh(game)
        return game

    async def increment_prize_pool(self, game_id: int, amount: float) -> Optional[BingoGame]:
        """Add amount to prize pool with row locking."""
        result = await self.session.execute(
            select(BingoGame).where(BingoGame.id == game_id).with_for_update()
        )
        game = result.scalar_one_or_none()
        if game:
            game.prize_pool = round(game.prize_pool + amount, 2)
            await self.session.flush()
            await self.session.refresh(game)
        return game
