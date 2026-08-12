# AMHABINGO Admin Quick Guide

## 🎯 Quick Start

You will receive notifications in Telegram for all pending requests. Each notification has inline buttons for quick approval/rejection.

---

## 📨 Notification Types

### 1. **Deposit Request** (Auto-Approved)
Deposits are automatically approved when SMS is valid. You receive notifications for logging purposes only.

```
🔔 New Deposit Request

👤 User: John Doe (ID: 123)
💰 Amount: 500.00 ETB
🔑 Reference: TXN12345678
📱 Sender: 0912345678
🆔 Deposit ID: 42
```

**Note**: With current configuration, deposits are auto-approved after SMS verification. To require manual approval, contact the developer.

---

### 2. **Withdrawal Request**
User wants to withdraw money to their Telebirr account.

```
🔔 New Withdrawal Request

👤 User: Jane Smith (ID: 456)
💸 Amount: 200.00 ETB
📱 Telebirr: 0923456789
🆔 Withdrawal ID: 15

[✅ Approve] [❌ Reject]
```

**When to Approve:**
- ✅ User has sufficient balance (checked automatically)
- ✅ Telebirr number looks valid
- ✅ No suspicious activity

**What Happens:**
- Amount deducted from user's Main Wallet
- User receives notification
- You must manually send money to their Telebirr number
- Message updates to show it was approved

**What User Sees:**
```
✅ Withdrawal Approved!

200.00 ETB will be sent to 0923456789 shortly.

The amount has been deducted from your Main Wallet.
```

---

### 3. **Transfer Request**
User wants to transfer money to another user.

```
🔔 New Transfer Request

📤 From: Alice (ID: 101)
📥 To: Bob (ID: 202)
🎁 Amount: 150.00 ETB
🆔 Transfer ID: 8

[✅ Approve] [❌ Reject]
```

**When to Approve:**
- ✅ Both users are legitimate
- ✅ Sender has sufficient balance (checked automatically)
- ✅ No suspicious activity

**What Happens:**
- Amount moved from sender to receiver atomically
- Both users receive notifications
- Message updates to show transfer details

**What Sender Sees:**
```
✅ Transfer Approved!

150.00 ETB has been sent to Bob.

The amount has been deducted from your Main Wallet.
```

**What Receiver Sees:**
```
🎁 You received a transfer!

Alice sent you 150.00 ETB.

The amount has been added to your Main Wallet.
```

---

## 🚫 Rejecting Requests

When you reject a request:

### Withdrawal Rejection
- ❌ User's balance is NOT changed
- 📢 User receives notification to contact support
- 💡 Common reasons: suspicious activity, duplicate request

**What User Sees:**
```
❌ Withdrawal Rejected

Your withdrawal request has been rejected.
Your balance remains unchanged.

Please contact support if you have questions.
```

### Transfer Rejection
- ❌ No funds moved
- 📢 Sender receives notification
- 💡 Common reasons: fraud prevention, terms violation

**What Sender Sees:**
```
❌ Transfer Rejected

Your transfer request has been rejected.
Your balance remains unchanged.

Please contact support if you have questions.
```

---

## 🔒 Safety Features

### 1. **Idempotent Approvals**
- Can't approve the same request twice
- If you accidentally click approve again, nothing happens
- System shows: "Already processed"

### 2. **Balance Protection**
- Balance verified at approval time (not just request time)
- If user spent money elsewhere, approval fails safely
- Prevents overdrafts and negative balances

### 3. **Status Checks**
- Only PENDING requests can be processed
- Already approved/rejected requests are locked

### 4. **Atomic Transactions**
- All database operations are atomic
- If something fails, everything rolls back
- No partial updates or corrupted data

---

## 📊 Admin Dashboard API

You can also manage requests via REST API:

**Base URL**: `https://your-domain.com/admin/`

**Authentication**: Add header `X-Admin-Id: YOUR_TELEGRAM_ID`

### List Pending Withdrawals
```bash
GET /admin/withdrawals?status=PENDING
```

### Approve Withdrawal
```bash
POST /admin/withdrawals/15/approve
Content-Type: application/json

{
  "note": "Verified and sent"
}
```

### Reject Withdrawal
```bash
POST /admin/withdrawals/15/reject
Content-Type: application/json

{
  "note": "Suspicious activity"
}
```

Same pattern for transfers:
- `GET /admin/transfers?status=PENDING`
- `POST /admin/transfers/8/approve`
- `POST /admin/transfers/8/reject`

### Dashboard Stats
```bash
GET /admin/stats
```

Returns:
```json
{
  "total_users": 1523,
  "registered_users": 1401,
  "total_deposits": 8456,
  "total_deposited_etb": 2451000.50,
  "pending_withdrawals": 12,
  "pending_transfers": 5
}
```

---

## 💰 Business Rules

### Minimum Amounts
- Deposit: **10 ETB**
- Withdrawal: **50 ETB**
- Transfer: **10 ETB**

### Maximum Amounts
- Withdrawal: **50,000 ETB**
- Transfer: **50,000 ETB**

These are configurable in `.env` file.

---

## ⚡ Quick Actions

### Check User Balance
1. Send `/admin` command in bot (future feature)
2. Or use API: `GET /admin/users/{user_id}`

### Search Users
```bash
GET /admin/users?search=0912345678
GET /admin/users?search=username
```

### View Transaction History
```bash
GET /admin/deposits?user_id=123
GET /admin/withdrawals?user_id=123
GET /admin/transfers?sender_id=123
```

---

## 🚨 Common Issues

### "Already processed"
- Someone already approved/rejected this request
- Check notification history
- No action needed

### "Insufficient balance"
- User spent money between request and approval
- Reject the request
- User will need to make new request

### User not receiving notifications
- Check if user blocked the bot
- Verify their chat_id is correct
- Logs will show "Failed to notify user"

---

## 📞 Support

If you encounter issues:
1. Check the logs: `backend/logs/`
2. Verify database status: `python check_db.py`
3. Contact developer

---

## 🎓 Best Practices

1. **Process requests promptly** - Users are waiting
2. **Verify large amounts** - Double-check big withdrawals
3. **Watch for patterns** - Same user requesting multiple times
4. **Keep records** - The system logs everything, but note suspicious activity
5. **Communicate** - If rejecting, follow up with user via support channel

---

## 📱 Admin Telegram IDs

Current admins (from `.env`):
```
ADMIN_TELEGRAM_IDS=[5655910680]
```

To add more admins:
1. Get their Telegram user ID
2. Add to the list in `.env`
3. Restart the bot

---

## ✅ Daily Checklist

- [ ] Check pending withdrawals
- [ ] Check pending transfers  
- [ ] Review any flagged deposits
- [ ] Verify sent money matches approved withdrawals
- [ ] Monitor dashboard stats
- [ ] Check for any error logs

---

**Remember**: The bot handles all the technical details. You just need to:
1. ✅ Approve legitimate requests
2. ❌ Reject suspicious ones
3. 💰 Send money for approved withdrawals

The system ensures everything else is safe and atomic! 🛡️
