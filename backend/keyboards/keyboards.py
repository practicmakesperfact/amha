

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    The persistent main menu keyboard. This is ALWAYS shown after every interaction.
    resize_keyboard=True, is_persistent=True, one_time_keyboard=False per spec.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton("🎮 Play"),
                KeyboardButton("📝 Register"),
            ],
            [
                KeyboardButton("💰 Deposit"),
                KeyboardButton("💵 Balance"),
            ],
            [
                KeyboardButton("💸 Withdraw"),
                KeyboardButton("🎁 Transfer"),
            ],
            [
                KeyboardButton("📖 Instruction"),
                KeyboardButton("☎ Support"),
            ],
        ],
        resize_keyboard=True,
        is_persistent=True,
        one_time_keyboard=False,
    )


def share_contact_keyboard() -> ReplyKeyboardMarkup:
    """Keyboard with a single 'Share Contact' button for registration."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton("📱 Share Contact", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    """Used to temporarily remove keyboard (rarely needed)."""
    return ReplyKeyboardRemove()


def cancel_keyboard() -> ReplyKeyboardMarkup:
    """A simple cancel button used during multi-step flows."""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton("❌ Cancel")]],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


# ── Inline keyboards for admin actions ───────────────────────────────────────


def deposit_admin_keyboard(deposit_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"admin:deposit:approve:{deposit_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"admin:deposit:reject:{deposit_id}"),
        ]
    ])


def withdrawal_admin_keyboard(withdrawal_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"admin:withdrawal:approve:{withdrawal_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"admin:withdrawal:reject:{withdrawal_id}"),
        ]
    ])


def transfer_admin_keyboard(transfer_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"admin:transfer:approve:{transfer_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"admin:transfer:reject:{transfer_id}"),
        ]
    ])
