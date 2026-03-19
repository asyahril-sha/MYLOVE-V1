#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script untuk menjalankan migrasi database V2
"""

import aiosqlite
import asyncio
import os
from pathlib import Path

async def run_migration():
    # Lokasi database
    db_path = Path("data/mylove.db")
    
    # Pastikan folder data ada
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Baca file SQL
    sql_file = Path("database/migrations/v2_migration.sql")
    if not sql_file.exists():
        print(f"❌ File migrasi tidak ditemukan: {sql_file}")
        return
    
    with open(sql_file, 'r') as f:
        sql = f.read()
    
    # Jalankan migrasi
    print(f"🔄 Menjalankan migrasi dari {sql_file}...")
    
    async with aiosqlite.connect(db_path) as db:
        # Jalankan semua perintah SQL
        await db.executescript(sql)
        await db.commit()
    
    print("✅ Migrasi selesai!")
    
    # Verifikasi
    async with aiosqlite.connect(db_path) as db:
        # Cek tabel baru
        tables = await db.execute_fetchall(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        
        print("\n📋 Daftar tabel setelah migrasi:")
        for table in tables:
            print(f"  • {table[0]}")

if __name__ == "__main__":
    asyncio.run(run_migration())
