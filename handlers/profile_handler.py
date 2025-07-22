from aiogram import Router, types
from aiogram.filters import Text, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from db import database
from utils import keyboards
import config

router = Router()

class ProfileFSM(StatesGroup):
    editing_bio = State()
    assigning_points = State()

def calculate_xp_for_next_level(level: int) -> int:
    return int(config.XP_PER_LEVEL_BASE * (config.XP_PER_LEVEL_FACTOR ** (level - 1)))

async def check_for_level_up(message: types.Message, player: asyncpg.Record):
    """Checks if a player has enough XP to level up and handles it."""
    xp_needed = calculate_xp_for_next_level(player['level'])
    if player['xp'] >= xp_needed:
        new_level = player['level'] + 1
        new_xp = player['xp'] - xp_needed
        new_skill_points = player['skill_points'] + 1
        new_max_health = player['max_health'] + 10
        
        await database.update_player(
            player['user_id'],
            level=new_level,
            xp=new_xp,
            skill_points=new_skill_points,
            max_health=new_max_health,
            health=new_max_health  # Full heal on level up
        )
        await message.answer(f"🎉 **سطحت بالا رفت!** 🎉\n\nتبریک، {player['name']}! تو به سطح **{new_level}** رسیدی!\nسلامتی‌ات کامل شد و یک امتیاز برای تخصیص دریافت کردی.")
        return await database.get_player(player['user_id'])
    return player

@router.message(Text(equals="👤 پروفایل من"))
async def my_profile(message: types.Message, state: FSMContext):
    await state.clear() # Clear any previous states
    player = await database.get_player(message.from_user.id)
    if not player:
        return await message.answer("ابتدا باید با /start ثبت‌نام کنی.")

    player = await check_for_level_up(message, player)

    partner_name = "ندارد"
    if player['partner_id']:
        partner_player = await database.get_player(player['partner_id'])
        partner_name = partner_player['name'] if partner_player else "ناشناس"

    xp_needed = calculate_xp_for_next_level(player['level'])
    profile_text = f"""
📜 **کارنامه {player['name']}** 📜

**سطح:** {player['level']} | **تجربه:** {player['xp']}/{xp_needed}
**سلامتی:** {player['health']}/{player['max_health']} ❤️
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
    await message.answer(profile_text, reply_markup=keyboards.profile_menu(player['skill_points'] > 0))

@router.callback_query(lambda c: c.data == "profile:assign_points")
async def assign_points_start(callback_query: types.CallbackQuery, state: FSMContext):
    player = await database.get_player(callback_query.from_user.id)
    if player['skill_points'] <= 0:
        return await callback_query.answer("امتیازی برای تخصیص نداری.", show_alert=True)
    
    await state.set_state(ProfileFSM.assigning_points)
    await callback_query.message.edit_text(
        f"کدام ویژگی را می‌خواهی تقویت کنی؟\n\nتو {player['skill_points']} امتیاز داری.",
        reply_markup=keyboards.stat_assignment_kb()
    )

@router.callback_query(ProfileFSM.assigning_points, lambda c: c.data.startswith("assign_point:"))
async def process_point_assignment(callback_query: types.CallbackQuery, state: FSMContext):
    action = callback_query.data.split(":")[1]
    user_id = callback_query.from_user.id

    if action == "cancel":
        await state.clear()
        await callback_query.message.delete()
        # Create a dummy message to call my_profile
        dummy_message = types.Message(message_id=0, date=datetime.datetime.now(), chat=callback_query.message.chat, from_user=callback_query.from_user)
        await my_profile(dummy_message, state)
        return

    player = await database.get_player(user_id)
    if player['skill_points'] <= 0:
        await state.clear()
        return await callback_query.message.edit_text("امتیازی برای تخصیص نداری.")

    update_data = {
        action: player[action] + 1,
        'skill_points': player['skill_points'] - 1
    }
    await database.update_player(user_id, **update_data)
    
    await callback_query.answer(f"{action.capitalize()} یک واحد افزایش یافت!")
    
    new_player_data = await database.get_player(user_id)
    if new_player_data['skill_points'] > 0:
        await callback_query.message.edit_text(
            f"کدام ویژگی را می‌خواهی تقویت کنی؟\n\nتو {new_player_data['skill_points']} امتیاز داری.",
            reply_markup=keyboards.stat_assignment_kb()
        )
    else:
        await state.clear()
        await callback_query.message.delete()
        dummy_message = types.Message(message_id=0, date=datetime.datetime.now(), chat=callback_query.message.chat, from_user=callback_query.from_user)
        await my_profile(dummy_message, state)

# Bio editing remains the same as previous version
@router.callback_query(lambda c: c.data == "profile:edit_bio")
async def edit_bio_start(callback_query: types.CallbackQuery, state: FSMContext):
    await state.set_state(ProfileFSM.editing_bio)
    await callback_query.message.answer("شرح حال جدید خود را بنویس (حداکثر ۲۰۰ حرف).")
    await callback_query.answer()

@router.message(ProfileFSM.editing_bio)
async def process_bio_edit(message: types.Message, state: FSMContext):
    bio = message.text.strip()
    if len(bio) > 200:
        return await message.answer("شرح حالت بیش از حد طولانی است. لطفاً کوتاه‌تر بنویس.")
    await database.update_player(message.from_user.id, bio=bio)
    await state.clear()
    await message.answer("شرح حال تو با موفقیت ثبت شد.")
    await my_profile(message, state)

