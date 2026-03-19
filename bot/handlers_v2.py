#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - HANDLERS V2
=============================================================================
Handler untuk semua command V2
- Mendaftarkan command ke bot
- Message handler untuk deteksi intent
- Callback handler untuk inline keyboard
=============================================================================
"""

import logging
from telegram import Update
from telegram.ext import (
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    filters,
    ContextTypes
)

from .commands_v2 import CommandsV2
from ..pdkt_natural.command_handler import PDKTCommandHandler
from ..core.intent_analyzer import IntentAnalyzer
from ..core.proactive_generator import ProactiveMessageGenerator

logger = logging.getLogger(__name__)


class HandlersV2:
    """
    Mendaftarkan semua handler V2 ke bot
    """
    
    def __init__(self,
                 commands: CommandsV2,
                 pdkt_handler: PDKTCommandHandler,
                 intent_analyzer: IntentAnalyzer,
                 proactive: ProactiveMessageGenerator):
        
        self.cmd = commands
        self.pdkt = pdkt_handler
        self.intent = intent_analyzer
        self.proactive = proactive
        
        logger.info("✅ HandlersV2 initialized")
    
    def register_handlers(self, application):
        """
        Daftarkan semua handler ke application
        """
        
        # =====================================================================
        # PDKT COMMANDS
        # =====================================================================
        application.add_handler(CommandHandler("pdkt", self.cmd.cmd_pdkt))
        application.add_handler(CommandHandler("pdktrandom", self.cmd.cmd_pdktrandom))
        application.add_handler(CommandHandler("pdktlist", self.cmd.cmd_pdktlist))
        application.add_handler(CommandHandler("pdktdetail", self.cmd.cmd_pdktdetail))
        application.add_handler(CommandHandler("pdktwho", self.cmd.cmd_pdktwho))
        application.add_handler(CommandHandler("pausepdkt", self.cmd.cmd_pausepdkt))
        application.add_handler(CommandHandler("resumepdkt", self.cmd.cmd_resumepdkt))
        application.add_handler(CommandHandler("stoppdkt", self.cmd.cmd_stoppdkt))
        
        # =====================================================================
        # MANTAN COMMANDS
        # =====================================================================
        application.add_handler(CommandHandler("mantanlist", self.cmd.cmd_mantanlist))
        application.add_handler(CommandHandler("mantan", self.cmd.cmd_mantan))
        application.add_handler(CommandHandler("fwbrequest", self.cmd.cmd_fwbrequest))
        
        # =====================================================================
        # FWB COMMANDS
        # =====================================================================
        application.add_handler(CommandHandler("fwblist", self.cmd.cmd_fwblist))
        application.add_handler(CommandHandler("fwb pause", self.cmd.cmd_fwb_pause))
        application.add_handler(CommandHandler("fwb resume", self.cmd.cmd_fwb_resume))
        application.add_handler(CommandHandler("fwb end", self.cmd.cmd_fwb_end))
        
        # Handler untuk /fwb-1, /fwb-2, dll
        application.add_handler(MessageHandler(
            filters.Regex(r'^/fwb-\d+$'), 
            self.cmd.cmd_fwb_call
        ))
        
        # =====================================================================
        # HTS COMMANDS
        # =====================================================================
        application.add_handler(CommandHandler("htslist", self.cmd.cmd_htslist))
        
        # Handler untuk /hts-1, /hts-2, dll
        application.add_handler(MessageHandler(
            filters.Regex(r'^/hts-\d+$'), 
            self.cmd.cmd_hts_call
        ))
        
        # =====================================================================
        # MEMORY COMMANDS
        # =====================================================================
        application.add_handler(CommandHandler("memory", self.cmd.cmd_memory))
        application.add_handler(CommandHandler("flashback", self.cmd.cmd_flashback))
        
        # =====================================================================
        # MESSAGE HANDLER (untuk analisis intent)
        # =====================================================================
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.message_handler
        ))
        
        # =====================================================================
        # CALLBACK HANDLERS
        # =====================================================================
        application.add_handler(CallbackQueryHandler(
            self.callback_handler,
            pattern='^pdkt_'
        ))
        
        application.add_handler(CallbackQueryHandler(
            self.callback_handler,
            pattern='^stoppdkt_'
        ))
        
        application.add_handler(CallbackQueryHandler(
            self.callback_handler,
            pattern='^fwb_'
        ))
        
        logger.info("✅ All V2 handlers registered")
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler untuk semua pesan teks (bukan command)
        - Analisis intent
        - Cek perlu proactive
        - Teruskan ke AI engine
        """
        user = update.effective_user
        message = update.message.text
        
        # Analisis intent
        analysis = self.intent.analyze(message)
        context.user_data['last_intent'] = analysis
        
        # Log
        logger.info(f"📨 Message from {user.first_name}: {message[:50]}...")
        logger.debug(f"Intent: {analysis['primary_intent'].value}")
        
        # TODO: Teruskan ke AI engine untuk diproses
        
        # Sementara balas dummy
        await update.message.reply_text(f"Pesan diterima. Intent: {analysis['primary_intent'].value}")
    
    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler untuk semua callback query
        """
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user = update.effective_user
        
        logger.info(f"🔄 Callback: {data} from {user.first_name}")
        
        # Handle callback berdasarkan pattern
        if data.startswith('pdkt_force_new_'):
            await self.pdkt.handle_pdkt_force_new_callback(update, context)
        
        elif data.startswith('stoppdkt_confirm_'):
            await self.pdkt.handle_stoppdkt_callback(update, context)
        
        elif data == 'stoppdkt_cancel':
            await query.edit_message_text("✅ PDKT dilanjutkan.")
        
        else:
            await query.edit_message_text("❌ Perintah tidak dikenal.")


__all__ = ['HandlersV2']
