# Time Limit Feature - Testing Guide

## 🧪 How to Test 5-Minute Time Limit

---

## ✅ Test 1: Player Wins Before Time Limit

### **Setup:**
```bash
# Create game with normal settings
curl -X POST http://localhost:8000/admin/bingo/games \
  -H "Content-Type: application/json" \
  -H "X-Admin-Id: 1" \
  -d '{
    "entry_fee": 50,
    "max_players": 10,
    "min_players": 2
  }'
```

### **Steps:**
1. Join with 2+ players via Telegram bot
2. Start game via admin API
3. Wait for auto-caller to call numbers
4. First winner should get 100% of prize
5. Game ends immediately (before 5 min)

### **Expected Result:**
- ✅ Winner gets full prize
- ✅ Game status = FINISHED
- ✅ Duration < 5 minutes
- ✅ No house wins message

---

## ✅ Test 2: House Wins by Time Limit

### **Setup - Create Impossible-to-Win Game:**

To force a time limit win, you need cartelas that can't possibly win. You can either:

**Option A: Use many players (lower probability of win)**
```bash
# Create game
curl -X POST http://localhost:8000/admin/bingo/games \
  -H "Content-Type: application/json" \
  -H "X-Admin-Id: 1" \
  -d '{
    "entry_fee": 10,
    "max_players": 3,
    "min_players": 2
  }'
```

**Option B: Temporarily reduce time limit for testing**

Edit `backend/services/auto_number_caller_service.py`:
```python
# Change this line:
max_duration = 5 * 60  # 5 minutes

# To this (for testing only):
max_duration = 30  # 30 seconds for quick testing
```

### **Steps:**
1. Join with 2-3 players
2. Start game
3. **Wait exactly 5 minutes** (or 30 seconds if you changed it)
4. Auto-caller should detect time limit
5. Check logs for "exceeded 5 minute limit"

### **Expected Result:**
```
LOG: Game X exceeded 5 minute limit (300s), checking for winners
LOG: No winners found - house wins!
LOG: House wins - prize transferred to admin @HA
LOG: Game X finished - house wins (time limit)
```

**Database:**
```sql
-- Check admin wallet increased
SELECT main_wallet FROM users WHERE phone_number = '0909425014';

-- Check game status
SELECT status, started_at, finished_at 
FROM bingo_games 
WHERE id = X;

-- Check wallet transaction
SELECT * FROM wallet_transactions 
WHERE description LIKE '%House wins%' 
ORDER BY created_at DESC LIMIT 1;

-- Check game event
SELECT * FROM game_events 
WHERE game_id = X AND event_type = 'GAME_FINISHED';
```

---

## ✅ Test 3: House Wins by All Numbers

### **Setup:**
```bash
# Create game with very few players (low win probability)
curl -X POST http://localhost:8000/admin/bingo/games \
  -H "Content-Type: application/json" \
  -H "X-Admin-Id: 1" \
  -d '{
    "entry_fee": 10,
    "max_players": 2,
    "min_players": 1
  }'
```

### **Steps:**
1. Join with only 1-2 players
2. Start game
3. Let auto-caller run through all 75 numbers (~6 minutes)
4. If no winner by number 75, house should win

### **Expected Result:**
```
LOG: No more numbers to call - all 75 exhausted
LOG: No winners found - house wins!
LOG: House wins - prize transferred to admin @HA
```

---

## 🚀 Quick Test Script

### **For Rapid Testing (Bash):**

