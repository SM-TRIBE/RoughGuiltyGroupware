from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID
import json

PLAYER_FILE = 'data/players.json'

async def god_speak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("فقط خدا اجازه دارد صحبت کند.")
        return

    if not context.args:
        await update.message.reply_text("استفاده: /god پیام شما")
        return

    msg = "📢 پیام خداوند:\n" + " ".join(context.args)

    with open(PLAYER_FILE, 'r') as f:
        players = json.load(f)

    for uid in players:
        try:
            await context.bot.send_message(chat_id=int(uid), text=msg)
        except Exception:
            continue

    await update.message.reply_text("پیام به تمام بندگان ارسال شد.")
