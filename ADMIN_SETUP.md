# Admin Setup Guide

## Setting Up Admin Users

Only admins can create tasks in the system. Here's how to set it up:

### Step 1: Get Your Telegram ID

1. Open Telegram and search for [@userinfobot](https://t.me/userinfobot)
2. Send `/start` to the bot
3. It will reply with your Telegram ID (a number like `123456789`)

### Step 2: Add Admin ID to Environment

Add your Telegram ID to the `.env` file:

```bash
ADMIN_TELEGRAM_IDS=123456789
```

For multiple admins, separate with commas:
```bash
ADMIN_TELEGRAM_IDS=123456789,987654321,555555555
```

### Step 3: Restart Services

After updating `.env`, restart your Flask server and bot:

```bash
# Stop current processes
# Then restart:
python3 app.py
python3 bot.py
```

## Features for Admins

✅ **Create Tasks** - Only admins can create new tasks  
✅ **No Cost** - Admins don't pay coins to create tasks  
✅ **Task Management** - Full control over task creation  

## Features for Regular Users

✅ **Complete Tasks** - Earn coins by completing tasks  
✅ **Level System** - Level up every 10 completed tasks  
✅ **Referral System** - Earn 5 coins per referral  
✅ **Leaderboard** - Compete with other players  

## Testing Admin Access

1. Make sure your Telegram ID is in `ADMIN_TELEGRAM_IDS`
2. Open the Mini App
3. You should see the "➕ Create" tab
4. Regular users won't see this tab

