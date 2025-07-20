
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.tools import init_player, save_json, load_json
from config import ADMIN_ID, AGE_MIN
import json

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    
    # Check if user exists and is approved
    if uid in players:
        if players[uid].get("approved"):
            await show_main_square(update, context)
            return
        elif players[uid].get("waiting_approval"):
            await update.message.reply_text(
                "🕐 درخواست شما در انتظار تأیید مدیر است.\n"
                "لطفاً صبر کنید تا پروفایل شما بررسی شود."
            )
            return
    
    # Start registration process
    await update.message.reply_text(
        "🌟 سلام! به بازی زندگی مجازی ایرانی خوش آمدید!\n\n"
        "برای شروع بازی، ابتدا باید پروفایل خود را تکمیل کنید.\n"
        "لطفاً نام واقعی خود را وارد کنید:"
    )
    
    # Initialize user data for registration
    context.user_data['registration_step'] = 'name'

async def handle_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)
    step = context.user_data.get('registration_step')
    
    if step == 'name':
        name = update.message.text.strip()
        if len(name) < 2:
            await update.message.reply_text("❌ نام باید حداقل ۲ کاراکتر باشد. دوباره وارد کنید:")
            return
            
        context.user_data['user_name'] = name
        context.user_data['registration_step'] = 'age'
        await update.message.reply_text(f"✅ نام شما: {name}\n\nحالا سن خود را وارد کنید:")
        
    elif step == 'age':
        try:
            age = int(update.message.text)
            if age < AGE_MIN:
                await update.message.reply_text(f"❌ حداقل سن مجاز {AGE_MIN} سال است.")
                return
            if age > 100:
                await update.message.reply_text("❌ لطفاً سن واقعی خود را وارد کنید:")
                return
                
            context.user_data['user_age'] = age
            context.user_data['registration_step'] = 'bio'
            await update.message.reply_text(
                f"✅ سن شما: {age}\n\n"
                "حالا یک توضیح کوتاه از خودتان بنویسید (حداقل ۱۰ کلمه):"
            )
            
        except ValueError:
            await update.message.reply_text("❌ لطفاً فقط عدد وارد کنید:")
            
    elif step == 'bio':
        bio = update.message.text.strip()
        if len(bio.split()) < 10:
            await update.message.reply_text("❌ توضیحات باید حداقل ۱۰ کلمه باشد. دوباره بنویسید:")
            return
            
        context.user_data['user_bio'] = bio
        context.user_data['registration_step'] = 'photo'
        await update.message.reply_text(
            f"✅ توضیحات شما ثبت شد.\n\n"
            "حالا یک عکس از خودتان ارسال کنید:"
        )
        
    elif step == 'photo':
        if not update.message.photo:
            await update.message.reply_text("❌ لطفاً یک عکس ارسال کنید:")
            return
            
        photo = update.message.photo[-1]  # Get highest quality photo
        context.user_data['user_photo'] = photo.file_id
        context.user_data['registration_step'] = 'voice'
        
        await update.message.reply_text(
            "✅ عکس شما ثبت شد.\n\n"
            "حالا یک پیام صوتی ارسال کنید که در آن نام و سن خود را بگویید.\n"
            "این برای تأیید هویت شما توسط مدیر استفاده خواهد شد:"
        )
        
    elif step == 'voice':
        if not update.message.voice:
            await update.message.reply_text("❌ لطفاً یک پیام صوتی ارسال کنید:")
            return
            
        voice = update.message.voice
        context.user_data['user_voice'] = voice.file_id
        
        # Save user data for approval
        await save_for_approval(update, context)

