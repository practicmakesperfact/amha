You are a Senior Python Backend Engineer and Telegram Bot Expert.

Build a COMPLETE production-ready Telegram Bot for AMHABINGO.

This phase ONLY builds the Telegram Bot.

DO NOT build the Telegram Mini App yet.
DO NOT build the Next.js frontend yet.

=========================================================
TECH STACK
=========================================================

- Python 3.13
- python-telegram-bot v21+
- FastAPI
- PostgreSQL
- SQLAlchemy 2 Async
- Alembic
- Redis
- Pydantic v2
- AsyncIO
- Docker Ready
- Production Logging

Architecture:

backend/
    bot/
    handlers/
    keyboards/
    services/
    repositories/
    database/
    middleware/
    models/
    utils/
    admin/
    core/

Use Clean Architecture and Repository Pattern.

=========================================================
GENERAL REQUIREMENTS
=========================================================

Everything must be asynchronous.

No placeholder code.

No duplicated code.

Every command must work.

Every handler must have proper error handling.

Every database operation must use transactions.

Every important action must be logged.

=========================================================
START COMMAND
=========================================================

When user sends

/start

Bot must:

• Verify Telegram user
• Create local user if doesn't exist
• Update Telegram username
• Update full name
• Save Telegram ID
• Save chat ID
• Save first name
• Save last name
• Save username
• Display welcome banner
• Display persistent keyboard
• Never silently fail

The keyboard must ALWAYS remain visible.

Use

ReplyKeyboardMarkup

with

resize_keyboard=True
is_persistent=True
one_time_keyboard=False

The keyboard must automatically appear every time the user opens the chat or sends /start.

=========================================================
MAIN MENU
=========================================================

Layout:

🎮 Play                 📝 Register

💰 Deposit              💵 Balance

💸 Withdraw             🎁 Transfer

📖 Instruction          ☎ Support

The keyboard must remain visible after every response.

Every response must include the keyboard.

=========================================================
REGISTER
=========================================================

When user presses

📝 Register

Bot first checks database.

IF USER ALREADY REGISTERED

Return

✅ You are already registered.

Do not ask anything else.

IF USER NOT REGISTERED

Bot sends

Please share your contact information.

Display a keyboard containing ONLY ONE BUTTON

📱 Share Contact

The button must use

KeyboardButton(request_contact=True)

When user presses Share Contact

Automatically obtain

• Telegram ID
• Username
• First Name
• Last Name
• Phone Number

Generate Full Name

Example

Hay Man

Store

telegram_id
chat_id
username
first_name
last_name
full_name
phone_number
balance=0
play_wallet=0
coin=0
wins=0
is_registered=True

Return

✅ Registration completed successfully.

Never ask the user to type their phone number.

Only accept Telegram shared contacts.

=========================================================
PLAY
=========================================================

When user presses

🎮 Play

Display

🚧 Telegram Mini App

Coming Soon.

Our real-time Bingo Mini App will be available soon.

No game logic yet.

Later this button will open the Telegram Mini App using

WebAppInfo()

Design the code so changing from "Coming Soon" to opening the Mini App only requires changing one function.

=========================================================
BALANCE
=========================================================

Display

👤 Name:
Hay Man

📞 Phone:
0909425014

💰 Main Wallet:
0.00 ETB

🎮 Play Wallet:
0.00 ETB

🪙 Coin:
0

Use formatted text.

Fetch values from PostgreSQL.

=========================================================
DEPOSIT
=========================================================

Conversation flow

User presses

💰 Deposit

Bot asks

How much would you like to deposit?

Accept only positive numbers.

Example

100

200

500

1000

After amount entered

Generate unique Deposit Request.

Store

user
amount
status=PENDING
created_at

Bot replies

Please send exactly

100 ETB

to the following Telebirr number

📱 0909425014

IMPORTANT

Payments must only be sent to this number.

After payment

Paste the COMPLETE Telebirr confirmation SMS below.

=========================================================
SMS VERIFICATION
=========================================================

When user pastes SMS

Bot must

Extract

Sender Number

Receiver Number

Amount

Reference Number

Date

Transaction ID

Validate

Receiver number MUST be

0909425014

If different

Reject.

Validate

Reference Number has never been submitted before.

If duplicate

Return

❌ This Telebirr confirmation message has already been used.

Please paste a valid payment confirmation.

Store every used reference forever.

Prevent duplicate deposits.

If valid

Store

Original SMS

Parsed SMS

Reference Number

Amount

User

Status=PENDING_ADMIN_APPROVAL

Notify Admin Dashboard.

Reply

✅ Deposit submitted successfully.

Waiting for admin approval.

