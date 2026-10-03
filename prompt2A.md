# AMHABINGO — PHASE 2A
# BINGO GAME BACKEND + REAL-TIME GAME ENGINE

You are a Senior Python Backend Engineer, Real-Time Systems Engineer,
and Telegram Bingo Game Architect.

=========================================================
IMPORTANT — EXISTING PROJECT
=========================================================

The existing AMHABINGO backend has already been implemented from
PHASE 1.

DO NOT rebuild PHASE 1.

DO NOT create a new project.

DO NOT create duplicate files, models, repositories, services,
database configurations, Redis configurations, authentication,
wallet systems, admin systems, or utilities that already exist.

WORK INSIDE THE EXISTING AMHABINGO BACKEND PROJECT.

Before writing any code:

1. Inspect the entire existing project.
2. Identify existing models.
3. Identify existing repositories.
4. Identify existing services.
5. Identify existing wallet/ledger implementation.
6. Identify existing AuditLog implementation.
7. Identify existing authentication.
8. Identify existing PostgreSQL configuration.
9. Identify existing Redis configuration.
10. Identify existing FastAPI application.
11. Identify existing admin APIs.
12. Identify existing migrations.
13. Identify existing logging and middleware.
14. Identify existing tests.

Then create a report:

EXISTING:
- Already implemented components

MISSING:
- Components required for Phase 2A

Then implement ONLY the missing Bingo functionality.

If an existing component can be reused, EXTEND/REUSE IT.

Never create a second implementation of the same functionality.

=========================================================
PHASE 1 ALREADY IMPLEMENTED
=========================================================

The existing system already includes:

- Telegram Bot
- python-telegram-bot
- FastAPI
- PostgreSQL
- SQLAlchemy Async
- Alembic
- Redis
- Pydantic
- AsyncIO
- User registration
- Telegram authentication
- Persistent Telegram keyboard
- Deposit system
- Telebirr SMS verification
- Auto-approved deposits
- Withdrawal system
- Transfer system
- Wallet balances
- WalletTransaction ledger
- AuditLog
- Admin authentication
- Admin APIs
- Financial transaction safety
- SELECT FOR UPDATE
- Idempotency protection
- Rate limiting
- Logging
- Docker configuration
- Production configuration
- Automated tests

These are EXISTING systems.

DO NOT recreate them.

=========================================================
PHASE 2A OBJECTIVE
=========================================================

Build the COMPLETE AMHABINGO BINGO GAME BACKEND.

Phase 2A must implement:

1. Bingo Game Engine
2. Cartela Generator
3. Game Rooms
4. Player Management
5. Entry Fee Integration
6. Game Lifecycle
7. Number Calling System
8. Redis Real-Time State
9. Redis Pub/Sub
10. FastAPI WebSockets
11. Winner Validator
12. Prize System
13. Prize Distribution
14. Game Refund System
15. Game History
16. Player Statistics
17. Anti-Cheat Protection
18. Real-Time Reconnection
19. Game Admin APIs
20. Game REST APIs
21. Database Persistence
22. Concurrency Protection
23. Idempotency
24. Audit Logging
25. Automated Tests

=========================================================
TECH STACK
=========================================================

Use the EXISTING:

- Python 3.13
- FastAPI
- PostgreSQL
- SQLAlchemy 2 Async
- Alembic
- Redis
- Pydantic v2
- AsyncIO
- WebSockets
- Docker

Do not replace the existing stack.

=========================================================
ARCHITECTURE
=========================================================

Follow the existing Clean Architecture and Repository Pattern.

If the existing project has a different but valid structure,
follow the existing architecture instead of restructuring the
entire application.

Add Bingo-specific modules only where appropriate.

Possible structure:

backend/
    bingo/
        models/
        schemas/
        repositories/
        services/
        engine/
        cartela/
        rooms/
        websocket/
        validators/
        prizes/
        utils/

IMPORTANT:

Do not create these directories if equivalent existing directories
already exist.

For example, if the project already has:

backend/services/

then do not create another duplicate:

backend/bingo_services/

unless there is a strong architectural reason.

Reuse existing infrastructure.

=========================================================
BINGO RULES
=========================================================

Standard 75-ball Bingo.

Numbers:

1–75

Columns:

