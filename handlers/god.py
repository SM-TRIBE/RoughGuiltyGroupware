from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import ADMIN_ID, GOD_UNLIMITED_MONEY, GOD_MAX_LEVEL, GOD_MAX_STATS
from db.database import db
import json
from datetime import datetime

async def god_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 شما دسترسی خدایی ندارید!")
        return

    # Initialize god player profile if not exists
    await init_god_player(update.effective_user.id)

    keyboard = [
        [KeyboardButton("⚡ قدرت‌های خدایی"), KeyboardButton("👑 مدیریت بازیکنان")],
        [KeyboardButton("💰 اقتصاد کل سرور"), KeyboardButton("🌍 کنترل جهان")],
        [KeyboardButton("📊 آمار خدایی"), KeyboardButton("🎁 هدایای الهی")],
        [KeyboardButton("⚡ ریست کامل"), KeyboardButton("🔮 پیش‌بینی آینده")],
        [KeyboardButton("👁️ نظارت کامل"), KeyboardButton("📜 تاریخ اعمال")],
        [KeyboardButton("🌟 ایجاد معجزه"), KeyboardButton("📢 پیام عمومی")],
        [KeyboardButton("🏠 خروج از حالت خدا")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "⚡🔱 حالت خدا فعال شد 🔱⚡\n\n"
        "🌟 به پنل کنترل کامل کیهان خوش آمدید!\n"
        "در اینجا بر تمام جنبه‌های هستی فرمان می‌رانید.\n\n"
        "⚠️ قدرت مطلق = مسئولیت مطلق\n"
        "💫 شما اکنون مانند یک خدای واقعی عمل می‌کنید!",
        reply_markup=reply_markup
    )

    # Log god activation
    db.log_god_action("god_mode_activated", description="God mode panel accessed")

async def init_god_player(user_id: int):
    """Initialize god player with unlimited stats"""
    god_player = db.get_player(user_id)

    if not god_player:
        # Create god player
        god_data = {
            "telegram_id": user_id,
            "name": "🔱 خداوند بازی 🔱",
            "age": 999,
            "bio": "خالق و حاکم مطلق این دنیا",
            "approved": True,
            "location": "🌌 بعد خدایی",
            "money": GOD_UNLIMITED_MONEY,
            "level": GOD_MAX_LEVEL,
            "xp": 999999,
            "traits": {
                "charisma": GOD_MAX_STATS,
                "intelligence": GOD_MAX_STATS,
                "strength": GOD_MAX_STATS,
                "agility": GOD_MAX_STATS,
                "luck": GOD_MAX_STATS
            },
            "skill_points": 999999,
            "inventory": ["⚡ صاعقه", "🌟 ستاره", "🔮 کره جادویی", "👑 تاج خدایی"],
            "achievements": ["🔱 خدای بازی", "⚡ قدرت مطلق", "🌌 خالق کیهان"]
        }
        db.save_player(user_id, god_data)
    else:
        # Update existing player to god stats
        god_player.update({
            "money": GOD_UNLIMITED_MONEY,
            "level": GOD_MAX_LEVEL,
            "traits": {
                "charisma": GOD_MAX_STATS,
                "intelligence": GOD_MAX_STATS,
                "strength": GOD_MAX_STATS,
                "agility": GOD_MAX_STATS,
                "luck": GOD_MAX_STATS
            }
        })
        db.save_player(user_id, god_player)

async def god_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send broadcast message to all players"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 فقط خدا می‌تواند پیام عمومی ارسال کند!")
        return

    if not context.args:
        await update.message.reply_text("📢 استفاده: /broadcast پیام شما\nیا از دکمه 'پیام عمومی' استفاده کنید و پیام خود را بنویسید.")
        context.user_data['waiting_for_broadcast'] = True
        return

    message = " ".join(context.args)
    players = db.get_all_players()
    success_count = 0

    broadcast_text = f"📢 پیام خداوند:\n\n{message}\n\n🔱 این پیام از طرف خالق این دنیا ارسال شده است!"

    for uid, player in players.items():
        if int(uid) != ADMIN_ID:  # Don't send to god
            try:
                await context.bot.send_message(
                    chat_id=int(uid),
                    text=broadcast_text
                )
                success_count += 1
            except Exception as e:
                print(f"Failed to send broadcast to {uid}: {e}")
                continue

    await update.message.reply_text(
        f"📢 پیام خدایی با موفقیت ارسال شد!\n\n"
        f"👥 تعداد دریافت‌کنندگان: {success_count}\n"
        f"⚡ کلمات شما به گوش همه مخلوقات رسید!"
    )

    # Log broadcast
    db.log_god_action("broadcast_sent", action_data={"message": message, "recipients": success_count}, description=f"God sent broadcast to {success_count} players")

