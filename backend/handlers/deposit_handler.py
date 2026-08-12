"""
Deposit handler — multi-step conversation flow.
Step 1: User presses 💰 Deposit → bot asks for amount
Step 2: User enters amount → bot sends payment instructions
Step 3: User pastes Telebirr SMS → bot verifies and credits wallet
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
    DEPOSIT_INVALID_AMOUNT_MESSAGE,
    DEPOSIT_PROMPT_MESSAGE,
    MUST_REGISTER_FIRST,
    deposit_instructions,
    escape_html,
)
from backend.core.logging import get_logger
from backend.database.session import get_session_factory
from backend.handlers.common import check_rate_limit
from backend.keyboards.keyboards import cancel_keyboard, main_menu_keyboard
from backend.services.deposit_service import DepositService
from backend.services.user_service import UserService
from backend.utils.validators import parse_amount

logger = get_logger(__name__)


async def deposit_button_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Step 1: Deposit button pressed — ask for amount."""
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

        await set_state(tg_user.id, UserState.AWAITING_DEPOSIT_AMOUNT)
        await update.effective_message.reply_text(
            DEPOSIT_PROMPT_MESSAGE,
            reply_markup=cancel_keyboard(),
            parse_mode="HTML",
        )

    except Exception:
        logger.exception("Error in deposit_button_handler", telegram_id=tg_user.id)
        await update.effective_message.reply_text(
            "⚠️ An error occurred\\. Please try again\\.",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML",
        )


async def deposit_amount_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Step 2: User entered deposit amount — validate and send payment instructions."""
    if update.effective_user is None or update.effective_message is None:
        return

    tg_user = update.effective_user
    text = update.effective_message.text or ""

    amount = parse_amount(text)
    if amount is None:
        await update.effective_message.reply_text(
            DEPOSIT_INVALID_AMOUNT_MESSAGE,
            reply_markup=cancel_keyboard(),
            parse_mode="HTML",
        )
        return

    try:
        from backend.core.config import settings
        
        # Validate minimum deposit
        if amount < settings.MIN_DEPOSIT_AMOUNT:
            await update.effective_message.reply_text(
                f"❌ Minimum deposit amount is <b>{settings.MIN_DEPOSIT_AMOUNT:.2f} ETB</b>.\n\nPlease enter a valid amount.",
                reply_markup=cancel_keyboard(),
                parse_mode="HTML",
            )
            return
        
        # Store amount in Redis context
        await update_context(tg_user.id, deposit_amount=amount)
        await set_state(tg_user.id, UserState.AWAITING_DEPOSIT_SMS)

        await update.effective_message.reply_text(
            deposit_instructions(amount),
            reply_markup=cancel_keyboard(),
            parse_mode="HTML",
        )

    except Exception:
        logger.exception("Error in deposit_amount_handler", telegram_id=tg_user.id)
        await clear_state(tg_user.id)
        await update.effective_message.reply_text(
            "⚠️ An error occurred\\. Please try again\\.",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML",
        )


async def deposit_sms_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Step 3: User pasted Telebirr SMS — verify and credit wallet."""
    if update.effective_user is None or update.effective_message is None:
        return

    tg_user = update.effective_user
    sms_text = update.effective_message.text or ""

    try:
        ctx = await get_context(tg_user.id)
        expected_amount: float | None = ctx.get("deposit_amount")

        if expected_amount is None:
            await clear_state(tg_user.id)
            await update.effective_message.reply_text(
                "⚠️ Session expired\\. Please start the deposit process again\\.",
                reply_markup=main_menu_keyboard(),
                parse_mode="HTML",
            )
            return

        # Send a "processing" indicator
        processing_msg = await update.effective_message.reply_text(
            "⏳ Processing your payment confirmation\\.\\.\\.",
            parse_mode="HTML",
        )

        factory = get_session_factory()
        async with factory() as session:
            async with session.begin():
                user_service = UserService(session)
                user = await user_service.get_by_telegram_id(tg_user.id)

                if user is None:
                    raise ValueError("User not found during SMS verification")

                deposit_service = DepositService(session)
                result = await deposit_service.process_sms_deposit(
                    user_id=user.id,
                    expected_amount=expected_amount,
                    sms_text=sms_text,
                )

        # Delete the "processing" message
        try:
            await processing_msg.delete()
        except Exception:
            pass

        await clear_state(tg_user.id)

        await update.effective_message.reply_text(
            result.message,
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML",
        )

        logger.info(
            "Deposit SMS processed",
            telegram_id=tg_user.id,
            success=result.success,
            amount=expected_amount,
        )

    except Exception:
        logger.exception("Error in deposit_sms_handler", telegram_id=tg_user.id)
        await clear_state(tg_user.id)
        await update.effective_message.reply_text(
            "⚠️ An error occurred while processing your payment\\. Please try again or contact support\\.",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML",
        )
