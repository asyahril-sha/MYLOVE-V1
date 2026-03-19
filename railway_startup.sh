#!/bin/bash
# railway_startup.sh

echo "🔄 Menjalankan migrasi database..."
sqlite3 data/mylove.db < database/migrations/v2_migration.sql
echo "✅ Migrasi selesai"

# Jalankan bot
python main.py
