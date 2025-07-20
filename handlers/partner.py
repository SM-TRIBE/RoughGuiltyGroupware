from telegram import Update
from telegram.ext import ContextTypes
from utils.tools import load_json, save_json, pick_random_partner

async def find_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json('data/players.json')
    partners_data = load_json('data/partners.json')
    uid = str(user.id)
    p = players[uid]
    if not p["age_confirmed"]:
        await update.message.reply_text("ابتدا سن‌تان را تأیید کنید.")
        return
    candidate = pick_random_partner(uid)
    if not candidate:
        await update.message.reply_text("فعلاً کسی برای ملاقات نیست. بعداً امتحان کن.")
        return
    # store candidate
    context.user_data['cand'] = candidate
    await update.message.reply_text(
        f"این فرد را ملاقات کن: {candidate['name']}؛ علاقه‌مند به ملاقات؟",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("بله 💖", callback_data='accept'),
             InlineKeyboardButton("نه ❌", callback_data='reject')]
        ])
    )

async def reply_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # optional user free text replies to partner
    await update.message.reply_text("از /findpartner استفاده کن برای شروع.")
