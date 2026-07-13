"""
Message dispatcher — routes incoming text messages to the correct handler
based on the button text OR the current FSM state.
"""

from telegram import Update
from telegram.ext import ContextTypes

from backend.bot.fsm import UserState, get_state
from backend.core.logging import get_logger
from backend.handlers.admin_handler import admin_callback_handler
from backend.handlers.balance_handler import balance_handler
from backend.handlers.common import handle_cancel, send_main_menu
from backend.handlers.deposit_handler import (
    deposit_amount_handler,
    deposit_button_handler,
    deposit_sms_handler,
)
from backend.handlers.info_handlers import (
    instruction_handler,
    play_handler,
    support_handler,
)
from backend.handlers.register_handler import (
    contact_handler,
    register_button_handler,
)
from backend.handlers.transfer_handler import (
    transfer_amount_handler,
    transfer_button_handler,
    transfer_recipient_handler,
)
from backend.handlers.withdrawal_handler import (
    withdraw_button_handler,
    withdrawal_amount_handler,
    withdrawal_phone_handler,
)

logger = get_logger(__name__)

# Mapping button labels to their handlers
BUTTON_HANDLERS = {
    "🎮 Play": play_handler,
    "📝 Register": register_button_handler,
    "💰 Deposit": deposit_button_handler,
    "💵 Balance": balance_handler,
    "💸 Withdraw": withdraw_button_handler,
    "🎁 Transfer": transfer_button_handler,
    "📖 Instruction": instruction_handler,
    "☎ Support": support_handler,
    "❌ Cancel": handle_cancel,
}


async def message_dispatcher(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Route incoming messages:
    1. Check if it's a known menu button → call its handler
    2. Otherwise check FSM state → call appropriate state handler
    3. Unknown messages → show main menu
    """
    if update.effective_user is None or update.effective_message is None:
        return

    text = update.effective_message.text or ""
    tg_user = update.effective_user

    logger.debug(
        "Message received",
        telegram_id=tg_user.id,
        text=text[:50],
    )

    # ── Menu button shortcuts (always available, resets FSM) ──────────────
    if text in BUTTON_HANDLERS:
        # Cancel doesn't need FSM reset (handle_cancel does it internally)
        # Other menu buttons: reset state first to avoid stuck flows
        from backend.bot.fsm import clear_state

        if text != "❌ Cancel":
            await clear_state(tg_user.id)

        await BUTTON_HANDLERS[text](update, context)
        return

    # ── FSM-based routing ─────────────────────────────────────────────────
    state = await get_state(tg_user.id)

    if state == UserState.AWAITING_DEPOSIT_AMOUNT:
        await deposit_amount_handler(update, context)

    elif state == UserState.AWAITING_DEPOSIT_SMS:
        await deposit_sms_handler(update, context)

    elif state == UserState.AWAITING_WITHDRAWAL_PHONE:
        await withdrawal_phone_handler(update, context)

    elif state == UserState.AWAITING_WITHDRAWAL_AMOUNT:
        await withdrawal_amount_handler(update, context)

    elif state == UserState.AWAITING_TRANSFER_RECIPIENT:
        await transfer_recipient_handler(update, context)

    elif state == UserState.AWAITING_TRANSFER_AMOUNT:
        await transfer_amount_handler(update, context)

    else:
        # Unknown message — show main menu
        await send_main_menu(
            update,
            context,
            text="Please use the buttons below to navigate\\.",
        )
