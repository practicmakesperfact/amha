"""
Game Player repository — database operations for GamePlayer model.
"""

from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models.bingo_models import GamePlayer, PlayerStatus
from backend.repositories.base import BaseRepository


class GamePlayerRepository(BaseRepository[GamePlayer]):
    model = GamePlayer

    async def get_by_game_and_user(self, game_id: int, user_id: int) -> Optional[GamePlayer]:
        """Get player by game and user ID."""
        result = await self.session.execute(
            select(GamePlayer)
            .where(GamePlayer.game_id == game_id, GamePlayer.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_with_cartela(self, player_id: int) -> Optional[GamePlayer]:
        """Get player with cartela eagerly loaded."""
        result = await self.session.execute(
            select(GamePlayer)
            .options(selectinload(GamePlayer.cartela))
            .where(GamePlayer.id == player_id)
        )
        return result.scalar_one_or_none()

    async def get_players_by_game(self, game_id: int) -> list[GamePlayer]:
        """Get all players in a game."""
        result = await self.session.execute(
            select(GamePlayer)
            .where(GamePlayer.game_id == game_id)
            .order_by(GamePlayer.joined_at)
        )
        return list(result.scalars().all())

    async def get_active_players_count(self, game_id: int) -> int:
        """Count active players in a game."""
        result = await self.session.execute(
            select(func.count(GamePlayer.id))
            .where(
                GamePlayer.game_id == game_id,
                GamePlayer.status.in_([PlayerStatus.JOINED, PlayerStatus.ACTIVE])
            )
        )
        return result.scalar() or 0

    async def get_winners_by_game(self, game_id: int) -> list[GamePlayer]:
        """Get all winners in a game, ordered by winning position."""
        result = await self.session.execute(
            select(GamePlayer)
            .where(GamePlayer.game_id == game_id, GamePlayer.is_winner == True)
            .order_by(GamePlayer.winning_position)
        )
        return list(result.scalars().all())

    async def get_players_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[GamePlayer]:
        """Get all games a user has participated in."""
        result = await self.session.execute(
            select(GamePlayer)
            .where(GamePlayer.user_id == user_id)
            .order_by(GamePlayer.joined_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
