# Deploy to Render - Step by Step Guide

## Quick Setup (5 minutes)

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub (easiest option)
3. Verify your email

### Step 2: Create New Web Service
1. In Render dashboard, click "New +"
2. Select "Web Service"
3. Connect your GitHub account if not already connected
4. Select your `tap-tap` repository

### Step 3: Configure Service
Fill in the following:

- **Name:** `tap-tap-miniapp` (or any name you like)
- **Region:** Choose closest to you (e.g., `Oregon (US West)`)
- **Branch:** `main` (or your default branch)
- **Root Directory:** Leave empty (or `./` if needed)
- **Environment:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python app.py`

### Step 4: Add Environment Variables
Scroll down to "Environment Variables" section, click "Add Environment Variable" and add:

1. **TELEGRAM_BOT_TOKEN**
   - Key: `TELEGRAM_BOT_TOKEN`
   - Value: Your bot token from BotFather

2. **WEB_APP_URL** (we'll update this after deployment)
   - Key: `WEB_APP_URL`
   - Value: `https://your-app-name.onrender.com` (we'll get the actual URL in next step)

### Step 5: Deploy
1. Scroll down and click "Create Web Service"
2. Render will start building and deploying (takes 2-3 minutes)
3. Wait for "Live" status (green indicator)

### Step 6: Get Your URL
1. Once deployed, you'll see your service URL at the top
2. It will look like: `https://tap-tap-miniapp.onrender.com`
3. **Copy this URL** - this is your Web App URL!

### Step 7: Update Environment Variable
1. Go to your service → Environment tab
2. Edit `WEB_APP_URL` variable
3. Set it to your actual Render URL: `https://tap-tap-miniapp.onrender.com`
4. Save changes (this will trigger a redeploy)

### Step 8: Configure Bot in BotFather
1. Open Telegram and go to [@BotFather](https://t.me/BotFather)
2. Send `/newapp`
3. Select your bot
4. When asked for **Web App URL**, paste your Render URL:
   ```
   https://tap-tap-miniapp.onrender.com
   ```
5. (Optional) Add a short name and description
6. Done! ✅

## Your Web App URL Format

Render will give you a URL like:
```
https://tap-tap-miniapp.onrender.com
```

**This is what you give to BotFather** - just the root URL, no paths needed.

## Testing Your Deployment

1. **Test in browser:**
   - Open `https://your-app.onrender.com` in browser
   - You should see the Mini App interface (may take a few seconds on first load due to cold start)

2. **Test in Telegram:**
   - Send `/start` to your bot
   - Click "🎮 Open Mini App" button
   - The Mini App should open! 🎉

## Running the Bot Locally

The bot (`bot.py`) can run on your local machine:

1. Make sure your `.env` file has:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   WEB_APP_URL=https://your-app.onrender.com
   ```

2. Run the bot:
   ```bash
   python3 bot.py
   ```

The bot just needs to send the Mini App button - it doesn't need to be deployed.

## Render Free Tier Notes

✅ **What's included:**
- Free HTTPS URL
- 750 hours/month (enough for always-on)
- 512MB RAM
- Auto-deploys on git push

⚠️ **Limitations:**
- Services sleep after 15 minutes of inactivity
- First request after sleep takes ~30 seconds (cold start)
- Subsequent requests are fast

💡 **Tip:** To keep it always awake, you can:
- Use a service like [UptimeRobot](https://uptimerobot.com) to ping your URL every 5 minutes
- Or upgrade to paid plan ($7/month) for always-on

## Updating Your App

Every time you push to GitHub:
1. Render automatically detects changes
2. Rebuilds and redeploys
3. Your Mini App updates automatically!

## Troubleshooting

**Service won't start:**
- Check Build Logs in Render dashboard
- Make sure `requirements.txt` is correct
- Verify Python version compatibility

**Mini App doesn't open:**
- Make sure URL in BotFather matches Render URL exactly
- Check that service status is "Live" (green)
- Try opening URL directly in browser first
- Wait a moment if it just woke up (cold start)

**Environment variables not working:**
- Make sure variables are set in Render dashboard
- Redeploy after adding/changing variables
- Check that variable names match exactly (case-sensitive)

## Next Steps

1. ✅ Deploy to Render (follow steps above)
2. ✅ Get your Render URL
3. ✅ Configure in BotFather
4. ✅ Test the Mini App
5. 🎉 Start using your task management system!

Need help? Check Render's [documentation](https://render.com/docs) or their support.

