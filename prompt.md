AMHABINGO — PHASE 2B
# TELEGRAM MINI APP + ADMIN DASHBOARD
# NEXT.JS FRONTEND

You are a Senior Next.js/React Engineer, Telegram Mini App Engineer,
and Frontend Architecture Engineer.

=========================================================
IMPORTANT — EXISTING BACKEND
=========================================================

AMHABINGO PHASE 1 AND PHASE 2A ARE ALREADY IMPLEMENTED.

PHASE 1 includes:

- Telegram Bot
- User registration
- Telegram authentication
- Main wallet
- Play wallet
- Deposit
- Telebirr SMS verification
- Withdrawals
- Transfers
- WalletTransaction ledger
- AuditLog
- Admin authentication
- Admin APIs
- PostgreSQL
- Redis
- FastAPI
- SQLAlchemy Async
- Alembic
- Rate limiting
- Financial transaction protection

PHASE 2A includes:

- Bingo game engine
- Game rooms
- Cartela generation
- Game lifecycle
- Player management
- Entry fee handling
- Number calling
- Winner validation
- Prize calculation
- Prize distribution
- Refund system
- Redis real-time state
- Redis Pub/Sub
- WebSockets
- Game history
- Player statistics
- Game REST APIs
- Game Admin APIs
- Server-side anti-cheat
- Concurrency protection
- Idempotency
- Automated tests

=========================================================
CRITICAL RULE
=========================================================

DO NOT REBUILD THE BACKEND.

DO NOT create:

- Another FastAPI backend
- Another PostgreSQL database
- Another Redis system
- Another wallet system
- Another Bingo engine
- Another game engine
- Another winner validator
- Another cartela generator
- Another authentication backend
- Another Admin API
- Another financial system

The backend is the source of truth.

Next.js is ONLY the frontend.

Next.js communicates with the existing FastAPI backend.

=========================================================
PHASE 2B OBJECTIVE
=========================================================

Build:

1. Telegram Mini App
2. Admin Dashboard

Using:

- Next.js
- TypeScript
- React
- Tailwind CSS
- Telegram Mini App SDK
- REST API
- WebSocket
- Responsive UI
- Production-ready frontend architecture

=========================================================
FRONTEND STRUCTURE
=========================================================

Create a separate frontend project:

frontend/

Recommended structure:

frontend/
├── app/
│   ├── page.tsx
│   ├── games/
│   ├── game/
│   ├── wallet/
│   ├── history/
│   ├── profile/
│   └── admin/
│
├── components/
│   ├── telegram/
│   ├── bingo/
│   ├── wallet/
│   ├── games/
│   ├── admin/
│   └── ui/
│
├── hooks/
│   ├── useTelegram.ts
│   ├── useAuth.ts
│   ├── useBingoGame.ts
│   ├── useWebSocket.ts
│   └── useWallet.ts
│
├── lib/
│   ├── api/
│   ├── websocket/
│   ├── telegram/
│   └── utils/
│
├── types/
│
├── providers/
│
└── ...

