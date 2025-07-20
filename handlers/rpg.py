
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from utils.tools import load_json, save_json
import random
from datetime import datetime, timedelta

QUESTS = [
    {
        "id": "delivery_quest",
        "name": "پیک موتوری",
        "description": "بسته‌ای را به آدرس مقصد برسان",
        "reward_xp": 100,
        "reward_money": 300,
        "duration": 30,
        "requirements": {"level": 1}
    },
    {
        "id": "treasure_hunt",
        "name": "شکار گنج",
        "description": "گنج مخفی شده در شهر را پیدا کن",
        "reward_xp": 250,
        "reward_money": 800,
        "duration": 60,
        "requirements": {"level": 3, "intelligence": 7}
    },
    {
        "id": "fight_boss",
        "name": "مبارزه با رئیس",
        "description": "با رئیس محله مبارزه کن",
        "reward_xp": 500,
        "reward_money": 1500,
        "duration": 90,
        "requirements": {"level": 5, "strength": 10}
    }
]

DUNGEONS = [
    {
        "id": "subway_tunnel",
        "name": "تونل مترو",
        "difficulty": "آسان",
        "monsters": ["موش غول‌پیکر", "سایه تاریک"],
        "rewards": ["کلید طلایی", "نقشه گنج"]
    },
    {
        "id": "abandoned_factory",
        "name": "کارخانه متروکه",
        "difficulty": "متوسط",
        "monsters": ["ربات خراب", "روح کارگر"],
        "rewards": ["آهن قراضه", "دستگاه عتیقه"]
    }
]

async def quest_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("📜 مشاهده ماموریت‌ها"), KeyboardButton("⚔️ شروع ماموریت")],
        [KeyboardButton("🗂️ ماموریت‌های فعال"), KeyboardButton("🏆 تکمیل ماموریت")],
        [KeyboardButton("🏠 بازگشت به منو اصلی")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "⚔️ مرکز ماموریت‌ها\n\n"
        "در اینجا می‌توانید ماموریت‌های مختلف را انجام دهید و جایزه دریافت کنید!",
        reply_markup=reply_markup
    )

async def view_quests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    p = players.get(uid, {})
    
    text = "📜 ماموریت‌های موجود:\n\n"
    
    for quest in QUESTS:
        # Check requirements
        can_do = True
        req_text = ""
        
        if "level" in quest["requirements"]:
            if p.get("level", 1) < quest["requirements"]["level"]:
                can_do = False
            req_text += f"سطح {quest['requirements']['level']} | "
            
        if "intelligence" in quest["requirements"]:
            if p.get("traits", {}).get("intelligence", 5) < quest["requirements"]["intelligence"]:
                can_do = False
            req_text += f"هوش {quest['requirements']['intelligence']} | "
            
        if "strength" in quest["requirements"]:
            if p.get("traits", {}).get("strength", 5) < quest["requirements"]["strength"]:
                can_do = False
            req_text += f"قدرت {quest['requirements']['strength']} | "
        
        status = "✅" if can_do else "❌"
        text += f"{status} {quest['name']}\n"
        text += f"📖 {quest['description']}\n"
        text += f"🎁 جایزه: {quest['reward_xp']} XP + {quest['reward_money']} تومان\n"
        text += f"⏱️ مدت: {quest['duration']} دقیقه\n"
        text += f"📋 نیازمندی‌ها: {req_text.rstrip(' | ')}\n\n"
    
    await update.message.reply_text(text)

async def start_quest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    
    for quest in QUESTS:
        keyboard.append([KeyboardButton(f"شروع {quest['name']}")])
    
    keyboard.append([KeyboardButton("🏠 بازگشت به منو اصلی")])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "⚔️ کدام ماموریت را می‌خواهید شروع کنید؟",
        reply_markup=reply_markup
    )

