"""
SMS parsing and validation utilities for Telebirr confirmation messages.
Handles various formats of Telebirr SMS.
"""

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ParsedSMS:
    """Structured data extracted from a Telebirr confirmation SMS."""

    sender_phone: Optional[str]
    receiver_phone: Optional[str]
    amount: Optional[float]
    reference_number: Optional[str]
    transaction_date: Optional[str]
    raw_text: str

    @property
    def sms_hash(self) -> str:
        """SHA-256 hash of the raw SMS text for deduplication."""
        return hashlib.sha256(self.raw_text.encode("utf-8")).hexdigest()


# Telebirr SMS patterns — ordered from most specific to least specific
_AMOUNT_PATTERNS = [
    r"(?:ETB|Birr)\s*([\d,]+\.?\d*)",
    r"([\d,]+\.?\d*)\s*(?:ETB|Birr)",
    r"amount[:\s]*([\d,]+\.?\d*)",
]

_RECEIVER_PATTERNS = [
    r"to\s*\+?(\d{9,12})",
    r"receiver[:\s]*\+?(\d{9,12})",
    r"sent to[:\s]*\+?(\d{9,12})",
    r"account[:\s]*\+?(\d{9,12})",
]

_SENDER_PATTERNS = [
    r"from\s*\+?(\d{9,12})",
    r"sender[:\s]*\+?(\d{9,12})",
]

_REFERENCE_PATTERNS = [
    r"(?:Ref(?:erence)?\.?\s*(?:No\.?|Number)?|Transaction\s*(?:No\.?|ID|Number)?|TxnID)[:\s]*([A-Z0-9]{6,20})",
    r"\b([A-Z]{2,4}\d{8,16})\b",
    r"Ref[:\s]*([A-Z0-9]{6,20})",
]

_DATE_PATTERNS = [
    r"(\d{2}[/-]\d{2}[/-]\d{4}(?:\s+\d{2}:\d{2}(?::\d{2})?)?)",
    r"(\d{4}[/-]\d{2}[/-]\d{2}(?:\s+\d{2}:\d{2}(?::\d{2})?)?)",
]


def _extract_first(text: str, patterns: list[str]) -> Optional[str]:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).replace(",", "").strip()
    return None


def normalize_phone(phone: Optional[str]) -> Optional[str]:
    """Normalize Ethiopian phone numbers to 10-digit local format."""
    if not phone:
        return None
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("251") and len(digits) == 12:
        return "0" + digits[3:]
    if digits.startswith("0") and len(digits) == 10:
        return digits
    return digits if len(digits) >= 10 else None


def parse_telebirr_sms(sms_text: str) -> ParsedSMS:
    """
    Parse a Telebirr confirmation SMS and extract structured fields.
    Never raises — returns ParsedSMS with None fields for anything not found.
    """
    text = sms_text.strip()

    # Amount
    raw_amount = _extract_first(text, _AMOUNT_PATTERNS)
    amount: Optional[float] = None
    if raw_amount:
        try:
            amount = float(raw_amount.replace(",", ""))
        except ValueError:
            pass

    # Phones
    receiver_raw = _extract_first(text, _RECEIVER_PATTERNS)
    sender_raw = _extract_first(text, _SENDER_PATTERNS)
    receiver_phone = normalize_phone(receiver_raw)
    sender_phone = normalize_phone(sender_raw)

    # Reference
    reference = _extract_first(text, _REFERENCE_PATTERNS)

    # Date
    date = _extract_first(text, _DATE_PATTERNS)

    return ParsedSMS(
        sender_phone=sender_phone,
        receiver_phone=receiver_phone,
        amount=amount,
        reference_number=reference,
        transaction_date=date,
        raw_text=text,
    )


def parse_sms_datetime(date_str: str) -> Optional[datetime]:
    """Parse transaction date string from Telebirr SMS into a timezone-aware EAT datetime."""
    from datetime import datetime, timezone, timedelta
    if not date_str:
        return None
    
    # Try different potential datetime formats
    formats = [
        "%d/%m/%Y %H:%M:%S",
        "%d-%m-%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d-%m-%Y %H:%M",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%Y-%m-%d %H:%M",
    ]
    
    EAT = timezone(timedelta(hours=3))
    date_str_clean = date_str.strip()
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str_clean, fmt)
            return dt.replace(tzinfo=EAT)
        except ValueError:
            continue
            
    # Try date-only formats
    date_only_formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%Y-%m-%d",
    ]
    for fmt in date_only_formats:
        try:
            dt = datetime.strptime(date_str_clean, fmt)
            return dt.replace(tzinfo=EAT)
        except ValueError:
            continue
            
    return None

