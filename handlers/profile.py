from telegram import Update
from telegram.ext import ContextTypes
from utils.tools import load_json

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    p = players.get(uid)
    if not p:
        await update.message.reply_text("پروفایلی نیست. لطفاً /start")
        return
    if not p["age_confirmed"]:
        await update.message.reply_text("لطفاً ابتدا سن‌تان را تأیید کنید.")
        return
    text = f"👤 پروفایل شما:\nنام: {p['name']}\n"
    text += f"محل: {p['location']}\nشریک کنونی: {p['partner'] or 'ندارد'}\n"
    text += "ویژگی‌‌ها:\n"
    for k,v in p["traits"].items():
        text += f" — {k}: {v}\n"
    if p["inventory"]:
        text += f"📦 آیتم‌ها: {', '.join(p['inventory'])}"
    await update.message.reply_text(text)
