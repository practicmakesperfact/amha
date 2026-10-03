# 🎯 AMHABINGO Frontend - Phase 2B Implementation Plan

## 📋 Overview

Building Next.js Telegram Mini App + Admin Dashboard according to `prompt.md` specifications.

---

## ✅ Setup (Complete)

- [x] package.json with dependencies
- [x] TypeScript configuration
- [x] Next.js configuration
- [x] Tailwind CSS setup
- [x] PostCSS configuration
- [x] Environment variables template
- [x] Global styles
- [x] Root layout

---

## 🔄 In Progress: Core Infrastructure

###  1. Providers & Context (Next)
- [ ] `providers/providers.tsx` - Main providers wrapper
- [ ] `providers/telegram-provider.tsx` - Telegram WebApp SDK
- [ ] `providers/query-provider.tsx` - TanStack Query
- [ ] `providers/auth-provider.tsx` - Authentication context

### 2. API Client
- [ ] `lib/api/client.ts` - Centralized API client
- [ ] `lib/api/endpoints.ts` - API endpoint definitions
- [ ] `lib/api/types.ts` - API type definitions

### 3. Telegram Integration
- [ ] `lib/telegram/init.ts` - Telegram WebApp initialization
- [ ] `hooks/useTelegram.ts` - Telegram hook
- [ ] `hooks/useAuth.ts` - Authentication hook

### 4. WebSocket
- [ ] `lib/websocket/client.ts` - WebSocket client
- [ ] `hooks/useBingoWebSocket.ts` - Bingo WebSocket hook

---

## 📱 Telegram Mini App Pages

### Home
- [ ] `app/page.tsx` - Home/landing page
- [ ] Display wallet balances
- [ ] Quick actions
- [ ] Available games preview

### Games
- [ ] `app/games/page.tsx` - Game lobby
- [ ] List available games
- [ ] Join game buttons
- [ ] Game filters

### Game Play
- [ ] `app/game/[id]/page.tsx` - Active game screen
- [ ] `components/bingo/BingoCard.tsx` - Interactive cartela
- [ ] `components/bingo/CurrentNumber.tsx` - Number display
- [ ] `components/bingo/CalledNumbers.tsx` - Number history
- [ ] Real-time WebSocket updates

### Wallet
- [ ] `app/wallet/page.tsx` - Wallet management
- [ ] Display all wallets
- [ ] Transaction history
- [ ] Deposit/withdraw/transfer (link to bot)

### History
- [ ] `app/history/page.tsx` - Game history
- [ ] Past games
- [ ] Win/loss record
- [ ] Prize history

### Profile
- [ ] `app/profile/page.tsx` - User profile
- [ ] User stats
- [ ] Settings
- [ ] Logout

---

## 👨‍💼 Admin Dashboard Pages

### Dashboard
- [ ] `app/admin/page.tsx` - Admin home
- [ ] Platform statistics
- [ ] Quick actions
- [ ] Pending requests

### Users
- [ ] `app/admin/users/page.tsx` - User list
- [ ] Search & filters
- [ ] User details modal

### Games
- [ ] `app/admin/games/page.tsx` - Game management
- [ ] Create game form
- [ ] Game list with actions
- [ ] Game control buttons

### Game Details
- [ ] `app/admin/games/[id]/page.tsx` - Single game view
- [ ] Player list
- [ ] Called numbers
- [ ] Events log
- [ ] Control panel

### Financial
- [ ] `app/admin/deposits/page.tsx` - Deposits list
- [ ] `app/admin/withdrawals/page.tsx` - Withdrawals list
- [ ] `app/admin/transfers/page.tsx` - Transfers list
- [ ] Approve/reject actions

### Reports
- [ ] `app/admin/transactions/page.tsx` - Transaction ledger
- [ ] `app/admin/audit-logs/page.tsx` - Audit trail
- [ ] Export functionality

---

## 🎨 Shared Components

### UI Components
- [ ] `components/ui/Button.tsx`
- [ ] `components/ui/Card.tsx`
- [ ] `components/ui/Input.tsx`
- [ ] `components/ui/Modal.tsx`
- [ ] `components/ui/Loading.tsx`
- [ ] `components/ui/Toast.tsx`

### Layout Components
- [ ] `components/layout/Navigation.tsx`
- [ ] `components/layout/Header.tsx`
- [ ] `components/layout/Footer.tsx`
- [ ] `components/layout/Sidebar.tsx` (admin)

### Bingo Components
- [ ] `components/bingo/BingoCard.tsx`
- [ ] `components/bingo/CurrentNumber.tsx`
- [ ] `components/bingo/CalledNumbers.tsx`
- [ ] `components/bingo/GameStatus.tsx`
- [ ] `components/bingo/WinnerModal.tsx`

### Wallet Components
- [ ] `components/wallet/WalletDisplay.tsx`
- [ ] `components/wallet/TransactionList.tsx`

---

## 🔧 Utilities & Helpers

- [ ] `lib/utils/cn.ts` - Class name merger
- [ ] `lib/utils/format.ts` - Number/date formatting
- [ ] `lib/utils/validation.ts` - Form validation

---

## 🧪 Testing

- [ ] Setup testing framework
- [ ] Component tests
- [ ] API integration tests
- [ ] E2E tests

---

## 📦 Deployment

- [ ] Build configuration
- [ ] Environment variables for production
- [ ] Deployment guide
- [ ] Telegram Bot Menu button configuration

---

## Priority Order

### Phase 1: MVP (Week 1)
1. Core infrastructure (providers, API client, Telegram)
2. Home page
3. Games lobby
4. Basic game screen with cartela
5. WebSocket integration

### Phase 2: Full Features (Week 2)
6. Complete game play experience
7. Wallet page
8. History page
9. Profile page

### Phase 3: Admin (Week 3)
10. Admin authentication
11. Admin dashboard
12. Game management
13. User management
14. Financial management

### Phase 4: Polish (Week 4)
15. UI/UX improvements
16. Loading states
17. Error handling
18. Testing
19. Deployment

---

## Current Status

**Started:** Configuration & setup complete
**Next:** Building core infrastructure (providers, API client, hooks)
**Progress:** 10%

---

## Notes

- Following `prompt.md` specifications exactly
- Backend APIs already exist (Phase 2A complete)
- No backend modifications needed
- Focus on clean, type-safe code
- Mobile-first responsive design
- Telegram theme support
