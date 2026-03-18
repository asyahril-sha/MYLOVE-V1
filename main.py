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
import time
import os
import signal
from pathlib import Path

# Tambahkan path ke root project
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from utils.logger import setup_logging

# Setup logging
logger = setup_logging("gadis_v81")

# =============================================================================
# HEALTHCHECK SERVER
# =============================================================================
HEALTH_SERVER_AVAILABLE = False
health_server_started = False

try:
    from flask import Flask, jsonify

    health_app = Flask(__name__)

    @health_app.route('/health')
    def health():
        """Health check endpoint untuk Railway"""
        return jsonify({
            "status": "healthy",
            "timestamp": time.time(),
            "bot": "running",
            "server_started": health_server_started
        }), 200

    @health_app.route('/')
    def root():
        """Root endpoint - info bot"""
        return jsonify({
            "name": "GADIS V81",
            "version": "1.0.0",
            "status": "running",
            "admin_id": str(settings.admin_id)
        }), 200

    @health_app.route('/debug')
    def debug():
        """Debug endpoint"""
        return jsonify({
            "python_version": sys.version,
            "cwd": os.getcwd(),
            "port": os.getenv('PORT', '8080'),
            "health_server_started": health_server_started
        }), 200

    HEALTH_SERVER_AVAILABLE = True
    logger.info("✅ Flask imported successfully")

except ImportError as e:
    logger.warning(f"⚠️ Flask not installed: {e}")
    HEALTH_SERVER_AVAILABLE = False


def run_health_server():
    """Run Flask healthcheck server - standalone thread"""
    global health_server_started
    
    try:
        port = int(os.getenv('PORT', 8080))
        logger.info(f"🚀 Healthcheck server starting on port {port}")
        
        # Set flag bahwa server akan start
        health_server_started = True
        
        # Jalankan Flask (blocking)
        health_app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        logger.error(f"❌ Healthcheck server failed: {e}")
        health_server_started = False


# =============================================================================
# SIGNAL HANDLERS
# =============================================================================
def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {sig}, shutting down...")
    sys.exit(0)


# =============================================================================
# BANNER
# =============================================================================
def print_banner():
    """Print startup banner"""
    print("="*70)
    print("    GADIS V81 - ULTIMATE AI BOT")
    print("    Premium Edition - All Features")
    print("="*70)
    
    # Database info
    try:
        if hasattr(settings, 'db'):
            db_info = f"{settings.db.name} @ {settings.db.host}"
        else:
            db_info = "SQLite (gadis_v81.db)"
    except AttributeError:
        db_info = "SQLite (gadis_v81.db)"
    print(f"📊 Database: {db_info}")
    
    # AI Model
    try:
        if hasattr(settings, 'ai'):
            ai_model = getattr(settings.ai, 'primary_model', 'deepseek')
        else:
            ai_model = "deepseek"
    except AttributeError:
        ai_model = "deepseek"
    print(f"🤖 AI Model: {ai_model}")
    
    # Admin ID
    print(f"👑 Admin ID: {settings.admin_id}")
    
    # Sexual features
    try:
        if hasattr(settings, 'sexual'):
            sexual_enabled = "ENABLED" if getattr(settings.sexual, 'enabled', True) else "DISABLED"
        else:
            sexual_enabled = "ENABLED"
    except AttributeError:
        sexual_enabled = "ENABLED"
    print(f"🔞 Sexual Features: {sexual_enabled}")
    
    # Public areas
    try:
        if hasattr(settings, 'sexual'):
            max_positions = getattr(settings.sexual, 'max_positions', 50)
        else:
            max_positions = 50
    except AttributeError:
        max_positions = 50
    print(f"🌍 Public Areas: {max_positions} positions")
    
    # Bot initiative
    try:
        if hasattr(settings, 'sexual'):
            bot_initiative = "ON" if getattr(settings.sexual, 'bot_initiative_enabled', True) else "OFF"
        else:
            bot_initiative = "ON"
    except AttributeError:
        bot_initiative = "ON"
    print(f"🎯 Bot Initiative: {bot_initiative}")
    
    # Healthcheck status
    if HEALTH_SERVER_AVAILABLE:
        print(f"✅ Healthcheck: ENABLED on port {os.getenv('PORT', '8080')}")
    else:
        print(f"⚠️ Healthcheck: DISABLED (Flask not installed)")
    
    print("="*70)


# =============================================================================
# COMPONENT INITIALIZATION
# =============================================================================
async def init_components():
    """Initialize all components asynchronously"""
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
        raise

    # Redis (mock) - Opsional
    try:
        from cache.redis_client import init_redis
        await init_redis()
        logger.info("✅ Redis initialized")
    except ImportError:
        logger.info("ℹ️ Redis module not found - using mock mode")
    except Exception as e:
        logger.error(f"❌ Redis initialization failed: {e}")

    # Bot application
    try:
        from bot.application import create_application
        app = create_application()
        logger.info("✅ Bot application created")
    except ImportError as e:
        logger.error(f"❌ Bot application module error: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Bot application creation failed: {e}")
        raise

    # Webhook setup - Opsional, fallback ke polling
    try:
        from bot.webhook import setup_webhook_sync
        mode = setup_webhook_sync(app)
        logger.info(f"✅ Webhook setup: {mode}")
    except ImportError:
        logger.info("ℹ️ Webhook module not found - using polling mode")
    except Exception as e:
        logger.error(f"❌ Webhook setup failed (using polling): {e}")

    logger.info("🚀 GADIS V81 is ready!")
    return app


# =============================================================================
# MAIN FUNCTION
# =============================================================================
def main():
    """Main entry point"""
    
    # Print banner
    print_banner()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    health_thread = None
    
    # ===== START HEALTHCHECK SERVER =====
    if HEALTH_SERVER_AVAILABLE:
        # Start health server di thread terpisah
        health_thread = threading.Thread(target=run_health_server)
        health_thread.daemon = True  # Daemon thread akan mati saat main thread mati
        health_thread.start()
        
        port = os.getenv('PORT', '8080')
        logger.info(f"✅ Healthcheck server thread started on port {port}")
        
        # Beri waktu Flask untuk start (2 detik)
        logger.info("⏳ Waiting 2 seconds for healthcheck server to initialize...")
        time.sleep(2)
        logger.info("✅ Healthcheck server should be ready")
    else:
        logger.warning("⚠️ Healthcheck server disabled - Railway may fail deployment")
        logger.warning("   Install Flask with: pip install flask")

    try:
        # Initialize components
        app = asyncio.run(init_components())

        from bot.webhook import setup_webhook_with_fallback

        logger.info("🚀 Starting webhook mode...")
        asyncio.run(setup_webhook_with_fallback(app))

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
