
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from utils.tools import load_json, save_json
from datetime import datetime, timedelta
import random
import re

async def give_daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    p = players[uid]
    last_daily = p.get('last_daily')
    
    if last_daily:
        try:
            last_daily_time = datetime.fromisoformat(last_daily)
            if datetime.now() - last_daily_time < timedelta(days=1):
                remaining = timedelta(days=1) - (datetime.now() - last_daily_time)
                hours = remaining.seconds // 3600
                minutes = (remaining.seconds % 3600) // 60
                await update.message.reply_text(
                    f"⏰ شما باید {hours} ساعت و {minutes} دقیقه صبر کنید."
                )
                return
        except ValueError:
            # Handle old date format
            today = datetime.now().strftime("%Y-%m-%d")
            if last_daily == today:
                await update.message.reply_text("شما امروز جایزه روزانه خود را دریافت کرده‌اید!")
                return
    
    # Daily reward calculation
    base_reward = 500
    level_bonus = p.get('level', 1) * 50
    random_bonus = random.randint(100, 300)
    total_reward = base_reward + level_bonus + random_bonus
    
    p['money'] = p.get('money', 0) + total_reward
    p['energy'] = min(100, p.get('energy', 100) + 20)
    p['happiness'] = min(100, p.get('happiness', 50) + 10)
    p['last_daily'] = datetime.now().isoformat()
    
    players[uid] = p
    save_json("data/players.json", players)
    
    await update.message.reply_text(
        f"🎁 جایزه روزانه دریافت شد!\n"
        f"💰 +{total_reward:,} تومان\n"
        f"⚡ +20 انرژی\n"
        f"😊 +10 شادی\n\n"
        f"موجودی فعلی: {p['money']:,} تومان"
    )

