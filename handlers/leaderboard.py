
from telegram import Update
from telegram.ext import ContextTypes
from utils.tools import load_json

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    players = load_json('data/players.json')
    
    if not players:
        await update.message.reply_text("هیچ بازیکنی ثبت نشده است.")
        return
    
    # Sort by level, then XP, then money
    sorted_players = sorted(
        players.items(),
        key=lambda x: (x[1].get('level', 1), x[1].get('xp', 0), x[1].get('money', 0)),
        reverse=True
    )
    
    text = "🏆 جدول امتیازات:\n\n"
    for i, (uid, player) in enumerate(sorted_players[:10], 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        text += f"{medal} {player['name']}\n"
        text += f"   سطح {player.get('level', 1)} | {player.get('xp', 0)} XP | {player.get('money', 0)} تومان\n\n"
    
    await update.message.reply_text(text)

async def wealth_board(update: Update, context: ContextTypes.DEFAULT_TYPE):
    players = load_json('data/players.json')
    
    sorted_players = sorted(
        players.items(),
        key=lambda x: x[1].get('money', 0),
        reverse=True
    )
    
    text = "💰 ثروتمندترین‌ها:\n\n"
    for i, (uid, player) in enumerate(sorted_players[:10], 1):
        text += f"{i}. {player['name']} - {player.get('money', 0)} تومان\n"
    
    await update.message.reply_text(text)
