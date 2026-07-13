"""
All message text templates for AMHABINGO Bot.
Centralized so all messages can be updated from one place.
Uses HTML parse mode for simplicity and reliability.
"""

from backend.core.config import settings


WELCOME_MESSAGE = (
    "🎉 <b>Welcome to AMHABINGO!</b> 🎲\n\n"
    "The ultimate Bingo experience on Telegram.\n\n"
    "Use the menu below to get started 👇"
)

ALREADY_REGISTERED_MESSAGE = "✅ You are already registered."

REGISTER_PROMPT_MESSAGE = (
    "📱 <b>Registration</b>\n\n"
    "Please share your contact information to register.\n"
    "Tap the button below:"
)

REGISTER_SUCCESS_MESSAGE = (
    "✅ <b>Registration completed successfully!</b>\n\n"
    "You can now use all features of AMHABINGO."
)

REGISTER_FAILED_MESSAGE = (
    "❌ Registration failed. Please try again or contact support."
)

PLAY_COMING_SOON_MESSAGE = (
    "🚧 <b>Telegram Mini App</b>\n\n"
    "Coming Soon.\n\n"
    "Our real-time Bingo Mini App will be available soon.\n\n"
    "Stay tuned! 🎮"
)

DEPOSIT_PROMPT_MESSAGE = (
    "💰 <b>Deposit</b>\n\n"
    "How much would you like to deposit?\n\n"
    "Enter a positive amount in ETB:\n"
    "<i>Example: 100, 200, 500, 1000</i>"
)

DEPOSIT_INVALID_AMOUNT_MESSAGE = (
    "❌ Invalid amount.\n\n"
    "Please enter a positive number.\n"
    "<i>Example: 100, 200, 500, 1000</i>"
)


def deposit_instructions(amount: float) -> str:
    return (
        f"📲 <b>Payment Instructions</b>\n\n"
        f"Please send exactly <b>{amount:.2f} ETB</b> to the following Telebirr number:\n\n"
        f"📱 <b>{settings.TELEBIRR_RECEIVER_NUMBER}</b>\n\n"
        f"⚠️ <b>IMPORTANT</b>\n"
        f"Payments must only be sent to this number.\n\n"
        f"After completing the payment, paste the <b>complete Telebirr confirmation SMS</b> below."
    )


WITHDRAWAL_NOT_REGISTERED = (
    "❌ You must complete registration before withdrawing."
)

WITHDRAWAL_PROMPT_PHONE = (
    "💸 <b>Withdraw</b>\n\n"
    "Please enter your Telebirr phone number to receive the payment:\n"
    "<i>Example: 0912345678</i>"
)

WITHDRAWAL_INVALID_PHONE = (
    "❌ Invalid phone number.\n\n"
    "Please enter a valid Ethiopian phone number.\n"
    "<i>Example: 0912345678</i>"
)

WITHDRAWAL_PROMPT_AMOUNT = (
    "💸 <b>Withdraw</b>\n\n"
    "How much would you like to withdraw? (ETB)\n"
    "<i>Example: 100, 200, 500</i>"
)

TRANSFER_PROMPT_RECIPIENT = (
    "🎁 <b>Transfer</b>\n\n"
    "Enter the recipient's username or phone number:\n"
    "<i>Example: @username or 0912345678</i>"
)

TRANSFER_PROMPT_AMOUNT = (
    "🎁 <b>Transfer</b>\n\n"
    "How much would you like to transfer? (ETB)\n"
    "<i>Example: 50, 100, 200</i>"
)

CANCEL_MESSAGE = "❌ Action cancelled. Returning to main menu."

MUST_REGISTER_FIRST = (
    "❌ You must register first to use this feature.\n\n"
    "Press 📝 <b>Register</b> to get started."
)

NOT_REGISTERED_BALANCE = (
    "❌ You must register first to view your balance.\n\n"
    "Press 📝 <b>Register</b> to get started."
)

