from aiogram import Router, types
from aiogram.filters import Text, Command

from db import database

router = Router()

@router.message(Text(equals="🏆 قهرمانان"), Command("leaderboard"))
async def leaderboard(message: types.Message):
    top_level = await database.get_top_players('level', 5)
    top_money = await database.get_top_players('money', 5)

    level_text = "\n".join([f"{i+1}. {p['name']} (سطح {p['level']})" for i, p in enumerate(top_level)])
    money_text = "\n".join([f"{i+1}. {p['name']} ({p['money']} سکه)" for i, p in enumerate(top_money)])

    response = f"""
👑 **تالار قهرمانان شهرستان وحشی** 👑

**برترین‌ها بر اساس سطح:**
{level_text}

**ثروتمندترین‌ها:**
{money_text}
"""
    await message.answer(response)
