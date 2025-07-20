
<old_str>
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

async def buy_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle item purchase callback"""
    query = update.callback_query
    await query.answer()
    
    item_id = query.data.replace("buy_", "")
    user = query.from_user
    uid = str(user.id)
    
    players = load_json('data/players.json')
    items = load_json("data/items.json")
    
    if uid not in players:
        await query.edit_message_text("❌ لطفاً ابتدا /start کنید!")
        return
    
    # Fi</old_str>
<new_str>
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from utils.tools import load_json, save_json

SHOP_ITEMS = {
    "energy_drink": {"name": "نوشابه انرژی ⚡", "cost": 200, "effect": "energy+20", "description": "انرژی شما را 20 واحد افزایش می‌دهد"},
    "rose": {"name": "گل رز 🌹", "cost": 50, "effect": "charisma+1", "description": "جذابیت +1"},
    "book": {"name": "کتاب 📚", "cost": 100, "effect": "intelligence+1", "description": "هوش +1"},
    "protein": {"name": "پروتئین 💪", "cost": 150, "effect": "strength+1", "description": "قدرت +1"},
    "coffee": {"name": "قهوه ☕", "cost": 80, "effect": "agility+1", "description": "چابکی +1"},
    "lucky_charm": {"name": "طلسم شانس 🍀", "cost": 300, "effect": "luck+1", "description": "شانس +1"},
    "health_potion": {"name": "معجون سلامت 🧪", "cost": 500, "effect": "full_heal", "description": "انرژی کامل + سلامت کامل"},
    "diamond": {"name": "الماس 💎", "cost": 1000, "effect": "charisma+3", "description": "جذابیت +3 - آیتم لوکس"},
    "magic_scroll": {"name": "طومار جادویی 📜", "cost": 800, "effect": "random_boost", "description": "مهارت تصادفی +2"},
    "gold_coin": {"name": "سکه طلا 🪙", "cost": 600, "effect": "money_multiplier", "description": "درآمد کار 2 برابر می‌شود"}
}

async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("ابتدا باید ثبت‌نام کنید!")
        return

    p = players[uid]
    money = p.get('money', 0)
    
    keyboard = [
        [KeyboardButton("🛒 آیتم‌های عمومی"), KeyboardButton("⚡ آیتم‌های انرژی")],
        [KeyboardButton("💪 آیتم‌های مهارتی"), KeyboardButton("💎 آیتم‌های لوکس")],
        [KeyboardButton("🎒 کیف من"), KeyboardButton("💰 فروش آیتم")],
        [KeyboardButton("🏠 بازگشت به منو اصلی")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        f"🏪 فروشگاه\n\n"
        f"💰 پول شما: {money:,} تومان\n"
        f"🎒 آیتم‌های شما: {len(p.get('inventory', []))}\n\n"
        f"دسته‌بندی مورد نظر را انتخاب کنید:",
        reply_markup=reply_markup
    )

async def general_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show general items"""
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    p = players[uid]
    money = p.get('money', 0)
    
    items = ["rose", "book", "coffee"]
    
    text = "🛒 آیتم‌های عمومی\n\n"
    keyboard = []
    
    for item_id in items:
        item = SHOP_ITEMS[item_id]
        affordable = "✅" if money >= item['cost'] else "❌"
        text += f"{affordable} {item['name']}\n"
        text += f"   💰 قیمت: {item['cost']:,} تومان\n"
        text += f"   📝 {item['description']}\n\n"
        
        button_text = f"{item['name']} - {item['cost']:,}T"
        if money < item['cost']:
            button_text = f"❌ {button_text}"
        
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"buy_{item_id}")])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت به فروشگاه", callback_data="back_to_shop")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def energy_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show energy items"""
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    p = players[uid]
    money = p.get('money', 0)
    
    items = ["energy_drink", "health_potion"]
    
    text = "⚡ آیتم‌های انرژی\n\n"
    keyboard = []
    
    for item_id in items:
        item = SHOP_ITEMS[item_id]
        affordable = "✅" if money >= item['cost'] else "❌"
        text += f"{affordable} {item['name']}\n"
        text += f"   💰 قیمت: {item['cost']:,} تومان\n"
        text += f"   📝 {item['description']}\n\n"
        
        button_text = f"{item['name']} - {item['cost']:,}T"
        if money < item['cost']:
            button_text = f"❌ {button_text}"
        
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"buy_{item_id}")])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت به فروشگاه", callback_data="back_to_shop")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def skill_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show skill items"""
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    p = players[uid]
    money = p.get('money', 0)
    
    items = ["protein", "lucky_charm", "magic_scroll"]
    
    text = "💪 آیتم‌های مهارتی\n\n"
    keyboard = []
    
    for item_id in items:
        item = SHOP_ITEMS[item_id]
        affordable = "✅" if money >= item['cost'] else "❌"
        text += f"{affordable} {item['name']}\n"
        text += f"   💰 قیمت: {item['cost']:,} تومان\n"
        text += f"   📝 {item['description']}\n\n"
        
        button_text = f"{item['name']} - {item['cost']:,}T"
        if money < item['cost']:
            button_text = f"❌ {button_text}"
        
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"buy_{item_id}")])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت به فروشگاه", callback_data="back_to_shop")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def luxury_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show luxury items"""
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    p = players[uid]
    money = p.get('money', 0)
    
    items = ["diamond", "gold_coin"]
    
    text = "💎 آیتم‌های لوکس\n\n"
    keyboard = []
    
    for item_id in items:
        item = SHOP_ITEMS[item_id]
        affordable = "✅" if money >= item['cost'] else "❌"
        text += f"{affordable} {item['name']}\n"
        text += f"   💰 قیمت: {item['cost']:,} تومان\n"
        text += f"   📝 {item['description']}\n\n"
        
        button_text = f"{item['name']} - {item['cost']:,}T"
        if money < item['cost']:
            button_text = f"❌ {button_text}"
        
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"buy_{item_id}")])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت به فروشگاه", callback_data="back_to_shop")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def my_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show player inventory"""
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    p = players[uid]
    
    inventory = p.get('inventory', [])
    
    if not inventory:
        await update.message.reply_text("🎒 کیف شما خالی است!\nبرای خرید آیتم به فروشگاه بروید.")
        return
    
    text = f"🎒 کیف {p['name']}\n\n"
    
    # Count items
    item_counts = {}
    for item in inventory:
        item_counts[item] = item_counts.get(item, 0) + 1
    
    keyboard = []
    for item, count in item_counts.items():
        if item in SHOP_ITEMS:
            item_info = SHOP_ITEMS[item]
            text += f"• {item_info['name']} x{count}\n"
            text += f"   📝 {item_info['description']}\n\n"
            
            keyboard.append([InlineKeyboardButton(f"استفاده از {item_info['name']}", callback_data=f"use_{item}")])
        else:
            text += f"• {item} x{count}\n\n"
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت به فروشگاه", callback_data="back_to_shop")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def buy_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle item purchase callback"""
    query = update.callback_query
    await query.answer()
    
    item_id = query.data.replace("buy_", "")
    user = query.from_user
    uid = str(user.id)
    
    players = load_json('data/players.json')
    
    if uid not in players:
        await query.edit_message_text("❌ لطفاً ابتدا /start کنید!")
        return
    
    if item_id not in SHOP_ITEMS:
        await query.edit_message_text("❌ آیتم یافت نشد!")
        return
    
    p = players[uid]
    item = SHOP_ITEMS[item_id]
    
    if p.get('money', 0) < item['cost']:
        await query.answer("❌ پول کافی ندارید!", show_alert=True)
        return
    
    # Purchase item
    p['money'] = p.get('money', 0) - item['cost']
    if 'inventory' not in p:
        p['inventory'] = []
    p['inventory'].append(item_id)
    
    save_json('data/players.json', players)
    
    await query.edit_message_text(
        f"✅ خرید موفق!\n\n"
        f"🛍️ آیتم: {item['name']}\n"
        f"💰 مبلغ پرداختی: {item['cost']:,} تومان\n"
        f"💵 موجودی باقی‌مانده: {p['money']:,} تومان\n\n"
        f"آیتم به کیف شما اضافه شد."
    )