B = 1–15
I = 16–30
N = 31–45
G = 46–60
O = 61–75

Cartela:

5 x 5

Center:

FREE

The FREE position is automatically considered marked.

=========================================================
CARTELA GENERATOR
=========================================================

Implement a production-ready cartela generator.

Requirements:

- Valid 5x5 cartela
- Correct B/I/N/G/O ranges
- FREE center
- Unique cartela ID
- Secure random generation
- Server-side validation
- Prevent duplicate cartela assignment within a game
- Persist assigned cartelas
- Never allow frontend to generate authoritative cartelas

Example:

 B   I   N   G   O

 5  19  34  47  68
12  22  39  53  71
 3  28 FREE 59  64
14  17  41  48  73
 8  30  36  55  62

=========================================================
DATABASE MODELS
=========================================================

Inspect existing models first.

Add only the required Bingo models.

At minimum:

BingoGame

- id
- game_number
- status
- entry_fee
- prize_pool
- max_players
- min_players
- started_at
- finished_at
- created_at
- updated_at

Statuses:

WAITING
STARTING
PLAYING
PAUSED
FINISHED
CANCELLED

=========================================================

GamePlayer

- id
- game_id
- user_id
- cartela_id
- entry_fee
- status
- marked_numbers
- is_winner
- winning_position
- prize_amount
- joined_at

Unique constraint:

game_id + user_id

A user cannot join the same game twice.

=========================================================

Cartela

- id
- game_id
- user_id
- numbers
- created_at

Ensure cartelas are unique within a game.

=========================================================

CalledNumber

Persist game number-call history.

Suggested fields:

- id
- game_id
- number
- sequence
- called_at

Unique:

game_id + number

=========================================================

GameEvent

Persist important game events where appropriate.

Examples:

GAME_CREATED
PLAYER_JOINED
PLAYER_LEFT
GAME_STARTED
NUMBER_CALLED
WINNER_DECLARED
GAME_FINISHED
GAME_CANCELLED

=========================================================
DO NOT DUPLICATE WALLET TABLES
=========================================================

The existing project already has wallet and ledger functionality.

DO NOT create:

- Another Wallet model
- Another WalletTransaction model
- Another AuditLog model
- Another User model

Reuse the existing implementation.

Game financial operations must use the existing wallet service.

=========================================================
GAME ROOM SYSTEM
=========================================================

Implement:

- Create game
- List available games
- Get game details
- Join game
- Leave game
- Player count
- Maximum player limit
- Minimum player requirement
- Room status
- Prevent joining after game starts
- Prevent duplicate joining

=========================================================
ENTRY FEE
=========================================================

When a user joins a paid game:

1. Authenticate user.
2. Verify user exists.
3. Verify registered user.
4. Lock wallet/user balance using existing SELECT FOR UPDATE mechanism.
5. Verify sufficient balance.
6. Deduct entry fee.
7. Create existing WalletTransaction ledger entry.
8. Update prize pool.
9. Create GamePlayer.
10. Create AuditLog.
11. Commit atomically.

If any step fails:

ROLL BACK EVERYTHING.

Never allow:

wallet deducted + player not created

or:

player created + wallet not deducted.

=========================================================
GAME STATE MACHINE
=========================================================

Implement:

WAITING
    ↓
STARTING
    ↓
PLAYING
    ↓
FINISHED

Alternative:

WAITING
    ↓
CANCELLED

Invalid state transitions must be rejected.

Example:

FINISHED → PLAYING

must fail.

=========================================================
GAME START
=========================================================

Before starting:

- Verify minimum players.
- Verify game is WAITING.
- Verify players.
- Verify cartelas.
- Initialize number pool.
- Initialize Redis state.
- Initialize event sequence.
- Set status PLAYING.

Broadcast:

GAME_STARTED

=========================================================
NUMBER CALLER
=========================================================

Implement server-authoritative number caller.

Numbers:

1–75

Every number may only be called once.

Use secure random selection.

Maintain:

available_numbers
called_numbers
current_number
sequence

Configurable interval:

BINGO_NUMBER_INTERVAL_SECONDS

Support:

- Start
- Pause
- Resume
- Stop
- Finish

When a number is called:

1. Persist event/history.
2. Update Redis.
3. Publish Redis event.
4. Broadcast WebSocket event.

