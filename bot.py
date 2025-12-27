import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from database import Database
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize database
db = Database()

# Constants
REFERRAL_BONUS = 5.0  # Coins for referring someone
TASK_CREATION_COST = 2.0  # Coins to create a task
TASK_COMPLETION_REWARD = 10.0  # Default reward for completing a task

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    referral_code = context.args[0] if context.args else None
    
    # Get or create user
    db_user = db.get_or_create_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name
    )
    
    # Handle referral
    if referral_code and not db_user.referred_by:
        referrer = db.get_user_by_referral_code(referral_code)
        if referrer and referrer.id != db_user.id:
            session = db.get_session()
            try:
                db_user.referred_by = referrer.id
                session.add(db_user)
                session.commit()
                # Give bonus to referrer
                db.add_coins(referrer.id, REFERRAL_BONUS, 'referral_bonus', 
                           f'Referred user {user.first_name}')
                await context.bot.send_message(
                    chat_id=referrer.telegram_id,
                    text=f"🎉 You earned {REFERRAL_BONUS} coins for referring {user.first_name}!"
                )
            finally:
                session.close()
    
    # Get web app URL from environment or use default
    web_app_url = os.getenv('WEB_APP_URL', 'http://localhost:5000')
    
    welcome_text = f"""
🎮 Welcome to Tap Tap Task Game, {user.first_name}!

💰 Your Balance: {db_user.coins} coins

🎯 Tap the button below to open the Mini App and start managing tasks!
    """
    
    # Create keyboard with Web App button
    keyboard = [
        [InlineKeyboardButton("🎮 Open Mini App", web_app={"url": web_app_url})]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
📚 Commands Guide:

💰 Coins & Rewards:
/balance - Check your coin balance
/transactions - View your transaction history

📋 Tasks:
/create_task - Create a new task (costs 2 coins)
/my_tasks - View tasks assigned to you
/available_tasks - View tasks you can complete
/complete_task <task_id> - Complete a task

👥 Social:
/referral - Get your referral link
/leaderboard - View top coin earners

❓ Help:
/help - Show this help message
    """
    await update.message.reply_text(help_text)

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's coin balance"""
    user = update.effective_user
    db_user = db.get_or_create_user(telegram_id=user.id)
    
    text = f"💰 Your Balance: {db_user.coins} coins"
    await update.message.reply_text(text)

async def create_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create a new task"""
    user = update.effective_user
    db_user = db.get_or_create_user(telegram_id=user.id)
    
    if db_user.coins < TASK_CREATION_COST:
        await update.message.reply_text(
            f"❌ Insufficient coins! You need {TASK_CREATION_COST} coins to create a task.\n"
            f"Your balance: {db_user.coins} coins"
        )
        return
    
    # Check if user provided task details
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "📝 To create a task, use:\n"
            "/create_task <title> <description> <reward_coins>\n\n"
            "Example:\n"
            "/create_task Review Code Please review my code and give feedback 15"
        )
        return
    
    try:
        title = context.args[0]
        description = ' '.join(context.args[1:-1]) if len(context.args) > 2 else context.args[1]
        reward = float(context.args[-1]) if len(context.args) > 2 and context.args[-1].replace('.', '').isdigit() else TASK_COMPLETION_REWARD
        
        session = db.get_session()
        try:
            from database import Task
            task = Task(
                title=title,
                description=description,
                created_by=db_user.id,
                reward_coins=reward
            )
            session.add(task)
            
            # Deduct coins
            db_user.coins -= TASK_CREATION_COST
            from database import Transaction
            transaction = Transaction(
                user_id=db_user.id,
                amount=-TASK_CREATION_COST,
                transaction_type='task_creation',
                description=f'Created task: {title}'
            )
            session.add(transaction)
            
            session.commit()
            session.refresh(task)
            
            await update.message.reply_text(
                f"✅ Task created!\n\n"
                f"📋 Task ID: {task.id}\n"
                f"📝 Title: {title}\n"
                f"📄 Description: {description}\n"
                f"💰 Reward: {reward} coins\n\n"
                f"Share this task ID with others to assign it!"
            )
        finally:
            session.close()
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        await update.message.reply_text("❌ Error creating task. Please try again.")

async def assign_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Assign a task to a user"""
    user = update.effective_user
    
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "📋 To assign a task, use:\n"
            "/assign_task <task_id> <user_id>\n\n"
            "Or reply to a message with:\n"
            "/assign_task <task_id>"
        )
        return
    
    try:
        task_id = int(context.args[0])
        target_user_id = int(context.args[1]) if len(context.args) > 1 else None
        
        # If replying to a message, get that user's ID
        if update.message.reply_to_message:
            target_user_id = update.message.reply_to_message.from_user.id
        
        if not target_user_id:
            await update.message.reply_text("❌ Please specify a user ID or reply to a message.")
            return
        
        session = db.get_session()
        try:
            from database import Task, User
            task = session.query(Task).filter_by(id=task_id).first()
            target_user = db.get_or_create_user(telegram_id=target_user_id)
            
            if not task:
                await update.message.reply_text("❌ Task not found!")
                return
            
            if task.completed:
                await update.message.reply_text("❌ This task is already completed!")
                return
            
            task.assigned_to = target_user.id
            session.commit()
            
            await context.bot.send_message(
                chat_id=target_user_id,
                text=f"📋 New Task Assigned!\n\n"
                     f"📝 Title: {task.title}\n"
                     f"📄 Description: {task.description}\n"
                     f"💰 Reward: {task.reward_coins} coins\n\n"
                     f"Use /complete_task {task.id} to complete it!"
            )
            
            await update.message.reply_text(f"✅ Task {task_id} assigned to user {target_user_id}!")
        finally:
            session.close()
    except ValueError:
        await update.message.reply_text("❌ Invalid task ID or user ID!")
    except Exception as e:
        logger.error(f"Error assigning task: {e}")
        await update.message.reply_text("❌ Error assigning task. Please try again.")

