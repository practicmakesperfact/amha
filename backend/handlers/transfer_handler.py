"""
Transfer handler — multi-step conversation:
Step 1: 🎁 Transfer → ask for recipient
Step 2: Recipient entered → validate → ask for amount
Step 3: Amount entered → create pending request
"""

from telegram import Update
from telegram.ext import ContextTypes

from backend.bot.fsm import (
    UserState,
    clear_state,
    get_context,
    set_state,
    update_context,
)
from backend.bot.messages import (
    MUST_REGISTER_FIRST,
    TRANSFER_PROMPT_AMOUNT,
    TRANSFER_PROMPT_RECIPIENT,
    escape_html,
    admin_transfer_notification,
)
from backend.core.config import settings
from backend.core.logging import get_logger
from backend.database.session import get_session_factory
from backend.handlers.common import check_rate_limit
from backend.keyboards.keyboards import cancel_keyboard, main_menu_keyboard, transfer_admin_keyboard
from backend.services.transfer_service import TransferService
from backend.services.user_service import UserService
from backend.utils.validators import parse_amount

logger = get_logger(__name__)


async def _notify_admins_transfer(
    context: ContextTypes.DEFAULT_TYPE,
    sender_name: str,
    sender_id: int,
    receiver_name: str,
    receiver_id: int,
    transfer_id: int,
    amount: float,
) -> None:
    text = admin_transfer_notification(
        sender_name=sender_name,
        sender_id=sender_id,
        receiver_name=receiver_name,
        receiver_id=receiver_id,
        transfer_id=transfer_id,
        amount=amount,
    )
    keyboard = transfer_admin_keyboard(transfer_id)
    for admin_id in settings.ADMIN_TELEGRAM_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=text,
                reply_markup=keyboard,
                parse_mode="HTML",
            )
        except Exception:
            logger.warning("Failed to notify admin of transfer", admin_id=admin_id)


async def transfer_button_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Step 1: 🎁 Transfer pressed — ask for recipient."""
    if update.effective_user is None:
        return
    if await check_rate_limit(update):
        return

    tg_user = update.effective_user

    try:
        factory = get_session_factory()
        async with factory() as session:
            service = UserService(session)
            user = await service.get_by_telegram_id(tg_user.id)

        if user is None or not user.is_registered:
            await update.effective_message.reply_text(
                MUST_REGISTER_FIRST,
                reply_markup=main_menu_keyboard(),
                parse_mode="HTML",
            )
            return

        await set_state(tg_user.id, UserState.AWAITING_TRANSFER_RECIPIENT)
        await update.effective_message.reply_text(
            TRANSFER_PROMPT_RECIPIENT,
            reply_markup=cancel_keyboard(),
            parse_mode="HTML",
        )

    except Exception:
        logger.exception("Error in transfer_button_handler", telegram_id=tg_user.id)
        await update.effective_message.reply_text(
            "⚠️ An error occurred\\. Please try again\\.",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML",
        )


async def transfer_recipient_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Step 2: Recipient entered — validate existence, then ask for amount."""
    if update.effective_user is None or update.effective_message is None:
        return

    tg_user = update.effective_user
    identifier = (update.effective_message.text or "").strip()

    try:
        factory = get_session_factory()
        async with factory() as session:
            t_service = TransferService(session)
            recipient = await t_service.find_recipient(identifier)

        if recipient is None:
            await update.effective_message.reply_text(
                f"❌ User *{escape_html(identifier)}* not found\\.\n\nPlease enter a valid @username or phone number\\.",
                reply_markup=cancel_keyboard(),
                parse_mode="HTML",
            )
            return

        if not recipient.is_registered:  # type: ignore[union-attr]
            await update.effective_message.reply_text(
                "❌ Recipient is not a registered user\\.",
                reply_markup=cancel_keyboard(),
                parse_mode="HTML",
            )
            return

        await update_context(
            tg_user.id,
            transfer_recipient_id=recipient.id,  # type: ignore[union-attr]
            transfer_recipient_name=recipient.full_name or recipient.username or identifier,  # type: ignore[union-attr]
        )
        await set_state(tg_user.id, UserState.AWAITING_TRANSFER_AMOUNT)
        await update.effective_message.reply_text(
            TRANSFER_PROMPT_AMOUNT,
            reply_markup=cancel_keyboard(),
            parse_mode="HTML",
        )

    except Exception:
        logger.exception("Error in transfer_recipient_handler", telegram_id=tg_user.id)
        await clear_state(tg_user.id)
        await update.effective_message.reply_text(
            "⚠️ An error occurred\\. Please try again\\.",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML",
        )


async def transfer_amount_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Step 3: Amount entered — execute instant transfer."""
    if update.effective_user is None or update.effective_message is None:
        return

    tg_user = update.effective_user
    text = (update.effective_message.text or "").strip()

    amount = parse_amount(text)
    if amount is None:
        await update.effective_message.reply_text(
            "❌ Invalid amount\\. Please enter a positive number\\.",
            reply_markup=cancel_keyboard(),
            parse_mode="HTML",
        )
        return

    try:
        ctx = await get_context(tg_user.id)
        receiver_id: int | None = ctx.get("transfer_recipient_id")
        receiver_name: str = ctx.get("transfer_recipient_name", "Unknown")

        if receiver_id is None:
            await clear_state(tg_user.id)
            await update.effective_message.reply_text(
                "⚠️ Session expired\\. Please start again\\.",
                reply_markup=main_menu_keyboard(),
                parse_mode="HTML",
            )
            return

        factory = get_session_factory()
        async with factory() as session:
            async with session.begin():
                user_service = UserService(session)
                sender = await user_service.get_by_telegram_id(tg_user.id)

                if sender is None:
                    raise ValueError("Sender not found")

                t_service = TransferService(session)
                receiver = await user_service.get_by_id(receiver_id)
                if receiver is None:
                    raise ValueError("Receiver not found")

                # Execute instant transfer
                result = await t_service.execute_transfer(
                    sender_id=sender.id,
                    recipient_identifier=receiver.username or receiver.phone_number or str(receiver_id),
                    amount=amount,
                )

        await clear_state(tg_user.id)

        await update.effective_message.reply_text(
            result.message,
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML",
        )
        
        # Notify receiver if successful
        if result.success and receiver:
            try:
                sender_name = sender.full_name or sender.username or "Someone"
                await context.bot.send_message(
                    chat_id=receiver.chat_id,
                    text=(
                        "🎁 <b>You received a transfer!</b>\n\n"
                        f"<b>{escape_html(sender_name)}</b> sent you <b>{amount:.2f} ETB</b>.\n\n"
                        "The amount has been added to your Main Wallet."
                    ),
                    reply_markup=main_menu_keyboard(),
                    parse_mode="HTML",
                )
            except Exception:
                logger.warning("Failed to notify receiver of transfer", user_id=receiver.id)

    except Exception:
        logger.exception("Error in transfer_amount_handler", telegram_id=tg_user.id)
        await clear_state(tg_user.id)
        await update.effective_message.reply_text(
            "⚠️ An error occurred\\. Please try again or contact support\\.",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML",
        )
