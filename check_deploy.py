#!/usr/bin/env python
# check_deploy.py
import sys
import os
from pathlib import Path

def check_imports():
    """Cek semua import penting"""
    try:
        from flask import Flask
        print("✅ Flask terinstal")
    except ImportError:
        print("❌ Flask tidak terinstal")
        return False
    
    try:
        from config import settings
        print("✅ Config OK")
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False
    
    try:
        from database.connection import init_db
        print("✅ Database connection OK")
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    
    try:
        from bot.application import create_application
        print("✅ Bot application OK")
    except Exception as e:
        print(f"❌ Bot error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    if check_imports():
        print("✅ Semua import OK, siap deploy")
        sys.exit(0)
    else:
        print("❌ Ada error, perbaiki sebelum deploy")
        sys.exit(1)
