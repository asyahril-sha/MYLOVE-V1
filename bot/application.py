#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - PTB APPLICATION FACTORY (FIX FULL)
=============================================================================
- Menggabungkan handler V1 dan V2
- Mendaftarkan semua command
- Conversation handlers untuk role selection
- Error handling
- Siap untuk V2 dengan semua fitur
=============================================================================
"""

import logging
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler
)
from telegram.request import HTTPXRequest

from config import settings
from utils.logger import logger
from database.models import Constants

# =============================================================================
# IMPORT HANDLERS V1
# =============================================================================
from bot.handlers import (
    start_command, help_command, status_command, cancel_command,
    dominant_command, pause_command, unpause_command,
    close_command, end_command, jadipacar_command,
    break_command, unbreak_command, breakup_command, fwb_command,
    htslist_command, fwblist_command, hts_call_handler,
    fwb_call_handler, tophts_command, myclimax_command,
    climaxhistory_command, explore_command,
    go_command, positions_command, risk_command, mood_command,
    admin_command, stats_command, db_stats_command, list_users_command,
    get_user_command, force_reset_command, backup_db_command,
    vacuum_command, memory_stats_command, reload_command, debug_command,
    message_handler, callback_handler, continue_handler,
    error_handler
)

from bot.callbacks import (
    agree_18_callback, start_pause_callback,
    role_ipar_callback, role_teman_kantor_callback,
    role_janda_callback, role_pelakor_callback,
    role_istri_orang_callback, role_pdkt_callback,
    role_sepupu_callback, role_teman_sma_callback,
    role_mantan_callback, end_callback, close_callback,
    jadipacar_callback, break_callback, breakup_callback,
    fwb_callback, threesome_menu_callback
)

# =============================================================================
# IMPORT V2 COMMANDS (JIKA ADA)
# =============================================================================
try:
    from bot.commands_v2 import CommandsV2
    from bot.handlers_v2 import HandlersV2
    from bot.callbacks_v2 import CallbacksV2
    V2_AVAILABLE = True
    logger.info("✅ V2 commands loaded")
except ImportError:
    V2_AVAILABLE = False
    logger.info("ℹ️ Running in V1 mode only")
    CommandsV2 = None
    HandlersV2 = None
    CallbacksV2 = None


# =============================================================================
# BOT STATES
# =============================================================================
class BotStates:
    """States for conversation handlers"""
    
    # V1 States
    SELECTING_ROLE = 1
    SELECTING_BOT_NAME = 2
    SELECTING_BOT_ROLE = 3
    SELECTING_DOMINANCE = 4
    SELECTING_PERSONALITY = 5
    SELECTING_APPEARANCE = 6
    CONFIRMATION = 7
    CHATTING = 8
    SELECTING_ACTION = 9
    SELECTING_LOCATION = 10
    SELECTING_CLOTHING = 11
    SELECTING_ACTIVITY = 12
    AWAITING_RESPONSE = 13
    CONFIRM_END = 14
    CONFIRM_CLOSE = 15
    CONFIRM_BROADCAST = 16
    
    # V2 States
    SELECTING_PDKT = 17
    SELECTING_PDKT_ACTION = 18
    SELECTING_MANTAN = 19
    SELECTING_FWB = 20
    SELECTING_FWB_ACTION = 21
    CONFIRM_FWB_REQUEST = 22
    SELECTING_HTS = 23
    PDKT_PAUSED = 24
    FWB_PAUSED = 25


def create_application() -> Application:
    """
    Create and configure telegram application
    Menggabungkan semua handler V1 dan V2
    """
    
    logger.info("🔧 Creating PTB application...")
    
    # Custom request dengan timeout besar
    request = HTTPXRequest(
        connection_pool_size=50,
        connect_timeout=60,
        read_timeout=60,
        write_timeout=60,
        pool_timeout=60,
    )
    
    # Build application
    app = ApplicationBuilder() \
        .token(settings.telegram_token) \
        .request(request) \
        .concurrent_updates(True) \
        .build()
    
    # ===== AMBIL STATE DARI CONSTANTS ATAU FALLBACK =====
    SELECTING_ROLE = getattr(Constants, 'SELECTING_ROLE', BotStates.SELECTING_ROLE)
    CONFIRM_END = getattr(Constants, 'CONFIRM_END', BotStates.CONFIRM_END)
    CONFIRM_CLOSE = getattr(Constants, 'CONFIRM_CLOSE', BotStates.CONFIRM_CLOSE)
    CONFIRM_BROADCAST = getattr(Constants, 'CONFIRM_BROADCAST', BotStates.CONFIRM_BROADCAST)
    
    logger.info(f"  • Using SELECTING_ROLE = {SELECTING_ROLE}")
    
    # =========================================================================
    # V1 CONVERSATION HANDLERS
    # =========================================================================
    
    # Start conversation
    start_conv = ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],
        states={
            SELECTING_ROLE: [
                CallbackQueryHandler(agree_18_callback, pattern='^agree_18$'),
                CallbackQueryHandler(start_pause_callback, pattern='^(unpause|new)$'),
                CallbackQueryHandler(role_ipar_callback, pattern='^role_ipar$'),
                CallbackQueryHandler(role_teman_kantor_callback, pattern='^role_teman_kantor$'),
                CallbackQueryHandler(role_janda_callback, pattern='^role_janda$'),
                CallbackQueryHandler(role_pelakor_callback, pattern='^role_pelakor$'),
                CallbackQueryHandler(role_istri_orang_callback, pattern='^role_istri_orang$'),
                CallbackQueryHandler(role_pdkt_callback, pattern='^role_pdkt$'),
                CallbackQueryHandler(role_sepupu_callback, pattern='^role_sepupu$'),
                CallbackQueryHandler(role_teman_sma_callback, pattern='^role_teman_sma$'),
                CallbackQueryHandler(role_mantan_callback, pattern='^role_mantan$'),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_command)],
        name="start_conversation",
        persistent=False,
        per_user=True,
        per_chat=True,
        per_message=False
    )
    
    # End conversation
    end_conv = ConversationHandler(
        entry_points=[CommandHandler('end', end_command)],
        states={
            CONFIRM_END: [CallbackQueryHandler(end_callback, pattern='^end_')],
        },
        fallbacks=[CommandHandler('cancel', cancel_command)],
        name="end_conversation",
        persistent=False,
        per_user=True,
        per_chat=True,
        per_message=False
    )
    
    # Close conversation
    close_conv = ConversationHandler(
        entry_points=[CommandHandler('close', close_command)],
        states={
            CONFIRM_CLOSE: [CallbackQueryHandler(close_callback, pattern='^close_')],
        },
        fallbacks=[CommandHandler('cancel', cancel_command)],
        name="close_conversation",
        persistent=False,
        per_user=True,
        per_chat=True,
        per_message=False
    )
    
    # Relationship conversations
    rel_conv = ConversationHandler(
        entry_points=[
            CommandHandler('jadipacar', jadipacar_command),
            CommandHandler('break', break_command),
            CommandHandler('breakup', breakup_command),
            CommandHandler('fwb', fwb_command)
        ],
        states={
            CONFIRM_BROADCAST: [
                CallbackQueryHandler(jadipacar_callback, pattern='^jadipacar_'),
                CallbackQueryHandler(break_callback, pattern='^break_'),
                CallbackQueryHandler(breakup_callback, pattern='^breakup_'),
                CallbackQueryHandler(fwb_callback, pattern='^fwb_'),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_command)],
        name="relationship_conversation",
        persistent=False,
        per_user=True,
        per_chat=True,
        per_message=False
    )
    
    # =========================================================================
    # ADD V1 CONVERSATION HANDLERS
    # =========================================================================
    app.add_handler(start_conv)
    app.add_handler(end_conv)
    app.add_handler(close_conv)
    app.add_handler(rel_conv)
    
    # =========================================================================
    # V1 COMMAND HANDLERS
    # =========================================================================
    logger.info("  • Registering V1 command handlers...")
    
    # Basic commands
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("cancel", cancel_command))
    
    # Dominance commands
    app.add_handler(CommandHandler("dominant", dominant_command))
    
    # Session commands
    app.add_handler(CommandHandler("pause", pause_command))
    app.add_handler(CommandHandler("unpause", unpause_command))
    app.add_handler(CommandHandler("close", close_command))
    app.add_handler(CommandHandler("end", end_command))
    
    # Relationship commands
    app.add_handler(CommandHandler("jadipacar", jadipacar_command))
    app.add_handler(CommandHandler("break", break_command))
    app.add_handler(CommandHandler("unbreak", unbreak_command))
    app.add_handler(CommandHandler("breakup", breakup_command))
    app.add_handler(CommandHandler("fwb", fwb_command))
    
    # HTS/FWB commands
    app.add_handler(CommandHandler("htslist", htslist_command))
    app.add_handler(CommandHandler("fwblist", fwblist_command))
    
    # HTS/FWB call commands (pattern matching)
    app.add_handler(MessageHandler(filters.Regex(r'^/hts-'), hts_call_handler))
    app.add_handler(MessageHandler(filters.Regex(r'^/fwb-'), fwb_call_handler))
    
    # Ranking commands
    app.add_handler(CommandHandler("tophts", tophts_command))
    app.add_handler(CommandHandler("myclimax", myclimax_command))
    app.add_handler(CommandHandler("climaxhistory", climaxhistory_command))
    
    # Public area commands
    app.add_handler(CommandHandler("explore", explore_command))
    app.add_handler(CommandHandler("go", go_command))
    app.add_handler(CommandHandler("positions", positions_command))
    app.add_handler(CommandHandler("risk", risk_command))
    app.add_handler(CommandHandler("mood", mood_command))
    
    # Admin commands
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("db_stats", db_stats_command))
    app.add_handler(CommandHandler("list_users", list_users_command))
    app.add_handler(CommandHandler("get_user", get_user_command))
    app.add_handler(CommandHandler("force_reset", force_reset_command))
    app.add_handler(CommandHandler("backup_db", backup_db_command))
    app.add_handler(CommandHandler("vacuum", vacuum_command))
    app.add_handler(CommandHandler("memory_stats", memory_stats_command))
    app.add_handler(CommandHandler("reload", reload_command))
    app.add_handler(CommandHandler("debug", debug_command))
    
    # Hidden commands
    app.add_handler(CommandHandler("reset", force_reset_command))
    
    # =========================================================================
    # V2 COMMAND HANDLERS (JIKA ADA)
    # =========================================================================
    if V2_AVAILABLE and CommandsV2:
        logger.info("  • Registering V2 command handlers...")
        
        # Buat instance commands V2 (akan diinisialisasi dengan dependencies nanti)
        # Ini hanya placeholder, sebenarnya commands V2 perlu dependencies
        # Yang akan di-set di main.py
        
        # PDKT Commands
        app.add_handler(CommandHandler("pdkt", lambda u,c: None))  # Akan di-override di main.py
        app.add_handler(CommandHandler("pdktrandom", lambda u,c: None))
        app.add_handler(CommandHandler("pdktlist", lambda u,c: None))
        app.add_handler(CommandHandler("pdktdetail", lambda u,c: None))
        app.add_handler(CommandHandler("pdktwho", lambda u,c: None))
        app.add_handler(CommandHandler("pausepdkt", lambda u,c: None))
        app.add_handler(CommandHandler("resumepdkt", lambda u,c: None))
        app.add_handler(CommandHandler("stoppdkt", lambda u,c: None))
        
        # Progress command (berlaku untuk semua role)
        app.add_handler(CommandHandler("progress", lambda u,c: None))
        app.add_handler(CommandHandler("pdktstatus", lambda u,c: None))  # Alias
        
        # Mantan Commands
        app.add_handler(CommandHandler("mantanlist", lambda u,c: None))
        app.add_handler(CommandHandler("mantan", lambda u,c: None))
        app.add_handler(CommandHandler("fwbrequest", lambda u,c: None))
        
        # FWB Commands
        app.add_handler(CommandHandler("fwblist", lambda u,c: None))
        app.add_handler(CommandHandler("fwb pause", lambda u,c: None))
        app.add_handler(CommandHandler("fwb resume", lambda u,c: None))
        app.add_handler(CommandHandler("fwb end", lambda u,c: None))
        
        # HTS Commands
        app.add_handler(CommandHandler("htslist", lambda u,c: None))
        
        # Memory Commands
        app.add_handler(CommandHandler("memory", lambda u,c: None))
        app.add_handler(CommandHandler("flashback", lambda u,c: None))
        
        # Pattern handlers untuk /fwb-1, /hts-1
        app.add_handler(MessageHandler(filters.Regex(r'^/fwb-\d+$'), lambda u,c: None))
        app.add_handler(MessageHandler(filters.Regex(r'^/hts-\d+$'), lambda u,c: None))
    
    # =========================================================================
    # MESSAGE HANDLER (HARUS PALING AKHIR)
    # =========================================================================
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # =========================================================================
    # CALLBACK HANDLERS
    # =========================================================================
    logger.info("  • Registering callback handlers...")
    
    # V1 Callbacks
    app.add_handler(CallbackQueryHandler(agree_18_callback, pattern='^agree_18$'))
    app.add_handler(CallbackQueryHandler(start_pause_callback, pattern='^(unpause|new)$'))
    app.add_handler(CallbackQueryHandler(role_ipar_callback, pattern='^role_ipar$'))
    app.add_handler(CallbackQueryHandler(role_teman_kantor_callback, pattern='^role_teman_kantor$'))
    app.add_handler(CallbackQueryHandler(role_janda_callback, pattern='^role_janda$'))
    app.add_handler(CallbackQueryHandler(role_pelakor_callback, pattern='^role_pelakor$'))
    app.add_handler(CallbackQueryHandler(role_istri_orang_callback, pattern='^role_istri_orang$'))
    app.add_handler(CallbackQueryHandler(role_pdkt_callback, pattern='^role_pdkt$'))
    app.add_handler(CallbackQueryHandler(role_sepupu_callback, pattern='^role_sepupu$'))
    app.add_handler(CallbackQueryHandler(role_teman_sma_callback, pattern='^role_teman_sma$'))
    app.add_handler(CallbackQueryHandler(role_mantan_callback, pattern='^role_mantan$'))
    app.add_handler(CallbackQueryHandler(end_callback, pattern='^end_'))
    app.add_handler(CallbackQueryHandler(close_callback, pattern='^close_'))
    app.add_handler(CallbackQueryHandler(jadipacar_callback, pattern='^jadipacar_'))
    app.add_handler(CallbackQueryHandler(break_callback, pattern='^break_'))
    app.add_handler(CallbackQueryHandler(breakup_callback, pattern='^breakup_'))
    app.add_handler(CallbackQueryHandler(fwb_callback, pattern='^fwb_'))
    app.add_handler(CallbackQueryHandler(threesome_menu_callback, pattern='^threesome_menu$'))
    
    # V2 Callbacks (placeholder, akan di-override di main.py)
    if V2_AVAILABLE:
        app.add_handler(CallbackQueryHandler(lambda u,c: None, pattern='^pdkt_'))
        app.add_handler(CallbackQueryHandler(lambda u,c: None, pattern='^stoppdkt_'))
        app.add_handler(CallbackQueryHandler(lambda u,c: None, pattern='^fwb_'))
    
    # =========================================================================
    # ERROR HANDLER
    # =========================================================================
    app.add_error_handler(error_handler)
    
    # Log jumlah handlers
    handler_count = sum(len(h) for h in app.handlers.values())
    logger.info(f"✅ All handlers registered: {handler_count} handlers")
    
    return app


def setup_v2_handlers(app: Application, commands_v2, handlers_v2, callbacks_v2):
    """
    Setup V2 handlers setelah dependencies tersedia
    Dipanggil dari main.py setelah inisialisasi komponen V2
    """
    if not commands_v2 or not handlers_v2 or not callbacks_v2:
        logger.warning("⚠️ V2 handlers not setup: missing dependencies")
        return
    
    logger.info("🔄 Setting up V2 handlers with real implementations...")
    
    # ===== HAPUS HANDLER LAMA =====
    # Hapus semua handler yang ada (cara simple: buat baru)
    # Tapi karena kita tidak bisa hapus, kita akan override dengan yang baru
    
    # ===== PDKT COMMANDS =====
    app.add_handler(CommandHandler("pdkt", commands_v2.cmd_pdkt))
    app.add_handler(CommandHandler("pdktrandom", commands_v2.cmd_pdktrandom))
    app.add_handler(CommandHandler("pdktlist", commands_v2.cmd_pdktlist))
    app.add_handler(CommandHandler("pdktdetail", commands_v2.cmd_pdktdetail))
    app.add_handler(CommandHandler("pdktwho", commands_v2.cmd_pdktwho))
    app.add_handler(CommandHandler("pausepdkt", commands_v2.cmd_pausepdkt))
    app.add_handler(CommandHandler("resumepdkt", commands_v2.cmd_resumepdkt))
    app.add_handler(CommandHandler("stoppdkt", commands_v2.cmd_stoppdkt))
    
    # ===== PROGRESS COMMANDS =====
    if hasattr(commands_v2, 'cmd_progress'):
        app.add_handler(CommandHandler("progress", commands_v2.cmd_progress))
        app.add_handler(CommandHandler("pdktstatus", commands_v2.cmd_progress))
    
    # ===== MANTAN COMMANDS =====
    app.add_handler(CommandHandler("mantanlist", commands_v2.cmd_mantanlist))
    app.add_handler(CommandHandler("mantan", commands_v2.cmd_mantan))
    app.add_handler(CommandHandler("fwbrequest", commands_v2.cmd_fwbrequest))
    
    # ===== FWB COMMANDS =====
    app.add_handler(CommandHandler("fwblist", commands_v2.cmd_fwblist))
    app.add_handler(CommandHandler("fwb pause", commands_v2.cmd_fwb_pause))
    app.add_handler(CommandHandler("fwb resume", commands_v2.cmd_fwb_resume))
    app.add_handler(CommandHandler("fwb end", commands_v2.cmd_fwb_end))
    
    # ===== HTS COMMANDS =====
    app.add_handler(CommandHandler("htslist", commands_v2.cmd_htslist))
    
    # ===== MEMORY COMMANDS =====
    if hasattr(commands_v2, 'cmd_memory'):
        app.add_handler(CommandHandler("memory", commands_v2.cmd_memory))
    if hasattr(commands_v2, 'cmd_flashback'):
        app.add_handler(CommandHandler("flashback", commands_v2.cmd_flashback))
    
    # ===== PATTERN HANDLERS =====
    app.add_handler(MessageHandler(filters.Regex(r'^/fwb-\d+$'), commands_v2.cmd_fwb_call))
    app.add_handler(MessageHandler(filters.Regex(r'^/hts-\d+$'), commands_v2.cmd_hts_call))
    
    # ===== V2 CALLBACKS =====
    app.add_handler(CallbackQueryHandler(
        callbacks_v2.handle_callback, 
        pattern='^pdkt_'
    ))
    app.add_handler(CallbackQueryHandler(
        callbacks_v2.handle_callback,
        pattern='^stoppdkt_'
    ))
    app.add_handler(CallbackQueryHandler(
        callbacks_v2.handle_callback,
        pattern='^fwb_'
    ))
    
    logger.info("✅ V2 handlers setup complete")


# =============================================================================
# EXPORT
# =============================================================================
__all__ = ['create_application', 'setup_v2_handlers', 'BotStates']
