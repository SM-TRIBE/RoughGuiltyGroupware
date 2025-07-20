
import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN
from utils.tools import load_json, save_json, init_player

# Import all handlers
from handlers import start, profile, admin, zones, shop, marriage, leaderboard, economy
from handlers import chat, hotel, jobs

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    p = init_player(user)
    
    main_keyboard = [
        [KeyboardButton("👤 پروفایل"), KeyboardButton("🗺️ سفر")],
        [KeyboardButton("🛍️ فروشگاه"), KeyboardButton("💼 کار")],
        [KeyboardButton("💬 کافه گپ"), KeyboardButton("🏨 هتل")],
        [KeyboardButton("💍 ازدواج"), KeyboardButton("🏆 رتبه‌بندی")],
        [KeyboardButton("💰 اقتصاد"), KeyboardButton("⚙️ تنظیمات")]
    ]
    reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        f"🌟 سلام {p['name']} عزیز!\n"
        f"به بازی زندگی مجازی ایرانی خوش آمدید!\n\n"
        f"🎮 این یک بازی نقش‌آفرینی کامل است که در آن می‌توانید:\n"
        f"• به مکان‌های مختلف سفر کنید\n"
        f"• با افراد مختلف آشنا شوید\n"
        f"• ازدواج کنید و خانواده تشکیل دهید\n"
        f"• کار کنید و پول درآورید\n"
        f"• در کافه گپ با دیگران صحبت کنید\n"
        f"• در هتل استراحت کنید\n"
        f"• مهارت‌هایتان را ارتقاء دهید\n\n"
        f"برای شروع، لطفاً سن خود را وارد کنید:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user
    uid = str(user.id)
    
    # Check if user exists
    players = load_json('data/players.json')
    if uid not in players:
        init_player(user)
        players = load_json('data/players.json')
    
    # Handle age confirmation first
    if not players[uid].get("age_confirmed") and text.isdigit():
        await start.reply_age(update, context)
        return
    
    # Handle chat messages
    if context.user_data.get('waiting_for_message'):
        await chat.receive_chat_message(update, context)
        return
    
    # Main menu navigation
    if text == "👤 پروفایل":
        await profile.profile(update, context)
    elif text == "🗺️ سفر":
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
        await economy.give_daily(update, context)
    
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
    
    # Back to main menu
    elif text == "🏠 بازگشت به منو اصلی":
        main_keyboard = [
            [KeyboardButton("👤 پروفایل"), KeyboardButton("🗺️ سفر")],
            [KeyboardButton("🛍️ فروشگاه"), KeyboardButton("💼 کار")],
            [KeyboardButton("💬 کافه گپ"), KeyboardButton("🏨 هتل")],
            [KeyboardButton("💍 ازدواج"), KeyboardButton("🏆 رتبه‌بندی")],
            [KeyboardButton("💰 اقتصاد"), KeyboardButton("⚙️ تنظیمات")]
        ]
        reply_markup = ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
        await update.message.reply_text("🏠 منوی اصلی", reply_markup=reply_markup)

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
    app.add_handler(CommandHandler("god", admin.god_speak))
    
    # Message handler for keyboard navigation
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 Bot started successfully!")
    app.run_polling()

if __name__ == '__main__':
    main()
