import asyncpg
import json
from typing import Optional, Dict, List

import config

pool: Optional[asyncpg.Pool] = None

async def connect():
    """Creates a connection pool to the PostgreSQL database."""
    global pool
    if not pool:
        pool = await asyncpg.create_pool(dsn=config.DATABASE_URL)
        await create_tables()
        print("Database connection pool created.")

async def disconnect():
    """Closes the database connection pool."""
    global pool
    if pool:
        await pool.close()
        print("Database connection pool closed.")

async def fetchval(query, *params):
    """Fetch a single value."""
    async with pool.acquire() as connection:
        return await connection.fetchval(query, *params)

async def fetchrow(query, *params):
    """Fetch a single row."""
    async with pool.acquire() as connection:
        return await connection.fetchrow(query, *params)

async def fetch(query, *params):
    """Fetch multiple rows."""
    async with pool.acquire() as connection:
        return await connection.fetch(query, *params)

async def execute(query, *params):
    """Execute a query without returning data."""
    async with pool.acquire() as connection:
        await connection.execute(query, *params)

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
        location VARCHAR(100) DEFAULT 'میدان اصلی',
        job VARCHAR(50),
        inventory JSONB DEFAULT '[]',
        partner_id BIGINT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS marriages (
        id SERIAL PRIMARY KEY,
        player1_id BIGINT NOT NULL,
        player2_id BIGINT NOT NULL,
        married_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(player1_id, player2_id)
    );
    """
    await execute(query)
    print("Tables checked/created successfully.")

# --- Player Management ---
async def get_player(user_id: int) -> Optional[asyncpg.Record]:
    """Retrieves a player's data from the database."""
    return await fetchrow("SELECT * FROM players WHERE user_id = $1", user_id)

async def create_player(user_id: int, name: str):
    """Creates a new player in the database."""
    query = """
    INSERT INTO players (user_id, name, money, location)
    VALUES ($1, $2, $3, $4)
    """
    await execute(query, user_id, name, config.STARTING_MONEY, config.STARTING_LOCATION)

async def save_player(user_id: int, data: Dict):
    """Saves a player's data. A more robust version of this would be better."""
    # This is a simplified save function. For a real game, you'd update specific fields.
    query = """
    UPDATE players SET
        name = $2, bio = $3, level = $4, xp = $5, money = $6,
        strength = $7, agility = $8, intelligence = $9,
        location = $10, job = $11, inventory = $12, partner_id = $13
    WHERE user_id = $1
    """
    await execute(
        query, user_id, data['name'], data.get('bio'), data['level'], data['xp'],
        data['money'], data['strength'], data['agility'], data['intelligence'],
        data['location'], data.get('job'), json.dumps(data.get('inventory', [])),
        data.get('partner_id')
    )
