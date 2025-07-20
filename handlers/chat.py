
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from utils.tools import load_json, save_json
from datetime import datetime
import json

async def public_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("💬 ارسال پیام"), KeyboardButton("📖 خواندن پیام‌ها")],
        [KeyboardButton("🏠 بازگشت به منو اصلی")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🌟 خوش آمدید به کافه گپ!\n"
        "اینجا می‌توانید با دیگر بازیکنان چت کنید.",
        reply_markup=reply_markup
    )

async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💭 پیام خود را بنویسید:\n"
        "(پیام شما برای همه نمایش داده خواهد شد)"
    )
    context.user_data['waiting_for_message'] = True

async def receive_chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('waiting_for_message'):
        return
    
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    
    if uid not in players:
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    message_text = update.message.text
    player_name = players[uid]['name']
    
    # Load chat history
    try:
        with open('data/chat.json', 'r', encoding='utf-8') as f:
            chat_history = json.load(f)
    except:
        chat_history = []
    
    # Add new message
    new_message = {
        "player": player_name,
        "message": message_text,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "location": players[uid].get('location', 'نامشخص')
    }
    
    chat_history.append(new_message)
    
    # Keep only last 50 messages
    if len(chat_history) > 50:
        chat_history = chat_history[-50:]
    
    # Save chat history
    with open('data/chat.json', 'w', encoding='utf-8') as f:
        json.dump(chat_history, f, ensure_ascii=False, indent=2)
    
    context.user_data['waiting_for_message'] = False
    
    await update.message.reply_text(
        f"✅ پیام شما ارسال شد!\n"
        f"📍 از {players[uid].get('location', 'نامشخص')}"
    )

async def read_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open('data/chat.json', 'r', encoding='utf-8') as f:
            chat_history = json.load(f)
    except:
        await update.message.reply_text("هیچ پیامی موجود نیست.")
        return
    
    if not chat_history:
        await update.message.reply_text("هیچ پیامی موجود نیست.")
        return
    
    # Show last 10 messages
    recent_messages = chat_history[-10:]
    
    text = "💬 آخرین پیام‌های کافه گپ:\n\n"
    for msg in recent_messages:
        text += f"👤 {msg['player']} ({msg['location']}):\n"
        text += f"💭 {msg['message']}\n"
        text += f"🕐 {msg['timestamp']}\n\n"
    
    await update.message.reply_text(text)
