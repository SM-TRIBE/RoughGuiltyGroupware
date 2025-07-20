from telegram import Update
from telegram.ext import ContextTypes
from utils.tools import init_player, save_json, load_json

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    p = init_player(user)
    await update.message.reply_text(
        f"👋 سلام {p['name']}!\n"
        "برای تأیید سن و ورود به دنیای عشق‌یابی، لطفاً سن خود را وارد کنید."
    )


async def reply_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config import AGE_MIN
    user = update.effective_user
    age = int(update.message.text) if update.message.text.isdigit() else 0
    players = load_json('data/players.json')
    uid = str(user.id)
    if age >= AGE_MIN:
        players[uid]["age_confirmed"] = True
        save_json('data/players.json', players)
        await update.message.reply_text("✅ تأیید شد! حالا برای شروع بازی بنویس /profile")
    else:
        await update.message.reply_text("❌ متأسفانه سن کافی نیست.")
