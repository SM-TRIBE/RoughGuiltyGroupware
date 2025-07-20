# === FILE: handlers/leaderboard.py ===
from telegram import Update
from telegram.ext import ContextTypes
from utils.tools import load_json

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    players = load_json("data/players.json")

    if not players:
        await update.message.reply_text("هیچ بازیکنی در بازی ثبت‌نام نکرده است.")
        return

    top_players = sorted(players.items(), key=lambda x: x[1].get("money", 0), reverse=True)[:5]

    text = "🏆 ۵ بازیکن برتر از نظر دارایی:\n\n"
    for rank, (uid, pdata) in enumerate(top_players, start=1):
        name = pdata.get("name", "ناشناخته")
        money = pdata.get("money", 0)
        level = pdata.get("level", 1)
        text += f"{rank}. {name} — 💰 {money} تومان — سطح {level}\n"

    await update.message.reply_text(text)
