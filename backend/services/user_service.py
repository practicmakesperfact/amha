"""
User service — business logic layer for user operations.
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.models import User
from backend.repositories.user_repository import UserRepository
from backend.core.logging import get_logger

logger = get_logger(__name__)


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = UserRepository(session)
        self.session = session

    async def get_or_create_from_telegram(
        self,
        telegram_id: int,
        chat_id: int,
        username: Optional[str],
        first_name: Optional[str],
        last_name: Optional[str],
    ) -> tuple[User, bool]:
        """
        Ensure a user exists for the given Telegram identity.
        Returns (user, created).
        """
        async with self.session.begin_nested():
            user, created = await self.repo.create_or_update_from_telegram(
                telegram_id=telegram_id,
                chat_id=chat_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )

        if created:
            logger.info(
                "New user created",
                telegram_id=telegram_id,
                username=username,
            )
        else:
            logger.debug(
                "Existing user updated",
                telegram_id=telegram_id,
                username=username,
            )
        return user, created

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        return await self.repo.get_by_telegram_id(telegram_id)

    async def get_by_id(self, user_id: int) -> Optional[User]:
        return await self.repo.get_by_id(user_id)

    async def get_by_username(self, username: str) -> Optional[User]:
        cleaned = username.lstrip("@")
        return await self.repo.get_by_username(cleaned)

    async def get_by_phone(self, phone: str) -> Optional[User]:
        return await self.repo.get_by_phone(phone)

    async def register_user(
        self, telegram_id: int, phone_number: str
    ) -> Optional[User]:
        """Complete the registration process for a user."""
        async with self.session.begin_nested():
            user = await self.repo.complete_registration(telegram_id, phone_number)

        if user:
            logger.info(
                "User registered",
                telegram_id=telegram_id,
                phone=phone_number,
            )
        return user

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return await self.repo.get_all(skip=skip, limit=limit)

    async def search_users(self, query: str) -> list[User]:
        return await self.repo.search(query)
