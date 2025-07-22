import asyncpg
import json
import datetime
from typing import Optional, Dict, List

import config

pool: Optional[asyncpg.Pool] = None

# --- Connection & Query Execution (No changes from previous version) ---
async def connect():
    global pool
    if not pool:
        pool = await asyncpg.create_pool(dsn=config.DATABASE_URL)
        await create_tables()
        print("Database connection pool created.")

async def disconnect():
    global pool
    if pool: await pool.close()

async def execute(query, *params):
    async with pool.acquire() as c: await c.execute(query, *params)

async def fetchrow(query, *params):
    async with pool.acquire() as c: return await c.fetchrow(query, *params)

async def fetchval(query, *params):
    async with pool.acquire() as c: return await c.fetchval(query, *params)

async def fetch(query, *params):
    async with pool.acquire() as c: return await c.fetch(query, *params)

# --- Schema ---
async def create_tables():
    """Creates/updates the necessary tables."""
    query = """
    CREATE TABLE IF NOT EXISTS players (
        user_id BIGINT PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        bio TEXT,
        level INT DEFAULT 1,
        xp INT DEFAULT 0,
        health INT DEFAULT 100,
        max_health INT DEFAULT 100,
        money BIGINT DEFAULT 100,
        strength INT DEFAULT 5,
        agility INT DEFAULT 5,
        intelligence INT DEFAULT 5,
        skill_points INT DEFAULT 0,
        location VARCHAR(100) DEFAULT 'میدان اصلی',
        job VARCHAR(50),
        last_work_time TIMESTAMP WITH TIME ZONE,
        last_daily_time TIMESTAMP WITH TIME ZONE,
        inventory JSONB DEFAULT '[]',
        partner_id BIGINT,
        proposal_from_id BIGINT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
    await execute(query)
    print("Player table checked/created successfully.")

# --- Player Management ---
async def get_player(user_id: int) -> Optional[asyncpg.Record]:
    return await fetchrow("SELECT * FROM players WHERE user_id = $1", user_id)

async def create_player(user_id: int, name: str):
    query = """
    INSERT INTO players (user_id, name, money, location, health, max_health)
    VALUES ($1, $2, $3, $4, $5, $6)
    """
    await execute(query, user_id, name, config.STARTING_MONEY, config.STARTING_LOCATION, config.STARTING_HEALTH, config.STARTING_HEALTH)

async def update_player(user_id: int, **kwargs):
    fields = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(kwargs.keys())])
    values = list(kwargs.values())
    query = f"UPDATE players SET {fields} WHERE user_id = $1"
    await execute(query, user_id, *values)

async def get_players_in_location(location: str, exclude_user_id: int) -> List[asyncpg.Record]:
    query = "SELECT user_id, name FROM players WHERE location = $1 AND user_id != $2"
    return await fetch(query, location, exclude_user_id)

async def get_top_players(by: str = 'level', limit: int = 10) -> List[asyncpg.Record]:
    """Fetches top players by a given stat."""
    if by not in ['level', 'money', 'strength']: # Whitelist columns
        by = 'level'
    query = f"SELECT name, {by} FROM players ORDER BY {by} DESC, name ASC LIMIT $1"
    return await fetch(query, limit)
