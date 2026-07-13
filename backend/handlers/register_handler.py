"""
Registration handler.
Handles the 📝 Register button and contact sharing flow.
"""

from telegram import Contact, Update
from telegram.ext import ContextTypes

from backend.bot.fsm import UserState, clear_state, get_state, set_state
from backend.bot.messages import (
    ALREADY_REGISTERED_MESSAGE,
    REGISTER_FAILED_MESSAGE,
    REGISTER_PROMPT_MESSAGE,
    REGISTER_SUCCESS_MESSAGE,
    escape_html,
)
from backend.core.logging import get_logger
from backend.database.session import get_session_factory
from backend.handlers.common import check_rate_limit, send_main_menu
from backend.keyboards.keyboards import main_menu_keyboard, share_contact_keyboard
from backend.services.user_service import UserService
from backend.utils import normalize_phone

logger = get_logger(__name__)


async def register_button_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the 📝 Register button press."""
    if update.effective_user is None:
        return
    if await check_rate_limit(update):
        return

    tg_user = update.effective_user
    logger.info("Register button pressed", telegram_id=tg_user.id)

    try:
        factory = get_session_factory()
        async with factory() as session:
            service = UserService(session)
            user = await service.get_by_telegram_id(tg_user.id)

        if user and user.is_registered:
            await update.effective_message.reply_text(
                ALREADY_REGISTERED_MESSAGE,
                reply_markup=main_menu_keyboard(),
                parse_mode="HTML",
            )
            return

        # Prompt for contact share
        await set_state(tg_user.id, UserState.AWAITING_CONTACT)
        await update.effective_message.reply_text(
            REGISTER_PROMPT_MESSAGE,
            reply_markup=share_contact_keyboard(),
            parse_mode="HTML",
        )

    except Exception:
        logger.exception("Error in register_button_handler", telegram_id=tg_user.id)
        await update.effective_message.reply_text(
            "⚠️ An error occurred\\. Please try again\\.",
            parse_mode="HTML",
        )


async def contact_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle the shared contact from Telegram."""
    if update.effective_user is None or update.message is None:
        return

    tg_user = update.effective_user
    contact: Contact | None = update.message.contact

    if contact is None:
        await update.effective_message.reply_text(
            "❌ No contact received\\. Please use the *Share Contact* button\\.",
            parse_mode="HTML",
        )
        return

    state = await get_state(tg_user.id)
    if state != UserState.AWAITING_CONTACT:
        # Ignore stray contacts outside registration flow
        return

    logger.info(
        "Contact received",
        telegram_id=tg_user.id,
        phone=contact.phone_number,
    )

    try:
        # Normalize phone
        raw_phone = contact.phone_number or ""
        phone = normalize_phone(raw_phone) or raw_phone

        factory = get_session_factory()
        async with factory() as session:
            async with session.begin():
                service = UserService(session)

                # Ensure user record exists
                await service.get_or_create_from_telegram(
                    telegram_id=tg_user.id,
                    chat_id=update.effective_chat.id,
                    username=tg_user.username,
                    first_name=tg_user.first_name,
                    last_name=tg_user.last_name,
                )

                # Complete registration
                user = await service.register_user(
                    telegram_id=tg_user.id,
                    phone_number=phone,
                )

        await clear_state(tg_user.id)

        if user:
            logger.info(
                "Registration completed",
                telegram_id=tg_user.id,
                phone=phone,
                user_id=user.id,
            )
            await update.effective_message.reply_text(
                REGISTER_SUCCESS_MESSAGE,
                reply_markup=main_menu_keyboard(),
                parse_mode="HTML",
            )
        else:
            await update.effective_message.reply_text(
                REGISTER_FAILED_MESSAGE,
                reply_markup=main_menu_keyboard(),
                parse_mode="HTML",
            )

    except Exception:
        logger.exception("Error in contact_handler", telegram_id=tg_user.id)
        await clear_state(tg_user.id)
        await update.effective_message.reply_text(
            "⚠️ Registration failed\\. Please try again\\.",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML",
        )
