# === FILE: handlers/economy.py ===
from telegram import Update
from telegram.ext import ContextTypes
from utils.tools import load_json, save_json
import random

async def give_daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    players = load_json("data/players.json")

    if user_id not in players:
        await update.message.reply_text("لطفاً ابتدا /start را بزنید.")
        return

    daily_amount = 500
    players[user_id]["money"] += daily_amount
    save_json("data/players.json", players)
    await update.message.reply_text(f"💰 جایزه روزانه: {daily_amount} تومان دریافت شد.")

async def do_job(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    players = load_json("data/players.json")

    if user_id not in players:
        await update.message.reply_text("لطفاً ابتدا /start را بزنید.")
        return

    income = random.randint(100, 500)
    players[user_id]["money"] += income
    save_json("data/players.json", players)

    await update.message.reply_text(f"💼 شما کار کردید و {income} تومان دریافت کردید.")