Adapt the structure if a frontend already exists.
Do not duplicate existing files.
=========================================================
TECHNOLOGY
Use:
- Next.js latest stable version
- TypeScript
- React
- Tailwind CSS
- Telegram Mini App SDK
- TanStack Query
- Zod where appropriate
Use strict TypeScript.
Avoid unnecessary dependencies.
=========================================================
TELEGRAM MINI APP
The Mini App must run inside Telegram.
Integrate Telegram WebApp functionality.
Use Telegram WebApp initialization data for authentication.
The frontend must NOT trust:
- Telegram user ID from arbitrary query parameters
- Wallet balance from frontend state
- Game result
- Winner status
- Prize amount
- Cartela validity
- Called numbers
The backend remains authoritative.
=========================================================
TELEGRAM AUTHENTICATION
On Mini App startup:
1. Initialize Telegram WebApp.
2. Retrieve Telegram WebApp initData.
3. Send initData securely to the existing FastAPI authentication endpoint.
4. Backend validates Telegram authentication.
5. Receive authenticated session/token according to the existing backend implementation.
6. Store authentication securely according to the backend/frontend architecture.
7. Load current user.
Do not implement Telegram authentication validation purely in Next.js.
Do not trust initData without backend verification.
=========================================================
MINI APP MAIN NAVIGATION
Create mobile-first navigation.
Main sections:
🏠 Home
🎮 Play
💰 Wallet
📜 History
👤 Profile
Use Telegram-friendly UI.
The application must work correctly on:
- Android Telegram
- iOS Telegram
- Telegram Desktop where supported
=========================================================
HOME SCREEN
Display:
AMHABINGO
Welcome, {user name}
Main Wallet
Play Wallet
Coins
Current/available games
Quick actions:
🎮 Play
💰 Wallet
📜 History
Display connection/loading/error states.
=========================================================
GAME LOBBY
Route:
/games
Display available Bingo rooms.
Each room should show:
- Game number
- Entry fee
- Current players
- Maximum players
- Minimum players
- Prize pool
- Game status
- Start information
Example:
🎯 Beginner Room
Entry:
10 ETB
Players:
23 / 50
Prize Pool:
450 ETB
Status:
WAITING
Button:
JOIN GAME
=========================================================
JOIN GAME
When user selects JOIN:
1. Call existing FastAPI join endpoint.
2. Backend validates balance.
3. Backend deducts entry fee.
4. Backend creates GamePlayer.
5. Backend assigns cartela.
6. Frontend receives game state.
7. Navigate to game screen.
Never deduct balance in Next.js.
Never calculate the final prize in Next.js.
=========================================================
GAME SCREEN
Route:
/game/[gameId]
Build the complete Bingo UI.
Display:
Top:
- Game number
- Game status
- Player count
- Prize pool
Current number:
BIG NUMBER
Example:
  N
  42

Called numbers history.
=========================================================
BINGO CARTELA
Display:
 B   I   N   G   O
 ┌───┬───┬───┬───┬───┐
 │   │   │   │   │   │
 ├───┼───┼───┼───┼───┤
 │   │   │   │   │   │
 ├───┼───┼───┼───┼───┤
 │   │   │ FREE│   │   │
 ├───┼───┼───┼───┼───┤
 │   │   │   │   │   │
 ├───┼───┼───┼───┼───┤
 │   │   │   │   │   │
 └───┴───┴───┴───┴───┘
