# BINGO API GUIDE

Complete API reference for AMHABINGO Phase 2A - Bingo Game Backend.

---

## TABLE OF CONTENTS

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Game Lifecycle](#game-lifecycle)
4. [Player APIs](#player-apis)
5. [Admin APIs](#admin-apis)
6. [WebSocket API](#websocket-api)
7. [Data Models](#data-models)
8. [Examples](#examples)

---

## OVERVIEW

The Bingo game system supports:
- Standard 75-ball Bingo
- Multiple concurrent games
- Real-time updates via WebSocket
- Server-authoritative gameplay
- Automated winner detection
- Prize distribution

### Game Flow

```
1. Admin creates game → WAITING
2. Players join (entry fee deducted, cartela assigned)
3. Admin starts game → PLAYING
4. Numbers called automatically or manually
5. System validates winners server-side
6. Prizes paid automatically
7. Game finishes → FINISHED
```

---

## AUTHENTICATION

### Player Endpoints

**Temporary**: Use `X-User-Id` header

```
X-User-Id: 123
```

**Production**: Will use Telegram authentication token

### Admin Endpoints

Use existing admin auth:

```
X-Admin-Id: 1
```

Admin user must have `is_admin=true` in database.

---

## GAME LIFECYCLE

### Game States

- `WAITING` - Accepting players
- `STARTING` - Game about to begin
- `PLAYING` - Numbers being called
- `PAUSED` - Temporarily stopped
- `FINISHED` - Game completed
- `CANCELLED` - Game cancelled (players refunded)

### State Transitions

```
WAITING → PLAYING (start)
PLAYING → PAUSED (pause)
PAUSED → PLAYING (resume)
PLAYING → FINISHED (finish)
WAITING → CANCELLED (cancel)
```

---

## PLAYER APIS

Base URL: `/api/v1/bingo`

### List Available Games

```http
GET /api/v1/bingo/games?status=waiting&skip=0&limit=100
```

Query params:
- `status` (optional): `waiting`, `active`, or all
- `skip` (optional): Pagination offset
- `limit` (optional): Max results (default 100)

Response:
```json
{
  "games": [
    {
      "id": 1,
      "game_number": "BG202608131A2B3C4D",
      "status": "WAITING",
      "entry_fee": 50.0,
      "prize_pool": 500.0,
      "max_players": 100,
      "min_players": 2,
      "player_count": 10,
      "current_number": null,
      "numbers_called_count": 0,
      "started_at": null,
      "finished_at": null,
      "created_at": "2026-08-13T10:00:00Z",
      "updated_at": "2026-08-13T10:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

### Get Game Details

```http
GET /api/v1/bingo/games/{game_id}
```

Response: Same as game object above

### Join Game

```http
POST /api/v1/bingo/games/{game_id}/join
Headers: X-User-Id: 123
```

Actions:
1. Validates user has sufficient balance
2. Deducts entry fee atomically
3. Generates unique cartela (5x5, FREE center)
4. Assigns cartela to player
5. Adds to prize pool
6. Records wallet transaction

Response:
```json
{
  "id": 1,
  "game_id": 1,
  "user_id": 123,
  "cartela_id": 1,
  "entry_fee": 50.0,
  "prize_amount": 0.0,
  "status": "JOINED",
  "is_winner": false,
  "winning_position": null,
  "win_pattern": null,
  "joined_at": "2026-08-13T10:01:00Z",
  "left_at": null
}
```

### Get Game State

```http
GET /api/v1/bingo/games/{game_id}/state
Headers: X-User-Id: 123
```

Complete game state including player's cartela and called numbers.

Response:
```json
{
  "game": { /* game object */ },
  "player": { /* player object */ },
  "cartela": {
    "id": 1,
    "game_id": 1,
    "user_id": 123,
    "numbers": [
      [5, 19, 34, 47, 68],
      [12, 22, 39, 53, 71],
      [3, 28, 0, 59, 64],  // 0 = FREE
      [14, 17, 41, 48, 73],
      [8, 30, 36, 55, 62]
    ],
    "cartela_number": "G1-U123-A1B2C3D4",
    "created_at": "2026-08-13T10:01:00Z"
  },
  "called_numbers": [5, 12, 19, 22, 28, 34],
  "last_called": {
    "number": 34,
    "column_letter": "N",
    "sequence": 6,
    "called_at": "2026-08-13T10:05:30Z"
  }
}
```

### Get My Cartela

```http
GET /api/v1/bingo/games/{game_id}/cartela
Headers: X-User-Id: 123
```

Returns cartela object (see above).

### Get My Games

```http
GET /api/v1/bingo/me/games?skip=0&limit=100
Headers: X-User-Id: 123
```

Returns all games the player has joined.

### Get My Statistics

```http
GET /api/v1/bingo/me/stats
Headers: X-User-Id: 123
```

Response:
```json
{
  "user_id": 123,
  "games_played": 45,
  "games_won": 12,
  "win_rate": 26.67,
  "total_entry_fees": 2250.0,
  "total_winnings": 3600.0,
  "net_profit": 1350.0,
  "first_place_wins": 5,
  "second_place_wins": 4,
  "third_place_wins": 3,
  "recent_game_count": 10
}
```

---

## ADMIN APIS

Base URL: `/api/admin/bingo`

### Create Game

```http
POST /api/admin/bingo/games
Headers: X-Admin-Id: 1
Content-Type: application/json

{
  "entry_fee": 50.0,
  "max_players": 100,
  "min_players": 2,
  "prize_distribution": {
    "first": 60,
    "second": 30,
    "third": 10
  }
}
```

Response: Game object

### List All Games

```http
GET /api/admin/bingo/games?skip=0&limit=100
Headers: X-Admin-Id: 1
```

### Get Game Details

```http
GET /api/admin/bingo/games/{game_id}
Headers: X-Admin-Id: 1
```

### Start Game

```http
POST /api/admin/bingo/games/{game_id}/start
Headers: X-Admin-Id: 1
```

Requirements:
- Game must be in WAITING status
- Must have minimum number of players

Response:
```json
{
  "message": "Game started",
  "game_id": 1,
  "status": "PLAYING"
}
```

### Call Next Number

```http
POST /api/admin/bingo/games/{game_id}/call-number
Headers: X-Admin-Id: 1
```

Actions:
1. Calls next random number (1-75, no duplicates)
2. Updates Redis state
3. Publishes WebSocket event
4. Checks all players for winners
5. Pays prizes to any new winners

Response:
```json
{
  "message": "Number called successfully",
  "winners": [
    {
      "user_id": 123,
      "winning_position": 1,
      "win_pattern": "ROW",
      "prize_amount": 300.0
    }
  ]
}
```

### Pause Game

```http
POST /api/admin/bingo/games/{game_id}/pause
Headers: X-Admin-Id: 1
```

### Resume Game

```http
POST /api/admin/bingo/games/{game_id}/resume
Headers: X-Admin-Id: 1
```

### Finish Game

```http
POST /api/admin/bingo/games/{game_id}/finish
Headers: X-Admin-Id: 1
```

### Get Players

```http
GET /api/admin/bingo/games/{game_id}/players
Headers: X-Admin-Id: 1
```

Returns list of all players in the game.

### Cancel Game

```http
POST /api/admin/bingo/games/{game_id}/cancel
Headers: X-Admin-Id: 1
```

Actions:
1. Refunds all players' entry fees
2. Records wallet transactions
3. Marks game as CANCELLED
4. Logs audit events

Response:
```json
{
  "message": "Game cancelled and players refunded",
  "game_id": 1,
  "players_refunded": 10
}
```

---

## WEBSOCKET API

### Connect

```
ws://localhost:8000/ws/bingo/{game_id}?user_id=123
```

### Events Received

#### GAME_STATE (on connect)

```json
{
  "event": "GAME_STATE",
  "game_id": 1,
  "status": "PLAYING",
  "current_number": 34,
  "numbers_called_count": 6,
  "player_count": 10,
  "prize_pool": 500.0
}
```

#### NUMBER_CALLED

```json
{
  "event": "NUMBER_CALLED",
  "game_id": 1,
  "number": 42,
  "column_letter": "N",
  "sequence": 7,
  "timestamp": "2026-08-13T10:06:00Z"
}
```

#### PLAYER_JOINED

```json
{
  "event": "PLAYER_JOINED",
  "game_id": 1,
  "user_id": 456,
  "player_count": 11,
  "timestamp": "2026-08-13T10:06:30Z"
}
```

#### WINNER_DECLARED

```json
{
  "event": "WINNER_DECLARED",
  "game_id": 1,
  "user_id": 123,
  "winning_position": 1,
  "win_pattern": "ROW",
  "prize_amount": 300.0,
  "timestamp": "2026-08-13T10:07:00Z"
}
```

#### GAME_FINISHED

```json
{
  "event": "GAME_FINISHED",
  "game_id": 1,
  "winner_count": 3,
  "winners": [
    {"user_id": 123, "position": 1, "prize": 300.0},
    {"user_id": 456, "position": 2, "prize": 150.0},
    {"user_id": 789, "position": 3, "prize": 50.0}
  ],
  "timestamp": "2026-08-13T10:08:00Z"
}
```

### Messages Sent (Client → Server)

#### PING (heartbeat)

```json
{
  "type": "PING",
  "timestamp": "2026-08-13T10:06:00Z"
}
```

Response:
```json
{
  "type": "PONG",
  "timestamp": "2026-08-13T10:06:00Z"
}
```

---

## DATA MODELS

### Cartela Structure

Standard 75-ball Bingo:

```
Column Ranges:
- B: 1-15
- I: 16-30
- N: 31-45 (center is FREE = 0)
- G: 46-60
- O: 61-75

Example:
 B   I   N   G   O
 5  19  34  47  68
12  22  39  53  71
 3  28  FREE 59  64
14  17  41  48  73
 8  30  36  55  62
```

### Win Patterns

- `ROW` - Any complete horizontal line
- `COLUMN` - Any complete vertical line
- `DIAGONAL` - Either diagonal
- `FULL_CARD` - Blackout (all numbers)

### Player Status

- `JOINED` - Player has joined
- `ACTIVE` - Player is actively playing
- `DISCONNECTED` - Player disconnected
- `LEFT` - Player left game
- `WINNER` - Player won

---

## EXAMPLES

### Complete Game Flow

```bash
# 1. Admin creates game
curl -X POST http://localhost:8000/api/admin/bingo/games \
  -H "X-Admin-Id: 1" \
  -H "Content-Type: application/json" \
  -d '{"entry_fee": 50.0, "max_players": 100, "min_players": 2}'

# Response: {"id": 1, "game_number": "BG...", ...}

# 2. Player joins game
curl -X POST http://localhost:8000/api/v1/bingo/games/1/join \
  -H "X-User-Id: 123"

# Response: {"id": 1, "game_id": 1, "cartela_id": 1, ...}

# 3. Get player's cartela
curl http://localhost:8000/api/v1/bingo/games/1/cartela \
  -H "X-User-Id: 123"

# 4. Admin starts game
curl -X POST http://localhost:8000/api/admin/bingo/games/1/start \
  -H "X-Admin-Id: 1"

# 5. Admin calls numbers
curl -X POST http://localhost:8000/api/admin/bingo/games/1/call-number \
  -H "X-Admin-Id: 1"

# Repeat step 5 until winners detected

# 6. Get player stats
curl http://localhost:8000/api/v1/bingo/me/stats \
  -H "X-User-Id: 123"
```

### WebSocket Client (JavaScript)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/bingo/1?user_id=123');

ws.onopen = () => {
  console.log('Connected to game');
  
  // Send heartbeat every 30s
  setInterval(() => {
    ws.send(JSON.stringify({
      type: 'PING',
      timestamp: new Date().toISOString()
    }));
  }, 30000);
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.event) {
    case 'GAME_STATE':
      console.log('Current state:', data);
      break;
    case 'NUMBER_CALLED':
      console.log('Number called:', data.number, data.column_letter);
      // Update UI to mark number on cartela
      break;
    case 'WINNER_DECLARED':
      console.log('Winner:', data.user_id, data.win_pattern);
      break;
    case 'GAME_FINISHED':
      console.log('Game finished. Winners:', data.winners);
      break;
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected. Attempting reconnect...');
  // Implement reconnection logic
};
```

---

## SECURITY

### Server-Authoritative

- Numbers called server-side only
- Winners validated server-side only
- Client cannot manipulate game state
- All financial operations use row locking
- Wallet transactions logged in ledger
- Audit log for all critical actions

### Protections

- Entry fee deduction is atomic (lock → verify → deduct → assign)
- Prize payment is atomic (lock → credit → record → commit)
- Unique constraints prevent duplicate joins
- Check constraints ensure data integrity
- Redis state expires after 24 hours

---

## CONFIGURATION

Environment variables:

```env
BINGO_MIN_PLAYERS=2
BINGO_MAX_PLAYERS=100
BINGO_NUMBER_INTERVAL_SECONDS=5
BINGO_AUTO_START=false
BINGO_ALLOW_RECONNECT=true
BINGO_FIRST_PRIZE_PERCENTAGE=60
BINGO_SECOND_PRIZE_PERCENTAGE=30
BINGO_THIRD_PRIZE_PERCENTAGE=10
BINGO_MIN_ENTRY_FEE=10.0
BINGO_MAX_ENTRY_FEE=1000.0
```

---

## TROUBLESHOOTING

### Tables don't exist

Run migration:
```bash
alembic upgrade head
```

### WebSocket not connecting

Check:
1. Redis is running
2. Game exists
3. User ID is valid
4. No firewall blocking WebSocket

### Winner not detected

System validates automatically when number is called. Check:
1. Cartela numbers vs called numbers
2. FREE cell (center) is always marked
3. Win patterns: row, column, diagonal, full card

---

## NEXT STEPS

1. Run `alembic upgrade head` to create tables
2. Create admin user with `is_admin=true`
3. Test game flow with Postman/curl
4. Implement proper Telegram authentication
5. Add automated number calling (scheduler)
6. Deploy to production

---

Last Updated: 2026-08-13
