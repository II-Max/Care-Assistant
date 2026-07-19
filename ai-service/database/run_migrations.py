"""
🔄 Database Migration Runner — AI Customer Care Assistant
Bệnh viện Tim Hà Nội

Tự động chạy migrations khi khởi động:
1. PostgreSQL: chạy 001 + 002 qua asyncpg
2. SQLite: chạy 001 + 002 qua aiosqlite

Usage:
    python database/run_migrations.py

Hoặc tự động chạy khi main.py startup.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

logger = logging.getLogger("migrations")

MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"


async def run_migrations():
    """Chạy tất cả migrations chưa được apply."""
    print("\n🔄 Running database migrations...")

    # Try PostgreSQL first
    try:
        from database.connection import database

        await database.initialize()
        if database.is_ready:
            print("   ✅ Database connected")
            await _run_pg_migrations(database)
            return
    except Exception as e:
        print(f"   ⚠️ PostgreSQL: {e}")

    # Fallback: SQLite
    print("   ⚠️ Fallback: SQLite (dữ liệu sẽ mất khi restart)")
    print("   ℹ️  Dùng PostgreSQL cho production: docker-compose up -d postgres")
    await _run_sqlite_migrations()


async def _run_pg_migrations(db):
    """Chạy migrations trên PostgreSQL."""
    try:
        # Check which migrations have been applied
        await db.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(64) PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        applied = set()
        rows = await db.fetch("SELECT version FROM schema_migrations")
        for row in rows:
            applied.add(row["version"])

        migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
        for filepath in migration_files:
            version = filepath.stem  # e.g., "001_initial_schema"
            if version in applied:
                print(f"   ✅ [SKIP] {filepath.name} — already applied")
                continue

            print(f"   🔄 Applying {filepath.name}...")
            with open(filepath, "r", encoding="utf-8") as f:
                sql = f.read()

            # Split by semicolons and execute each statement
            statements = [s.strip() for s in sql.split(";") if s.strip()]
            for stmt in statements:
                # Skip comments
                if stmt.startswith("--"):
                    continue
                try:
                    # Remove OR IGNORE for PostgreSQL compatibility
                    clean_stmt = stmt.replace("OR IGNORE", "")
                    await db.execute(clean_stmt)
                except Exception as e:
                    # Ignore "already exists" errors
                    if "already exists" in str(e) or "duplicate" in str(e):
                        continue
                    logger.warning(f"   ⚠️ Statement warning: {e}")

            # Record migration
            await db.execute(
                "INSERT INTO schema_migrations (version, filename) VALUES ($1, $2)",
                version, filepath.name
            )
            print(f"   ✅ {filepath.name} applied")

        print("   ✅ All PostgreSQL migrations complete")

    except Exception as e:
        logger.error(f"   ❌ PostgreSQL migration failed: {e}")
        raise


async def _run_sqlite_migrations():
    """Chạy migrations trên SQLite (aiosqlite)."""
    db_path = Path(__file__).resolve().parent.parent / "data" / "care_assistant.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    import aiosqlite

    async with aiosqlite.connect(str(db_path)) as db:
        db.row_factory = aiosqlite.Row

        # Create migrations tracking table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Get applied migrations
        cursor = await db.execute("SELECT version FROM schema_migrations")
        applied = {row["version"] for row in await cursor.fetchall()}

        migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
        for filepath in migration_files:
            version = filepath.stem
            if version in applied:
                print(f"   ✅ [SKIP] {filepath.name} — already applied")
                continue

            print(f"   🔄 Applying {filepath.name}...")
            with open(filepath, "r", encoding="utf-8") as f:
                sql = f.read()

            # Execute all statements
            await db.executescript(sql)

            # Record migration
            await db.execute(
                "INSERT INTO schema_migrations (version, filename) VALUES (?, ?)",
                (version, filepath.name)
            )
            await db.commit()
            print(f"   ✅ {filepath.name} applied")

        print("   ✅ All SQLite migrations complete")


if __name__ == "__main__":
    # Add project root to path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    asyncio.run(run_migrations())
