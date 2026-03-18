#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - MAIN ENTRY POINT
=============================================================================
Hybrid Webhook + Polling dengan Debug System Lengkap untuk Railway
"""

import os
import sys
import json
import time
import uuid
import asyncio
import logging
import traceback
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import signal

# Tambahkan path ke sys.path
sys.path.insert(0, str(Path(__file__).parent))

# =============================================================================
# DEBUG SYSTEM - EARLY INITIALIZATION
# =============================================================================
class DebugSystem:
    """Sistem debug komprehensif untuk identifikasi error di Railway"""
    
    def __init__(self):
        self.start_time = time.time()
        self.errors = []
        self.warnings = []
        self.debug_info = {}
        self.component_status = {}
        self.log_file = Path("data/logs/debug.log")
        self.crash_log = Path("data/logs/crash.log")
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup early logging sebelum konfigurasi penuh"""
        # Buat directory logs
        Path("data/logs").mkdir(parents=True, exist_ok=True)
        
        # Configure basic logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("MYLOVE_DEBUG")
        
    def log_component_start(self, component: str):
        """Log ketika komponen mulai diinisialisasi"""
        self.component_status[component] = {
            "status": "starting",
            "start_time": time.time(),
            "timestamp": datetime.now().isoformat()
        }
        self.logger.info(f"🚀 Starting component: {component}")
        
    def log_component_success(self, component: str, details: str = ""):
        """Log ketika komponen berhasil diinisialisasi"""
        if component in self.component_status:
            self.component_status[component]["status"] = "success"
            self.component_status[component]["end_time"] = time.time()
            self.component_status[component]["duration"] = (
                self.component_status[component]["end_time"] - 
                self.component_status[component]["start_time"]
            )
            self.component_status[component]["details"] = details
        self.logger.info(f"✅ Component success: {component} ({details})")
        
    def log_component_error(self, component: str, error: Exception, details: str = ""):
        """Log ketika komponen gagal diinisialisasi"""
        error_info = {
            "component": component,
            "error": str(error),
            "traceback": traceback.format_exc(),
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.errors.append(error_info)
        
        if component in self.component_status:
            self.component_status[component]["status"] = "error"
            self.component_status[component]["error"] = str(error)
            self.component_status[component]["traceback"] = traceback.format_exc()
        
        self.logger.error(f"❌ Component error: {component} - {error}")
        self.logger.error(traceback.format_exc())
        
        # Simpan ke crash log
        self._save_crash_log(error_info)
        
    def log_warning(self, component: str, warning: str):
        """Log warning"""
        warning_info = {
            "component": component,
            "warning": warning,
            "timestamp": datetime.now().isoformat()
        }
        self.warnings.append(warning_info)
        self.logger.warning(f"⚠️ Warning: {component} - {warning}")
        
    def log_info(self, component: str, info: str):
        """Log info"""
        self.logger.info(f"ℹ️ {component}: {info}")
        
    def log_debug(self, component: str, debug_info: Any):
        """Log debug info"""
        self.logger.debug(f"🐛 {component}: {debug_info}")
        
    def _save_crash_log(self, error_info: Dict):
        """Simpan crash log untuk analisis"""
        try:
            crash_data = {
                "timestamp": datetime.now().isoformat(),
                "uptime": time.time() - self.start_time,
                "error": error_info,
                "component_status": self.component_status,
                "environment": dict(os.environ),
                "python_version": sys.version,
                "platform": sys.platform
            }
            
            with open(self.crash_log, 'a') as f:
                f.write(json.dumps(crash_data, indent=2))
                f.write("\n" + "="*50 + "\n")
        except:
            pass
            
    async def health_check(self) -> Dict:
        """Health check endpoint untuk Railway"""
        return {
            "status": "healthy" if len(self.errors) == 0 else "degraded",
            "uptime": time.time() - self.start_time,
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "components": self.component_status,
            "timestamp": datetime.now().isoformat()
        }
        
    def print_summary(self):
        """Print ringkasan debug"""
        print("\n" + "="*70)
        print("🔍 MYLOVE ULTIMATE - DEBUG SUMMARY")
        print("="*70)
        print(f"Uptime: {time.time() - self.start_time:.2f} seconds")
        print(f"Total Errors: {len(self.errors)}")
        print(f"Total Warnings: {len(self.warnings)}")
        print("\n📊 Component Status:")
        for comp, status in self.component_status.items():
            emoji = "✅" if status["status"] == "success" else "❌" if status["status"] == "error" else "⏳"
            duration = status.get("duration", 0)
            print(f"  {emoji} {comp}: {status['status']} ({duration:.2f}s)")
            
        if self.errors:
            print("\n❌ Recent Errors:")
            for i, error in enumerate(self.errors[-3:]):  # Show last 3 errors
                print(f"  {i+1}. {error['component']}: {error['error']}")
                
        if self.warnings:
            print("\n⚠️ Recent Warnings:")
            for i, warning in enumerate(self.warnings[-3:]):
                print(f"  {i+1}. {warning['component']}: {warning['warning']}")
                
        print("="*70 + "\n")


# =============================================================================
# INITIALIZE DEBUG SYSTEM
# =============================================================================
debug = DebugSystem()
debug.log_info("DEBUG_SYSTEM", "Debug system initialized")


# =============================================================================
# IMPORTS WITH ERROR HANDLING
# =============================================================================
try:
    debug.log_component_start("CONFIG_LOAD")
    from config import settings
    debug.log_component_success("CONFIG_LOAD", f"Database: {settings.database.type}")
except Exception as e:
    debug.log_component_error("CONFIG_LOAD", e, "Fatal: Cannot load config")
    sys.exit(1)

try:
    debug.log_component_start("UTILS_LOGGER")
    from utils.logger import setup_logging
    logger = setup_logging("mylove_ultimate")
    debug.log_component_success("UTILS_LOGGER")
except Exception as e:
    debug.log_component_error("UTILS_LOGGER", e)
    logger = debug.logger  # Fallback ke debug logger

try:
    debug.log_component_start("TELEGRAM_IMPORT")
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application, CommandHandler, MessageHandler, 
        filters, CallbackQueryHandler, ContextTypes
    )
    from telegram.error import TelegramError, NetworkError, TimedOut
    debug.log_component_success("TELEGRAM_IMPORT")
