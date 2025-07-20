
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from config import ADMIN_ID
from utils.tools import load_json, save_json
import json

async def god_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("🚫 شما دسترسی خدایی ندارید!")
        return
    
    keyboard = [
        [KeyboardButton("📢 پیام عمومی"), KeyboardButton("👑 مدیریت بازیکنان")],
        [KeyboardButton("💰 مدیریت اقتصاد"), KeyboardButton("🎮 تنظیمات بازی")],
        [KeyboardButton("📊 آمار کلی"), KeyboardButton("🎁 هدیه عمومی")],
        [KeyboardButton("⚡ ریست سرور"), KeyboardButton("🔒 قفل/آزاد کردن")],
        [KeyboardButton("🏠 خروج از حالت خدا")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "👑 حالت خدا فعال شد\n\n"
        "🔱 به پنل مدیریت کامل بازی خوش آمدید!\n"
        "در اینجا می‌توانید تمام جنبه‌های بازی را کنترل کنید.",
        reply_markup=reply_markup
    )

async def god_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    if not context.args:
        await update.message.reply_text("📢 استفاده: متن پیام خود را بنویسید")
        return
    
    msg = "📢 پیام مهم از مدیریت:\n\n" + " ".join(context.args)
    players = load_json('data/players.json')
    
    success = 0
    failed = 0
    
    for uid in players:
        try:
            await context.bot.send_message(int(uid), msg)
            success += 1
        except Exception:
            failed += 1
    
    await update.message.reply_text(
        f"✅ پیام با موفقیت ارسال شد!\n"
        f"📤 موفق: {success}\n"
        f"❌ ناموفق: {failed}"
    )

async def god_player_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    keyboard = [
        [KeyboardButton("👥 لیست بازیکنان"), KeyboardButton("🔍 درخواست‌های تأیید")],
        [KeyboardButton("💰 تغییر پول"), KeyboardButton("⭐ تغییر سطح")],
        [KeyboardButton("🚫 مسدود کردن"), KeyboardButton("✅ رفع مسدودیت")],
        [KeyboardButton("🗑️ حذف بازیکن"), KeyboardButton("👑 بازگشت به حالت خدا")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    players = load_json('data/players.json')
    total_players = len(players)
    approved_players = sum(1 for p in players.values() if p.get('approved'))
    waiting_approval = sum(1 for p in players.values() if p.get('waiting_approval'))
    
    await update.message.reply_text(
        f"👑 مدیریت بازیکنان\n\n"
        f"👥 تعداد کل: {total_players}\n"
        f"✅ تأیید شده: {approved_players}\n"
        f"🕐 در انتظار تأیید: {waiting_approval}\n\n"
        "برای مدیریت بازیکن خاص، آیدی تلگرام او را ارسال کنید.",
        reply_markup=reply_markup
    )

async def god_economy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    keyboard = [
        [KeyboardButton("💸 تورم اقتصادی"), KeyboardButton("💰 کاهش قیمت‌ها")],
        [KeyboardButton("🎁 هدیه پولی عمومی"), KeyboardButton("📊 آمار اقتصادی")],
        [KeyboardButton("⚙️ تنظیمات فروشگاه"), KeyboardButton("👑 بازگشت به حالت خدا")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    players = load_json('data/players.json')
    total_money = sum(p.get('money', 0) for p in players.values())
    
    await update.message.reply_text(
        f"💰 مدیریت اقتصاد\n\n"
        f"💵 کل پول در گردش: {total_money:,} تومان\n"
        f"📊 میانگین ثروت: {total_money // len(players) if players else 0:,} تومان\n\n"
        "مدیریت کلی اقتصاد بازی را از اینجا انجام دهید.",
        reply_markup=reply_markup
    )

async def god_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    players = load_json('data/players.json')
    
    if not players:
        await update.message.reply_text("📊 هیچ بازیکنی ثبت نشده!")
        return
    
    # Calculate stats
    total_players = len(players)
    active_today = sum(1 for p in players.values() if p.get('last_daily'))
    married_players = sum(1 for p in players.values() if p.get('partner'))
    total_money = sum(p.get('money', 0) for p in players.values())
    avg_level = sum(p.get('level', 1) for p in players.values()) / total_players
    highest_level = max(p.get('level', 1) for p in players.values())
    
    # Top players
    richest = max(players.values(), key=lambda p: p.get('money', 0))
    highest_lvl_player = max(players.values(), key=lambda p: p.get('level', 1))
    
    text = f"📊 آمار کلی سرور\n\n"
    text += f"👥 کل بازیکنان: {total_players}\n"
    text += f"🟢 فعال امروز: {active_today}\n"
    text += f"💍 متاهل: {married_players}\n"
    text += f"💰 کل پول: {total_money:,} تومان\n"
    text += f"📊 میانگین سطح: {avg_level:.1f}\n"
    text += f"🏆 بالاترین سطح: {highest_level}\n\n"
    text += f"🥇 ثروتمندترین: {richest.get('name', 'نامشخص')} ({richest.get('money', 0):,} تومان)\n"
    text += f"⭐ بالاترین سطح: {highest_lvl_player.get('name', 'نامشخص')} (سطح {highest_lvl_player.get('level', 1)})"
    
    await update.message.reply_text(text)

async def god_gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("🎁 استفاده: /gift مبلغ پیام\nمثال: /gift 1000 هدیه عید")
        return
    
    try:
        amount = int(context.args[0])
        message = " ".join(context.args[1:])
    except ValueError:
        await update.message.reply_text("❌ مبلغ باید عدد باشد!")
        return
    
    players = load_json('data/players.json')
    
    for uid, player in players.items():
        player["money"] = player.get("money", 0) + amount
        try:
            await context.bot.send_message(
                int(uid),
                f"🎁 هدیه ویژه از مدیریت!\n\n"
                f"💰 مبلغ: {amount:,} تومان\n"
                f"📝 پیام: {message}"
            )
        except Exception:
            continue
    
    save_json('data/players.json', players)
    
    await update.message.reply_text(
        f"✅ هدیه با موفقیت به همه بازیکنان داده شد!\n"
        f"💰 مبلغ: {amount:,} تومان\n"
        f"👥 تعداد دریافت کنندگان: {len(players)}"
    )

async def god_reset_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    keyboard = [
        [KeyboardButton("⚠️ تأیید ریست کامل"), KeyboardButton("❌ انصراف")],
        [KeyboardButton("🔄 ریست اقتصاد فقط"), KeyboardButton("👑 بازگشت به حالت خدا")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "⚠️ هشدار! ریست سرور\n\n"
        "این عمل همه اطلاعات بازیکنان را پاک می‌کند!\n"
        "آیا مطمئن هستید؟",
        reply_markup=reply_markup
    )

async def handle_god_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    text = update.message.text
    
    if text == "⚠️ تأیید ریست کامل":
        # Reset everything
        save_json('data/players.json', {})
        save_json('data/chat.json', {"messages": []})
        save_json('data/partners.json', [])
        
        await update.message.reply_text("✅ سرور به طور کامل ریست شد!")
        
    elif text == "🔄 ریست اقتصاد فقط":
        # Reset only economy
        players = load_json('data/players.json')
        for uid, player in players.items():
            player["money"] = 1000
            player["inventory"] = []
        save_json('data/players.json', players)
        
        await update.message.reply_text("✅ اقتصاد بازی ریست شد!")
        
    elif text.startswith("💰 پول ") and len(text.split()) >= 3:
        # Change player money: "💰 پول USER_ID AMOUNT"
        parts = text.split()
        try:
            target_id = parts[2]
            amount = int(parts[3])
            
            players = load_json('data/players.json')
            if target_id in players:
                players[target_id]["money"] = amount
                save_json('data/players.json', players)
                await update.message.reply_text(f"✅ پول بازیکن {target_id} به {amount:,} تغییر یافت!")
            else:
                await update.message.reply_text("❌ بازیکن یافت نشد!")
        except (IndexError, ValueError):
            await update.message.reply_text("❌ فرمت اشتباه! استفاده: 💰 پول USER_ID AMOUNT")
