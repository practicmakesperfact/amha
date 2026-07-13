"""
Play, Instruction, and Support handlers.
"""

from telegram import Update
from telegram.ext import ContextTypes

from backend.bot.messages import INSTRUCTION_MESSAGE, PLAY_COMING_SOON_MESSAGE, support_message
from backend.core.config import settings
from backend.core.logging import get_logger
from backend.handlers.common import check_rate_limit
from backend.keyboards.keyboards import main_menu_keyboard

logger = get_logger(__name__)


def get_play_message_and_keyboard():
    """
    Returns the play action message and optional inline keyboard.
    ─────────────────────────────────────────────────────────────
    DESIGN DECISION: Switching from "Coming Soon" to the Mini App
    only requires changing this ONE function.

    When MINI_APP_URL is set in settings:
        - Show the WebApp button (future implementation)
    Otherwise:
        - Show "Coming Soon" message
    """
    if settings.MINI_APP_URL:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🎮 Open AMHABINGO",
                    web_app=WebAppInfo(url=settings.MINI_APP_URL),
                )
            ]
        ])
        text = "🎮 *AMHABINGO Mini App*\n\nTap the button below to launch the game\\!"
        return text, keyboard
    else:
        return PLAY_COMING_SOON_MESSAGE, None


async def play_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle 🎮 Play button."""
    if update.effective_user is None:
        return
    if await check_rate_limit(update):
        return

    logger.info("Play button pressed", telegram_id=update.effective_user.id)

    text, inline_keyboard = get_play_message_and_keyboard()

    await update.effective_message.reply_text(
        text,
        reply_markup=inline_keyboard if inline_keyboard else main_menu_keyboard(),
        parse_mode="MarkdownV2",
    )

    # Always send main menu keyboard if we sent an inline keyboard
    if inline_keyboard:
        await update.effective_message.reply_text(
            "Use the menu below for other actions\\.",
            reply_markup=main_menu_keyboard(),
            parse_mode="MarkdownV2",
        )


async def instruction_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle 📖 Instruction button."""
    if update.effective_user is None:
        return
    if await check_rate_limit(update):
        return

    logger.info("Instruction button pressed", telegram_id=update.effective_user.id)

    await update.effective_message.reply_text(
        INSTRUCTION_MESSAGE,
        reply_markup=main_menu_keyboard(),
        parse_mode="MarkdownV2",
    )


async def support_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle ☎ Support button."""
    if update.effective_user is None:
        return
    if await check_rate_limit(update):
        return

    logger.info("Support button pressed", telegram_id=update.effective_user.id)

    await update.effective_message.reply_text(
        support_message(),
        reply_markup=main_menu_keyboard(),
        parse_mode="MarkdownV2",
        disable_web_page_preview=True,
    )
