#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
CHECK DEPLOY - Verifikasi semua import sebelum deploy ke Railway
=============================================================================
"""

import sys
import traceback
from pathlib import Path

# Tambahkan path ke root project
sys.path.insert(0, str(Path(__file__).parent))

print("="*70)
print("🔍 CHECK DEPLOY - Verifikasi Import MYLOVE ULTIMATE")
print("="*70)


def check_import(module_name, import_name=None):
    """Cek apakah import berhasil"""
    try:
        if import_name:
            exec(f"from {module_name} import {import_name}")
            print(f"✅ from {module_name} import {import_name} OK")
        else:
            exec(f"import {module_name}")
            print(f"✅ import {module_name} OK")
        return True
    except Exception as e:
        print(f"❌ {module_name} error: {e}")
        traceback.print_exc()
        return False


def main():
    errors = []
    
    print("\n📦 1. CEK DEPENDENCIES EXTERNAL...")
    print("-" * 50)
    
    # Core dependencies
    check_import("telegram", "Update")
    check_import("telegram.ext", "Application")
    check_import("loguru", "logger")
    check_import("pydantic", "BaseModel")
    check_import("dotenv", "load_dotenv")
    check_import("flask", "Flask")
    check_import("aiosqlite")
    check_import("httpx")
    
    print("\n📁 2. CEK MODUL INTERNAL...")
    print("-" * 50)
    
    # Config
    if check_import("config", "settings"):
        try:
            from config import settings
            print(f"   • Admin ID: {settings.admin_id}")
            print(f"   • Telegram Token: {settings.telegram_token[:5]}...{settings.telegram_token[-5:]}")
            print(f"   • Log Dir: {settings.logging.log_dir}")
            print(f"   • Database Path: {settings.database.path}")
        except Exception as e:
            print(f"   ❌ Cannot access settings: {e}")
            errors.append("settings")
    
    # Utils
    check_import("utils.logger", "setup_logging")
    check_import("utils.logger", "logger")
    check_import("utils.exceptions", "GadisBaseException")
    
    # Database
    check_import("database.connection", "init_db")
    check_import("database.models", "Constants")
    check_import("database.models", "Relationship")
    
    # Cache
    check_import("cache.redis_client", "init_redis")
    
    # Bot
    check_import("bot.application", "create_application")
    check_import("bot.handlers", "start_command")
    check_import("bot.callbacks", "agree_18_callback")
    check_import("bot.commands", "help_command")
    check_import("bot.webhook", "setup_webhook_sync")
    
    print("\n📊 3. CEK FUNGSI UTAMA...")
    print("-" * 50)
    
    # Coba import main functions
    try:
        from main import init_components, main
        print("✅ main.py functions OK")
    except Exception as e:
        print(f"❌ main.py error: {e}")
        traceback.print_exc()
        errors.append("main")
    
    # Kesimpulan
    print("\n" + "="*70)
    if errors:
        print(f"❌ GAGAL: {len(errors)} error ditemukan")
        for err in errors:
            print(f"   - {err}")
        print("\n⚠️  Perbaiki error di atas sebelum deploy ke Railway!")
        return 1
    else:
        print("✅ SUKSES: Semua import berfungsi dengan baik!")
        print("🚀 Siap deploy ke Railway!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
