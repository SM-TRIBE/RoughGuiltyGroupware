from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.tools import load_json, save_json

async def choice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    uid = str(query.from_user.id)
    players = load_json('data/players.json')
    p = players[uid]
    candidate = context.user_data.get('cand')
    if data == 'accept':
        p['partner'] = candidate['name']
        save_json('data/players.json', players)
        await query.edit_message_text(f"🎉 شما اکنون با {candidate['name']} شریک شدید!")
    else:
        await query.edit_message_text("😢 متأسفانه پیشنهاد رد شد.")
