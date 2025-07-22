# Main application file. Initializes the bot, web server, and handlers.
import asyncio
import logging
import os

from flask import Flask, request
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from dotenv import load_dotenv

# --- Local Imports ---
import config
from db import database
from handlers import (
    start_handler, profile_handler, explore_handler,
    jobs_handler, social_handler, admin_handler,
    shop_handler, inventory_handler
)
from utils.scheduler import setup_scheduler

# --- Configuration & Initialization ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# --- Flask App for Webhook ---
app = Flask(__name__)
WEBHOOK_PATH = f"/bot/{config.BOT_TOKEN}"
WEBHOOK_URL = f"{config.WEB_APP_URL}{WEBHOOK_PATH}"

@app.route(WEBHOOK_PATH, methods=['POST'])
async def webhook_endpoint():
    """Receives updates from Telegram."""
    telegram_update = types.Update.model_validate_json(
        request.get_data().decode('utf-8'),
        context={"bot": bot}
    )
    await dp.feed_update(bot=bot, update=telegram_update)
    return 'ok', 200

@app.route('/')
def health_check():
    """A simple endpoint to confirm the web service is live."""
    return "<h1>شهرستان وحشی زنده است!</h1>", 200

# --- Bot Lifecycle ---
async def on_startup(dispatcher: Dispatcher):
    """Actions on bot startup."""
    logging.info("Connecting to database...")
    await database.connect()
    logging.info("Setting up scheduler...")
    await setup_scheduler(bot)
    logging.info("Setting webhook...")
    await bot.set_webhook(url=WEBHOOK_URL)
    logging.info(f"Bot started! Webhook is set to {WEBHOOK_URL}")

async def on_shutdown(dispatcher: Dispatcher):
    """Actions on bot shutdown."""
    logging.warning('Shutting down...')
    await database.disconnect()
    await bot.delete_webhook()
    logging.warning('Bot stopped.')

def main():
    """Configures and includes all routers."""
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Register all feature routers
    dp.include_routers(
        admin_handler.router,
        start_handler.router,
        profile_handler.router,
        explore_handler.router,
        jobs_handler.router,
        social_handler.router,
        shop_handler.router,
        inventory_handler.router
    )
    logging.info("All routers included.")

if __name__ == '__main__':
    main()
    # On Render, Gunicorn runs the 'app' object directly.
    # This block is for local development using polling.
    logging.info("Starting bot in polling mode for local development.")
    # To run locally, comment out the webhook lines in on_startup and run this file.
    # dp.run_polling(bot)
```python
