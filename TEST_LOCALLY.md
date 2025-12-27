# Testing Locally

## Quick Test - See the UI in Browser

1. **Start the Flask server:**
   ```bash
   python3 app.py
   ```

2. **Open in browser:**
   - Go to: `http://localhost:5000`
   - You'll see the Mini App interface!

**Note:** Some Telegram-specific features won't work in browser (like user data), but you can see the UI and test the layout.

## Full Test - With Telegram Mini App

To test the actual Mini App in Telegram:

1. **Install ngrok:**
   ```bash
   brew install ngrok
   # Or download from https://ngrok.com/download
   ```

2. **Start Flask server:**
   ```bash
   python3 app.py
   ```

3. **In a new terminal, start ngrok:**
   ```bash
   ngrok http 5000
   ```

4. **Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

5. **Update your `.env` file:**
   ```
   WEB_APP_URL=https://abc123.ngrok.io
   ```

6. **Configure in BotFather:**
   - Send `/newapp` to [@BotFather](https://t.me/BotFather)
   - Set Web App URL to your ngrok URL

7. **Test in Telegram:**
   - Send `/start` to your bot
   - Click "Open Mini App" button
   - The Mini App will open! 🎉

## Testing Features

### In Browser (localhost:5000):
- ✅ See the UI design
- ✅ Test navigation between tabs
- ✅ See layout and styling
- ❌ User data won't load (needs Telegram context)
- ❌ API calls will fail (needs Telegram initData)

### In Telegram Mini App:
- ✅ Full functionality
- ✅ User authentication
- ✅ All features work
- ✅ Real task management

## Troubleshooting

**Port already in use:**
```bash
# Find what's using port 5000
lsof -i :5000

# Kill it or use different port
python3 app.py  # Will use PORT env var or default 5000
```

**ngrok not working:**
- Make sure Flask is running first
- Check ngrok is pointing to correct port (5000)
- Try restarting ngrok

**Mini App not opening:**
- Make sure URL in BotFather matches ngrok URL exactly
- Check that Flask is running
- Verify ngrok shows "Forwarding" status

