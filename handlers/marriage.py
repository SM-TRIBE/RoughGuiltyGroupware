# === FILE: main.py ===
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import BOT_TOKEN
from utils.tools import load_json, save_json
from handlers import economy, leveling, zones, adult_scene, shop, marriage, leaderboard

logging.basicConfig(level=logging.INFO)

async def start(update, context):
    user = update.effective_user
    uid = str(user.id)
    players = load_json("data/players.json")
    if uid not in players:
        players[uid] = {
            "name": user.first_name,
            "partner": None,
            "location": "مرکز شهر",
            "traits": {"charisma": 5, "intelligence": 5, "strength": 5},
            "money": 1000,
            "xp": 0,
            "level": 1,
            "inventory": [],
            "age_confirmed": False
        }
        save_json("data/players.json", players)
    await update.message.reply_text(f"🎮 به دنیای آینده خوش آمدی، {user.first_name}! از /city و /shop دیدن کن.")

async def confirm_age(update, context):
    uid = str(update.effective_user.id)
    players = load_json("data/players.json")
    players[uid]['age_confirmed'] = True
    save_json("data/players.json", players)
    await update.message.reply_text("✅ تأیید سنی انجام شد. اکنون به بخش 🔞 دسترسی دارید.")

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("daily", economy.give_daily))
app.add_handler(CommandHandler("work", economy.do_job))
app.add_handler(CommandHandler("city", zones.city))
app.add_handler(CallbackQueryHandler(zones.enter_zone, pattern="^zone_"))
app.add_handler(CommandHandler("shop", shop.shop))
app.add_handler(CallbackQueryHandler(shop.buy_item, pattern="^buy_"))
app.add_handler(CommandHandler("scene", adult_scene.start_scene))
app.add_handler(CommandHandler("confirm18", confirm_age))
app.add_handler(CommandHandler("marry", marriage.marry))
app.add_handler(CommandHandler("top", leaderboard.leaderboard))

if __name__ == '__main__':
    print("🚀 Bot is running...")
    app.run_polling()
