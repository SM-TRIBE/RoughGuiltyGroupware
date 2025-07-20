
import json
import os
from datetime import datetime

def load_json(path):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}

    with open(path, 'r', encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def init_player(user):
    players = load_json('data/players.json')
    uid = str(user.id)
    
    if uid not in players:
        players[uid] = {
            "name": user.first_name or "بازیکن",
            "partner": None,
            "location": "مرکز شهر",
            "traits": {
                "charisma": 5,
                "intelligence": 5,
                "strength": 5,
                "agility": 5,
                "luck": 5
            },
            "money": 1000,
            "xp": 0,
            "level": 1,
            "inventory": [],
            "age_confirmed": False,
            "energy": 100,
            "happiness": 50,
            "mental_health": 50,
            "fitness": 50,
            "social_points": 0,
            "culture_points": 0,
            "current_job": None,
            "work_stats": {},
            "last_work": None,
            "last_daily": None,
            "created_at": datetime.now().isoformat(),
            "skill_points": 0,
            "achievements": [],
            "action_stats": {},
            "active_quests": [],
            "completed_quests": [],
            "equipment": {
                "weapon": None,
                "armor": None,
                "accessory": None
            },
            "battle_stats": {
                "wins": 0,
                "losses": 0,
                "monsters_defeated": 0
            }
        }
        save_json('data/players.json', players)
    
    return players[uid]

def ensure_player_exists(user_id):
    players = load_json('data/players.json')
    if str(user_id) not in players:
        # Create basic player data if not exists
        players[str(user_id)] = {
            "name": "بازیکن جدید",
            "partner": None,
            "location": "مرکز شهر",
            "traits": {"charisma": 5, "intelligence": 5, "strength": 5},
            "money": 1000,
            "xp": 0,
            "level": 1,
            "inventory": [],
            "age_confirmed": False,
            "energy": 100,
            "happiness": 50
        }
        save_json('data/players.json', players)
    return players[str(user_id)]

def check_level_up(player):
    xp = player.get("xp", 0)
    level = player.get("level", 1)
    xp_needed = level * 100
    
    leveled_up = False
    
    while xp >= xp_needed:
        player["level"] = level + 1
        player["xp"] = xp - xp_needed
        
        # Level up bonuses
        player["skill_points"] = player.get("skill_points", 0) + 2
        player["energy"] = 100  # Full energy restore
        player["happiness"] = min(100, player.get("happiness", 50) + 10)
        
        # Update for next level check
        level = player["level"]
        xp = player["xp"]
        xp_needed = level * 100
        leveled_up = True
    
    return leveled_up