async def economy_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    keyboard = [
        [KeyboardButton("🎁 جایزه روزانه"), KeyboardButton("📊 آمار مالی")],
        [KeyboardButton("💸 انتقال پول"), KeyboardButton("🎰 شانس‌آزمایی")],
        [KeyboardButton("💳 وام‌گیری"), KeyboardButton("💎 سرمایه‌گذاری")],
        [KeyboardButton("🏠 بازگشت به منو اصلی")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "💰 مرکز اقتصادی\n"
        "اینجا می‌توانید امور مالی خود را مدیریت کنید.",
        reply_markup=reply_markup
    )

async def financial_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    p = players[uid]
    
    # Calculate net worth
    item_values = {
        "گل رز قرمز": 150, "عطر زعفرانی": 300, "الماس شب": 1000,
        "کتاب شاهنامه": 200, "فرش اصفهان": 2000, "زعفران مشهد": 500
    }
    
    inventory_value = sum(item_values.get(item, 0) for item in p.get('inventory', []))
    net_worth = p.get('money', 0) + inventory_value
    
    # Work income calculation
    work_income = 0
    work_stats = p.get('work_stats', {})
    job_salaries = {
        "راننده تاکسی": 200, "برنامه‌نویس": 500, "مدل": 400,
        "ورزشکار": 350, "معلم": 300, "بازیگر": 600
    }
    
    for job, count in work_stats.items():
        work_income += job_salaries.get(job, 0) * count
    
    text = f"📊 آمار مالی {p['name']}:\n\n"
    text += f"💰 پول نقد: {p.get('money', 0):,} تومان\n"
    text += f"🎒 ارزش کالاها: {inventory_value:,} تومان\n"
    text += f"💎 ثروت کل: {net_worth:,} تومان\n\n"
    text += f"💼 درآمد کاری: {work_income:,} تومان\n"
    text += f"📈 سطح: {p.get('level', 1)}\n"
    text += f"🏆 رتبه شما در بین ثروتمندان: "
    
    # Calculate rank
    all_players = [(uid, data) for uid, data in players.items() if data.get("approved")]
    all_players.sort(key=lambda x: x[1].get('money', 0), reverse=True)
    
    for i, (player_uid, _) in enumerate(all_players, 1):
        if player_uid == uid:
            text += f"{i}\n"
            break
    
    await update.message.reply_text(text)

async def gambling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    p = players[uid]
    
    if p.get('money', 0) < 100:
        await update.message.reply_text("حداقل 100 تومان نیاز دارید!")
        return
    
    keyboard = [
        [KeyboardButton("🎰 100 تومان"), KeyboardButton("🎰 500 تومان")],
        [KeyboardButton("🎰 1000 تومان"), KeyboardButton("🎰 5000 تومان")],
        [KeyboardButton("🚪 بازگشت")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🎰 شانس‌آزمایی!\n"
        "مبلغ مورد نظر را انتخاب کنید:",
        reply_markup=reply_markup
    )

async def play_gamble(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text.startswith("🎰"):
        return
    
    try:
        amount_str = text.split()[1]
        amount = int(amount_str)
    except (IndexError, ValueError):
        await update.message.reply_text("مبلغ نامعتبر!")
        return
    
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    p = players[uid]
    
    if p.get('money', 0) < amount:
        await update.message.reply_text(f"پول کافی ندارید! نیاز: {amount:,} تومان")
        return
    
    # Gambling logic
    luck = random.randint(1, 100)
    player_luck = p.get('traits', {}).get('luck', 5)
    
    # Adjust odds based on player luck
    luck_bonus = player_luck - 5
    
    if luck + luck_bonus <= 15:  # 15% chance - jackpot
        winnings = amount * 5
        p['money'] = p.get('money', 0) + winnings
        result = f"🎰🎉 جک‌پات! برنده بزرگ شدید! +{winnings:,} تومان"
    elif luck + luck_bonus <= 25:  # 10% chance - big win
        winnings = amount * 3
        p['money'] = p.get('money', 0) + winnings
        result = f"🎉 برنده بزرگ شدید! +{winnings:,} تومان"
    elif luck + luck_bonus <= 45:  # 20% chance - small win
        winnings = amount
        p['money'] = p.get('money', 0) + winnings
        result = f"😊 برنده شدید! +{winnings:,} تومان"
    elif luck + luck_bonus <= 60:  # 15% chance - break even
        result = "😐 مساوی! پولتان برگشت"
    else:  # 40% chance - lose
        p['money'] = p.get('money', 0) - amount
        result = f"😢 باختید! -{amount:,} تومان"
    
    players[uid] = p
    save_json("data/players.json", players)
    
    await update.message.reply_text(
        f"{result}\n"
        f"موجودی فعلی: {p['money']:,} تومان"
    )

async def transfer_money(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    await update.message.reply_text(
        "💸 انتقال پول\n\n"
        "برای انتقال پول، دستور زیر را ارسال کنید:\n"
        "/transfer @username مبلغ\n\n"
        "مثال: /transfer @john 1000"
    )

async def handle_transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("استفاده: /transfer @username مبلغ")
        return
    
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    try:
        target_username = context.args[0].replace('@', '')
        amount = int(context.args[1])
    except ValueError:
        await update.message.reply_text("مبلغ نامعتبر!")
        return
    
    if amount <= 0:
        await update.message.reply_text("مبلغ باید مثبت باشد!")
        return
    
    sender = players[uid]
    
    if sender.get('money', 0) < amount:
        await update.message.reply_text("موجودی کافی ندارید!")
        return
    
    # Find target player
    target_uid = None
    for player_id, player_data in players.items():
        if player_data.get('username', '').lower() == target_username.lower():
            target_uid = player_id
            break
    
    if not target_uid:
        await update.message.reply_text("کاربر یافت نشد!")
        return
    
    target = players[target_uid]
    
    # Transfer money
    sender['money'] = sender.get('money', 0) - amount
    target['money'] = target.get('money', 0) + amount
    
    players[uid] = sender
    players[target_uid] = target
    save_json("data/players.json", players)
    
    await update.message.reply_text(
        f"✅ {amount:,} تومان با موفقیت به @{target_username} انتقال داده شد!\n"
        f"موجودی شما: {sender['money']:,} تومان"
    )
    
    # Notify receiver
    try:
        await context.bot.send_message(
            chat_id=int(target_uid),
            text=f"💰 شما {amount:,} تومان از @{user.username or sender['name']} دریافت کردید!"
        )
    except Exception:
        pass

async def loan_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    p = players[uid]
    current_loan = p.get('loan', 0)
    level = p.get('level', 1)
    max_loan = level * 2000
    
    if current_loan > 0:
        interest = int(current_loan * 0.1)
        total_debt = current_loan + interest
        
        keyboard = [
            [KeyboardButton(f"💰 پرداخت کامل ({total_debt:,} تومان)")],
            [KeyboardButton("🔍 مشاهده جزئیات"), KeyboardButton("🚪 بازگشت")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            f"💳 وضعیت وام شما:\n\n"
            f"💸 مبلغ وام: {current_loan:,} تومان\n"
            f"📈 سود (10%): {interest:,} تومان\n"
            f"💰 کل بدهی: {total_debt:,} تومان\n\n"
            f"موجودی شما: {p.get('money', 0):,} تومان",
            reply_markup=reply_markup
        )
    else:
        keyboard = [
            [KeyboardButton("💳 وام 1000 تومان"), KeyboardButton("💳 وام 2000 تومان")],
            [KeyboardButton("💳 وام 5000 تومان"), KeyboardButton(f"💳 حداکثر ({max_loan:,} تومان)")],
            [KeyboardButton("🚪 بازگشت")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            f"💳 سیستم وام‌گیری\n\n"
            f"حداکثر وام مجاز شما: {max_loan:,} تومان\n"
            f"نرخ سود: 10% (پرداخت یکجا)\n\n"
            f"مبلغ مورد نظر را انتخاب کنید:",
            reply_markup=reply_markup
        )

async def investment_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    p = players[uid]
    investments = p.get('investments', {})
    
    keyboard = [
        [KeyboardButton("📈 طلا (کم ریسک)"), KeyboardButton("💎 ارز دیجیتال (پر ریسک)")],
        [KeyboardButton("🏢 املاک (متوسط ریسک)"), KeyboardButton("📊 مشاهده سبد")],
        [KeyboardButton("🚪 بازگشت")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    total_investment = sum(investments.values())
    
    await update.message.reply_text(
        f"💎 مرکز سرمایه‌گذاری\n\n"
        f"💰 موجودی: {p.get('money', 0):,} تومان\n"
        f"📊 کل سرمایه‌گذاری: {total_investment:,} تومان\n\n"
        f"انواع سرمایه‌گذاری:",
        reply_markup=reply_markup
    )

async def economy_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    keyboard = [
        [KeyboardButton("🎁 جایزه روزانه"), KeyboardButton("📊 آمار مالی")],
        [KeyboardButton("💸 انتقال پول"), KeyboardButton("🎰 شانس‌آزمایی")],
        [KeyboardButton("🏠 بازگشت به منو اصلی")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "💰 مرکز اقتصادی\n"
        "اینجا می‌توانید امور مالی خود را مدیریت کنید.",
        reply_markup=reply_markup
    )

async def financial_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    p = players[uid]
    
    # Calculate net worth
    item_values = {
        "گل رز قرمز": 150, "عطر زعفرانی": 300, "الماس شب": 1000,
        "کتاب شاهنامه": 200, "فرش اصفهان": 2000, "زعفران مشهد": 500
    }
    
    inventory_value = sum(item_values.get(item, 0) for item in p.get('inventory', []))
    net_worth = p.get('money', 0) + inventory_value
    
    # Work income calculation
    work_income = 0
    work_stats = p.get('work_stats', {})
    job_salaries = {
        "راننده تاکسی": 200, "برنامه‌نویس": 500, "مدل": 400,
        "ورزشکار": 350, "معلم": 300, "بازیگر": 600
    }
    
    for job, count in work_stats.items():
        work_income += job_salaries.get(job, 0) * count
    
    text = f"📊 آمار مالی {p['name']}:\n\n"
    text += f"💰 پول نقد: {p.get('money', 0):,} تومان\n"
    text += f"🎒 ارزش کالاها: {inventory_value:,} تومان\n"
    text += f"💎 ثروت کل: {net_worth:,} تومان\n\n"
    text += f"💼 درآمد کاری: {work_income:,} تومان\n"
    text += f"📈 سطح: {p.get('level', 1)}\n"
    text += f"🏆 رتبه شما در بین ثروتمندان: "
    
    # Calculate rank
    all_players = [(uid, data) for uid, data in players.items() if data.get("approved")]
    all_players.sort(key=lambda x: x[1].get('money', 0), reverse=True)
    
    for i, (player_uid, _) in enumerate(all_players, 1):
        if player_uid == uid:
            text += f"{i}\n"
            break
    
    await update.message.reply_text(text)

async def gambling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    p = players[uid]
    
    if p.get('money', 0) < 100:
        await update.message.reply_text("حداقل 100 تومان نیاز دارید!")
        return
    
    keyboard = [
        [KeyboardButton("🎰 100 تومان"), KeyboardButton("🎰 500 تومان")],
        [KeyboardButton("🎰 1000 تومان"), KeyboardButton("🚪 بازگشت")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🎰 شانس‌آزمایی!\n"
        "مبلغ مورد نظر را انتخاب کنید:",
        reply_markup=reply_markup
    )

async def play_gamble(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text.startswith("🎰"):
        return
    
    try:
        amount_str = text.split()[1]
        amount = int(amount_str)
    except (IndexError, ValueError):
        await update.message.reply_text("مبلغ نامعتبر!")
        return
    
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    p = players[uid]
    
    if p.get('money', 0) < amount:
        await update.message.reply_text(f"پول کافی ندارید! نیاز: {amount:,} تومان")
        return
    
    # Gambling logic
    luck = random.randint(1, 100)
    
    if luck <= 10:  # 10% chance - big win
        winnings = amount * 3
        p['money'] = p.get('money', 0) + winnings
        result = f"🎉 برنده بزرگ شدید! +{winnings:,} تومان"
    elif luck <= 30:  # 20% chance - small win
        winnings = amount
        p['money'] = p.get('money', 0) + winnings
        result = f"😊 برنده شدید! +{winnings:,} تومان"
    elif luck <= 50:  # 20% chance - break even
        result = "😐 مساوی! پولتان برگشت"
    else:  # 50% chance - lose
        p['money'] = p.get('money', 0) - amount
        result = f"😢 باختید! -{amount:,} تومان"
    
    players[uid] = p
    save_json("data/players.json", players)
    
    await update.message.reply_text(
        f"{result}\n"
        f"موجودی فعلی: {p['money']:,} تومان"
    )

async def transfer_money(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    await update.message.reply_text(
        "💸 انتقال پول\n\n"
        "برای انتقال پول، دستور زیر را ارسال کنید:\n"
        "/transfer @username مبلغ\n\n"
        "مثال: /transfer @john 1000"
    )