async def dungeon_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("🗡️ ورود به سیاه‌چال"), KeyboardButton("🎒 تجهیزات")],
        [KeyboardButton("📊 آمار مبارزه"), KeyboardButton("🏥 درمانگاه")],
        [KeyboardButton("🏠 بازگشت به منو اصلی")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    text = "⚔️ سیاه‌چال‌های شهر\n\n"
    text += "در اینجا می‌توانید با هیولاها مبارزه کنید و آیتم‌های ارزشمند به دست آورید!\n\n"
    
    for dungeon in DUNGEONS:
        text += f"🏰 {dungeon['name']}\n"
        text += f"📊 سختی: {dungeon['difficulty']}\n"
        text += f"👹 هیولاها: {', '.join(dungeon['monsters'])}\n"
        text += f"🎁 جوایز: {', '.join(dungeon['rewards'])}\n\n"
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def battle_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    p = players.get(uid, {})
    
    if p.get("energy", 100) < 20:
        await update.message.reply_text("❌ انرژی کافی ندارید! برای بازیابی انرژی استراحت کنید.")
        return
    
    # Random battle
    monsters = ["سگ ولگرد", "دزد خیابانی", "موتور سوار مزاحم", "فروشنده مواد"]
    monster = random.choice(monsters)
    
    player_power = p.get("traits", {}).get("strength", 5) + p.get("level", 1) * 2
    monster_power = random.randint(5, 15)
    
    keyboard = [
        [KeyboardButton("⚔️ حمله"), KeyboardButton("🛡️ دفاع")],
        [KeyboardButton("💨 فرار"), KeyboardButton("🎒 استفاده از آیتم")],
        [KeyboardButton("🏠 بازگشت به منو اصلی")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    if player_power > monster_power:
        # Victory
        xp_gained = random.randint(30, 80)
        money_gained = random.randint(100, 300)
        
        p["xp"] = p.get("xp", 0) + xp_gained
        p["money"] = p.get("money", 0) + money_gained
        p["energy"] = max(0, p.get("energy", 100) - 15)
        
        # Check level up
        from utils.tools import check_level_up
        leveled_up = check_level_up(p)
        
        players[uid] = p
        save_json('data/players.json', players)
        
        result_text = f"🎉 پیروزی!\n\n"
        result_text += f"👹 شما {monster} را شکست دادید!\n"
        result_text += f"🎁 جوایز دریافتی:\n"
        result_text += f"   • {xp_gained} XP\n"
        result_text += f"   • {money_gained} تومان\n"
        
        if leveled_up:
            result_text += f"\n🎊 تبریک! شما به سطح {p['level']} رسیدید!"
        
        await update.message.reply_text(result_text, reply_markup=reply_markup)
    else:
        # Defeat
        money_lost = min(p.get("money", 0) // 10, 200)
        p["money"] = max(0, p.get("money", 0) - money_lost)
        p["energy"] = max(0, p.get("energy", 100) - 25)
        
        players[uid] = p
        save_json('data/players.json', players)
        
        result_text = f"💀 شکست!\n\n"
        result_text += f"👹 {monster} شما را شکست داد!\n"
        result_text += f"💸 {money_lost} تومان از دست دادید!\n"
        result_text += f"⚡ انرژی کم شد!"
        
        await update.message.reply_text(result_text, reply_markup=reply_markup)

async def inventory_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    p = players.get(uid, {})
    
    keyboard = [
        [KeyboardButton("🎒 مشاهده آیتم‌ها"), KeyboardButton("💊 استفاده از دارو")],
        [KeyboardButton("⚔️ تغییر سلاح"), KeyboardButton("🛡️ تغییر زره")],
        [KeyboardButton("📦 فروش آیتم"), KeyboardButton("🏠 بازگشت به منو اصلی")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    inventory = p.get("inventory", [])
    text = "🎒 کیف شما:\n\n"
    
    if not inventory:
        text += "کیف شما خالی است!"
    else:
        for item in inventory:
            text += f"• {item}\n"
    
    text += f"\n💰 پول: {p.get('money', 0):,} تومان"
    text += f"\n⚡ انرژی: {p.get('energy', 100)}/100"
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def skills_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    p = players.get(uid, {})
    
    keyboard = [
        [KeyboardButton("📈 ارتقاء مهارت"), KeyboardButton("📊 مشاهده مهارت‌ها")],
        [KeyboardButton("🎯 تمرین"), KeyboardButton("📚 آموزش")],
        [KeyboardButton("🏠 بازگشت به منو اصلی")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    traits = p.get("traits", {})
    text = f"⚡ مهارت‌های {p.get('name', 'بازیکن')}:\n\n"
    text += f"💪 قدرت: {traits.get('strength', 5)}/20\n"
    text += f"🧠 هوش: {traits.get('intelligence', 5)}/20\n"
    text += f"😎 جذابیت: {traits.get('charisma', 5)}/20\n"
    text += f"🏃 چابکی: {traits.get('agility', 5)}/20\n"
    text += f"🍀 شانس: {traits.get('luck', 5)}/20\n\n"
    text += f"📊 سطح: {p.get('level', 1)}\n"
    text += f"⭐ XP: {p.get('xp', 0)}\n"
    text += f"🎯 امتیاز مهارت باقی‌مانده: {p.get('skill_points', 0)}"
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def upgrade_skill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("💪 ارتقاء قدرت"), KeyboardButton("🧠 ارتقاء هوش")],
        [KeyboardButton("😎 ارتقاء جذابیت"), KeyboardButton("🏃 ارتقاء چابکی")],
        [KeyboardButton("🍀 ارتقاء شانس"), KeyboardButton("🏠 بازگشت")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "📈 کدام مهارت را می‌خواهید ارتقاء دهید؟\n"
        "هر ارتقاء 1 امتیاز مهارت می‌خواهد.",
        reply_markup=reply_markup
    )
