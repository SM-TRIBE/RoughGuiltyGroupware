import asyncpg
import json
import datetime
from typing import Optional, Dict, List

import config

pool: Optional[asyncpg.Pool] = None

# --- Connection Management ---
async def connect():
    """Creates a connection pool to the PostgreSQL database."""
    global pool
    if not pool:
        try:
            pool = await asyncpg.create_pool(dsn=config.DATABASE_URL)
            await create_tables()
            print("Database connection pool created successfully.")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise

async def disconnect():
    """Closes the database connection pool."""
    global pool
    if pool:
        await pool.close()
        print("Database connection pool closed.")

# --- Query Execution ---
async def execute(query, *params):
    async with pool.acquire() as connection:
        await connection.execute(query, *params)

async def fetchrow(query, *params):
    async with pool.acquire() as connection:
        return await connection.fetchrow(query, *params)

async def fetchval(query, *params):
    async with pool.acquire() as connection:
        return await connection.fetchval(query, *params)

async def fetch(query, *params):
    async with pool.acquire() as connection:
        return await connection.fetch(query, *params)

# --- Schema ---
async def create_tables():
    """Creates the necessary tables if they don't exist."""
    query = """
    CREATE TABLE IF NOT EXISTS players (
        user_id BIGINT PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        bio TEXT,
        level INT DEFAULT 1,
        xp INT DEFAULT 0,
        money BIGINT DEFAULT 100,
        strength INT DEFAULT 5,
        agility INT DEFAULT 5,
        intelligence INT DEFAULT 5,
        skill_points INT DEFAULT 0,
        location VARCHAR(100) DEFAULT 'میدان اصلی',
        job VARCHAR(50),
        last_work_time TIMESTAMP WITH TIME ZONE,
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
    query = "INSERT INTO players (user_id, name, money, location) VALUES ($1, $2, $3, $4)"
    await execute(query, user_id, name, config.STARTING_MONEY, config.STARTING_LOCATION)

async def update_player(user_id: int, **kwargs):
    """Updates specific fields for a player."""
    fields = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(kwargs.keys())])
    values = list(kwargs.values())
    query = f"UPDATE players SET {fields} WHERE user_id = $1"
    await execute(query, user_id, *values)

async def get_players_in_location(location: str, exclude_user_id: int) -> List[asyncpg.Record]:
    """Finds other players in the same location."""
    query = "SELECT user_id, name FROM players WHERE location = $1 AND user_id != $2"
    return await fetch(query, location, exclude_user_id)
