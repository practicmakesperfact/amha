"""
Admin callback query handlers.
Handles approve/reject inline button callbacks from admin notifications.
"""

from telegram import Update
from telegram.ext import ContextTypes

from backend.core.config import settings
from backend.core.logging import get_logger
from backend.database.session import get_session_factory
from backend.models.models import DepositStatus, TransferStatus, WithdrawalStatus
from backend.services.deposit_service import DepositService
from backend.services.transfer_service import TransferService
from backend.services.user_service import UserService
from backend.services.withdrawal_service import WithdrawalService

logger = get_logger(__name__)


def is_admin(telegram_id: int) -> bool:
    """Check if the Telegram user is a configured admin."""
    return telegram_id in settings.ADMIN_TELEGRAM_IDS


async def admin_callback_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Route admin inline keyboard callbacks.
    Pattern: admin:{type}:{action}:{id}
    Example: admin:deposit:approve:42
    """
    query = update.callback_query
    if query is None or update.effective_user is None:
        return

    await query.answer()

    admin_id = update.effective_user.id
    if not is_admin(admin_id):
        await query.answer("❌ You are not authorized.", show_alert=True)
        return

    data = query.data or ""
    parts = data.split(":")

    if len(parts) != 4 or parts[0] != "admin":
        return

    _, entity_type, action, entity_id_str = parts
    try:
        entity_id = int(entity_id_str)
    except ValueError:
        return

    logger.info(
        "Admin callback",
        admin_id=admin_id,
        entity_type=entity_type,
        action=action,
        entity_id=entity_id,
    )

    factory = get_session_factory()

    if entity_type == "deposit":
        await _handle_deposit_action(
            action, entity_id, admin_id, query, context, factory
        )
    elif entity_type == "withdrawal":
        await _handle_withdrawal_action(
            action, entity_id, admin_id, query, context, factory
        )
    elif entity_type == "transfer":
        await _handle_transfer_action(
            action, entity_id, admin_id, query, context, factory
        )


async def _handle_deposit_action(action, deposit_id, admin_id, query, context, factory):
    async with factory() as session:
        async with session.begin():
            service = DepositService(session)
            if action == "approve":
                deposit = await service.admin_approve(deposit_id, admin_id)
                if deposit:
                    # Notify user
                    user_service = UserService(session)
                    user = await user_service.get_by_id(deposit.user_id)
                    if user:
                        try:
                            await context.bot.send_message(
                                chat_id=user.chat_id,
                                text=(
                                    f"✅ *Deposit Approved\\!*\n\n"
                                    f"`{deposit.amount:.2f} ETB` has been added to your Main Wallet\\."
                                ),
                                parse_mode="MarkdownV2",
                            )
                        except Exception:
                            logger.warning("Failed to notify user of deposit approval", user_id=user.id)
                    await query.edit_message_text(
                        f"✅ Deposit #{deposit_id} approved by admin {admin_id}\\.",
                        parse_mode="MarkdownV2",
                    )
            elif action == "reject":
                deposit = await service.admin_reject(deposit_id, admin_id)
                if deposit:
                    user_service = UserService(session)
                    user = await user_service.get_by_id(deposit.user_id)
                    if user:
                        try:
                            await context.bot.send_message(
                                chat_id=user.chat_id,
                                text="❌ *Deposit Rejected*\n\nYour deposit request has been rejected\\. Please contact support\\.",
                                parse_mode="MarkdownV2",
                            )
                        except Exception:
                            pass
                    await query.edit_message_text(
                        f"❌ Deposit #{deposit_id} rejected\\.",
                        parse_mode="MarkdownV2",
                    )


async def _handle_withdrawal_action(action, withdrawal_id, admin_id, query, context, factory):
    async with factory() as session:
        async with session.begin():
            service = WithdrawalService(session)
            if action == "approve":
                w = await service.admin_approve(withdrawal_id, admin_id)
                if w:
                    user_service = UserService(session)
                    user = await user_service.get_by_id(w.user_id)
                    if user:
                        try:
                            await context.bot.send_message(
                                chat_id=user.chat_id,
                                text=(
                                    f"✅ *Withdrawal Approved\\!*\n\n"
                                    f"`{w.amount:.2f} ETB` will be sent to `{w.telebirr_number}` shortly\\."
                                ),
                                parse_mode="MarkdownV2",
                            )
                        except Exception:
                            pass
                    await query.edit_message_text(
                        f"✅ Withdrawal #{withdrawal_id} approved\\.",
                        parse_mode="MarkdownV2",
                    )
            elif action == "reject":
                w = await service.admin_reject(withdrawal_id, admin_id)
                if w:
                    user_service = UserService(session)
                    user = await user_service.get_by_id(w.user_id)
                    if user:
                        try:
                            await context.bot.send_message(
                                chat_id=user.chat_id,
                                text="❌ *Withdrawal Rejected*\n\nYour withdrawal request has been rejected\\. Please contact support\\.",
                                parse_mode="MarkdownV2",
                            )
                        except Exception:
                            pass
                    await query.edit_message_text(
                        f"❌ Withdrawal #{withdrawal_id} rejected\\.",
                        parse_mode="MarkdownV2",
                    )


async def _handle_transfer_action(action, transfer_id, admin_id, query, context, factory):
    async with factory() as session:
        async with session.begin():
            service = TransferService(session)
            if action == "approve":
                t = await service.admin_approve(transfer_id, admin_id)
                if t:
                    user_service = UserService(session)
                    sender = await user_service.get_by_id(t.sender_id)
                    receiver = await user_service.get_by_id(t.receiver_id)
                    if sender:
                        try:
                            await context.bot.send_message(
                                chat_id=sender.chat_id,
                                text=f"✅ *Transfer Approved\\!*\n\n`{t.amount:.2f} ETB` has been sent\\.",
                                parse_mode="MarkdownV2",
                            )
                        except Exception:
                            pass
                    if receiver:
                        try:
                            await context.bot.send_message(
                                chat_id=receiver.chat_id,
                                text=f"🎁 *You received a transfer\\!*\n\n`{t.amount:.2f} ETB` has been added to your wallet\\.",
                                parse_mode="MarkdownV2",
                            )
                        except Exception:
                            pass
                    await query.edit_message_text(
                        f"✅ Transfer #{transfer_id} approved\\.",
                        parse_mode="MarkdownV2",
                    )
            elif action == "reject":
                t = await service.admin_reject(transfer_id, admin_id)
                if t:
                    user_service = UserService(session)
                    sender = await user_service.get_by_id(t.sender_id)
                    if sender:
                        try:
                            await context.bot.send_message(
                                chat_id=sender.chat_id,
                                text="❌ *Transfer Rejected*\n\nYour transfer request has been rejected\\.",
                                parse_mode="MarkdownV2",
                            )
                        except Exception:
                            pass
                    await query.edit_message_text(
                        f"❌ Transfer #{transfer_id} rejected\\.",
                        parse_mode="MarkdownV2",
                    )
