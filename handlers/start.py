from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from db import database
from utils import keyboards

router = Router()

class Registration(StatesGroup):
    enter_name = State()
    confirm_name = State()

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    """Handles the /start command."""
    player = await database.get_player(message.from_user.id)
    if player:
        await message.answer(
            f"ای {player['name']}، دوباره به شهرستان وحشی خوش آمدی!",
            reply_markup=keyboards.main_menu()
        )
    else:
        await state.set_state(Registration.enter_name)
        await message.answer(
            "ای غریبه، به دروازه‌های شهرستان وحشی رسیدی. سرزمینی بی‌قانون و پر از فرصت. نامت چیست تا در تاریخ این دیار ثبت شود؟"
        )

@router.message(Registration.enter_name)
async def process_name(message: types.Message, state: FSMContext):
    """Processes the name entered by the new player."""
    name = message.text.strip()
    if len(name) < 2 or len(name) > 20:
        await message.answer("نام تو باید بین ۲ تا ۲۰ حرف باشد. نامی درخور برای خودت انتخاب کن.")
        return

    await state.update_data(name=name)
    await state.set_state(Registration.confirm_name)
    await message.answer(
        f"پس نامت «{name}» است. آیا این نام را برای خود می‌پسندی؟",
        reply_markup=keyboards.yes_no()
    )

@router.callback_query(Registration.confirm_name, lambda c: c.data == 'yes')
async def confirm_name_yes(callback_query: types.CallbackQuery, state: FSMContext):
    """Confirms the name and creates the player."""
    user_data = await state.get_data()
    name = user_data['name']
    user_id = callback_query.from_user.id

    await database.create_player(user_id, name)
    await state.clear()

    await callback_query.message.edit_text(
        f"بسیار خب، {name}. سرگذشت تو در شهرستان وحشی آغاز شد. از کوچه‌پس‌کوچه‌های خاکی آن گرفته تا taverns پر از دود، ماجراجویی در انتظار توست.",
        reply_markup=None
    )
    await callback_query.message.answer("چه می‌خواهی بکنی؟", reply_markup=keyboards.main_menu())

@router.callback_query(Registration.confirm_name, lambda c: c.data == 'no')
async def confirm_name_no(callback_query: types.CallbackQuery, state: FSMContext):
    """Allows the player to re-enter their name."""
    await state.set_state(Registration.enter_name)
    await callback_query.message.edit_text("ایرادی ندارد. بگو تو را چه بنامیم؟", reply_markup=None)
```python
# handlers/profile_handler.py
from aiogram import Router, types
from aiogram.filters import Text

from db import database
from utils import keyboards

router = Router()

@router.message(Text(equals="👤 پروفایل من"))
async def my_profile(message: types.Message):
    """Displays the player's profile."""
    player = await database.get_player(message.from_user.id)
    if not player:
        await message.answer("ابتدا باید با /start ثبت‌نام کنی.")
        return

    partner_name = "ندارد"
    if player['partner_id']:
        partner_player = await database.get_player(player['partner_id'])
        partner_name = partner_player['name'] if partner_player else "ناشناس"

    profile_text = f"""
📜 **کارنامه {player['name']}** 📜

**سطح:** {player['level']} | **تجربه:** {player['xp']}/{player['level'] * 100}
**سکه‌های نقره:** {player['money']} 🪙

**ویژگی‌ها:**
- **قدرت:** {player['strength']} 💪
- **چابکی:** {player['agility']} 🏃
- **هوش:** {player['intelligence']} 🧠

**موقعیت:** {player['location']}
**شغل:** {player.get('job') or 'بیکار'}
**شریک:** {partner_name}

**شرح حال:**
_{player.get('bio') or 'هنوز شرح حالی ننوشته‌ای.'}_
"""
    await message.answer(profile_text, reply_markup=keyboards.profile_menu())
```python
