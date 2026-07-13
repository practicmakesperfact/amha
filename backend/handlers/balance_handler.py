"""
Balance handler — displays user's wallet information.
"""

from telegram import Update
from telegram.ext import ContextTypes

from backend.bot.messages import NOT_REGISTERED_BALANCE, balance_message
from backend.core.logging import get_logger
from backend.database.session import get_session_factory
from backend.handlers.common import check_rate_limit
from backend.keyboards.keyboards import main_menu_keyboard
from backend.services.user_service import UserService

logger = get_logger(__name__)


async def balance_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the 💵 Balance button — show user's wallet info."""
    if update.effective_user is None:
        return
    if await check_rate_limit(update):
        return

    tg_user = update.effective_user
    logger.info("Balance requested", telegram_id=tg_user.id)

    try:
        factory = get_session_factory()
        async with factory() as session:
            service = UserService(session)
            user = await service.get_by_telegram_id(tg_user.id)

        if user is None or not user.is_registered:
            await update.effective_message.reply_text(
                NOT_REGISTERED_BALANCE,
                reply_markup=main_menu_keyboard(),
                parse_mode="HTML",
            )
            return

        name = user.full_name or user.username or "N/A"
        phone = user.phone_number or "N/A"

        msg = balance_message(
            name=name,
            phone=phone,
            main_wallet=user.main_wallet,
            play_wallet=user.play_wallet,
            coin=user.coin,
        )

        await update.effective_message.reply_text(
            msg,
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML",
        )

    except Exception:
        logger.exception("Error in balance_handler", telegram_id=tg_user.id)
        await update.effective_message.reply_text(
            "⚠️ Could not fetch balance\\. Please try again\\.",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML",
        )
