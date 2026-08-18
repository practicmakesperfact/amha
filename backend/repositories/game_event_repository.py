"""
Game Event repository — database operations for GameEvent model.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.bingo_models import GameEvent, GameEventType
from backend.repositories.base import BaseRepository


class GameEventRepository(BaseRepository[GameEvent]):
    model = GameEvent

    async def get_events_by_game(self, game_id: int, skip: int = 0, limit: int = 100) -> list[GameEvent]:
        """Get all events for a game, ordered by creation time."""
        result = await self.session.execute(
            select(GameEvent)
            .where(GameEvent.game_id == game_id)
            .order_by(GameEvent.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_events_by_type(self, game_id: int, event_type: GameEventType) -> list[GameEvent]:
        """Get all events of a specific type for a game."""
        result = await self.session.execute(
            select(GameEvent)
            .where(GameEvent.game_id == game_id, GameEvent.event_type == event_type)
            .order_by(GameEvent.created_at)
        )
        return list(result.scalars().all())

    async def get_latest_event(self, game_id: int) -> Optional[GameEvent]:
        """Get the most recent event for a game."""
        result = await self.session.execute(
            select(GameEvent)
            .where(GameEvent.game_id == game_id)
            .order_by(GameEvent.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
