"""
/start command handler.
"""

from telegram import Update
from telegram.ext import ContextTypes

from backend.bot.fsm import clear_state
from backend.bot.messages import WELCOME_MESSAGE
from backend.core.logging import get_logger
from backend.database.session import get_session_factory
from backend.handlers.common import check_rate_limit, send_main_menu
from backend.services.user_service import UserService

logger = get_logger(__name__)


async def start_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle the /start command.
    • Verifies Telegram user
    • Creates or updates the local user record
    • Displays the welcome banner with persistent keyboard
    """
    if update.effective_user is None or update.effective_message is None:
        return

    if await check_rate_limit(update):
        return

    tg_user = update.effective_user
    logger.info(
        "Start command received",
        telegram_id=tg_user.id,
        username=tg_user.username,
    )

    try:
        # Reset any ongoing conversation flow
        await clear_state(tg_user.id)

        factory = get_session_factory()
        async with factory() as session:
            async with session.begin():
                service = UserService(session)
                user, created = await service.get_or_create_from_telegram(
                    telegram_id=tg_user.id,
                    chat_id=update.effective_chat.id,
                    username=tg_user.username,
                    first_name=tg_user.first_name,
                    last_name=tg_user.last_name,
                )

        logger.info(
            "Start command processed",
            telegram_id=tg_user.id,
            user_id=user.id,
            created=created,
        )

        await update.effective_message.reply_text(
            WELCOME_MESSAGE,
            reply_markup=__import__(
                "backend.keyboards.keyboards", fromlist=["main_menu_keyboard"]
            ).main_menu_keyboard(),
            parse_mode="MarkdownV2",
        )

    except Exception:
        logger.exception("Error in start_handler", telegram_id=tg_user.id)
        await update.effective_message.reply_text(
            "⚠️ An error occurred\\. Please try again later\\.",
            parse_mode="MarkdownV2",
        )
