"""
Database Migration and Setup Script

Script för att köra databasmigreringar och setup.
"""

import asyncio
import asyncpg
import os
import sys
from pathlib import Path


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://lovable:lovable123@localhost:5433/lovable_db")


async def check_database_connection():
    """Check if database is accessible."""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        version = await conn.fetchval("SELECT version()")
        await conn.close()
        print(f"✅ Database connection successful: {version}")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


async def run_migrations():
    """Run database migrations."""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Read and execute init script
        init_script = Path("docker/postgres/init/01-init.sql")
        if init_script.exists():
            with open(init_script, 'r', encoding='utf-8') as f:
                sql = f.read()
            
            # Execute script
            await conn.execute(sql)
            print("✅ Database schema initialized successfully")
        else:
            print("⚠️  Init script not found, skipping...")
        
        # Check tables
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        print(f"📊 Database contains {len(tables)} tables:")
        for table in tables:
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table['table_name']}")
            print(f"   • {table['table_name']}: {count} records")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    return True


async def create_sample_data():
    """Create sample data for testing."""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Check if admin user exists
        admin_exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM users WHERE username = 'admin')"
        )
        
        if not admin_exists:
            print("👤 Creating admin user...")
            # This would be handled by the init script
            pass
        
        # Create sample project for admin
        admin_id = await conn.fetchval("SELECT id FROM users WHERE username = 'admin'")
        if admin_id:
            project_exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM projects WHERE owner_id = $1)",
                admin_id
            )
            
            if not project_exists:
                await conn.execute(
                    "INSERT INTO projects (name, description, owner_id) VALUES ($1, $2, $3)",
                    "Sample Project", "A sample project for testing", admin_id
                )
                print("📁 Created sample project")
        
        await conn.close()
        print("✅ Sample data created successfully")
        
    except Exception as e:
        print(f"❌ Sample data creation failed: {e}")
        return False
    
    return True


async def main():
    """Main migration function."""
    print("🔄 Starting database migration...")
    
    # Check connection
    if not await check_database_connection():
        sys.exit(1)
    
    # Run migrations
    if not await run_migrations():
        sys.exit(1)
    
    # Create sample data
    if not await create_sample_data():
        print("⚠️  Sample data creation failed, but migration was successful")
    
    print("🎉 Database migration completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
