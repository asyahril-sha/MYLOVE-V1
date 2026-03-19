#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE-V1 - MAIN ENTRY POINT (AIOHTTP VERSION)
=============================================================================
Menggunakan aiohttp untuk webhook server - STABIL untuk Railway
"""

import os
import sys
import asyncio
import logging
import signal
from datetime import datetime
from pathlib import Path

from aiohttp import web
from telegram import Update
from telegram.ext import Application, ContextTypes
from telegram.request import HTTPXRequest

# ===== AUTO MIGRATION (PAKE PYTHON) =====
import os
if os.path.exists("database/auto_migrate.py"):
    print("🔄 Menjalankan auto migration...")
    import database.auto_migrate
    database.auto_migrate.migrate()
# =====

# Tambahkan path ke root project
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from utils.logger import setup_logging

# Setup logging
logger = setup_logging("MYLOVE-V1")


class MYLOVEBot:
    """Main bot class dengan aiohttp server"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.application = None
        self.is_ready = False
        self._shutdown_flag = False
        
        logger.info("📦 MYLOVE-V1 Initializing...")
        
    async def init_components(self):
        """Initialize all components asynchronously"""
        logger.info("🚀 Starting MYLOVE-v1...")

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
            self.application = create_application()
            
            # Initialize bot
            await self.application.initialize()
            logger.info("✅ Bot application created and initialized")
        except ImportError as e:
            logger.error(f"❌ Bot application module error: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Bot application creation failed: {e}")
            raise

        # Register error handler
        self.application.add_error_handler(self.error_handler)
        
        logger.info("🚀 MYLOVE-v1 is ready!")
        return self.application

    async def error_handler(self, update, context: ContextTypes.DEFAULT_TYPE):
        """Global error handler"""
        logger.error(f"❌ Error: {context.error}", exc_info=True)
        try:
            if update and update.effective_message:
                await update.effective_message.reply_text(
                    "❌ Terjadi error internal. Silakan coba lagi."
                )
        except:
            pass

    async def setup_webhook(self):
        """Setup webhook untuk Telegram"""
        try:
            # Dapatkan webhook URL
            railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
            if not railway_url:
                logger.error("❌ RAILWAY_PUBLIC_DOMAIN not set")
                return False
            
            webhook_url = f"https://{railway_url}/webhook"
            logger.info(f"🔗 Setting webhook to: {webhook_url}")

            # Delete old webhook first
            await self.application.bot.delete_webhook(drop_pending_updates=True)
            logger.info("✅ Old webhook deleted")

            # Set new webhook
            result = await self.application.bot.set_webhook(
                url=webhook_url,
                allowed_updates=['message', 'callback_query'],
                drop_pending_updates=True,
                max_connections=40
            )
            logger.info(f"✅ Webhook set result: {result}")

            # Verify
            webhook_info = await self.application.bot.get_webhook_info()
            if webhook_info.url == webhook_url:
                logger.info(f"✅ Webhook verified: {webhook_info.url}")
                logger.info(f"   Pending updates: {webhook_info.pending_update_count}")
                return True
            else:
                logger.error(f"Webhook verification failed: {webhook_info.url}")
                return False

        except Exception as e:
            logger.error(f"❌ Webhook setup failed: {e}")
            return False

    async def webhook_handler(self, request):
        """AIOHTTP webhook handler"""
        if not self.application:
            logger.error("Bot not ready")
            return web.Response(status=503, text='Bot not ready')

        try:
            # Parse update dari Telegram
            update_data = await request.json()
            if not update_data:
                return web.Response(status=400, text='No data')

            # Convert ke Update object
            update = Update.de_json(update_data, self.application.bot)
            
            # Process update di background
            asyncio.create_task(self.application.process_update(update))
            
            logger.debug(f"✅ Processed update: {update.update_id}")
            return web.Response(text='OK')

        except Exception as e:
            logger.error(f"❌ Webhook error: {e}")
            return web.Response(status=500, text=str(e))

    async def health_handler(self, request):
        """Health check endpoint untuk Railway"""
        return web.json_response({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "bot": "running",
            "bot_ready": self.application is not None,
            "uptime": str(datetime.now() - self.start_time)
        })

    async def root_handler(self, request):
        """Root endpoint - info bot"""
        return web.json_response({
            "name": "MYLOV-V1",
            "version": "1.0.0",
            "status": "running",
            "admin_id": str(settings.admin_id),
            "uptime": str(datetime.now() - self.start_time)
        })

    async def debug_handler(self, request):
        """Debug endpoint"""
        import sys
        return web.json_response({
            "python_version": sys.version,
            "cwd": os.getcwd(),
            "port": os.getenv('PORT', '8080'),
            "bot_ready": self.application is not None,
            "uptime": str(datetime.now() - self.start_time)
        })

    async def start(self):
        """Start bot and aiohttp server"""
        try:
            # Print banner
            self.print_banner()
            
            # Initialize components
            await self.init_components()

            # Setup webhook
            webhook_success = await self.setup_webhook()
            
            if webhook_success:
                logger.info("✅ Webhook mode activated!")
            else:
                logger.warning("⚠️ Webhook failed - check your configuration")

            # Start aiohttp server
            port = int(os.getenv('PORT', 8080))
            
            app = web.Application()
            app.router.add_post('/webhook', self.webhook_handler)
            app.router.add_get('/health', self.health_handler)
            app.router.add_get('/', self.root_handler)
            app.router.add_get('/debug', self.debug_handler)

            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, '0.0.0.0', port)
            await site.start()

            logger.info(f"✅ AIOHTTP server running on port {port}")
            logger.info(f"   • Healthcheck: /health")
            logger.info(f"   • Webhook: /webhook")
            logger.info("✅ Bot is running. Press Ctrl+C to stop.")
            
            self.is_ready = True

            # Keep running
            while not self._shutdown_flag:
                await asyncio.sleep(1)

        except asyncio.CancelledError:
            logger.info("👋 Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            await self.shutdown()

    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 Shutting down...")
        self._shutdown_flag = True
        
        if self.application:
            try:
                await self.application.stop()
                await self.application.shutdown()
                logger.info("✅ Application stopped")
            except Exception as e:
                logger.error(f"Error stopping application: {e}")

    def print_banner(self):
        """Print startup banner"""
        print("="*70)
        print("    MYLOVE-v1 - ULTIMATE AI BOT")
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
        
        print("="*70)


# =============================================================================
# SIGNAL HANDLERS
# =============================================================================
def signal_handler():
    """Handle shutdown signals"""
    logger.info("Received signal, shutting down...")
    for task in asyncio.all_tasks():
        task.cancel()


# =============================================================================
# MAIN
# =============================================================================
async def main():
    """Main entry point"""
    bot = MYLOVEBot()
    
    # Register signal handlers
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)
    
    try:
        await bot.start()
    except asyncio.CancelledError:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("👋 Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())
