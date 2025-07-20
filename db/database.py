
import psycopg2
import psycopg2.extras
import os
import json
from typing import Dict, List, Any, Optional

class Database:
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        if not self.database_url:
            print("Warning: DATABASE_URL not found. Using JSON files as fallback.")
            self.use_postgres = False
        else:
            self.use_postgres = True
            self.init_tables()
    
    def get_connection(self):
        if not self.use_postgres:
            return None
        return psycopg2.connect(self.database_url)
    
    def init_tables(self):
        """Initialize database tables"""
        if not self.use_postgres:
            return
            
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            
            # Players table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    telegram_id BIGINT PRIMARY KEY,
                    username VARCHAR(255),
                    name VARCHAR(255) NOT NULL,
                    age INTEGER,
                    bio TEXT,
                    photo_id VARCHAR(255),
                    voice_id VARCHAR(255),
                    waiting_approval BOOLEAN DEFAULT FALSE,
                    approved BOOLEAN DEFAULT FALSE,
                    registration_date TIMESTAMP,
                    location VARCHAR(255) DEFAULT 'میدان اصلی',
                    money BIGINT DEFAULT 1000,
                    level INTEGER DEFAULT 1,
                    xp INTEGER DEFAULT 0,
                    partner VARCHAR(255),
                    job VARCHAR(255),
                    last_daily TIMESTAMP,
                    skill_points INTEGER DEFAULT 0,
                    charisma INTEGER DEFAULT 5,
                    intelligence INTEGER DEFAULT 5,
                    strength INTEGER DEFAULT 5,
                    agility INTEGER DEFAULT 5,
                    luck INTEGER DEFAULT 5,
                    inventory JSONB DEFAULT '[]',
                    skills JSONB DEFAULT '{}',
                    achievements JSONB DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Chat messages table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id SERIAL PRIMARY KEY,
                    sender_id BIGINT NOT NULL,
                    sender_name VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_public BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Marriages table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS marriages (
                    id SERIAL PRIMARY KEY,
                    player1_id BIGINT NOT NULL,
                    player2_id BIGINT NOT NULL,
                    married_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(player1_id, player2_id)
                )
            """)
            
            # God actions log table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS god_actions (
                    id SERIAL PRIMARY KEY,
                    action_type VARCHAR(100) NOT NULL,
                    target_id BIGINT,
                    action_data JSONB,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    description TEXT
                )
            """)
            
            conn.commit()
            cur.close()
            conn.close()
            print("✅ PostgreSQL tables initialized successfully!")
            
        except Exception as e:
            print(f"❌ Error initializing PostgreSQL tables: {e}")
    
    # Player operations
    def get_player(self, telegram_id: int) -> Optional[Dict]:
        if not self.use_postgres:
            from utils.tools import load_json
            players = load_json('data/players.json')
            return players.get(str(telegram_id))
        
        try:
            conn = self.get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cur.execute("SELECT * FROM players WHERE telegram_id = %s", (telegram_id,))
            result = cur.fetchone()
            
            cur.close()
            conn.close()
            
            if result:
                # Convert to dict and handle JSON fields
                player = dict(result)
                player['traits'] = {
                    'charisma': player['charisma'],
                    'intelligence': player['intelligence'],
                    'strength': player['strength'],
                    'agility': player['agility'],
                    'luck': player['luck']
                }
                return player
            return None
            
        except Exception as e:
            print(f"Error getting player: {e}")
            return None
    
    def save_player(self, telegram_id: int, player_data: Dict):
        if not self.use_postgres:
            from utils.tools import load_json, save_json
            players = load_json('data/players.json')
            players[str(telegram_id)] = player_data
            save_json('data/players.json', players)
            return
        
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            
            # Extract traits
            traits = player_data.get('traits', {})
            
            cur.execute("""
                INSERT INTO players (
                    telegram_id, username, name, age, bio, photo_id, voice_id,
                    waiting_approval, approved, registration_date, location,
                    money, level, xp, partner, job, last_daily, skill_points,
                    charisma, intelligence, strength, agility, luck,
                    inventory, skills, achievements
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (telegram_id) DO UPDATE SET
                    username = EXCLUDED.username,
                    name = EXCLUDED.name,
                    age = EXCLUDED.age,
                    bio = EXCLUDED.bio,
                    photo_id = EXCLUDED.photo_id,
                    voice_id = EXCLUDED.voice_id,
                    waiting_approval = EXCLUDED.waiting_approval,
                    approved = EXCLUDED.approved,
                    location = EXCLUDED.location,
                    money = EXCLUDED.money,
                    level = EXCLUDED.level,
                    xp = EXCLUDED.xp,
                    partner = EXCLUDED.partner,
                    job = EXCLUDED.job,
                    last_daily = EXCLUDED.last_daily,
                    skill_points = EXCLUDED.skill_points,
                    charisma = EXCLUDED.charisma,
                    intelligence = EXCLUDED.intelligence,
                    strength = EXCLUDED.strength,
                    agility = EXCLUDED.agility,
                    luck = EXCLUDED.luck,
                    inventory = EXCLUDED.inventory,
                    skills = EXCLUDED.skills,
                    achievements = EXCLUDED.achievements,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                telegram_id, player_data.get('username', ''), player_data.get('name', ''),
                player_data.get('age'), player_data.get('bio'), player_data.get('photo_id'),
                player_data.get('voice_id'), player_data.get('waiting_approval', False),
                player_data.get('approved', False), player_data.get('registration_date'),
                player_data.get('location', 'میدان اصلی'), player_data.get('money', 1000),
                player_data.get('level', 1), player_data.get('xp', 0), player_data.get('partner'),
                player_data.get('job'), player_data.get('last_daily'), player_data.get('skill_points', 0),
                traits.get('charisma', 5), traits.get('intelligence', 5), traits.get('strength', 5),
                traits.get('agility', 5), traits.get('luck', 5),
                json.dumps(player_data.get('inventory', [])),
                json.dumps(player_data.get('skills', {})),
                json.dumps(player_data.get('achievements', []))
            ))
            
            conn.commit()
            cur.close()
            conn.close()
            
        except Exception as e:
            print(f"Error saving player: {e}")
    
    def get_all_players(self) -> Dict:
        if not self.use_postgres:
            from utils.tools import load_json
            return load_json('data/players.json')
        
        try:
            conn = self.get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cur.execute("SELECT * FROM players")
            results = cur.fetchall()
            
            cur.close()
            conn.close()
            
            players = {}
            for row in results:
                player = dict(row)
                player['traits'] = {
                    'charisma': player['charisma'],
                    'intelligence': player['intelligence'],
                    'strength': player['strength'],
                    'agility': player['agility'],
                    'luck': player['luck']
                }
                players[str(player['telegram_id'])] = player
            
            return players
            
        except Exception as e:
            print(f"Error getting all players: {e}")
            return {}
    
    def log_god_action(self, action_type: str, target_id: int = None, action_data: Dict = None, description: str = ""):
        if not self.use_postgres:
            return
        
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO god_actions (action_type, target_id, action_data, description)
                VALUES (%s, %s, %s, %s)
            """, (action_type, target_id, json.dumps(action_data) if action_data else None, description))
            
            conn.commit()
            cur.close()
            conn.close()
            
        except Exception as e:
            print(f"Error logging god action: {e}")
    
    def get_god_stats(self) -> Dict:
        if not self.use_postgres:
            players = self.get_all_players()
            return {
                'total_players': len(players),
                'approved_players': sum(1 for p in players.values() if p.get('approved')),
                'total_money': sum(p.get('money', 0) for p in players.values()),
                'avg_level': sum(p.get('level', 1) for p in players.values()) / len(players) if players else 0
            }
        
        try:
            conn = self.get_connection()
            cur = conn.cursor()
            
            cur.execute("""
                SELECT 
                    COUNT(*) as total_players,
                    COUNT(*) FILTER (WHERE approved = true) as approved_players,
                    COUNT(*) FILTER (WHERE waiting_approval = true) as waiting_approval,
                    SUM(money) as total_money,
                    AVG(level) as avg_level,
                    MAX(level) as max_level,
                    COUNT(*) FILTER (WHERE partner IS NOT NULL) as married_players
                FROM players
            """)
            
            result = cur.fetchone()
            cur.close()
            conn.close()
            
            if result:
                return {
                    'total_players': result[0] or 0,
                    'approved_players': result[1] or 0,
                    'waiting_approval': result[2] or 0,
                    'total_money': result[3] or 0,
                    'avg_level': float(result[4]) if result[4] else 0,
                    'max_level': result[5] or 0,
                    'married_players': result[6] or 0
                }
            
            return {}
            
        except Exception as e:
            print(f"Error getting god stats: {e}")
            return {}

# Global database instance
db = Database()
