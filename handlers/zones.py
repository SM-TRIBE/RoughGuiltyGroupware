
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from utils.tools import load_json, save_json
import random

LOCATIONS = {
    "مرکز شهر": {"description": "قلب پرتردد شهر", "charisma_bonus": 1, "events": ["meet_stranger", "find_money"]},
    "میدان توپخانه": {"description": "میدان تاریخی با کافه‌های سنتی", "charisma_bonus": 2, "events": ["tea_house", "poetry"]},
    "پاساژ علاءالدین": {"description": "بازار مدرن برای خرید", "charisma_bonus": 1, "events": ["shopping", "business"]},
    "پارک لاله": {"description": "فضای سبز برای آرامش", "intelligence_bonus": 2, "events": ["meditation", "reading"]},
    "کافه‌ی ادبی": {"description": "محل گردهمایی روشنفکران", "intelligence_bonus": 3, "events": ["poetry", "philosophy"]},
    "باشگاه ورزشی": {"description": "برای تقویت بدن", "strength_bonus": 3, "events": ["workout", "competition"]},
    "هتل پارس": {"description": "هتل لوکس شهر", "charisma_bonus": 4, "events": ["luxury", "networking"]},
    "بار زیرزمینی": {"description": "محل مخفی شبانه", "charisma_bonus": 3, "events": ["party", "secrets"]},
    "بازار تجریش": {"description": "بازار سنتی کوهپایه", "charisma_bonus": 2, "events": ["bargain", "culture"]},
    "دانشگاه تهران": {"description": "محیط علمی و دانشگاهی", "intelligence_bonus": 4, "events": ["study", "research"]}
}

async def travel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    locations = list(LOCATIONS.keys())
    
    for i in range(0, len(locations), 2):
        row = [KeyboardButton(locations[i])]
        if i + 1 < len(locations):
            row.append(KeyboardButton(locations[i + 1]))
        keyboard.append(row)
    
    keyboard.append([KeyboardButton("🏠 بازگشت به منو اصلی")])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🗺️ به کجا می‌خواهید بروید؟",
        reply_markup=reply_markup
    )

async def visit_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location_name = update.message.text
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    
    if location_name not in LOCATIONS:
        return
    
    location = LOCATIONS[location_name]
    p = players[uid]
    
    # Update player location
    p['location'] = location_name
    
    # Apply bonuses
    if 'charisma_bonus' in location:
        p['traits']['charisma'] += location['charisma_bonus']
    if 'intelligence_bonus' in location:
        p['traits']['intelligence'] += location['intelligence_bonus']
    if 'strength_bonus' in location:
        p['traits']['strength'] += location['strength_bonus']
    
    # Random event
    event = random.choice(location['events'])
    event_text = await handle_location_event(event, p)
    
    save_json('data/players.json', players)
    
    await update.message.reply_text(
        f"📍 شما به {location_name} رفتید.\n"
        f"📝 {location['description']}\n\n"
        f"🎭 {event_text}"
    )

async def handle_location_event(event, player):
    if event == "meet_stranger":
        player['social_points'] = player.get('social_points', 0) + 5
        return "شما با فرد جالبی آشنا شدید! (+5 امتیاز اجتماعی)"
    elif event == "find_money":
        money = random.randint(50, 200)
        player['money'] += money
        return f"پول پیدا کردید! (+{money} تومان)"
    elif event == "tea_house":
        player['happiness'] = player.get('happiness', 50) + 10
        return "چای خوشمزه‌ای نوشیدید و آرام شدید! (+10 شادی)"
    elif event == "poetry":
        player['culture_points'] = player.get('culture_points', 0) + 3
        return "شعری زیبا شنیدید! (+3 امتیاز فرهنگی)"
    elif event == "meditation":
        player['mental_health'] = player.get('mental_health', 50) + 15
        return "مدیتیشن کردید و آرامش یافتید! (+15 سلامت روان)"
    elif event == "workout":
        player['energy'] = player.get('energy', 100) - 20
        player['fitness'] = player.get('fitness', 50) + 10
        return "ورزش کردید! (-20 انرژی، +10 آمادگی جسمی)"
    else:
        return "چیز جالبی اتفاق نیفتاد."
