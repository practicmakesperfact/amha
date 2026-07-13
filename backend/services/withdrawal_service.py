"""
Withdrawal service.
"""

from dataclasses import dataclass
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.models.models import Withdrawal, WithdrawalStatus
from backend.repositories.withdrawal_repository import WithdrawalRepository
from backend.repositories.user_repository import UserRepository

logger = get_logger(__name__)


@dataclass
class WithdrawalResult:
    success: bool
    message: str
    withdrawal: Optional[Withdrawal] = None


class WithdrawalService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = WithdrawalRepository(session)
        self.user_repo = UserRepository(session)

    async def request_withdrawal(
        self,
        user_id: int,
        telebirr_number: str,
        amount: float,
    ) -> WithdrawalResult:
        """Create a pending withdrawal request (no balance deducted yet)."""
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            return WithdrawalResult(success=False, message="❌ User not found.")

        if not user.is_registered:
            return WithdrawalResult(
                success=False,
                message="❌ You must complete registration before withdrawing."
            )

        if amount < settings.MIN_WITHDRAWAL_AMOUNT:
            return WithdrawalResult(
                success=False,
                message=f"❌ Minimum withdrawal amount is *{settings.MIN_WITHDRAWAL_AMOUNT:.2f} ETB*."
            )

        if user.main_wallet < amount:
            return WithdrawalResult(
                success=False,
                message=(
                    f"❌ Insufficient balance.\n"
                    f"Your Main Wallet: *{user.main_wallet:.2f} ETB*\n"
                    f"Requested: *{amount:.2f} ETB*"
                ),
            )

        async with self.session.begin_nested():
            withdrawal = await self.repo.create(
                user_id=user_id,
                telebirr_number=telebirr_number,
                amount=amount,
            )

        logger.info(
            "Withdrawal requested",
            user_id=user_id,
            amount=amount,
            telebirr=telebirr_number,
            withdrawal_id=withdrawal.id,
        )
        return WithdrawalResult(
            success=True,
            message=(
                "✅ Withdrawal request submitted!\n\n"
                f"Amount: *{amount:.2f} ETB*\n"
                f"To: *{telebirr_number}*\n\n"
                "An administrator will process your request shortly."
            ),
            withdrawal=withdrawal,
        )

    async def get_pending(self) -> list[Withdrawal]:
        return await self.repo.get_pending()

    async def get_user_withdrawals(
        self, user_id: int, skip: int = 0, limit: int = 50
    ) -> list[Withdrawal]:
        return await self.repo.get_by_user(user_id, skip=skip, limit=limit)

    async def admin_approve(
        self, withdrawal_id: int, admin_telegram_id: int
    ) -> Optional[Withdrawal]:
        async with self.session.begin_nested():
            w = await self.repo.get_by_id(withdrawal_id)
            if w is None:
                return None
            # Deduct balance only on approval
            await self.user_repo.debit_wallet(user_id=w.user_id, amount=w.amount)
            w = await self.repo.update_status(
                withdrawal_id, WithdrawalStatus.APPROVED, admin_id=admin_telegram_id
            )
        logger.info(
            "Withdrawal approved", withdrawal_id=withdrawal_id, admin_id=admin_telegram_id
        )
        return w

    async def admin_reject(
        self, withdrawal_id: int, admin_telegram_id: int, note: str = ""
    ) -> Optional[Withdrawal]:
        async with self.session.begin_nested():
            w = await self.repo.update_status(
                withdrawal_id, WithdrawalStatus.REJECTED, admin_id=admin_telegram_id, note=note
            )
        logger.info(
            "Withdrawal rejected", withdrawal_id=withdrawal_id, admin_id=admin_telegram_id
        )
        return w
