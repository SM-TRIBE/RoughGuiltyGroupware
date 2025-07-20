
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from utils.tools import load_json, save_json

ACHIEVEMENTS = [
    {
        "id": "first_steps",
        "name": "قدم‌های اول",
        "description": "اولین بار وارد بازی شوید",
        "icon": "👶",
        "reward_xp": 50,
        "reward_money": 200,
        "condition": {"action": "login", "count": 1}
    },
    {
        "id": "social_butterfly", 
        "name": "پروانه اجتماعی",
        "description": "با 10 نفر ازدواج کنید",
        "icon": "🦋",
        "reward_xp": 500,
        "reward_money": 2000,
        "condition": {"action": "marriage", "count": 10}
    },
    {
        "id": "wealthy",
        "name": "ثروتمند",
        "description": "100,000 تومان جمع کنید",
        "icon": "💎",
        "reward_xp": 300,
        "reward_money": 5000,
        "condition": {"money": 100000}
    },
    {
        "id": "level_master",
        "name": "استاد سطوح",
        "description": "به سطح 20 برسید",
        "icon": "🏆",
        "reward_xp": 1000,
        "reward_money": 10000,
        "condition": {"level": 20}
    },
    {
        "id": "workaholic",
        "name": "کارمند نمونه",
        "description": "50 بار کار کنید",
        "icon": "💼",
        "reward_xp": 400,
        "reward_money": 3000,
        "condition": {"action": "work", "count": 50}
    },
    {
        "id": "explorer",
        "name": "کاوشگر",
        "description": "تمام مکان‌ها را بازدید کنید",
        "icon": "🗺️",
        "reward_xp": 350,
        "reward_money": 2500,
        "condition": {"action": "visit_all_locations", "count": 1}
    }
]

async def achievements_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("🏆 دستاوردهای من"), KeyboardButton("📜 همه دستاوردها")],
        [KeyboardButton("📊 پیشرفت"), KeyboardButton("🎁 دریافت جایزه")],
        [KeyboardButton("🏠 بازگشت به منو اصلی")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🏆 سیستم دستاوردها\n\n"
        "با انجام کارهای مختلف در بازی، دستاوردهای جدید باز کنید و جایزه بگیرید!",
        reply_markup=reply_markup
    )

async def my_achievements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    p = players.get(uid, {})
    
    unlocked_achievements = p.get("achievements", [])
    text = f"🏆 دستاوردهای {p.get('name', 'شما')}:\n\n"
    
    if not unlocked_achievements:
        text += "هنوز هیچ دستاوردی کسب نکرده‌اید!"
    else:
        for achievement_id in unlocked_achievements:
            achievement = next((a for a in ACHIEVEMENTS if a["id"] == achievement_id), None)
            if achievement:
                text += f"{achievement['icon']} {achievement['name']}\n"
                text += f"   {achievement['description']}\n\n"
    
    text += f"📊 مجموع: {len(unlocked_achievements)}/{len(ACHIEVEMENTS)}"
    
    await update.message.reply_text(text)

async def all_achievements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    p = players.get(uid, {})
    
    unlocked_achievements = p.get("achievements", [])
    text = "📜 تمام دستاوردها:\n\n"
    
    for achievement in ACHIEVEMENTS:
        status = "✅" if achievement["id"] in unlocked_achievements else "🔒"
        text += f"{status} {achievement['icon']} {achievement['name']}\n"
        text += f"   {achievement['description']}\n"
        text += f"   🎁 جایزه: {achievement['reward_xp']} XP + {achievement['reward_money']:,} تومان\n\n"
    
    await update.message.reply_text(text)

def check_achievements(player_id, action_type=None, action_count=None):
    """Check if player unlocked new achievements"""
    players = load_json('data/players.json')
    p = players.get(str(player_id), {})
    
    unlocked = p.get("achievements", [])
    newly_unlocked = []
    
    for achievement in ACHIEVEMENTS:
        if achievement["id"] in unlocked:
            continue
            
        # Check conditions
        unlocked_now = False
        condition = achievement["condition"]
        
        if "level" in condition:
            if p.get("level", 1) >= condition["level"]:
                unlocked_now = True
                
        elif "money" in condition:
            if p.get("money", 0) >= condition["money"]:
                unlocked_now = True
                
        elif "action" in condition:
            action_stats = p.get("action_stats", {})
            if action_type == condition["action"]:
                current_count = action_stats.get(action_type, 0) + (action_count or 1)
                if current_count >= condition["count"]:
                    unlocked_now = True
            elif action_stats.get(condition["action"], 0) >= condition["count"]:
                unlocked_now = True
        
        if unlocked_now:
            unlocked.append(achievement["id"])
            newly_unlocked.append(achievement)
            
            # Give rewards
            p["xp"] = p.get("xp", 0) + achievement["reward_xp"]
            p["money"] = p.get("money", 0) + achievement["reward_money"]
    
    p["achievements"] = unlocked
    players[str(player_id)] = p
    save_json('data/players.json', players)
    
    return newly_unlocked

async def notify_achievements(context, user_id, achievements):
    """Send notification about new achievements"""
    if not achievements:
        return
        
    for achievement in achievements:
        text = f"🎉 دستاورد جدید!\n\n"
        text += f"{achievement['icon']} {achievement['name']}\n"
        text += f"{achievement['description']}\n\n"
        text += f"🎁 جایزه دریافت شد:\n"
        text += f"• {achievement['reward_xp']} XP\n"
        text += f"• {achievement['reward_money']:,} تومان"
        
        try:
            await context.bot.send_message(user_id, text)
        except:
            pass