async def save_for_approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)
    
    # Save user data
    players = load_json('data/players.json')
    players[uid] = {
        "telegram_id": user.id,
        "username": user.username or "",
        "name": context.user_data['user_name'],
        "age": context.user_data['user_age'],
        "bio": context.user_data['user_bio'],
        "photo_id": context.user_data['user_photo'],
        "voice_id": context.user_data['user_voice'],
        "waiting_approval": True,
        "approved": False,
        "registration_date": str(update.message.date),
        "location": "در انتظار تأیید",
        "traits": {
            "charisma": 5,
            "intelligence": 5,
            "strength": 5,
            "agility": 5,
            "luck": 5
        },
        "money": 0,
        "level": 1,
        "xp": 0,
        "inventory": [],
        "partner": None,
        "job": None,
        "skills": {},
        "achievements": [],
        "last_daily": None,
        "skill_points": 0
    }
    save_json('data/players.json', players)
    
    # Send to admin for approval
    admin_message = (
        f"🔔 درخواست عضویت جدید:\n\n"
        f"👤 نام: {context.user_data['user_name']}\n"
        f"🎂 سن: {context.user_data['user_age']}\n"
        f"📝 توضیحات: {context.user_data['user_bio']}\n"
        f"👤 آیدی تلگرام: @{user.username or 'ندارد'}\n"
        f"🆔 آیدی عددی: {user.id}\n\n"
        f"برای تأیید یا رد، از دکمه‌های زیر استفاده کنید:"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("✅ تأیید", callback_data=f"approve_{uid}"),
            InlineKeyboardButton("❌ رد", callback_data=f"reject_{uid}")
        ],
        [InlineKeyboardButton("👁️ مشاهده جزئیات", callback_data=f"details_{uid}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        # Send photo
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=context.user_data['user_photo'],
            caption=admin_message,
            reply_markup=reply_markup
        )
        
        # Send voice
        await context.bot.send_voice(
            chat_id=ADMIN_ID,
            voice=context.user_data['user_voice'],
            caption=f"🎤 پیام صوتی {context.user_data['user_name']}"
        )
        
    except Exception as e:
        print(f"خطا در ارسال به مدیر: {e}")
    
    # Clear user data
    context.user_data.clear()
    
    await update.message.reply_text(
        "✅ ثبت‌نام شما با موفقیت انجام شد!\n\n"
        "🕐 پروفایل شما برای بررسی به مدیر ارسال شده است.\n"
        "پس از تأیید، می‌توانید وارد بازی شوید.\n\n"
        "معمولاً این فرآیند کمتر از ۲۴ ساعت طول می‌کشد."
    )

async def approve_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id != ADMIN_ID:
        await query.edit_message_text("🚫 شما دسترسی لازم ندارید!")
        return
    
    action, uid = query.data.split('_', 1)
    players = load_json('data/players.json')
    
    if uid not in players:
        await query.edit_message_text("❌ کاربر یافت نشد!")
        return
    
    if action == "approve":
        players[uid]["approved"] = True
        players[uid]["waiting_approval"] = False
        players[uid]["location"] = "میدان اصلی"
        players[uid]["money"] = 1000  # Starting money
        save_json('data/players.json', players)
        
        # Notify user
        try:
            await context.bot.send_message(
                chat_id=int(uid),
                text="🎉 تبریک! پروفایل شما تأیید شد!\n\n"
                     "حالا می‌توانید با ارسال /start وارد بازی شوید و از تمام امکانات آن استفاده کنید.\n\n"
                     "🎁 هدیه شروع: ۱۰۰۰ تومان به حساب شما واریز شد!"
            )
        except Exception:
            pass
            
        await query.edit_message_text(
            f"✅ کاربر {players[uid]['name']} تأیید شد!\n"
            f"پیام تأیید برای او ارسال شده است."
        )
        
    elif action == "reject":
        user_name = players[uid]['name']
        del players[uid]
        save_json('data/players.json', players)
        
        # Notify user
        try:
            await context.bot.send_message(
                chat_id=int(uid),
                text="❌ متأسفانه پروفایل شما تأیید نشد.\n\n"
                     "دلایل احتمالی:\n"
                     "• اطلاعات ناکافی یا نامناسب\n"
                     "• عدم رعایت قوانین\n\n"
                     "می‌توانید مجدداً با /start تلاش کنید."
            )
        except Exception:
            pass
            
        await query.edit_message_text(f"❌ کاربر {user_name} رد شد!")
        
    elif action == "details":
        user_data = players[uid]
        details = (
            f"📋 جزئیات کامل کاربر:\n\n"
            f"👤 نام: {user_data['name']}\n"
            f"🎂 سن: {user_data['age']}\n"
            f"📝 توضیحات: {user_data['bio']}\n"
            f"📅 تاریخ ثبت‌نام: {user_data['registration_date']}\n"
            f"🆔 آیدی: {uid}\n"
            f"📱 یوزرنیم: @{user_data.get('username', 'ندارد')}"
        )
        await query.edit_message_text(details)

async def show_main_square(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    p = players.get(uid, {})
    
    level = p.get('level', 1)
    
    # Base buttons available to all levels
    main_keyboard = [
        [KeyboardButton("👤 پروفایل"), KeyboardButton("💰 اقتصاد")],
        [KeyboardButton("🗺️ اکتشاف"), KeyboardButton("💬 کافه گپ")],
        [KeyboardButton("🛍️ فروشگاه"), KeyboardButton("🏨 هتل")]
    ]
    
    # Level-based features
    if level >= 2:
        main_keyboard.append([KeyboardButton("💼 کار"), KeyboardButton("⚔️ ماموریت‌ها")])
    
    if level >= 3:
        main_keyboard.append([KeyboardButton("💍 ازدواج"), KeyboardButton("🏰 سیاه‌چال‌ها")])
        
    if level >= 4:
        main_keyboard.append([KeyboardButton("🎮 بازی‌ها"), KeyboardButton("👥 اجتماعی")])
        
    if level >= 5:
        main_keyboard.append([KeyboardButton("🎒 کیف"), KeyboardButton("📈 مهارت‌ها")])
        
    if level >= 7:
        main_keyboard.append([KeyboardButton("🏅 دستاوردها"), KeyboardButton("🏆 رتبه‌بندی")])
    
    # Admin features
    if user.id == ADMIN_ID:
        main_keyboard.append([KeyboardButton("👑 حالت خدا")])
    
    main_keyboard.append([KeyboardButton("⚙️ تنظیمات"), KeyboardButton("❓ راهنما")])
    
    reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
    
    welcome_text = (
        f"🏛️ میدان اصلی\n\n"
        f"سلام {p.get('name', 'بازیکن')} عزیز!\n"
        f"به میدان اصلی شهر خوش آمدید.\n\n"
        f"📊 وضعیت شما:\n"
        f"💰 پول: {p.get('money', 0):,} تومان\n"
        f"⭐ سطح: {level}\n"
        f"📍 مکان: {p.get('location', 'میدان اصلی')}\n\n"
    )
    
    if level < 2:
        welcome_text += "💡 برای باز شدن قابلیت‌های بیشتر، سطح خود را بالا ببرید!"
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)
