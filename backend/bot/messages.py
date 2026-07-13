"""
All message text templates for AMHABINGO Bot.
Centralized so all messages can be updated from one place.
"""

from backend.core.config import settings


WELCOME_MESSAGE = """🎉 *Welcome to AMHABINGO!* 🎲

The ultimate Bingo experience on Telegram.

Use the menu below to get started\\. 👇
"""

ALREADY_REGISTERED_MESSAGE = "✅ You are already registered\\."

REGISTER_PROMPT_MESSAGE = (
    "📱 *Registration*\n\n"
    "Please share your contact information to register\\.\n"
    "Tap the button below:"
)

REGISTER_SUCCESS_MESSAGE = (
    "✅ *Registration completed successfully\\!*\n\n"
    "You can now use all features of AMHABINGO\\."
)

REGISTER_FAILED_MESSAGE = (
    "❌ Registration failed\\. Please try again or contact support\\."
)

PLAY_COMING_SOON_MESSAGE = (
    "🚧 *Telegram Mini App*\n\n"
    "Coming Soon\\.\n\n"
    "Our real\\-time Bingo Mini App will be available soon\\.\n\n"
    "Stay tuned\\! 🎮"
)

DEPOSIT_PROMPT_MESSAGE = (
    "💰 *Deposit*\n\n"
    "How much would you like to deposit?\n\n"
    "Enter a positive amount in ETB:\n"
    "_Example: 100, 200, 500, 1000_"
)

DEPOSIT_INVALID_AMOUNT_MESSAGE = (
    "❌ Invalid amount\\.\n\n"
    "Please enter a positive number\\.\n"
    "_Example: 100, 200, 500, 1000_"
)


def deposit_instructions(amount: float) -> str:
    return (
        f"📲 *Payment Instructions*\n\n"
        f"Please send exactly *{amount:.2f} ETB* to the following Telebirr number:\n\n"
        f"📱 *{settings.TELEBIRR_RECEIVER_NUMBER}*\n\n"
        f"⚠️ *IMPORTANT*\n"
        f"Payments must only be sent to this number\\.\n\n"
        f"After completing the payment, paste the *complete Telebirr confirmation SMS* below\\."
    )


WITHDRAWAL_NOT_REGISTERED = (
    "❌ You must complete registration before withdrawing\\."
)

WITHDRAWAL_PROMPT_PHONE = (
    "💸 *Withdraw*\n\n"
    "Please enter your Telebirr phone number to receive the payment:\n"
    "_Example: 0912345678_"
)

WITHDRAWAL_INVALID_PHONE = (
    "❌ Invalid phone number\\.\n\n"
    "Please enter a valid Ethiopian phone number\\.\n"
    "_Example: 0912345678_"
)

WITHDRAWAL_PROMPT_AMOUNT = (
    "💸 *Withdraw*\n\n"
    "How much would you like to withdraw? \\(ETB\\)\n"
    "_Example: 100, 200, 500_"
)

TRANSFER_PROMPT_RECIPIENT = (
    "🎁 *Transfer*\n\n"
    "Enter the recipient's username or phone number:\n"
    "_Example: @username or 0912345678_"
)

TRANSFER_PROMPT_AMOUNT = (
    "🎁 *Transfer*\n\n"
    "How much would you like to transfer? \\(ETB\\)\n"
    "_Example: 50, 100, 200_"
)

CANCEL_MESSAGE = "❌ Action cancelled\\. Returning to main menu\\."

MUST_REGISTER_FIRST = (
    "❌ You must register first to use this feature\\.\n\n"
    "Press 📝 *Register* to get started\\."
)

NOT_REGISTERED_BALANCE = (
    "❌ You must register first to view your balance\\.\n\n"
    "Press 📝 *Register* to get started\\."
)

