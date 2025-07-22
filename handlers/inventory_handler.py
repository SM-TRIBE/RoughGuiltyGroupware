from aiogram import Router, types
from aiogram.filters import Text, CallbackQuery
import json

from db import database
from data.items import ITEMS
from utils import keyboards

router = Router()

@router.message(Text(equals="🎒 کوله‌پشتی"))
async def view_inventory(message: types.Message):
    player = await database.get_player(message.from_user.id)
    if not player: return await message.answer("ابتدا باید با /start ثبت‌نام کنی.")

    inventory_ids = json.loads(player.get('inventory', '[]'))
    if not inventory_ids: return await message.answer("کوله‌پشتی تو خالی است.")

    inventory_items = []
    item_counts = {}
    for item_id in inventory_ids:
        item_counts[item_id] = item_counts.get(item_id, 0) + 1
        
    response = "در کوله‌پشتی خود این‌ها را داری:\n\n"
    for item_id, count in item_counts.items():
        item_name = next((name for name, details in ITEMS.items() if details['id'] == item_id), "کالای ناشناس")
        item_details = ITEMS.get(item_name, {})
        response += f"- {item_name} (x{count})\n_{item_details.get('description', '')}_\n"
        
        # Add to list for keyboard if it's consumable
        if item_details.get('type') == 'consumable':
            inventory_items.append((item_id, item_name))

    await message.answer(response, reply_markup=keyboards.inventory_kb(inventory_items))

@router.callback_query(lambda c: c.data.startswith("inventory:use:"))
async def use_item(callback_query: types.CallbackQuery):
    item_id = callback_query.data.split(":")[2]
    user_id = callback_query.from_user.id
    
    player = await database.get_player(user_id)
    inventory = json.loads(player.get('inventory', '[]'))

    if item_id not in inventory:
        return await callback_query.answer("این آیتم در کوله‌پشتی تو نیست!", show_alert=True)

    item_name = next((name for name, details in ITEMS.items() if details['id'] == item_id), None)
    item_details = ITEMS.get(item_name)

    if not item_details or item_details.get('type') != 'consumable':
        return await callback_query.answer("نمی‌توانی از این آیتم استفاده کنی.", show_alert=True)

    # Apply effect
    effect = item_details.get('effect', {})
    if 'hp' in effect:
        new_health = min(player['health'] + effect['hp'], player['max_health'])
        if new_health == player['health']:
            return await callback_query.answer("سلامتی‌ات کامل است و نیازی به این نداری.", show_alert=True)
            
        await database.update_player(user_id, health=new_health)
        await callback_query.answer(f"از «{item_name}» استفاده کردی و {effect['hp']} سلامتی به دست آوردی.", show_alert=True)
    
    # Remove one instance of the item from inventory
    inventory.remove(item_id)
    await database.update_player(user_id, inventory=json.dumps(inventory))

    await callback_query.message.delete() # Refresh inventory view
    dummy_message = types.Message(message_id=0, date=datetime.datetime.now(), chat=callback_query.message.chat, from_user=callback_query.from_user)
    await view_inventory(dummy_message)

