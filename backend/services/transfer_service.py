"""
Transfer service.
"""

from dataclasses import dataclass
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.models.models import Transfer, TransferStatus
from backend.repositories.transfer_repository import TransferRepository
from backend.repositories.user_repository import UserRepository

logger = get_logger(__name__)


@dataclass
class TransferResult:
    success: bool
    message: str
    transfer: Optional[Transfer] = None
    receiver_telegram_id: Optional[int] = None
    sender_name: Optional[str] = None
    amount: Optional[float] = None


class TransferService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = TransferRepository(session)
        self.user_repo = UserRepository(session)

    async def find_recipient(
        self, identifier: str
    ) -> Optional[object]:  # Returns User or None
        """Find a user by @username or phone number."""
        if identifier.startswith("@"):
            return await self.user_repo.get_by_username(identifier.lstrip("@"))
        return await self.user_repo.get_by_phone(identifier)

    async def request_transfer(
        self,
        sender_id: int,
        recipient_identifier: str,
        amount: float,
    ) -> TransferResult:
        """Create a pending transfer request."""
        sender = await self.user_repo.get_by_id(sender_id)
        if sender is None:
            return TransferResult(success=False, message="❌ Sender not found.")

        if not sender.is_registered:
            return TransferResult(
                success=False,
                message="❌ You must be registered to make transfers."
            )

        if amount < settings.MIN_TRANSFER_AMOUNT:
            return TransferResult(
                success=False,
                message=f"❌ Minimum transfer amount is *{settings.MIN_TRANSFER_AMOUNT:.2f} ETB*."
            )

        if amount > settings.MAX_TRANSFER_AMOUNT:
            return TransferResult(
                success=False,
                message=f"❌ Maximum transfer amount is *{settings.MAX_TRANSFER_AMOUNT:.2f} ETB*."
            )

        if sender.main_wallet < amount:
            return TransferResult(
                success=False,
                message=(
                    f"❌ Insufficient balance.\n"
                    f"Your Main Wallet: *{sender.main_wallet:.2f} ETB*\n"
                    f"Requested: *{amount:.2f} ETB*"
                ),
            )

        recipient = await self.find_recipient(recipient_identifier)
        if recipient is None:
            return TransferResult(
                success=False,
                message=f"❌ Recipient *{recipient_identifier}* not found.",
            )

        if recipient.id == sender_id:  # type: ignore[union-attr]
            return TransferResult(
                success=False, message="❌ You cannot transfer to yourself."
            )

        if not recipient.is_registered:  # type: ignore[union-attr]
            return TransferResult(
                success=False,
                message="❌ Recipient is not a registered user."
            )

        async with self.session.begin_nested():
            transfer = await self.repo.create(
                sender_id=sender_id,
                receiver_id=recipient.id,  # type: ignore[union-attr]
                amount=amount,
            )

        logger.info(
            "Transfer requested",
            sender_id=sender_id,
            receiver_id=recipient.id,  # type: ignore[union-attr]
            amount=amount,
            transfer_id=transfer.id,
        )

        return TransferResult(
            success=True,
            message=(
                "✅ Transfer request submitted!\n\n"
                f"Amount: *{amount:.2f} ETB*\n"
                f"To: *{recipient_identifier}*\n\n"
                "An administrator will process your request shortly."
            ),
            transfer=transfer,
            receiver_telegram_id=recipient.telegram_id,  # type: ignore[union-attr]
            sender_name=sender.full_name or sender.username or "User",
            amount=amount,
        )

    async def get_pending(self) -> list[Transfer]:
        return await self.repo.get_pending()

    async def get_user_transfers(
        self, user_id: int, skip: int = 0, limit: int = 50
    ) -> list[Transfer]:
        return await self.repo.get_by_user(user_id, skip=skip, limit=limit)

    async def admin_approve(
        self, transfer_id: int, admin_telegram_id: int
    ) -> Optional[Transfer]:
        async with self.session.begin_nested():
            t = await self.repo.get_by_id(transfer_id)
            if t is None:
                return None
            
            # Check if already processed
            if t.status != TransferStatus.PENDING:
                logger.warning(
                    "Attempted to approve already processed transfer",
                    transfer_id=transfer_id,
                    current_status=t.status.value,
                )
                return None
            
            # Verify sender has sufficient balance (prevent race conditions)
            sender = await self.user_repo.get_by_id(t.sender_id)
            if sender is None or sender.main_wallet < t.amount:
                logger.error(
                    "Insufficient balance for transfer approval",
                    transfer_id=transfer_id,
                    sender_balance=sender.main_wallet if sender else 0,
                    transfer_amount=t.amount,
                )
                return None
            
            # Atomic fund movement on approval
            await self.user_repo.transfer_funds(
                sender_id=t.sender_id,
                receiver_id=t.receiver_id,
                amount=t.amount,
            )
            t = await self.repo.update_status(
                transfer_id, TransferStatus.APPROVED, admin_id=admin_telegram_id
            )
        logger.info(
            "Transfer approved", transfer_id=transfer_id, admin_id=admin_telegram_id
        )
        return t

    async def admin_reject(
        self, transfer_id: int, admin_telegram_id: int, note: str = ""
    ) -> Optional[Transfer]:
        async with self.session.begin_nested():
            t = await self.repo.get_by_id(transfer_id)
            if t is None:
                return None
            
            # Check if already processed
            if t.status != TransferStatus.PENDING:
                logger.warning(
                    "Attempted to reject already processed transfer",
                    transfer_id=transfer_id,
                    current_status=t.status.value,
                )
                return None
            
            t = await self.repo.update_status(
                transfer_id, TransferStatus.REJECTED, admin_id=admin_telegram_id, note=note
            )
        logger.info(
            "Transfer rejected", transfer_id=transfer_id, admin_id=admin_telegram_id
        )
        return t
