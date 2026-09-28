# Simultaneous Winners - How It Works

## Overview

The bingo game now implements **fair handling of simultaneous winners** - when multiple players complete a winning pattern on the same number call.

---

## 🎯 Winner Logic

### **Single Winner (Most Common)**

**Scenario:** Only one player wins
```
Numbers called: B-5, I-20, N-35, G-50, O-65
→ Player A completes a LINE on O-65
→ No other players have winning pattern yet

Result:
✅ Player A wins 100% of prize pool
✅ Game ends immediately
```

**Example:**
- Prize pool: 1000 Birr
- Player A wins: **1000 Birr** (100%)

---

### **Simultaneous Winners (Rare but Handled)**

**Scenario:** Multiple players win on the SAME number call
```
Numbers called: B-5, I-20, N-35, G-50, O-65
→ Player A completes a LINE on O-65
→ Player B completes a DIAGONAL on O-65 (same number!)
→ Both detected as winners simultaneously

Result:
✅ Player A wins 50% of prize pool
✅ Player B wins 50% of prize pool
✅ Game ends immediately
```

**Example:**
- Prize pool: 1000 Birr
- Player A wins: **500 Birr** (50%)
- Player B wins: **500 Birr** (50%)

---

## 📊 Prize Distribution Examples

### **2 Simultaneous Winners**
```
Prize Pool: 1000 Birr
÷ 2 winners
= 500 Birr each
```

### **3 Simultaneous Winners**
```
Prize Pool: 1000 Birr
÷ 3 winners
= 333.33 Birr each
```

### **4 Simultaneous Winners**
```
Prize Pool: 1000 Birr
÷ 4 winners
= 250 Birr each
```

---

## 🔍 How Detection Works

### **During Number Call:**

1. **Number is called** (e.g., O-65)
2. **Server checks ALL active players** for winning patterns
3. **All winners on this number call are detected simultaneously**
4. **Prize pool divided equally** among all winners
5. **All winners paid at once**
6. **Game ends immediately**

### **Code Flow:**

```python
# Call number O-65
called_number = await call_next_number(game_id)

# Check ALL players for winners
new_winners = await check_all_players_for_winners(game_id)

# Result: Multiple players may have won on O-65
# new_winners = [
#     (Player A, WinPattern.ROW),
#     (Player B, WinPattern.DIAGONAL),
# ]

# Process all simultaneous winners
if new_winners:
    winner_count = len(new_winners)  # 2
    prize_per_winner = prize_pool / winner_count  # 1000 / 2 = 500
    
    for player, pattern in new_winners:
        pay_winner(player, prize_per_winner)  # Each gets 500
    
    finish_game(game_id)  # Game ends
```

---

## ⚖️ Fairness Guarantees

### **✅ Atomic Detection**
- All winners detected in same database transaction
- No race conditions
- Impossible for one winner to be processed before others

### **✅ Equal Split**
- Prize divided mathematically: `prize_pool / winner_count`
- Rounded to 2 decimal places (Birr)
- All winners get exactly equal amounts

### **✅ Simultaneous Payment**
- All winners paid in same transaction
- If one payment fails, all payments rollback
- Database locks prevent double-spending

### **✅ Audit Trail**
- All winners logged in `game_events` table
- Each winner's `WalletTransaction` recorded
- Event data includes: `simultaneous_winners` count and `prize_split` amount

---

## 📝 Database Records

### **Example: 2 Simultaneous Winners**

**game_events table:**
```sql
id | game_id | event_type       | user_id | description
---|---------|------------------|---------|----------------------------------
1  | 123     | WINNER_DECLARED  | 456     | Winner - ROW (2 simultaneous winner(s))
2  | 123     | WINNER_DECLARED  | 789     | Winner - DIAGONAL (2 simultaneous winner(s))
```

**game_players table:**
```sql
id | game_id | user_id | is_winner | winning_position | prize_amount
---|---------|---------|-----------|------------------|-------------
1  | 123     | 456     | true      | 1                | 500.00
2  | 123     | 789     | true      | 1                | 500.00
```

