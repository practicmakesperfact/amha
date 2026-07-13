"""
Shared helpers used across all handlers.
"""

from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from backend.bot.fsm import clear_state, get_state, UserState
from backend.bot.messages import CANCEL_MESSAGE
from backend.core.logging import get_logger
from backend.keyboards.keyboards import main_menu_keyboard
from backend.middleware.rate_limiter import is_rate_limited

logger = get_logger(__name__)


async def send_main_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str = "🏠 Main Menu",
    parse_mode: str = "MarkdownV2",
) -> None:
    """Send a message with the persistent main menu keyboard."""
    await update.effective_message.reply_text(
        text,
        reply_markup=main_menu_keyboard(),
        parse_mode=parse_mode,
    )


async def check_rate_limit(update: Update) -> bool:
    """
    Check if the user is rate-limited.
    Returns True if rate-limited (caller should stop processing).
    """
    if update.effective_user is None:
        return False
    limited = await is_rate_limited(update.effective_user.id)
    if limited:
        await update.effective_message.reply_text(
            "⚠️ You are sending messages too fast\\. Please slow down\\.",
            parse_mode="MarkdownV2",
        )
    return limited


async def handle_cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle the ❌ Cancel button — resets FSM and returns to main menu."""
    if update.effective_user:
        await clear_state(update.effective_user.id)
    await send_main_menu(update, context, text=CANCEL_MESSAGE)
