# QUICK TEST GUIDE - Phase 2A Bingo

## 🚀 Start Servers

### Terminal 1: API Server
```bash
python run_api.py
```

**Wait for:** `INFO: Automatic number caller started (interval: 5s)`

### Terminal 2: Telegram Bot
```bash
python run_bot.py
```

**Wait for:** `INFO: Bot application started`

---

## 📱 Test via Telegram Bot (User Flow)

### 1. Register & Deposit
1. Open your Telegram bot
2. Click **📝 Register** → Share contact
3. Click **💰 Deposit** → Enter 100 → Forward SMS (or admin approves)

### 2. Create Game (Admin)
Use REST API to create a game:

```bash
curl -X POST http://localhost:8000/admin/bingo/games \
  -H "Content-Type: application/json" \
  -H "X-Admin-Id: YOUR_USER_ID" \
  -d '{
    "entry_fee": 10,
    "max_players": 10,
    "min_players": 2
  }'
```

**Response:** Game created with `game_id` and `game_number`

### 3. Join Game (Telegram)
1. Click **🎲 Play Bingo**
2. You'll see: "⏳ Waiting to Start: Game #XXX"
3. Click **🎮 Join Game #XXX (10 Birr)**
4. ✅ Success! Your cartela is displayed

**What happens:**
- 10 Birr deducted from play_wallet
- Unique cartela assigned
- Entry recorded in database

### 4. Start Game (Admin)
```bash
curl -X POST http://localhost:8000/admin/bingo/games/GAME_ID/start \
  -H "X-Admin-Id: YOUR_USER_ID"
```

**Result:** Game status → PLAYING

### 5. Watch Auto Number Calling
- Numbers are called automatically every 5 seconds
- Check logs: `INFO: Number called successfully`

### 6. View Your Card (Telegram)
1. Click **🎲 Play Bingo**
2. Click **📋 My Card - Game #XXX**
3. See cartela with ✅ marked numbers

**Example Display:**
```
🎫 Your Bingo Card
Game #1234

  B    I    N    G    O
━━━━━━━━━━━━━━━━━━━━━━
  5   20   35   50   65
  10  25  FREE  55   70
  15  30   40   60   75

Numbers called: 12/75
✅ = Number has been called
```

### 7. Win! 🎉
When you complete a pattern (row/column/diagonal/full):
- Game ends immediately (single winner mode)
- Prize credited to main_wallet automatically
- You receive notification

### 8. Check Stats
1. Click **🎲 Play Bingo**
2. Click **📊 My Games History**
3. See:
   - Games played
   - Games won
   - Win rate
   - Total winnings
   - Net profit

---

## 🔧 Test via REST API (Developer Flow)

### Get Available Games
```bash
curl http://localhost:8000/api/v1/bingo/games?status=waiting
```

### Join Game (User ID 1)
```bash
curl -X POST http://localhost:8000/api/v1/bingo/games/GAME_ID/join \
  -H "X-User-Id: 1"
```

### Get Game State
```bash
curl http://localhost:8000/api/v1/bingo/games/GAME_ID/state \
  -H "X-User-Id: 1"
```

**Response includes:**
- Game details
- Your cartela
- Called numbers
- Player count

### Get My Cartela
```bash
curl http://localhost:8000/api/v1/bingo/games/GAME_ID/cartela \
  -H "X-User-Id: 1"
```

### Get My Stats
```bash
curl http://localhost:8000/api/v1/bingo/me/stats \
  -H "X-User-Id: 1"
```

---

## 🎮 Admin Operations

### Create Game
```bash
curl -X POST http://localhost:8000/admin/bingo/games \
  -H "Content-Type: application/json" \
  -H "X-Admin-Id: 1" \
  -d '{
    "entry_fee": 50,
    "max_players": 10,
    "min_players": 2
  }'
```

### Start Game
```bash
curl -X POST http://localhost:8000/admin/bingo/games/GAME_ID/start \
  -H "X-Admin-Id: 1"
```

### Manual Call Number (Optional - auto caller does this)
```bash
curl -X POST http://localhost:8000/admin/bingo/games/GAME_ID/call-number \
  -H "X-Admin-Id: 1"
```

### Check Winners
```bash
curl http://localhost:8000/admin/bingo/games/GAME_ID/winners \
  -H "X-Admin-Id: 1"
```

### Get Game Players
```bash
curl http://localhost:8000/admin/bingo/games/GAME_ID/players \
  -H "X-Admin-Id: 1"
```

### Cancel Game (Refunds All Players)
```bash
curl -X POST http://localhost:8000/admin/bingo/games/GAME_ID/cancel \
  -H "X-Admin-Id: 1"
```

---

## ✅ What to Verify

### Financial Safety
- [ ] Entry fee deducted atomically
- [ ] Can't join twice (idempotent)
- [ ] Prize paid to winner only
- [ ] Refund works if game cancelled
- [ ] WalletTransaction created for each operation
- [ ] AuditLog records important events

### Game Logic
- [ ] Cartela has 25 numbers (5x5 grid)
- [ ] Center cell is FREE
- [ ] B column: 1-15, I: 16-30, N: 31-45, G: 46-60, O: 61-75
- [ ] Numbers 1-75 called in random order
- [ ] No number called twice
- [ ] First winner gets 100% of prize
- [ ] Game ends immediately after first winner

### Concurrency
- [ ] Multiple users can join simultaneously
- [ ] No race conditions in wallet operations
- [ ] Database row locking works (SELECT FOR UPDATE)

### Rate Limiting
- [ ] Spam join requests blocked (HTTP 429)
- [ ] Rate limit resets after time window
- [ ] Each user has independent rate limit

### Telegram Bot
- [ ] "🎲 Play Bingo" button appears
- [ ] Shows waiting and playing games
- [ ] Join button works
- [ ] Cartela displays correctly
- [ ] Marked numbers show with ✅
- [ ] Stats display correctly

---

## 🐛 Common Issues & Solutions

### Issue: "Authentication required"
**Solution:** Add `-H "X-User-Id: 1"` to curl commands

### Issue: "Insufficient balance"
**Solution:** Deposit funds first or transfer to play_wallet

### Issue: "Game not found"
**Solution:** Check GAME_ID is correct, game might be finished

### Issue: "Too many requests"
**Solution:** Wait 60 seconds for rate limit to reset

### Issue: Bot not responding
**Solution:** Check `python run_bot.py` is running

### Issue: Auto caller not working
**Solution:** Check API logs for `INFO: Automatic number caller started`

---

## 📊 Monitor Logs

### Watch API Logs
```bash
# Terminal 1
python run_api.py
```

**Look for:**
- `INFO: Automatic number caller started (interval: 5s)`
- `INFO: Number called successfully`
- `INFO: Winner detected`
- `INFO: Game finished - winner takes all`

### Watch Bot Logs
```bash
# Terminal 2
python run_bot.py
```

**Look for:**
- `INFO: Bot application started`
- `INFO: Bingo menu requested`
- `INFO: Balance requested`

---

## 🎉 Success Indicators

✅ **Backend Working:**
- API server starts without errors
- Auto caller logs every 5 seconds
- Database queries succeed

✅ **Bot Working:**
- Bot responds to buttons
- "🎲 Play Bingo" button shows
- Inline buttons work

✅ **Game Flow Working:**
- Can create game
- Can join game
- Numbers auto-call
- Winner detected
- Prize paid

✅ **Financial Safety Working:**
- Entry fee deducted
- Prize credited
- Refund works
- Ledger records all transactions

---

## 🚀 Ready for Production!

If all tests pass, your bingo system is ready! 🎉
