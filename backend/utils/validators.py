"""
Utility helpers for phone validation, amount parsing, etc.
"""

import re
from typing import Optional


ETHIOPIAN_PHONE_RE = re.compile(r"^(0[79]\d{8}|09\d{8})$")


def validate_ethiopian_phone(phone: str) -> bool:
    """Validate an Ethiopian phone number (local 10-digit format)."""
    digits = re.sub(r"\D", "", phone)
    return bool(ETHIOPIAN_PHONE_RE.match(digits))


def parse_amount(text: str) -> Optional[float]:
    """
    Try to parse a user-entered amount string.
    Returns None if not a valid positive number.
    """
    text = text.strip().replace(",", "")
    try:
        val = float(text)
        if val > 0:
            return round(val, 2)
        return None
    except ValueError:
        return None


def format_currency(amount: float) -> str:
    """Format a float as currency string."""
    return f"{amount:,.2f} ETB"


def mask_phone(phone: str) -> str:
    """Mask middle digits of a phone number for display."""
    if len(phone) < 6:
        return phone
    return phone[:3] + "****" + phone[-3:]
