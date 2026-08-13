"""
WalletTransaction repository.
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.models import WalletTransaction, TransactionType
from backend.repositories.base import BaseRepository


class WalletTransactionRepository(BaseRepository[WalletTransaction]):
    model = WalletTransaction

    async def create_transaction(
        self,
        user_id: int,
        transaction_type: TransactionType,
        amount: float,
        balance_before: float,
        balance_after: float,
        deposit_id: Optional[int] = None,
        withdrawal_id: Optional[int] = None,
        transfer_id: Optional[int] = None,
        description: Optional[str] = None,
    ) -> WalletTransaction:
        """Create a wallet transaction record."""
        tx = WalletTransaction(
            user_id=user_id,
            transaction_type=transaction_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            deposit_id=deposit_id,
            withdrawal_id=withdrawal_id,
            transfer_id=transfer_id,
            description=description,
        )
        self.session.add(tx)
        await self.session.flush()
        await self.session.refresh(tx)
        return tx

    async def get_user_transactions(
        self, user_id: int, skip: int = 0, limit: int = 50
    ) -> list[WalletTransaction]:
        """Get all transactions for a user."""
        result = await self.session.execute(
            select(WalletTransaction)
            .where(WalletTransaction.user_id == user_id)
            .order_by(WalletTransaction.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
