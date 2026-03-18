#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
GADIS V81 - MAIN ENTRY POINT (SINGLE FLASK SERVER)
=============================================================================
Satu Flask server untuk healthcheck DAN webhook
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
logger = setup_logging("MYLOVE-V1")

# =============================================================================
# GLOBAL VARIABLES
# =============================================================================
_bot_app = None  # Untuk menyimpan bot application

# =============================================================================
# FLASK SERVER (untuk healthcheck DAN webhook)
# =============================================================================
HEALTH_SERVER_AVAILABLE = False
health_server_started = False

try:
    from flask import Flask, jsonify, request
    from telegram import Update

    app_flask = Flask(__name__)

    @app_flask.route('/health')
    def health():
        """Health check endpoint untuk Railway"""
        return jsonify({
            "status": "healthy",
            "timestamp": time.time(),
            "bot": "running",
            "server_started": health_server_started,
            "bot_ready": _bot_app is not None
        }), 200

    @app_flask.route('/')
    def root():
        """Root endpoint - info bot"""
        return jsonify({
            "name": "GADIS V81",
            "version": "1.0.0",
            "status": "running",
            "admin_id": str(settings.admin_id)
        }), 200

    @app_flask.route('/debug')
    def debug():
        """Debug endpoint"""
        return jsonify({
            "python_version": sys.version,
            "cwd": os.getcwd(),
            "port": os.getenv('PORT', '8080'),
            "health_server_started": health_server_started,
            "bot_ready": _bot_app is not None
        }), 200

    # ===== WEBHOOK ENDPOINT =====
    @app_flask.route('/webhook', methods=['POST'])
    def webhook():
        """Webhook endpoint untuk Telegram"""
        global _bot_app
        
        if not _bot_app:
            logger.error("Bot not ready")
            return jsonify({"error": "Bot not ready"}), 503
        
        try:
            # Parse update dari Telegram
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data"}), 400
            
            update = Update.de_json(data, _bot_app.bot)
            
            # Process update di background
            asyncio.run(_bot_app.process_update(update))
            
            logger.debug(f"Processed update: {update.update_id}")
            return "OK", 200
            
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return jsonify({"error": str(e)}), 500

    HEALTH_SERVER_AVAILABLE = True
    logger.info("✅ Flask server ready (healthcheck + webhook)")

except ImportError as e:
    logger.warning(f"⚠️ Flask not installed: {e}")
    HEALTH_SERVER_AVAILABLE = False


def run_flask_server():
    """Run Flask server - standalone thread"""
    global health_server_started
    
    try:
        port = int(os.getenv('PORT', 8080))
        logger.info(f"🚀 Flask server starting on port {port}")
        
        # Set flag bahwa server akan start
        health_server_started = True
        
        # Jalankan Flask (blocking)
        app_flask.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        logger.error(f"❌ Flask server failed: {e}")
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
    
    # Server status
    if HEALTH_SERVER_AVAILABLE:
        print(f"✅ Flask server: ENABLED on port {os.getenv('PORT', '8080')}")
        print(f"   • Healthcheck: /health")
        print(f"   • Webhook: /webhook")
    else:
        print(f"⚠️ Flask server: DISABLED (Flask not installed)")
    
    print("="*70)


# =============================================================================
# COMPONENT INITIALIZATION
# =============================================================================
async def init_components():
    """Initialize all components asynchronously"""
    global _bot_app
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
        _bot_app = create_application()
        logger.info("✅ Bot application created")
    except ImportError as e:
        logger.error(f"❌ Bot application module error: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Bot application creation failed: {e}")
        raise

    logger.info("🚀 GADIS V81 is ready!")
    return _bot_app


# =============================================================================
# SETUP WEBHOOK
# =============================================================================
async def setup_webhook(app):
    """Setup webhook untuk bot"""
    try:
        # Dapatkan webhook URL
        railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN')
        if railway_url:
            webhook_url = f"https://{railway_url}/webhook"
        else:
            webhook_url = os.getenv('WEBHOOK_URL')
            if not webhook_url:
                webhook_url = f"http://localhost:{os.getenv('PORT', 8080)}/webhook"
                logger.warning(f"No public domain, using local URL: {webhook_url}")
        
        logger.info(f"🔗 Setting webhook to: {webhook_url}")
        
        # Set webhook
        await app.bot.set_webhook(
            url=webhook_url,
            allowed_updates=['message', 'callback_query'],
            drop_pending_updates=True,
            max_connections=40,
            timeout=30
        )
        
        # Verify
        webhook_info = await app.bot.get_webhook_info()
        if webhook_info.url == webhook_url:
            logger.info(f"✅ Webhook set successfully: {webhook_info.url}")
            logger.info(f"   Pending updates: {webhook_info.pending_update_count}")
            return True
        else:
            logger.error(f"Webhook verification failed: {webhook_info.url}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Webhook setup failed: {e}")
        return False


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
    
    # ===== START FLASK SERVER (di thread) =====
    if HEALTH_SERVER_AVAILABLE:
        flask_thread = threading.Thread(target=run_flask_server)
        flask_thread.daemon = True
        flask_thread.start()
        
        port = os.getenv('PORT', '8080')
        logger.info(f"✅ Flask server thread started on port {port}")
        
        # Beri waktu Flask untuk start (2 detik)
        logger.info("⏳ Waiting 2 seconds for Flask server to initialize...")
        time.sleep(2)
        logger.info("✅ Flask server should be ready")
    else:
        logger.warning("⚠️ Flask server disabled - Railway may fail deployment")
        logger.warning("   Install Flask with: pip install flask")

    try:
        # Initialize components
        app = asyncio.run(init_components())

        # Setup webhook
        logger.info("🚀 Setting up webhook...")
        webhook_success = asyncio.run(setup_webhook(app))
        
        if webhook_success:
            logger.info("✅ Webhook mode activated!")
            logger.info(f"📡 Bot will receive updates at /webhook")
        else:
            logger.warning("⚠️ Webhook failed - check your configuration")

        # Keep main thread alive
        logger.info("✅ Bot is running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)

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
