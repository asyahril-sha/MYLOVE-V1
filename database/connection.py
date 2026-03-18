#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - DATABASE CONNECTION (ENHANCED)
=============================================================================
- Koneksi SQLite untuk single user
- Connection pooling
- Async support dengan aiosqlite
- **TAMBAHAN: Auto migration untuk kolom bot_name**
=============================================================================
"""

import os
import time
import json
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

import aiosqlite

from config import settings

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Manajemen koneksi database SQLite
    Support async operations dengan connection pooling
    """
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.pool_size = settings.database.pool_size
        self.timeout = settings.database.timeout
        self._connection = None
        self._pool = []
        self._initialized = False
        
    async def initialize(self):
        """Initialize database and create tables"""
        try:
            # Buat directory jika belum ada
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Koneksi pertama untuk setup
            self._connection = await aiosqlite.connect(
                self.db_path,
                timeout=self.timeout
            )
            
            # Enable foreign keys
            await self._connection.execute("PRAGMA foreign_keys = ON")
            
            # Optimize SQLite for performance
            await self._connection.execute("PRAGMA journal_mode = WAL")
            await self._connection.execute("PRAGMA synchronous = NORMAL")
            await self._connection.execute("PRAGMA cache_size = 10000")
            await self._connection.execute("PRAGMA temp_store = MEMORY")
            
            # Buat tables
            await self._create_tables()
            
            # ===== TAMBAHAN MYLOVE V2 =====
            # Jalankan migrasi untuk menambah kolom baru
            await self._run_migrations()
            # ===== END TAMBAHAN =====
            
            self._initialized = True
            logger.info(f"✅ Database initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    # ===== TAMBAHAN MYLOVE V2 =====
    async def _run_migrations(self):
        """Jalankan migrasi database untuk versi 2"""
        logger.info("🔄 Running database migrations...")
        
        # Cek dan tambah kolom bot_name ke tabel sessions
        await self._add_column_if_not_exists('sessions', 'bot_name', 'TEXT DEFAULT "Aurora"')
        
        # Cek dan tambah kolom bot_name ke tabel relationships
        await self._add_column_if_not_exists('relationships', 'bot_name', 'TEXT DEFAULT "Aurora"')
        
        # Cek dan tambah kolom bot_name ke tabel threesome_participants (jika ada)
        await self._add_column_if_not_exists('threesome_participants', 'bot_name', 'TEXT DEFAULT "Aurora"')
        
        logger.info("✅ Database migrations completed")
    
    async def _add_column_if_not_exists(self, table: str, column: str, definition: str):
        """
        Tambah kolom ke tabel jika belum ada
        """
        try:
            # Cek apakah kolom sudah ada
            cursor = await self._connection.execute(f"PRAGMA table_info({table})")
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if column not in column_names:
                # Tambah kolom baru
                await self._connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
                await self._connection.commit()
                logger.info(f"  ✅ Added column '{column}' to table '{table}'")
            else:
                logger.debug(f"  ⏩ Column '{column}' already exists in '{table}'")
                
        except Exception as e:
            logger.warning(f"  ⚠️ Could not add column '{column}' to '{table}': {e}")
    # ===== END TAMBAHAN =====
    
    async def _create_tables(self):
        """Create all database tables"""
        
        # ===== USERS TABLE =====
        await self._connection.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at REAL NOT NULL,
                last_active REAL NOT NULL,
                total_interactions INTEGER DEFAULT 0,
                preferences TEXT,  -- JSON
                settings TEXT       -- JSON
            )
        ''')
        
        # ===== SESSIONS TABLE =====
        await self._connection.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,  -- MYLOVE-NAMA_BOT-ROLE-USER-DATE-SEQ
                user_id INTEGER NOT NULL,
                bot_name TEXT DEFAULT 'Aurora',  -- Nama bot (tambah di V2)
                role TEXT NOT NULL,
                status TEXT DEFAULT 'active',  -- active, closed, expired
                start_time REAL NOT NULL,
                end_time REAL,
                last_message_time REAL NOT NULL,
                total_messages INTEGER DEFAULT 0,
                intimacy_level INTEGER DEFAULT 1,
                location TEXT,
                summary TEXT,
                metadata TEXT,  -- JSON for additional data
                FOREIGN KEY (user_id) REFERENCES users (telegram_id)
            )
        ''')
        
        # ===== CONVERSATIONS TABLE =====
        await self._connection.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp REAL NOT NULL,
                user_message TEXT,
                bot_response TEXT,
                intent TEXT,
                mood TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        ''')
        
        # ===== MEMORIES TABLE =====
        await self._connection.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT,
                memory_type TEXT,  -- episodic, semantic, relationship
                content TEXT NOT NULL,
                importance REAL DEFAULT 0.5,
                emotional_tag TEXT,
                timestamp REAL NOT NULL,
                metadata TEXT,  -- JSON
                FOREIGN KEY (user_id) REFERENCES users (telegram_id)
            )
        ''')
        
        # ===== RELATIONSHIPS TABLE =====
        await self._connection.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                bot_name TEXT DEFAULT 'Aurora',  -- Nama bot (tambah di V2)
                role TEXT NOT NULL,
                instance_id TEXT,  -- Untuk multiple FWB
                status TEXT DEFAULT 'hts',  -- hts, fwb, pacar, putus
                intimacy_level INTEGER DEFAULT 1,
                total_interactions INTEGER DEFAULT 0,
                total_intim_sessions INTEGER DEFAULT 0,
                total_climax INTEGER DEFAULT 0,
                created_at REAL NOT NULL,
                last_interaction REAL NOT NULL,
                preferences TEXT,  -- JSON
                milestones TEXT,   -- JSON array
                history TEXT,      -- JSON array
                UNIQUE(user_id, role, instance_id)
            )
        ''')
        
        # ===== THREESOME PARTICIPANTS TABLE =====
        await self._connection.execute('''
            CREATE TABLE IF NOT EXISTS threesome_participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                threesome_session_id TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                bot_name TEXT DEFAULT 'Aurora',  -- Nama bot (tambah di V2)
                role TEXT NOT NULL,
                instance_id TEXT,
                participant_type TEXT NOT NULL,
                name TEXT NOT NULL,
                intimacy_level INTEGER DEFAULT 1,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (threesome_session_id) REFERENCES threesome_sessions (id)
            )
        ''')
        
        # ===== PREFERENCES TABLE =====
        await self._connection.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT,
                pref_type TEXT NOT NULL,  -- position, area, activity, location
                item TEXT NOT NULL,
                score REAL DEFAULT 0.5,
                count INTEGER DEFAULT 1,
                last_updated REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (telegram_id)
            )
        ''')
        
        # ===== MILESTONES TABLE =====
        await self._connection.execute('''
            CREATE TABLE IF NOT EXISTS milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT,
                milestone_type TEXT NOT NULL,
                description TEXT,
                timestamp REAL NOT NULL,
                intimacy_level INTEGER,
                metadata TEXT,
                FOREIGN KEY (user_id) REFERENCES users (telegram_id)
            )
        ''')
        
        # ===== BACKUPS TABLE =====
        await self._connection.execute('''
            CREATE TABLE IF NOT EXISTS backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                size INTEGER,
                created_at REAL NOT NULL,
                type TEXT DEFAULT 'auto',  -- auto, manual
                status TEXT DEFAULT 'completed',
                metadata TEXT
            )
        ''')
        
        # ===== THREESOME SESSIONS TABLE =====
        await self._connection.execute('''
            CREATE TABLE IF NOT EXISTS threesome_sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                created_at REAL NOT NULL,
                started_at REAL,
                completed_at REAL,
                last_activity REAL NOT NULL,
                total_messages INTEGER DEFAULT 0,
                climax_count INTEGER DEFAULT 0,
                aftercare_needed INTEGER DEFAULT 0,
                current_focus INTEGER,
                last_pattern TEXT,
                participants TEXT,
                interactions TEXT,
                FOREIGN KEY (user_id) REFERENCES users (telegram_id)
            )
        ''')
        
        # ===== CREATE INDEXES =====
        await self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id, status)"
        )
        await self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_sessions_time ON sessions(last_message_time)"
        )
        await self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_memories_user ON memories(user_id, role)"
        )
        await self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_relationships_user ON relationships(user_id, status)"
        )
        await self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_preferences_user ON preferences(user_id, pref_type)"
        )
        await self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_milestones_user ON milestones(user_id, timestamp)"
        )
        
        await self._connection.commit()
        logger.info("✅ Database tables created/indexed")
        
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool"""
        if not self._initialized:
            await self.initialize()
            
        conn = None
        try:
            conn = await aiosqlite.connect(
                self.db_path,
                timeout=self.timeout
            )
            await conn.execute("PRAGMA foreign_keys = ON")
            yield conn
        finally:
            if conn:
                await conn.close()
                
    async def execute(self, query: str, params: tuple = ()) -> aiosqlite.Cursor:
        """Execute query and return cursor"""
        async with self.get_connection() as conn:
            cursor = await conn.execute(query, params)
            await conn.commit()
            return cursor
            
    async def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Fetch one row as dict"""
        async with self.get_connection() as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(query, params)
            row = await cursor.fetchone()
            return dict(row) if row else None
            
    async def fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
        """Fetch all rows as list of dicts"""
        async with self.get_connection() as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(query, params)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
            
    async def execute_many(self, query: str, params_list: List[tuple]):
        """Execute many inserts/updates"""
        async with self.get_connection() as conn:
            await conn.executemany(query, params_list)
            await conn.commit()
            
    async def vacuum(self):
        """Vacuum database (optimize)"""
        async with self.get_connection() as conn:
            await conn.execute("VACUUM")
            logger.info("✅ Database vacuum completed")
            
    async def backup(self, backup_path: Path) -> bool:
        """Backup database to file"""
        try:
            async with self.get_connection() as conn:
                await conn.backup(aiosqlite.connect(backup_path))
            logger.info(f"✅ Database backed up to {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False
            
    async def get_stats(self) -> Dict:
        """Get database statistics"""
        stats = {}
        
        # Table sizes
        tables = [
            'users', 'sessions', 'conversations', 'memories',
            'relationships', 'preferences', 'milestones', 'backups',
            'threesome_sessions', 'threesome_participants'
        ]
        
        for table in tables:
            try:
                result = await self.fetch_one(f"SELECT COUNT(*) as count FROM {table}")
                stats[f"{table}_count"] = result['count'] if result else 0
            except:
                stats[f"{table}_count"] = 0
                
        # Database file size
        if self.db_path.exists():
            stats['db_size_mb'] = round(self.db_path.stat().st_size / (1024 * 1024), 2)
        else:
            stats['db_size_mb'] = 0
            
        return stats
        
    async def close(self):
        """Close database connection"""
        if self._connection:
            await self._connection.close()
            self._initialized = False
            logger.info("Database connection closed")


# =============================================================================
# GLOBAL DATABASE INSTANCE
# =============================================================================

_db_instance: Optional[DatabaseConnection] = None


async def get_db() -> DatabaseConnection:
    """Get global database instance"""
    global _db_instance
    if _db_instance is None:
        db_path = settings.database.path
        _db_instance = DatabaseConnection(db_path)
        await _db_instance.initialize()
    return _db_instance


async def init_db():
    """Initialize database (for startup)"""
    db = await get_db()
    return db


__all__ = ['DatabaseConnection', 'get_db', 'init_db']
