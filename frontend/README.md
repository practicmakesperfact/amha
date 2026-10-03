# 🎮 AMHABINGO - Telegram Mini App Frontend

**Next.js Telegram Mini App for AMHABINGO real-time bingo gaming platform**

---

## 📋 Overview

This is the **Phase 2B** frontend implementation - a Telegram Mini App built with Next.js that provides a beautiful, interactive UI for the AMHABINGO bingo game.

### What's Included:
- ✅ Telegram Mini App integration
- ✅ Real-time bingo gameplay with WebSocket
- ✅ Interactive 5×5 bingo card
- ✅ Wallet management
- ✅ Game history & statistics
- ✅ User profile
- ✅ Responsive mobile-first design
- ✅ Dark/Light theme support

---

## 🛠 Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript (strict mode)
- **Styling:** Tailwind CSS
- **State Management:** TanStack Query (React Query)
- **HTTP Client:** Axios
- **WebSocket:** Native WebSocket API
- **Telegram:** Telegram WebApp SDK
- **Validation:** Zod

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ or 20+
- npm, yarn, or pnpm
- Running AMHABINGO backend (Phase 1 + Phase 2A)

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
# or
yarn install
# or
pnpm install
```

### Configuration

1. Create environment file:
```bash
cp .env.local.example .env.local
```

2. Edit `.env.local` with your backend URLs:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

For production:
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com
```

### Development

```bash
# Run development server
npm run dev

# Open http://localhost:3000 in your browser
```

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm start

# Or export static files
npm run build && npm run export
```

---

### Player Features
- ✅ **Home Page**
  - Wallet overview (4 wallets)
  - Quick actions
  - Available games preview
  - Bottom navigation

- ✅ **Games Lobby**
  - List all available games
  - Filter by status (waiting/playing)
  - Join game with balance validation
  - Auto-refresh every 5 seconds

- ✅ **Game Play Screen** ⭐
  - Interactive 5×5 bingo card
  - Real-time number calling (WebSocket)
  - Current number display (animated)
  - Called numbers history
  - Connection status indicator
  - Winner detection & modal
  - Confetti animation for winners

- ✅ **Wallet Page**
  - View all wallet balances
  - Transaction history (placeholder)
  - Link to Telegram bot for actions

- ✅ **History Page**
  - Game history with win/loss
  - Player statistics
  - Win rate calculation
  - Net profit/loss

- ✅ **Profile Page**
  - User information
  - Game statistics
  - Achievements
  - Logout functionality

### Admin Features ✅
- ✅ **Admin Dashboard** (`/admin`)
  - Platform statistics (8 key metrics)
  - User count, game count, financial summary
  - Quick actions & system status
  - Real-time updates

- ✅ **User Management** (`/admin/users`)
  - List all users with search
  - View wallet balances
  - Registration status
  - Pagination

- ✅ **Game Management** (`/admin/games`)
  - Create new games
  - List all games with status
  - Start/pause/cancel controls
  - Real-time monitoring

- ✅ **Game Details** (`/admin/games/[id]`)
  - Complete game information
  - Player list with winners
  - Game controls
  - Real-time updates

- ✅ **Deposits** (`/admin/deposits`)
  - View deposit history
  - Filter by status
  - Auto-approved via SMS

- ✅ **Withdrawals** (`/admin/withdrawals`)
  - Approve/reject requests
  - View Telebirr numbers
  - Status tracking

- ✅ **Transfers** (`/admin/transfers`)
  - Approve/reject transfers
  - Sender/receiver tracking
  - Status management

- ✅ **Transactions** (`/admin/transactions`)
  - Complete wallet ledger
  - All transaction types
  - Audit trail
  - Before/after balances

---

## 🎨 Design Principles

Following `prompt.md` specifications:
- **Mobile-first** responsive design
- **Telegram theme** integration (auto dark/light mode)
- **Large touch targets** for mobile usability
- **Simple, clean UI** - no distracting animations during gameplay
- **Performance-first** - smooth real-time updates
- **Backend authoritative** - never trust client data

---

## 🏗️ Project Structure

```
frontend/
├── app/                      # Next.js App Router pages
│   ├── page.tsx             # Home page
│   ├── games/               # Games lobby
│   ├── game/[id]/           # Game play screen
│   ├── wallet/              # Wallet page
│   ├── history/             # History page
│   ├── profile/             # Profile page
│   ├── layout.tsx           # Root layout
│   └── globals.css          # Global styles
│
├── components/              # React components
│   ├── ui/                  # Base UI components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   └── Loading.tsx
│   └── bingo/               # Bingo-specific components
│       ├── BingoCard.tsx
│       ├── CurrentNumber.tsx
│       ├── CalledNumbers.tsx
│       ├── GameStatus.tsx
│       ├── ConnectionStatus.tsx
│       └── WinnerModal.tsx
│
├── providers/               # React context providers
│   ├── providers.tsx        # Main provider wrapper
│   ├── telegram-provider.tsx
│   └── auth-provider.tsx
│
├── hooks/                   # Custom React hooks
│   ├── useTelegram.ts
│   └── useBingoWebSocket.ts
│
├── lib/                     # Library code
│   ├── api/                 # API client
│   │   ├── client.ts        # Axios instance
│   │   ├── types.ts         # TypeScript types
│   │   └── endpoints.ts     # API functions
│   ├── websocket/           # WebSocket client
│   │   └── client.ts
│   └── utils/               # Utility functions
│       ├── cn.ts            # Class names
│       └── format.ts        # Formatting
│
├── public/                  # Static files
├── package.json             # Dependencies
├── tsconfig.json            # TypeScript config
├── tailwind.config.ts       # Tailwind config
└── next.config.js           # Next.js config
```

---

## 🔌 API Integration

The frontend consumes the existing FastAPI backend APIs:

### Player Endpoints
- `GET /api/v1/bingo/games` - List games
- `GET /api/v1/bingo/games/{id}` - Game details
- `POST /api/v1/bingo/games/{id}/join` - Join game
- `GET /api/v1/bingo/games/{id}/cartela` - Get cartela
- `GET /api/v1/bingo/me/games` - My games
- `GET /api/v1/bingo/me/stats` - My statistics

### WebSocket
- `WS /ws/bingo/{game_id}` - Real-time game updates

Events:
- `NUMBER_CALLED` - New number called
- `WINNER_DECLARED` - Winner found
- `GAME_FINISHED` - Game ended
- `GAME_STATE` - Full state sync

---

## 🎮 How It Works

### 1. Authentication Flow
```
User opens Mini App
    ↓
