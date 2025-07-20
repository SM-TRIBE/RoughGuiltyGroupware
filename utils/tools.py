import json
import os
from datetime import datetime
from random import choice

def load_json(path):
    """Load JSON file with fallback support for database"""
    from db.database import db
    
    # If it's players.json, try to use database first
    if 'players.json' in path and hasattr(db, 'use_postgres') and db.use_postgres:
        return db.get_all_players()
    
    # Fallback to file system
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

def datetime_converter(o):
    """Convert datetime objects to ISO string for JSON serialization"""
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(f"Object of type {type(o)} is not JSON serializable")

def save_json(path, data):
    """Save JSON file with database support"""
    from db.database import db
    
    # If it's players.json and we're using postgres, save to database
    if 'players.json' in path and hasattr(db, 'use_postgres') and db.use_postgres:
        for uid, player_data in data.items():
            try:
                db.save_player(int(uid), player_data)
            except Exception as e:
                print(f"Database save error for player {uid}: {e}")
        return
    
    # Fallback to file system with datetime serialization
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=datetime_converter)

def init_player(user_id, name, age):
    """Initialize a new player with default values"""
    return {
        "telegram_id": user_id,
        "name": name,
        "age": age,
        "approved": False,
        "waiting_approval": True,
        "location": "میدان اصلی",
        "traits": {
            "charisma": 5,
            "intelligence": 5,
            "strength": 5,
            "agility": 5,
            "luck": 5
        },
        "money": 1000,
        "level": 1,
        "xp": 0,
        "energy": 100,
        "inventory": [],
        "partner": None,
        "job": None,
        "current_job": None,
        "skills": {},
        "achievements": [],
        "last_daily": None,
        "last_work": None,
        "skill_points": 0,
        "friends": [],
        "social_activities": {},
        "privacy_settings": {
            "allow_friend_requests": True,
            "show_online_status": True,
            "allow_gifts": True,
            "show_location": True
        },
        "work_stats": {},
        "prophet": False,
        "last_seen": datetime.now().isoformat()
    }

def check_level_up(player):
    """Check if player should level up and apply changes"""
    current_level = player.get('level', 1)
    current_xp = player.get('xp', 0)
    xp_needed = current_level * 100
    
    if current_xp >= xp_needed:
        player['level'] = current_level + 1
        player['xp'] = current_xp - xp_needed
        player['skill_points'] = player.get('skill_points', 0) + 2
        return True
    return False

def pick_random_partner(exclude_uid):
    """Pick a random partner for dating"""
    players = load_json('data/players.json')
    candidates = []
    
    for uid, player in players.items():
        if uid != exclude_uid and player.get('approved') and not player.get('partner'):
            candidates.append(player)
    
    if candidates:
        return choice(candidates)
    return None
                db.save_player(int(uid), player_data)
            except (ValueError, TypeError):
                continue
    
    # Always save to file as backup
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