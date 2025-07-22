import random
import datetime
from aiogram import Router, types
from aiogram.filters import Text, Command

from db import database
from utils import keyboards
from data.jobs import JOBS
import config

router = Router()

@router.message(Text(equals="⚒️ کار و پیشه"))
async def jobs_menu(message: types.Message):
    player = await database.get_player(message.from_user.id)
    if not player:
        await message.answer("ابتدا باید با /start ثبت‌نام کنی.")
        return

    if player.get('job'):
        await message.answer(f"تو در حال حاضر به عنوان «{player['job']}» مشغول به کار هستی. برای کسب درآمد /work را وارد کن.")
        return

    available_jobs = []
    for job, details in JOBS.items():
        reqs = details['requirements']
        if all(player[stat] >= value for stat, value in reqs.items()):
            available_jobs.append(job)

    if not available_jobs:
        await message.answer("متأسفانه با این توانایی‌ها، هیچ کار مناسبی برای تو پیدا نمی‌شود. سعی کن قوی‌تر شوی.")
        return

    await message.answer("کارهای زیر برای تو موجود است:", reply_markup=keyboards.jobs_kb(available_jobs))

@router.callback_query(lambda c: c.data.startswith("job:get:"))
async def get_job(callback_query: types.CallbackQuery):
    job_name = callback_query.data.split(":")[2]
    await database.update_player(callback_query.from_user.id, job=job_name)
    await callback_query.message.edit_text(f"تبریک! تو به عنوان «{job_name}» استخدام شدی. برای شروع به کار از دستور /work استفاده کن.")
    await callback_query.answer()

@router.message(Command("work"))
async def work_command(message: types.Message):
    player = await database.get_player(message.from_user.id)
    if not player or not player.get('job'):
        await message.answer("تو شغلی نداری که بخواهی کار کنی! ابتدا یک شغل پیدا کن.")
        return

    job_name = player['job']
    job_details = JOBS[job_name]

    last_work_time = player.get('last_work_time')
    if last_work_time:
        cooldown = datetime.timedelta(hours=config.WORK_COOLDOWN_HOURS)
        if datetime.datetime.now(datetime.timezone.utc) < last_work_time + cooldown:
            await message.answer("تو خسته‌ای و هنوز نمی‌توانی کار کنی. کمی استراحت کن.")
            return

    payout = random.randint(job_details['payout_min'], job_details['payout_max'])
    xp_gain = job_details['xp_gain']

    new_money = player['money'] + payout
    new_xp = player['xp'] + xp_gain
    
    await database.update_player(
        message.from_user.id,
        money=new_money,
        xp=new_xp,
        last_work_time=datetime.datetime.now(datetime.timezone.utc)
    )
    await message.answer(f"سخت کار کردی و {payout} سکه نقره و {xp_gain} تجربه به دست آوردی.")
    # Add level up check here
```python
