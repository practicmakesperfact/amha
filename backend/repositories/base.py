"""
Base repository with common CRUD operations.
"""

from typing import Generic, Optional, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Generic async repository."""

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, id: int) -> Optional[ModelT]:
        result = await self.session.get(self.model, id)
        return result

    async def save(self, instance: ModelT) -> ModelT:
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: ModelT) -> None:
        await self.session.delete(instance)
        await self.session.flush()
