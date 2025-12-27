# Tap Tap Task Game - Telegram Mini App

A Telegram Mini App game where users can assign tasks to others, complete tasks to earn coins, and participate in a referral system. Features a beautiful web-based interface accessible directly within Telegram.

## Features

- 🎯 **Task Management**: Create, assign, and complete tasks through an intuitive web interface
- 💰 **Coin System**: Earn coins by completing tasks
- 👥 **Referral System**: Earn bonus coins by referring friends
- 📊 **Leaderboard**: See top coin earners
- 📈 **Transaction History**: Track all your coin transactions
- 🎨 **Modern UI**: Beautiful Telegram Mini App interface with native Telegram theming

## Setup

### Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (get one from [@BotFather](https://t.me/BotFather))
- A public URL for your web app (for production) or use localhost for development

### Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```bash
cp .env.example .env
```

4. Edit `.env` and add your configuration:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
WEB_APP_URL=http://localhost:5000
```

**For Production (Recommended - Render):**
- See `DEPLOY_RENDER.md` for detailed step-by-step instructions
- Render provides free HTTPS hosting with automatic deployments
- Your URL will be: `https://your-app-name.onrender.com`
- Configure your bot's Mini App URL in [@BotFather](https://t.me/BotFather) using `/newapp` command

5. Start the Flask web server:
```bash
python app.py
```

6. In a separate terminal, start the Telegram bot:
```bash
python bot.py
```

**Note:** For local development, you can use tools like [ngrok](https://ngrok.com/) to expose your local server:
```bash
ngrok http 5000
```
Then use the ngrok URL as your `WEB_APP_URL`.

## Usage

### Mini App Interface

The main interface is accessed through the Telegram Mini App. When users send `/start` to your bot, they'll see a button to open the Mini App. The Mini App provides:

- **Tasks Tab**: View assigned and available tasks, complete tasks to earn coins
- **Create Tab**: Create new tasks (costs 2 coins)
- **Referral Tab**: Get your referral link and see referral stats
- **Leaderboard Tab**: View top coin earners

### Bot Commands (Optional)

The bot also supports these commands for quick access:

- `/start` - Start the bot and open Mini App
- `/help` - Show all available commands
- `/balance` - Check your coin balance
- `/referral` - Get your referral link
- `/leaderboard` - View top coin earners

## Game Mechanics

- **Task Creation**: Costs 2 coins to create a task
- **Task Completion**: Earn coins based on the reward set by the task creator
- **Referral Bonus**: Earn 5 coins when someone joins using your referral link
- **Default Task Reward**: 10 coins (can be customized when creating tasks)

## Database

The bot uses SQLite to store:
- User information and coin balances
- Tasks and their assignments
- Transaction history
- Referral relationships

The database file (`bot.db`) will be created automatically on first run.

## License

MIT License