=========================================================
REDIS REAL-TIME STATE
=========================================================

Use existing Redis.

Do NOT create another Redis connection system if one already exists.

Use Redis for active game state.

Example:

bingo:game:{game_id}

Store:

- status
- current_number
- called_numbers
- player_count
- event_sequence
- last_event
- game_version

PostgreSQL remains the permanent source of truth.

=========================================================
REDIS PUB/SUB
=========================================================

Use Redis Pub/Sub for real-time game events.

Channel:

bingo:game:{game_id}:events

Events:

PLAYER_JOINED
PLAYER_LEFT
GAME_STARTING
GAME_STARTED
NUMBER_CALLED
GAME_PAUSED
GAME_RESUMED
WINNER_DECLARED
GAME_FINISHED
GAME_CANCELLED

=========================================================
WEBSOCKETS
=========================================================

Implement:

WS /ws/bingo/{game_id}

Requirements:

- Authentication
- Authorization
- Player identification
- Connection management
- Disconnection handling
- Reconnection
- Heartbeat
- Ping/pong
- Event broadcasting
- Error handling
- Connection cleanup

The WebSocket must NEVER trust the client for:

- Winner result
- Number result
- Prize
- Wallet balance
- Game result

=========================================================
WEBSOCKET EVENTS
=========================================================

Use Pydantic schemas.

Example:

{
    "event": "NUMBER_CALLED",
    "game_id": "123",
    "number": 42,
    "column": "N",
    "sequence": 17,
    "timestamp": "..."
}

Support:

GAME_STATE
PLAYER_JOINED
PLAYER_LEFT
PLAYER_COUNT_UPDATED
GAME_STARTED
NUMBER_CALLED
WINNER_DECLARED
GAME_FINISHED
ERROR

=========================================================
RECONNECTION
=========================================================

When a player reconnects:

1. Authenticate.
2. Verify player belongs to game.
3. Retrieve current game state.
4. Retrieve called-number history.
5. Retrieve player's cartela.
6. Send synchronized GAME_STATE.
7. Continue gameplay.

Never restart the game because a player disconnected.

=========================================================
WINNER VALIDATION
=========================================================

Implement SERVER-SIDE winner validation.

The frontend cannot declare itself winner.

Calculate winner using:

Cartela
+
Called Numbers
+
FREE cell

Support:

1. Row
2. Column
3. Diagonal
4. Full Card

Design the validator so additional patterns can be added later.

=========================================================
PLAYER MARKING
=========================================================

The server is authoritative.

Client marking is only UI state.

Do not trust:

client_marked_numbers

The backend calculates valid marks:

cartela numbers ∩ called numbers

plus FREE.

=========================================================
WINNER PROCESSING
=========================================================

When a possible winner is detected:

1. Lock game state.
2. Recalculate winner.
3. Verify player.
4. Prevent duplicate winner processing.
5. Calculate prize.
6. Credit prize through EXISTING wallet service.
7. Create WalletTransaction.
8. Create AuditLog.
9. Mark player winner.
10. Broadcast WINNER_DECLARED.
11. Finish game if configured.
12. Commit atomically.

The same winner must never receive the prize twice.

=========================================================
PRIZE SYSTEM
=========================================================

Implement configurable prize distribution.

Example:

Prize Pool = 1000 ETB

1st = 60%
2nd = 30%
3rd = 10%

Configuration must not be hardcoded.

Support:

- Prize percentage
- Platform commission
- Multiple winners
- Prize rounding rules

Ensure total distribution is mathematically valid.

=========================================================
PRIZE PAYMENT
=========================================================

Use existing wallet infrastructure.

Never directly modify balance without ledger entry.

Use:

SELECT FOR UPDATE
+
Database transaction
+
WalletTransaction
+
AuditLog

Example:

GAME_PRIZE +600 ETB

=========================================================
GAME REFUND
=========================================================

If game is cancelled:

- Refund every eligible player.
- Use existing wallet service.
- Create WalletTransaction for each refund.
- Create AuditLog.
- Mark game CANCELLED.
- Prevent duplicate refunds.
- Notify clients.

Refund operation must be idempotent.

=========================================================
GAME HISTORY
=========================================================

Persist:

