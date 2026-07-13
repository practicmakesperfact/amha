import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

url = os.environ["DATABASE_URL"].replace("postgresql+asyncpg://", "postgresql://")

async def check():
    conn = await asyncpg.connect(url)
    tables = await conn.fetch(
        "SELECT tablename FROM pg_tables WHERE schemaname='public'"
    )
    print("Tables in DB:", [t["tablename"] for t in tables])
    await conn.close()

asyncio.run(check())
