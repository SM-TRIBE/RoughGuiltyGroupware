from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from utils.tools import load_json, save_json
from config import ADMIN_ID

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    p = players.get(uid)

    if not p:
        await update.message.reply_text("پروفایلی موجود نیست. لطفاً /start کنید.")
        return

    if not p.get("approved") and user.id != ADMIN_ID:
        await update.message.reply_text("لطفاً ابتدا تأیید پروفایل را انتظار بکشید.")
        return

    # Special God profile display
    if user.id == ADMIN_ID:
        await show_god_profile(update, context, p)
        return

    # Check if user is prophet
    is_prophet = p.get('prophet', False)

    traits_text = ""
    for trait, value in p.get("traits", {}).items():
        persian_names = {
            "charisma": "جذابیت",
            "intelligence": "هوش", 
            "strength": "قدرت",
            "agility": "چابکی",
            "luck": "شانس"
        }
        persian_name = persian_names.get(trait, trait)
        bar = "█" * min(value, 20) + "░" * max(0, 20 - value)
        traits_text += f"• {persian_name}: {bar} {value}/20\n"

    # Status icons
    status_icons = []
    if is_prophet:
        status_icons.append("🔮 پیامبر")
    if p.get('partner'):
        status_icons.append("💍 متاهل")
    if p.get('job'):
        status_icons.append(f"💼 {p['job']}")

    status_text = " | ".join(status_icons) if status_icons else "🆓 آزاد"

    text = f"{'🔮' if is_prophet else '👤'} پروفایل {p['name']}\n"
    text += f"📊 وضعیت: {status_text}\n\n"
    text += f"🎂 سن: {p.get('age', 'نامشخص')}\n"
    text += f"📍 مکان: {p.get('location', 'میدان اصلی')}\n"
    text += f"💰 پول: {p.get('money', 0):,} تومان\n"
    text += f"⭐ سطح: {p.get('level', 1)} (XP: {p.get('xp', 0)})\n"
    text += f"🎯 امتیاز مهارت: {p.get('skill_points', 0)}\n\n"
    text += f"📊 ویژگی‌ها:\n{traits_text}\n"

    if p.get("inventory"):
        text += f"🎒 آیتم‌ها: {', '.join(p['inventory'][:5])}"
        if len(p['inventory']) > 5:
            text += f" (+{len(p['inventory']) - 5} دیگر)"
        text += "\n"

    if p.get("achievements"):
        text += f"🏅 دستاوردها: {len(p['achievements'])} عدد\n"

    if p.get("bio"):
        text += f"\n📝 توضیحات: {p['bio']}"

    # Add edit button for profile owner
    keyboard = [
        [KeyboardButton("✏️ ویرایش پروفایل"), KeyboardButton("📸 تغییر عکس")],
        [KeyboardButton("🏠 بازگشت به منو اصلی")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(text, reply_markup=reply_markup)

async def show_god_profile(update: Update, context: ContextTypes.DEFAULT_TYPE, p: dict):
    """Special profile display for God"""
    text = f"🔱⚡ پروفایل خداوند کیهان ⚡🔱\n\n"
    text += f"👑 نام: {p.get('name', 'خداوند بازی')}\n"
    text += f"🌌 مقام: خالق و حاکم مطلق\n"
    text += f"⚡ قدرت: نامحدود ∞\n"
    text += f"🎂 سن: ابدی\n"
    text += f"📍 مکان: {p.get('location', '🌌 بعد خدایی')}\n"
    text += f"💰 ثروت: ∞ (نامحدود)\n"
    text += f"⭐ سطح: {p.get('level', 999)} (حداکثر)\n\n"

    text += f"🔱 ویژگی‌های خدایی:\n"
    for trait, value in p.get("traits", {}).items():
        persian_names = {
            "charisma": "جذابیت",
            "intelligence": "هوش", 
            "strength": "قدرت",
            "agility": "چابکی",
            "luck": "شانس"
        }
        persian_name = persian_names.get(trait, trait)
        bar = "█" * 20  # Full bar for god
        text += f"• {persian_name}: {bar} ∞/∞\n"

    text += f"\n⚡ قدرت‌های خاص:\n"
    text += f"🌟 خلق و نابودی مخلوقات\n"
    text += f"💫 کنترل کامل اقتصاد\n"
    text += f"🔮 انتخاب پیامبران\n"
    text += f"📢 پیام‌رسانی به همه مخلوقات\n"
    text += f"⏰ کنترل زمان و مکان\n"

    # Show current prophets
    players = load_json('data/players.json')
    prophets = [p_data['name'] for p_data in players.values() if p_data.get('prophet')]
    if prophets:
        text += f"\n👑 پیامبران فعلی: {', '.join(prophets)}\n"

    if p.get("bio"):
        text += f"\n📜 فرمان خدایی: {p['bio']}"

    keyboard = [
        [KeyboardButton("✏️ ویرایش فرمان"), KeyboardButton("🔮 انتخاب پیامبر")],
        [KeyboardButton("👥 لیست پیامبران"), KeyboardButton("❌ برکناری پیامبر")],
        [KeyboardButton("👑 بازگشت به حالت خدا")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(text, reply_markup=reply_markup)

async def select_prophet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allow god to select prophets"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 فقط خداوند می‌تواند پیامبر انتخاب کند!")
        return

    players = load_json('data/players.json')
    eligible_players = []

    for uid, player in players.items():
        if (player.get('approved') and 
            not player.get('prophet') and 
            int(uid) != ADMIN_ID and
            player.get('level', 1) >= 5):
            eligible_players.append((uid, player))

    if not eligible_players:
        await update.message.reply_text("هیچ بازیکن واجد شرایطی برای پیامبری یافت نشد!")
        return

    # Show list of eligible players
    text = "🔮 انتخاب پیامبر\n\n"
    text += "بازیکنان واجد شرایط (سطح 5+):\n\n"

    for uid, player in eligible_players[:10]:  # Show max 10
        text += f"👤 {player['name']} - سطح {player.get('level', 1)}\n"
        text += f"   💰 ثروت: {player.get('money', 0):,}\n"
        text += f"   🎯 XP: {player.get('xp', 0)}\n"
        text += f"   🆔 ID: {uid}\n\n"

    await update.message.reply_text(
        text + 
        "برای انتخاب پیامبر، فرمان زیر را ارسال کنید:\n"
        "پیامبر [ID بازیکن]\n\n"
        "مثال: پیامبر 123456789"
    )

async def handle_prophet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle prophet selection command"""
    if update.effective_user.id != ADMIN_ID:
        return False

    text = update.message.text
    if not text.startswith("پیامبر "):
        return False

    try:
        target_id = text.split()[1]
        players = load_json('data/players.json')

        if target_id not in players:
            await update.message.reply_text("❌ بازیکن یافت نشد!")
            return True

        target_player = players[target_id]

        if not target_player.get('approved'):
            await update.message.reply_text("❌ این بازیکن تأیید نشده است!")
            return True

        if target_player.get('prophet'):
            await update.message.reply_text("❌ این بازیکن از قبل پیامبر است!")
            return True

        if target_player.get('level', 1) < 5:
            await update.message.reply_text("❌ این بازیکن سطح کافی ندارد! (حداقل سطح 5)")
            return True

        # Make the player a prophet
        target_player['prophet'] = True
        target_player['prophet_since'] = update.message.date.isoformat()

        # Give prophet bonuses
        target_player['money'] = target_player.get('money', 0) + 10000
        for trait in target_player['traits']:
            target_player['traits'][trait] = min(20, target_player['traits'][trait] + 5)

        save_json('data/players.json', players)

        # Notify the new prophet
        try:
            await context.bot.send_message(
                chat_id=int(target_id),
                text=f"🔮⚡ تبریک! شما به عنوان پیامبر انتخاب شدید! ⚡🔮\n\n"
                     f"🎁 هدایای پیامبری:\n"
                     f"💰 +10,000 تومان\n"
                     f"📈 +5 امتیاز به همه مهارت‌ها\n"
                     f"👑 دسترسی به قدرت‌های خاص\n\n"
                     f"شما اکنون نماینده خداوند در این دنیا هستید!"
            )
        except Exception:
            pass

        await update.message.reply_text(
            f"✅ {target_player['name']} با موفقیت به عنوان پیامبر انتخاب شد!\n"
            f"🎁 هدایای پیامبری به او اعطا شده است."
        )

    except (IndexError, ValueError):
        await update.message.reply_text("❌ فرمت نادرست! استفاده کنید: پیامبر [ID]")

    return True

async def dismiss_prophet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allow god to dismiss prophets"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 فقط خداوند می‌تواند پیامبر را برکنار کند!")
        return

    players = load_json('data/players.json')
    prophets = [(uid, p) for uid, p in players.items() if p.get('prophet')]

    if not prophets:
        await update.message.reply_text("هیچ پیامبری موجود نیست!")
        return

    text = "👑 لیست پیامبران فعلی:\n\n"

    for uid, prophet in prophets:
        text += f"🔮 {prophet['name']}\n"
        text += f"   📅 پیامبر از: {prophet.get('prophet_since', 'نامشخص')}\n"
        text += f"   ⭐ سطح: {prophet.get('level', 1)}\n"
        text += f"   🆔 ID: {uid}\n\n"

    await update.message.reply_text(
        text + 
        "برای برکناری پیامبر، فرمان زیر را ارسال کنید:\n"
        "برکناری [ID پیامبر]\n\n"
        "مثال: برکناری 123456789"
    )

async def handle_dismiss_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle prophet dismissal command"""
    if update.effective_user.id != ADMIN_ID:
        return False

    text = update.message.text
    if not text.startswith("برکناری "):
        return False

    try:
        target_id = text.split()[1]
        players = load_json('data/players.json')

        if target_id not in players:
            await update.message.reply_text("❌ بازیکن یافت نشد!")
            return True

        target_player = players[target_id]

        if not target_player.get('prophet'):
            await update.message.reply_text("❌ این بازیکن پیامبر نیست!")
            return True

        # Remove prophet status
        target_player['prophet'] = False
        target_player.pop('prophet_since', None)

        save_json('data/players.json', players)

        # Notify the dismissed prophet
        try:
            await context.bot.send_message(
                chat_id=int(target_id),
                text=f"⚡ شما از مقام پیامبری برکنار شدید.\n"
                     f"قدرت‌های خاص شما باطل شده است."
            )
        except Exception:
            pass

        await update.message.reply_text(
            f"✅ {target_player['name']} از مقام پیامبری برکنار شد!"
        )

    except (IndexError, ValueError):
        await update.message.reply_text("❌ فرمت نادرست! استفاده کنید: برکناری [ID]")

    return True

async def edit_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle profile editing"""
    keyboard = [
        [KeyboardButton("📝 تغییر توضیحات"), KeyboardButton("📸 تغییر عکس")],
        [KeyboardButton("🏷️ تغییر نام"), KeyboardButton("🎂 تغییر سن")],
        [KeyboardButton("❌ انصراف")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "✏️ ویرایش پروفایل\n\n"
        "کدام بخش را می‌خواهید تغییر دهید؟",
        reply_markup=reply_markup
    )

async def handle_profile_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle profile edit selections"""
    text = update.message.text
    user = update.effective_user

    if text == "📝 تغییر توضیحات":
        context.user_data['edit_mode'] = 'bio'
        await update.message.reply_text(
            "📝 توضیحات جدید خود را بنویسید:\n"
            "(حداقل 10 کلمه)"
        )
    elif text == "🏷️ تغییر نام":
        context.user_data['edit_mode'] = 'name'
        await update.message.reply_text(
            "🏷️ نام جدید خود را وارد کنید:\n"
            "(حداقل 2 کاراکتر)"
        )
    elif text == "🎂 تغییر سن":
        context.user_data['edit_mode'] = 'age'
        await update.message.reply_text(
            "🎂 سن جدید خود را وارد کنید:\n"
            f"(حداقل {18} سال)"
        )
    elif text == "📸 تغییر عکس":
        context.user_data['edit_mode'] = 'photo'
        await update.message.reply_text(
            "📸 عکس جدید خود را ارسال کنید:"
        )

async def process_profile_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process the actual profile edits"""
    user = update.effective_user
    uid = str(user.id)
    edit_mode = context.user_data.get('edit_mode')

    if not edit_mode:
        return False

    players = load_json('data/players.json')
    p = players.get(uid, {})

    if edit_mode == 'bio':
        new_bio = update.message.text.strip()
        if len(new_bio.split()) < 10:
            await update.message.reply_text("❌ توضیحات باید حداقل 10 کلمه باشد. دوباره بنویسید:")
            return True

        p['bio'] = new_bio
        players[uid] = p
        save_json('data/players.json', players)
        context.user_data.pop('edit_mode', None)

        await update.message.reply_text(
            "✅ توضیحات شما با موفقیت تغییر کرد!\n"
            "برای مشاهده پروفایل جدید، دکمه 'پروفایل' را بزنید."
        )

    elif edit_mode == 'name':
        new_name = update.message.text.strip()
        if len(new_name) < 2:
            await update.message.reply_text("❌ نام باید حداقل 2 کاراکتر باشد. دوباره وارد کنید:")
            return True

        p['name'] = new_name
        players[uid] = p
        save_json('data/players.json', players)
        context.user_data.pop('edit_mode', None)

        await update.message.reply_text(
            f"✅ نام شما به '{new_name}' تغییر کرد!\n"
            "برای مشاهده پروفایل جدید، دکمه 'پروفایل' را بزنید."
        )

    elif edit_mode == 'age':
        try:
            new_age = int(update.message.text)
            if new_age < 18:
                await update.message.reply_text("❌ حداقل سن مجاز 18 سال است. دوباره وارد کنید:")
                return True
            if new_age > 100:
                await update.message.reply_text("❌ لطفاً سن واقعی خود را وارد کنید:")
                return True

            p['age'] = new_age
            players[uid] = p
            save_json('data/players.json', players)
            context.user_data.pop('edit_mode', None)

            await update.message.reply_text(
                f"✅ سن شما به {new_age} تغییر کرد!\n"
                "برای مشاهده پروفایل جدید، دکمه 'پروفایل' را بزنید."
            )

        except ValueError:
            await update.message.reply_text("❌ لطفاً فقط عدد وارد کنید:")
            return True

    elif edit_mode == 'photo':
        if not update.message.photo:
            await update.message.reply_text("❌ لطفاً یک عکس ارسال کنید:")
            return True

        photo = update.message.photo[-1]
        p['photo_id'] = photo.file_id
        players[uid] = p
        save_json('data/players.json', players)
        context.user_data.pop('edit_mode', None)

        await update.message.reply_text(
            f"✅ عکس پروفایل شما تغییر کرد!\n"
            "برای مشاهده پروفایل جدید، دکمه 'پروفایل' را بزنید."
        )

    # Return to main menu
    keyboard = [
        [KeyboardButton("👤 پروفایل"), KeyboardButton("💰 اقتصاد")],
        [KeyboardButton("🗺️ اکتشاف"), KeyboardButton("💬 کافه گپ")],
        [KeyboardButton("🛍️ فروشگاه"), KeyboardButton("🏨 هتل")],
        [KeyboardButton("🏠 بازگشت به منو اصلی")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("عملیات تکمیل شد.", reply_markup=reply_markup)

    return True