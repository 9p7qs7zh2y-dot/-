from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncpg
import json
from datetime import datetime

# ===== ВАША СТРОКА ПОДКЛЮЧЕНИЯ К POSTGRESQL =====
DATABASE_URL = "postgresql://postgres:vqF-tf3-sCu-m64@db.sppitirtojodgoaworuo.supabase.co:5432/postgres"

class TapAction(BaseModel):
    user_id: int
    taps_count: int

async def init_db():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
    CREATE TABLE IF NOT EXISTS players (
        user_id BIGINT PRIMARY KEY,
        name TEXT NOT NULL,
        level INTEGER DEFAULT 1,
        exp INTEGER DEFAULT 0,
        leaves REAL DEFAULT 0,
        stars INTEGER DEFAULT 0,
        tap_power REAL DEFAULT 1,
        energy INTEGER DEFAULT 100,
        max_energy INTEGER DEFAULT 100,
        has_premium BOOLEAN DEFAULT FALSE,
        daily_streak INTEGER DEFAULT 1,
        total_taps INTEGER DEFAULT 0,
        total_leaves REAL DEFAULT 0,
        battles_won INTEGER DEFAULT 0,
        boosts TEXT DEFAULT '{}',
        daily_tasks TEXT DEFAULT '{}',
        challenges TEXT DEFAULT '{}',
        last_energy_update TEXT
    )
    ''')
    await conn.close()
    print("✅ База данных PostgreSQL подключена")

async def get_player(user_id: int):
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow('SELECT * FROM players WHERE user_id = $1', user_id)
    await conn.close()
    if not row:
        return None
    return dict(row)

async def save_player(player_data: dict):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute('''
    INSERT INTO players (
        user_id, name, level, exp, leaves, stars, tap_power,
        energy, max_energy, has_premium, daily_streak, total_taps,
        total_leaves, battles_won, boosts, daily_tasks, challenges, last_energy_update
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
    ON CONFLICT (user_id) DO UPDATE SET
        name = EXCLUDED.name,
        level = EXCLUDED.level,
        exp = EXCLUDED.exp,
        leaves = EXCLUDED.leaves,
        stars = EXCLUDED.stars,
        tap_power = EXCLUDED.tap_power,
        energy = EXCLUDED.energy,
        max_energy = EXCLUDED.max_energy,
        has_premium = EXCLUDED.has_premium,
        daily_streak = EXCLUDED.daily_streak,
        total_taps = EXCLUDED.total_taps,
        total_leaves = EXCLUDED.total_leaves,
        battles_won = EXCLUDED.battles_won,
        boosts = EXCLUDED.boosts,
        daily_tasks = EXCLUDED.daily_tasks,
        challenges = EXCLUDED.challenges,
        last_energy_update = EXCLUDED.last_energy_update
    ''', (
        player_data['user_id'], player_data['name'], player_data['level'],
        player_data['exp'], player_data['leaves'], player_data['stars'],
        player_data['tap_power'], player_data['energy'], player_data['max_energy'],
        player_data['has_premium'], player_data['daily_streak'],
        player_data['total_taps'], player_data['total_leaves'], player_data['battles_won'],
        json.dumps(player_data['boosts']), json.dumps(player_data['daily_tasks']),
        json.dumps(player_data['challenges']), player_data.get('last_energy_update')
    ))
    await conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Подключение к базе данных...")
    await init_db()
    yield
    print("🛑 Отключение от базы данных...")

app = FastAPI(title="Koala Quest API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/player/register")
async def register_player(user_id: int, name: str):
    if await get_player(user_id):
        return {"status": "exists"}
    new_player = {
        'user_id': user_id,
        'name': name,
        'level': 1,
        'exp': 0,
        'leaves': 500,
        'stars': 0,
        'tap_power': 1,
        'energy': 100,
        'max_energy': 100,
        'has_premium': False,
        'daily_streak': 1,
        'total_taps': 0,
        'total_leaves': 0,
        'battles_won': 0,
        'boosts': {},
        'daily_tasks': {},
        'challenges': {},
        'last_energy_update': datetime.now().isoformat()
    }
    await save_player(new_player)
    return {"status": "success", "player": new_player}

@app.get("/api/player/{user_id}")
async def get_player_data(user_id: int):
    player = await get_player(user_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player

@app.post("/api/tap")
async def process_tap(tap_data: TapAction):
    player = await get_player(tap_data.user_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    gain = player['tap_power']
    if player['has_premium']:
        gain *= 2
    
    player['energy'] -= tap_data.taps_count
    player['leaves'] += gain * tap_data.taps_count
    player['total_taps'] += tap_data.taps_count
    player['total_leaves'] += gain * tap_data.taps_count
    
    await save_player(player)
    
    return {
        "success": True,
        "new_leaves": player['leaves'],
        "new_energy": player['energy'],
        "gain": gain
    }

@app.get("/api/leaderboard")
async def get_leaderboard(limit: int = 50):
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch('''
    SELECT user_id, name, level, total_taps, total_leaves
    FROM players
    ORDER BY level DESC, total_taps DESC
    LIMIT $1
    ''', limit)
    await conn.close()
    return [dict(row) for row in rows]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)