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
    name = message.text.strip()
    if not (2 <= len(name) <= 20):
        await message.answer("نام تو باید بین ۲ تا ۲۰ حرف باشد. نامی درخور برای خودت انتخاب کن.")
        return
    await state.update_data(name=name)
    await state.set_state(Registration.confirm_name)
    await message.answer(f"پس نامت «{name}» است. آیا این نام را برای خود می‌پسندی؟", reply_markup=keyboards.yes_no("register"))

@router.callback_query(Registration.confirm_name, lambda c: c.data == 'register:yes')
async def confirm_name_yes(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    name = user_data['name']
    await database.create_player(callback_query.from_user.id, name)
    await state.clear()
    await callback_query.message.edit_text(
        f"بسیار خب، {name}. سرگذشت تو در شهرستان وحشی آغاز شد. از کوچه‌پس‌کوچه‌های خاکی آن گرفته تا میکده‌های پر از دود، ماجراجویی در انتظار توست.",
    )
    await callback_query.message.answer("چه می‌خواهی بکنی؟", reply_markup=keyboards.main_menu())

@router.callback_query(Registration.confirm_name, lambda c: c.data == 'register:no')
async def confirm_name_no(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(Registration.enter_name)
    await callback_query.message.edit_text("ایرادی ندارد. بگو تو را چه بنامیم؟")

# --- Back to Main Menu Handler ---
@router.message(lambda message: message.text == "➡️ بازگشت به منوی اصلی")
async def back_to_main_menu(message: types.Message):
    await message.answer("به منوی اصلی بازگشتی.", reply_markup=keyboards.main_menu())
```python
# handlers/profile_handler.py
from aiogram import Router, types
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from db import database
from utils import keyboards
import config

router = Router()

class ProfileEdit(StatesGroup):
    editing_bio = State()
    assigning_points = State()

def calculate_xp_for_next_level(level: int) -> int:
    return int(config.XP_PER_LEVEL_BASE * (config.XP_PER_LEVEL_FACTOR ** (level - 1)))

@router.message(Text(equals="👤 پروفایل من"))
async def my_profile(message: types.Message):
    player = await database.get_player(message.from_user.id)
    if not player:
        await message.answer("ابتدا باید با /start ثبت‌نام کنی.")
        return

    partner_name = "ندارد"
    if player['partner_id']:
        partner_player = await database.get_player(player['partner_id'])
        partner_name = partner_player['name'] if partner_player else "ناشناس"

    xp_needed = calculate_xp_for_next_level(player['level'])
    profile_text = f"""
📜 **کارنامه {player['name']}** 📜

**سطح:** {player['level']} | **تجربه:** {player['xp']}/{xp_needed}
**امتیاز قابل تخصیص:** {player['skill_points']} ✨
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

@router.callback_query(lambda c: c.data == "profile:edit_bio")
async def edit_bio_start(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(ProfileEdit.editing_bio)
    await callback_query.message.answer("شرح حال جدید خود را بنویس (حداکثر ۲۰۰ حرف).")
    await callback_query.answer()

@router.message(ProfileEdit.editing_bio)
async def process_bio_edit(message: types.Message, state: FSMContext):
    bio = message.text.strip()
    if len(bio) > 200:
        await message.answer("شرح حالت بیش از حد طولانی است. لطفاً کوتاه‌تر بنویس.")
        return
    await database.update_player(message.from_user.id, bio=bio)
    await state.clear()
    await message.answer("شرح حال تو با موفقیت ثبت شد.")
    await my_profile(message)