except Exception as e:
    debug.log_component_error("TELEGRAM_IMPORT", e)
    raise

try:
    debug.log_component_start("FASTAPI_IMPORT")
    from fastapi import FastAPI, Request, Response
    import uvicorn
    debug.log_component_success("FASTAPI_IMPORT")
except Exception as e:
    debug.log_component_error("FASTAPI_IMPORT", e)
    # Non-fatal, mungkin hanya untuk webhook

try:
    debug.log_component_start("DATABASE_IMPORT")
    from database.connection import init_db, get_db
    from database.models import Base
    debug.log_component_success("DATABASE_IMPORT")
except Exception as e:
    debug.log_component_error("DATABASE_IMPORT", e)
    # Non-fatal, akan dihandle di initialization


# =============================================================================
# MYLOVE BOT CLASS
# =============================================================================
class MyLoveUltimate:
    """MYLOVE ULTIMATE VERSI 1 - Main Bot Class"""
    
    def __init__(self):
        self.debug = debug
        self.logger = logger
        self.app: Optional[Application] = None
        self.fastapi_app: Optional[FastAPI] = None
        self.webhook_manager = None
        self.start_time = time.time()
        self.message_count = 0
        self.error_count = 0
        self.webhook_mode = False
        
        debug.log_info("BOT_INIT", "MyLoveUltimate instance created")
        
    async def initialize(self):
        """Initialize all components asynchronously"""
        self.debug.log_component_start("BOT_INITIALIZATION")
        
        try:
            # Initialize database
            self.debug.log_component_start("DATABASE")
            await init_db()
            self.debug.log_component_success("DATABASE", "SQLite connected")
        except Exception as e:
            self.debug.log_component_error("DATABASE", e)
            self.error_count += 1
            
        try:
            # Initialize memory systems
            self.debug.log_component_start("MEMORY_SYSTEM")
            from memory.vector_db import VectorMemory
            self.memory = VectorMemory(settings.memory.vector_db_dir)
            await self.memory.initialize()
            self.debug.log_component_success("MEMORY_SYSTEM", "Vector DB ready")
        except Exception as e:
            self.debug.log_component_error("MEMORY_SYSTEM", e)
            self.error_count += 1
            
            
        try:
            # Initialize AI engine
            self.debug.log_component_start("AI_ENGINE")
            from core.ai_engine import DeepSeekEngine
            self.ai_engine = DeepSeekEngine(
                api_key=settings.deepseek_api_key,
                memory=self.memory
            )
            self.debug.log_component_success("AI_ENGINE", f"Model: {settings.ai.model}")
        except Exception as e:
            self.debug.log_component_error("AI_ENGINE", e)
            self.error_count += 1
            
        try:
            # Initialize session manager
            self.debug.log_component_start("SESSION_MANAGER")
            from session.storage import SessionStorage
            self.session_storage = SessionStorage(
                db_path=settings.database.path,
                session_dir=settings.session.session_dir
            )
            self.debug.log_component_success("SESSION_MANAGER")
        except Exception as e:
            self.debug.log_component_error("SESSION_MANAGER", e)
            self.error_count += 1
            
        try:
        # Initialize relationship system
        self.debug.log_component_start("RELATIONSHIP_SYSTEM")
    
        # Import yang diperlukan
        from memory.relationship import RelationshipMemory
        from relationship.intimacy import IntimacySystem
        from relationship.ranking import RankingSystem
    
        # Inisialisasi relationship memory
        self.relationship_memory = RelationshipMemory(db_path=settings.database.path)
        await self.relationship_memory.initialize()
    
        # Inisialisasi intimacy system (consolidation bisa None dulu)
        self.intimacy = IntimacySystem(
            relationship_memory=self.relationship_memory,
            consolidation=None
        )
    
        # Inisialisasi ranking system dengan relationship_memory
        self.ranking = RankingSystem(relationship_memory=self.relationship_memory)
    
        self.debug.log_component_success("RELATIONSHIP_SYSTEM")
    except Exception as e:
        self.debug.log_component_error("RELATIONSHIP_SYSTEM", e)
        self.error_count += 1
            
        # Build Telegram application
        try:
            self.debug.log_component_start("TELEGRAM_APP")
            self.app = Application.builder()\
                .token(settings.telegram_token)\
                .concurrent_updates(True)\
                .build()
            self.debug.log_component_success("TELEGRAM_APP")
        except Exception as e:
            self.debug.log_component_error("TELEGRAM_APP", e)
            self.error_count += 1
            raise
            
        # Register handlers
        await self._register_handlers()
        
        # Setup error handlers
        self.app.add_error_handler(self.error_handler)
        
        self.debug.log_component_success("BOT_INITIALIZATION", 
            f"Components: {len(self.debug.component_status)}/{self.error_count} errors")
        
        return self
        
    async def _register_handlers(self):
        """Register all command and message handlers"""
        self.debug.log_component_start("HANDLER_REGISTRATION")
        
        try:
            # Import commands
            from bot.commands import (
                start_command, help_command, status_command,
                jadipacar_command, break_command, unbreak_command,
                breakup_command, fwb_command,
                htslist_command, fwblist_command,
                close_command, continue_command, sessions_command,
                explore_command, locations_command, risk_command,
                tophts_command, myclimax_command, climaxhistory_command,
                stats_command, db_stats_command, backup_command, recover_command
            )
            
            # Register all commands
            commands = [
                # Basic
                ("start", start_command),
                ("help", help_command),
                ("status", status_command),
                ("cancel", self.cancel_command),
                
                # Relationship
                ("jadipacar", jadipacar_command),
                ("break", break_command),
                ("unbreak", unbreak_command),
                ("breakup", breakup_command),
                ("fwb", fwb_command),
                
                # HTS/FWB
                ("htslist", htslist_command),
                ("fwblist", fwblist_command),
                
                # Session
                ("close", close_command),
                ("sessions", sessions_command),
                
                # Public Area
                ("explore", explore_command),
                ("locations", locations_command),
                ("risk", risk_command),
                
                # Ranking
                ("tophts", tophts_command),
                ("myclimax", myclimax_command),
                ("climaxhistory", climaxhistory_command),
                
                # Admin
                ("stats", stats_command),
                ("db_stats", db_stats_command),
                ("backup", backup_command),
                ("recover", recover_command),
                ("debug", self.debug_command),
            ]
            
            for command, handler in commands:
                self.app.add_handler(CommandHandler(command, handler))
                self.debug.log_debug("HANDLER", f"Registered /{command}")
                
            # Register callback for HTS calls (/hts- [id])
            self.app.add_handler(MessageHandler(
                filters.Regex(r'^/hts-\s*\w+'), 
                hts_call_command
            ))
            
            # Register callback for continue (/continue [id])
            self.app.add_handler(MessageHandler(
                filters.Regex(r'^/continue\s+'), 
                continue_command
            ))
            
            # Register message handler (for natural conversation)
            self.app.add_handler(MessageHandler(
                filters.TEXT & ~filters.COMMAND, 
                self.message_handler
            ))
            
            # Register callback query handler (for buttons)
            self.app.add_handler(CallbackQueryHandler(self.callback_handler))
            
            self.debug.log_component_success("HANDLER_REGISTRATION", 
                f"Registered {len(commands)} commands")
                
        except Exception as e:
            self.debug.log_component_error("HANDLER_REGISTRATION", e)
            self.error_count += 1
            
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Global error handler"""
        self.error_count += 1
        
        error_msg = f"Error: {context.error}"
        self.debug.log_component_error("RUNTIME_ERROR", context.error, 
            f"Update: {update}")
        
        try:
            if update and update.effective_message:
                await update.effective_message.reply_text(
                    "❌ Maaf, terjadi kesalahan. Tim MYLOVE sudah mencatat error ini."
                )
        except:
            pass
            
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        start_time = time.time()
        self.message_count += 1
        
        try:
            user = update.effective_user
            message = update.message.text
            
            self.debug.log_debug("MESSAGE", f"From {user.id}: {message[:50]}...")
            
            # Check if this is a location intent (auto-detect)
            location = await self.location_selector.detect_location_intent(message)
            if location:
                # Handle location selection
                response = await self._handle_location(user.id, location)
            else:
                # Generate AI response
                response = await self.ai_engine.generate_response(
                    user_message=message,
                    user_id=user.id,
                    context=await self._get_context(user.id)
                )
                
            # Check response length
            if len(response) < settings.performance.min_message_length:
                response += "\n\n" + await self._generate_continuation()
            elif len(response) > settings.performance.max_message_length:
                response = response[:settings.performance.max_message_length-3] + "..."
                
            # Send response
            await update.message.reply_text(
                response,
                parse_mode='HTML'
            )
            
            # Log performance
            response_time = time.time() - start_time
            if response_time > settings.performance.target_response_time:
                self.debug.log_warning("PERFORMANCE", 
                    f"Slow response: {response_time:.2f}s > {settings.performance.target_response_time}s")
                
        except Exception as e:
            self.debug.log_component_error("MESSAGE_HANDLER", e)
            await update.message.reply_text(
                "❌ Error processing message. Coba lagi nanti."
            )
            
    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        await query.answer()
        
        try:
            data = query.data
            self.debug.log_debug("CALLBACK", f"Data: {data}")
            
            # Handle callback based on data
            if data.startswith("hts_select_"):
                role_id = data.replace("hts_select_", "")
                # Handle HTS selection
                await query.edit_message_text(f"Memilih HTS: {role_id}")
                
        except Exception as e:
            self.debug.log_component_error("CALLBACK_HANDLER", e)
            
    async def _get_context(self, user_id: int) -> Dict:
        """Get user context from memory"""
        try:
            # Get active session
            session = await self.session_storage.get_active_session(user_id)
            
            # Get intimacy level
            intimacy = await self.intimacy.get_level(user_id, session.role if session else None)
            
            # Get recent memories
            memories = await self.memory.get_recent(user_id, limit=5)
            
            return {
                "session": session,
                "intimacy": intimacy,
                "memories": memories,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.debug.log_warning("CONTEXT", f"Error getting context: {e}")
            return {}
            
    async def _generate_continuation(self) -> str:
        """Generate continuation for short messages"""
        # Simple continuation examples
        continuations = [
            "\n\nAku kangen kamu...",
            "\n\nEh kamu lagi ngapain?",
            "\n\nJangan lupa makan ya...",
            "\n\n*mesem-mesem sendiri*",
            "\n\nUdah makan belum?",
        ]
        import random
        return random.choice(continuations)
        
    async def _handle_location(self, user_id: int, location: str) -> str:
        """Handle location selection"""
        # Get location details
        location_data = await self.location_selector.get_location_details(location)
        
        # Calculate dynamic risk
        risk = await self.location_selector.calculate_risk(location_data)
        
        # Generate response
        response = f"📍 {location}\n"
        response += f"⚠️ Risk: {risk}%\n"
        
        if risk > 70:
            response += "Wah risk tinggi nih... berani? 😈"
        elif risk > 50:
            response += "Risk medium, asal hati-hati aja 🤫"
        else:
            response += "Aman kayaknya, yuk! 🥰"
            
        return response
        
    async def debug_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Debug command - only for admin"""
        user_id = update.effective_user.id
        
        if user_id != settings.admin_id:
            await update.message.reply_text("❌ Command hanya untuk admin")
            return
            
        # Get debug info
        health = await self.debug.health_check()
        
        debug_text = "🔍 **MYLOVE DEBUG INFO**\n\n"
        debug_text += f"Uptime: {health['uptime']:.2f}s\n"
        debug_text += f"Messages: {self.message_count}\n"
        debug_text += f"Errors: {self.error_count}\n"
        debug_text += f"Webhook Mode: {self.webhook_mode}\n\n"
        
        debug_text += "**Components:**\n"
        for comp, status in health['components'].items():
            emoji = "✅" if status['status'] == 'success' else "❌"
            debug_text += f"{emoji} {comp}: {status['status']}\n"
            
        if self.debug.errors:
            debug_text += "\n**Recent Errors:**\n"
            for error in self.debug.errors[-3:]:
                debug_text += f"• {error['component']}: {error['error'][:100]}\n"
                
        await update.message.reply_text(debug_text, parse_mode='Markdown')
        
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel current conversation"""
        await update.message.reply_text(
            "❌ Percakapan dibatalkan.\n"
            "Ketik /start untuk memulai lagi."
        )
        
    async def setup_webhook(self) -> bool:
        """Setup webhook with retry mechanism"""
        self.debug.log_component_start("WEBHOOK_SETUP")
        
        # Determine webhook URL
        if settings.railway.public_domain:
            webhook_url = f"https://{settings.railway.public_domain}/webhook/{settings.telegram_token}"
        elif settings.webhook.url:
            webhook_url = f"{settings.webhook.url}/webhook/{settings.telegram_token}"
        else:
            self.debug.log_warning("WEBHOOK", "No public domain, using polling")
            return False
            
        # Try to set webhook with retry
        for attempt in range(settings.webhook.max_retries):
            try:
                self.debug.log_info("WEBHOOK", f"Attempt {attempt+1}: Setting webhook to {webhook_url}")
                
                await self.app.bot.set_webhook(
                    url=webhook_url,
                    allowed_updates=['message', 'callback_query', 'inline_query'],
                    drop_pending_updates=True,
                    max_connections=40
                )
                
                # Verify webhook
                webhook_info = await self.app.bot.get_webhook_info()
                self.debug.log_info("WEBHOOK", f"Webhook set: {webhook_info.url}")
                self.debug.log_info("WEBHOOK", f"Pending updates: {webhook_info.pending_update_count}")
                
                self.debug.log_component_success("WEBHOOK_SETUP", f"URL: {webhook_url}")
                self.webhook_mode = True
                return True
                
            except Exception as e:
                wait = settings.webhook.retry_backoff ** attempt
                self.debug.log_warning("WEBHOOK", f"Attempt {attempt+1} failed: {e}, retrying in {wait}s")
                await asyncio.sleep(wait)
                
        # Fallback to polling
        self.debug.log_warning("WEBHOOK", "All webhook attempts failed, falling back to polling")
        self.debug.log_component_success("WEBHOOK_SETUP", "Using polling mode (fallback)")
        self.webhook_mode = False
        return False
        
    async def start_polling(self):
        """Start bot in polling mode"""
        self.debug.log_info("POLLING", "Starting in polling mode...")
        
        await self.app.initialize()
        await self.app.start()
        
        # Start polling
        await self.app.updater.start_polling(
            allowed_updates=[],
            drop_pending_updates=True,
            poll_interval=1.0,
            timeout=30
        )
        
        self.debug.log_info("POLLING", "Polling started successfully")
        
    async def start_webhook_server(self):
        """Start FastAPI server for webhook"""
        self.debug.log_component_start("FASTAPI_SERVER")
        
        try:
            # Create FastAPI app
            self.fastapi_app = FastAPI(
                title="MYLOVE Ultimate",
                version="1.0",
                description="MYLOVE Ultimate V1 - Telegram Bot API"
            )
            
            # Setup routes
            @self.fastapi_app.get("/")
            async def root():
                health = await self.debug.health_check()
                return {
                    "name": "MYLOVE Ultimate V1",
                    "status": health['status'],
                    "uptime": health['uptime'],
                    "webhook_mode": self.webhook_mode,
                    "admin_id": settings.admin_id
                }
                
            @self.fastapi_app.get("/health")
            async def health_check():
                return await self.debug.health_check()
                
            @self.fastapi_app.get("/debug")
            async def debug_info():
                if not self.app:
                    return {"error": "Bot not initialized"}
                
                return {
                    "components": self.debug.component_status,
                    "errors": self.debug.errors[-5:],
                    "warnings": self.debug.warnings[-5:],
                    "message_count": self.message_count,
                    "error_count": self.error_count,
                    "webhook_mode": self.webhook_mode,
                    "start_time": self.start_time,
                    "current_time": time.time()
                }
                
            @self.fastapi_app.post(f"/webhook/{settings.telegram_token}")
            async def webhook(request: Request):
                """Telegram webhook endpoint"""
                if not self.app:
                    return Response(status_code=503, content="Bot not ready")
                    
                try:
                    # Parse update
                    data = await request.json()
                    update = Update.de_json(data, self.app.bot)
                    
                    # Process in background
                    asyncio.create_task(self.app.process_update(update))
                    
                    return Response(status_code=200)
                    
                except Exception as e:
                    self.debug.log_component_error("WEBHOOK_ENDPOINT", e)
                    return Response(status_code=500)
                    
            @self.fastapi_app.post("/webhook/test")
            async def test_webhook():
                return {"message": "Webhook is working!"}
                
            self.debug.log_component_success("FASTAPI_SERVER", "Routes configured")
            
            # Start server
            port = int(os.getenv("PORT", settings.webhook.port))
            host = os.getenv("HOST", "0.0.0.0")
            
            self.debug.log_info("FASTAPI", f"Starting server on {host}:{port}")
            
            config = uvicorn.Config(
                self.fastapi_app,
                host=host,
                port=port,
                log_level="info",
                reload=False
            )
            server = uvicorn.Server(config)
            
            # Run server
            await server.serve()
            
        except Exception as e:
            self.debug.log_component_error("FASTAPI_SERVER", e)
            raise
            
    async def run(self):
        """Main run method"""
        try:
            # Initialize
            await self.initialize()
            
            # Try webhook first
            webhook_success = await self.setup_webhook()
            
            if webhook_success:
                # Start webhook server
                await self.start_webhook_server()
            else:
                # Fallback to polling
                await self.start_polling()
                
                # Keep running
                while True:
                    await asyncio.sleep(1)
                    
        except KeyboardInterrupt:
            self.debug.log_info("SHUTDOWN", "Received keyboard interrupt")
        except Exception as e:
            self.debug.log_component_error("MAIN_RUN", e)
        finally:
            await self.shutdown()
            
    async def shutdown(self):
        """Graceful shutdown"""
        self.debug.log_info("SHUTDOWN", "Shutting down...")
        
        if self.app:
            try:
                if self.webhook_mode:
                    await self.app.bot.delete_webhook(drop_pending_updates=True)
                    self.debug.log_info("SHUTDOWN", "Webhook deleted")
                    
                await self.app.stop()
                await self.app.shutdown()
                self.debug.log_info("SHUTDOWN", "Telegram app stopped")
            except Exception as e:
                self.debug.log_component_error("SHUTDOWN", e)
                
        # Close memory
        if hasattr(self, 'memory'):
            try:
                await self.memory.close()
            except:
                pass
                
        # Print final summary
        self.debug.print_summary()
        
        self.debug.log_info("SHUTDOWN", "Goodbye!")


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================
async def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("💕 MYLOVE ULTIMATE VERSI 1")
    print("="*70)
    print(f"Debug System: ACTIVE")
    print(f"Log file: {debug.log_file}")
    print(f"Crash log: {debug.crash_log}")
    print("="*70 + "\n")
    
    # Create bot instance
    bot = MyLoveUltimate()
    
    # Handle shutdown signals
    loop = asyncio.get_running_loop()
    
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda: asyncio.create_task(bot.shutdown())
        )
    
    # Run bot
    await bot.run()


def run_main():
    """Synchronous wrapper for main"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        debug.log_info("EXIT", "Bot stopped by user")
    except Exception as e:
        debug.log_component_error("FATAL", e)
        debug.print_summary()
        sys.exit(1)


if __name__ == "__main__":
    run_main()