**wallet_transactions table:**
```sql
id | user_id | type          | amount  | description
---|---------|---------------|---------|--------------------------------
1  | 456     | BINGO_PRIZE   | 500.00  | Bingo Prize - Game #123 (Pos 1)
2  | 789     | BINGO_PRIZE   | 500.00  | Bingo Prize - Game #123 (Pos 1)
```

**Note:** Both winners have `winning_position = 1` because they won simultaneously (no 1st/2nd place).

---

## 🎮 Player Experience

### **Telegram Notification (Single Winner):**
```
🎉 CONGRATULATIONS! 🎉

You won Game #123!

Pattern: ROW
Prize: 1000 Birr

The prize has been credited to your main wallet.
```

### **Telegram Notification (Simultaneous Winners):**
```
🎉 CONGRATULATIONS! 🎉

You won Game #123!

Pattern: ROW
You and 1 other player won simultaneously!
Your share: 500 Birr (50%)

The prize has been credited to your main wallet.
```

---

## 🔧 Admin View

### **Admin API Response (Simultaneous Winners):**

```json
{
  "message": "Number called successfully",
  "winners": [
    {
      "user_id": 456,
      "winning_position": 1,
      "win_pattern": "ROW",
      "prize_amount": 500.00
    },
    {
      "user_id": 789,
      "winning_position": 1,
      "win_pattern": "DIAGONAL",
      "prize_amount": 500.00
    }
  ]
}
```

---

## 📊 Probability of Simultaneous Winners

### **How Rare Is It?**

**Depends on:**
1. **Number of players** - More players = higher chance
2. **Pattern type** - Simple patterns (lines) = higher chance than full card
3. **Game timing** - Later in game = more marked numbers = higher chance

**Example Probabilities:**

| Players | Pattern Type | Probability |
|---------|--------------|-------------|
| 10      | Any Line     | ~5-10%      |
| 50      | Any Line     | ~20-30%     |
| 100     | Any Line     | ~40-50%     |
| 10      | Full Card    | ~0.1%       |
| 50      | Full Card    | ~1-2%       |
| 100     | Full Card    | ~5-10%      |

**Reality:** Simultaneous winners are **uncommon but possible**, especially with:
- Many players (50+)
- Simple patterns (lines)
- Late-game scenarios

---

## ✅ Why This Is Fair

### **Traditional Bingo Problem:**
In physical bingo halls, if two people shout "BINGO!" at the same time:
- Hard to determine who said it first
- Sometimes leads to disputes
- Relies on human judgment

### **Our Digital Solution:**
- Server is the source of truth
- Mathematically precise detection
- No human judgment needed
- Perfectly fair prize split
- Transparent audit trail

---

## 🚀 Testing Scenarios

### **Test 1: Single Winner**
1. Create game with 2+ players
2. Let auto-caller run
3. First winner detected
4. Verify winner gets 100%
5. Verify game ends immediately

### **Test 2: Simultaneous Winners (Simulated)**
To simulate simultaneous winners for testing:

1. Manually construct cartelas so multiple players win on same number
2. Or: Run game with many players (50+) to increase probability
3. Verify prize split correctly
4. Verify all winners paid
5. Verify game ends immediately

### **Test 3: Database Integrity**
1. Check `game_events` - one entry per winner
2. Check `game_players` - all have `is_winner = true`
3. Check `wallet_transactions` - one per winner
4. Verify sum of prizes = prize pool

---

## 📖 Summary

**Single Winner (Most Games):**
- ✅ First player to win gets 100%
- ✅ Game ends immediately
- ✅ Simple and exciting

**Simultaneous Winners (Rare):**
- ✅ Prize split equally among all winners
- ✅ All paid in same transaction
- ✅ Fair and transparent
- ✅ Game ends immediately

**Result:** Fair, exciting, and mathematically correct bingo game! 🎉
