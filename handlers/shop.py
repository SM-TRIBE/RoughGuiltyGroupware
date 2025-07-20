
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.tools import load_json, save_json

async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("ابتدا باید ثبت‌نام کنید!")
        return
    
    items = load_json("data/items.json")
    if not items:
        # Initialize default items
        items = [
            {"id": "1", "name": "گل رز 🌹", "cost": 50, "effect": "charisma+1"},
            {"id": "2", "name": "کتاب 📚", "cost": 100, "effect": "intelligence+1"},
            {"id": "3", "name": "دمبل 🏋️", "cost": 150, "effect": "strength+1"},
            {"id": "4", "name": "کفش ورزشی 👟", "cost": 200, "effect": "agility+1"},
            {"id": "5", "name": "سکه طلا 🪙", "cost": 500, "effect": "luck+1"}
        ]
        save_json("data/items.json", items)
    
    p = players[uid]
    buttons = []
    for item in items:
        if p['money'] >= item['cost']:
            status = "✅"
        else:
            status = "❌"
        buttons.append([InlineKeyboardButton(
            f"{status} {item['name']} - {item['cost']:,}💰", 
            callback_data=f"buy_{item['id']}"
        )])
    
    text = f"🛍️ فروشگاه\n\n💰 پول شما: {p['money']:,} تومان\n\nآیتم‌های موجود:"
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

async def buy_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    uid = str(query.from_user.id)
    item_id = query.data.replace("buy_", "")
    
    players = load_json("data/players.json")
    items = load_json("data/items.json")
    
    if uid not in players:
        await query.edit_message_text("❌ شما ثبت‌نام نکرده‌اید!")
        return
    
    item = next((i for i in items if i['id'] == item_id), None)
    if not item:
        await query.edit_message_text("❌ آیتم یافت نشد!")
        return
    
    p = players[uid]
    if p['money'] >= item['cost']:
        p['money'] -= item['cost']
        p['inventory'].append(item['name'])
        
        # Apply item effect
        if item['effect']:
            effect_parts = item['effect'].split('+')
            if len(effect_parts) == 2:
                trait = effect_parts[0]
                bonus = int(effect_parts[1])
                if trait in p['traits']:
                    p['traits'][trait] = min(20, p['traits'][trait] + bonus)
        
        players[uid] = p
        save_json("data/players.json", players)
        
        await query.edit_message_text(
            f"✅ {item['name']} خریداری شد!\n"
            f"💰 باقی‌مانده: {p['money']:,} تومان"
        )
    else:
        needed = item['cost'] - p['money']
        await query.edit_message_text(
            f"❌ پول کافی ندارید!\n"
            f"💰 نیاز: {needed:,} تومان بیشتر"
        )
