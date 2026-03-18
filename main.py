#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
GADIS V81 - MAIN ENTRY POINT (FIXED)
=============================================================================
"""

import asyncio
import sys
import traceback
import threading
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from utils.logger import setup_logging

logger = setup_logging("gadis_v81")

# ===== HEALTHCHECK SERVER =====
try:
    from flask import Flask, jsonify
    health_app = Flask(__name__)

    @health_app.route('/health')
    def health():
        return jsonify({"status": "ok"}), 200

    def run_health_server():
        port = int(os.getenv('PORT', 8080))
        health_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

    HEALTH_SERVER_AVAILABLE = True
except ImportError:
    logger.warning("Flask not installed, healthcheck disabled")
    HEALTH_SERVER_AVAILABLE = False
    def run_health_server():
        pass

# ===== BANNER with safe attribute access =====
print("="*70)
print("    GADIS V81 - ULTIMATE AI BOT")
print("    Premium Edition - All Features")
print("="*70)

# Database info
try:
    db_info = f"{settings.db.name} @ {settings.db.host}"
except AttributeError:
    db_info = "SQLite (gadis_v81.db)"
print(f"📊 Database: {db_info}")

# AI Model
try:
    ai_model = settings.ai.primary_model
except AttributeError:
    ai_model = "deepseek"
print(f"🤖 AI Model: {ai_model}")

# Admin ID
print(f"👑 Admin ID: {settings.admin_id}")

# Sexual features
try:
    sexual_enabled = "ENABLED" if settings.sexual.enabled else "DISABLED"
except AttributeError:
    sexual_enabled = "ENABLED"
print(f"🔞 Sexual Features: {sexual_enabled}")

# Public areas
try:
    max_positions = settings.sexual.max_positions
except AttributeError:
    max_positions = 50
print(f"🌍 Public Areas: {max_positions} positions")

# Bot initiative
try:
    bot_initiative = "ON" if settings.sexual.bot_initiative_enabled else "OFF"
except AttributeError:
    bot_initiative = "ON"
print(f"🎯 Bot Initiative: {bot_initiative}")

print("="*70)


async def init_components():
    logger.info("🚀 Starting GADIS V81...")

    # Database
    try:
        from database.connection import init_db
        await init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

    # Redis (mock)
    try:
        from cache.redis_client import init_redis
        await init_redis()
        logger.info("✅ Redis initialized")
    except ImportError:
        logger.warning("⚠️ Redis module not found, skipping...")
    except Exception as e:
        logger.error(f"❌ Redis initialization failed: {e}")

    # Bot application
    try:
        from bot.application import create_application
        app = create_application()
        logger.info("✅ Bot application created")
    except Exception as e:
        logger.error(f"❌ Bot application creation failed: {e}")
        raise

    # Webhook setup
    try:
        from bot.webhook import setup_webhook_sync
        mode = setup_webhook_sync(app)
        logger.info(f"✅ Webhook URL: {mode}")
    except ImportError:
        logger.warning("⚠️ Webhook module not found, continuing with polling")
    except Exception as e:
        logger.error(f"❌ Webhook setup failed: {e}")

    logger.info("🚀 GADIS V81 is ready!")
    return app


def main():
    if HEALTH_SERVER_AVAILABLE:
        threading.Thread(target=run_health_server, daemon=True).start()
        logger.info(f"✅ Healthcheck server started on port {os.getenv('PORT', 8080)}")

    try:
        app = asyncio.run(init_components())
        logger.info("📡 Starting bot in polling mode...")
        app.run_polling(
            allowed_updates=['message', 'callback_query'],
            drop_pending_updates=True
        )
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)
    finally:
        logger.info("👋 Goodbye!")


if __name__ == "__main__":
    main()