Telegram WebApp SDK initializes
    ↓
Get Telegram initData
    ↓
Send to backend for verification
    ↓
Backend validates & returns user data
    ↓
Frontend stores auth token
    ↓
User authenticated ✓
```

### 2. Game Play Flow
```
User joins game
    ↓
Backend deducts entry fee
    ↓
Backend generates cartela
    ↓
Frontend receives cartela
    ↓
Game starts (backend)
    ↓
WebSocket connects
    ↓
Backend calls numbers every 5s
    ↓
Frontend receives NUMBER_CALLED events
    ↓
Frontend marks called numbers on card
    ↓
Backend detects winner
    ↓
Frontend receives WINNER_DECLARED
    ↓
Show winner modal with confetti 🎉
```

### 3. Real-time Updates
```
WebSocket connection established
    ↓
Subscribe to game events
    ↓
Receive events: NUMBER_CALLED, WINNER_DECLARED, etc.
    ↓
Update UI in real-time
    ↓
Handle reconnection automatically
    ↓
Sync state on reconnect
```

---

## 🔐 Security

### What Frontend Does:
- ✅ Display data from backend
- ✅ Send user actions to backend
- ✅ Handle UI state and animations
- ✅ Validate Telegram WebApp init data

### What Frontend Does NOT Do:
- ❌ Calculate winners (backend only)
- ❌ Generate bingo numbers (backend only)
- ❌ Modify wallet balances (backend only)
- ❌ Verify transactions (backend only)
- ❌ Store sensitive data (backend only)

**The backend is ALWAYS the source of truth!**

---

## 🧪 Testing

### Development Mode
The app includes mock data for testing without Telegram:

```typescript
// Runs outside Telegram
if (!window.Telegram?.WebApp) {
  // Use mock user data
  mockUser = {
    id: 123456789,
    first_name: 'Test',
    username: 'testuser',
  }
}
```

### Production Mode
Deploy to HTTPS URL and configure in Telegram BotFather.

---

## 📦 Deployment

### Option 1: Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

### Option 2: Docker
```bash
# Build image
docker build -t amhabingo-frontend .

# Run container
docker run -p 3000:3000 amhabingo-frontend
```

### Option 3: Static Export
```bash
# Build static files
npm run build

# Deploy to any static host (Netlify, Cloudflare Pages, etc.)
```

---

## 🔗 Connect to Telegram Bot

After deployment:

1. Get your Mini App URL (e.g., `https://amhabingo.vercel.app`)
2. Open @BotFather on Telegram
3. Send `/mybots`
4. Select your bot
5. Select **Menu Button** → **Edit Menu Button URL**
6. Enter your Mini App URL
7. Save

Now the 🎮 Play button in your bot opens the Mini App!

---

## 🐛 Troubleshooting

### WebSocket Connection Failed
- Check `NEXT_PUBLIC_WS_URL` is correct
- Ensure backend WebSocket endpoint is running
- Check CORS settings on backend

### Authentication Failed
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check backend is running
- Ensure Telegram WebApp script is loaded

### Numbers Not Updating
- Check WebSocket connection status
- Verify game status is PLAYING
- Check browser console for errors

---

## 📊 Performance

### Optimizations:
- ✅ React Query caching
- ✅ Optimistic updates
- ✅ WebSocket reconnection
- ✅ Lazy loading components
- ✅ Image optimization
- ✅ Code splitting

### Bundle Size:
- First Load JS: ~100KB
- Page sizes: 10-30KB each

---

## 🎯 What's Next?

### Phase 2B Continuation:
1. ⏳ Admin Dashboard
   - Platform statistics
   - User management
   - Game management
   - Financial management
   - Audit logs

2. ⏳ Additional Features
   - Transaction history (detailed)
   - Push notifications
   - Sound effects
   - More animations
   - Leaderboards
   - Tournaments

---

## 🤝 Contributing

This is part of the AMHABINGO project. See main README for contribution guidelines.

---

## 📄 License

Proprietary software. All rights reserved.

---

## 📞 Support

- Telegram: [@amhabingosupport_team](https://t.me/amhabingosupport_team)
- Bot: [@amhabingo_bot](https://t.me/amhabingo_bot)

---

**Built with ❤️ using Next.js + Telegram Mini Apps**

🎮 Play | 💰 Win | 🎉 Enjoy
