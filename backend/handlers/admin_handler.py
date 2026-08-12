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
                if not deposit:
                    await query.edit_message_text(
                        f"❌ Deposit #{deposit_id} not found or already processed.",
                        parse_mode="HTML",
                    )
                    return
                
                # Notify user
                user_service = UserService(session)
                user = await user_service.get_by_id(deposit.user_id)
                if user:
                    try:
                        from backend.keyboards.keyboards import main_menu_keyboard
                        await context.bot.send_message(
                            chat_id=user.chat_id,
                            text=(
                                "✅ <b>Deposit Approved!</b>\n\n"
                                f"<b>{deposit.amount:.2f} ETB</b> has been added to your Main Wallet."
                            ),
                            reply_markup=main_menu_keyboard(),
                            parse_mode="HTML",
                        )
                    except Exception:
                        logger.warning("Failed to notify user of deposit approval", user_id=user.id)
                await query.edit_message_text(
                    f"✅ Deposit #{deposit_id} approved by admin {admin_id}.",
                    parse_mode="HTML",
                )
            elif action == "reject":
                deposit = await service.admin_reject(deposit_id, admin_id, note="Admin rejected")
                if not deposit:
                    await query.edit_message_text(
                        f"❌ Deposit #{deposit_id} not found or already processed.",
                        parse_mode="HTML",
                    )
                    return
                
                user_service = UserService(session)
                user = await user_service.get_by_id(deposit.user_id)
                if user:
                    try:
                        from backend.keyboards.keyboards import main_menu_keyboard
                        await context.bot.send_message(
                            chat_id=user.chat_id,
                            text=(
                                "❌ <b>Deposit Rejected</b>\n\n"
                                "Your deposit request has been rejected.\n"
                                "Please contact support if you believe this is an error."
                            ),
                            reply_markup=main_menu_keyboard(),
                            parse_mode="HTML",
                        )
                    except Exception:
                        logger.warning("Failed to notify user of deposit rejection", user_id=user.id)
                await query.edit_message_text(
                    f"❌ Deposit #{deposit_id} rejected.",
                    parse_mode="HTML",
                )


async def _handle_withdrawal_action(action, withdrawal_id, admin_id, query, context, factory):
    async with factory() as session:
        async with session.begin():
            service = WithdrawalService(session)
            if action == "approve":
                w = await service.admin_approve(withdrawal_id, admin_id)
                if not w:
                    await query.edit_message_text(
                        f"❌ Withdrawal #{withdrawal_id} not found, already processed, or insufficient balance.",
                        parse_mode="HTML",
                    )
                    return
                
                user_service = UserService(session)
                user = await user_service.get_by_id(w.user_id)
                if user:
                    try:
                        from backend.keyboards.keyboards import main_menu_keyboard
                        await context.bot.send_message(
                            chat_id=user.chat_id,
                            text=(
                                "✅ <b>Withdrawal Approved!</b>\n\n"
                                f"<b>{w.amount:.2f} ETB</b> will be sent to <code>{w.telebirr_number}</code> shortly.\n\n"
                                "The amount has been deducted from your Main Wallet."
                            ),
                            reply_markup=main_menu_keyboard(),
                            parse_mode="HTML",
                        )
                    except Exception:
                        logger.warning("Failed to notify user of withdrawal approval", user_id=user.id)
                await query.edit_message_text(
                    f"✅ Withdrawal #{withdrawal_id} approved.\n\n"
                    f"💸 Amount: {w.amount:.2f} ETB\n"
                    f"📱 Send to: {w.telebirr_number}",
                    parse_mode="HTML",
                )
            elif action == "reject":
                w = await service.admin_reject(withdrawal_id, admin_id, note="Admin rejected")
                if not w:
                    await query.edit_message_text(
                        f"❌ Withdrawal #{withdrawal_id} not found or already processed.",
                        parse_mode="HTML",
                    )
                    return
                
                user_service = UserService(session)
                user = await user_service.get_by_id(w.user_id)
                if user:
                    try:
                        from backend.keyboards.keyboards import main_menu_keyboard
                        await context.bot.send_message(
                            chat_id=user.chat_id,
                            text=(
                                "❌ <b>Withdrawal Rejected</b>\n\n"
                                "Your withdrawal request has been rejected.\n"
                                "Your balance remains unchanged.\n\n"
                                "Please contact support if you have questions."
                            ),
                            reply_markup=main_menu_keyboard(),
                            parse_mode="HTML",
                        )
                    except Exception:
                        logger.warning("Failed to notify user of withdrawal rejection", user_id=user.id)
                await query.edit_message_text(
                    f"❌ Withdrawal #{withdrawal_id} rejected.",
                    parse_mode="HTML",
                )


