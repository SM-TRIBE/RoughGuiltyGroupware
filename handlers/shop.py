from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def shop(update, context):
    items = load_json("data/items.json")
    buttons = [[InlineKeyboardButton(f"{item['name']} - {item['cost']}💳", callback_data=f"buy_{item['id']}")]
               for item in items]
    await update.message.reply_text("🛍️ فروشگاه:", reply_markup=InlineKeyboardMarkup(buttons))

async def buy_item(update, context):
    query = update.callback_query
    uid = str(query.from_user.id)
    item_id = query.data.replace("buy_", "")
    players = load_json("data/players.json")
    items = load_json("data/items.json")
    item = next(i for i in items if i['id'] == item_id)
    if players[uid]['money'] >= item['cost']:
        players[uid]['money'] -= item['cost']
        players[uid]['inventory'].append(item['name'])
        save_json("data/players.json", players)
        await query.edit_message_text(f"✅ {item['name']} خریداری شد!")
    else:
        await query.edit_message_text("❌ پول کافی نداری!")