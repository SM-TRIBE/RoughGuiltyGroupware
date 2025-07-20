from telegram import Update
from telegram.ext import ContextTypes
from utils.tools import load_json

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    p = players.get(uid)
    
    if not p:
        await update.message.reply_text("پروفایلی موجود نیست. لطفاً /start کنید.")
        return
    
    if not p.get("approved"):
        await update.message.reply_text("لطفاً ابتدا تأیید پروفایل را انتظار بکشید.")
        return
    
    traits_text = ""
    for trait, value in p.get("traits", {}).items():
        persian_names = {
            "charisma": "جذابیت",
            "intelligence": "هوش", 
            "strength": "قدرت",
            "agility": "چابکی",
            "luck": "شانس"
        }
        persian_name = persian_names.get(trait, trait)
        traits_text += f"• {persian_name}: {value}\n"
    
    text = f"👤 پروفایل {p['name']}\n\n"
    text += f"🎂 سن: {p.get('age', 'نامشخص')}\n"
    text += f"📍 مکان: {p.get('location', 'میدان اصلی')}\n"
    text += f"💰 پول: {p.get('money', 0):,} تومان\n"
    text += f"⭐ سطح: {p.get('level', 1)}\n"
    text += f"💍 شریک: {p.get('partner') or 'ندارد'}\n"
    text += f"💼 شغل: {p.get('job') or 'بیکار'}\n\n"
    text += f"📊 ویژگی‌ها:\n{traits_text}\n"
    
    if p.get("inventory"):
        text += f"🎒 آیتم‌ها: {', '.join(p['inventory'])}\n"
    
    if p.get("bio"):
        text += f"\n📝 توضیحات: {p['bio']}"
    
    await update.message.reply_text(text)
