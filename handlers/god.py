from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_ID
from utils.tools import load_json

async def god_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("فقط خدا مجاز است.")
        return
    msg = "🔱 پیام خداوند:\n" + " ".join(context.args)
    players = load_json('data/players.json')
    for uid in players:
        try:
            await context.bot.send_message(int(uid), msg)
        except:
            pass
    await update.message.reply_text("پیام الهی ارسال شد.")
