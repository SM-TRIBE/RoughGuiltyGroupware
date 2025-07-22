from aiogram import Router, types
from aiogram.filters import Text
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db import database
from utils import keyboards
from data.items import ITEMS

router = Router()

@router.message(Text(equals="💰 بازارچه"))
async def shop_menu(message: types.Message):
    await message.answer("به بازارچه شهرستان وحشی خوش آمدی. قصد خرید داری یا فروش؟", reply_markup=keyboards.shop_kb())

@router.callback_query(lambda c: c.data == "shop:buy")
async def buy_menu(callback_query: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    for name, details in ITEMS.items():
        builder.button(text=f"{name} - {details['price']} سکه", callback_data=f"shop:buy_item:{details['id']}")
    builder.adjust(1)
    await callback_query.message.edit_text("چه چیزی چشمت را گرفته؟", reply_markup=builder.as_markup())
    await callback_query.answer()

@router.callback_query(lambda c: c.data.startswith("shop:buy_item:"))
async def buy_item(callback_query: types.CallbackQuery):
    item_id = callback_query.data.split(":")[2]
    item_to_buy = next((details for details in ITEMS.values() if details['id'] == item_id), None)
    item_name = next((name for name, details in ITEMS.items() if details['id'] == item_id), "Unknown")

    if not item_to_buy:
        await callback_query.answer("این کالا دیگر موجود نیست.", show_alert=True)
        return

    player = await database.get_player(callback_query.from_user.id)
    if player['money'] < item_to_buy['price']:
        await callback_query.answer("سکه کافی برای خرید این کالا را نداری.", show_alert=True)
        return

    new_inventory = player['inventory'] + [item_id]
    await database.update_player(
        callback_query.from_user.id,
        money=player['money'] - item_to_buy['price'],
        inventory=json.dumps(new_inventory)
    )
    await callback_query.answer(f"«{item_name}» را خریدی!", show_alert=True)
    await callback_query.message.delete() # Clean up the shop menu