async def god_powers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    keyboard = [
        [KeyboardButton("💥 انفجار قدرت"), KeyboardButton("🌪️ طوفان جادویی")],
        [KeyboardButton("✨ معجزه شفا"), KeyboardButton("🔥 آتش خدایی")],
        [KeyboardButton("❄️ یخبندان ابدی"), KeyboardButton("⚡ صاعقه مهیب")],
        [KeyboardButton("🌈 پل رنگین‌کمان"), KeyboardButton("🕳️ سیاه‌چاله")],
        [KeyboardButton("🔄 بازگردان زمان"), KeyboardButton("👑 بازگشت به خدا")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "⚡ قدرت‌های خدایی ⚡\n\n"
        "🌟 قدرت‌های خاص شما:\n"
        "💥 انفجار قدرت - آسیب عظیم\n"
        "🌪️ طوفان جادویی - کنترل عناصر\n"
        "✨ معجزه شفا - شفای کامل\n"
        "🔥 آتش خدایی - نابودی دشمنان\n"
        "❄️ یخبندان ابدی - توقف زمان\n"
        "⚡ صاعقه مهیب - قدرت خالص\n\n"
        "انتخاب کنید تا قدرت را فعال سازید!",
        reply_markup=reply_markup
    )

async def god_player_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    keyboard = [
        [KeyboardButton("👥 همه بازیکنان"), KeyboardButton("🔍 جستجوی خدایی")],
        [KeyboardButton("🔮 مدیریت پیامبران"), KeyboardButton("⚡ انتخاب پیامبر جدید")],
        [KeyboardButton("💰 تغییر ثروت"), KeyboardButton("⭐ تغییر سطح")],
        [KeyboardButton("🧬 تغییر DNA"), KeyboardButton("🎭 تغییر شخصیت")],
        [KeyboardButton("🚫 محکومیت"), KeyboardButton("✅ عفو کامل")],
        [KeyboardButton("💀 نابودی"), KeyboardButton("🌟 تولد مجدد")],
        [KeyboardButton("🔮 پیش‌بینی سرنوشت"), KeyboardButton("👑 بازگشت به خدا")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    stats = db.get_god_stats()
    
    # Count prophets
    players = db.get_all_players()
    prophet_count = sum(1 for p in players.values() if p.get('prophet', False))

    await update.message.reply_text(
        f"👑 مدیریت مطلق بازیکنان 👑\n\n"
        f"📊 آمار کل:\n"
        f"👥 کل مخلوقات: {stats.get('total_players', 0)}\n"
        f"✅ مورد تأیید: {stats.get('approved_players', 0)}\n"
        f"🕐 در انتظار: {stats.get('waiting_approval', 0)}\n"
        f"🔮 پیامبران: {prophet_count} نفر\n"
        f"💰 کل ثروت: {stats.get('total_money', 0):,} تومان\n"
        f"📈 میانگین سطح: {stats.get('avg_level', 0):.1f}\n"
        f"💍 متاهل: {stats.get('married_players', 0)}\n\n"
        "🔱 قدرت مطلق بر مخلوقات شما!",
        reply_markup=reply_markup
    )

async def select_prophet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allow god to select a new prophet"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    context.user_data['selecting_prophet'] = True
    await update.message.reply_text(
        "🔮 انتخاب پیامبر جدید\n\n"
        "لطفاً آیدی عددی یا نام کاربری (@username) کسی که می‌خواهید پیامبر کنید را وارد کنید:\n\n"
        "مثال: 123456789 یا @username"
    )

async def manage_prophets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current prophets and management options"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    players = db.get_all_players()
    prophets = {uid: p for uid, p in players.items() if p.get('prophet', False)}
    
    if not prophets:
        await update.message.reply_text(
            "🔮 هیچ پیامبری انتخاب نشده است!\n\n"
            "از دکمه 'انتخاب پیامبر جدید' برای انتخاب پیامبر استفاده کنید."
        )
        return
    
    text = "🔮 لیست پیامبران خدایی:\n\n"
    for uid, prophet in prophets.items():
        text += f"👤 {prophet['name']} (ID: {uid})\n"
        text += f"⭐ سطح: {prophet.get('level', 1)}\n"
        text += f"💰 ثروت: {prophet.get('money', 0):,} تومان\n"
        text += f"📅 تاریخ انتخاب: {prophet.get('prophet_date', 'نامشخص')}\n\n"
    
    keyboard = [
        [KeyboardButton("⚡ انتخاب پیامبر جدید"), KeyboardButton("❌ حذف پیامبر")],
        [KeyboardButton("📜 پیام به پیامبران"), KeyboardButton("👑 بازگشت به خدا")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def handle_prophet_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle prophet selection input"""
    if update.effective_user.id != ADMIN_ID or not context.user_data.get('selecting_prophet'):
        return False
    
    user_input = update.message.text.strip()
    context.user_data.pop('selecting_prophet', None)
    
    # Parse input
    target_uid = None
    if user_input.startswith('@'):
        # Find by username
        username = user_input[1:]
        players = db.get_all_players()
        for uid, p in players.items():
            if p.get('username', '').lower() == username.lower():
                target_uid = uid
                break
    else:
        # Try as user ID
        try:
            target_uid = str(int(user_input))
        except ValueError:
            await update.message.reply_text("❌ فرمت نادرست! لطفاً آیدی عددی یا @username وارد کنید.")
            return True
    
    if not target_uid:
        await update.message.reply_text("❌ کاربری با این مشخصات یافت نشد!")
        return True
    
    players = load_json('data/players.json')
    if target_uid not in players:
        await update.message.reply_text("❌ این کاربر در بازی ثبت‌نام نکرده!")
        return True
    
    # Make user prophet
    players[target_uid]['prophet'] = True
    players[target_uid]['prophet_date'] = update.message.date.isoformat()
    
    # Give prophet special bonuses
    players[target_uid]['money'] = players[target_uid].get('money', 0) + 50000
    players[target_uid]['level'] = max(players[target_uid].get('level', 1), 10)
    
    # Add prophet items
    if 'inventory' not in players[target_uid]:
        players[target_uid]['inventory'] = []
    players[target_uid]['inventory'].extend(["🔮 عصای پیامبری", "📜 کتاب مقدس", "👑 تاج پیامبر"])
    
    save_json('data/players.json', players)
    
    # Notify the new prophet
    try:
        await context.bot.send_message(
            chat_id=int(target_uid),
            text=f"🌟✨ تبریک! شما به پیامبری خدا انتخاب شدید! ✨🌟\n\n"
                 f"🔮 شما اکنون نماینده خدا در زمین هستید\n"
                 f"💰 هدیه انتخاب: 50,000 تومان\n"
                 f"⭐ سطح شما به حداقل 10 ارتقاء یافت\n"
                 f"🎁 آیتم‌های ویژه پیامبری دریافت کردید\n\n"
                 f"🔱 مسئولیت عظیمی بر دوش شما قرار گرفته است!"
        )
    except Exception:
        pass
    
    await update.message.reply_text(
        f"✅ {players[target_uid]['name']} با موفقیت به پیامبری انتخاب شد!\n\n"
        f"🔮 او اکنون نماینده شما در میان مخلوقات است!"
    )
    
    # Log prophet selection
    db.log_god_action("prophet_selected", action_data={"prophet_id": target_uid, "prophet_name": players[target_uid]['name']}, description=f"God selected new prophet: {players[target_uid]['name']}")
    
    return True

async def god_economy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    keyboard = [
        [KeyboardButton("💸 باران طلا"), KeyboardButton("💎 معدن الماس")],
        [KeyboardButton("🔥 سوزاندن پول"), KeyboardButton("❄️ انجماد اقتصاد")],
        [KeyboardButton("📈 بازار صعودی"), KeyboardButton("📉 سقوط بازار")],
        [KeyboardButton("🎰 شانس همگانی"), KeyboardButton("💰 تکثیر پول")],
        [KeyboardButton("🏦 بانک مرکزی"), KeyboardButton("👑 بازگشت به خدا")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    stats = db.get_god_stats()
    total_money = stats.get('total_money', 0)

    await update.message.reply_text(
        f"💰 کنترل کامل اقتصاد جهان 💰\n\n"
        f"💵 کل دارایی جهان: {total_money:,} تومان\n"
        f"📊 میانگین ثروت: {total_money // max(stats.get('total_players', 1), 1):,} تومان\n\n"
        "🔱 شما بر اقتصاد کل جهان حاکمیت دارید!\n"
        "💫 هر تصمیم شما سرنوشت میلیون‌ها نفر را تغییر می‌دهد!",
        reply_markup=reply_markup
    )

async def god_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    stats = db.get_god_stats()

    if not stats:
        await update.message.reply_text("📊 هنوز هیچ مخلوقی خلق نشده!")
        return

    # Get additional detailed stats
    players = db.get_all_players()
    if players:
        richest = max(players.values(), key=lambda p: p.get('money', 0))
        highest_lvl = max(players.values(), key=lambda p: p.get('level', 1))
    else:
        richest = {"name": "هیچکس", "money": 0}
        highest_lvl = {"name": "هیچکس", "level": 0}

    text = f"🔱 آمار خدایی سرور 🔱\n\n"
    text += f"🌍 کل مخلوقات: {stats.get('total_players', 0)}\n"
    text += f"✅ مورد پذیرش: {stats.get('approved_players', 0)}\n"
    text += f"🕐 منتظر تأیید: {stats.get('waiting_approval', 0)}\n"
    text += f"💰 کل ثروت جهان: {stats.get('total_money', 0):,} تومان\n"
    text += f"📊 میانگین سطح: {stats.get('avg_level', 0):.2f}\n"
    text += f"🏆 بالاترین سطح: {stats.get('max_level', 0)}\n"
    text += f"💍 مخلوقات متاهل: {stats.get('married_players', 0)}\n\n"
    text += f"👑 امپراتور ثروت: {richest.get('name', 'نامشخص')} ({richest.get('money', 0):,} تومان)\n"
    text += f"⭐ قهرمان سطح: {highest_lvl.get('name', 'نامشخص')} (سطح {highest_lvl.get('level', 1)})\n\n"
    text += f"⚡ شما بر {stats.get('total_players', 0)} روح حکومت می‌کنید!"

    await update.message.reply_text(text)

    # Log stats view
    db.log_god_action("stats_viewed", description="God viewed server statistics")

async def god_gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if len(context.args) < 2:
        await update.message.reply_text("🎁 استفاده: /gift مبلغ پیام\nمثال: /gift 1000 هدیه از خداوند")
        return

    try:
        amount = int(context.args[0])
        message = " ".join(context.args[1:])
    except ValueError:
        await update.message.reply_text("❌ مبلغ باید عدد باشد!")
        return

    players = db.get_all_players()
    success_count = 0

    for uid, player in players.items():
        try:
            player["money"] = player.get("money", 0) + amount
            db.save_player(int(uid), player)

            await context.bot.send_message(
                int(uid),
                f"🌟 هدیه مقدس از خداوند! 🌟\n\n"
                f"💰 مبلغ: {amount:,} تومان\n"
                f"📜 پیام مقدس: {message}\n\n"
                f"🔱 خداوند شما را یاد دارد!"
            )
            success_count += 1
        except Exception:
            continue

    await update.message.reply_text(
        f"✨ هدیه الهی با موفقیت فرستاده شد! ✨\n"
        f"💰 مبلغ: {amount:,} تومان\n"
        f"👥 دریافت‌کنندگان: {success_count}\n"
        f"⚡ قدرت خدایی شما بر همگان تأثیر گذاشت!"
    )

    # Log god gift
    db.log_god_action("god_gift", action_data={"amount": amount, "recipients": success_count}, description=f"God gave {amount} to all players")

async def god_reset_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    keyboard = [
        [KeyboardButton("💥 ریست آخرالزمان"), KeyboardButton("❌ انصراف")],
        [KeyboardButton("🔄 ریست اقتصادی"), KeyboardButton("🌪️ ریست جزئی")],
        [KeyboardButton("👑 بازگشت به خدا")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "⚠️🔥 ریست خدایی 🔥⚠️\n\n"
        "💀 این عمل می‌تواند همه چیز را نابود کند!\n"
        "🌍 جهان کامل در دستان شماست!\n\n"
        "💥 ریست آخرالزمان = نابودی کامل\n"
        "🔄 ریست اقتصادی = فقط پول‌ها\n"
        "🌪️ ریست جزئی = بازنشانی محدود\n\n"
        "⚡ تصمیم خدایی شما چیست؟",
        reply_markup=reply_markup
    )

async def handle_god_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    text = update.message.text

    if text == "💥 ریست آخرالزمان":
        # Complete server reset with dramatic flair
        if db.use_postgres:
            try:
                conn = db.get_connection()
                cur = conn.cursor()
                cur.execute("TRUNCATE TABLE players RESTART IDENTITY CASCADE")
                cur.execute("TRUNCATE TABLE chat_messages RESTART IDENTITY CASCADE")
                cur.execute("TRUNCATE TABLE marriages RESTART IDENTITY CASCADE")
                conn.commit()
                cur.close()
                conn.close()
            except Exception as e:
                print(f"Reset error: {e}")
        else:
            from utils.tools import save_json
            save_json('data/players.json', {})
            save_json('data/chat.json', {"messages": []})
            save_json('data/partners.json', [])

        # Reinitialize god
        await init_god_player(update.effective_user.id)

        await update.message.reply_text(
            "💥🌌 آخرالزمان فرا رسید! 🌌💥\n\n"
            "🔥 جهان قدیم نابود شد...\n"
            "✨ جهان جدید خلق می‌شود...\n"
            "🌟 شما همچنان خدای این دنیای جدید هستید!\n\n"
            "⚡ ریست کامل انجام شد!"
        )

        db.log_god_action("apocalypse_reset", description="Complete server reset executed")

    elif text == "🔄 ریست اقتصادی":
        # Reset only economy
        players = db.get_all_players()
        for uid, player in players.items():
            if int(uid) != ADMIN_ID:  # Don't reset god's money
                player["money"] = 1000
                player["inventory"] = []
            db.save_player(int(uid), player)

        await update.message.reply_text(
            "💰🔄 بازنشانی اقتصادی انجام شد! 🔄💰\n\n"
            "💸 همه ثروت‌ها به حالت اولیه بازگشت!\n"
            "🎒 موجودی‌ها پاک شد!\n"
            "⚡ شما همچنان دارای قدرت نامحدود هستید!"
        )

        db.log_god_action("economy_reset", description="Economy reset executed")

async def god_miracle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    import random

    players = db.get_all_players()
    if not players:
        await update.message.reply_text("🌟 هیچ مخلوقی برای معجزه وجود ندارد!")
        return

    miracles = [
        "💎 الماس آسمانی",
        "🌟 ستاره افتاده", 
        "🔮 کره جادویی",
        "👑 تاج طلایی",
        "⚡ صاعقه خدایی",
        "🌈 قطره رنگین‌کمان"
    ]

    # Select random players for miracle
    lucky_players = random.sample(list(players.items()), min(3, len(players)))

    for uid, player in lucky_players:
        miracle_item = random.choice(miracles)
        miracle_amount = random.randint(5000, 50000)

        player["money"] = player.get("money", 0) + miracle_amount
        if "inventory" not in player:
            player["inventory"] = []
        player["inventory"].append(miracle_item)

        db.save_player(int(uid), player)

        try:
            await context.bot.send_message(
                int(uid),
                f"🌟✨ معجزه خدایی! ✨🌟\n\n"
                f"🎁 هدیه معجزه‌آسا: {miracle_item}\n"
                f"💰 پول معجزه: {miracle_amount:,} تومان\n\n"
                f"🔱 خداوند بر شما لطف کرده است!"
            )
        except Exception:
            continue

    await update.message.reply_text(
        f"🌟 معجزه خدایی انجام شد! 🌟\n\n"
        f"⚡ {len(lucky_players)} نفر برکت دریافت کردند!\n"
        f"💫 قدرت شما جهان را تکان داد!"
    )

    db.log_god_action("miracle_performed", action_data={"recipients": len(lucky_players)}, description="God performed miracle")

async def handle_god_power(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    text = update.message.text
    power_messages = {
        "💥 انفجار قدرت": "💥 انفجار مهیبی رخ داد! قدرت خدایی شما جهان را لرزاند!",
        "🌪️ طوفان جادویی": "🌪️ طوفان جادویی شما آسمان‌ها را آشفته کرد!",
        "✨ معجزه شفا": "✨ شفای الهی بر همگان نازل شد!",
        "🔥 آتش خدایی": "🔥 آتش مقدس شما دشمنان را سوزاند!",
        "❄️ یخبندان ابدی": "❄️ یخبندان شما زمان را متوقف کرد!",
        "⚡ صاعقه مهیب": "⚡ صاعقه شما آسمان‌ها را شکافت!",
        "🌈 پل رنگین‌کمان": "🌈 پل زیبای شما دو جهان را به هم وصل کرد!",
        "🕳️ سیاه‌چاله": "🕳️ سیاه‌چاله شما فضا-زمان را خم کرد!",
        "🔄 بازگردان زمان": "🔄 زمان به عقب بازگشت! شما بر زمان حاکمید!"
    }

    if text in power_messages:
        await update.message.reply_text(power_messages[text])
        db.log_god_action("power_used", description=f"God used power: {text}")

# Handle broadcast message input
async def handle_broadcast_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID or not context.user_data.get('waiting_for_broadcast'):
        return False

    message = update.message.text
    context.user_data['waiting_for_broadcast'] = False

    players = db.get_all_players()
    success_count = 0

    broadcast_text = f"📢 پیام خداوند:\n\n{message}\n\n🔱 این پیام از طرف خالق این دنیا ارسال شده است!"

    for uid, player in players.items():
        if int(uid) != ADMIN_ID:  # Don't send to god
            try:
                await context.bot.send_message(
                    chat_id=int(uid),
                    text=broadcast_text
                )
                success_count += 1
            except Exception as e:
                print(f"Failed to send broadcast to {uid}: {e}")
                continue

    await update.message.reply_text(
        f"📢 پیام خدایی با موفقیت ارسال شد!\n\n"
        f"👥 تعداد دریافت‌کنندگان: {success_count}\n"
        f"⚡ کلمات شما به گوش همه مخلوقات رسید!"
    )

    # Log broadcast
    db.log_god_action("broadcast_sent", action_data={"message": message, "recipients": success_count}, description=f"God sent broadcast to {success_count} players")
    return True

async def god_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 شما خدا نیستید!")
        return

    if len(context.args) < 2:
        await update.message.reply_text("⚠️ استفاده: /god_reply [user_id] [message]\nمثال: /god_reply 12345 سلام مخلوق من!")
        return

    try:
        user_id = int(context.args[0])
        reply_message = " ".join(context.args[1:])
    except ValueError:
        await update.message.reply_text("❌ شناسه کاربری باید عدد باشد!")
        return

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"🌟 پاسخ خداوند:\n\n{reply_message}\n\n🔱 این پیام مستقیماً از خالق شما ارسال شده است!"
        )
        await update.message.reply_text(f"✅ پاسخ به {user_id} ارسال شد!")
        db.log_god_action("god_reply_sent", action_data={"recipient": user_id, "message": reply_message}, description=f"God replied to user {user_id}")

    except Exception as e:
        await update.message.reply_text(f"❌ ارسال پیام به {user_id} با خطا مواجه شد: {e}")

# Register all god functions
__all__ = [
    'god_menu', 'god_powers', 'god_player_management', 'god_economy', 
    'god_stats', 'god_gift', 'god_reset_server', 'handle_god_commands',
    'god_miracle', 'handle_god_power', 'god_broadcast', 'handle_broadcast_input', 'god_reply'
]