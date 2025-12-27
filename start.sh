#!/bin/bash

# Start script for Tap Tap Task Game
# This script starts both the Flask web server and Telegram bot

echo "🚀 Starting Tap Tap Task Game..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file with your TELEGRAM_BOT_TOKEN and WEB_APP_URL"
    exit 1
fi

# Start Flask app in background
echo "📱 Starting Flask web server..."
python3 app.py &
FLASK_PID=$!

# Wait a moment for Flask to start
sleep 2

# Start Telegram bot
echo "🤖 Starting Telegram bot..."
python3 bot.py &
BOT_PID=$!

echo ""
echo "✅ Services started!"
echo "   Flask server PID: $FLASK_PID"
echo "   Bot PID: $BOT_PID"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap "kill $FLASK_PID $BOT_PID 2>/dev/null; exit" INT TERM
wait

