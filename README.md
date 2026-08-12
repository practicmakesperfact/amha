# 🎮 AMHABINGO - Telegram Bot

**Production-ready Telegram bot for AMHABINGO bingo gaming platform**

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-21+-green.svg)](https://python-telegram-bot.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-teal.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-blue.svg)](https://www.postgresql.org/)
[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen.svg)]()

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Testing](#testing)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

### User Features
- 🎮 **Interactive Menu** - Persistent keyboard with all features
- 📝 **Easy Registration** - One-tap contact sharing
- 💰 **Instant Deposits** - Auto-verified via Telebirr SMS
- 💸 **Withdrawals** - Admin-approved, secure process
- 🎁 **Transfers** - Send money to other users
- 💵 **Balance Tracking** - Real-time wallet management
- 📖 **Instructions** - Complete user guide built-in
- ☎️ **Support** - Direct support channel access

### Admin Features
- 📊 **Admin Dashboard** - Full REST API for management
- 🔔 **Real-time Notifications** - Telegram alerts for all requests
- ⚡ **Quick Actions** - Inline approve/reject buttons
- 👥 **User Management** - Search, view, manage users
- 📈 **Analytics** - Transaction stats and insights
- 🔐 **Multi-admin Support** - Multiple administrators

### Security Features
- 🛡️ **SMS Verification** - Telebirr payment validation
- 🚫 **Duplicate Prevention** - Reference number tracking
- ⏱️ **Timestamp Validation** - 30-minute transaction window
- 💰 **Balance Protection** - Race condition prevention
- 🔒 **Idempotent Operations** - Can't double-process
- 🔑 **Rate Limiting** - Spam prevention

---

## 🛠 Tech Stack

### Backend
- **Python 3.13** - Latest Python features
- **python-telegram-bot v21+** - Telegram Bot API
- **FastAPI** - Modern REST API framework
- **SQLAlchemy 2 Async** - Async ORM
- **Alembic** - Database migrations
- **Pydantic v2** - Data validation

### Database & Cache
- **PostgreSQL 16+** - Primary database
- **Redis** - Session management & FSM

### Architecture
- **Clean Architecture** - Separation of concerns
- **Repository Pattern** - Data access abstraction
- **Service Layer** - Business logic isolation
- **Async/Await** - Non-blocking operations

---

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- PostgreSQL 16+
- Redis
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))

### Installation

1. **Clone Repository**
   ```bash
   git clone https://github.com/yourusername/amhabingo-bot.git
   cd amhabingo-bot
   ```

2. **Create Virtual Environment**
   ```bash
   python3.13 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your settings
   ```

5. **Setup Database**
   ```bash
   # Run migrations
   alembic upgrade head
   
   # Verify setup
   python check_db.py
   ```

6. **Run Bot**
   ```bash
   # Polling mode (development)
   python backend/run_polling.py
   
   # Or webhook mode (production)
   uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md) | Complete feature documentation |
| [ADMIN_QUICK_GUIDE.md](ADMIN_QUICK_GUIDE.md) | Admin user guide |
| [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) | Step-by-step deployment |
| [CHANGES_SUMMARY.md](CHANGES_SUMMARY.md) | Recent changes and updates |
| [prompt.md](prompt.md) | Original requirements |

---

## 📁 Project Structure

```
amhabingo-bot/
├── backend/
│   ├── admin/              # Admin API routes
│   ├── bot/                # Bot core (application, FSM, messages)
│   ├── core/               # Configuration, logging, Redis
│   ├── database/           # Database connection & session
│   ├── handlers/           # Telegram message handlers
│   ├── keyboards/          # Reply & inline keyboards
│   ├── middleware/         # Rate limiting, etc.
│   ├── models/             # SQLAlchemy models
│   ├── repositories/       # Data access layer
│   ├── services/           # Business logic layer
│   ├── utils/              # Utilities (SMS parser, validators)
│   ├── main.py             # FastAPI application
│   └── run_polling.py      # Bot polling mode
├── alembic/                # Database migrations
│   └── versions/           # Migration files
├── tests/                  # Test files
├── .env                    # Environment variables
├── alembic.ini             # Alembic configuration
├── docker-compose.yml      # Docker Compose setup
├── Dockerfile              # Docker image
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file with:

```env
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_WEBHOOK_URL=https://yourdomain.com  # Optional
BOT_USERNAME=your_bot_username

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host/db

# Redis
REDIS_URL=redis://localhost:6379/0

# Admin
ADMIN_TELEGRAM_IDS=[123456789,987654321]

# Business
TELEBIRR_RECEIVER_NUMBER=0909425014
SUPPORT_CHANNEL_URL=https://t.me/your_support_channel

# Limits
MIN_DEPOSIT_AMOUNT=10.0
MIN_WITHDRAWAL_AMOUNT=50.0
MIN_TRANSFER_AMOUNT=10.0
MAX_WITHDRAWAL_AMOUNT=50000.0
MAX_TRANSFER_AMOUNT=50000.0

# App
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO
ENVIRONMENT=production
```

