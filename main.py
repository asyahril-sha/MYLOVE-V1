#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
GADIS V81 - MAIN ENTRY POINT (FULL FIX)
=============================================================================
Native python-telegram-bot v20+ dengan polling mode + healthcheck server
"""

import asyncio
import sys
import traceback
import threading
import os
from pathlib import Path

# Tambahkan path ke root project
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from utils.logger import setup_logging

# Setup logging
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

# ===== BANNER =====
print("="*70)
print("    GADIS V81 - ULTIMATE AI BOT")
print("    Premium Edition - All Features")
print("="*70)
print(f"📊 Database: {settings.db.name} @ {settings.db.host}")
print(f"🤖 AI Model: {settings.ai.primary_model}")
print(f"👑 Admin ID: {settings.admin_id}")
print(f"🔞 Sexual Features: {'ENABLED' if settings.sexual.enabled else 'DISABLED'}")
print(f"🌍 Public Areas: {settings.sexual.max_positions} positions")
print(f"🎯 Bot Initiative: {'ON' if settings.sexual.bot_initiative_enabled else 'OFF'}")
print("="*70)


# ===== INISIALISASI ASYNC =====
async def init_components():
    """Inisialisasi semua komponen (database, redis, bot app)"""
    logger.info("🚀 Starting GADIS V81...")

    # Database
    try:
        from database.connection import init_db
        await init_db()
        logger.info("✅ Database initialized")
    except ImportError as e:
        logger.error(f"❌ Database module error: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        traceback.print_exc()
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
        # non-critical

    # Bot application (synchronous)
    try:
        from bot.application import create_application
        app = create_application()
        logger.info("✅ Bot application created")
    except ImportError as e:
        logger.error(f"❌ Bot application module error: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Bot application creation failed: {e}")
        traceback.print_exc()
        raise

    # Setup webhook (sync wrapper)
    try:
        from bot.webhook import setup_webhook_sync
        mode = setup_webhook_sync(app)
        logger.info(f"✅ Webhook URL: {mode}")
    except ImportError:
        logger.warning("⚠️ Webhook module not found, continuing with polling")
    except Exception as e:
        logger.error(f"❌ Webhook setup failed: {e}")
        # continue with polling anyway

    logger.info("🚀 GADIS V81 is ready!")
    return app


# ===== MAIN FUNCTION =====
def main():
    """Main entry point – fully synchronous after init"""
    # Start healthcheck server di thread terpisah
    if HEALTH_SERVER_AVAILABLE:
        threading.Thread(target=run_health_server, daemon=True).start()
        logger.info(f"✅ Healthcheck server started on port {os.getenv('PORT', 8080)}")

    try:
        # Inisialisasi async components
        app = asyncio.run(init_components())

        logger.info("📡 Starting bot in polling mode...")

        # Jalankan polling (blocking, synchronous)
        app.run_polling(
            allowed_updates=['message', 'callback_query'],
            drop_pending_updates=True  # Hindari konflik instance
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