Features:
- Highlight called numbers
- Highlight FREE
- Smooth visual updates
- Responsive mobile layout
- Clear current number indicator
IMPORTANT:
The frontend may visually mark numbers,
but the backend remains authoritative.
Do not send arbitrary winner results to the backend.
=========================================================
REAL-TIME WEBSOCKET
Connect to:
WS /ws/bingo/{game_id}
Use the existing backend WebSocket protocol.
Handle events:
GAME_STATE
PLAYER_JOINED
PLAYER_LEFT
PLAYER_COUNT_UPDATED
GAME_STARTING
GAME_STARTED
NUMBER_CALLED
GAME_PAUSED
GAME_RESUMED
WINNER_DECLARED
GAME_FINISHED
GAME_CANCELLED
ERROR
=========================================================
WEBSOCKET BEHAVIOR
Implement:
- Automatic connection
- Reconnection
- Exponential backoff
- Heartbeat/ping handling
- Connection status
- Clean disconnect
- State synchronization
- Duplicate event protection
- Event sequence handling
When reconnecting:
1. Reconnect.
2. Request/retrieve current state.
3. Restore cartela.
4. Restore called numbers.
5. Restore current game status.
6. Continue without refreshing the page.
Never assume that the client received every event.
Use the backend's authoritative state and event sequence.
=========================================================
NUMBER CALLING UI
When NUMBER_CALLED arrives:
- Update current number.
- Add number to called-number history.
- Mark matching cartela number.
- Update animation.
- Update B/I/N/G/O indicator.
Do not generate numbers locally.
Do not randomly generate Bingo numbers in Next.js.
=========================================================
WINNER UI
When WINNER_DECLARED arrives:
Display:
🏆 BINGO!
Winner information according to the backend response.
If current user is the winner:
🎉 Congratulations!
Display:
- Prize
- Winning pattern
- Game number
The frontend must never decide that the player won.
=========================================================
GAME FINISHED
Display:
🏆 Game Finished
Winner(s)
Prize
Final called numbers
Game information
Buttons:
View History
Back to Games
=========================================================
WALLET SCREEN
Route:
/wallet
Display:
Main Wallet
Play Wallet
Coin
Transactions
Deposit
Withdraw
Transfer
IMPORTANT:
Reuse existing backend wallet APIs.
Do not implement financial calculations locally.
=========================================================
DEPOSIT UI
The Telegram Bot already implements the deposit system.
The Mini App should use existing backend APIs if available.
Display:
Deposit Amount
Telebirr number
Deposit instructions
Deposit status
If backend supports SMS submission through API:
Provide SMS input.
Otherwise:
Direct user to the existing Telegram Bot deposit flow.
Do not implement a second deposit verification system.
Do not duplicate Telebirr SMS parsing in Next.js.
=========================================================
WITHDRAW UI
Display:
Telebirr Number
Amount
Available Balance
Submit Withdrawal
Backend validates:
- Amount
- Balance
- Limits
- Authentication
- Request status
Frontend only displays backend responses.
=========================================================
TRANSFER UI
Display:
Recipient
Amount
Submit Transfer
Backend handles:
- Recipient validation
- Balance validation
- Transaction creation
- Approval logic
- Ledger
- AuditLog
Do not move money from frontend.
=========================================================
TRANSACTION HISTORY
Route:
/history
Display:
- Deposits
- Withdrawals
- Transfers
- Game entry fees
- Game prizes
- Refunds
Each transaction:
- Type
- Amount
- Status
- Date
- Reference
- Description
Use pagination.
=========================================================
PROFILE
Route:
/profile
Display:
- Name
- Username
- Phone
- Telegram information where appropriate
- Registration information
- Games played
- Games won
- Win rate
- Total winnings
Do not expose sensitive backend information.
=========================================================
GAME HISTORY
Display:
- Game number
- Date
- Entry fee
- Result
- Prize
- Winning pattern
Use backend data.
=========================================================
PLAYER STATISTICS
Display:
Games Played
Games Won
Win Rate
Total Entry Fees
Total Winnings
Use existing backend statistics API.
=========================================================
LOADING STATES
Every API request must have proper:
- Loading
- Success
- Error
- Empty
- Retry
states.
Never leave the UI frozen.
=========================================================
ERROR HANDLING
Handle:
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Validation Error
429 Rate Limited
500 Server Error
WebSocket disconnect
Network failure
Game already started
Game cancelled
Insufficient balance
Duplicate join
Invalid game
Display user-friendly messages.
Do not expose stack traces.
=========================================================
ADMIN DASHBOARD
Build a separate admin interface inside the same Next.js project.
Route:
/admin
IMPORTANT:
The Admin Dashboard must use the EXISTING backend Admin APIs.
Do not implement admin authentication only in the frontend.
Backend remains responsible for authorization.
=========================================================
ADMIN LOGIN
Use the existing backend admin authentication mechanism.
Do not create a second admin authentication system.
Protect all /admin routes.
Unauthorized users must not access admin pages.
=========================================================
ADMIN DASHBOARD HOME
Display:
Total Users
Active Games
Completed Games
Pending Withdrawals
Total Deposits
Total Withdrawals
Total Transfers
Total Prize Distributed
Platform Revenue/Commission if available
Pending Requests
Use existing backend statistics APIs.
=========================================================
ADMIN USERS
Route:
/admin/users
Features:
- List users
- Search
- Pagination
- User details
- Wallet balances
- Coins
- Wins
- Registration date
- Game statistics
Do not expose unnecessary sensitive information.
=========================================================
ADMIN GAMES
Route:
/admin/games
Display:
- Game number
- Status
- Players
- Entry fee
- Prize pool
- Created time
- Start time
- Finish time
Actions:
Create Game
Start
Pause
Resume
Cancel
View
=========================================================
ADMIN GAME DETAILS
Route:
/admin/games/[gameId]
Display:
- Game information
- Players
- Cartelas where authorized
- Called numbers
- Events
- Winners
- Prize distribution
- Entry fees
- Refunds
Provide real-time updates where appropriate.
=========================================================
ADMIN GAME CONTROLS
Buttons:
START GAME
PAUSE GAME
RESUME GAME
CANCEL GAME
These call existing backend APIs.
Frontend must not directly manipulate Redis or PostgreSQL.
=========================================================
ADMIN DEPOSITS
Route:
/admin/deposits
Display:
- User
- Amount
- Reference
- Receiver
- Status
- Date
Use existing APIs.
IMPORTANT:
Deposits are auto-approved according to Phase 1.
Do not create an unnecessary manual deposit approval workflow.
If the backend exposes historical/manual review functionality,
display it accurately.
=========================================================
ADMIN WITHDRAWALS
Route:
/admin/withdrawals
Display:
- User
- Telebirr number
- Amount
- Status
- Date
Actions:
Approve
Reject
Use existing backend APIs.
=========================================================
ADMIN TRANSFERS
Route:
/admin/transfers
Display:
- Sender
- Receiver
- Amount
- Status
- Date
Actions must match the actual backend behavior.
Do not assume approval is required if the existing backend
implements instant transfer execution.
Read the backend API behavior first.
=========================================================
ADMIN AUDIT LOG
Route:
/admin/audit-logs
Display:
- Action
- User
- Admin
- Entity
- Entity ID
- Timestamp
- Metadata where appropriate
Support:
- Search
- Filtering
- Pagination
=========================================================
ADMIN TRANSACTIONS
Route:
/admin/transactions
Display ledger records:
- User
- Transaction type
- Amount
- Direction
- Reference
- Status
- Date
Use existing WalletTransaction API.
Do not create another ledger.
=========================================================
ADMIN REPORTS
Create report UI for:
- Users
- Deposits
- Withdrawals
- Transfers
- Games
- Winners
- Wallet transactions
- Audit logs
If backend provides export endpoints:
Use them.
Do not generate authoritative financial reports solely from
frontend calculations.
=========================================================
SEARCH AND FILTERING
Admin pages should support:
Search
Pagination
Status filters
Date filters
User filters
Game filters
Transaction type filters
Use server-side filtering whenever the backend supports it.
=========================================================
RESPONSIVE DESIGN
Mini App:
Mobile-first.
Admin Dashboard:
Desktop-first but responsive.
Must work on:
- Desktop
- Tablet
- Mobile
=========================================================
UI/UX
Create a professional Bingo interface.
Use:
- Clear typography
- Large touch targets
- Smooth transitions
- Accessible buttons
- Loading skeletons
- Toast notifications
- Modal confirmations
- Empty states
- Error states
Avoid unnecessary animations during active gameplay.
Gameplay performance is more important than visual effects.
=========================================================
TELEGRAM THEME
The Mini App should respect Telegram's theme where supported.
Use:
- Telegram theme colors
- Dark mode
- Light mode
- Safe-area support
- Mobile viewport handling
Do not hardcode only one theme.
=========================================================
API CLIENT
Create a centralized typed API client.
Example:
lib/api/client.ts
Features:
- Base URL
- Authentication
- Request handling
- Error normalization
- Type-safe responses
Do not scatter fetch() calls throughout components.
=========================================================
TANSTACK QUERY
Use TanStack Query for:
- Games
- User
- Wallet
- History
- Statistics
- Admin data
Configure:
- Query caching
- Refetching
- Mutation handling
- Error handling
- Invalidation
Do not use unnecessary global state for server data.
=========================================================
WEBSOCKET ARCHITECTURE
Create reusable:
useBingoWebSocket()
or equivalent.
Responsibilities:
- Connect
- Disconnect
- Reconnect
- Parse events
- Validate event shape
- Maintain event sequence
- Notify UI
Do not put WebSocket logic directly into the Bingo page.
=========================================================
TYPE SAFETY
Define TypeScript types matching backend schemas.
Examples:
User
Game
GamePlayer
Cartela
CalledNumber
GameEvent
Winner
Wallet
WalletTransaction
Deposit
Withdrawal
Transfer
AuditLog
Do not use:
any
unless absolutely unavoidable.
=========================================================
SECURITY
Never trust frontend values for:
- User ID
- Wallet balance
- Entry fee
- Prize
- Winner
- Cartela
- Game state
- Called number
Everything important must be verified by FastAPI.
Prevent:
- Unauthorized admin access
- Token leakage
- XSS
- Unsafe HTML rendering
- Sensitive data exposure
- Duplicate mutations
- Replay of stale UI actions
Do not store secrets in NEXT_PUBLIC_* variables.
=========================================================
ENVIRONMENT VARIABLES
Use:
NEXT_PUBLIC_API_URL
NEXT_PUBLIC_WS_URL
Only public configuration may use NEXT_PUBLIC_.
Never expose:
Database credentials
Redis credentials
Telegram bot token
Admin secrets
JWT signing secrets
Private API keys
=========================================================
NEXT.JS SERVER VS CLIENT
Use Server Components where appropriate.
Use Client Components only where required.
Telegram WebApp APIs and WebSockets must run client-side.
Avoid unnecessary client rendering.
=========================================================
PERFORMANCE
Optimize:
- WebSocket rendering
- Bingo cartela updates
- Called number list
- Game state updates
- Admin tables
Do not rerender the entire application for every number call.
=========================================================
OFFLINE / CONNECTION HANDLING
If WebSocket connection is lost:
Display:
⚠️ Connection lost
Reconnecting...
When restored:
Connection restored
Synchronize game state.
Never declare the game finished based only on a disconnected
client.
=========================================================
NO BUSINESS LOGIC DUPLICATION
The backend controls:
- Wallet
- Money
- Bingo numbers
- Game state
- Winners
- Prizes
- Cartelas
- Refunds
- Authentication
- Authorization
The frontend controls:
- UI
- Navigation
- Rendering
- User interaction
- Local presentation state
- WebSocket display
=========================================================
TESTING
Implement frontend tests for:
Authentication
Game lobby
Join game
Wallet display
Cartela rendering
Called number rendering
WebSocket events
WebSocket reconnection
Winner UI
Game completion
Admin authentication
Admin games
Admin users
Admin transactions
Admin approvals
Error handling
Responsive behavior where practical.
=========================================================
END-TO-END TESTING
Test complete flows:
FLOW 1
Telegram user
→ Open Mini App
→ Authenticate
→ View games
→ Join game
→ Receive cartela
→ Connect WebSocket
→ Receive numbers
→ Win
→ Receive prize
→ View updated wallet
FLOW 2
User
→ Open wallet
→ View balance
→ Withdraw
→ Admin sees request
→ Admin approves
→ User sees status
FLOW 3
Admin
→ Login
→ Dashboard
→ View games
→ Create game
→ Start game
→ Monitor players
→ View winner
→ View transactions
=========================================================
BUILD AND DEPLOYMENT
Production build must succeed:
npm run build
No TypeScript errors.
No ESLint errors where configured.
No broken routes.
No missing environment variables.
=========================================================
TELEGRAM MINI APP DEPLOYMENT
Prepare the application for HTTPS deployment.
Telegram Mini Apps require a secure HTTPS URL in production.
The frontend URL will later be configured in the Telegram Bot.
The existing Telegram Bot's 🎮 Play button should open this Mini App.
Do not modify the existing bot unnecessarily.
=========================================================
ADMIN DEPLOYMENT
The Admin Dashboard may use the same Next.js deployment.
Protect /admin routes.
Backend authorization remains mandatory.
=========================================================
IMPORTANT — API CONTRACT
Before implementing each page:
Inspect the actual FastAPI endpoints and schemas.
Do NOT invent API fields.
Do NOT assume endpoint names.
Do NOT assume response formats.
If the backend endpoint already exists, use it.
If an endpoint required by the frontend is missing:
1. Identify it.
2. Document it.
3. Only add a backend endpoint if absolutely necessary.
4. Do not duplicate existing endpoints.
=========================================================
DEFINITION OF DONE
MINI APP:
[ ] Telegram authentication works.
[ ] Home works.
[ ] Game lobby works.
[ ] Game details work.
[ ] Join game works.
[ ] Cartela displays correctly.
[ ] WebSocket connects.
[ ] Reconnection works.
[ ] Real-time numbers display.
[ ] Called numbers update.
[ ] Winner notification works.
[ ] Game completion works.
[ ] Wallet works.
[ ] Transaction history works.
[ ] Game history works.
[ ] Profile works.
[ ] Statistics work.
[ ] Errors are handled.
[ ] Telegram theme works.
[ ] Mobile UI works.
ADMIN:
[ ] Admin authentication works.
[ ] Dashboard works.
[ ] Users page works.
[ ] Games page works.
[ ] Game details work.
[ ] Game controls work.
[ ] Deposits page works.
[ ] Withdrawals page works.
[ ] Transfers page works.
[ ] Transactions page works.
[ ] Audit logs work.
[ ] Reports work.
[ ] Search works.
[ ] Filtering works.
[ ] Pagination works.
[ ] Authorization works.
=========================================================
FINAL VERIFICATION
Run:
npm run lint
npm run build
Run all frontend tests.
Verify API connectivity.
Verify WebSocket connectivity.
Verify Telegram Mini App initialization.
Verify Admin authentication.
=========================================================
FINAL REPORT
After implementation, provide an honest report.
DO NOT simply say:
"100% complete."
Report:
1. Frontend files created
2. Frontend files modified
3. API endpoints consumed
4. WebSocket endpoints consumed
5. New backend endpoints required, if any
6. Mini App features completed
7. Admin Dashboard features completed
8. Tests added
9. Tests passed
10. Build result
11. Known issues
12. Remaining work
IMPORTANT:
Do not claim a feature is complete unless it has actually been
implemented and tested.
=========================================================
PHASE 2B BOUNDARY
This phase builds ONLY:
NEXT.JS
+
TELEGRAM MINI APP
+
ADMIN DASHBOARD
Do NOT implement:
- New Bingo engine
- New wallet engine
- New PostgreSQL database
- New Redis game state
- New Telegram Bot
- New payment gateway
- New Telebirr parser
- New financial ledger
- New winner calculation
- New prize calculation
Those belong to the existing backend.
=========================================================
FINAL ARCHITECTURE
Telegram User
      │
      ▼
