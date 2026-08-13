# Technical Specifications - AMHABINGO Bot

## 📱 Telebirr SMS Formats

### Supported SMS Formats

The bot supports multiple Telebirr SMS confirmation formats:

#### Format 1: Standard Telebirr Confirmation
```
You have received ETB 100.00 from 0912345678
to 0909425014 on 08/12/2024 14:30:45.
Ref: TXN12345678
```

#### Format 2: Alternative Format
```
Transfer successful!
Amount: ETB 500.00
From: 0923456789
To: 0909425014
Date: 08-12-2024 15:45:30
Reference: TB87654321
```

#### Format 3: Compact Format
```
ETB 250 received from 0934567890 to 0909425014
Ref: REF123456 Date: 08/12/2024 16:20
```

### Required Fields

The SMS parser extracts:
1. **Amount** - Transaction amount in ETB
2. **Sender Phone** - Sender's phone number (10 digits)
3. **Receiver Phone** - Must be `0909425014`
4. **Reference Number** - Unique transaction ID
5. **Transaction Date** - Date and time of transaction

### Validation Rules

1. **Receiver Phone**: Must exactly match `0909425014`
2. **Amount**: Must match user's requested deposit amount (±0.01 ETB tolerance)
3. **Reference**: Must be unique (never used before)
4. **Timestamp**: Transaction must be within 30 minutes
5. **Format**: SMS must be unmodified Telebirr confirmation

---

## 💰 Transaction Limits

### Deposits
- **Minimum**: 10.00 ETB
- **Maximum**: Unlimited
- **Approval**: Auto-approved after SMS verification

### Withdrawals
- **Minimum**: 50.00 ETB
- **Maximum**: 50,000.00 ETB
- **Approval**: Requires admin approval

### Transfers
- **Minimum**: 10.00 ETB
- **Maximum**: 50,000.00 ETB
- **Approval**: **Instant** - No admin approval required

---

## 🔐 Admin Authentication & Roles

### Authentication Method
- **Header-based**: `X-Admin-Id: TELEGRAM_USER_ID`
- **Configuration**: `ADMIN_TELEGRAM_IDS` in `.env`
- **Format**: List of Telegram user IDs `[123456789,987654321]`

### Admin Permissions
All admins have full access to:
- ✅ Approve/reject withdrawals
- ✅ View all users
- ✅ View all transactions
- ✅ Access dashboard stats
- ✅ Search users and transactions

### Role Hierarchy
Currently single-tier admin system. All admins have equal permissions.

**Future Enhancement**: Add role-based access control (RBAC):
- Super Admin
- Finance Admin
- Support Admin

---

## 📊 Database Schema

### Core Tables

#### users
- Primary user data
- Wallet balances
- Registration status

#### deposits
- Deposit requests and SMS data
- Auto-approved status

#### withdrawals
- Withdrawal requests
- Admin approval required
- Telebirr payout details

#### transfers
- **Instant** peer-to-peer transfers
- No admin approval
- Auto-executed

#### used_sms
- Duplicate SMS prevention
- Reference number tracking
- SHA-256 hash storage

### Audit & Ledger Tables (NEW)

#### wallet_transactions
Complete ledger of all wallet movements:
- Transaction type (DEPOSIT, WITHDRAWAL, TRANSFER_IN, TRANSFER_OUT)
- Amount
- Balance before
- Balance after
- Reference to source entity (deposit_id, withdrawal_id, transfer_id)
- Timestamp

#### audit_logs
Complete audit trail of all actions:
- Action type
- User ID
- Admin ID (if applicable)
- Related entity references
- Metadata (JSON)
- IP address
- Timestamp

### Database Constraints

#### Financial Integrity
1. **Positive Balance**: `CHECK (main_wallet >= 0)`
2. **Valid Amounts**: `CHECK (amount > 0)`
3. **Unique References**: Unique constraint on `used_sms.reference_number`
4. **Foreign Keys**: CASCADE on user deletion, SET NULL on referenced entities

#### Concurrency Control
1. **Row Locking**: `SELECT FOR UPDATE` on wallet operations
2. **Ordered Locking**: Lock users by ID order to prevent deadlocks
3. **Atomic Transactions**: All wallet operations in single transaction

---

## ⚡ Rate Limiting

### Current Implementation
- **Window**: 60 seconds
- **Max Requests**: 30 per user
- **Storage**: Redis
- **Scope**: Per Telegram user ID

### Bypass Rules
- Admins: Not rate-limited
- System messages: Not rate-limited

---

## 🔄 Transaction Flow

### Deposit Flow (Auto-Approval)
```
User → Request Amount → Send to Telebirr → Paste SMS
  ↓
Parse SMS → Validate → Check Duplicate → Verify Timestamp
  ↓
APPROVED → Credit Wallet → Record Ledger → Notify User
```

### Withdrawal Flow (Admin Approval)
```
User → Request Amount → Enter Phone
  ↓
Create PENDING → Notify Admin
  ↓
Admin Approves → Verify Balance → Debit Wallet → Record Ledger
  ↓
Notify User → Admin Sends Money
```

### Transfer Flow (Instant - No Approval)
```
User → Enter Recipient → Enter Amount
  ↓
Validate Recipient → Check Balance → Lock Users
  ↓
Debit Sender → Credit Receiver → Record Ledger
  ↓
APPROVED → Notify Both Users
```

---

## 🔒 Security Features