async def _handle_transfer_action(action, transfer_id, admin_id, query, context, factory):
    async with factory() as session:
        async with session.begin():
            service = TransferService(session)
            if action == "approve":
                t = await service.admin_approve(transfer_id, admin_id)
                if not t:
                    await query.edit_message_text(
                        f"❌ Transfer #{transfer_id} not found, already processed, or insufficient balance.",
                        parse_mode="HTML",
                    )
                    return
                
                user_service = UserService(session)
                sender = await user_service.get_by_id(t.sender_id)
                receiver = await user_service.get_by_id(t.receiver_id)
                
                sender_name = sender.full_name or sender.username or "User" if sender else "User"
                receiver_name = receiver.full_name or receiver.username or "User" if receiver else "User"
                
                # Notify sender
                if sender:
                    try:
                        from backend.keyboards.keyboards import main_menu_keyboard
                        await context.bot.send_message(
                            chat_id=sender.chat_id,
                            text=(
                                "✅ <b>Transfer Approved!</b>\n\n"
                                f"<b>{t.amount:.2f} ETB</b> has been sent to <b>{receiver_name}</b>.\n\n"
                                "The amount has been deducted from your Main Wallet."
                            ),
                            reply_markup=main_menu_keyboard(),
                            parse_mode="HTML",
                        )
                    except Exception:
                        logger.warning("Failed to notify sender of transfer approval", user_id=sender.id)
                
                # Notify receiver
                if receiver:
                    try:
                        from backend.keyboards.keyboards import main_menu_keyboard
                        await context.bot.send_message(
                            chat_id=receiver.chat_id,
                            text=(
                                "🎁 <b>You received a transfer!</b>\n\n"
                                f"<b>{sender_name}</b> sent you <b>{t.amount:.2f} ETB</b>.\n\n"
                                "The amount has been added to your Main Wallet."
                            ),
                            reply_markup=main_menu_keyboard(),
                            parse_mode="HTML",
                        )
                    except Exception:
                        logger.warning("Failed to notify receiver of transfer", user_id=receiver.id)
                
                await query.edit_message_text(
                    f"✅ Transfer #{transfer_id} approved.\n\n"
                    f"From: {sender_name}\n"
                    f"To: {receiver_name}\n"
                    f"Amount: {t.amount:.2f} ETB",
                    parse_mode="HTML",
                )
            elif action == "reject":
                t = await service.admin_reject(transfer_id, admin_id, note="Admin rejected")
                if not t:
                    await query.edit_message_text(
                        f"❌ Transfer #{transfer_id} not found or already processed.",
                        parse_mode="HTML",
                    )
                    return
                
                user_service = UserService(session)
                sender = await user_service.get_by_id(t.sender_id)
                
                # Only notify sender
                if sender:
                    try:
                        from backend.keyboards.keyboards import main_menu_keyboard
                        await context.bot.send_message(
                            chat_id=sender.chat_id,
                            text=(
                                "❌ <b>Transfer Rejected</b>\n\n"
                                "Your transfer request has been rejected.\n"
                                "Your balance remains unchanged.\n\n"
                                "Please contact support if you have questions."
                            ),
                            reply_markup=main_menu_keyboard(),
                            parse_mode="HTML",
                        )
                    except Exception:
                        logger.warning("Failed to notify sender of transfer rejection", user_id=sender.id)
                
                await query.edit_message_text(
                    f"❌ Transfer #{transfer_id} rejected.",
                    parse_mode="HTML",
                )