Telegram Mini App
      │
      ├──────── REST API ──────────┐
      │                            │
      └──────── WebSocket ─────────┤
                                   ▼
                              FastAPI
                                   │
              ┌────────────────────┼───────────────────┐
              ▼                    ▼                   ▼
         Bingo Engine          PostgreSQL            Redis
              │                    │                   │
              │                    │                   │
              └──────── Existing Wallet/Ledger ───────┘
Admin
  │
  ▼
Next.js Admin Dashboard
  │
  ▼
Existing FastAPI Admin APIs
  │
  ├── PostgreSQL
  ├── Redis
  ├── Bingo Engine
  ├── Wallet/Ledger
  └── AuditLog

### One important point

For your project, **Phase 2B should not be responsible for the payment gateway**. Your current Telebirr flow is based on **SMS verification**, so the Mini App should consume the existing wallet/deposit APIs rather than invent another payment mechanism.

Your final architecture becomes:

**Telegram Bot** → registration, deposit SMS flow, withdrawals/transfers, notifications  
**Next.js Mini App** → actual Bingo gameplay UI  
**Next.js Admin** → management interface  
**FastAPI** → API + game engine + financial/business logic  
**PostgreSQL** → permanent data  
**Redis** → real-time game state/Pub/Sub  
**WebSocket** → live Bingo gameplay

That is the clean separation you want for the production version.