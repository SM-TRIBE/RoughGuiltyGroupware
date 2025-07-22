import asyncio
import logging
import os

from flask import Flask, request, abort
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# main.py - NEW
from db.database import setup_database
from handlers import (
    achievements, admin, adult_scene, chat, choices, dating, economy,
    explore, god, hotel, jobs, leaderboard, leveling, marriage,
    minigames, missing_handlers, notifications, partner, profile, rpg,
    shop, social, start, temple, zones
)

# --- Configuration ---
# Load environment variables.
TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')
# This is the base URL of your Render web service, e.g., "https://your-app-name.onrender.com"
# You MUST set this as an environment variable in your Render dashboard.
WEB_APP_URL = os.getenv('WEB_APP_URL')

if not all([TOKEN, ADMIN_ID, WEB_APP_URL]):
    raise ValueError("Essential environment variables are missing (BOT_TOKEN, ADMIN_ID, WEB_APP_URL)")

# --- Initialization ---
logging.basicConfig(level=logging.INFO)

# Bot and Dispatcher
bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Flask App for Webhook
app = Flask(__name__)

# --- Webhook Setup ---
# A secret path to receive updates from Telegram. Using the token makes it unique and secure.
WEBHOOK_PATH = f"/bot/{TOKEN}"
WEBHOOK_URL = f"{WEB_APP_URL}{WEBHOOK_PATH}"

# --- Bot Handlers and Logic ---
async def on_startup(dispatcher: Dispatcher):
    """
    Actions to perform on bot startup.
    This includes setting the webhook and initializing the database and scheduler.
    """
    logging.warning("Configuring webhook...")
    await bot.set_webhook(url=WEBHOOK_URL)
    logging.warning(f"Webhook set to {WEBHOOK_URL}")

    logging.warning("Initializing database...")
  await setup_database()
    logging.warning("Database initialized.")

    logging.warning("Setting up scheduler...")
    scheduler = AsyncIOScheduler()
    # Schedule the notification check to run every minute
    scheduler.add_job(notifications.check_and_send_notifications, 'interval', minutes=1, args=(bot,))
    scheduler.start()
    logging.warning("Scheduler started.")
    logging.warning("Bot is up and running!")

async def on_shutdown(dispatcher: Dispatcher):
    """
    Actions to perform on bot shutdown.
    """
    logging.warning('Shutting down...')
    # Gracefully close the bot session and remove the webhook.
    await bot.session.close()
    await bot.delete_webhook()
    logging.warning('Webhook removed. Shutdown complete.')

# Register all your command and message handlers (routers)
dp.include_routers(
    admin.router,
    start.router,
    profile.router,
    rpg.router,
    social.router,
    marriage.router,
    partner.router,
    economy.router,
    shop.router,
    jobs.router,
    explore.router,
    zones.router,
    leaderboard.router,
    leveling.router,
    achievements.router,
    minigames.router,
    chat.router,
    dating.router,
    temple.router,
    hotel.router,
    god.router,
    choices.router,
    adult_scene.router,
    # The 'missing_handlers' router should always be last to act as a fallback.
    missing_handlers.router
)

# Register startup and shutdown logic
dp.startup.register(on_startup)
dp.shutdown.register(on_shutdown)

# --- Flask Web Server ---
@app.route(WEBHOOK_PATH, methods=['POST'])
async def webhook_endpoint():
    """
    This is the main endpoint that receives updates from Telegram.
    """
    telegram_update = types.Update.model_validate_json(
        request.get_data().decode('utf-8'),
        context={"bot": bot}
    )
    await dp.feed_update(bot=bot, update=telegram_update)
    return 'ok', 200

@app.route('/')
def index():
    """
    A simple health check endpoint to confirm the web service is running.
    """
    return "<h1>Your bot is running!</h1>", 200

if __name__ == '__main__':
    # This block is for local development and debugging.
    # It will not be used when deploying with a production server like Gunicorn.
    logging.basicConfig(level=logging.INFO)
    asyncio.run(on_startup(dp)) # Manually run startup logic for local testing
    try:
        # Start the Flask app
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)
    finally:
        asyncio.run(on_shutdown(dp)) # Manually run shutdown logic
