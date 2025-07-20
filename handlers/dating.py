

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.tools import load_json, save_json
import random
from datetime import datetime, timedelta

DATING_LOCATIONS = {
    "🌹 کافه رمانتیک": {"cost": 100, "success_rate": 0.7, "xp": 30},
    "🍽️ رستوران فاخر": {"cost": 300, "success_rate": 0.8, "xp": 50},
    "🎬 سینما": {"cost": 150, "success_rate": 0.6, "xp": 25},
    "🌳 پارک عاشقان": {"cost": 50, "success_rate": 0.5, "xp": 20},
    "🎭 تئاتر": {"cost": 200, "success_rate": 0.75, "xp": 40},
    "🏖️ ساحل": {"cost": 80, "success_rate": 0.65, "xp": 35}
}

DATING_GIFTS = {
    "🌹 دسته گل": {"cost": 50, "effect": 10},
    "💎 جواهر": {"cost": 500, "effect": 50},
    "🍫 شکلات": {"cost": 30, "effect": 8},
    "🧸 عروسک": {"cost": 80, "effect": 15},
    "💍 انگشتر": {"cost": 1000, "effect": 100},
    "🎁 هدیه مرموز": {"cost": 200, "effect": 25}
}

async def dating_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    keyboard = [
        [KeyboardButton("💕 جستجوی شریک"), KeyboardButton("📱 دیتینگ آنلاین")],
        [KeyboardButton("💝 خرید هدیه"), KeyboardButton("🌟 پروفایل دیتینگ")],
        [KeyboardButton("💬 چت عاشقانه"), KeyboardButton("📊 آمار قرارها")],
        [KeyboardButton("🎯 ماچ‌میکر هوشمند"), KeyboardButton("💔 تاریخچه روابط")],
        [KeyboardButton("🏠 بازگشت به منو اصلی")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    p = players[uid]
    dating_stats = p.get('dating_stats', {
        'total_dates': 0,
        'successful_dates': 0,
        'gifts_given': 0,
        'relationships': 0,
        'dating_level': 1,
        'dating_xp': 0
    })
    
    success_rate = (dating_stats['successful_dates'] / max(dating_stats['total_dates'], 1)) * 100
    
    await update.message.reply_text(
        f"💕 مرکز دیتینگ و روابط عاشقانه 💕\n\n"
        f"👤 {p['name']} عزیز، به دنیای عشق خوش آمدید!\n\n"
        f"📊 آمار شما:\n"
        f"💘 سطح دیتینگ: {dating_stats['dating_level']}\n"
        f"⭐ امتیاز عاشقی: {dating_stats['dating_xp']}\n"
        f"📅 کل قرارها: {dating_stats['total_dates']}\n"
        f"✅ قرارهای موفق: {dating_stats['successful_dates']}\n"
        f"📈 درصد موفقیت: {success_rate:.1f}%\n"
        f"💝 هدایای داده شده: {dating_stats['gifts_given']}\n\n"
        f"💫 عشق در انتظار شماست!",
        reply_markup=reply_markup
    )

async def find_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    partners = load_json("data/partners.json")
    uid = str(user.id)
    
    p = players[uid]
    
    # Create some default partners if none exist
    if not partners:
        partners = [
            {
                "name": "سارا",
                "description": "دختری زیبا و باهوش با علاقه به هنر",
                "charisma": 8,
                "intelligence": 7,
                "available": True
            },
            {
                "name": "علی",
                "description": "پسری مهربان و ورزشکار",
                "charisma": 7,
                "intelligence": 6,
                "available": True
            },
            {
                "name": "مریم",
                "description": "دکتری جوان و پرانرژی",
                "charisma": 9,
                "intelligence": 9,
                "available": True
            }
        ]
        save_json("data/partners.json", partners)
    
    # Find compatible partners based on user's traits
    compatible_partners = []
    user_charisma = p.get('traits', {}).get('charisma', 5)
    
    for partner in partners:
        if partner.get('available', True):
            compatibility = calculate_compatibility(p, partner)
            if compatibility > 0.3:  # Minimum 30% compatibility
                partner['compatibility'] = compatibility
                compatible_partners.append(partner)
    
    if not compatible_partners:
        await update.message.reply_text(
            "💔 متأسفانه در حال حاضر شریک مناسبی یافت نشد.\n"
            "💪 جذابیت خود را بالا ببرید تا شانس بیشتری داشته باشید!"
        )
        return
    
    # Sort by compatibility
    compatible_partners.sort(key=lambda x: x['compatibility'], reverse=True)
    best_match = compatible_partners[0]
    
    context.user_data['current_match'] = best_match
    
    keyboard = [
        [InlineKeyboardButton("💕 علاقه‌مندم", callback_data="date_interested")],
        [InlineKeyboardButton("👀 مشاهده بیشتر", callback_data="date_view_more")],
        [InlineKeyboardButton("❌ نه ممنون", callback_data="date_pass")],
        [InlineKeyboardButton("🎁 ارسال هدیه", callback_data="date_send_gift")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"💖 شریک پیشنهادی برای شما:\n\n"
        f"👤 نام: {best_match['name']}\n"
        f"📝 توضیحات: {best_match['description']}\n"
        f"💫 سازگاری: {best_match['compatibility']*100:.0f}%\n"
        f"⭐ جذابیت: {best_match.get('charisma', 5)}/10\n"
        f"🧠 هوش: {best_match.get('intelligence', 5)}/10\n\n"
        f"💕 می‌خواهید با {best_match['name']} قرار بگذارید؟",
        reply_markup=reply_markup
    )

async def online_dating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    # Show other real players for dating
    available_players = []
    current_player = players[uid]
    
    for pid, pdata in players.items():
        if (pid != uid and 
            pdata.get("approved") and 
            not pdata.get('partner') and
            pdata.get('dating_settings', {}).get('looking_for_date', True)):
            
            compatibility = calculate_player_compatibility(current_player, pdata)
            pdata['compatibility'] = compatibility
            pdata['player_id'] = pid
            available_players.append(pdata)
    
    if not available_players:
        await update.message.reply_text(
            "📱 در حال حاضر کاربر آنلاینی برای دیتینگ یافت نشد.\n"
            "🔄 لطفاً بعداً دوباره تلاش کنید."
        )
        return
    
    # Sort by compatibility
    available_players.sort(key=lambda x: x['compatibility'], reverse=True)
    
    keyboard = []
    text = "📱 دیتینگ آنلاین - کاربران در دسترس:\n\n"
    
    for i, player in enumerate(available_players[:5], 1):
        text += f"{i}. {player['name']} - سازگاری: {player['compatibility']*100:.0f}%\n"
        text += f"   📍 {player.get('location', 'نامشخص')}\n"
        text += f"   ⭐ سطح {player.get('level', 1)}\n\n"
        
        keyboard.append([InlineKeyboardButton(
            f"💕 {player['name']}", 
            callback_data=f"online_date_{player['player_id']}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔄 نمایش افراد دیگر", callback_data="refresh_online_dating")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def dating_gifts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    p = players[uid]
    money = p.get('money', 0)
    
    text = f"💝 فروشگاه هدایای عاشقانه 💝\n\n"
    text += f"💰 پول شما: {money:,} تومان\n\n"
    text += "🎁 هدایای موجود:\n"
    
    keyboard = []
    for gift_name, gift_data in DATING_GIFTS.items():
        cost = gift_data['cost']
        effect = gift_data['effect']
        
        if money >= cost:
            keyboard.append([InlineKeyboardButton(
                f"{gift_name} - {cost:,} تومان (+{effect} امتیاز)",
                callback_data=f"buy_dating_gift_{gift_name}"
            )])
        else:
            keyboard.append([InlineKeyboardButton(
                f"❌ {gift_name} - {cost:,} تومان (ناکافی)",
                callback_data="insufficient_money_dating"
            )])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_dating")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def dating_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    p = players[uid]
    dating_profile = p.get('dating_profile', {})
    
    if not dating_profile:
        # Create default dating profile
        dating_profile = {
            'bio': "در جستجوی عشق واقعی...",
            'interests': ['سینما', 'مطالعه', 'سفر'],
            'looking_for': 'رابطه جدی',
            'age_range': [p.get('age', 18) - 5, p.get('age', 18) + 5],
            'visible': True
        }
        p['dating_profile'] = dating_profile
        players[uid] = p
        save_json("data/players.json", players)
    
    keyboard = [
        [InlineKeyboardButton("✏️ ویرایش بیو", callback_data="edit_dating_bio")],
        [InlineKeyboardButton("🎯 تنظیم علایق", callback_data="edit_dating_interests")],
        [InlineKeyboardButton("💕 نوع رابطه", callback_data="edit_dating_type")],
        [InlineKeyboardButton("🔧 تنظیمات", callback_data="dating_settings")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_dating")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    visibility = "🟢 فعال" if dating_profile.get('visible', True) else "🔴 غیرفعال"
    interests = ", ".join(dating_profile.get('interests', []))
    
    await update.message.reply_text(
        f"🌟 پروفایل دیتینگ شما:\n\n"
        f"👤 نام: {p['name']}\n"
        f"🎂 سن: {p.get('age', 'نامشخص')}\n"
        f"📝 بیو: {dating_profile.get('bio', 'بدون توضیحات')}\n"
        f"🎯 علایق: {interests}\n"
        f"💕 به دنبال: {dating_profile.get('looking_for', 'نامشخص')}\n"
        f"👁️ نمایان بودن: {visibility}\n\n"
        f"⭐ جذابیت: {p.get('traits', {}).get('charisma', 5)}/20",
        reply_markup=reply_markup
    )

async def dating_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    # Load recent dating conversations
    dating_chats = load_json("data/dating_chats.json")
    user_chats = dating_chats.get(uid, [])
    
    if not user_chats:
        await update.message.reply_text(
            "💬 هنوز هیچ مکالمه عاشقانه‌ای ندارید!\n"
            "💕 ابتدا با کسی قرار بگذارید تا بتوانید چت کنید."
        )
        return
    
    keyboard = []
    text = "💬 مکالمات عاشقانه شما:\n\n"
    
    for i, chat in enumerate(user_chats[-5:], 1):  # Show last 5 chats
        partner_name = chat.get('partner_name', 'نامشخص')
        last_message = chat.get('last_message', 'پیامی ندارد')[:30]
        text += f"{i}. {partner_name}\n   آخرین پیام: {last_message}...\n\n"
        
        keyboard.append([InlineKeyboardButton(
            f"💬 {partner_name}", 
            callback_data=f"open_dating_chat_{chat.get('partner_id')}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_dating")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def dating_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    p = players[uid]
    stats = p.get('dating_stats', {
        'total_dates': 0,
        'successful_dates': 0,
        'gifts_given': 0,
        'relationships': 0,
        'dating_level': 1,
        'dating_xp': 0,
        'heartbreaks': 0,
        'proposals_sent': 0,
        'proposals_received': 0
    })
    
    success_rate = (stats['successful_dates'] / max(stats['total_dates'], 1)) * 100
    
    await update.message.reply_text(
        f"📊 آمار کامل دیتینگ شما:\n\n"
        f"💘 سطح عاشقی: {stats['dating_level']}\n"
        f"⭐ امتیاز دیتینگ: {stats['dating_xp']}\n"
        f"📅 کل قرارها: {stats['total_dates']}\n"
        f"✅ قرارهای موفق: {stats['successful_dates']}\n"
        f"📈 درصد موفقیت: {success_rate:.1f}%\n"
        f"💝 هدایای داده شده: {stats['gifts_given']}\n"
        f"💕 روابط برقرار شده: {stats['relationships']}\n"
        f"💔 شکست‌های عاشقانه: {stats['heartbreaks']}\n"
        f"💌 پیشنهادهای ارسالی: {stats['proposals_sent']}\n"
        f"💝 پیشنهادهای دریافتی: {stats['proposals_received']}\n\n"
        f"🏆 رتبه شما: {get_dating_rank(stats['dating_level'])}"
    )

async def smart_matchmaker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎯 ماچ‌میکر هوشمند\n\n"
        "🔍 در حال جستجوی بهترین شریک برای شما...\n"
        "💫 این قابلیت به زودی اضافه خواهد شد!"
    )

async def relationship_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💔 تاریخچه روابط\n\n"
        "📜 سابقه روابط عاشقانه شما اینجا نمایش داده خواهد شد.\n"
        "💫 این قابلیت به زودی اضافه خواهد شد!"
    )

def calculate_compatibility(user, partner):
    """Calculate compatibility between user and NPC partner"""
    user_charisma = user.get('traits', {}).get('charisma', 5)
    user_intelligence = user.get('traits', {}).get('intelligence', 5)
    
    partner_charisma = partner.get('charisma', 5)
    partner_intelligence = partner.get('intelligence', 5)
    
    # Calculate based on trait similarity and user's charisma
    charisma_factor = min(user_charisma / 10, 1.0)  # Max 1.0
    intelligence_match = 1 - abs(user_intelligence - partner_intelligence) / 10
    
    return (charisma_factor + intelligence_match) / 2

def calculate_player_compatibility(user1, user2):
    """Calculate compatibility between two real players"""
    traits1 = user1.get('traits', {})
    traits2 = user2.get('traits', {})
    
    # Age compatibility
    age1 = user1.get('age', 25)
    age2 = user2.get('age', 25)
    age_diff = abs(age1 - age2)
    age_factor = max(0, 1 - age_diff / 20)  # Decreases with age difference
    
    # Trait compatibility
    trait_scores = []
    for trait in ['charisma', 'intelligence']:
        val1 = traits1.get(trait, 5)
        val2 = traits2.get(trait, 5)
        trait_scores.append(1 - abs(val1 - val2) / 20)
    
    trait_factor = sum(trait_scores) / len(trait_scores)
    
    return (age_factor + trait_factor) / 2

def get_dating_rank(level):
    """Get dating rank based on level"""
    ranks = {
        1: "💔 تازه‌کار",
        2: "💕 عاشق مبتدی", 
        3: "💖 رمانتیک",
        4: "💝 عاشق حرفه‌ای",
        5: "👑 استاد عشق"
    }
    return ranks.get(min(level, 5), "💔 تازه‌کار")

async def handle_dating_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = query.from_user
    uid = str(user.id)
    
    if data == "date_interested":
        await start_date(query, context)
    elif data == "date_view_more":
        await view_partner_details(query, context)
    elif data == "date_pass":
        await pass_partner(query, context)
    elif data == "date_send_gift":
        await send_dating_gift_menu(query, context)
    elif data.startswith("online_date_"):
        partner_id = data.split("_")[-1]
        await start_online_date(query, context, partner_id)
    elif data.startswith("buy_dating_gift_"):
        gift_name = data.replace("buy_dating_gift_", "")
        await buy_dating_gift(query, context, gift_name)
    elif data == "back_dating":
        await query.message.delete()

async def start_date(query, context):
    user = query.from_user
    uid = str(user.id)
    
    current_match = context.user_data.get('current_match')
    if not current_match:
        await query.edit_message_text("❌ خطا: اطلاعات شریک یافت نشد!")
        return
    
    # Show dating location options
    keyboard = []
    text = f"💕 قرار با {current_match['name']}\n\n"
    text += "🌟 مکان قرار را انتخاب کنید:\n\n"
    
    for location, data in DATING_LOCATIONS.items():
        cost = data['cost']
        success_rate = data['success_rate'] * 100
        keyboard.append([InlineKeyboardButton(
            f"{location} - {cost:,} تومان ({success_rate:.0f}% موفقیت)",
            callback_data=f"choose_location_{location}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text, reply_markup=reply_markup)

async def view_partner_details(query, context):
    current_match = context.user_data.get('current_match')
    if not current_match:
        await query.edit_message_text("❌ خطا: اطلاعات شریک یافت نشد!")
        return
    
    details = f"👤 جزئیات {current_match['name']}:\n\n"
    details += f"📝 توضیحات: {current_match['description']}\n"
    details += f"⭐ جذابیت: {current_match.get('charisma', 5)}/10\n"
    details += f"🧠 هوش: {current_match.get('intelligence', 5)}/10\n"
    details += f"💫 سازگاری با شما: {current_match['compatibility']*100:.0f}%\n"
    
    keyboard = [
        [InlineKeyboardButton("💕 علاقه‌مندم", callback_data="date_interested")],
        [InlineKeyboardButton("❌ نه ممنون", callback_data="date_pass")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(details, reply_markup=reply_markup)

async def pass_partner(query, context):
    await query.edit_message_text(
        "❌ شریک رد شد!\n"
        "💕 با دکمه 'جستجوی شریک' می‌توانید دوباره تلاش کنید."
    )

async def send_dating_gift_menu(query, context):
    await query.edit_message_text(
        "🎁 قابلیت ارسال هدیه به زودی اضافه خواهد شد!"
    )

async def start_online_date(query, context, partner_id):
    await query.edit_message_text(
        f"💕 قرار آنلاین با کاربر {partner_id}\n"
        "💫 این قابلیت به زودی توسعه خواهد یافت!"
    )

async def buy_dating_gift(query, context, gift_name):
    user = query.from_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players:
        await query.edit_message_text("❌ خطا: اطلاعات کاربر یافت نشد!")
        return
    
    p = players[uid]
    money = p.get('money', 0)
    
    if gift_name in DATING_GIFTS:
        cost = DATING_GIFTS[gift_name]['cost']
        if money >= cost:
            p['money'] = money - cost
            if 'inventory' not in p:
                p['inventory'] = []
            p['inventory'].append(gift_name)
            
            # Update dating stats
            if 'dating_stats' not in p:
                p['dating_stats'] = {'gifts_given': 0}
            p['dating_stats']['gifts_given'] = p['dating_stats'].get('gifts_given', 0) + 1
            
            players[uid] = p
            save_json("data/players.json", players)
            
            await query.edit_message_text(
                f"✅ {gift_name} خریداری شد!\n"
                f"💰 پول باقی‌مانده: {p['money']:,} تومان"
            )
        else:
            await query.edit_message_text(
                f"❌ پول کافی ندارید!\n"
                f"💰 نیاز: {cost:,} تومان\n"
                f"💳 دارید: {money:,} تومان"
            )
    else:
        await query.edit_message_text("❌ هدیه یافت نشد!")