Balance is NOT updated until admin approval.

=========================================================
DEPOSIT (AUTO APPROVAL)
=========================================================

When user presses

💰 Deposit

Bot asks:

How much would you like to deposit?

Accept only positive numbers.

Example:

100
200
500
1000

Store a pending deposit session in Redis.

Bot replies:

Please send exactly

100 ETB

to the following Telebirr number:

📱 0909425014

After payment, paste the COMPLETE Telebirr confirmation SMS.

=========================================================
SMS VERIFICATION
=========================================================

When the user pastes the Telebirr confirmation SMS:

The bot automatically extracts:

- Sender phone number
- Receiver phone number
- Amount
- Transaction/Reference number
- Date and time

Validation:

1. Receiver phone number MUST equal:
   0909425014

2. Amount in SMS MUST exactly match the requested deposit amount.

3. Transaction/Reference number must not already exist in the database.

4. Reject edited or invalid SMS formats.

If any validation fails:

❌ Invalid payment confirmation.
Please send a valid Telebirr confirmation SMS.

If the reference number already exists:

❌ This payment confirmation has already been used.

If all validations pass:

- Save the deposit record.
- Save the SMS text.
- Save the parsed transaction details.
- Save the unique transaction/reference number.
- Immediately credit the user's Main Wallet with the deposited amount.
- Mark the deposit status as APPROVED.
- Notify the user:

✅ Deposit successful.

100 ETB has been added to your Main Wallet.

No admin approval is required for deposits.

Log the deposit for the Admin Dashboard.

=========================================================
WITHDRAW
=========================================================

Withdrawal requests REQUIRE admin approval.

Workflow:

- Validate minimum withdrawal.
- Validate sufficient balance.
- Ask for Telebirr number.
- Ask for amount.
- Create a withdrawal request with status=PENDING.
- Notify administrators.
- Do NOT deduct balance until an admin approves.
- After approval:
  - Deduct the balance.
  - Mark as APPROVED.
  - Notify the user.

=========================================================
TRANSFER
=========================================================

Transfers REQUIRE admin approval.

Workflow:

- Ask for recipient username or phone number.
- Validate recipient exists.
- Ask for transfer amount.
- Validate sender has enough balance.
- Create transfer request with status=PENDING.
- Notify administrators.
- Do NOT move funds until approved.
- After approval:
  - Transfer funds atomically.
  - Notify both sender and recipient.

=========================================================
INSTRUCTION
=========================================================

Explain

Registration

Deposit

Withdraw

Transfer

Play

Winning

Support

Use formatted messages.

=========================================================
SUPPORT
=========================================================

Display

☎ AMHABINGO Support

Support Channel

https://t.me/amhabingosupport_team

Bot

@AMHABINGOBOT

Display clickable links.

=========================================================
ADMIN PANEL
=========================================================

Build backend APIs and models for future admin panel.

Admin can view

Users

Deposits

Withdrawals

Transfers

Registration History

Wallet Balances

Coins

Wins

Pending Requests

Approved Requests

Rejected Requests

Search Users

Search Transactions

Approve Deposit

Reject Deposit

Approve Withdraw

Reject Withdraw

Approve Transfer

Reject Transfer

Export Reports

No frontend required yet.

Only backend services and APIs.

=========================================================
DATABASE
=========================================================

Users

id
telegram_id
chat_id
username
first_name
last_name
full_name
phone_number
main_wallet
play_wallet
coin
wins
registered
created_at

Deposits

id
user_id
amount
sms_text
reference
receiver_phone
status
created_at

Withdrawals

id
user_id
telebirr_number
amount
status
created_at

Transfers

id
sender_id
receiver_id
amount
status
created_at

UsedSMS

id
reference_number
sms_hash
created_at

=========================================================
REDIS
=========================================================

Use Redis for

Conversation State

FSM

Rate Limiting

Temporary Sessions

=========================================================
SECURITY
=========================================================

Prevent

Duplicate registrations

Duplicate SMS

SQL Injection

Spam

Replay attacks

Invalid phone numbers

Invalid amounts

=========================================================
LOGGING
=========================================================

Log

Every command

Every callback

Every registration

Every deposit

Every withdrawal

Every transfer

Every admin approval

Every exception

=========================================================
QUALITY
=========================================================

Everything must be

Production Ready

Async

PEP8

Type hinted

Clean Architecture

Repository Pattern

Service Layer

Reusable

Modular

Easy to extend to Telegram Mini App later.

The bot should behave similarly to Beteseb Bingo, with a persistent keyboard, smooth conversation flow, robust validation, and full backend support for future integration with the Telegram Mini App and admin dashboard.