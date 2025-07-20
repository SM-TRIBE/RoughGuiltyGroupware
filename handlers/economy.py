from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db.database import db
from datetime import datetime, timedelta
import random
import re
from config import DAILY_REWARD, ADMIN_ID, GOD_UNLIMITED_MONEY

async def economy_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)
    player = db.get_player(user.id)

    if not player or not player.get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return

    # Special god mode display
    if user.id == ADMIN_ID:
        money_display = f"♾️ نامحدود (قدرت خدایی)"
    else:
        money_display = f"{player.get('money', 0):,} تومان"

    keyboard = [
        [KeyboardButton("🎁 جایزه روزانه"), KeyboardButton("📊 آمار مالی")],
        [KeyboardButton("🎰 شانس‌آزمایی"), KeyboardButton("💸 انتقال پول")],
        [KeyboardButton("💳 وام‌گیری"), KeyboardButton("💎 سرمایه‌گذاری")],
        [KeyboardButton("🏪 بازار سهام"), KeyboardButton("🎲 بازی‌های شانسی")],
        [KeyboardButton("💰 ماشین پول‌ساز"), KeyboardButton("🏦 بانک مرکزی")],
        [KeyboardButton("🏠 بازگشت به منو اصلی")]
    ]

    # Add god-only options
    if user.id == ADMIN_ID:
        keyboard.insert(-1, [KeyboardButton("⚡ قدرت‌های مالی خدایی"), KeyboardButton("💸 باران طلا")])

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    text = f"💰 مرکز اقتصادی\n\n"
    text += f"👤 {player.get('name', 'بازیکن')}\n"
    text += f"💵 دارایی: {money_display}\n"
    text += f"📅 آخرین جایزه: {player.get('last_daily') or 'هرگز'}\n\n"

    if user.id == ADMIN_ID:
        text += "🔱 شما دسترسی خدایی به تمام امکانات اقتصادی دارید!"
    else:
        text += "انتخاب کنید که چه کاری انجام دهید."

    await update.message.reply_text(text, reply_markup=reply_markup)

async def give_daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = db.get_player(user.id)

    if not player or not player.get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return

    now = datetime.now()
    last_daily = player.get('last_daily')

    # Parse last_daily if it's a string
    if last_daily and isinstance(last_daily, str):
        try:
            last_daily = datetime.fromisoformat(last_daily.replace('Z', '+00:00'))
        except:
            last_daily = None

    # Check if 24 hours have passed
    if last_daily and (now - last_daily).total_seconds() < 86400:
        remaining = 86400 - (now - last_daily).total_seconds()
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        await update.message.reply_text(
            f"⏰ هنوز زمان جایزه روزانه نرسیده!\n"
            f"⏳ زمان باقی‌مانده: {hours} ساعت و {minutes} دقیقه"
        )
        return

    # God gets special daily reward
    if user.id == ADMIN_ID:
        reward = GOD_UNLIMITED_MONEY
        special_msg = "\n\n⚡ به عنوان خداوند، قدرت نامحدود دریافت کردید!"
    else:
        # Calculate reward based on level
        base_reward = DAILY_REWARD
        level_bonus = player.get('level', 1) * 100
        luck_bonus = player.get('traits', {}).get('luck', 5) * 50

        reward = base_reward + level_bonus + luck_bonus

        # Random bonus chance
        if random.random() < 0.1:  # 10% chance
            bonus_multiplier = random.uniform(1.5, 3.0)
            reward = int(reward * bonus_multiplier)
            special_msg = f"\n\n🎉 شانس آورده‌اید! جایزه {bonus_multiplier:.1f} برابر شد!"
        else:
            special_msg = ""

    # Update player data
    if user.id != ADMIN_ID:  # Don't change god's money from unlimited
        player['money'] = player.get('money', 0) + reward
    player['last_daily'] = now.isoformat()

    db.save_player(user.id, player)

    await update.message.reply_text(
        f"🎁 جایزه روزانه دریافت شد!\n\n"
        f"💰 مبلغ: {reward:,} تومان\n"
        f"💵 دارایی جدید: {player.get('money', GOD_UNLIMITED_MONEY):,} تومان{special_msg}"
    )

