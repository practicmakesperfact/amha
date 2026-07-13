"""
Withdrawal handler — multi-step conversation:
Step 1: User presses 💸 Withdraw → ask for Telebirr number
Step 2: User enters phone → validate → ask for amount
Step 3: User enters amount → create pending request
"""

from telegram import Update
from telegram.ext import ContextTypes

from backend.bot.fsm import (
    UserState,
    clear_state,
    get_context,
    get_state,
    set_state,
    update_context,
)
from backend.bot.messages import (
    MUST_REGISTER_FIRST,
    WITHDRAWAL_INVALID_PHONE,
    WITHDRAWAL_PROMPT_AMOUNT,
    WITHDRAWAL_PROMPT_PHONE,
    escape_md,
)
from backend.core.config import settings
from backend.core.logging import get_logger
from backend.database.session import get_session_factory
from backend.handlers.common import check_rate_limit
from backend.keyboards.keyboards import cancel_keyboard, main_menu_keyboard, withdrawal_admin_keyboard
from backend.services.user_service import UserService
from backend.services.withdrawal_service import WithdrawalService
from backend.utils.validators import parse_amount, validate_ethiopian_phone

logger = get_logger(__name__)


async def _notify_admins_withdrawal(
    context: ContextTypes.DEFAULT_TYPE,
    user_name: str,
    user_id: int,
    withdrawal_id: int,
    amount: float,
    telebirr_number: str,
) -> None:
    """Notify all configured admin Telegram IDs about a new withdrawal request."""
    from backend.bot.messages import admin_withdrawal_notification

    text = admin_withdrawal_notification(
        user_name=user_name,
        user_id=user_id,
        withdrawal_id=withdrawal_id,
        amount=amount,
        telebirr_number=telebirr_number,
    )
    keyboard = withdrawal_admin_keyboard(withdrawal_id)

    for admin_id in settings.ADMIN_TELEGRAM_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=text,
                reply_markup=keyboard,
                parse_mode="MarkdownV2",
            )
        except Exception:
            logger.warning("Failed to notify admin", admin_id=admin_id, withdrawal_id=withdrawal_id)


async def withdraw_button_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Step 1: 💸 Withdraw pressed — ask for Telebirr number."""
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
                parse_mode="MarkdownV2",
            )
            return

        await set_state(tg_user.id, UserState.AWAITING_WITHDRAWAL_PHONE)
        await update.effective_message.reply_text(
            WITHDRAWAL_PROMPT_PHONE,
            reply_markup=cancel_keyboard(),
            parse_mode="MarkdownV2",
        )

    except Exception:
        logger.exception("Error in withdraw_button_handler", telegram_id=tg_user.id)
        await update.effective_message.reply_text(
            "⚠️ An error occurred\\. Please try again\\.",
            reply_markup=main_menu_keyboard(),
            parse_mode="MarkdownV2",
        )


async def withdrawal_phone_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Step 2: Phone entered — validate and ask for amount."""
    if update.effective_user is None or update.effective_message is None:
        return

    tg_user = update.effective_user
    phone = (update.effective_message.text or "").strip()

    if not validate_ethiopian_phone(phone):
        await update.effective_message.reply_text(
            WITHDRAWAL_INVALID_PHONE,
            reply_markup=cancel_keyboard(),
            parse_mode="MarkdownV2",
        )
        return

    try:
        await update_context(tg_user.id, withdrawal_phone=phone)
        await set_state(tg_user.id, UserState.AWAITING_WITHDRAWAL_AMOUNT)
        await update.effective_message.reply_text(
            WITHDRAWAL_PROMPT_AMOUNT,
            reply_markup=cancel_keyboard(),
            parse_mode="MarkdownV2",
        )
    except Exception:
        logger.exception("Error in withdrawal_phone_handler", telegram_id=tg_user.id)
        await clear_state(tg_user.id)
        await update.effective_message.reply_text(
            "⚠️ An error occurred\\. Please try again\\.",
            reply_markup=main_menu_keyboard(),
            parse_mode="MarkdownV2",
        )


async def withdrawal_amount_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Step 3: Amount entered — validate and create pending withdrawal."""
    if update.effective_user is None or update.effective_message is None:
        return

    tg_user = update.effective_user
    text = (update.effective_message.text or "").strip()

    amount = parse_amount(text)
    if amount is None:
        await update.effective_message.reply_text(
            "❌ Invalid amount\\. Please enter a positive number\\.",
            reply_markup=cancel_keyboard(),
            parse_mode="MarkdownV2",
        )
        return

    try:
        ctx = await get_context(tg_user.id)
        phone: str | None = ctx.get("withdrawal_phone")

        if phone is None:
            await clear_state(tg_user.id)
            await update.effective_message.reply_text(
                "⚠️ Session expired\\. Please start again\\.",
                reply_markup=main_menu_keyboard(),
                parse_mode="MarkdownV2",
            )
            return

        factory = get_session_factory()
        async with factory() as session:
            async with session.begin():
                user_service = UserService(session)
                user = await user_service.get_by_telegram_id(tg_user.id)

                if user is None:
                    raise ValueError("User not found")

                w_service = WithdrawalService(session)
                result = await w_service.request_withdrawal(
                    user_id=user.id,
                    telebirr_number=phone,
                    amount=amount,
                )

        await clear_state(tg_user.id)

        await update.effective_message.reply_text(
            result.message,
            reply_markup=main_menu_keyboard(),
            parse_mode="MarkdownV2",
        )

        # Notify admins if request was created successfully
        if result.success and result.withdrawal and user:
            name = user.full_name or user.username or "User"
            await _notify_admins_withdrawal(
                context=context,
                user_name=name,
                user_id=user.id,
                withdrawal_id=result.withdrawal.id,
                amount=amount,
                telebirr_number=phone,
            )

    except Exception:
        logger.exception("Error in withdrawal_amount_handler", telegram_id=tg_user.id)
        await clear_state(tg_user.id)
        await update.effective_message.reply_text(
            "⚠️ An error occurred\\. Please try again or contact support\\.",
            reply_markup=main_menu_keyboard(),
            parse_mode="MarkdownV2",
        )
