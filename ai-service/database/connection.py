"""
Database Connection — asyncpg connection pool.

Config:
- DATABASE_URL: PostgreSQL connection string
- Pool min/max size
- Fallback: SQLite in-memory (cho development)
"""

import os
import json
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger("database")


@dataclass
class DatabaseConfig:
    """Cau hinh ket noi database."""
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "5432"))
    database: str = os.getenv("DB_NAME", "care_assistant")
    user: str = os.getenv("DB_USER", "app_user")
    password: str = os.getenv("DB_PASSWORD", "")
    min_size: int = int(os.getenv("DB_POOL_MIN", "2"))
    max_size: int = int(os.getenv("DB_POOL_MAX", "10"))
    command_timeout: int = 30


class Database:
    """Quan ly asyncpg connection pool.

    Fallback ve SQLite in-memory neu PostgreSQL khong available.
    """

    def __init__(self):
        self._pool = None
        self._fallback_conn = None
        self._use_pg = False
        self._initialized = False

    @property
    def is_ready(self) -> bool:
        return self._initialized

    @property
    def is_postgres(self) -> bool:
        return self._use_pg

    @staticmethod
    def _pg_to_sqlite(query: str) -> str:
        """Convert $1, $2, ... placeholders to ? for SQLite compatibility."""
        import re
        return re.sub(r'\$(\d+)', '?', query)

    async def initialize(self, config: Optional[DatabaseConfig] = None):
        """Initialize database connection.

        Thu PostgreSQL truoc, fallback SQLite neu that bai.
        """
        cfg = config or DatabaseConfig()

        # Try PostgreSQL
        if cfg.password:
            try:
                import asyncpg
                self._pool = await asyncpg.create_pool(
                    host=cfg.host, port=cfg.port,
                    database=cfg.database, user=cfg.user,
                    password=cfg.password,
                    min_size=cfg.min_size, max_size=cfg.max_size,
                    command_timeout=cfg.command_timeout
                )
                self._use_pg = True
                self._initialized = True
                logger.info(f"PostgreSQL connected: {cfg.host}:{cfg.port}/{cfg.database}")
                return
            except Exception as e:
                logger.warning(f"PostgreSQL connection failed: {e}")

        # Fallback: SQLite in-memory
        logger.info("Falling back to SQLite in-memory database")
        self._fallback_conn = SQLiteFallback()
        self._use_pg = False
        self._initialized = True

    async def close(self):
        """Close connection pool."""
        if self._pool:
            await self._pool.close()
        self._initialized = False

    async def execute(self, query: str, *args) -> str:
        """Execute query tra ve string (INSERT RETURNING id)."""
        if self._use_pg:
            async with self._pool.acquire() as conn:
                return await conn.fetchval(query, *args)
        else:
            return self._fallback_conn.execute(self._pg_to_sqlite(query), *args)

    async def fetch(self, query: str, *args) -> list:
        """Fetch nhieu rows."""
        if self._use_pg:
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(query, *args)
                return [dict(row) for row in rows]
        else:
            return self._fallback_conn.fetch(self._pg_to_sqlite(query), *args)

    async def fetchrow(self, query: str, *args) -> Optional[dict]:
        """Fetch mot row."""
        if self._use_pg:
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow(query, *args)
                return dict(row) if row else None
        else:
            return self._fallback_conn.fetchrow(self._pg_to_sqlite(query), *args)

    async def execute_many(self, query: str, args_list: list):
        """Execute cung query voi nhieu args sets."""
        if self._use_pg:
            async with self._pool.acquire() as conn:
                await conn.executemany(query, args_list)
        else:
            sqlite_query = self._pg_to_sqlite(query)
            for args in args_list:
                self._fallback_conn.execute(sqlite_query, *args)


class SQLiteFallback:
    """SQLite in-memory fallback cho development.

    Luu y: Khong dung cho production.
    """

    def __init__(self):
        import sqlite3
        self._conn = sqlite3.connect(":memory:", check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()
        logger.info("SQLite fallback initialized (in-memory)")

    def _init_schema(self):
        """Tao bang co ban."""
        schema = """
        CREATE TABLE IF NOT EXISTS appointments (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            doctor_id TEXT,
            department_id TEXT,
            slot_id TEXT,
            schedule_id TEXT,
            patient_name TEXT,
            patient_phone TEXT,
            patient_email TEXT,
            status TEXT DEFAULT 'pending',
            symptoms TEXT,
            notes TEXT,
            is_bhyt INTEGER DEFAULT 0,
            idempotency_key TEXT UNIQUE,
            source TEXT DEFAULT 'ai_chat',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_appointments_user
            ON appointments(user_id);
        CREATE INDEX IF NOT EXISTS idx_appointments_status
            ON appointments(status);
        CREATE INDEX IF NOT EXISTS idx_appointments_idempotency
            ON appointments(idempotency_key);
        CREATE TABLE IF NOT EXISTS time_slots (
            id TEXT PRIMARY KEY,
            schedule_id TEXT,
            doctor_id TEXT,
            start_time TEXT,
            end_time TEXT,
            is_booked INTEGER DEFAULT 0,
            booked_by TEXT,
            booking_id TEXT,
            version INTEGER DEFAULT 1
        );
        CREATE INDEX IF NOT EXISTS idx_slots_schedule
            ON time_slots(schedule_id);
        CREATE INDEX IF NOT EXISTS idx_slots_doctor_date
            ON time_slots(doctor_id, start_time);
        CREATE TABLE IF NOT EXISTS notification_queue (
            id TEXT PRIMARY KEY,
            appointment_id TEXT,
            channel TEXT,
            recipient TEXT,
            template TEXT,
            params TEXT,
            status TEXT DEFAULT 'pending',
            retry_count INTEGER DEFAULT 0,
            max_retries INTEGER DEFAULT 3,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS audit_events (
            id TEXT PRIMARY KEY,
            event_type TEXT,
            appointment_id TEXT,
            user_id TEXT,
            actor_role TEXT,
            details TEXT,
            ip_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_audit_type ON audit_events(event_type);
        """
        self._conn.executescript(schema)

    def execute(self, query: str, *args) -> str:
        cursor = self._conn.execute(query, args)
        self._conn.commit()
        return str(cursor.lastrowid) if cursor.lastrowid else ""

    def fetch(self, query: str, *args) -> list:
        cursor = self._conn.execute(query, args)
        return [dict(row) for row in cursor.fetchall()]

    def fetchrow(self, query: str, *args) -> Optional[dict]:
        cursor = self._conn.execute(query, args)
        row = cursor.fetchone()
        return dict(row) if row else None


# Singleton
database = Database()