async def financial_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = db.get_player(user.id)

    if not player or not player.get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return

    # Get server-wide stats
    stats = db.get_god_stats()
    all_players = db.get_all_players()

    if all_players:
        player_money = player.get('money', 0)
        total_money = stats.get('total_money', 0)
        avg_money = total_money // max(len(all_players), 1)

        # Find ranking
        money_list = sorted([p.get('money', 0) for p in all_players.values()], reverse=True)
        try:
            rank = money_list.index(player_money) + 1
        except ValueError:
            rank = len(money_list)

        # Calculate wealth percentage
        wealth_percentage = (player_money / max(total_money, 1)) * 100

        text = f"📊 آمار مالی شما\n\n"
        text += f"💰 دارایی فعلی: {player_money:,} تومان\n"
        text += f"🏆 رتبه ثروت: {rank} از {len(all_players)}\n"
        text += f"📈 درصد کل ثروت: {wealth_percentage:.2f}%\n"
        text += f"📊 میانگین سرور: {avg_money:,} تومان\n\n"

        if player_money > avg_money:
            text += "🟢 شما بالاتر از میانگین هستید!"
        elif player_money == avg_money:
            text += "🟡 شما در حد میانگین هستید!"
        else:
            text += "🔴 شما زیر میانگین هستید!"

        # God special stats
        if user.id == ADMIN_ID:
            text += f"\n\n⚡ آمار خدایی:\n"
            text += f"🌍 کنترل {stats.get('total_players', 0)} نفر\n"
            text += f"💎 دارایی نامحدود\n"
            text += f"👑 رتبه: خداوند مطلق"
    else:
        text = "📊 هنوز آماری موجود نیست!"

    await update.message.reply_text(text)

async def gambling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = db.get_player(user.id)

    if not player or not player.get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return

    keyboard = [
        [KeyboardButton("🎰 شانس کم - برد بالا"), KeyboardButton("🎯 شانس متوسط")],
        [KeyboardButton("💰 شانس بالا - برد کم"), KeyboardButton("⚡ شانس خدایی")],
        [KeyboardButton("🎲 تاس طلایی"), KeyboardButton("🃏 کارت شانس")],
        [KeyboardButton("💰 بازگشت به اقتصاد")]
    ]

    # Remove god option for non-admins
    if user.id != ADMIN_ID:
        keyboard[1] = [KeyboardButton("💰 شانس بالا - برد کم")]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    money = player.get('money', 0)
    if user.id == ADMIN_ID:
        money_display = "♾️ نامحدود"
    else:
        money_display = f"{money:,} تومان"

    await update.message.reply_text(
        f"🎰 شانس‌آزمایی\n\n"
        f"💰 دارایی شما: {money_display}\n\n"
        f"🎯 انواع بازی:\n"
        f"🔴 شانس کم (10%) - برد ۱۰ برابر\n"
        f"🟡 شانس متوسط (30%) - برد ۳ برابر\n"
        f"🟢 شانس بالا (60%) - برد ۱.۵ برابر\n"
        + ("⚡ شانس خدایی (100%) - هر چه بخواهید!\n" if user.id == ADMIN_ID else "") +
        f"\nحداقل شرط: ۱۰۰ تومان",
        reply_markup=reply_markup
    )

