
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from utils.tools import load_json, save_json
import random
from datetime import datetime, timedelta

JOBS = {
    "راننده تاکسی": {
        "salary": 200, "energy_cost": 20, "requirements": {"level": 1},
        "description": "کار ساده با درآمد متوسط"
    },
    "برنامه‌نویس": {
        "salary": 500, "energy_cost": 30, "requirements": {"intelligence": 15, "level": 3},
        "description": "کار فکری با درآمد بالا"
    },
    "مدل": {
        "salary": 400, "energy_cost": 25, "requirements": {"charisma": 20, "level": 2},
        "description": "کار جذاب برای افراد خوش‌ظاهر"
    },
    "ورزشکار": {
        "salary": 350, "energy_cost": 40, "requirements": {"strength": 18, "level": 2},
        "description": "کار بدنی با درآمد خوب"
    },
    "معلم": {
        "salary": 300, "energy_cost": 25, "requirements": {"intelligence": 12, "level": 2},
        "description": "کار آموزشی با احترام اجتماعی"
    },
    "بازیگر": {
        "salary": 600, "energy_cost": 35, "requirements": {"charisma": 25, "intelligence": 15, "level": 4},
        "description": "کار هنری با درآمد عالی"
    }
}

async def job_center(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("💼 مشاهده مشاغل"), KeyboardButton("⚡ کار کردن")],
        [KeyboardButton("📊 آمار کاری"), KeyboardButton("🏠 بازگشت به منو اصلی")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🏢 مرکز اشتغال\n"
        "اینجا می‌توانید شغل انتخاب کنید و کار کنید.",
        reply_markup=reply_markup
    )

async def view_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    p = players[uid]
    
    text = "💼 مشاغل موجود:\n\n"
    available_jobs = []
    
    for job_name, job_info in JOBS.items():
        requirements_met = True
        req_text = "شرایط: "
        
        for req, value in job_info["requirements"].items():
            if req == "level" and p.get("level", 1) < value:
                requirements_met = False
                req_text += f"❌ سطح {value} "
            elif req in p["traits"] and p["traits"][req] < value:
                requirements_met = False
                req_text += f"❌ {req} {value} "
            else:
                req_text += f"✅ {req} {value} "
        
        status = "🟢 قابل انجام" if requirements_met else "🔴 نیاز به ارتقاء"
        if requirements_met:
            available_jobs.append(job_name)
        
        text += f"🏢 {job_name}\n"
        text += f"💰 درآمد: {job_info['salary']} تومان\n"
        text += f"⚡ انرژی مورد نیاز: {job_info['energy_cost']}\n"
        text += f"📝 {job_info['description']}\n"
        text += f"{req_text}\n"
        text += f"{status}\n\n"
    
    keyboard = []
    for job in available_jobs:
        keyboard.append([KeyboardButton(f"کار {job}")])
    
    keyboard.append([KeyboardButton("🚪 بازگشت")])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(text, reply_markup=reply_markup)

async def work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    p = players[uid]
    
    # Check if player has worked recently
    last_work = p.get('last_work')
    if last_work:
        last_work_time = datetime.fromisoformat(last_work)
        if datetime.now() - last_work_time < timedelta(hours=1):
            remaining = timedelta(hours=1) - (datetime.now() - last_work_time)
            await update.message.reply_text(
                f"⏰ شما باید {remaining.seconds // 60} دقیقه صبر کنید تا دوباره کار کنید."
            )
            return
    
    current_job = p.get('current_job')
    if not current_job or current_job not in JOBS:
        await update.message.reply_text("ابتدا یک شغل انتخاب کنید.")
        return
    
    job_info = JOBS[current_job]
    
    if p.get('energy', 100) < job_info['energy_cost']:
        await update.message.reply_text(
            f"انرژی کافی ندارید! نیاز: {job_info['energy_cost']}, دارید: {p.get('energy', 100)}"
        )
        return
    
    # Perform work
    p['energy'] = p.get('energy', 100) - job_info['energy_cost']
    base_salary = job_info['salary']
    
    # Calculate bonus based on traits
    bonus_multiplier = 1.0
    if current_job == "برنامه‌نویس":
        bonus_multiplier += (p['traits']['intelligence'] - 15) * 0.02
    elif current_job == "مدل":
        bonus_multiplier += (p['traits']['charisma'] - 20) * 0.02
    elif current_job == "ورزشکار":
        bonus_multiplier += (p['traits']['strength'] - 18) * 0.02
    
    final_salary = int(base_salary * bonus_multiplier)
    p['money'] += final_salary
    p['xp'] = p.get('xp', 0) + 20
    p['last_work'] = datetime.now().isoformat()
    
    # Work stats
    if 'work_stats' not in p:
        p['work_stats'] = {}
    if current_job not in p['work_stats']:
        p['work_stats'][current_job] = 0
    p['work_stats'][current_job] += 1
    
    save_json('data/players.json', players)
    
    await update.message.reply_text(
        f"💼 کار انجام شد!\n"
        f"💰 درآمد: {final_salary} تومان\n"
        f"⚡ انرژی باقی‌مانده: {p['energy']}\n"
        f"🎯 تجربه: +20 XP"
    )

async def set_job(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text.startswith("کار "):
        return
    
    job_name = text[4:]  # Remove "کار " prefix
    
    if job_name not in JOBS:
        return
    
    user = update.effective_user
    players = load_json('data/players.json')
    uid = str(user.id)
    
    players[uid]['current_job'] = job_name
    save_json('data/players.json', players)
    
    await update.message.reply_text(
        f"✅ شغل شما به {job_name} تغییر یافت!\n"
        f"حالا می‌توانید با دکمه 'کار کردن' شروع کنید."
    )
