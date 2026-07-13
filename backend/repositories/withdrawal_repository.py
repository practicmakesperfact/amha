"""
Withdrawal repository.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.models.models import Withdrawal, WithdrawalStatus
from backend.repositories.base import BaseRepository


class WithdrawalRepository(BaseRepository[Withdrawal]):
    model = Withdrawal

    async def get_by_user(
        self, user_id: int, skip: int = 0, limit: int = 50
    ) -> list[Withdrawal]:
        result = await self.session.execute(
            select(Withdrawal)
            .where(Withdrawal.user_id == user_id)
            .order_by(Withdrawal.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_pending(self) -> list[Withdrawal]:
        result = await self.session.execute(
            select(Withdrawal)
            .where(Withdrawal.status == WithdrawalStatus.PENDING)
            .options(selectinload(Withdrawal.user))
            .order_by(Withdrawal.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Withdrawal]:
        result = await self.session.execute(
            select(Withdrawal)
            .options(selectinload(Withdrawal.user))
            .order_by(Withdrawal.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(
        self,
        user_id: int,
        telebirr_number: str,
        amount: float,
    ) -> Withdrawal:
        w = Withdrawal(
            user_id=user_id,
            telebirr_number=telebirr_number,
            amount=amount,
            status=WithdrawalStatus.PENDING,
        )
        self.session.add(w)
        await self.session.flush()
        await self.session.refresh(w)
        return w

    async def update_status(
        self,
        withdrawal_id: int,
        status: WithdrawalStatus,
        admin_id: Optional[int] = None,
        note: Optional[str] = None,
    ) -> Optional[Withdrawal]:
        w = await self.get_by_id(withdrawal_id)
        if w is None:
            return None
        w.status = status
        if admin_id is not None:
            w.approved_by = admin_id
        if note is not None:
            w.admin_note = note
        await self.session.flush()
        await self.session.refresh(w)
        return w
