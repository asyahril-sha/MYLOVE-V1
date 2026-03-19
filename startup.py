#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Startup script untuk Railway
Menjalankan migrasi database sebelum bot start
"""

import subprocess
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Jalankan migrasi database menggunakan subprocess"""
    logger.info("🔄 Menjalankan migrasi database...")
    
    db_path = Path("data/mylove.db")
    sql_path = Path("database/migrations/v2_migration.sql")
    
    # Pastikan folder data ada
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not sql_path.exists():
        logger.error(f"❌ File migrasi tidak ditemukan: {sql_path}")
        return False
    
    try:
        # Jalankan perintah sqlite3
        cmd = f"sqlite3 {db_path} < {sql_path}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ Migrasi database selesai")
            
            # Verifikasi dengan listing tables
            verify = subprocess.run(
                f"sqlite3 {db_path} \"SELECT name FROM sqlite_master WHERE type='table';\"",
                shell=True, capture_output=True, text=True
            )
            if verify.stdout:
                tables = verify.stdout.strip().split('\n')
                logger.info(f"📋 Tabel tersedia: {len(tables)} tables")
            
            return True
        else:
            logger.error(f"❌ Migrasi gagal: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

def main():
    """Main function"""
    # Jalankan migrasi
    success = run_migration()
    
    if not success:
        logger.warning("⚠️ Migrasi gagal, tetapi akan mencoba menjalankan bot")
    
    # Jalankan bot
    logger.info("🚀 Menjalankan bot...")
    import main
    main.main()

if __name__ == "__main__":
    main()
