# handlers/achievements.py

# 1. Use imports from aiogram
from aiogram import Router, types
from aiogram.filters import Command

# 2. Create a router for this file
router = Router()

# This is a placeholder for your database logic.
# Make sure you import your actual database instance correctly.
from db.database import db 

# 3. Use the router to register the command handler
@router.message(Command("achievements"))
async def achievements_menu(message: types.Message): # 4. Use aiogram's 'types.Message'
    """
    Displays the player's achievements.
    """
    try:
        player_id = message.from_user.id
        player = db.get_player(player_id)

        if not player or not player.get('approved', False):
            await message.answer("You need to be a registered and approved player to see your achievements.")
            return

        achievements = player.get('achievements', [])

        if not achievements:
            response_text = "🏆 **Your Achievements** 🏆\n\nYou haven't earned any achievements yet. Keep exploring and interacting to unlock them!"
        else:
            response_text = "🏆 **Your Achievements** 🏆\n\n"
            for achievement in achievements:
                # Assuming achievement is a dict like {'name': 'Explorer', 'description': 'Visited 10 zones'}
                name = achievement.get('name', 'Unknown Achievement')
                description = achievement.get('description', 'No description available.')
                response_text += f"🏅 **{name}**: {description}\n"

        await message.answer(response_text)

    except Exception as e:
        print(f"Error in achievements_menu: {e}")
        await message.answer("Sorry, there was an error fetching your achievements. Please try again later.")
