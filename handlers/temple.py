
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.tools import load_json, save_json
import random
from datetime import datetime
from config import ADMIN_ID

DIVINE_REWARDS = {
    "blessing": {"money": 1000, "xp": 100, "trait_boost": 2},
    "miracle": {"money": 5000, "xp": 500, "trait_boost": 5},
    "divine_gift": {"money": 10000, "xp": 1000, "trait_boost": 10}
}

PRAYER_TYPES = {
    "🙏 دعای سلامتی": {"cost": 0, "effect": "health_boost"},
    "💰 دعای روزی": {"cost": 100, "effect": "money_boost"},
    "🧠 دعای هوش": {"cost": 200, "effect": "intelligence_boost"},
    "💪 دعای قدرت": {"cost": 200, "effect": "strength_boost"},
    "❤️ دعای عشق": {"cost": 300, "effect": "charisma_boost"},
    "🍀 دعای شانس": {"cost": 400, "effect": "luck_boost"}
}

DIVINE_QUESTS = [
    {
        "id": "charity",
        "name": "خیرات به نیازمندان",
        "description": "1000 تومان به خیریه اهدا کنید",
        "cost": 1000,
        "reward": "divine_blessing"
    },
    {
        "id": "wisdom",
        "name": "جستجوی دانش",
        "description": "10 کتاب مطالعه کنید",
        "requirement": "books_read:10",
        "reward": "wisdom_boost"
    },
    {
        "id": "kindness",
        "name": "مهربانی با دیگران",
        "description": "به 5 نفر هدیه بدهید",
        "requirement": "gifts_given:5",
        "reward": "karma_boost"
    }
]

