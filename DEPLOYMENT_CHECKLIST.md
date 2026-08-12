# 🚀 AMHABINGO Bot - Deployment Checklist

## Pre-Deployment

### 1. Environment Variables
- [ ] Copy `.env.example` to `.env` (if not already done)
- [ ] Set `TELEGRAM_BOT_TOKEN` (get from @BotFather)
- [ ] Set `DATABASE_URL` (PostgreSQL connection string)
- [ ] Set `REDIS_URL` (Redis connection string)
- [ ] Add `ADMIN_TELEGRAM_IDS` (your Telegram user ID)
- [ ] Verify `TELEBIRR_RECEIVER_NUMBER` (payment receiving number)
- [ ] Set `SUPPORT_CHANNEL_URL` (your support Telegram channel)
- [ ] Set `BOT_USERNAME` (your bot's username without @)
- [ ] Review and adjust limits if needed:
  - `MIN_DEPOSIT_AMOUNT`
  - `MIN_WITHDRAWAL_AMOUNT`
  - `MIN_TRANSFER_AMOUNT`
  - `MAX_WITHDRAWAL_AMOUNT`
  - `MAX_TRANSFER_AMOUNT`

### 2. Database Setup
- [ ] PostgreSQL server is running
- [ ] Database created
- [ ] Connection string tested
- [ ] Run migrations:
  ```bash
  alembic upgrade head
  ```
- [ ] Verify tables created:
  ```bash
  python check_db.py
  ```

### 3. Redis Setup
- [ ] Redis server is running
- [ ] Connection string tested
- [ ] Or use `memory://` for development

### 4. Dependencies
- [ ] Python 3.13 installed
- [ ] Install requirements:
  ```bash
  pip install -r requirements.txt
  ```
- [ ] All packages installed successfully

### 5. Bot Configuration
- [ ] Bot created via @BotFather
- [ ] Bot username set
- [ ] Bot description set
- [ ] Bot profile picture uploaded (optional)
- [ ] Privacy mode disabled (so bot receives all messages)
  ```
  /mybots → Select bot → Bot Settings → Group Privacy → Turn OFF
  ```

---

## Testing (Development)

### 1. Start Bot in Polling Mode
```bash
python backend/run_polling.py
```

### 2. Test Basic Commands
- [ ] Send `/start` - verify welcome message and keyboard
- [ ] Press each button and verify response
- [ ] Test registration with contact sharing
- [ ] Check balance display

### 3. Test Deposit Flow
- [ ] Start deposit with amount below minimum (should reject)
- [ ] Start deposit with valid amount
- [ ] Paste invalid SMS (wrong receiver) - should reject
- [ ] Paste valid SMS - should approve and credit wallet
- [ ] Try same SMS again - should reject as duplicate

### 4. Test Withdrawal Flow
- [ ] Request withdrawal below minimum (should reject)
- [ ] Request withdrawal with insufficient balance (should reject)
- [ ] Request valid withdrawal
- [ ] Admin approves - verify balance deducted
- [ ] User receives notification

### 5. Test Transfer Flow
- [ ] Transfer to non-existent user (should reject)
- [ ] Transfer below minimum (should reject)
- [ ] Transfer with insufficient balance (should reject)
- [ ] Transfer to valid user
- [ ] Admin approves - verify both notified

### 6. Test Admin Features
- [ ] Receive notification for withdrawal
- [ ] Click Approve - verify works
- [ ] Try approve again - verify blocked
- [ ] Reject a request - verify user notified

### 7. Test Cancel Button
- [ ] Start deposit flow → press Cancel
- [ ] Start withdrawal flow → press Cancel
- [ ] Start transfer flow → press Cancel
- [ ] Verify returns to main menu each time

### 8. Run Test Suite
```bash
python test_bot_complete.py
```
- [ ] All tests pass

---

## Production Deployment

### Option A: VPS/Dedicated Server

#### 1. Server Setup
- [ ] Ubuntu/Debian server provisioned
- [ ] SSH access configured
- [ ] Firewall configured (allow 80, 443, PostgreSQL, Redis)
- [ ] Domain name pointed to server (optional)

#### 2. Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.13
sudo apt install python3.13 python3.13-venv python3-pip -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Redis
sudo apt install redis-server -y

# Install Nginx (if using webhook)
sudo apt install nginx -y
```

#### 3. Application Setup
```bash
# Create user
sudo useradd -m -s /bin/bash amhabingo
sudo su - amhabingo

# Clone/upload code
git clone YOUR_REPO_URL amhabingo-bot
cd amhabingo-bot

# Create virtual environment
python3.13 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Setup environment
cp .env.example .env
nano .env  # Configure all variables

# Run migrations
alembic upgrade head
```

#### 4. Systemd Service (Polling Mode)
Create `/etc/systemd/system/amhabingo-bot.service`:
```ini
[Unit]
Description=AMHABINGO Telegram Bot
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=amhabingo
WorkingDirectory=/home/amhabingo/amhabingo-bot
Environment="PATH=/home/amhabingo/amhabingo-bot/venv/bin"
ExecStart=/home/amhabingo/amhabingo-bot/venv/bin/python backend/run_polling.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable amhabingo-bot
sudo systemctl start amhabingo-bot
sudo systemctl status amhabingo-bot
```

#### 5. FastAPI Service (for Admin API + Webhook)
Create `/etc/systemd/system/amhabingo-api.service`:
```ini
[Unit]
Description=AMHABINGO API Server
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=amhabingo
WorkingDirectory=/home/amhabingo/amhabingo-bot
Environment="PATH=/home/amhabingo/amhabingo-bot/venv/bin"
ExecStart=/home/amhabingo/amhabingo-bot/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable amhabingo-api
sudo systemctl start amhabingo-api
```

#### 6. Nginx Configuration (Optional - for Admin API)
Create `/etc/nginx/sites-available/amhabingo`:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /admin/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/amhabingo /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

### Option B: Docker Deployment

#### 1. Install Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### 2. Configure Environment
```bash
cp .env.example .env
nano .env  # Configure all variables
```

#### 3. Start Services
```bash
# Build and start
docker-compose up -d

# Check logs
docker-compose logs -f bot

# Run migrations
docker-compose exec bot alembic upgrade head
```

#### 4. Management Commands
```bash
# Stop services
docker-compose down

# Restart bot only
docker-compose restart bot

# View logs
docker-compose logs -f bot

# Access bot shell
docker-compose exec bot bash
```

---

### Option C: Render.com Deployment

#### 1. Prepare Repository
- [ ] Push code to GitHub
- [ ] Ensure `render.yaml` is configured
- [ ] Ensure `Dockerfile` is present

#### 2. Create Services on Render
- [ ] Create PostgreSQL database
- [ ] Note database connection URL
- [ ] Create Redis instance (or use Upstash)
- [ ] Create Web Service for API
- [ ] Create Background Worker for bot

#### 3. Configure Environment
- [ ] Add all environment variables in Render dashboard
- [ ] Use internal database URL
- [ ] Use internal Redis URL

#### 4. Deploy
- [ ] Push to GitHub
- [ ] Render auto-deploys
- [ ] Check logs for errors
- [ ] Run migrations via Render shell

---

## Post-Deployment

### 1. Verify Bot Running
- [ ] Send `/start` to bot
- [ ] Bot responds correctly
- [ ] Keyboard appears
- [ ] All buttons work

### 2. Test Critical Flows
- [ ] Registration works
- [ ] Deposit works end-to-end
- [ ] Withdrawal creates request
- [ ] Transfer creates request
- [ ] Admin receives notifications

### 3. Monitor Logs
```bash
# Systemd
sudo journalctl -u amhabingo-bot -f

# Docker
docker-compose logs -f bot

# File logs
tail -f backend/logs/app.log
```

### 4. Database Health
```bash
python check_db.py
```
- [ ] All tables present
- [ ] Can create test user
- [ ] Migrations up to date

### 5. Performance Check
- [ ] Bot responds quickly (< 1 second)
- [ ] Database queries fast
- [ ] Redis working
- [ ] No memory leaks

---

## Monitoring & Maintenance

### Daily Tasks
- [ ] Check logs for errors
- [ ] Process pending withdrawals
- [ ] Process pending transfers
- [ ] Monitor user growth

### Weekly Tasks
- [ ] Review transaction patterns
- [ ] Check database size
- [ ] Backup database
- [ ] Update dependencies if needed

### Monthly Tasks
- [ ] Review server resources
- [ ] Optimize database (VACUUM)
- [ ] Update bot features
- [ ] Review admin access

---

## Backup Strategy

### Database Backup (PostgreSQL)
```bash
# Manual backup
pg_dump -U username dbname > backup_$(date +%Y%m%d).sql

# Automated daily backup (cron)
0 2 * * * pg_dump -U username dbname > /backups/backup_$(date +\%Y\%m\%d).sql
```

### Configuration Backup
- [ ] Backup `.env` file (securely!)
- [ ] Backup `alembic.ini`
- [ ] Backup Nginx configs
- [ ] Backup systemd services

---

## Rollback Plan

### If Deployment Fails:

1. **Revert Code**
   ```bash
   git checkout previous_stable_tag
   sudo systemctl restart amhabingo-bot
   ```

2. **Revert Database**
   ```bash
   alembic downgrade -1
   ```

3. **Restore from Backup**
   ```bash
   psql -U username dbname < backup_YYYYMMDD.sql
   ```

---

## Security Checklist

- [ ] `.env` file has restricted permissions (600)
- [ ] PostgreSQL uses strong password
- [ ] Redis uses password (if exposed)
- [ ] SSH uses key authentication only
- [ ] Firewall configured properly
- [ ] Admin Telegram IDs verified
- [ ] Webhook uses secret token (if applicable)
- [ ] HTTPS enabled for API (if exposed)
- [ ] Rate limiting configured
- [ ] Logs don't contain sensitive data

---

## Scaling Considerations

### If User Base Grows:

1. **Database**
   - [ ] Add read replicas
   - [ ] Enable connection pooling
   - [ ] Add indexes for slow queries

2. **Bot Performance**
   - [ ] Use webhook mode instead of polling
   - [ ] Add more bot workers
   - [ ] Implement message queue

3. **Admin API**
   - [ ] Add caching layer
   - [ ] Use CDN for static files
   - [ ] Add load balancer

---

## Support Contacts

- **Bot Issues**: Check logs first
- **Database Issues**: PostgreSQL documentation
- **Telegram Issues**: Telegram Bot API docs
- **Code Issues**: Review GitHub issues

---

## 🎉 Launch Day

Once everything is checked:

1. [ ] Announce bot in support channel
2. [ ] Share bot link with initial users
3. [ ] Monitor first transactions closely
4. [ ] Be ready to handle support requests
5. [ ] Celebrate! 🎊

---

**Bot is ready for production! Good luck! 🚀**
