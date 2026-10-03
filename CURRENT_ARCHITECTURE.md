# 🏗️ AMHABINGO - Current Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    TELEGRAM USERS                            │
│                         ↓↑                                   │
│                  Telegram Bot API                            │
└─────────────────────────────────────────────────────────────┘
                            ↓↑
┌─────────────────────────────────────────────────────────────┐
│              AMHABINGO TELEGRAM BOT (Python)                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Handlers:                                           │   │
│  │  • /start, Register, Balance                         │   │
│  │  • Deposit, Withdraw, Transfer                       │   │
│  │  • 🎲 Play Bingo ✅ (NEW!)                          │   │
│  │  • Admin callback handlers                           │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↓↑                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  FSM (Redis):                                        │   │
│  │  • Conversation state management                     │   │
│  │  • User flow tracking                                │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓↑
┌─────────────────────────────────────────────────────────────┐
│                  FASTAPI BACKEND                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Services:                                           │   │
│  │  • UserService                                       │   │
│  │  • DepositService, WithdrawalService                 │   │
│  │  • TransferService                                   │   │
│  │  • BingoGameService ✅ (NEW!)                       │   │
│  │  • GameEngineService ✅ (NEW!)                      │   │
│  │  • WinnerValidatorService ✅ (NEW!)                 │   │
│  │  • AutoNumberCallerService ✅ (NEW!)                │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↓↑                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Repositories:                                       │   │
│  │  • UserRepository                                    │   │
│  │  • DepositRepository, WithdrawalRepository           │   │
│  │  • BingoGameRepository ✅ (NEW!)                    │   │
│  │  • GamePlayerRepository ✅ (NEW!)                   │   │
│  │  • CartelaRepository ✅ (NEW!)                      │   │
│  │  • CalledNumberRepository ✅ (NEW!)                 │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↓↑                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  REST APIs:                                          │   │
│  │  • /admin/* (user/deposit/withdrawal/transfer)       │   │
│  │  • /api/v1/bingo/games ✅ (NEW!)                    │   │
│  │  • /api/v1/bingo/games/{id}/join ✅ (NEW!)         │   │
│  │  • /admin/games (CRUD) ✅ (NEW!)                    │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↓↑                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  WebSocket:                                          │   │
│  │  • /ws/bingo/{game_id} ✅ (NEW!)                    │   │
│  │  • Real-time number calling                          │   │
│  │  • Winner notifications                              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓↑
┌─────────────────────────────────────────────────────────────┐
│                     DATA LAYER                               │
│  ┌─────────────────────┐  ┌─────────────────────────────┐   │
│  │   PostgreSQL        │  │   Redis                     │   │
│  │   (Supabase)        │  │   (In-Memory / Cloud)       │   │
│  ├─────────────────────┤  ├─────────────────────────────┤   │
│  │ • users             │  │ • FSM states                │   │
│  │ • wallet_trans...   │  │ • Rate limiting             │   │
│  │ • audit_logs        │  │ • Game state cache ✅       │   │
│  │ • deposits          │  │ • Pub/Sub (future) ⏳       │   │
│  │ • withdrawals       │  │                             │   │
│  │ • transfers         │  │                             │   │
│  │ • bingo_games ✅    │  │                             │   │
│  │ • game_players ✅   │  │                             │   │
│  │ • cartelas ✅       │  │                             │   │
│  │ • called_numbers ✅ │  │                             │   │
│  │ • game_events ✅    │  │                             │   │
│  └─────────────────────┘  └─────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Status

### ✅ PHASE 1: Complete
- Telegram Bot (python-telegram-bot v21+)
- User registration & authentication
- Financial system (deposit/withdraw/transfer)
- Multi-wallet (main_wallet, play_wallet, coin, wins)
- WalletTransaction ledger
- AuditLog system
- Admin REST API
- Rate limiting
- Docker configuration

### ✅ PHASE 2A: Complete
- Bingo game engine (5 tables)
- 8 game services (cartela, winner, number caller, etc.)
- REST APIs (18 endpoints)
- WebSocket endpoint
- Real-time game state
- Prize distribution
- House wins logic
- Telegram bot bingo integration

### ⏳ PHASE 2B: Not Started
- Next.js Telegram Mini App
- Admin Dashboard UI
- Automated tests

---

## Database Schema (PostgreSQL)

### Phase 1 Tables:
```sql
users
├── id (PK)
├── telegram_id (unique)
├── username
├── phone_number (unique)
├── full_name
├── is_registered
├── is_admin ⚠️ (needs to be set for admin user)
├── main_wallet
├── play_wallet
├── coin
├── wins
└── timestamps

wallet_transactions
├── id (PK)
├── user_id (FK)
├── transaction_type
├── amount
├── status
├── reference_id
└── timestamps

deposits
withdrawals
transfers
audit_logs
```

### Phase 2A Tables:
```sql
bingo_games
├── id (PK)
├── game_number (unique)
├── status (WAITING/PLAYING/FINISHED/CANCELLED)
├── entry_fee
├── prize_pool
├── max_players
├── min_players
├── started_at
├── finished_at
└── timestamps

game_players
├── id (PK)
├── game_id (FK)
├── user_id (FK)
├── cartela_id (FK)
├── entry_fee
├── status
├── is_winner
├── prize_amount
└── timestamps
UNIQUE(game_id, user_id)

cartelas
├── id (PK)
├── game_id (FK)
├── user_id (FK)
├── numbers (JSON: 5x5 array)
└── timestamps

called_numbers
├── id (PK)
├── game_id (FK)
├── number (1-75)
├── sequence
└── called_at
UNIQUE(game_id, number)

game_events
├── id (PK)
├── game_id (FK)
├── event_type
├── event_data (JSON)
└── timestamp
```

---

## Data Flow Examples

### 1. User Joins Game
```
User clicks "🎮 Join Game #1"
    ↓
bingo_callback_handler()
    ↓
BingoGameService.join_game()
    ↓
┌─ Verify game exists & is WAITING
├─ Verify user not already joined
├─ Lock user wallet (SELECT FOR UPDATE)
├─ Verify sufficient balance
├─ Deduct entry_fee from play_wallet
├─ Create WalletTransaction (GAME_ENTRY)
├─ Update game.prize_pool
├─ Generate unique cartela
├─ Create Cartela record
├─ Create GamePlayer record
├─ Create GameEvent (PLAYER_JOINED)
└─ Commit transaction
    ↓
Bot sends: "✅ Joined! Here's your card..."
```

### 2. Number Called (Automatic)
```
AutoNumberCallerService (background task)
    ↓
Every 5 seconds:
├─ Get game from Redis cache
├─ Verify game is PLAYING
├─ Check if 5 minutes elapsed → House wins if true
├─ Select random uncalled number (1-75)
├─ Create CalledNumber record
├─ Update Redis cache
├─ Check all players for winners
│   └─ If winner found:
│       ├─ Validate winning pattern
│       ├─ Credit prize to winner
│       ├─ Create WalletTransaction (GAME_PRIZE)
│       ├─ Create GameEvent (WINNER_DECLARED)
│       ├─ Set game status = FINISHED
│       └─ Broadcast winner notification
└─ Broadcast NUMBER_CALLED via WebSocket
    ↓
All connected players receive update
```

### 3. House Wins (Time Limit)
```
AutoNumberCallerService checks every 5s:
    ↓
If (time.now - game.started_at) > 5 minutes:
    ↓
GameEngineService._handle_no_winner_house_wins()
    ↓
├─ Get admin user (phone: 0909425014)
├─ Credit prize_pool to admin.main_wallet
├─ Create WalletTransaction (ADMIN_CREDIT)
├─ Create GameEvent (house_wins_5min_timeout)
├─ Set game status = FINISHED
└─ Broadcast to all players: "House wins!"
```

---

## Critical Configuration

### Required SQL (NOT DONE YET):
```sql
-- Make hay man an admin
UPDATE users 
SET is_admin = true, 
    username = 'HA'
WHERE phone_number = '0909425014';
```

### Environment Variables:
```env
# Telegram
TELEGRAM_BOT_TOKEN=8724658540:AAFQkvFuHM1KdkazV7Ob1o43ABuxb0FTRQ0
BOT_USERNAME=amhabingo_bot

# Database
DATABASE_URL=postgresql+asyncpg://postgres.unvullajggwzgamlrfii:GbXLbMpS1%212@aws-0-eu-west-1.pooler.supabase.com:5432/postgres

# Redis
REDIS_URL=memory://  # In-memory for now

# Admin
ADMIN_TELEGRAM_IDS=[5655910680]
TELEBIRR_RECEIVER_NUMBER=0909425014

# Bingo Settings
BINGO_MIN_PLAYERS=2
BINGO_MAX_PLAYERS=100
BINGO_NUMBER_INTERVAL_SECONDS=5
BINGO_MIN_ENTRY_FEE=10.0
BINGO_MAX_ENTRY_FEE=1000.0
```

---

## Running the System

### Development (Current):
```bash
# Terminal 1: Start bot
python run_bot.py

# Terminal 2: Test API
curl http://localhost:8000/admin/stats \
  -H "X-Admin-Id: 5655910680"
```

### Production (Recommended):
```bash
# Use webhook mode instead of polling
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Background worker for number calling
# (Runs automatically with FastAPI startup)
```

---

## Missing Features for Launch

### Critical (Must Have):
1. ⚠️ **Admin bot commands** - Easy way to create games
   - `/admin_create_game <entry_fee> <max_players> <min_players>`
   - `/admin_start_game <game_id>`
   - `/admin_cancel_game <game_id>`
   - `/admin_list_games`

2. ⚠️ **Set admin user** - Run SQL to make 0909425014 admin

3. ⚠️ **Auto-start games** - Start when min_players reached
   - Currently requires manual start via API

### Nice to Have:
1. ✅ WebSocket broadcasting improvements
2. ✅ Better error messages for users
3. ✅ Game history UI in bot
4. ✅ Leaderboard

### Future (Phase 2B):
1. ⏳ Next.js Mini App with visual Bingo card
2. ⏳ Admin Dashboard web interface
3. ⏳ Automated tests
4. ⏳ Redis Pub/Sub (for multi-server scaling)

---

## Security Features

### Financial Protection:
- ✅ Row locking (SELECT FOR UPDATE)
- ✅ Atomic transactions
- ✅ WalletTransaction ledger
- ✅ AuditLog trail
- ✅ Idempotent operations
- ✅ Status validation

### Game Integrity:
- ✅ Server-authoritative (never trust client)
- ✅ Cartela generation server-side
- ✅ Winner validation server-side
- ✅ Number calling server-side
- ✅ Prize calculation server-side
- ✅ Anti-cheat (no client manipulation possible)

### Rate Limiting:
- ✅ 30 requests per 60 seconds per user
- ✅ Applied to critical endpoints
- ✅ Redis-based tracking

---

## Next Steps

**Choose Your Path:**

### Option A: Launch Text Bot NOW
1. Add admin bot commands (1 hour)
2. Set admin user via SQL
3. Deploy bot
4. Create first game
5. Test with real users
6. Start earning! 💰

### Option B: Build Mini App First
1. Set up Next.js project (4 hours)
2. Implement Telegram Mini App SDK (2 days)
3. Build game UI components (1 week)
4. Integrate with existing APIs (3 days)
5. Test & deploy (1 week)
6. **Total: 3-4 weeks**

**My Recommendation:** Option A 🚀
