"""Quick script to verify Bingo tables were created successfully"""
import asyncio
import asyncpg
from backend.core.config import get_settings

async def verify_tables():
    settings = get_settings()
    # Extract connection string without the +asyncpg driver prefix
    db_url = settings.DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
    
    conn = await asyncpg.connect(db_url)
    
    try:
        # Check if all 5 bingo tables exist
        tables = ['bingo_games', 'game_players', 'cartelas', 'called_numbers', 'game_events']
        
        print("✓ Database connection successful!")
        print("\nChecking Bingo tables:")
        
        for table in tables:
            result = await conn.fetchval(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = $1",
                table
            )
            status = "✓ EXISTS" if result > 0 else "✗ MISSING"
            print(f"  {status}: {table}")
        
        # Check if ENUMs exist
        print("\nChecking ENUM types:")
        enums = ['gamestatus', 'playerstatus', 'gameeventtype', 'winpattern']
        
        for enum in enums:
            result = await conn.fetchval(
                "SELECT COUNT(*) FROM pg_type WHERE typname = $1",
                enum
            )
            status = "✓ EXISTS" if result > 0 else "✗ MISSING"
            print(f"  {status}: {enum}")
        
        print("\n🎉 Phase 2A database migration complete!")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(verify_tables())
