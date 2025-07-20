
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from utils.tools import load_json, save_json
import random

HOTEL_SERVICES = {
    "اتاق معمولی": {"cost": 200, "energy_restore": 50, "description": "اتاق ساده برای استراحت"},
    "سوئیت لوکس": {"cost": 500, "energy_restore": 100, "happiness_bonus": 20, "description": "اتاق مجلل با امکانات کامل"},
    "اتاق VIP": {"cost": 1000, "energy_restore": 100, "happiness_bonus": 30, "charisma_bonus": 5, "description": "بهترین اتاق هتل با خدمات ویژه"},
    "سالن مهمانی": {"cost": 800, "description": "برای برگزاری مهمانی خصوصی", "social_bonus": 15}
}

async def hotel_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("🛏️ رزرو اتاق"), KeyboardButton("🍽️ رستوران هتل")],
        [KeyboardButton("🎉 سالن مهمانی"), KeyboardButton("💆 اسپا و ماساژ")],
        [KeyboardButton("🏠 بازگشت به منو اصلی")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🏨 خوش آمدید به هتل پارس!\n"
        "بهترین خدمات شهر را ارائه می‌دهیم.",
        reply_markup=reply_markup
    )

async def book_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for room_type, details in HOTEL_SERVICES.items():
        if "energy_restore" in details:
            keyboard.append([KeyboardButton(f"{room_type} - {details['cost']} تومان")])
    
    keyboard.append([KeyboardButton("🚪 بازگشت")])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    text = "🛏️ انواع اتاق‌های موجود:\n\n"
    for room_type, details in HOTEL_SERVICES.items():
        if "energy_restore" in details:
            text += f"🏠 {room_type}\n"
            text += f"💰 قیمت: {details['cost']} تومان\n"
            text += f"📝 {details['description']}\n"
            text += f"⚡ بازیابی انرژی: +{details['energy_restore']}\n"
            if 'happiness_bonus' in details:
                text += f"😊 شادی: +{details['happiness_bonus']}\n"
            if 'charisma_bonus' in details:
                text += f"✨ جذابیت: +{details['charisma_bonus']}\n"
            text += "\n"
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def hotel_restaurant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    
    foods = [
        {"name": "چلو کباب کوبیده", "cost": 150, "energy": 30, "happiness": 10},
        {"name": "فیله مرغ زعفرانی", "cost": 120, "energy": 25, "happiness": 8},
        {"name": "خورشت فیسنجان", "cost": 100, "energy": 20, "happiness": 12},
        {"name": "آش رشته", "cost": 80, "energy": 15, "happiness": 5},
        {"name": "بستنی زعفرانی", "cost": 50, "energy": 10, "happiness": 15}
    ]
    
    keyboard = []
    for food in foods:
        keyboard.append([KeyboardButton(f"{food['name']} - {food['cost']} تومان")])
    
    keyboard.append([KeyboardButton("🚪 بازگشت")])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    text = "🍽️ منوی رستوران هتل:\n\n"
    for food in foods:
        text += f"🍽️ {food['name']}\n"
        text += f"💰 {food['cost']} تومان | ⚡ +{food['energy']} انرژی | 😊 +{food['happiness']} شادی\n\n"
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def spa_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    
    services = [
        {"name": "ماساژ ریلکس", "cost": 300, "energy": 40, "mental_health": 20},
        {"name": "ماساژ درمانی", "cost": 500, "energy": 60, "mental_health": 30, "strength": 5},
        {"name": "فیشال صورت", "cost": 400, "charisma": 8, "happiness": 15},
        {"name": "ساونا", "cost": 200, "energy": 30, "mental_health": 15}
    ]
    
    keyboard = []
    for service in services:
        keyboard.append([KeyboardButton(f"{service['name']} - {service['cost']} تومان")])
    
    keyboard.append([KeyboardButton("🚪 بازگشت")])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    text = "💆 خدمات اسپا:\n\n"
    for service in services:
        text += f"💆 {service['name']}\n"
        text += f"💰 {service['cost']} تومان\n"
        if 'energy' in service:
            text += f"⚡ +{service['energy']} انرژی\n"
        if 'mental_health' in service:
            text += f"🧠 +{service['mental_health']} سلامت روان\n"
        if 'charisma' in service:
            text += f"✨ +{service['charisma']} جذابیت\n"
        if 'happiness' in service:
            text += f"😊 +{service['happiness']} شادی\n"
        text += "\n"
    
    await update.message.reply_text(text, reply_markup=reply_markup)