- Game
- Players
- Cartelas
- Called numbers
- Winners
- Prize amounts
- Entry fees
- Start time
- End time
- Status

=========================================================
PLAYER STATISTICS
=========================================================

Provide backend support for:

- Games played
- Games won
- Win rate
- Total entry fees
- Total winnings

Use database/ledger data.

=========================================================
REST API
=========================================================

Create player APIs:

GET /api/v1/bingo/games

GET /api/v1/bingo/games/{game_id}

POST /api/v1/bingo/games/{game_id}/join

POST /api/v1/bingo/games/{game_id}/leave

GET /api/v1/bingo/games/{game_id}/state

GET /api/v1/bingo/games/{game_id}/cartela

GET /api/v1/bingo/me/games

GET /api/v1/bingo/me/current-game

GET /api/v1/bingo/me/stats

Do not expose internal admin functionality through these endpoints.

=========================================================
ADMIN GAME APIs
=========================================================

Extend the EXISTING admin API.

Do not create another admin authentication system.

Add:

GET /admin/games

GET /admin/games/{game_id}

POST /admin/games

POST /admin/games/{game_id}/start

POST /admin/games/{game_id}/pause

POST /admin/games/{game_id}/resume

POST /admin/games/{game_id}/cancel

GET /admin/games/{game_id}/players

GET /admin/games/{game_id}/events

GET /admin/games/{game_id}/winners

All admin actions require the existing admin authentication.

=========================================================
ANTI-CHEAT
=========================================================

Prevent:

- Fake winner claims
- Fake number claims
- Duplicate joining
- Multiple participation
- Joining after game start
- Unauthorized game access
- Replay attacks
- Prize duplication
- Refund duplication
- Manipulated WebSocket messages
- Client-generated cartelas
- Client-controlled prize amounts

Server is always authoritative.

=========================================================
CONCURRENCY
=========================================================

This system handles real money.

Use existing:

SELECT FOR UPDATE
transactions
idempotency
unique constraints
ledger

Protect:

- Entry fee
- Prize payment
- Refund
- Winner declaration
- Game joining
- Game state transitions

Test concurrent requests.

Example:

Two simultaneous join requests must NOT both spend the same balance.

=========================================================
RATE LIMITING
=========================================================

Reuse existing Redis rate limiting.

Add Bingo-specific limits where required:

- Join game
- Leave game
- Game state requests
- WebSocket connections
- WebSocket messages
- Winner claim attempts

=========================================================
DATABASE INTEGRITY
=========================================================

Add:

- Foreign keys
- Unique constraints
- Indexes
- Check constraints
- Proper cascading behavior

Important uniqueness:

game_number

game_id + user_id

game_id + number

game_id + cartela_id

=========================================================
AUDIT LOGGING
=========================================================

Reuse existing AuditLog.

Record:

GAME_CREATED
GAME_STARTED
GAME_PAUSED
GAME_RESUMED
GAME_CANCELLED
PLAYER_JOINED
PLAYER_LEFT
ENTRY_FEE_CHARGED
NUMBER_CALLED
WINNER_DECLARED
PRIZE_PAID
GAME_REFUNDED

Include relevant:

user_id
game_id
action
timestamp
metadata

=========================================================
LOGGING
=========================================================

Use existing production logging.

Log:

- Game creation
- Player joins
- Player leaves
- Game start
- Game pause
- Game resume
- Number calls
- Winner detection
- Prize payment
- Refund
- WebSocket connections
- WebSocket disconnections
- Exceptions
- Database errors
- Redis errors

Never log secrets.

=========================================================
TESTING
=========================================================

Add comprehensive tests ONLY for the new Bingo functionality.

Do not duplicate existing Phase 1 tests.

Test:

CARTELA

- Correct dimensions
- Correct ranges
- FREE center
- Valid uniqueness

GAME

- Create
- Join
- Duplicate join
- Full room
- Start
- Pause
- Resume
- Cancel
- Finish

NUMBER CALLER

- 1–75
- No duplicate numbers
- Sequence
- Stop after all numbers

WINNER

- Row
- Column
- Diagonal
- Full card
- Invalid winner
- Duplicate winner

WALLET

- Entry fee
- Insufficient balance
- Prize
- Refund
- Concurrent operations
- Rollback

WEBSOCKET

