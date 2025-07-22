import random
from aiogram import Router, types
from aiogram.filters import Text

from db import database
from utils import keyboards
from data.locations import LOCATIONS

router = Router()

@router.message(Text(equals="🗺️ گشت و گذار"))
async def explore_start(message: types.Message):
    player = await database.get_player(message.from_user.id)
    if not player:
        await message.answer("ابتدا باید با /start ثبت‌نام کنی.")
        return

    current_location_name = player['location']
    location_data = LOCATIONS.get(current_location_name, {})
    connections = location_data.get("connections", [])

    await message.answer(
        f"تو در «{current_location_name}» هستی.\n_{location_data.get('description', '')}_\n\nبه کجا می‌خواهی بروی؟",
        reply_markup=keyboards.locations_kb(connections)
    )

@router.message(lambda message: message.text in LOCATIONS)
async def move_location(message: types.Message):
    player = await database.get_player(message.from_user.id)
    if not player:
        await message.answer("ابتدا باید با /start ثبت‌نام کنی.")
        return

    current_location_name = player['location']
    target_location_name = message.text
    
    if target_location_name in LOCATIONS[current_location_name]['connections']:
        await database.update_player(message.from_user.id, location=target_location_name)
        await message.answer(f"به «{target_location_name}» سفر کردی.")
        # Trigger a random event upon arrival
        await trigger_random_event(message)
        # Show the new location menu
        await explore_start(message)
    else:
        await message.answer("از اینجا نمی‌توانی به آنجا بروی.")

async def trigger_random_event(message: types.Message):
    # This is a placeholder for a more complex event system.
    event_roll = random.randint(1, 10)
    if event_roll <= 3:
        found_coins = random.randint(5, 20)
        await database.update_player(message.from_user.id, money=types.F('money') + found_coins)
        await message.answer(f"روی زمین چند سکه پیدا کردی! {found_coins} سکه به جیب زدی.")
    elif event_roll == 4:
        await message.answer("یک سایه از کنار تو رد شد و ناپدید گشت. اتفاق خاصی نیفتاد.")
    # More events can be added here.
```python
