#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AUTO MIGRATE - JALANKAN CUKUP 1X, DIAMIN JALAN SENDIRI
Cukup upload ke GitHub, Railway akan jalanin otomatis
"""

import sqlite3
import os
from pathlib import Path

def migrate():
    """Migrasi database - Panggil sekali, langsung beres"""
    
    db_path = Path("data/mylove.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Cek apakah sudah pernah migrasi
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS migration_log (
            version TEXT PRIMARY KEY,
            migrated_at REAL NOT NULL
        )
    """)
    
    cursor.execute("SELECT version FROM migration_log WHERE version = 'v2'")
    if cursor.fetchone():
        print("✅ Database sudah V2, tidak perlu migrasi")
        conn.close()
        return True
    
    print("🔄 Migrasi ke V2...")
    
    # ===== 1. TABEL PDKT SESSIONS =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pdkt_sessions (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            bot_name TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            direction TEXT NOT NULL,
            chemistry_score REAL DEFAULT 50.0,
            chemistry_level TEXT DEFAULT 'biasa',
            mood TEXT DEFAULT 'calm',
            level INTEGER DEFAULT 1,
            total_duration REAL DEFAULT 0.0,
            total_chats INTEGER DEFAULT 0,
            total_intim INTEGER DEFAULT 0,
            total_climax INTEGER DEFAULT 0,
            created_at REAL NOT NULL,
            last_interaction REAL NOT NULL,
            paused_at REAL,
            ended_at REAL,
            end_reason TEXT,
            inner_thoughts TEXT,
            milestones TEXT,
            metadata TEXT
        )
    """)
    
    # ===== 2. TABEL PDKT INNER THOUGHTS =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pdkt_inner_thoughts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pdkt_id TEXT NOT NULL,
            thought TEXT NOT NULL,
            context TEXT,
            timestamp REAL NOT NULL
        )
    """)
    
    # ===== 3. TABEL MANTAN =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mantan (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            pdkt_id TEXT NOT NULL,
            bot_name TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT DEFAULT 'putus',
            putus_time REAL NOT NULL,
            putus_reason TEXT NOT NULL,
            chemistry_history TEXT,
            milestones TEXT,
            total_chats INTEGER DEFAULT 0,
            total_intim INTEGER DEFAULT 0,
            total_climax INTEGER DEFAULT 0,
            first_kiss_time REAL,
            first_intim_time REAL,
            become_pacar_time REAL,
            last_chat_time REAL NOT NULL,
            fwb_requests TEXT,
            fwb_start_time REAL,
            fwb_end_time REAL
        )
    """)
    
    # ===== 4. TABEL FWB REQUESTS =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fwb_requests (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            mantan_id TEXT NOT NULL,
            bot_name TEXT NOT NULL,
            user_message TEXT,
            timestamp REAL NOT NULL,
            status TEXT NOT NULL,
            bot_decision TEXT,
            expiry_time REAL NOT NULL
        )
    """)
    
    # ===== 5. TABEL FWB RELATIONS =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fwb_relations (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            mantan_id TEXT NOT NULL,
            bot_name TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            created_at REAL NOT NULL,
            last_interaction REAL NOT NULL,
            chemistry_score REAL DEFAULT 50.0,
            climax_count INTEGER DEFAULT 0,
            intim_count INTEGER DEFAULT 0,
            total_chats INTEGER DEFAULT 0,
            pause_history TEXT,
            ended_at REAL,
            end_reason TEXT
        )
    """)
    
    # ===== 6. TABEL HTS RELATIONS =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hts_relations (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            bot_name TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            created_at REAL NOT NULL,
            expiry_time REAL NOT NULL,
            last_interaction REAL NOT NULL,
            chemistry_score REAL DEFAULT 50.0,
            climax_count INTEGER DEFAULT 0,
            intimacy_level INTEGER DEFAULT 7,
            total_chats INTEGER DEFAULT 0,
            total_intim INTEGER DEFAULT 0,
            history TEXT
        )
    """)
    
    # ===== 7. TABEL MEMORIES V2 =====
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories_v2 (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            session_id TEXT,
            content TEXT NOT NULL,
            memory_type TEXT NOT NULL,
            importance REAL DEFAULT 0.5,
            emotional_tag TEXT,
            timestamp REAL NOT NULL,
            access_count INTEGER DEFAULT 0,
            last_access REAL NOT NULL,
            context TEXT,
            metadata TEXT
        )
    """)
    
    # ===== INDEXES =====
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pdkt_sessions_user ON pdkt_sessions(user_id, status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inner_thoughts_pdkt ON pdkt_inner_thoughts(pdkt_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_mantan_user ON mantan(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fwb_user ON fwb_relations(user_id, status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hts_user ON hts_relations(user_id, status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hts_expiry ON hts_relations(expiry_time)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_v2_user ON memories_v2(user_id)")
    
    # ===== LOG MIGRASI =====
    import time
    cursor.execute(
        "INSERT INTO migration_log (version, migrated_at) VALUES (?, ?)",
        ('v2', time.time())
    )
    
    conn.commit()
    conn.close()
    
    print("✅ Migrasi V2 selesai!")
    return True

if __name__ == "__main__":
    migrate()
