"""
User repository — all database operations for the User model.
"""

from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.models import User
from backend.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone_number: str) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.phone_number == phone_number)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        result = await self.session.execute(
            select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
        )
        return list(result.scalars().all())

    async def search(self, query: str) -> list[User]:
        """Search users by username, phone, or full_name."""
        q = f"%{query}%"
        result = await self.session.execute(
            select(User).where(
                User.username.ilike(q)
                | User.phone_number.ilike(q)
                | User.full_name.ilike(q)
            )
        )
        return list(result.scalars().all())

    async def create_or_update_from_telegram(
        self,
        telegram_id: int,
        chat_id: int,
        username: Optional[str],
        first_name: Optional[str],
        last_name: Optional[str],
    ) -> tuple[User, bool]:
        """
        Upsert a user based on their Telegram identity.
        Returns (user, created) where created=True if newly created.
        """
        user = await self.get_by_telegram_id(telegram_id)
        created = False

        full_name_parts = filter(None, [first_name, last_name])
        full_name = " ".join(full_name_parts) or None

        if user is None:
            user = User(
                telegram_id=telegram_id,
                chat_id=chat_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                full_name=full_name,
            )
            self.session.add(user)
            await self.session.flush()
            await self.session.refresh(user)
            created = True
        else:
            user.chat_id = chat_id
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.full_name = full_name
            await self.session.flush()

        return user, created

    async def complete_registration(
        self,
        telegram_id: int,
        phone_number: str,
    ) -> Optional[User]:
        """Mark user as fully registered and store phone number."""
        user = await self.get_by_telegram_id(telegram_id)
        if user is None:
            return None
        user.phone_number = phone_number
        user.is_registered = True
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def credit_wallet(self, user_id: int, amount: float) -> Optional[User]:
        """Add amount to main wallet."""
        user = await self.get_by_id(user_id)
        if user is None:
            return None
        user.main_wallet = round(user.main_wallet + amount, 2)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def debit_wallet(self, user_id: int, amount: float) -> Optional[User]:
        """Subtract amount from main wallet (caller must check balance first)."""
        user = await self.get_by_id(user_id)
        if user is None:
            return None
        user.main_wallet = round(user.main_wallet - amount, 2)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def transfer_funds(
        self, sender_id: int, receiver_id: int, amount: float
    ) -> tuple[Optional[User], Optional[User]]:
        """Atomically move funds from sender to receiver."""
        sender = await self.get_by_id(sender_id)
        receiver = await self.get_by_id(receiver_id)
        if sender is None or receiver is None:
            return None, None
        sender.main_wallet = round(sender.main_wallet - amount, 2)
        receiver.main_wallet = round(receiver.main_wallet + amount, 2)
        await self.session.flush()
        await self.session.refresh(sender)
        await self.session.refresh(receiver)
        return sender, receiver
