"""
Deposit service — business logic for deposit and SMS verification.
"""

from dataclasses import dataclass
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.models.models import Deposit, DepositStatus
from backend.repositories.deposit_repository import DepositRepository, UsedSMSRepository
from backend.repositories.user_repository import UserRepository
from backend.utils.sms_parser import parse_telebirr_sms, ParsedSMS

logger = get_logger(__name__)


@dataclass
class DepositResult:
    success: bool
    message: str
    deposit: Optional[Deposit] = None
    parsed_sms: Optional[ParsedSMS] = None


class DepositService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.deposit_repo = DepositRepository(session)
        self.sms_repo = UsedSMSRepository(session)
        self.user_repo = UserRepository(session)

    async def create_pending_deposit(self, user_id: int, amount: float) -> Deposit:
        """Create a PENDING deposit record before SMS submission."""
        async with self.session.begin_nested():
            deposit = await self.deposit_repo.create(
                user_id=user_id,
                amount=amount,
                status=DepositStatus.PENDING,
            )
        logger.info("Pending deposit created", user_id=user_id, amount=amount, deposit_id=deposit.id)
        return deposit

    async def process_sms_deposit(
        self,
        user_id: int,
        expected_amount: float,
        sms_text: str,
    ) -> DepositResult:
        """
        Parse and validate Telebirr SMS, then auto-approve and credit the wallet.
        Returns a DepositResult describing what happened.
        """
        parsed = parse_telebirr_sms(sms_text)

        # ── Validate receiver phone ────────────────────────────────────────
        expected_receiver = settings.TELEBIRR_RECEIVER_NUMBER
        if parsed.receiver_phone != expected_receiver:
            logger.warning(
                "SMS receiver mismatch",
                user_id=user_id,
                expected=expected_receiver,
                got=parsed.receiver_phone,
            )
            return DepositResult(
                success=False,
                message=(
                    "❌ Invalid payment confirmation.\n"
                    f"The receiver number must be *{expected_receiver}*.\n"
                    "Please send a valid Telebirr confirmation SMS."
                ),
                parsed_sms=parsed,
            )

        # ── Validate amount match ──────────────────────────────────────────
        if parsed.amount is None or abs(parsed.amount - expected_amount) > 0.01:
            logger.warning(
                "SMS amount mismatch",
                user_id=user_id,
                expected=expected_amount,
                got=parsed.amount,
            )
            return DepositResult(
                success=False,
                message=(
                    f"❌ Amount mismatch.\n"
                    f"Expected *{expected_amount:.2f} ETB* but SMS shows *{parsed.amount} ETB*.\n"
                    "Please send the correct Telebirr confirmation."
                ),
                parsed_sms=parsed,
            )

        # ── Validate reference number ──────────────────────────────────────
        if not parsed.reference_number:
            return DepositResult(
                success=False,
                message=(
                    "❌ Could not extract reference number from SMS.\n"
                    "Please paste the complete Telebirr confirmation message."
                ),
                parsed_sms=parsed,
            )

        # ── Validate transaction date/time ─────────────────────────────────
        if not parsed.transaction_date:
            return DepositResult(
                success=False,
                message=(
                    "❌ Could not extract transaction date/time from SMS.\n"
                    "Please paste the complete Telebirr confirmation message."
                ),
                parsed_sms=parsed,
            )

        from backend.utils.sms_parser import parse_sms_datetime
        from datetime import datetime, timezone, timedelta

        tx_dt = parse_sms_datetime(parsed.transaction_date)
        if not tx_dt:
            logger.warning("SMS date parsing failed", user_id=user_id, raw_date=parsed.transaction_date)
            return DepositResult(
                success=False,
                message=(
                    "❌ Invalid transaction date format in SMS.\n"
                    "Please paste the complete, unmodified Telebirr confirmation message."
                ),
                parsed_sms=parsed,
            )

        EAT = timezone(timedelta(hours=3))
        now_eat = datetime.now(EAT)
        
        # Check transaction age (e.g., max 30 minutes)
        time_diff = now_eat - tx_dt
        max_age = timedelta(minutes=30)
        future_tolerance = timedelta(minutes=5)  # tolerates small client/server clock skew

        if time_diff > max_age:
            logger.warning(
                "SMS transaction is too old",
                user_id=user_id,
                tx_date=parsed.transaction_date,
                tx_age_seconds=time_diff.total_seconds(),
            )
            return DepositResult(
                success=False,
                message=(
                    "❌ Deposit verification failed.\n"
                    "This transaction is too old (older than 30 minutes).\n"
                    "Deposits must be verified immediately after payment. "
                    "If you faced a delay, please contact support."
                ),
                parsed_sms=parsed,
            )

        if time_diff < -future_tolerance:
            logger.warning(
                "SMS transaction is in the future",
                user_id=user_id,
                tx_date=parsed.transaction_date,
                tx_age_seconds=time_diff.total_seconds(),
            )
            return DepositResult(
                success=False,
                message=(
                    "❌ Deposit verification failed.\n"
                    "The transaction timestamp is invalid (in the future).\n"
                    "Please check your system or try again."
                ),
                parsed_sms=parsed,
            )

        already_used = await self.sms_repo.is_reference_used(parsed.reference_number)
        if already_used:
            logger.warning(
                "Duplicate SMS reference",
                user_id=user_id,
                reference=parsed.reference_number,
            )
            return DepositResult(
                success=False,
                message="❌ This payment confirmation has already been used.",
                parsed_sms=parsed,
            )

        # ── All validations passed — credit wallet atomically ─────────────
        async with self.session.begin_nested():
            deposit = await self.deposit_repo.create(
                user_id=user_id,
                amount=expected_amount,
                sms_text=sms_text,
                sender_phone=parsed.sender_phone,
                receiver_phone=parsed.receiver_phone,
                reference=parsed.reference_number,
                transaction_date=parsed.transaction_date,
                status=DepositStatus.APPROVED,
            )
            await self.sms_repo.record(
                reference=parsed.reference_number,
                sms_hash=parsed.sms_hash,
                deposit_id=deposit.id,
            )
            await self.user_repo.credit_wallet(user_id=user_id, amount=expected_amount)

        logger.info(
            "Deposit auto-approved and wallet credited",
            user_id=user_id,
            amount=expected_amount,
            reference=parsed.reference_number,
            deposit_id=deposit.id,
        )

        return DepositResult(
            success=True,
            message=(
                f"✅ Deposit successful!\n\n"
                f"*{expected_amount:.2f} ETB* has been added to your Main Wallet."
            ),
            deposit=deposit,
            parsed_sms=parsed,
        )

    async def get_user_deposits(
        self, user_id: int, skip: int = 0, limit: int = 50
    ) -> list[Deposit]:
        return await self.deposit_repo.get_by_user(user_id, skip=skip, limit=limit)

    async def get_pending_deposits(self) -> list[Deposit]:
        return await self.deposit_repo.get_pending()

    async def admin_approve(
        self, deposit_id: int, admin_telegram_id: int
    ) -> Optional[Deposit]:
        async with self.session.begin_nested():
            deposit = await self.deposit_repo.get_by_id(deposit_id)
            if deposit is None:
                return None
            deposit = await self.deposit_repo.update_status(
                deposit_id, DepositStatus.APPROVED, admin_id=admin_telegram_id
            )
            await self.user_repo.credit_wallet(
                user_id=deposit.user_id, amount=deposit.amount
            )
        logger.info(
            "Deposit approved by admin",
            deposit_id=deposit_id,
            admin_id=admin_telegram_id,
        )
        return deposit

    async def admin_reject(
        self, deposit_id: int, admin_telegram_id: int, note: str = ""
    ) -> Optional[Deposit]:
        async with self.session.begin_nested():
            deposit = await self.deposit_repo.update_status(
                deposit_id, DepositStatus.REJECTED, admin_id=admin_telegram_id, note=note
            )
        logger.info(
            "Deposit rejected by admin",
            deposit_id=deposit_id,
            admin_id=admin_telegram_id,
        )
        return deposit
