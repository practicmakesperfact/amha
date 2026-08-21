# BINGO GAME TESTING GUIDE

Quick guide to test the Phase 2A Bingo implementation.

---

## STEP 1: RUN MIGRATION

Create the bingo tables in your database:

```bash
alembic upgrade head
```

Verify tables were created:
```bash
# Connect to your PostgreSQL database
psql -h localhost -U your_user -d your_database

# List bingo tables
\dt *bingo*
\dt *cartela*
\dt *game_player*
\dt *called_number*
\dt *game_event*

# Exit
\q
```

You should see:
- bingo_games
- game_players
- cartelas
- called_numbers
- game_events

---

## STEP 2: START THE API

```bash
python run_api.py
```

The API should start on `http://localhost:8000`

---

## STEP 3: CREATE AN ADMIN USER

You need a user with `is_admin=true` to create games.

Option A: Use SQL directly
```sql
UPDATE users SET is_admin = true WHERE telegram_id = YOUR_TELEGRAM_ID;
```

Option B: Use the bot to register first, then set admin flag manually.

---

## STEP 4: TEST GAME FLOW

### 4.1 Create a Game (Admin)

```bash
curl -X POST http://localhost:8000/admin/bingo/games \
  -H "X-Admin-Id: 1" \
  -H "Content-Type: application/json" \
  -d '{
    "entry_fee": 50.0,
    "max_players": 10,
    "min_players": 2
  }'
```

Response should include `game_id` and `game_number`.

### 4.2 List Available Games

```bash
curl http://localhost:8000/api/v1/bingo/games
```

### 4.3 Join Game (Player 1)

```bash
curl -X POST http://localhost:8000/api/v1/bingo/games/1/join \
  -H "X-User-Id: 123"
```

**Note**: User 123 must exist in database and have sufficient balance (≥50 ETB).

### 4.4 Join Game (Player 2)

```bash
curl -X POST http://localhost:8000/api/v1/bingo/games/1/join \
  -H "X-User-Id: 456"
```

### 4.5 Get Game State

```bash
curl http://localhost:8000/api/v1/bingo/games/1/state \
  -H "X-User-Id: 123"
```

You should see:
- Game details
- Your player info
- Your cartela (5x5 grid with FREE in center)
- Called numbers (empty before start)

### 4.6 Start Game (Admin)

```bash
curl -X POST http://localhost:8000/admin/bingo/games/1/start \
  -H "X-Admin-Id: 1"
```

Game status should change to `PLAYING`.

### 4.7 Call Numbers (Admin)

Call multiple numbers to test winner detection:

```bash
# Call first number
curl -X POST http://localhost:8000/admin/bingo/games/1/call-number \
  -H "X-Admin-Id: 1"

# Call second number
curl -X POST http://localhost:8000/admin/bingo/games/1/call-number \
  -H "X-Admin-Id: 1"

# Keep calling until winner detected
```

After each number call:
- Check game state: `curl http://localhost:8000/api/v1/bingo/games/1/state -H "X-User-Id: 123"`
- Look for `called_numbers` array growing
- Look for `is_winner` flag on players

### 4.8 Check Winners

```bash
curl http://localhost:8000/admin/bingo/games/1/winners \
  -H "X-Admin-Id: 1"
```

### 4.9 Check Player Balance

After winning, verify wallet was credited:

```bash
# Check user balance via your existing admin endpoints
curl http://localhost:8000/api/admin/users/123 \
  -H "X-Admin-Id: 1"
```

### 4.10 Get Player Stats

```bash
curl http://localhost:8000/api/v1/bingo/me/stats \
  -H "X-User-Id: 123"
```

Should show:
- games_played: 1
- games_won: 1 (if won)
- win_rate: percentage
- total_winnings: prize amount

---

## STEP 5: TEST WEBSOCKET

### Using JavaScript (Browser Console)

```javascript
// Connect to game 1 as user 123
const ws = new WebSocket('ws://localhost:8000/ws/bingo/1?user_id=123');

ws.onopen = () => {
    console.log('Connected!');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Event:', data.event, data);
};

ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};

ws.onclose = () => {
    console.log('Disconnected');
};

// Send ping
ws.send(JSON.stringify({ type: 'ping' }));
```

### Using Python

```python
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/bingo/1?user_id=123"
    
    async with websockets.connect(uri) as websocket:
        # Receive initial state
        message = await websocket.recv()
        print(f"Received: {message}")
        
        # Send ping
        await websocket.send(json.dumps({"type": "ping"}))
        
        # Receive pong
        message = await websocket.recv()
        print(f"Received: {message}")
        
        # Keep listening for events
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Event: {data.get('event')}")
            print(f"Data: {data}")

asyncio.run(test_websocket())
```

---

## STEP 6: TEST EDGE CASES

### Insufficient Balance