### SMS Validation
1. **Receiver Verification**: Must match configured number
2. **Amount Matching**: ±0.01 ETB tolerance
3. **Duplicate Prevention**: Reference number + SHA-256 hash
4. **Timestamp Check**: 30-minute window
5. **Format Validation**: Regex pattern matching

### Wallet Protection
1. **Row Locking**: `SELECT FOR UPDATE` prevents race conditions
2. **Ledger Trail**: Every transaction recorded
3. **Balance Verification**: Checked at execution time, not request time
4. **Atomic Operations**: All-or-nothing transactions
5. **Ordered Locking**: Prevent deadlocks in transfers

### Audit Trail
1. **Complete Logging**: All actions logged in audit_logs
2. **Immutable Records**: Audit logs never deleted
3. **Metadata Storage**: JSON for additional context
4. **IP Tracking**: Optional IP address logging
5. **Admin Attribution**: Every admin action tracked

---

## 🌐 Environment Variables

### Required
```env
TELEGRAM_BOT_TOKEN=your_bot_token
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
REDIS_URL=redis://localhost:6379/0
TELEBIRR_RECEIVER_NUMBER=0909425014
ADMIN_TELEGRAM_IDS=[123456789]
```

### Optional
```env
TELEGRAM_WEBHOOK_URL=https://yourdomain.com
TELEGRAM_WEBHOOK_SECRET=random_secret
MINI_APP_URL=https://your-mini-app.com
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### Transaction Limits
```env
MIN_DEPOSIT_AMOUNT=10.0
MIN_WITHDRAWAL_AMOUNT=50.0
MIN_TRANSFER_AMOUNT=10.0
MAX_WITHDRAWAL_AMOUNT=50000.0
MAX_TRANSFER_AMOUNT=50000.0
```

### Rate Limiting
```env
RATE_LIMIT_MAX_REQUESTS=30
RATE_LIMIT_WINDOW_SECONDS=60
```

---

## 🐳 Docker Deployment

### Structure
```
amhabingo-bot/
├── docker-compose.yml      # Multi-service orchestration
├── Dockerfile              # Bot image
├── .env                    # Environment variables (gitignored)
└── volumes/
    ├── postgres_data/      # Database persistence
    └── redis_data/         # Redis persistence
```

### Services
1. **bot**: Python bot service
2. **api**: FastAPI webhook service
3. **postgres**: PostgreSQL database
4. **redis**: Redis cache

---

## 📈 Monitoring & Alerts

### Metrics to Monitor
- Deposit success rate
- Withdrawal approval time
- Transfer volume
- Failed SMS validations
- Database connection pool
- Redis memory usage

### Recommended Alerts
- Failed database connection
- High error rate (>5%)
- Slow admin approval (>1 hour)
- Duplicate SMS attempts
- Unusual transaction patterns

---

## 🧪 Testing Strategy

### Manual Testing Checklist
- [ ] User registration with contact
- [ ] Deposit with valid SMS
- [ ] Deposit with invalid SMS (wrong receiver)
- [ ] Deposit with duplicate SMS
- [ ] Deposit with old SMS (>30 min)
- [ ] Withdrawal request creation
- [ ] Admin withdrawal approval
- [ ] Admin withdrawal rejection
- [ ] Instant transfer execution
- [ ] Transfer to invalid user
- [ ] Transfer with insufficient balance
- [ ] Balance display accuracy
- [ ] Concurrent transfers (race condition test)

### Database Integrity Tests
- [ ] Wallet transaction ledger matches balances
- [ ] Audit logs match all actions
- [ ] No negative balances
- [ ] Reference numbers are unique
- [ ] Foreign key constraints work

---

## 🔄 Rejection Behavior

### Withdrawal Rejection
- Balance **NOT** deducted
- User notified: "Contact support"
- Status: REJECTED
- Logged in audit_logs

### Transfer (No Rejection - Instant Execution)
- Validation happens before execution
- Either succeeds completely or fails with clear error
- No pending state
- No admin review

### Deposit Rejection (Validation Failure)
- User notified immediately
- Specific error message (wrong receiver, duplicate, etc.)
- Can retry with different SMS
- Not logged in deposits table if validation fails

---

## 📋 API Endpoints

### Public
- `GET /health` - Health check

### Admin (Requires `X-Admin-Id` header)
- `GET /api/admin/stats` - Dashboard statistics
- `GET /api/admin/users` - List users
- `GET /api/admin/users/{id}` - Get user details
- `GET /api/admin/users?search=query` - Search users
- `GET /api/admin/deposits` - List deposits
- `GET /api/admin/withdrawals` - List withdrawals
- `POST /api/admin/withdrawals/{id}/approve` - Approve withdrawal
- `POST /api/admin/withdrawals/{id}/reject` - Reject withdrawal
- `GET /api/admin/transfers` - List transfers
- `GET /api/admin/audit-logs` - View audit trail (Future)
- `GET /api/admin/wallet-transactions` - View ledger (Future)

---

## 🚀 Performance Considerations

### Database Optimization
- Indexes on frequently queried columns
- Connection pooling (SQLAlchemy)
- Prepared statements
- Row-level locking only when needed

### Redis Usage
- FSM state storage (ephemeral)
- Rate limiting counters
- TTL on all keys (1 hour)

### Async Operations
- Non-blocking I/O throughout
- Concurrent notification sending
- Background task support (future)

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Status**: Production Ready
