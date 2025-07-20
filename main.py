import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config import BOT_TOKEN, ADMIN_ID
from utils.tools import load_json, save_json

# Import all handlers
from handlers import start, profile, admin, zones, shop, marriage, leaderboard, economy
from handlers import chat, hotel, jobs, rpg, god, achievements, minigames, social

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Use the proper registration system from start.py
    await start.start(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user
    uid = str(user.id)

    # Check if user exists and is approved
    players = load_json('data/players.json')

    # Handle registration process
    if context.user_data.get('registration_step'):
        await start.handle_registration(update, context)
        return

    # Check if user needs to register or is waiting approval
    if uid not in players:
        await start.start(update, context)
        return
    elif not players[uid].get("approved"):
        if players[uid].get("waiting_approval"):
            await update.message.reply_text(
                "🕐 درخواست شما در انتظار تأیید مدیر است.\n"
                "لطفاً صبر کنید تا پروفایل شما بررسی شود."
            )
        else:
            await start.start(update, context)
        return

    # Handle chat messages
    if context.user_data.get('waiting_for_message'):
        await chat.receive_chat_message(update, context)
        return

    # Handle god broadcast input
    if await god.handle_broadcast_input(update, context):
        return

    # Handle profile editing first
    if context.user_data.get('edit_mode'):
        if await profile.process_profile_edit(update, context):
            return
    
    # Main menu navigation
    if text == "👤 پروفایل":
        await profile.profile(update, context)
    elif text == "✏️ ویرایش پروفایل":
        await profile.edit_profile(update, context)
    elif text in ["📝 تغییر توضیحات", "🏷️ تغییر نام", "🎂 تغییر سن", "📸 تغییر عکس"]:
        await profile.handle_profile_edit(update, context)
    elif text == "🗺️ اکتشاف" or text == "🗺️ سفر":
        await zones.travel(update, context)
    elif text == "🛍️ فروشگاه":
        await shop.shop(update, context)
    elif text == "💼 کار":
        await jobs.job_center(update, context)
    elif text == "💬 کافه گپ":
        await chat.public_chat(update, context)
    elif text == "🏨 هتل":
        await hotel.hotel_menu(update, context)
    elif text == "💍 ازدواج":
        await marriage.marry(update, context)
    elif text == "🏆 رتبه‌بندی":
        await leaderboard.leaderboard(update, context)
    elif text == "💰 اقتصاد":
        await economy.economy_menu(update, context)
    elif text == "⚔️ ماموریت‌ها":
        await rpg.quest_menu(update, context)
    elif text == "🏰 سیاه‌چال‌ها":
        await rpg.dungeon_menu(update, context)
    elif text == "🎒 کیف":
        await rpg.inventory_menu(update, context)
    elif text == "📈 مهارت‌ها":
        await rpg.skills_menu(update, context)
    elif text == "🏅 دستاوردها":
        await achievements.achievements_menu(update, context)
    elif text == "🎮 بازی‌ها":
        await minigames.minigames_menu(update, context)
    elif text == "👥 اجتماعی":
        await social.social_menu(update, context)
    elif text == "👑 حالت خدا":
        await god.god_menu(update, context)
    elif text == "💕 دیتینگ":
        from handlers import dating
        await dating.dating_menu(update, context)
    elif text == "💕 جستجوی شریک":
        from handlers import dating
        await dating.find_partner(update, context)
    elif text == "📱 دیتینگ آنلاین":
        from handlers import dating
        await dating.online_dating(update, context)
    elif text == "💝 خرید هدیه":
        from handlers import dating
        await dating.dating_gifts(update, context)
    elif text == "🌟 پروفایل دیتینگ":
        from handlers import dating
        await dating.dating_profile(update, context)
    elif text == "💬 چت عاشقانه":
        from handlers import dating
        await dating.dating_chat(update, context)
    elif text == "📊 آمار قرارها":
        from handlers import dating
        await dating.dating_stats(update, context)
    elif text == "🎯 ماچ‌میکر هوشمند":
        from handlers import dating
        await dating.smart_matchmaker(update, context)
    elif text == "💔 تاریخچه روابط":
        from handlers import dating
        await dating.relationship_history(update, context)
    elif text == "🏛️ معبد":
        await god.temple_menu(update, context)
    elif text == "⚡ انتخاب پیامبر جدید":
        await god.select_prophet(update, context)
    elif text == "🔮 مدیریت پیامبران":
        await god.manage_prophets(update, context)
    elif text == "✏️ ویرایش فرمان":
        if user.id == ADMIN_ID:
            context.user_data['edit_mode'] = 'bio'
            await update.message.reply_text("📜 فرمان جدید خدایی را بنویسید:")
    elif text == "🔮 انتخاب پیامبر":
        await god.select_prophet(update, context)

    # Job center navigation
    elif text == "💼 مشاهده مشاغل":
        await jobs.view_jobs(update, context)
    elif text == "⚡ کار کردن":
        await jobs.work(update, context)
    elif text.startswith("کار "):
        await jobs.set_job(update, context)

    # Chat navigation
    elif text == "💬 ارسال پیام":
        await chat.send_message(update, context)
    elif text == "📖 خواندن پیام‌ها":
        await chat.read_messages(update, context)

    # Hotel navigation
    elif text == "🛏️ رزرو اتاق":
        await hotel.book_room(update, context)
    elif text == "🍽️ رستوران هتل":
        await hotel.hotel_restaurant(update, context)
    elif text == "💆 اسپا و ماساژ":
        await hotel.spa_services(update, context)

    # Marriage navigation
    elif text == "💍 پیشنهاد ازدواج":
        await marriage.propose_marriage(update, context)
    elif text == "❌ انصراف":
        await update.message.reply_text("عملیات لغو شد.")

    # Location visits
    elif text in zones.LOCATIONS:
        await zones.visit_location(update, context)

    # RPG Features Navigation
    elif text == "📜 مشاهده ماموریت‌ها":
        await rpg.view_quests(update, context)
    elif text == "⚔️ شروع ماموریت":
        await rpg.start_quest(update, context)
    elif text.startswith("شروع "):
        await rpg.start_quest(update, context)
    elif text == "🗡️ ورود به سیاه‌چال":
        await rpg.battle_system(update, context)
    elif text == "🎒 مشاهده آیتم‌ها":
        await rpg.inventory_menu(update, context)
    elif text == "📈 ارتقاء مهارت":
        await rpg.upgrade_skill(update, context)
    elif text == "📊 مشاهده مهارت‌ها":
        await rpg.skills_menu(update, context)
    elif text.startswith("💪 ارتقاء") or text.startswith("🧠 ارتقاء") or text.startswith("😎 ارتقاء") or text.startswith("🏃 ارتقاء") or text.startswith("🍀 ارتقاء"):
        # Handle skill upgrades
        await handle_skill_upgrade(update, context)

    # Achievement navigation
    elif text == "🏆 دستاوردهای من":
        await achievements.my_achievements(update, context)
    elif text == "📜 همه دستاوردها":
        await achievements.all_achievements(update, context)

    # Economy menu navigation
    elif text == "🎁 جایزه روزانه":
        await economy.give_daily(update, context)
    elif text == "📊 آمار مالی":
        await economy.financial_stats(update, context)
    elif text == "🎰 شانس‌آزمایی":
        await economy.gambling(update, context)
    elif text == "💸 انتقال پول":
        await economy.transfer_money(update, context)
    elif text == "💳 وام‌گیری":
        await economy.loan_system(update, context)
    elif text == "💎 سرمایه‌گذاری":
        await economy.investment_system(update, context)
    elif await economy.handle_gambling_selection(update, context):
        pass  # Gambling selection handled
    elif context.user_data.get('expecting_bet'):
        await economy.play_gamble(update, context)
    elif text.startswith("انتقال "):
        await economy.handle_transfer(update, context)

    # Minigames navigation
    elif text == "🎲 تاس‌بازی":
        await minigames.dice_game(update, context)
    elif text == "🃏 بلک‌جک":
        await minigames.blackjack_game(update, context)
    elif text == "🧩 حدس عدد":
        await minigames.number_guess_game(update, context)
    elif text == "🎮 بازی حافظه":
        await minigames.memory_game(update, context)
    elif text == "🎯 تیراندازی":
        await minigames.shooting_game(update, context)
    elif text.startswith("🎲 تاس"):
        await minigames.play_dice(update, context)

    # Social navigation
    elif text == "👥 لیست دوستان":
        await social.friends_list(update, context)
    elif text == "🔍 جستجوی کاربر":
        await social.search_users(update, context)
    elif text == "💌 درخواست دوستی":
        await social.send_friend_request(update, context)
    elif text == "🎁 هدیه به دوست":
        await social.gift_to_friend(update, context)
    elif text == "📱 چت خصوصی":
        await social.private_chat(update, context)
    elif text == "📊 فعالیت‌های اجتماعی":
        await social.social_activities(update, context)

    # Handle friend request input
    elif context.user_data.get('waiting_for_friend_request'):
        await social.handle_friend_request_input(update, context)

    # God mode navigation  
    elif text == "📢 پیام عمومی":
        context.user_data['waiting_for_broadcast'] = True
        await update.message.reply_text(
            "📢 پیام خدایی\n\n"
            "لطفاً پیامی که می‌خواهید به همه بازیکنان ارسال شود را بنویسید:"
        )
    elif text == "👑 مدیریت بازیکنان":
        await god.god_player_management(update, context)
    elif text == "💰 اقتصاد کل سرور":
        await god.god_economy(update, context)
    elif text == "📊 آمار خدایی":
        await god.god_stats(update, context)
    elif text == "⚡ ریست کامل":
        await god.god_reset_server(update, context)
    elif text == "⚡ قدرت‌های خدایی":
        await god.god_powers(update, context)
    elif text == "🌟 ایجاد معجزه":
        await god.god_miracle(update, context)
    elif text in ["💥 ریست آخرالزمان", "🔄 ریست اقتصادی"] or text.startswith("💰 پول "):
        await god.handle_god_commands(update, context)
    elif text in ["💥 انفجار قدرت", "🌪️ طوفان جادویی", "✨ معجزه شفا", "🔥 آتش خدایی", "❄️ یخبندان ابدی", "⚡ صاعقه مهیب", "🌈 پل رنگین‌کمان", "🕳️ سیاه‌چاله", "🔄 بازگردان زمان"]:
        await god.handle_god_power(update, context)

    # Back to main menu
    elif text == "🏠 بازگشت به منو اصلی":
        await start.show_main_square(update, context)

async def handle_photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle photo messages during registration
    if context.user_data.get('registration_step') == 'photo':
        await start.handle_registration(update, context)
    else:
        await update.message.reply_text("لطفاً ابتدا فرآیند ثبت‌نام را با ارسال /start شروع کنید.")

async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle voice messages during registration
    if context.user_data.get('registration_step') == 'voice':
        await start.handle_registration(update, context)
    else:
        await update.message.reply_text("لطفاً ابتدا فرآیند ثبت‌نام را با ارسال /start شروع کنید.")

async def handle_skill_upgrade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    p = players.get(uid, {})

    skill_points = p.get('skill_points', 0)
    if skill_points <= 0:
        await update.message.reply_text("❌ امتیاز مهارت کافی ندارید!")
        return

    text = update.message.text
    skill_map = {
        "قدرت": "strength",
        "هوش": "intelligence", 
        "جذابیت": "charisma",
        "چابکی": "agility",
        "شانس": "luck"
    }

    skill_persian = None
    for persian, english in skill_map.items():
        if persian in text:
            skill_persian = persian
            skill_english = english
            break

    if not skill_persian:
        return

    current_level = p.get("traits", {}).get(skill_english, 5)
    if current_level >= 20:
        await update.message.reply_text(f"❌ {skill_persian} شما به حداکثر سطح رسیده!")
        return

    # Upgrade skill
    p["traits"][skill_english] = current_level + 1
    p["skill_points"] = skill_points - 1
    players[uid] = p
    save_json('data/players.json', players)

    await update.message.reply_text(
        f"✅ {skill_persian} شما ارتقاء یافت!\n"
        f"📊 سطح جدید: {current_level + 1}\n"
        f"🎯 امتیاز باقی‌مانده: {skill_points - 1}"
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands  
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("profile", profile.profile))
    app.add_handler(CommandHandler("marry", marriage.marry))
    app.add_handler(CommandHandler("divorce", marriage.divorce))
    app.add_handler(CommandHandler("leaderboard", leaderboard.leaderboard))
    app.add_handler(CommandHandler("wealth", leaderboard.wealth_board))
    app.add_handler(CommandHandler("daily", economy.give_daily))
    app.add_handler(CommandHandler("god", god.god_menu))
    app.add_handler(CommandHandler("broadcast", god.god_broadcast))
    app.add_handler(CommandHandler("gift", god.god_gift))
    app.add_handler(CommandHandler("quest", rpg.quest_menu))
    app.add_handler(CommandHandler("battle", rpg.battle_system))
    app.add_handler(CommandHandler("achievements", achievements.achievements_menu))
    app.add_handler(CommandHandler("transfer", economy.handle_transfer))

    # Callback query handlers
    app.add_handler(CallbackQueryHandler(start.approve_user, pattern="^(approve|reject|details)_"))
    app.add_handler(CallbackQueryHandler(shop.buy_item, pattern="^buy_"))
    
    # Dating callback handlers
    from handlers import dating, social
    app.add_handler(CallbackQueryHandler(dating.handle_dating_callback, pattern="^(date_|online_date_|buy_dating_gift_)"))
    app.add_handler(CallbackQueryHandler(social.handle_social_callback, pattern="^(refresh_users|user_profile_|gift_to_|chat_with_|back_social|toggle_)"))

    # Message handler for keyboard navigation
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Message handler for photos during registration
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo_message))

    # Message handler for voice messages during registration
    app.add_handler(MessageHandler(filters.VOICE, handle_voice_message))

    print("🚀 Bot started successfully!")
    app.run_polling()

if __name__ == '__main__':
    main()