async def my_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's assigned tasks"""
    user = update.effective_user
    db_user = db.get_or_create_user(telegram_id=user.id)
    
    session = db.get_session()
    try:
        from database import Task
        tasks = session.query(Task).filter_by(assigned_to=db_user.id, completed=False).all()
        
        if not tasks:
            await update.message.reply_text("📋 You have no assigned tasks.")
            return
        
        text = "📋 Your Tasks:\n\n"
        for task in tasks:
            text += f"🆔 Task ID: {task.id}\n"
            text += f"📝 Title: {task.title}\n"
            text += f"📄 Description: {task.description}\n"
            text += f"💰 Reward: {task.reward_coins} coins\n"
            text += f"📅 Created: {task.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
        
        await update.message.reply_text(text)
    finally:
        session.close()

async def available_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available tasks"""
    user = update.effective_user
    db_user = db.get_or_create_user(telegram_id=user.id)
    
    session = db.get_session()
    try:
        from database import Task
        tasks = session.query(Task).filter_by(assigned_to=None, completed=False).all()
        
        if not tasks:
            await update.message.reply_text("📋 No available tasks at the moment.")
            return
        
        text = "📋 Available Tasks:\n\n"
        for task in tasks:
            text += f"🆔 Task ID: {task.id}\n"
            text += f"📝 Title: {task.title}\n"
            text += f"📄 Description: {task.description}\n"
            text += f"💰 Reward: {task.reward_coins} coins\n\n"
        
        text += "Use /assign_task <task_id> <your_user_id> to assign a task to yourself!"
        await update.message.reply_text(text)
    finally:
        session.close()

async def complete_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Complete a task"""
    user = update.effective_user
    db_user = db.get_or_create_user(telegram_id=user.id)
    
    if not context.args:
        await update.message.reply_text("❌ Please provide a task ID:\n/complete_task <task_id>")
        return
    
    try:
        task_id = int(context.args[0])
        session = db.get_session()
        try:
            from database import Task
            task = session.query(Task).filter_by(id=task_id).first()
            
            if not task:
                await update.message.reply_text("❌ Task not found!")
                return
            
            if task.completed:
                await update.message.reply_text("❌ This task is already completed!")
                return
            
            if task.assigned_to != db_user.id:
                await update.message.reply_text("❌ This task is not assigned to you!")
                return
            
            # Mark task as completed
            task.completed = True
            task.completed_at = datetime.utcnow()
            session.commit()
            
            # Give reward
            new_balance = db.add_coins(
                db_user.id,
                task.reward_coins,
                'task_reward',
                f'Completed task: {task.title}'
            )
            
            await update.message.reply_text(
                f"✅ Task completed!\n\n"
                f"💰 You earned {task.reward_coins} coins!\n"
                f"💵 New balance: {new_balance} coins"
            )
            
            # Notify task creator
            if task.created_by != db_user.id:
                from database import User
                creator = session.query(User).filter_by(id=task.created_by).first()
                if creator:
                    await context.bot.send_message(
                        chat_id=creator.telegram_id,
                        text=f"🎉 Your task '{task.title}' has been completed by {user.first_name}!"
                    )
        finally:
            session.close()
    except ValueError:
        await update.message.reply_text("❌ Invalid task ID!")
    except Exception as e:
        logger.error(f"Error completing task: {e}")
        await update.message.reply_text("❌ Error completing task. Please try again.")