async def play_gamble(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = db.get_player(user.id)
    text = update.message.text

    if not player or not player.get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return

    # Extract bet amount from context if available
    if context.user_data.get('gambling_type') and context.user_data.get('expecting_bet'):
        try:
            bet_amount = int(text.replace(',', ''))
            gambling_type = context.user_data['gambling_type']
            context.user_data.clear()
        except ValueError:
            await update.message.reply_text("❌ لطفاً مبلغ شرط را به صورت عدد وارد کنید.")
            return
    else:
        await update.message.reply_text("لطفاً ابتدا نوع بازی را انتخاب کنید.")
        return

    money = player.get('money', 0)

    # God mode gambling
    if user.id == ADMIN_ID and gambling_type == "god":
        await update.message.reply_text(
            f"⚡ شانس خدایی! ⚡\n\n"
            f"🎊 شما {bet_amount:,} تومان برنده شدید!\n"
            f"🔱 قدرت خدایی شما لامحدود است!"
        )
        return

    # Check if player has enough money
    if money < bet_amount:
        await update.message.reply_text(
            f"❌ پول کافی ندارید!\n"
            f"💰 دارایی شما: {money:,} تومان\n"
            f"💸 مبلغ مورد نیاز: {bet_amount:,} تومان"
        )
        return

    # Minimum bet check
    if bet_amount < 100:
        await update.message.reply_text("❌ حداقل مبلغ شرط ۱۰۰ تومان است!")
        return

    # Determine game type and odds
    if gambling_type == "low":
        win_chance = 0.1
        multiplier = 10
        game_name = "شانس کم"
    elif gambling_type == "medium":
        win_chance = 0.3
        multiplier = 3
        game_name = "شانس متوسط"
    elif gambling_type == "high":
        win_chance = 0.6
        multiplier = 1.5
        game_name = "شانس بالا"
    else:
        await update.message.reply_text("❌ نوع بازی نامعتبر!")
        return

    # Play the game
    luck_stat = player.get('traits', {}).get('luck', 5)
    luck_bonus = (luck_stat - 5) * 0.02  # 2% per luck point above 5
    final_chance = min(win_chance + luck_bonus, 0.95)  # Max 95% chance

    won = random.random() < final_chance

    if won:
        winnings = int(bet_amount * multiplier)
        player['money'] = money - bet_amount + winnings
        result_text = f"🎉 برنده شدید! 🎉\n\n"
        result_text += f"🎰 بازی: {game_name}\n"
        result_text += f"💰 شرط: {bet_amount:,} تومان\n"
        result_text += f"🏆 برد: {winnings:,} تومان\n"
        result_text += f"📈 سود: {winnings - bet_amount:,} تومان\n"
        result_text += f"💵 دارایی جدید: {player['money']:,} تومان"
    else:
        player['money'] = money - bet_amount
        result_text = f"😞 متأسفانه باختید! 😞\n\n"
        result_text += f"🎰 بازی: {game_name}\n"
        result_text += f"💸 ضرر: {bet_amount:,} تومان\n"
        result_text += f"💵 دارایی باقی‌مانده: {player['money']:,} تومان"

    db.save_player(user.id, player)
    await update.message.reply_text(result_text)

# Handle gambling type selection
async def handle_gambling_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "شانس کم" in text:
        context.user_data['gambling_type'] = "low"
        game_info = "🔴 شانس کم (10%) - برد ۱۰ برابر"
    elif "شانس متوسط" in text:
        context.user_data['gambling_type'] = "medium"
        game_info = "🟡 شانس متوسط (30%) - برد ۳ برابر"
    elif "شانس بالا" in text:
        context.user_data['gambling_type'] = "high"
        game_info = "🟢 شانس بالا (60%) - برد ۱.۵ برابر"
    elif "شانس خدایی" in text and update.effective_user.id == ADMIN_ID:
        context.user_data['gambling_type'] = "god"
        game_info = "⚡ شانس خدایی (100%) - هر چه بخواهید"
    else:
        return False

    context.user_data['expecting_bet'] = True

    await update.message.reply_text(
        f"🎰 {game_info}\n\n"
        f"💰 چه مبلغی می‌خواهید شرط بندی کنید؟\n"
        f"(حداقل ۱۰۰ تومان)"
    )
    return True

async def transfer_money(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = db.get_player(user.id)

    if not player or not player.get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return

    await update.message.reply_text(
        "💸 انتقال پول\n\n"
        "برای انتقال پول به فرمت زیر پیام ارسال کنید:\n"
        "انتقال [مبلغ] [آیدی_دریافت_کننده]\n\n"
        "مثال: انتقال 1000 123456789"
    )

async def handle_transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = db.get_player(user.id)
    text = update.message.text

    if not player or not player.get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return

    # Parse transfer command
    match = re.match(r'انتقال (\d+) (\d+)', text)
    if not match:
        await update.message.reply_text("❌ فرمت نادرست! استفاده کنید: انتقال [مبلغ] [آیدی]")
        return

    amount = int(match.group(1))
    target_id = int(match.group(2))

    if target_id == user.id:
        await update.message.reply_text("❌ نمی‌توانید به خودتان پول انتقال دهید!")
        return

    if amount < 100:
        await update.message.reply_text("❌ حداقل مبلغ انتقال ۱۰۰ تومان است!")
        return

    # God mode - unlimited transfer
    if user.id == ADMIN_ID:
        target_player = db.get_player(target_id)
        if not target_player:
            await update.message.reply_text("❌ بازیکن مقصد یافت نشد!")
            return

        target_player['money'] = target_player.get('money', 0) + amount
        db.save_player(target_id, target_player)

        try:
            await context.bot.send_message(
                target_id,
                f"💰 هدیه از خداوند!\n\n"
                f"💵 مبلغ: {amount:,} تومان\n"
                f"🔱 این هدیه‌ای از جانب خداوند بازی است!"
            )
        except Exception:
            pass

        await update.message.reply_text(
            f"⚡ انتقال خدایی انجام شد!\n"
            f"💰 مبلغ: {amount:,} تومان\n"
            f"👤 به: {target_player.get('name', 'ناشناس')}"
        )
        return

    # Regular player transfer
    current_money = player.get('money', 0)

    if current_money < amount:
        await update.message.reply_text(
            f"❌ موجودی کافی ندارید!\n"
            f"💰 موجودی شما: {current_money:,} تومان\n"
            f"💸 مبلغ درخواستی: {amount:,} تومان"
        )
        return

    target_player = db.get_player(target_id)
    if not target_player or not target_player.get('approved'):
        await update.message.reply_text("❌ بازیکن مقصد یافت نشد یا تأیید نشده!")
        return

    # Transfer fee (2%)
    fee = max(amount * 0.02, 10)  # Minimum 10 toman fee
    total_deduct = amount + fee

    if current_money < total_deduct:
        await update.message.reply_text(
            f"❌ موجودی برای پرداخت کارمزد کافی نیست!\n"
            f"💰 مبلغ انتقال: {amount:,} تومان\n"
            f"💸 کارمزد: {fee:,} تومان\n"
            f"💵 مجموع: {total_deduct:,} تومان\n"
            f"🏦 موجودی شما: {current_money:,} تومان"
        )
        return

    # Perform transfer
    player['money'] = current_money - total_deduct
    target_player['money'] = target_player.get('money', 0) + amount

    db.save_player(user.id, player)
    db.save_player(target_id, target_player)

    # Notify both parties
    try:
        await context.bot.send_message(
            target_id,
            f"💰 پول دریافت کردید!\n\n"
            f"👤 فرستنده: {player.get('name', 'ناشناس')}\n"
            f"💵 مبلغ: {amount:,} تومان\n"
            f"💼 موجودی جدید: {target_player['money']:,} تومان"
        )
    except Exception:
        pass

    await update.message.reply_text(
        f"✅ انتقال موفق!\n\n"
        f"👤 به: {target_player.get('name', 'ناشناس')}\n"
        f"💰 مبلغ انتقال: {amount:,} تومان\n"
        f"💸 کارمزد: {fee:,} تومان\n"
        f"💵 موجودی باقی‌مانده: {player['money']:,} تومان"
    )

async def loan_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚧 سیستم وام در حال توسعه است!")

async def investment_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚧 سیستم سرمایه‌گذاری در حال توسعه است!")

# Export all functions
__all__ = [
    'economy_menu', 'give_daily', 'financial_stats', 'gambling', 'play_gamble',
    'handle_gambling_selection', 'transfer_money', 'handle_transfer', 
    'loan_system', 'investment_system'
]