from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.tools import load_json, save_json

async def city(update, context):
    zones = load_json("data/city_zones.json")
    buttons = [[InlineKeyboardButton(z['name'], callback_data=f"zone_{z['id']}")]
               for z in zones]
    await update.message.reply_text("🏙️ به کدام منطقه می‌روی؟", reply_markup=InlineKeyboardMarkup(buttons))

async def enter_zone(update, context):
    query = update.callback_query
    await query.answer()
    zone_id = query.data.replace("zone_", "")
    uid = str(query.from_user.id)
    players = load_json("data/players.json")
    zones = load_json("data/city_zones.json")
    zone = next(z for z in zones if z['id'] == zone_id)
    players[uid]['location'] = zone['name']
    players[uid]['traits']['charisma'] += zone['charisma_bonus']
    save_json("data/players.json", players)
    await query.edit_message_text(f"🚶 وارد {zone['name']} شدی!\n✨ {zone['desc']}")
