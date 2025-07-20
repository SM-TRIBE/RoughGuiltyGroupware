
<line_number>1</line_number>

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.tools import load_json, save_json
import random

async def minigames_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    keyboard = [
        [KeyboardButton("🎲 تاس‌بازی"), KeyboardButton("🃏 بلک‌جک")],
        [KeyboardButton("🎯 تیراندازی"), KeyboardButton("🧩 حدس عدد")],
        [KeyboardButton("🎮 بازی حافظه"), KeyboardButton("⚡ واکنش‌سنج")],
        [KeyboardButton("🏠 بازگشت به منو اصلی")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🎮 سالن بازی‌ها\n\n"
        "بازی مورد نظر خود را انتخاب کنید:\n"
        "هر بازی امتیاز XP و جوایز نقدی دارد!",
        reply_markup=reply_markup
    )

async def dice_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    keyboard = [
        [KeyboardButton("🎲 تاس 50 تومان"), KeyboardButton("🎲 تاس 100 تومان")],
        [KeyboardButton("🎲 تاس 200 تومان"), KeyboardButton("🚪 بازگشت")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🎲 بازی تاس\n\n"
        "قوانین:\n"
        "• شما و ربات هرکدام یک تاس می‌اندازید\n"
        "• عدد بیشتر برنده است\n"
        "• مساوی = برگشت پول\n\n"
        "مبلغ شرط را انتخاب کنید:",
        reply_markup=reply_markup
    )

async def play_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text.startswith("🎲 تاس"):
        return
    
    try:
        bet = int(text.split()[2])
    except (IndexError, ValueError):
        return
    
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    p = players[uid]
    
    if p.get('money', 0) < bet:
        await update.message.reply_text("پول کافی ندارید!")
        return
    
    player_dice = random.randint(1, 6)
    bot_dice = random.randint(1, 6)
    
    if player_dice > bot_dice:
        winnings = bet
        p['money'] = p.get('money', 0) + winnings
        p['xp'] = p.get('xp', 0) + 10
        result = f"🎉 برنده شدید!\n🎲 شما: {player_dice} | ربات: {bot_dice}\n💰 +{winnings:,} تومان"
    elif player_dice < bot_dice:
        p['money'] = p.get('money', 0) - bet
        result = f"😢 باختید!\n🎲 شما: {player_dice} | ربات: {bot_dice}\n💸 -{bet:,} تومان"
    else:
        p['xp'] = p.get('xp', 0) + 5
        result = f"😐 مساوی!\n🎲 شما: {player_dice} | ربات: {bot_dice}\nپول برگشت داده شد"
    
    players[uid] = p
    save_json("data/players.json", players)
    
    await update.message.reply_text(result)

async def blackjack_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    # Initialize blackjack game
    context.user_data['blackjack'] = {
        'player_cards': [random.randint(1, 11), random.randint(1, 11)],
        'dealer_cards': [random.randint(1, 11)],
        'bet': 100,
        'game_active': True
    }
    
    game = context.user_data['blackjack']
    player_total = sum(game['player_cards'])
    
    keyboard = [
        [KeyboardButton("🃏 کارت بکش"), KeyboardButton("🛑 استپ")],
        [KeyboardButton("🚪 بازگشت")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        f"🃏 بلک‌جک\n\n"
        f"کارت‌های شما: {game['player_cards']} (مجموع: {player_total})\n"
        f"کارت دیلر: [{game['dealer_cards'][0]}, ?]\n\n"
        f"شرط: {game['bet']:,} تومان\n"
        f"هدف: نزدیک‌ترین عدد به 21",
        reply_markup=reply_markup
    )

async def number_guess_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    # Initialize guess game
    context.user_data['guess_game'] = {
        'number': random.randint(1, 100),
        'attempts': 0,
        'max_attempts': 7,
        'prize': 300
    }
    
    await update.message.reply_text(
        "🧩 بازی حدس عدد\n\n"
        "من عددی بین 1 تا 100 انتخاب کرده‌ام.\n"
        "شما 7 تلاش دارید تا آن را حدس بزنید.\n\n"
        "💰 جایزه: 300 تومان\n\n"
        "عدد خود را بفرستید:"
    )

async def memory_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    # Generate sequence
    sequence = [random.choice(['🔴', '🟢', '🔵', '🟡']) for _ in range(5)]
    context.user_data['memory_game'] = {
        'sequence': sequence,
        'step': 0,
        'user_sequence': []
    }
    
    await update.message.reply_text(
        "🎮 بازی حافظه\n\n"
        "دنباله زیر را به خاطر بسپارید:\n"
        f"{' '.join(sequence)}\n\n"
        "5 ثانیه بعد باید همین ترتیب را تکرار کنید.\n"
        "آماده باشید..."
    )
    
    # Wait and then start the game
    import asyncio
    await asyncio.sleep(5)
    
    keyboard = [
        [KeyboardButton("🔴"), KeyboardButton("🟢")],
        [KeyboardButton("🔵"), KeyboardButton("🟡")],
        [KeyboardButton("✅ تمام"), KeyboardButton("🚪 بازگشت")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "حالا دنباله را تکرار کنید:\n"
        "رنگ‌ها را به ترتیب انتخاب کنید:",
        reply_markup=reply_markup
    )

async def shooting_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    # Generate targets
    targets = []
    for i in range(3):
        row = []
        for j in range(3):
            if random.randint(1, 100) <= 30:  # 30% chance for target
                row.append("🎯")
            else:
                row.append("⬜")
        targets.append(row)
    
    context.user_data['shooting_game'] = {
        'targets': targets,
        'shots': 5,
        'score': 0
    }
    
    # Create inline keyboard
    keyboard = []
    for i in range(3):
        row = []
        for j in range(3):
            row.append(InlineKeyboardButton("🔍", callback_data=f"shoot_{i}_{j}"))
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎯 بازی تیراندازی\n\n"
        "شما 5 تیر دارید.\n"
        "روی مربع‌ها کلیک کنید تا تیراندازی کنید:\n\n"
        "🎯 = هدف (امتیاز)\n"
        "💥 = خطا",
        reply_markup=reply_markup
    )

