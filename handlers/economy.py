
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from utils.tools import load_json, save_json
from datetime import datetime, timedelta
import random

async def give_daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("ابتدا باید ثبت‌نام کنید!")
        return
    
    p = players[uid]
    today = datetime.now().strftime("%Y-%m-%d")
    last_daily = p.get("last_daily")
    
    if last_daily == today:
        await update.message.reply_text("شما امروز جایزه روزانه خود را دریافت کرده‌اید!")
        return
    
    # Give daily reward
    daily_amount = 500 + (p.get("level", 1) * 50)  # Base + level bonus
    p["money"] = p.get("money", 0) + daily_amount
    p["last_daily"] = today
    
    # Save data
    players[uid] = p
    save_json("data/players.json", players)
    
    await update.message.reply_text(
        f"🎁 جایزه روزانه!\n"
        f"💰 {daily_amount:,} تومان دریافت کردید!\n"
        f"💳 موجودی جدید: {p['money']:,} تومان"
    )te.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    p = players[uid]
    last_daily = p.get('last_daily')
    
    if last_daily:
        last_daily_time = datetime.fromisoformat(last_daily)
        if datetime.now() - last_daily_time < timedelta(days=1):
            remaining = timedelta(days=1) - (datetime.now() - last_daily_time)
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            await update.message.reply_text(
                f"⏰ شما باید {hours} ساعت و {minutes} دقیقه صبر کنید."
            )
            return
    
    # Daily reward calculation
    base_reward = 500
    level_bonus = p.get('level', 1) * 50
    random_bonus = random.randint(100, 300)
    total_reward = base_reward + level_bonus + random_bonus
    
    p['money'] += total_reward
    p['energy'] = min(100, p.get('energy', 100) + 20)
    p['happiness'] = min(100, p.get('happiness', 50) + 10)
    p['last_daily'] = datetime.now().isoformat()
    
    save_json("data/players.json", players)
    
    await update.message.reply_text(
        f"🎁 جایزه روزانه دریافت شد!\n"
        f"💰 +{total_reward} تومان\n"
        f"⚡ +20 انرژی\n"
        f"😊 +10 شادی\n\n"
        f"موجودی فعلی: {p['money']} تومان"
    )

async def economy_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    all_players = [(uid, data) for uid, data in players.items()]
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
    
    amount_str = text.split()[1]
    amount = int(amount_str)
    
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    p = players[uid]
    
    if p.get('money', 0) < amount:
        await update.message.reply_text(f"پول کافی ندارید! نیاز: {amount} تومان")
        return
    
    # Gambling logic
    luck = random.randint(1, 100)
    
    if luck <= 10:  # 10% chance - big win
        winnings = amount * 3
        p['money'] += winnings
        result = f"🎉 برنده شدید! +{winnings} تومان"
    elif luck <= 30:  # 20% chance - small win
        winnings = amount
        p['money'] += winnings
        result = f"😊 برنده شدید! +{winnings} تومان"
    elif luck <= 50:  # 20% chance - break even
        result = "😐 مساوی! پولتان برگشت"
    else:  # 50% chance - lose
        p['money'] -= amount
        result = f"😢 باختید! -{amount} تومان"
    
    save_json("data/players.json", players)
    
    await update.message.reply_text(
        f"{result}\n"
        f"موجودی فعلی: {p['money']} تومان"
    )
