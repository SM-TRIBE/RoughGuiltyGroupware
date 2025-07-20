from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.tools import load_json, save_json
from random import randint

LOCATIONS = ["کافهٔ فضایی", "بار زیرزمینی", "پارک نئونی"]

async def explore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    p = players[uid]
    loc = choice(LOCATIONS)
    p['location'] = loc
    save_json('data/players.json', players)
    await update.message.reply_text(
        f"🏙️ شما به {loc} رفتید. اتفاقی در راه افتاد: ",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("همراه شو", callback_data='meet'),
             InlineKeyboardButton("برو دنبال کارت", callback_data='skip')]
        ])
    )