- Authentication
- Connect
- State
- Number event
- Winner event
- Disconnect
- Reconnect
- Unauthorized access

CONCURRENCY

Simulate multiple simultaneous users and financial operations.

=========================================================
ALEMBIC
=========================================================

Create only the migrations required for Phase 2A.

Do not recreate Phase 1 tables.

Do not delete existing production data.

=========================================================
ENVIRONMENT VARIABLES
=========================================================

Reuse existing configuration system.

Add only missing Bingo variables.

Example:

BINGO_MIN_PLAYERS=2

BINGO_MAX_PLAYERS=100

BINGO_NUMBER_INTERVAL_SECONDS=5

BINGO_AUTO_START=false

BINGO_ALLOW_RECONNECT=true

BINGO_FIRST_PRIZE_PERCENTAGE=60

BINGO_SECOND_PRIZE_PERCENTAGE=30

BINGO_THIRD_PRIZE_PERCENTAGE=10

Do not duplicate existing environment variables.

=========================================================
DOCKER
=========================================================

Reuse existing Docker configuration.

Do not create duplicate PostgreSQL or Redis containers.

Ensure the existing Docker setup can run:

FastAPI
Bingo engine
WebSockets
PostgreSQL
Redis

=========================================================
SECURITY
=========================================================

The backend must:

- Authenticate every player
- Authorize game access
- Validate all inputs
- Prevent SQL injection
- Prevent replay attacks
- Prevent duplicate financial operations
- Prevent race conditions
- Prevent fake winners
- Prevent client manipulation
- Never trust client wallet values
- Never trust client game results

=========================================================
NO FRONTEND
=========================================================

DO NOT build:

- Next.js
- React
- Tailwind
- Telegram Mini App UI
- Admin Dashboard UI

Phase 2A is BACKEND ONLY.

The Next.js Mini App and Admin Dashboard will be Phase 2B.

=========================================================
DEFINITION OF DONE
=========================================================

Phase 2A is complete only when:

[ ] Existing Phase 1 functionality still works.

[ ] Bingo game can be created.

[ ] Players can join.

[ ] Entry fee is safely deducted.

[ ] Cartelas are generated.

[ ] Cartelas are assigned uniquely.

[ ] Game can start.

[ ] Number caller works.

[ ] Numbers cannot repeat.

[ ] Redis real-time state works.

[ ] Redis Pub/Sub works.

[ ] WebSocket works.

[ ] Reconnection works.

[ ] Winner validation is server-side.

[ ] Fake winner claims are rejected.

[ ] Prize calculation works.

[ ] Prize payment works.

[ ] Wallet ledger records prize.

[ ] AuditLog records important operations.

[ ] Game cancellation works.

[ ] Refund works.

[ ] Refund cannot happen twice.

[ ] Game history is persisted.

[ ] Player statistics work.

[ ] Admin game APIs work.

[ ] Rate limiting works.

[ ] Concurrent operations are safe.

[ ] Idempotency works.

[ ] Database constraints work.

[ ] Alembic migration works.

[ ] Automated tests pass.

[ ] Docker works.

=========================================================
VERY IMPORTANT FINAL REPORT
=========================================================

After implementation, DO NOT simply say:

"100% complete."

Instead provide an honest report:

PHASE 1 REUSED:
- list existing components reused

PHASE 2A CREATED:
- list new files

PHASE 2A MODIFIED:
- list modified existing files

DATABASE:
- new tables
- new migrations
- new constraints
- new indexes

API:
- new REST endpoints

WEBSOCKET:
- WebSocket endpoints
- event types

REDIS:
- keys
- Pub/Sub channels

TESTS:
- tests added
- tests passed
- tests failed

SECURITY:
- protections implemented

REMAINING:
- anything not implemented

IMPORTANT:

Do not claim production-ready unless the actual code has been inspected,
implemented, migrated, and tested successfully.

=========================================================
PHASE 2B PREPARATION
=========================================================

The backend APIs and WebSockets must be designed so that a future
Next.js Telegram Mini App can consume them without changing the
core Bingo engine.

The future frontend will use:

REST APIs
+
WebSockets

for:

- Game lobby
- Game rooms
- Cartela
- Number calling
- Player status
- Winners
- Game history
- Wallet information

Do not build that frontend now.