See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for details.

---

## 🐳 Deployment

### Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# Run migrations
docker-compose exec bot alembic upgrade head

# View logs
docker-compose logs -f bot

# Stop services
docker-compose down
```

### Manual Deployment

See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for:
- VPS deployment
- Systemd service setup
- Nginx configuration
- SSL setup

### Render.com / Cloud

Use included `render.yaml` for one-click deployment.

---

## 🧪 Testing

### Manual Testing
1. Start bot: `python run_bot.py`
2. Send `/start` to your bot
3. Test each feature:
   - Registration
   - Deposit with SMS
   - Withdrawal request
   - Transfer request
   - Admin approvals

### Check Database
```bash
python check_db.py
```

---

## 📡 API Reference

### Admin API

**Base URL:** `http://your-domain.com/admin/`

**Authentication:** Header `X-Admin-Id: YOUR_TELEGRAM_ID`

#### Endpoints

**Users**
- `GET /admin/users` - List users
- `GET /admin/users/{id}` - Get user
- `GET /admin/users?search=query` - Search

**Deposits**
- `GET /admin/deposits` - List deposits
- `POST /admin/deposits/{id}/approve` - Approve
- `POST /admin/deposits/{id}/reject` - Reject

**Withdrawals**
- `GET /admin/withdrawals` - List withdrawals
- `POST /admin/withdrawals/{id}/approve` - Approve
- `POST /admin/withdrawals/{id}/reject` - Reject

**Transfers**
- `GET /admin/transfers` - List transfers
- `POST /admin/transfers/{id}/approve` - Approve
- `POST /admin/transfers/{id}/reject` - Reject

**Stats**
- `GET /admin/stats` - Dashboard statistics

See [ADMIN_QUICK_GUIDE.md](ADMIN_QUICK_GUIDE.md) for examples.

---

## 🎯 Features Checklist

- ✅ Start command with user creation
- ✅ Persistent reply keyboard
- ✅ Contact-based registration
- ✅ Auto-approved deposits with SMS verification
- ✅ Admin-approved withdrawals
- ✅ Admin-approved transfers
- ✅ Balance display
- ✅ Instructions
- ✅ Support links
- ✅ Admin notifications
- ✅ User notifications
- ✅ Min/max amount limits
- ✅ Duplicate SMS prevention
- ✅ Timestamp validation
- ✅ Race condition protection
- ✅ Idempotent operations
- ✅ Rate limiting
- ✅ Comprehensive logging
- ✅ Clean architecture
- ✅ Full type hints
- ✅ Docker support
- ✅ Admin REST API
- ✅ Database migrations
- ✅ Error handling

---

## 💡 Usage Examples

### User Flow

1. **Registration**
   ```
   User: /start
   Bot: Welcome! [Shows keyboard]
   User: [Presses 📝 Register]
   Bot: Share your contact
   User: [Shares contact]
   Bot: ✅ Registration complete!
   ```

2. **Deposit**
   ```
   User: [Presses 💰 Deposit]
   Bot: How much?
   User: 100
   Bot: Send 100 ETB to 0909425014
   User: [Pastes Telebirr SMS]
   Bot: ✅ Deposit successful! 100 ETB added.
   ```

3. **Withdrawal**
   ```
   User: [Presses 💸 Withdraw]
   Bot: Enter Telebirr number
   User: 0912345678
   Bot: How much?
   User: 200
   Bot: ✅ Request submitted!
   Admin: [Receives notification, approves]
   User: ✅ Withdrawal approved! 200 ETB will be sent.
   ```

### Admin Flow

1. **Receive Notification**
   ```
   Bot → Admin: 🔔 New Withdrawal Request
                 User: John (ID: 123)
                 Amount: 200 ETB
                 [✅ Approve] [❌ Reject]
   ```

2. **Approve**
   ```
   Admin: [Clicks ✅ Approve]
   Bot → Admin: ✅ Withdrawal #15 approved.
   Bot → User: ✅ Withdrawal approved! 200 ETB will be sent.
   Admin: [Sends money via Telebirr]
   ```

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## 📄 License

This project is proprietary software. All rights reserved.

---

## 📞 Support

- **Telegram Support:** [@amhabingosupport_team](https://t.me/amhabingosupport_team)
- **Bot:** [@amhabingo_bot](https://t.me/amhabingo_bot)
- **Issues:** GitHub Issues

---

## 🙏 Acknowledgments

Built with:
- [python-telegram-bot](https://python-telegram-bot.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Alembic](https://alembic.sqlalchemy.org/)

---

## 📊 Status

**Current Version:** 1.0.0  
**Status:** Production Ready ✅  
**Last Updated:** December 2024

---

**Made with ❤️ for AMHABINGO**

🎮 Play | 💰 Win | 🎉 Enjoy