INSTRUCTION_MESSAGE = """📖 *AMHABINGO Instructions*

━━━━━━━━━━━━━━━━━━━━━━━━
📝 *Registration*
Press *Register* and share your contact to create your account\\.

━━━━━━━━━━━━━━━━━━━━━━━━
💰 *Deposit*
1\\. Press *Deposit* and enter the amount\\.
2\\. Send the exact amount via Telebirr to *{receiver}*\\.
3\\. Paste the Telebirr confirmation SMS\\.
4\\. Funds are added to your wallet instantly\\.

━━━━━━━━━━━━━━━━━━━━━━━━
💸 *Withdraw*
1\\. Press *Withdraw* and enter your Telebirr number\\.
2\\. Enter the withdrawal amount\\.
3\\. An admin will process your request and send the funds\\.

━━━━━━━━━━━━━━━━━━━━━━━━
🎁 *Transfer*
1\\. Press *Transfer* and enter recipient's username or phone\\.
2\\. Enter the amount to transfer\\.
3\\. An admin will process and confirm the transfer\\.

━━━━━━━━━━━━━━━━━━━━━━━━
🎮 *Play*
Join our real\\-time Bingo game via the Telegram Mini App\\.
\\(Coming Soon\\)

━━━━━━━━━━━━━━━━━━━━━━━━
🏆 *Winning*
Win ETB by completing Bingo patterns in real\\-time games\\.
Winnings are credited to your Play Wallet automatically\\.

━━━━━━━━━━━━━━━━━━━━━━━━
☎ *Support*
Contact our support team for any issues or questions\\.
""".format(receiver=settings.TELEBIRR_RECEIVER_NUMBER)


def support_message() -> str:
    return (
        f"☎ *AMHABINGO Support*\n\n"
        f"📢 Support Channel:\n"
        f"[t\\.me/amhabingosupport\\_team](https://t.me/amhabingosupport_team)\n\n"
        f"🤖 Bot:\n"
        f"@{settings.BOT_USERNAME}"
    )


def balance_message(
    name: str,
    phone: str,
    main_wallet: float,
    play_wallet: float,
    coin: int,
) -> str:
    return (
        f"👤 *Name:*\n{escape_md(name)}\n\n"
        f"📞 *Phone:*\n{escape_md(phone)}\n\n"
        f"💰 *Main Wallet:*\n`{main_wallet:.2f} ETB`\n\n"
        f"🎮 *Play Wallet:*\n`{play_wallet:.2f} ETB`\n\n"
        f"🪙 *Coin:*\n`{coin}`"
    )


def escape_md(text: str) -> str:
    """Escape special characters for MarkdownV2."""
    special = r"\_*[]()~`>#+-=|{}.!"
    for char in special:
        text = text.replace(char, f"\\{char}")
    return text


def admin_deposit_notification(
    user_name: str,
    user_id: int,
    deposit_id: int,
    amount: float,
    reference: str,
    sender_phone: str,
) -> str:
    return (
        f"🔔 *New Deposit Request*\n\n"
        f"👤 User: {escape_md(user_name)} \\(ID: {user_id}\\)\n"
        f"💰 Amount: `{amount:.2f} ETB`\n"
        f"🔑 Reference: `{escape_md(reference)}`\n"
        f"📱 Sender: `{escape_md(sender_phone)}`\n"
        f"🆔 Deposit ID: `{deposit_id}`"
    )


def admin_withdrawal_notification(
    user_name: str,
    user_id: int,
    withdrawal_id: int,
    amount: float,
    telebirr_number: str,
) -> str:
    return (
        f"🔔 *New Withdrawal Request*\n\n"
        f"👤 User: {escape_md(user_name)} \\(ID: {user_id}\\)\n"
        f"💸 Amount: `{amount:.2f} ETB`\n"
        f"📱 Telebirr: `{escape_md(telebirr_number)}`\n"
        f"🆔 Withdrawal ID: `{withdrawal_id}`"
    )


def admin_transfer_notification(
    sender_name: str,
    sender_id: int,
    receiver_name: str,
    receiver_id: int,
    transfer_id: int,
    amount: float,
) -> str:
    return (
        f"🔔 *New Transfer Request*\n\n"
        f"📤 From: {escape_md(sender_name)} \\(ID: {sender_id}\\)\n"
        f"📥 To: {escape_md(receiver_name)} \\(ID: {receiver_id}\\)\n"
        f"🎁 Amount: `{amount:.2f} ETB`\n"
        f"🆔 Transfer ID: `{transfer_id}`"
    )
