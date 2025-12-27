# Deploy to Railway - Step by Step Guide

## Quick Setup (5 minutes)

### Step 1: Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub (easiest)

### Step 2: Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your `tap-tap` repository
4. Railway will automatically detect it's a Python app

### Step 3: Add Environment Variables
In Railway dashboard, go to your project → Variables tab, add:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
WEB_APP_URL=https://your-app-name.railway.app
```

**Important:** Railway will give you a URL like `https://your-app-name.railway.app` - use that for `WEB_APP_URL`

### Step 4: Get Your URL
1. Railway automatically provides a URL
2. Go to Settings → Domains
3. Copy your Railway-provided domain (e.g., `https://tap-tap-production.up.railway.app`)

### Step 5: Configure Bot
1. Send `/newapp` to [@BotFather](https://t.me/BotFather)
2. Select your bot
3. When asked for Web App URL, paste your Railway URL
4. Done! ✅

## Your Web App URL Format

Railway will give you a URL like:
```
https://tap-tap-production-xxxx.up.railway.app
```

**This is what you give to BotFather** - just the root URL, no paths needed.

## Updating Your Bot

The bot (`bot.py`) also needs to know the URL. You have two options:

### Option A: Run bot locally (recommended for now)
- Keep running `python bot.py` on your computer
- The bot just needs to send the Mini App button, it doesn't need to be deployed

### Option B: Deploy bot to Railway too
- Create a second service in Railway
- Set start command: `python bot.py`
- Add the same environment variables

## Testing

1. Deploy to Railway
2. Wait for deployment to complete (usually 1-2 minutes)
3. Test the URL in browser: `https://your-url.railway.app`
4. You should see the Mini App interface
5. Send `/start` to your bot in Telegram
6. Click the "Open Mini App" button
7. The Mini App should open! 🎉

## Troubleshooting

**If the URL doesn't work:**
- Check Railway logs (View Logs in dashboard)
- Make sure environment variables are set
- Verify the app is running (Status should be "Active")

**If Mini App doesn't open:**
- Make sure URL is HTTPS (Railway provides this automatically)
- Check that URL in BotFather matches Railway URL exactly
- Try opening the URL directly in browser first

## Free Tier Limits

Railway free tier includes:
- $5 credit per month
- Enough for small apps like this
- Auto-sleeps after inactivity (wakes on first request)

For always-on, consider upgrading or use Render (no sleep on free tier).

