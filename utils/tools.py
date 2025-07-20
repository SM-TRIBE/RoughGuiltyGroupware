import json
import os
from datetime import datetime
from random import choice

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
    """Initialize player - now only for legacy support"""
    players = load_json('data/players.json')
    uid = str(user.id)

    if uid not in players:
        players[uid] = {
            "name": user.first_name or "بازیکن",
            "partner": None,
            "location": "در انتظار ثبت‌نام",
            "traits": {
                "charisma": 5,
                "intelligence": 5,
                "strength": 5,
                "agility": 5,
                "luck": 5
            },
            "money": 0,
            "level": 1,
            "xp": 0,
            "inventory": [],
            "job": None,
            "skills": {},
            "achievements": [],
            "last_daily": None,
            "skill_points": 0,
            "approved": False,
            "waiting_approval": False
        }
        save_json('data/players.json', players)

    return players[uid]

def check_level_up(player):
    xp = player.get("xp", 0)
    level = player.get("level", 1)
    if xp >= level * 100:
        player["level"] = level + 1
        player["xp"] = 0
        player["skill_points"] = player.get("skill_points", 0) + 2
        return True
    return False

def pick_random_partner(user_id):
    """Pick a random partner from available users"""
    players = load_json('data/players.json')
    available = []

    for uid, player in players.items():
        if (uid != user_id and 
            player.get('approved') and 
            not player.get('partner')):
            available.append({
                'id': uid,
                'name': player.get('name', 'نامشخص'),
                'age': player.get('age', 'نامشخص'),
                'bio': player.get('bio', 'بدون توضیحات')
            })

    return choice(available) if available else None

def add_xp(player, amount):
    """Add XP to player and check for level up"""
    player["xp"] = player.get("xp", 0) + amount
    if check_level_up(player):
        return True
    return False