Try joining with a user who doesn't have enough money:
```bash
curl -X POST http://localhost:8000/api/v1/bingo/games/1/join \
  -H "X-User-Id: 999"
```

Should return 400 error: "Insufficient balance"

### Duplicate Join

Try joining same game twice:
```bash
curl -X POST http://localhost:8000/api/v1/bingo/games/1/join \
  -H "X-User-Id: 123"
```

Should return 400 error: "User already joined this game"

### Join After Start

Start a game, then try to join:
```bash
curl -X POST http://localhost:8000/admin/bingo/games/1/start \
  -H "X-Admin-Id: 1"

curl -X POST http://localhost:8000/api/v1/bingo/games/1/join \
  -H "X-User-Id: 789"
```

Should return 400 error: "Cannot join game in status PLAYING"

### Game Cancellation

```bash
curl -X POST http://localhost:8000/admin/bingo/games/1/cancel \
  -H "X-Admin-Id: 1"
```

Check that all players were refunded.

---

## STEP 7: VERIFY DATABASE STATE

### Check Wallet Transactions

```sql
SELECT * FROM wallet_transactions 
WHERE description LIKE '%Bingo%' 
ORDER BY created_at DESC 
LIMIT 10;
```

### Check Audit Logs

```sql
SELECT * FROM audit_logs 
WHERE description LIKE '%Bingo%' 
ORDER BY created_at DESC 
LIMIT 10;
```

### Check Game Events

```sql
SELECT * FROM game_events 
WHERE game_id = 1 
ORDER BY created_at;
```

### Check Called Numbers

```sql
SELECT * FROM called_numbers 
WHERE game_id = 1 
ORDER BY sequence;
```

---

## STEP 8: TEST PAUSE/RESUME

```bash
# Start a game
curl -X POST http://localhost:8000/admin/bingo/games/1/start \
  -H "X-Admin-Id: 1"

# Pause it
curl -X POST http://localhost:8000/admin/bingo/games/1/pause \
  -H "X-Admin-Id: 1"

# Try calling number (should fail)
curl -X POST http://localhost:8000/admin/bingo/games/1/call-number \
  -H "X-Admin-Id: 1"

# Resume
curl -X POST http://localhost:8000/admin/bingo/games/1/resume \
  -H "X-Admin-Id: 1"

# Call number (should work now)
curl -X POST http://localhost:8000/admin/bingo/games/1/call-number \
  -H "X-Admin-Id: 1"
```

---

## STEP 9: TEST MULTIPLE WINNERS

Create a game with lower entry fee and join with multiple users. Keep calling numbers until you get 3 winners. Verify:
- Each winner gets correct prize percentage
- Prizes sum to ~prize pool
- All winners recorded in database

---

## TROUBLESHOOTING

### Error: "Game not found"
- Check game_id in URL matches created game
- Verify migration ran successfully

### Error: "User not found"
- User must exist in `users` table
- Use bot to register user first

### Error: "Insufficient balance"
- Credit user wallet via admin API or deposit
- Check `main_wallet` column in `users` table

### WebSocket won't connect
- Verify FastAPI is running
- Check firewall settings
- Try `ws://` instead of `wss://`

### Numbers not being called
- Check game status is `PLAYING`
- Verify you're using admin credentials

### Winner not detected
- Check cartela numbers vs called numbers
- Verify FREE cell is at position [2][2]
- Look at game_events table for validation errors

---

## EXPECTED TEST RESULTS

After successful testing, you should have:

1. ✅ Games created in `bingo_games` table
2. ✅ Players with cartelas in `game_players` and `cartelas` tables
3. ✅ Called numbers in `called_numbers` table
4. ✅ Winners with prizes in `game_players` table (`is_winner=true`, `prize_amount>0`)
5. ✅ Wallet transactions in `wallet_transactions` table (entry fees + prizes)
6. ✅ Audit logs in `audit_logs` table
7. ✅ Game events in `game_events` table
8. ✅ Updated user balances in `users` table
9. ✅ WebSocket events received by clients
10. ✅ Player statistics showing correct data

---

## NEXT STEPS

Once basic testing passes:

1. **Integrate with Telegram Bot**
   - Add bot commands: `/play`, `/bingo`, `/mybingos`
   - Replace X-User-Id with Telegram auth
   - Send game notifications via bot

2. **Implement Auto-Caller**
   - Background task to call numbers automatically
   - Configurable interval
   - Integrate with WebSocket broadcasts

3. **Add Rate Limiting**
   - Limit join attempts per user
   - Limit WebSocket connections per user

4. **Write Automated Tests**
   - Unit tests for services
   - Integration tests for APIs
   - Concurrency tests

5. **Production Hardening**
   - Add monitoring
   - Set up alerts
   - Performance tuning
   - Load testing

---

Last Updated: 2026-08-13
