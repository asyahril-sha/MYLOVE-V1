#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - BOT APPLICATION
=============================================================================
- Setup Telegram bot application
- Register all handlers
- Error handling
"""

import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from telegram.error import TelegramError, NetworkError, TimedOut

from config import settings
from .commands import (
    start_command, help_command, status_command, cancel_command,
    jadipacar_command, break_command, unbreak_command, breakup_command, fwb_command,
    htslist_command, fwblist_command,
    close_command, continue_command, sessions_command,
    explore_command, locations_command, risk_command,
    tophts_command, myclimax_command, climaxhistory_command,
    stats_command, db_stats_command, backup_command, recover_command,
    debug_command
)
from .handlers import message_handler, callback_handler, hts_call_handler
from ..utils.logger import setup_logging

logger = logging.getLogger(__name__)


class BotApplication:
    """Telegram Bot Application Setup"""
    
    def __init__(self):
        self.app = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize bot application"""
        try:
            # Create application
            self.app = Application.builder()\
                .token(settings.telegram_token)\
                .concurrent_updates(True)\
                .build()
                
            # Register all handlers
            await self._register_handlers()
            
            # Set error handler
            self.app.add_error_handler(self.error_handler)
            
            self.initialized = True
            logger.info("✅ BotApplication initialized")
            
            return self.app
            
        except Exception as e:
            logger.error(f"Failed to initialize BotApplication: {e}")
            raise
            
    async def _register_handlers(self):
        """Register all command and message handlers"""
        
        # ===== BASIC COMMANDS =====
        basic_commands = [
            ("start", start_command),
            ("help", help_command),
            ("status", status_command),
            ("cancel", cancel_command),
        ]
        
        for cmd, handler in basic_commands:
            self.app.add_handler(CommandHandler(cmd, handler))
            logger.debug(f"Registered command: /{cmd}")
            
        # ===== RELATIONSHIP COMMANDS =====
        relationship_commands = [
            ("jadipacar", jadipacar_command),
            ("break", break_command),
            ("unbreak", unbreak_command),
            ("breakup", breakup_command),
            ("fwb", fwb_command),
        ]
        
        for cmd, handler in relationship_commands:
            self.app.add_handler(CommandHandler(cmd, handler))
            logger.debug(f"Registered command: /{cmd}")
            
        # ===== HTS/FWB COMMANDS =====
        hts_commands = [
            ("htslist", htslist_command),
            ("fwblist", fwblist_command),
        ]
        
        for cmd, handler in hts_commands:
            self.app.add_handler(CommandHandler(cmd, handler))
            logger.debug(f"Registered command: /{cmd}")
            
        # Special handler for /hts- [id]
        self.app.add_handler(MessageHandler(
            filters.Regex(r'^/hts-'), 
            hts_call_handler
        ))
        
        # ===== SESSION COMMANDS =====
        session_commands = [
            ("close", close_command),
            ("sessions", sessions_command),
        ]
        
        for cmd, handler in session_commands:
            self.app.add_handler(CommandHandler(cmd, handler))
            logger.debug(f"Registered command: /{cmd}")
            
        # Special handler for /continue
        self.app.add_handler(MessageHandler(
            filters.Regex(r'^/continue\s+'), 
            continue_command
        ))
        
        # ===== PUBLIC AREA COMMANDS =====
        public_commands = [
            ("explore", explore_command),
            ("locations", locations_command),
            ("risk", risk_command),
        ]
        
        for cmd, handler in public_commands:
            self.app.add_handler(CommandHandler(cmd, handler))
            logger.debug(f"Registered command: /{cmd}")
            
        # ===== RANKING COMMANDS =====
        ranking_commands = [
            ("tophts", tophts_command),
            ("myclimax", myclimax_command),
            ("climaxhistory", climaxhistory_command),
        ]
        
        for cmd, handler in ranking_commands:
            self.app.add_handler(CommandHandler(cmd, handler))
            logger.debug(f"Registered command: /{cmd}")
            
        # ===== ADMIN COMMANDS =====
        admin_commands = [
            ("stats", stats_command),
            ("db_stats", db_stats_command),
            ("backup", backup_command),
            ("recover", recover_command),
            ("debug", debug_command),
        ]
        
        for cmd, handler in admin_commands:
            self.app.add_handler(CommandHandler(cmd, handler))
            logger.debug(f"Registered command: /{cmd}")
            
        # ===== MESSAGE HANDLER =====
        self.app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            message_handler
        ))
        
        # ===== CALLBACK HANDLER =====
        self.app.add_handler(CallbackQueryHandler(callback_handler))
        
        logger.info(f"✅ Registered {len(basic_commands) + len(relationship_commands) + len(hts_commands) + len(session_commands) + len(public_commands) + len(ranking_commands) + len(admin_commands)} commands")
        
    async def error_handler(self, update, context):
        """Global error handler"""
        logger.error(f"Update {update} caused error {context.error}")
        
        try:
            if update and update.effective_message:
                await update.effective_message.reply_text(
                    "❌ Maaf, terjadi kesalahan. Tim MYLOVE sudah mencatat error ini."
                )
        except:
            pass
            
    async def start_polling(self):
        """Start bot in polling mode"""
        if not self.initialized:
            await self.initialize()
            
        await self.app.initialize()
        await self.app.start()
        
        logger.info("📡 Starting polling...")
        await self.app.updater.start_polling(
            allowed_updates=['message', 'callback_query'],
            drop_pending_updates=True,
            poll_interval=1.0,
            timeout=30
        )
        
    async def stop(self):
        """Stop bot"""
        if self.app:
            await self.app.stop()
            await self.app.shutdown()
            logger.info("Bot stopped")


__all__ = ['BotApplication']
