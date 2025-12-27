# Setting Up Web App URL for Telegram Mini App

## What URL to Give BotFather

The Web App URL should point to your Flask application's root URL (where `index.html` is served).

## Option 1: Using ngrok (Quick Local Testing)

1. **Install ngrok:**
   ```bash
   # macOS
   brew install ngrok
   
   # Or download from https://ngrok.com/download
   ```

2. **Start your Flask app:**
   ```bash
   python3 app.py
   ```
   Your app will run on `http://localhost:5000`

3. **In a new terminal, start ngrok:**
   ```bash
   ngrok http 5000
   ```

4. **Copy the HTTPS URL** (looks like `https://abc123.ngrok.io`)

5. **Give this URL to BotFather:**
   ```
   https://abc123.ngrok.io
   ```
   (Use your actual ngrok URL)

6. **Update your `.env` file:**
   ```
   WEB_APP_URL=https://abc123.ngrok.io
   ```

**Note:** Free ngrok URLs change each time you restart ngrok. For permanent URLs, use ngrok's paid plan or deploy to a hosting service.

## Option 2: Deploy to Hosting Service (Recommended for Production)

### Railway (Easy & Free Tier Available)

1. Go to [railway.app](https://railway.app)
2. Create new project → Deploy from GitHub
3. Connect your repository
4. Add environment variables:
   - `TELEGRAM_BOT_TOKEN=your_token`
   - `WEB_APP_URL=https://your-app.railway.app`
5. Railway will give you a URL like: `https://your-app.railway.app`
6. Give this URL to BotFather

### Render (Free Tier Available)

1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect your repository
4. Set:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
5. Add environment variables
6. Render gives you: `https://your-app.onrender.com`
7. Give this URL to BotFather

### Heroku

1. Install Heroku CLI
2. Create `Procfile`:
   ```
   web: python app.py
   ```
3. Deploy:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```
4. Get URL: `https://your-app-name.herokuapp.com`
5. Give this URL to BotFather

## Option 3: Your Own Server

If you have a VPS or server:

1. Deploy your Flask app
2. Set up Nginx reverse proxy
3. Configure SSL certificate (Let's Encrypt)
4. Your URL: `https://yourdomain.com`
5. Give this URL to BotFather

## Important Notes

✅ **Must be HTTPS** - Telegram requires HTTPS for Mini Apps  
✅ **Must be publicly accessible** - Can't use localhost directly  
✅ **Root URL** - Just the domain, Flask serves `/` automatically  
✅ **Keep it running** - The URL must be accessible when users open the Mini App

## Quick Test

After setting up, test your URL:
```bash
curl https://your-url.com
```

You should see the HTML content of your Mini App.

## Example URLs

- ✅ `https://my-app.railway.app`
- ✅ `https://my-app.onrender.com`
- ✅ `https://abc123.ngrok.io` (for testing)
- ✅ `https://mydomain.com`
- ❌ `http://localhost:5000` (not accessible)
- ❌ `http://192.168.1.100:5000` (not HTTPS)

