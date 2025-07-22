from aiogram import Router, types
from aiogram.filters import Text

from db import database
from data.items import ITEMS

router = Router()

@router.message(Text(equals="🎒 کوله‌پشتی"))
async def view_inventory(message: types.Message):
    player = await database.get_player(message.from_user.id)
    if not player:
        await message.answer("ابتدا باید با /start ثبت‌نام کنی.")
        return

    inventory_ids = player.get('inventory', [])
    if not inventory_ids:
        await message.answer("کوله‌پشتی تو خالی است.")
        return

    inventory_counts = {}
    for item_id in inventory_ids:
        inventory_counts[item_id] = inventory_counts.get(item_id, 0) + 1

    response = "در کوله‌پشتی خود این‌ها را داری:\n\n"
    for item_id, count in inventory_counts.items():
        item_name = next((name for name, details in ITEMS.items() if details['id'] == item_id), "کالای ناشناس")
        response += f"- {item_name} (x{count})\n"

    await message.answer(response)
```python
# handlers/admin_handler.py
from aiogram import Router, types
from aiogram.filters import Command

import config

router = Router()
# Restrict admin commands to the designated admin user
@router.message(lambda message: message.from_user.id == int(config.ADMIN_ID))
@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    await message.answer("به پنل خدایگان خوش آمدی. دستورات مدیریتی در اینجا قرار خواهند گرفت.")
