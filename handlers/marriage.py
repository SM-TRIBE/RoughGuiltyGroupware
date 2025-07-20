
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from utils.tools import load_json, save_json
import random

async def marry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    
    if uid not in players:
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    p = players[uid]
    if not p.get("age_confirmed"):
        await update.message.reply_text("ابتدا سن خود را تأیید کنید.")
        return
    
    if p.get("partner"):
        await update.message.reply_text(f"شما قبلاً با {p['partner']} ازدواج کرده‌اید!")
        return
    
    # Find potential partners
    partners = load_json('data/partners.json')
    available = [p for p in partners if p.get("available", True)]
    
    if not available:
        await update.message.reply_text("هیچ شریک مناسبی در حال حاضر موجود نیست.")
        return
    
    partner = random.choice(available)
    
    keyboard = [
        [KeyboardButton("💍 پیشنهاد ازدواج"), KeyboardButton("❌ انصراف")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        f"شما {partner['name']} را ملاقات کردید.\n"
        f"توضیحات: {partner['description']}\n"
        f"ویژگی‌ها: جذابیت {partner['charisma']}, هوش {partner['intelligence']}\n"
        "چه کاری انجام می‌دهید؟",
        reply_markup=reply_markup
    )
    
    context.user_data['potential_partner'] = partner

async def propose_marriage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    
    partner = context.user_data.get('potential_partner')
    if not partner:
        await update.message.reply_text("هیچ شریک پیشنهادی ندارید.")
        return
    
    # Check compatibility
    p = players[uid]
    success_chance = min(90, (p['traits']['charisma'] + p['traits']['intelligence']) * 5)
    
    if random.randint(1, 100) <= success_chance:
        players[uid]['partner'] = partner['name']
        players[uid]['happiness'] = players[uid].get('happiness', 50) + 30
        save_json('data/players.json', players)
        
        await update.message.reply_text(
            f"🎉 تبریک! شما با {partner['name']} ازدواج کردید!\n"
            f"شادی شما افزایش یافت!"
        )
    else:
        await update.message.reply_text(
            f"😢 متأسفانه {partner['name']} پیشنهاد شما را رد کرد.\n"
            "سعی کنید جذابیت و هوش خود را افزایش دهید."
        )

async def divorce(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    
    p = players[uid]
    if not p.get("partner"):
        await update.message.reply_text("شما ازدواج نکرده‌اید!")
        return
    
    partner_name = p['partner']
    players[uid]['partner'] = None
    players[uid]['happiness'] = max(0, players[uid].get('happiness', 50) - 20)
    players[uid]['money'] = max(0, players[uid]['money'] - 500)  # Divorce cost
    save_json('data/players.json', players)
    
    await update.message.reply_text(
        f"😔 شما از {partner_name} طلاق گرفتید.\n"
        f"هزینه طلاق: 500 تومان\n"
        f"شادی شما کاهش یافت."
    )