async def temple_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    keyboard = [
        [KeyboardButton("🙏 دعا و نیایش"), KeyboardButton("💬 صحبت با خداوند")],
        [KeyboardButton("📿 طلب آمرزش"), KeyboardButton("🎁 درخواست برکت")],
        [KeyboardButton("⚡ ماموریت‌های الهی"), KeyboardButton("🔮 فال‌گیری مقدس")],
        [KeyboardButton("💫 اعمال خیر"), KeyboardButton("📊 آمار معنوی")],
        [KeyboardButton("🕯️ روشن کردن شمع"), KeyboardButton("💝 نذر و نیاز")],
        [KeyboardButton("🏠 خروج از معبد")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    p = players[uid]
    spiritual_stats = p.get('spiritual_stats', {
        'prayers_made': 0,
        'divine_favor': 0,
        'karma_points': 0,
        'last_prayer': None,
        'blessings_received': 0,
        'divine_level': 1
    })
    
    await update.message.reply_text(
        f"🏛️ معبد مقدس - حضور الهی 🏛️\n\n"
        f"✨ {p['name']} عزیز، به خانه خدا خوش آمدید!\n\n"
        f"🌟 وضعیت معنوی شما:\n"
        f"🙏 تعداد نمازها: {spiritual_stats['prayers_made']}\n"
        f"💫 لطف الهی: {spiritual_stats['divine_favor']}\n"
        f"⚖️ امتیاز کارما: {spiritual_stats['karma_points']}\n"
        f"🏆 سطح معنوی: {spiritual_stats['divine_level']}\n"
        f"🎁 برکات دریافتی: {spiritual_stats['blessings_received']}\n\n"
        f"🔥 در این مکان مقدس، خداوند سخنان شما را می‌شنود...\n"
        f"💝 با ایمان و خلوص نیت درخواست خود را بیان کنید.",
        reply_markup=reply_markup
    )

async def prayer_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    p = players[uid]
    money = p.get('money', 0)
    
    text = f"🙏 منوی دعا و نیایش 🙏\n\n"
    text += f"💰 پول شما: {money:,} تومان\n\n"
    text += "انواع دعا را انتخاب کنید:\n\n"
    
    keyboard = []
    for prayer_name, prayer_data in PRAYER_TYPES.items():
        cost = prayer_data['cost']
        
        if money >= cost or cost == 0:
            keyboard.append([InlineKeyboardButton(
                f"{prayer_name}" + (f" - {cost:,} تومان" if cost > 0 else " - رایگان"),
                callback_data=f"pray_{prayer_name}"
            )])
        else:
            keyboard.append([InlineKeyboardButton(
                f"❌ {prayer_name} - {cost:,} تومان (ناکافی)",
                callback_data="insufficient_money_prayer"
            )])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت به معبد", callback_data="back_temple")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def talk_to_god(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    # Check if user has high enough spiritual level
    p = players[uid]
    spiritual_stats = p.get('spiritual_stats', {})
    divine_favor = spiritual_stats.get('divine_favor', 0)
    
    if divine_favor < 10:
        await update.message.reply_text(
            "🚫 برای صحبت مستقیم با خداوند، باید لطف الهی بیشتری داشته باشید!\n\n"
            "🙏 ابتدا بیشتر دعا کنید و اعمال خیر انجام دهید.\n"
            f"📊 لطف الهی فعلی: {divine_favor}/10"
        )
        return
    
    await update.message.reply_text(
        "✨ کانال ارتباط الهی باز شد... ✨\n\n"
        "🌟 شما اکنون می‌توانید مستقیماً با خداوند صحبت کنید!\n"
        "💫 پیام خود را بنویسید و ارسال کنید:\n\n"
        "⚠️ توجه: این ارتباط مقدس است و باید با احترام باشد."
    )
    
    context.user_data['talking_to_god'] = True

async def request_blessing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    p = players[uid]
    spiritual_stats = p.get('spiritual_stats', {})
    divine_favor = spiritual_stats.get('divine_favor', 0)
    
    if divine_favor < 5:
        await update.message.reply_text(
            "❌ برای درخواست برکت، لطف الهی کافی ندارید!\n"
            f"📊 لطف الهی شما: {divine_favor}/5\n"
            "🙏 ابتدا دعا کنید تا لطف الهی کسب کنید."
        )
        return
    
    # Generate random blessing
    blessing_types = ["money", "xp", "trait_boost", "special_item"]
    blessing_type = random.choice(blessing_types)
    
    if blessing_type == "money":
        amount = random.randint(500, 2000) * spiritual_stats.get('divine_level', 1)
        p['money'] = p.get('money', 0) + amount
        blessing_msg = f"💰 {amount:,} تومان برکت الهی"
        
    elif blessing_type == "xp":
        amount = random.randint(50, 200) * spiritual_stats.get('divine_level', 1)
        p['xp'] = p.get('xp', 0) + amount
        blessing_msg = f"⭐ {amount} امتیاز تجربه الهی"
        
    elif blessing_type == "trait_boost":
        traits = ['charisma', 'intelligence', 'strength', 'agility', 'luck']
        chosen_trait = random.choice(traits)
        boost = random.randint(1, 3)
        
        if 'traits' not in p:
            p['traits'] = {}
        p['traits'][chosen_trait] = p['traits'].get(chosen_trait, 5) + boost
        
        trait_names = {
            'charisma': 'جذابیت',
            'intelligence': 'هوش',
            'strength': 'قدرت',
            'agility': 'چابکی',
            'luck': 'شانس'
        }
        blessing_msg = f"💫 +{boost} {trait_names[chosen_trait]}"
        
    elif blessing_type == "special_item":
        divine_items = ["🌟 ستاره آسمانی", "⚡ صاعقه مقدس", "🔮 کره نورانی", "👑 تاج الهی"]
        item = random.choice(divine_items)
        
        if 'inventory' not in p:
            p['inventory'] = []
        p['inventory'].append(item)
        blessing_msg = f"🎁 {item}"
    
    # Decrease divine favor
    spiritual_stats['divine_favor'] = max(0, divine_favor - 5)
    spiritual_stats['blessings_received'] = spiritual_stats.get('blessings_received', 0) + 1
    p['spiritual_stats'] = spiritual_stats
    
    players[uid] = p
    save_json("data/players.json", players)
    
    await update.message.reply_text(
        f"✨ برکت الهی نازل شد! ✨\n\n"
        f"🎁 دریافت کردید: {blessing_msg}\n\n"
        f"🙏 خداوند شما را یاد دارد و بر شما رحمت فرستاده است!\n"
        f"💫 لطف الهی باقی‌مانده: {spiritual_stats['divine_favor']}"
    )

async def divine_quests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    text = "⚡ ماموریت‌های الهی ⚡\n\n"
    text += "🌟 خداوند برای شما ماموریت‌هایی تعریف کرده است:\n\n"
    
    keyboard = []
    for i, quest in enumerate(DIVINE_QUESTS, 1):
        text += f"{i}. {quest['name']}\n"
        text += f"   📝 {quest['description']}\n"
        text += f"   🏆 پاداش: {quest['reward']}\n\n"
        
        keyboard.append([InlineKeyboardButton(
            f"⚡ {quest['name']}", 
            callback_data=f"divine_quest_{quest['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت به معبد", callback_data="back_temple")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def sacred_fortune(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    p = players[uid]
    
    # Generate mystical fortune
    fortunes = [
        "🌟 آینده‌ای پر از نور و برکت در انتظار شماست",
        "💫 عشق واقعی به زودی راه خود را به قلب شما خواهد یافت",
        "⚡ قدرت درونی شما بزرگتر از آن چیزی است که تصور می‌کنید",
        "🔮 تغییرات مثبت بزرگی در راه است، آماده باشید",
        "🌈 پس از هر طوفان، رنگین‌کمان امید ظاهر می‌شود",
        "💎 استعدادهای پنهان شما به زودی آشکار خواهد شد",
        "🗝️ کلید موفقیت در دستان شماست، فقط باید جرأت استفاده داشته باشید",
        "🕊️ آرامش و سکینه به زودی جایگزین نگرانی‌هایتان خواهد شد"
    ]
    
    fortune = random.choice(fortunes)
    
    # Small spiritual boost for getting fortune
    spiritual_stats = p.get('spiritual_stats', {})
    spiritual_stats['divine_favor'] = spiritual_stats.get('divine_favor', 0) + 1
    p['spiritual_stats'] = spiritual_stats
    players[uid] = p
    save_json("data/players.json", players)
    
    await update.message.reply_text(
        f"🔮 فال مقدس برای {p['name']} 🔮\n\n"
        f"✨ پیام الهی:\n"
        f"{fortune}\n\n"
        f"🙏 این پیام از عالم غیب برای شما فرستاده شده است.\n"
        f"💫 +1 لطف الهی دریافت کردید!"
    )

async def charity_work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    p = players[uid]
    money = p.get('money', 0)
    
    if money < 100:
        await update.message.reply_text(
            "💔 برای انجام اعمال خیر حداقل 100 تومان نیاز دارید!\n"
            "💰 پول شما کافی نیست."
        )
        return
    
    keyboard = [
        [InlineKeyboardButton("💝 100 تومان", callback_data="charity_100")],
        [InlineKeyboardButton("💖 500 تومان", callback_data="charity_500")],
        [InlineKeyboardButton("💛 1000 تومان", callback_data="charity_1000")],
        [InlineKeyboardButton("💙 همه پولم!", callback_data="charity_all")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_temple")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"💫 اعمال خیر و کمک به نیازمندان 💫\n\n"
        f"💰 پول شما: {money:,} تومان\n\n"
        f"🤲 چقدر می‌خواهید به خیریه کمک کنید؟\n"
        f"⚖️ هر تومان خیرات = 1 امتیاز کارما\n"
        f"🌟 کارمای بالا = برکات بیشتر",
        reply_markup=reply_markup
    )

async def spiritual_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    p = players[uid]
    stats = p.get('spiritual_stats', {
        'prayers_made': 0,
        'divine_favor': 0,
        'karma_points': 0,
        'last_prayer': None,
        'blessings_received': 0,
        'divine_level': 1,
        'charity_given': 0,
        'divine_quests_completed': 0
    })
    
    rank = get_spiritual_rank(stats['divine_level'])
    
    await update.message.reply_text(
        f"📊 آمار معنوی {p['name']} 📊\n\n"
        f"🏆 رتبه معنوی: {rank}\n"
        f"🌟 سطح الهی: {stats['divine_level']}\n"
        f"💫 لطف الهی: {stats['divine_favor']}\n"
        f"⚖️ امتیاز کارما: {stats['karma_points']}\n"
        f"🙏 تعداد نمازها: {stats['prayers_made']}\n"
        f"🎁 برکات دریافتی: {stats['blessings_received']}\n"
        f"💝 مبلغ خیرات: {stats.get('charity_given', 0):,} تومان\n"
        f"⚡ ماموریت‌های الهی: {stats.get('divine_quests_completed', 0)}\n\n"
        f"🔥 هرچه معنویت بالاتر، برکات بیشتر!"
    )

async def light_candle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    p = players[uid]
    
    if p.get('money', 0) < 50:
        await update.message.reply_text(
            "🕯️ برای روشن کردن شمع 50 تومان نیاز دارید!\n"
            "💰 پول کافی ندارید."
        )
        return
    
    # Deduct money and give spiritual benefits
    p['money'] = p.get('money', 0) - 50
    spiritual_stats = p.get('spiritual_stats', {})
    spiritual_stats['divine_favor'] = spiritual_stats.get('divine_favor', 0) + 2
    spiritual_stats['karma_points'] = spiritual_stats.get('karma_points', 0) + 5
    p['spiritual_stats'] = spiritual_stats
    
    players[uid] = p
    save_json("data/players.json", players)
    
    candle_messages = [
        "🕯️ شمع شما روشن شد و نور آن تا آسمان‌ها بالا رفت...",
        "✨ نور شمع شما ارواح را آرام کرد و فرشتگان لبخند زدند...",
        "🌟 شعله‌ای که افروختید، امید تازه‌ای در دل‌ها برانگیخت...",
        "💫 نور شمع شما راه گمشدگان را روشن کرد..."
    ]
    
    await update.message.reply_text(
        f"{random.choice(candle_messages)}\n\n"
        f"🙏 نذر شما پذیرفته شد!\n"
        f"💫 +2 لطف الهی\n"
        f"⚖️ +5 امتیاز کارما\n"
        f"💰 -50 تومان"
    )

async def make_vow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    await update.message.reply_text(
        "💝 نذر و نیاز 💝\n\n"
        "🤲 نذر خود را به خداوند تقدیم کنید:\n"
        "مثال: 'اگر کارم درست شود، 1000 تومان صدقه می‌دهم'\n\n"
        "✍️ نذر خود را بنویسید:"
    )
    
    context.user_data['making_vow'] = True

def get_spiritual_rank(level):
    """Get spiritual rank based on divine level"""
    ranks = {
        1: "🌱 طالب مبتدی",
        2: "🙏 نمازگزار", 
        3: "💫 عابد",
        4: "🌟 ولی",
        5: "⚡ قطب روحانی",
        6: "👑 استاد معنوی"
    }
    return ranks.get(min(level, 6), "🌱 طالب مبتدی")

# Handle temple interactions
async def handle_temple_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)
    
    # Handle talking to god
    if context.user_data.get('talking_to_god'):
        message = update.message.text
        
        # Send to admin (god)
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"🙏 پیام از معبد - {user.first_name} ({uid}):\n\n"
                     f"'{message}'\n\n"
                     f"💫 برای پاسخ از /god_reply {uid} پیام استفاده کنید"
            )
        except Exception:
            pass
        
        context.user_data['talking_to_god'] = False
        
        await update.message.reply_text(
            "✨ پیام شما به حضور الهی رسید... ✨\n\n"
            "🌟 خداوند سخنان شما را شنید و در صورت مصلحت پاسخ خواهد داد.\n"
            "🙏 صبر و انتظار خود را حفظ کنید."
        )
        return True
    
    # Handle making vow
    if context.user_data.get('making_vow'):
        vow = update.message.text
        players = load_json("data/players.json")
        
        p = players[uid]
        if 'vows' not in p:
            p['vows'] = []
        
        p['vows'].append({
            'text': vow,
            'date': datetime.now().isoformat(),
            'fulfilled': False
        })
        
        spiritual_stats = p.get('spiritual_stats', {})
        spiritual_stats['divine_favor'] = spiritual_stats.get('divine_favor', 0) + 3
        p['spiritual_stats'] = spiritual_stats
        
        players[uid] = p
        save_json("data/players.json", players)
        
        context.user_data['making_vow'] = False
        
        await update.message.reply_text(
            f"💝 نذر شما ثبت شد! 💝\n\n"
            f"📜 نذر: {vow}\n\n"
            f"🤲 خداوند شاهد نذر شماست.\n"
            f"💫 +3 لطف الهی دریافت کردید!"
        )
        return True
    
    return False

async def forgiveness_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📿 طلب آمرزش 📿\n\n"
        "🤲 'استغفرالله العظیم'\n\n"
        "💫 خداوند غفور و رحیم است...\n"
        "🌟 +1 لطف الهی دریافت کردید!"
    )
    
    # Give forgiveness benefit
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    p = players[uid]
    spiritual_stats = p.get('spiritual_stats', {})
    spiritual_stats['divine_favor'] = spiritual_stats.get('divine_favor', 0) + 1
    p['spiritual_stats'] = spiritual_stats
    
    players[uid] = p
    save_json("data/players.json", players)
