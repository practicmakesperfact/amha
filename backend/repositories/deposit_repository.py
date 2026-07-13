"""
Deposit repository.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models.models import Deposit, DepositStatus, UsedSMS
from backend.repositories.base import BaseRepository


class DepositRepository(BaseRepository[Deposit]):
    model = Deposit

    async def get_by_reference(self, reference: str) -> Optional[Deposit]:
        result = await self.session.execute(
            select(Deposit).where(Deposit.reference == reference)
        )
        return result.scalar_one_or_none()

    async def get_by_user(
        self, user_id: int, skip: int = 0, limit: int = 50
    ) -> list[Deposit]:
        result = await self.session.execute(
            select(Deposit)
            .where(Deposit.user_id == user_id)
            .order_by(Deposit.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_pending(self) -> list[Deposit]:
        result = await self.session.execute(
            select(Deposit)
            .where(Deposit.status == DepositStatus.PENDING_ADMIN_APPROVAL)
            .options(selectinload(Deposit.user))
            .order_by(Deposit.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Deposit]:
        result = await self.session.execute(
            select(Deposit)
            .options(selectinload(Deposit.user))
            .order_by(Deposit.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(
        self,
        user_id: int,
        amount: float,
        sms_text: Optional[str] = None,
        sender_phone: Optional[str] = None,
        receiver_phone: Optional[str] = None,
        reference: Optional[str] = None,
        transaction_date: Optional[str] = None,
        status: DepositStatus = DepositStatus.PENDING,
    ) -> Deposit:
        deposit = Deposit(
            user_id=user_id,
            amount=amount,
            sms_text=sms_text,
            sender_phone=sender_phone,
            receiver_phone=receiver_phone,
            reference=reference,
            transaction_date=transaction_date,
            status=status,
        )
        self.session.add(deposit)
        await self.session.flush()
        await self.session.refresh(deposit)
        return deposit

    async def update_status(
        self,
        deposit_id: int,
        status: DepositStatus,
        admin_id: Optional[int] = None,
        note: Optional[str] = None,
    ) -> Optional[Deposit]:
        deposit = await self.get_by_id(deposit_id)
        if deposit is None:
            return None
        deposit.status = status
        if admin_id is not None:
            deposit.approved_by = admin_id
        if note is not None:
            deposit.admin_note = note
        await self.session.flush()
        await self.session.refresh(deposit)
        return deposit


class UsedSMSRepository(BaseRepository[UsedSMS]):
    model = UsedSMS

    async def is_reference_used(self, reference: str) -> bool:
        result = await self.session.execute(
            select(UsedSMS).where(UsedSMS.reference_number == reference)
        )
        return result.scalar_one_or_none() is not None

    async def record(
        self, reference: str, sms_hash: str, deposit_id: Optional[int] = None
    ) -> UsedSMS:
        entry = UsedSMS(
            reference_number=reference,
            sms_hash=sms_hash,
            deposit_id=deposit_id,
        )
        self.session.add(entry)
        await self.session.flush()
        return entry
