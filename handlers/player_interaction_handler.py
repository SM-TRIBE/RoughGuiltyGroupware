# New handler for /view, /daily, etc.
import datetime
from aiogram import Router, types
from aiogram.filters import Command, CommandObject

from db import database
import config

router = Router()

@router.message(Command("view"))
async def view_player(message: types.Message, command: CommandObject):
    if command.args is None:
        return await message.answer("لطفاً کد کاربری فرد مورد نظر را وارد کن.\nمثال: `/view 12345678`")
    try:
        target_id = int(command.args)
    except ValueError:
        return await message.answer("کد کاربری باید یک عدد باشد.")

    player = await database.get_player(target_id)
    if not player:
        return await message.answer("فردی با این کد کاربری یافت نشد.")

    # Simplified profile view for others
    profile_text = f"""
📜 **کارنامه {player['name']}** 📜
**سطح:** {player['level']}
**شغل:** {player.get('job') or 'بیکار'}
**شرح حال:** _{player.get('bio') or 'شرح حالی ندارد.'}_
**کد کاربری:** `{player['user_id']}`
"""
    await message.answer(profile_text)

@router.message(Text(equals="🎁 پاداش روزانه"), Command("daily"))
async def daily_reward(message: types.Message):
    player = await database.get_player(message.from_user.id)
    if not player: return await message.answer("ابتدا باید با /start ثبت‌نام کنی.")

    last_daily = player.get('last_daily_time')
    if last_daily:
        cooldown = datetime.timedelta(hours=22) # A bit less than a day
        if datetime.datetime.now(datetime.timezone.utc) < last_daily + cooldown:
            return await message.answer("هنوز زمان دریافت پاداش روزانه‌ات فرا نرسیده است.")

    new_money = player['money'] + config.DAILY_REWARD_MONEY
    new_xp = player['xp'] + config.DAILY_REWARD_XP
    
    await database.update_player(
        message.from_user.id,
        money=new_money,
        xp=new_xp,
        last_daily_time=datetime.datetime.now(datetime.timezone.utc)
    )
    await message.answer(f"پاداش روزانه خود را دریافت کردی!\n+{config.DAILY_REWARD_MONEY} سکه 🪙\n+{config.DAILY_REWARD_XP} تجربه ✨")
    # Check for level up after getting XP
    from .profile_handler import check_for_level_up
    await check_for_level_up(message, await database.get_player(message.from_user.id))

