from aiogram import Router, types
from aiogram.filters import Text
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db import database
from utils import keyboards

router = Router()

@router.message(Text(equals="🍻 زندگی اجتماعی"))
async def social_menu(message: types.Message):
    player = await database.get_player(message.from_user.id)
    if not player:
        await message.answer("ابتدا باید با /start ثبت‌نام کنی.")
        return

    builder = InlineKeyboardBuilder()
    builder.button(text="👀 نگاهی به اطراف", callback_data="social:look_around")
    if player['partner_id']:
        builder.button(text="💔 فسخ پیمان", callback_data="social:divorce")
    else:
        builder.button(text="💍 ارسال پیشنهاد پیمان", callback_data="social:propose")
    
    if player['proposal_from_id']:
         builder.button(text="💌 مشاهده پیشنهاد", callback_data="social:view_proposal")

    builder.adjust(1)
    await message.answer("در میکده شهر چه می‌کنی؟", reply_markup=builder.as_markup())

@router.callback_query(lambda c: c.data == "social:look_around")
async def look_around(callback_query: types.CallbackQuery):
    player = await database.get_player(callback_query.from_user.id)
    other_players = await database.get_players_in_location(player['location'], player['user_id'])
    
    if not other_players:
        await callback_query.message.answer("به نظر می‌رسد در حال حاضر تنها هستی.")
        return

    response = "افراد زیر را در اطراف خود می‌بینی:\n"
    for p in other_players:
        response += f"- {p['name']} (`/view {p['user_id']}`)\n"
    
    await callback_query.message.answer(response)
    await callback_query.answer()

@router.callback_query(lambda c: c.data == "social:propose")
async def propose_start(callback_query: types.CallbackQuery):
    # In a real scenario, this would likely involve a more complex state machine
    # to select a player to propose to.
    await callback_query.message.answer("برای ارسال پیشنهاد، پروفایل فرد مورد نظر را باز کرده و از آنجا اقدام کن. (ویژگی در دست ساخت)")
    await callback_query.answer()

# ... more social features like accepting/declining proposals would be built out here ...
```python