INSTRUCTION_MESSAGE = (
    "📖 <b>AMHABINGO Instructions</b>\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "📝 <b>Registration</b>\n"
    "Press <b>Register</b> and share your contact to create your account.\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "💰 <b>Deposit</b>\n"
    "1. Press <b>Deposit</b> and enter the amount.\n"
    f"2. Send the exact amount via Telebirr to <b>{settings.TELEBIRR_RECEIVER_NUMBER}</b>.\n"
    "3. Paste the Telebirr confirmation SMS.\n"
    "4. Funds are added to your wallet instantly.\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "💸 <b>Withdraw</b>\n"
    "1. Press <b>Withdraw</b> and enter your Telebirr number.\n"
    "2. Enter the withdrawal amount.\n"
    "3. An admin will process your request and send the funds.\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "🎁 <b>Transfer</b>\n"
    "1. Press <b>Transfer</b> and enter recipient's username or phone.\n"
    "2. Enter the amount to transfer.\n"
    "3. An admin will process and confirm the transfer.\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "🎮 <b>Play</b>\n"
    "Join our real-time Bingo game via the Telegram Mini App.\n"
    "(Coming Soon)\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "🏆 <b>Winning</b>\n"
    "Win ETB by completing Bingo patterns in real-time games.\n"
    "Winnings are credited to your Play Wallet automatically.\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "☎ <b>Support</b>\n"
    "Contact our support team for any issues or questions."
)


def support_message() -> str:
    return (
        f"☎ <b>AMHABINGO Support</b>\n\n"
        f"📢 Support Channel:\n"
        f'<a href="https://t.me/amhabingosupport_team">t.me/amhabingosupport_team</a>\n\n'
        f"🤖 Bot:\n"
        f"@{settings.BOT_USERNAME}"
    )


def escape_html(text: str) -> str:
    """Escape special characters for HTML parse mode."""
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
    )


def balance_message(
    name: str,
    phone: str,
    main_wallet: float,
    play_wallet: float,
    coin: int,
) -> str:
    return (
        f"👤 <b>Name:</b>\n{escape_html(name)}\n\n"
        f"📞 <b>Phone:</b>\n{escape_html(phone)}\n\n"
        f"💰 <b>Main Wallet:</b>\n<code>{main_wallet:.2f} ETB</code>\n\n"
        f"🎮 <b>Play Wallet:</b>\n<code>{play_wallet:.2f} ETB</code>\n\n"
        f"🪙 <b>Coin:</b>\n<code>{coin}</code>"
    )


def admin_deposit_notification(
    user_name: str,
    user_id: int,
    deposit_id: int,
    amount: float,
    reference: str,
    sender_phone: str,
) -> str:
    return (
        f"🔔 <b>New Deposit Request</b>\n\n"
        f"👤 User: {escape_html(user_name)} (ID: {user_id})\n"
        f"💰 Amount: <code>{amount:.2f} ETB</code>\n"
        f"🔑 Reference: <code>{escape_html(reference)}</code>\n"
        f"📱 Sender: <code>{escape_html(sender_phone)}</code>\n"
        f"🆔 Deposit ID: <code>{deposit_id}</code>"
    )


def admin_withdrawal_notification(
    user_name: str,
    user_id: int,
    withdrawal_id: int,
    amount: float,
    telebirr_number: str,
) -> str:
    return (
        f"🔔 <b>New Withdrawal Request</b>\n\n"
        f"👤 User: {escape_html(user_name)} (ID: {user_id})\n"
        f"💸 Amount: <code>{amount:.2f} ETB</code>\n"
        f"📱 Telebirr: <code>{escape_html(telebirr_number)}</code>\n"
        f"🆔 Withdrawal ID: <code>{withdrawal_id}</code>"
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
        f"🔔 <b>New Transfer Request</b>\n\n"
        f"📤 From: {escape_html(sender_name)} (ID: {sender_id})\n"
        f"📥 To: {escape_html(receiver_name)} (ID: {receiver_id})\n"
        f"🎁 Amount: <code>{amount:.2f} ETB</code>\n"
        f"🆔 Transfer ID: <code>{transfer_id}</code>"
    )
