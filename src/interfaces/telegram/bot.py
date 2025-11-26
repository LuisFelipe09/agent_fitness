import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from src.infrastructure.database import SessionLocal
from src.infrastructure.repositories import SqlAlchemyUserRepository
from src.application.services import UserService

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Register user if not exists
    db = SessionLocal()
    user_repo = SqlAlchemyUserRepository(db)
    user_service = UserService(user_repo)
    
    # Register user (will create with CLIENT role by default)
    registered_user = user_service.register_user(str(user.id), user.username or "Unknown")
    
    # Check if user should be an admin
    admin_ids_str = os.getenv("ADMIN_TELEGRAM_IDS", "")
    admin_ids = [id.strip() for id in admin_ids_str.split(",") if id.strip()]
    
    if str(user.id) in admin_ids:
        # Assign admin role if not already present
        if "admin" not in registered_user.roles:
            registered_user.roles.append("admin")
            user_repo.update(registered_user)
            logging.info(f"Assigned ADMIN role to user {user.id}")
    
    db.close()
    
    # Show user their roles
    roles_display = ", ".join(registered_user.roles).upper()
    role_message = f"\n\n🎭 Your roles: {roles_display}"

    # Create a button to open the Mini App
    # Replace URL with the actual URL where the frontend is hosted
    # For local development, this might need a tunnel like ngrok
    web_app_url = os.getenv("WEB_APP_URL", "https://google.com") 
    
    keyboard = [
        [InlineKeyboardButton("Open Fitness App", web_app=WebAppInfo(url=web_app_url))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Hello {user.first_name}! Welcome to your AI Fitness Agent.{role_message}\n\nClick the button below to manage your plans.",
        reply_markup=reply_markup
    )

def run_bot():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN not found in environment variables.")
        return

    application = ApplicationBuilder().token(token).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    run_bot()
