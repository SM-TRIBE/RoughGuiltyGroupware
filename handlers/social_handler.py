# This handler is now significantly more complex to handle the full marriage flow.
from aiogram import Router, types
from aiogram.filters import Text, Command, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import json

from db import database
from utils import keyboards

router = Router()

class SocialFSM(StatesGroup):
    proposing = State()

@router.message(Text(equals="🍻 زندگی اجتماعی"))
async def social_menu(message: types.Message):
    player = await database.get_player(message.from_user.id)
    if not player: return await message.answer("ابتدا باید با /start ثبت‌نام کنی.")

    builder = InlineKeyboardBuilder()
    builder.button(text="👀 نگاهی به اطراف", callback_data="social:look_around")
    
    if player['partner_id']:
        partner = await database.get_player(player['partner_id'])
        builder.button(text=f"💔 فسخ پیمان با {partner['name']}", callback_data="social:divorce")
    elif player['proposal_from_id']:
        proposer = await database.get_player(player['proposal_from_id'])
        builder.button(text=f"💌 مشاهده پیشنهاد از {proposer['name']}", callback_data="social:view_proposal")
    else:
        builder.button(text="💍 ارسال پیشنهاد پیمان", callback_data="social:propose")
    
    builder.adjust(1)
    await message.answer("در میکده شهر چه می‌کنی؟", reply_markup=builder.as_markup())

@router.callback_query(lambda c: c.data == "social:propose")
async def propose_start(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(SocialFSM.proposing)
    await callback_query.message.answer("کد کاربری فردی که می‌خواهی به او پیشنهاد دهی را وارد کن. (می‌توانی کد را از پروفایل او با دستور /view پیدا کنی)")
    await callback_query.answer()

@router.message(SocialFSM.proposing)
async def process_proposal(message: types.Message, state: FSMContext):
    try:
        target_id = int(message.text)
    except ValueError:
        return await message.answer("کد کاربری باید یک عدد باشد.")

    proposer_id = message.from_user.id
    if target_id == proposer_id:
        return await message.answer("نمی‌توانی به خودت پیشنهاد دهی!")

    target_player = await database.get_player(target_id)
    if not target_player:
        return await message.answer("فردی با این کد کاربری یافت نشد.")
    if target_player['partner_id']:
        return await message.answer(f"{target_player['name']} در حال حاضر با فرد دیگری پیمان بسته است.")
    if target_player['proposal_from_id']:
        return await message.answer(f"{target_player['name']} در حال حاضر یک پیشنهاد دیگر دارد و باید به آن پاسخ دهد.")

    await database.update_player(target_id, proposal_from_id=proposer_id)
    await state.clear()
    await message.answer(f"پیشنهاد تو برای {target_player['name']} ارسال شد. او اکنون باید در منوی اجتماعی آن را بپذیرد یا رد کند.")
    # You could also send a notification to the target player here via bot.send_message

@router.callback_query(lambda c: c.data == "social:view_proposal")
async def view_proposal(callback_query: types.CallbackQuery):
    player = await database.get_player(callback_query.from_user.id)
    proposer = await database.get_player(player['proposal_from_id'])
    await callback_query.message.edit_text(
        f"💌 {proposer['name']} به تو پیشنهاد پیمان داده است. آیا می‌پذیری؟",
        reply_markup=keyboards.yes_no("proposal_response")
    )

@router.callback_query(lambda c: c.data.startswith("proposal_response:"))
async def process_proposal_response(callback_query: types.CallbackQuery):
    action = callback_query.data.split(":")[1]
    user_id = callback_query.from_user.id
    player = await database.get_player(user_id)
    proposer_id = player['proposal_from_id']

    if action == "yes":
        await database.update_player(user_id, partner_id=proposer_id, proposal_from_id=None)
        await database.update_player(proposer_id, partner_id=user_id, proposal_from_id=None)
        await callback_query.message.edit_text(f"تبریک! تو و { (await database.get_player(proposer_id))['name'] } اکنون شریک زندگی هم هستید.")
    else: # no
        await database.update_player(user_id, proposal_from_id=None)
        await callback_query.message.edit_text("پیشنهاد را رد کردی.")
        # Notify the proposer
        await bot.send_message(proposer_id, f"😔 {player['name']} پیشنهاد پیمان تو را رد کرد.")

# Divorce logic and other handlers remain similar
```python