```bash
#!/bin/bash

# 1. Create admin user @HA if not exists
echo "Creating admin user @HA..."
psql $DATABASE_URL -c "
INSERT INTO users (telegram_id, phone_number, username, full_name, is_admin, is_registered, main_wallet, play_wallet)
VALUES (123456, '0909425014', 'HA', 'House Admin', true, true, 0, 0)
ON CONFLICT (phone_number) DO NOTHING;
"

# 2. Check admin wallet before
BEFORE=$(psql $DATABASE_URL -t -c "SELECT main_wallet FROM users WHERE phone_number='0909425014'")
echo "Admin wallet before: $BEFORE Birr"

# 3. Create game
GAME_ID=$(curl -s -X POST http://localhost:8000/admin/bingo/games \
  -H "Content-Type: application/json" \
  -H "X-Admin-Id: 1" \
  -d '{"entry_fee": 100, "max_players": 5, "min_players": 2}' \
  | jq -r '.id')

echo "Created game ID: $GAME_ID"

# 4. Join with test users (replace with your user IDs)
curl -X POST http://localhost:8000/api/v1/bingo/games/$GAME_ID/join \
  -H "X-User-Id: 1"

curl -X POST http://localhost:8000/api/v1/bingo/games/$GAME_ID/join \
  -H "X-User-Id: 2"

# 5. Start game
curl -X POST http://localhost:8000/admin/bingo/games/$GAME_ID/start \
  -H "X-Admin-Id: 1"

echo "Game started. Waiting for 5 minutes (time limit)..."

# 6. Wait 5 minutes
sleep 310  # 5 min + 10 sec buffer

# 7. Check results
echo "Checking results..."

# Check admin wallet after
AFTER=$(psql $DATABASE_URL -t -c "SELECT main_wallet FROM users WHERE phone_number='0909425014'")
echo "Admin wallet after: $AFTER Birr"

# Calculate difference
DIFF=$(echo "$AFTER - $BEFORE" | bc)
echo "House won: $DIFF Birr"

# Check game status
psql $DATABASE_URL -c "SELECT id, status, started_at, finished_at FROM bingo_games WHERE id=$GAME_ID"

# Check game events
psql $DATABASE_URL -c "SELECT event_type, description FROM game_events WHERE game_id=$GAME_ID ORDER BY created_at"
```

---

## 📊 Verification Checklist

After house wins (time limit):

### **Database Checks:**

```sql
-- 1. Game finished
SELECT status FROM bingo_games WHERE id = X;
-- Expected: FINISHED

-- 2. No winners in game
SELECT COUNT(*) FROM game_players WHERE game_id = X AND is_winner = true;
-- Expected: 0

-- 3. Admin wallet increased
SELECT main_wallet FROM users WHERE phone_number = '0909425014';
-- Expected: Increased by prize_pool amount

-- 4. Wallet transaction created
SELECT * FROM wallet_transactions 
WHERE user_id = (SELECT id FROM users WHERE phone_number = '0909425014')
  AND description LIKE '%House wins%'
ORDER BY created_at DESC LIMIT 1;
-- Expected: One row with ADMIN_CREDIT type

-- 5. Game event logged
SELECT * FROM game_events 
WHERE game_id = X 
  AND event_type = 'GAME_FINISHED'
  AND description LIKE '%House wins%';
-- Expected: One row with house_wins = true in event_data
```

### **API Checks:**

```bash
# Get game details
curl http://localhost:8000/admin/bingo/games/X \
  -H "X-Admin-Id: 1"

# Expected response:
{
  "id": X,
  "status": "FINISHED",
  "prize_pool": 200.0,
  ...
}

# Get game winners (should be empty)
curl http://localhost:8000/admin/bingo/games/X/winners \
  -H "X-Admin-Id: 1"

# Expected response:
{
  "game_id": X,
  "winners": [],
  "total_winners": 0
}
```

---

## 🐛 Common Issues

### **Issue 1: Admin @HA not found**
```
ERROR: Admin user @HA (0909425014) not found!
```

**Solution:**
```sql
INSERT INTO users (
    telegram_id,
    phone_number,
    username,
    full_name,
    is_admin,
    is_registered,
    main_wallet,
    play_wallet
) VALUES (
    123456789,
    '0909425014',
    'HA',
    'House Admin',
    true,
    true,
    0.00,
    0.00
);
```

---

### **Issue 2: Time limit not triggering**

**Check:**
1. Is auto-caller running? Check logs for "Auto-called number"
2. Is game status = PLAYING? Check `bingo_games.status`
3. Is started_at set? Check `bingo_games.started_at`

**Debug:**
```sql
-- Check game timing
SELECT 
    id,
    status,
    started_at,
    NOW() - started_at as elapsed,
    EXTRACT(EPOCH FROM (NOW() - started_at)) as elapsed_seconds
FROM bingo_games 
WHERE status = 'PLAYING';

-- Expected: If elapsed_seconds >= 300, house should win
```

---

### **Issue 3: Game not finishing**

**Force finish manually:**
```bash
curl -X POST http://localhost:8000/admin/bingo/games/X/finish \
  -H "X-Admin-Id: 1"
```

---

## ✅ Success Indicators

**Time limit working correctly when:**
- ✅ Game finishes at exactly 5 minutes if no winner
- ✅ Prize transfers to admin @HA
- ✅ Wallet transaction recorded
- ✅ Game event logged
- ✅ Players notified
- ✅ Admin wallet increases correctly

**Your time limit feature is ready!** ⏰