async def use_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle item usage"""
    query = update.callback_query
    await query.answer()
    
    item_id = query.data.replace("use_", "")
    user = query.from_user
    uid = str(user.id)
    
    players = load_json('data/players.json')
    
    if uid not in players:
        await query.edit_message_text("❌ لطفاً ابتدا /start کنید!")
        return
    
    if item_id not in SHOP_ITEMS:
        await query.edit_message_text("❌ آیتم یافت نشد!")
        return
    
    p = players[uid]
    inventory = p.get('inventory', [])
    
    if item_id not in inventory:
        await query.answer("❌ این آیتم در کیف شما نیست!", show_alert=True)
        return
    
    item = SHOP_ITEMS[item_id]
    effect = item['effect']
    result_text = f"✨ استفاده از {item['name']}\n\n"
    
    # Apply item effects
    import random
    
    if effect.startswith("energy"):
        bonus = int(effect.split("+")[1])
        p['energy'] = min(100, p.get('energy', 100) + bonus)
        result_text += f"⚡ انرژی +{bonus} (فعلی: {p['energy']}/100)"
        
    elif effect.startswith("charisma"):
        bonus = int(effect.split("+")[1])
        p['traits']['charisma'] = min(20, p['traits']['charisma'] + bonus)
        result_text += f"😎 جذابیت +{bonus} (فعلی: {p['traits']['charisma']}/20)"
        
    elif effect.startswith("intelligence"):
        bonus = int(effect.split("+")[1])
        p['traits']['intelligence'] = min(20, p['traits']['intelligence'] + bonus)
        result_text += f"🧠 هوش +{bonus} (فعلی: {p['traits']['intelligence']}/20)"
        
    elif effect.startswith("strength"):
        bonus = int(effect.split("+")[1])
        p['traits']['strength'] = min(20, p['traits']['strength'] + bonus)
        result_text += f"💪 قدرت +{bonus} (فعلی: {p['traits']['strength']}/20)"
        
    elif effect.startswith("agility"):
        bonus = int(effect.split("+")[1])
        p['traits']['agility'] = min(20, p['traits']['agility'] + bonus)
        result_text += f"🏃 چابکی +{bonus} (فعلی: {p['traits']['agility']}/20)"
        
    elif effect.startswith("luck"):
        bonus = int(effect.split("+")[1])
        p['traits']['luck'] = min(20, p['traits']['luck'] + bonus)
        result_text += f"🍀 شانس +{bonus} (فعلی: {p['traits']['luck']}/20)"
        
    elif effect == "full_heal":
        p['energy'] = 100
        result_text += f"🧪 انرژی کامل بازیابی شد! (100/100)"
        
    elif effect == "random_boost":
        traits = list(p['traits'].keys())
        random_trait = random.choice(traits)
        p['traits'][random_trait] = min(20, p['traits'][random_trait] + 2)
        trait_names = {"charisma": "جذابیت", "intelligence": "هوش", "strength": "قدرت", "agility": "چابکی", "luck": "شانس"}
        result_text += f"🎲 {trait_names[random_trait]} +2 (تصادفی!)"
        
    elif effect == "money_multiplier":
        if 'buffs' not in p:
            p['buffs'] = {}
        p['buffs']['money_multiplier'] = True
        result_text += f"🪙 درآمد کار شما 2 برابر شد! (موقتی)"
    
    # Remove item from inventory
    inventory.remove(item_id)
    p['inventory'] = inventory
    
    save_json('data/players.json', players)
    
    await query.edit_message_text(result_text)

async def handle_shop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle shop callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("buy_"):
        await buy_item(update, context)
    elif data.startswith("use_"):
        await use_item(update, context)
    elif data == "back_to_shop":
        await shop(query, context)</new_str>
