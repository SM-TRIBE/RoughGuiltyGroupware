
<line_number>1</line_number>

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.tools import load_json, save_json
import random
from datetime import datetime, timedelta

async def social_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    keyboard = [
        [KeyboardButton("👥 لیست دوستان"), KeyboardButton("🔍 جستجوی کاربر")],
        [KeyboardButton("💌 درخواست دوستی"), KeyboardButton("🎁 هدیه به دوست")],
        [KeyboardButton("📱 چت خصوصی"), KeyboardButton("🏆 مسابقه با دوست")],
        [KeyboardButton("📊 فعالیت‌های اجتماعی"), KeyboardButton("⚙️ تنظیمات حریم خصوصی")],
        [KeyboardButton("🏠 بازگشت به منو اصلی")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    p = players[uid]
    friends_count = len(p.get('friends', []))
    
    await update.message.reply_text(
        f"👥 مرکز اجتماعی\n\n"
        f"نام: {p['name']}\n"
        f"دوستان: {friends_count}\n"
        f"محبوبیت: {p.get('reputation', 0)}\n\n"
        f"اینجا می‌توانید با سایر بازیکنان ارتباط برقرار کنید.",
        reply_markup=reply_markup
    )

async def friends_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    p = players[uid]
    friends = p.get('friends', [])
    
    if not friends:
        await update.message.reply_text("هنوز دوستی ندارید! از قسمت جستجو کاربران جدید پیدا کنید.")
        return
    
    friends_text = "👥 لیست دوستان شما:\n\n"
    
    for friend_id in friends:
        if friend_id in players:
            friend = players[friend_id]
            online_status = "🟢 آنلاین" if is_recently_active(friend) else "⚫ آفلاین"
            friends_text += f"• {friend['name']} - {online_status}\n"
            friends_text += f"  📍 {friend.get('location', 'نامشخص')}\n"
            friends_text += f"  ⭐ سطح {friend.get('level', 1)}\n\n"
    
    await update.message.reply_text(friends_text)

async def search_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    # Show random users
    all_users = [(pid, pdata) for pid, pdata in players.items() 
                 if pdata.get("approved") and pid != uid]
    
    if not all_users:
        await update.message.reply_text("هیچ کاربری برای نمایش وجود ندارد!")
        return
    
    # Show 5 random users
    random_users = random.sample(all_users, min(5, len(all_users)))
    
    keyboard = []
    text = "🔍 کاربران آنلاین:\n\n"
    
    for i, (pid, pdata) in enumerate(random_users, 1):
        text += f"{i}. {pdata['name']}\n"
        text += f"   ⭐ سطح {pdata.get('level', 1)}\n"
        text += f"   📍 {pdata.get('location', 'نامشخص')}\n\n"
        
        keyboard.append([InlineKeyboardButton(
            f"👤 {pdata['name']}", 
            callback_data=f"user_profile_{pid}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔄 نمایش کاربران دیگر", callback_data="refresh_users")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def send_friend_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    await update.message.reply_text(
        "💌 ارسال درخواست دوستی\n\n"
        "نام کاربری یا نام شخص را وارد کنید:\n"
        "(مثال: @username یا نام کامل)"
    )
    
    context.user_data['waiting_for_friend_request'] = True

async def gift_to_friend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    p = players[uid]
    friends = p.get('friends', [])
    
    if not friends:
        await update.message.reply_text("شما هنوز دوستی ندارید!")
        return
    
    keyboard = []
    for friend_id in friends[:10]:  # Show max 10 friends
        if friend_id in players:
            friend = players[friend_id]
            keyboard.append([InlineKeyboardButton(
                f"🎁 {friend['name']}", 
                callback_data=f"gift_to_{friend_id}"
            )])
    
    keyboard.append([InlineKeyboardButton("🚪 بازگشت", callback_data="back_social")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎁 هدیه به دوست\n\n"
        "دوست خود را انتخاب کنید:",
        reply_markup=reply_markup
    )

async def private_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    p = players[uid]
    friends = p.get('friends', [])
    
    if not friends:
        await update.message.reply_text("برای چت خصوصی ابتدا باید دوست داشته باشید!")
        return
    
    keyboard = []
    for friend_id in friends:
        if friend_id in players:
            friend = players[friend_id]
            online = "🟢" if is_recently_active(friend) else "⚫"
            keyboard.append([InlineKeyboardButton(
                f"{online} {friend['name']}", 
                callback_data=f"chat_with_{friend_id}"
            )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📱 چت خصوصی\n\n"
        "با کدام دوست چت کنید:",
        reply_markup=reply_markup
    )

async def social_activities(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    p = players[uid]
    activities = p.get('social_activities', {})
    
    text = f"📊 فعالیت‌های اجتماعی {p['name']}:\n\n"
    text += f"👥 تعداد دوستان: {len(p.get('friends', []))}\n"
    text += f"💌 درخواست‌های ارسالی: {activities.get('friend_requests_sent', 0)}\n"
    text += f"🎁 هدایای ارسالی: {activities.get('gifts_sent', 0)}\n"
    text += f"💬 پیام‌های ارسالی: {activities.get('messages_sent', 0)}\n"
    text += f"🏆 مسابقات برنده شده: {activities.get('competitions_won', 0)}\n"
    text += f"⭐ امتیاز محبوبیت: {p.get('reputation', 0)}\n\n"
    
    # Recent activity
    recent = activities.get('recent', [])
    if recent:
        text += "📈 فعالیت‌های اخیر:\n"
        for activity in recent[-5:]:  # Show last 5 activities
            text += f"• {activity}\n"
    
    await update.message.reply_text(text)

def is_recently_active(player_data):
    """Check if player was active in last 30 minutes"""
    last_seen = player_data.get('last_seen')
    if not last_seen:
        return False
    
    try:
        last_time = datetime.fromisoformat(last_seen)
        return datetime.now() - last_time < timedelta(minutes=30)
    except:
        return False

async def handle_friend_request_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('waiting_for_friend_request'):
        return
    
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    target_name = update.message.text.strip().replace('@', '')
    
    # Find target user
    target_uid = None
    for pid, pdata in players.items():
        if (pdata.get('username', '').lower() == target_name.lower() or 
            pdata.get('name', '').lower() == target_name.lower()):
            target_uid = pid
            break
    
    if not target_uid:
        await update.message.reply_text("کاربر یافت نشد!")
        context.user_data['waiting_for_friend_request'] = False
        return
    
    if target_uid == uid:
        await update.message.reply_text("نمی‌توانید با خودتان دوست شوید!")
        context.user_data['waiting_for_friend_request'] = False
        return
    
    sender = players[uid]
    target = players[target_uid]
    
    # Check if already friends
    if target_uid in sender.get('friends', []):
        await update.message.reply_text("شما قبلاً با این کاربر دوست هستید!")
        context.user_data['waiting_for_friend_request'] = False
        return
    
    # Send friend request
    if 'friend_requests' not in target:
        target['friend_requests'] = []
    
    if uid not in target['friend_requests']:
        target['friend_requests'].append(uid)
        players[target_uid] = target
        save_json("data/players.json", players)
        
        # Notify target user
        try:
            await context.bot.send_message(
                chat_id=int(target_uid),
                text=f"💌 درخواست دوستی جدید از {sender['name']}!\n"
                     f"برای پاسخ به بخش اجتماعی بروید."
            )
        except:
            pass
        
        await update.message.reply_text(f"✅ درخواست دوستی به {target['name']} ارسال شد!")
    else:
        await update.message.reply_text("قبلاً درخواست دوستی ارسال کرده‌اید!")
    
    context.user_data['waiting_for_friend_request'] = False

