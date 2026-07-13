"""
Keyboards package init.
"""
from backend.keyboards.keyboards import (
    main_menu_keyboard,
    share_contact_keyboard,
    remove_keyboard,
    cancel_keyboard,
    deposit_admin_keyboard,
    withdrawal_admin_keyboard,
    transfer_admin_keyboard,
)

__all__ = [
    "main_menu_keyboard",
    "share_contact_keyboard",
    "remove_keyboard",
    "cancel_keyboard",
    "deposit_admin_keyboard",
    "withdrawal_admin_keyboard",
    "transfer_admin_keyboard",
]
