
<old_str>
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from utils.tools import load_json, save_json
import random

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("🔔 اعلانات"), KeyboardButton("🌙 حالت شب")],
        [KeyboardButton("🔒 حریم خصوصی"), KeyboardButton("🎵 صدا")],
        [KeyboardButton("🏠 بازگشت به منو اصلی")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "⚙️ تنظیمات\n\nاینجا می‌توانید تنظیمات بازی را تغییر دهید.",
        reply_markup=reply_markup
    )

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
❓ راهنمای بازی

🎮 اصول بازی:
• ابتدا پروفایل خود را کامل کنید
• از کار کردن پول درآوری کنید
• مهارت‌هایتان را افزایش دهید
• با سایر بازیکنان ارتباط برقرار کنید

💰 اقتصاد:
• هر روز جایزه روزانه دریافت کنید
• در شانس‌آزمایی شرکت کنید
• پول به دوستان انتقال دهید

⚔️ ماجراجویی:
• در سیاه‌چال‌ها مبارزه کنید
• ماموریت‌ها را انجام دهید
• آیتم‌های ارزشمند جمع کنید

👥 اجتماعی:
• دوست پیدا کنید
• با سایرین چت کنید
• هدیه ارسال کنید

برای کمک بیشتر با مدیران تماس بگیرید.
    """
    
    await update.message.reply_text(help_text)

async def notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔔 تنظیمات اعلانات - در حال توسعه")

async def night_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌙 حالت شب - در حال توسعه")

async def privacy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔒 حریم خصوصی - در حال توسعه")

async def sound_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 تنظیمات صدا - در حال توسعه")</old_str>
<new_str>
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.tools import load_json, save_json
import random

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("🔔 اعلانات"), KeyboardButton("🌙 حالت شب")],
        [KeyboardButton("🔒 حریم خصوصی"), KeyboardButton("🎵 صدا")],
        [KeyboardButton("🔄 بازنشانی بازی"), KeyboardButton("📱 درباره بازی")],
        [KeyboardButton("🏠 بازگشت به منو اصلی")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "⚙️ تنظیمات\n\nاینجا می‌توانید تنظیمات بازی را تغییر دهید.",
        reply_markup=reply_markup
    )

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
❓ راهنمای کامل بازی

🎮 شروع بازی:
• ثبت‌نام کنید و تأیید شوید
• پروفایل خود را کامل کنید
• از میدان اصلی شروع کنید

💰 سیستم اقتصادی:
• 🎁 جایزه روزانه: هر 24 ساعت
• 💼 کار کردن: درآمد ثابت
• 🎰 شانس‌آزمایی: ریسک و برد
• 💸 انتقال پول: به دوستان

⚔️ ماجراجویی و مبارزه:
• 🏰 سیاه‌چال‌ها: مبارزه با هیولا
• 📜 ماموریت‌ها: XP و پول
• 🎒 کیف: آیتم‌های خاص
• ⚔️ مبارزه: با بازیکنان دیگر

👥 بخش اجتماعی:
• 👥 دوستان: اضافه و چت
• 💌 درخواست دوستی
• 🎁 هدیه دادن
• 💬 چت خصوصی

💍 روابط:
• 💕 دیتینگ: آشنایی
• 💍 ازدواج: با سایر بازیکنان
• 🏛️ معبد: با خداوند صحبت

🎮 بازی‌ها:
• 🎲 تاس‌بازی، 🃏 بلک‌جک
• 🎯 تیراندازی، 🧩 حدس عدد
• 🎮 حافظه، ⚡ واکنش‌سنج

📊 پیشرفت:
• ⭐ سطح: با XP افزایش
• 💪 مهارت‌ها: 5 ویژگی اصلی
• 🏅 دستاوردها: انجام کارها
• 🎯 امتیاز مهارت: برای ارتقاء

برای کمک بیشتر با مدیران تماس بگیرید.
    """
    
    keyboard = [
        [KeyboardButton("🎮 راهنمای کوتاه"), KeyboardButton("💡 نکات مفید")],
        [KeyboardButton("🏠 بازگشت به منو اصلی")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(help_text, reply_markup=reply_markup)

async def notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    
    if uid not in players:
        await update.message.reply_text("ابتدا /start کنید")
        return
    
    p = players[uid]
    notifications_settings = p.get('notifications', {
        'daily_reward': True,
        'friend_requests': True,
        'gifts': True,
        'level_up': True,
        'work_available': True
    })
    
    keyboard = [
        [InlineKeyboardButton(
            f"{'✅' if notifications_settings['daily_reward'] else '❌'} جایزه روزانه",
            callback_data="toggle_notif_daily"
        )],
        [InlineKeyboardButton(
            f"{'✅' if notifications_settings['friend_requests'] else '❌'} درخواست دوستی",
            callback_data="toggle_notif_friends"
        )],
        [InlineKeyboardButton(
            f"{'✅' if notifications_settings['gifts'] else '❌'} هدایا",
            callback_data="toggle_notif_gifts"
        )],
        [InlineKeyboardButton(
            f"{'✅' if notifications_settings['level_up'] else '❌'} ارتقاء سطح",
            callback_data="toggle_notif_levelup"
        )],
        [InlineKeyboardButton(
            f"{'✅' if notifications_settings['work_available'] else '❌'} دسترسی کار",
            callback_data="toggle_notif_work"
        )],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_settings")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔔 تنظیمات اعلانات\n\n"
        "روی هر گزینه کلیک کنید تا فعال/غیرفعال شود:",
        reply_markup=reply_markup
    )

async def night_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    
    if uid not in players:
        await update.message.reply_text("ابتدا /start کنید")
        return
    
    p = players[uid]
    night_mode = p.get('night_mode', False)
    
    keyboard = [
        [InlineKeyboardButton(
            "🌙 فعال کردن حالت شب" if not night_mode else "☀️ غیرفعال کردن حالت شب",
            callback_data="toggle_night_mode"
        )],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_settings")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    status = "فعال 🌙" if night_mode else "غیرفعال ☀️"
    
    await update.message.reply_text(
        f"🌙 حالت شب\n\n"
        f"وضعیت فعلی: {status}\n\n"
        f"حالت شب رنگ‌های تیره‌تری را نمایش می‌دهد.",
        reply_markup=reply_markup
    )

async def privacy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    
    if uid not in players:
        await update.message.reply_text("ابتدا /start کنید")
        return
    
    p = players[uid]
    privacy_settings = p.get('privacy_settings', {
        'allow_friend_requests': True,
        'show_online_status': True,
        'allow_gifts': True,
        'show_location': True,
        'allow_dating': True
    })
    
    keyboard = [
        [InlineKeyboardButton(
            f"{'✅' if privacy_settings['allow_friend_requests'] else '❌'} درخواست دوستی",
            callback_data="toggle_privacy_friends"
        )],
        [InlineKeyboardButton(
            f"{'✅' if privacy_settings['show_online_status'] else '❌'} نمایش وضعیت آنلاین",
            callback_data="toggle_privacy_online"
        )],
        [InlineKeyboardButton(
            f"{'✅' if privacy_settings['allow_gifts'] else '❌'} دریافت هدیه",
            callback_data="toggle_privacy_gifts"
        )],
        [InlineKeyboardButton(
            f"{'✅' if privacy_settings['show_location'] else '❌'} نمایش مکان",
            callback_data="toggle_privacy_location"
        )],
        [InlineKeyboardButton(
            f"{'✅' if privacy_settings['allow_dating'] else '❌'} دیتینگ",
            callback_data="toggle_privacy_dating"
        )],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_settings")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔒 تنظیمات حریم خصوصی\n\n"
        "با کلیک روی هر گزینه، آن را فعال/غیرفعال کنید:",
        reply_markup=reply_markup
    )

async def sound_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    
    if uid not in players:
        await update.message.reply_text("ابتدا /start کنید")
        return
    
    p = players[uid]
    sound_settings = p.get('sound_settings', {
        'music': True,
        'effects': True,
        'notifications': True,
        'volume': 50
    })
    
    keyboard = [
        [InlineKeyboardButton(
            f"{'🎵' if sound_settings['music'] else '🔇'} موسیقی",
            callback_data="toggle_sound_music"
        )],
        [InlineKeyboardButton(
            f"{'🔊' if sound_settings['effects'] else '🔇'} جلوه‌های صوتی",
            callback_data="toggle_sound_effects"
        )],
        [InlineKeyboardButton(
            f"{'🔔' if sound_settings['notifications'] else '🔕'} صدای اعلانات",
            callback_data="toggle_sound_notifications"
        )],
        [InlineKeyboardButton("🔉 کم کردن صدا", callback_data="volume_down"),
         InlineKeyboardButton("🔊 زیاد کردن صدا", callback_data="volume_up")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_settings")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🎵 تنظیمات صدا\n\n"
        f"🔊 حجم صدا: {sound_settings['volume']}%\n"
        f"🎵 موسیقی: {'فعال' if sound_settings['music'] else 'غیرفعال'}\n"
        f"🔊 جلوه‌ها: {'فعال' if sound_settings['effects'] else 'غیرفعال'}\n"
        f"🔔 اعلانات: {'فعال' if sound_settings['notifications'] else 'غیرفعال'}",
        reply_markup=reply_markup
    )

async def quick_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    guide_text = """
🎮 راهنمای کوتاه

⚡ شروع سریع:
1️⃣ /start برای شروع
2️⃣ پروفایل تکمیل کن
3️⃣ جایزه روزانه بگیر
4️⃣ کار کن و پول درآور
5️⃣ مهارت‌ها را ارتقاء بده

🔥 بهترین راه‌ها:
• هر روز جایزه بگیر
• با دوستان بازی کن  
• در شانس‌آزمایی شرکت کن
• ماموریت‌ها انجام بده
• سطحت را بالا ببر
    """
    
    await update.message.reply_text(guide_text)

async def useful_tips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tips_text = """
💡 نکات مفید

🎯 نکات مهارتی:
• جذابیت → برای دیتینگ و کار مدل
• هوش → برای برنامه‌نویسی و معلمی  
• قدرت → برای ورزش و مبارزه
• چابکی → برای فرار از خطر
• شانس → برای شانس‌آزمایی

💰 نکات مالی:
• پول را در شانس‌آزمایی کم ریسک سرمایه‌گذاری کن
• کارهای سخت‌تر درآمد بیشتری دارن
• با دوستان پول مبادله کن

⚔️ نکات مبارزه:
• انرژی خود را مدیریت کن
• آیتم‌های مفید جمع کن
• قدرت را بالا ببر

👥 نکات اجتماعی:
• مؤدب باش تا دوست بیشتری پیدا کنی
• هدیه بده تا محبوب‌تر شوی
• در گروه‌ها فعال باش
    """
    
    await update.message.reply_text(tips_text)

async def reset_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⚠️ بله، بازنشانی کن!", callback_data="confirm_reset")],
        [InlineKeyboardButton("❌ انصراف", callback_data="cancel_reset")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "⚠️ بازنشانی بازی\n\n"
        "🚨 هشدار: این عمل همه پیشرفت شما را پاک می‌کند!\n\n"
        "شامل:\n"
        "• سطح و XP\n"
        "• پول و آیتم‌ها\n"
        "• دوستان\n"
        "• دستاوردها\n\n"
        "آیا مطمئن هستید؟",
        reply_markup=reply_markup
    )

async def about_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = """
📱 درباره بازی زندگی مجازی ایرانی

🎮 نسخه: 2.0
👨‍💻 سازنده: تیم توسعه ایرانی
🌟 ویژگی‌ها:
• بازی کامل زندگی مجازی
• سیستم اقتصادی پیشرفته
• روابط اجتماعی کامل
• بخش دیتینگ و ازدواج
• مبارزه و ماجراجویی
• بازی‌های مختلف

🔄 آپدیت‌ها:
• بروزرسانی‌های منظم
• امکانات جدید
• رفع باگ‌ها

📞 پشتیبانی: @support_bot
📧 ارتباط با ما: info@game.ir

🙏 از بازی کردن سپاسگزاریم!
    """
    
    await update.message.reply_text(about_text)

async def handle_settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    uid = str(user.id)
    players = load_json('data/players.json')
    
    if uid not in players:
        await query.edit_message_text("ابتدا /start کنید")
        return
    
    p = players[uid]
    data = query.data
    
    if data.startswith("toggle_notif_"):
        setting = data.replace("toggle_notif_", "")
        if 'notifications' not in p:
            p['notifications'] = {}
        
        current = p['notifications'].get(setting, True)
        p['notifications'][setting] = not current
        save_json('data/players.json', players)
        
        await notifications(query, context)
        
    elif data == "toggle_night_mode":
        p['night_mode'] = not p.get('night_mode', False)
        save_json('data/players.json', players)
        await night_mode(query, context)
        
    elif data.startswith("toggle_privacy_"):
        setting = data.replace("toggle_privacy_", "")
        if 'privacy_settings' not in p:
            p['privacy_settings'] = {}
        
        current = p['privacy_settings'].get(setting, True)
        p['privacy_settings'][setting] = not current
        save_json('data/players.json', players)
        
        await privacy(query, context)
        
    elif data.startswith("toggle_sound_"):
        setting = data.replace("toggle_sound_", "")
        if 'sound_settings' not in p:
            p['sound_settings'] = {}
        
        current = p['sound_settings'].get(setting, True)
        p['sound_settings'][setting] = not current
        save_json('data/players.json', players)
        
        await sound_settings(query, context)
        
    elif data == "volume_up":
        if 'sound_settings' not in p:
            p['sound_settings'] = {'volume': 50}
        p['sound_settings']['volume'] = min(100, p['sound_settings'].get('volume', 50) + 10)
        save_json('data/players.json', players)
        await sound_settings(query, context)
        
    elif data == "volume_down":
        if 'sound_settings' not in p:
            p['sound_settings'] = {'volume': 50}
        p['sound_settings']['volume'] = max(0, p['sound_settings'].get('volume', 50) - 10)
        save_json('data/players.json', players)
        await sound_settings(query, context)
        
    elif data == "confirm_reset":
        # Reset user data but keep basic info
        basic_info = {
            'telegram_id': p['telegram_id'],
            'username': p.get('username', ''),
            'name': p['name'],
            'age': p['age'],
            'bio': p['bio'],
            'photo_id': p['photo_id'],
            'approved': True
        }
        
        from utils.tools import init_player
        new_player = init_player(p['telegram_id'], p['name'], p['age'])
        new_player.update(basic_info)
        
        players[uid] = new_player
        save_json('data/players.json', players)
        
        await query.edit_message_text(
            "✅ بازی شما با موفقیت بازنشانی شد!\n"
            "از /start استفاده کنید تا دوباره شروع کنید."
        )
        
    elif data == "cancel_reset":
        await query.edit_message_text("❌ بازنشانی لغو شد.")
        
    elif data == "back_settings":
        await settings(query, context)</new_str>