async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's referral link"""
    user = update.effective_user
    db_user = db.get_or_create_user(telegram_id=user.id)
    
    bot_username = context.bot.username
    referral_link = f"https://t.me/{bot_username}?start={db_user.referral_code}"
    
    text = f"""
🔗 Your Referral Link:

{referral_link}

👥 Share this link with friends!
💰 You'll earn {REFERRAL_BONUS} coins when someone joins using your link!
    """
    
    await update.message.reply_text(text)

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show leaderboard"""
    session = db.get_session()
    try:
        from database import User
        top_users = session.query(User).order_by(User.coins.desc()).limit(10).all()
        
        if not top_users:
            await update.message.reply_text("📊 No users yet!")
            return
        
        text = "🏆 Top Coin Earners:\n\n"
        for i, user in enumerate(top_users, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            name = user.first_name or user.username or f"User {user.telegram_id}"
            text += f"{medal} {name}: {user.coins} coins\n"
        
        await update.message.reply_text(text)
    finally:
        session.close()

async def transactions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's transaction history"""
    user = update.effective_user
    db_user = db.get_or_create_user(telegram_id=user.id)
    
    session = db.get_session()
    try:
        from database import Transaction
        transactions = session.query(Transaction).filter_by(user_id=db_user.id).order_by(Transaction.created_at.desc()).limit(10).all()
        
        if not transactions:
            await update.message.reply_text("📊 No transactions yet!")
            return
        
        text = "📊 Recent Transactions:\n\n"
        for txn in transactions:
            sign = "+" if txn.amount > 0 else ""
            text += f"{sign}{txn.amount} coins - {txn.transaction_type}\n"
            if txn.description:
                text += f"   {txn.description}\n"
            text += f"   {txn.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
        
        await update.message.reply_text(text)
    finally:
        session.close()

def main():
    """Start the bot"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        return
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("create_task", create_task))
    application.add_handler(CommandHandler("assign_task", assign_task))
    application.add_handler(CommandHandler("my_tasks", my_tasks))
    application.add_handler(CommandHandler("available_tasks", available_tasks))
    application.add_handler(CommandHandler("complete_task", complete_task))
    application.add_handler(CommandHandler("referral", referral))
    application.add_handler(CommandHandler("leaderboard", leaderboard))
    application.add_handler(CommandHandler("transactions", transactions))
    
    # Start bot
    logger.info("Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

