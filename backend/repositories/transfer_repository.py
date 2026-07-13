"""
Transfer repository.
"""

from typing import Optional
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from backend.models.models import Transfer, TransferStatus
from backend.repositories.base import BaseRepository


class TransferRepository(BaseRepository[Transfer]):
    model = Transfer

    async def get_by_user(
        self, user_id: int, skip: int = 0, limit: int = 50
    ) -> list[Transfer]:
        result = await self.session.execute(
            select(Transfer)
            .where(
                or_(Transfer.sender_id == user_id, Transfer.receiver_id == user_id)
            )
            .order_by(Transfer.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_pending(self) -> list[Transfer]:
        result = await self.session.execute(
            select(Transfer)
            .where(Transfer.status == TransferStatus.PENDING)
            .options(
                selectinload(Transfer.sender), selectinload(Transfer.receiver)
            )
            .order_by(Transfer.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Transfer]:
        result = await self.session.execute(
            select(Transfer)
            .options(
                selectinload(Transfer.sender), selectinload(Transfer.receiver)
            )
            .order_by(Transfer.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(
        self, sender_id: int, receiver_id: int, amount: float
    ) -> Transfer:
        t = Transfer(
            sender_id=sender_id,
            receiver_id=receiver_id,
            amount=amount,
            status=TransferStatus.PENDING,
        )
        self.session.add(t)
        await self.session.flush()
        await self.session.refresh(t)
        return t

    async def update_status(
        self,
        transfer_id: int,
        status: TransferStatus,
        admin_id: Optional[int] = None,
        note: Optional[str] = None,
    ) -> Optional[Transfer]:
        t = await self.get_by_id(transfer_id)
        if t is None:
            return None
        t.status = status
        if admin_id is not None:
            t.approved_by = admin_id
        if note is not None:
            t.admin_note = note
        await self.session.flush()
        await self.session.refresh(t)
        return t
