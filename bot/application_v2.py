#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - APPLICATION FACTORY V2
=============================================================================
Berdasarkan V1 dengan penambahan:
- Handler untuk command V2 (PDKT, Mantan, FWB, HTS)
- Integrasi dengan semua sistem V2
- Conversation states untuk V2
- Callback handlers untuk V2
=============================================================================
"""

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
from database.models_v2 import Constants

# =============================================================================
# IMPORT HANDLERS V1 (TETAP)
# =============================================================================
from bot.handlers import (
    start_command, help_command, status_command, cancel_command,
    dominant_command, pause_command, unpause_command,
    close_command, end_command, jadipacar_command,
    break_command, unbreak_command, breakup_command, fwb_command,
    htslist_command, fwblist_command, hts_call_handler,
    fwb_call_handler, tophts_command, myclimax_command,
    climaxrank_command, climaxhistory_command, explore_command,
    go_command, positions_command, risk_command, mood_command,
    admin_command, stats_command, db_stats_command, list_users_command,
    get_user_command, force_reset_command, backup_db_command,
    vacuum_command, memory_stats_command, reload_command,
    message_handler,
)

from bot.callbacks import (
    agree_18_callback, start_pause_callback,
    role_ipar_callback, role_teman_kantor_callback,
    role_janda_callback, role_pelakor_callback,
    role_istri_orang_callback, role_pdkt_callback,
    role_sepupu_callback, role_teman_sma_callback,
    role_mantan_callback, end_callback, close_callback,
    jadipacar_callback, break_callback, breakup_callback,
    fwb_callback,
)

from bot.commands import error_handler

# =============================================================================
# IMPORT HANDLERS V2 (BARU)
# =============================================================================
from bot.commands_v2 import CommandsV2
from bot.handlers_v2 import HandlersV2


# =============================================================================
# BOT STATES (V1 + V2)
# =============================================================================
class BotStates:
    """States for conversation handlers (V1 + V2)"""
    
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


def create_application_v2(commands_v2: CommandsV2, handlers_v2: HandlersV2) -> Application:
    """
    Create and configure telegram application V2
    Menggabungkan handler V1 dan V2
    
    Args:
        commands_v2: Instance CommandsV2
        handlers_v2: Instance HandlersV2
        
    Returns:
        Application instance
    """
    
    logger.info("🔧 Creating PTB application V2...")
    
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
    SELECTING_PDKT = getattr(Constants, 'SELECTING_PDKT', BotStates.SELECTING_PDKT)
    SELECTING_FWB = getattr(Constants, 'SELECTING_FWB', BotStates.SELECTING_FWB)
    
    logger.info(f"  • Using SELECTING_ROLE = {SELECTING_ROLE}")
    logger.info(f"  • Using SELECTING_PDKT = {SELECTING_PDKT}")
    
    # =========================================================================
    # V1 CONVERSATION HANDLERS (TETAP)
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
    # V2 CONVERSATION HANDLERS (BARU)
    # =========================================================================
    
    # PDKT conversation
    pdkt_conv = ConversationHandler(
        entry_points=[CommandHandler('pdkt', commands_v2.cmd_pdkt)],
        states={
            SELECTING_PDKT: [
                CallbackQueryHandler(handlers_v2.callback_handler, pattern='^pdkt_'),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_command)],
        name="pdkt_conversation",
        persistent=False,
        per_user=True,
        per_chat=True,
        per_message=False
    )
    
    # FWB conversation
    fwb_conv = ConversationHandler(
        entry_points=[CommandHandler('fwbrequest', commands_v2.cmd_fwbrequest)],
        states={
            SELECTING_FWB: [
                CallbackQueryHandler(handlers_v2.callback_handler, pattern='^fwb_'),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_command)],
        name="fwb_conversation",
        persistent=False,
        per_user=True,
        per_chat=True,
        per_message=False
    )
    
    # =========================================================================
    # ADD ALL HANDLERS
    # =========================================================================
    
    # ===== V1 CONVERSATION HANDLERS =====
    app.add_handler(start_conv)
    app.add_handler(end_conv)
    app.add_handler(close_conv)
    app.add_handler(rel_conv)
    
    # ===== V2 CONVERSATION HANDLERS =====
    app.add_handler(pdkt_conv)
    app.add_handler(fwb_conv)
    
    # ===== V1 COMMAND HANDLERS =====
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("cancel", cancel_command))
    app.add_handler(CommandHandler("dominant", dominant_command))
    app.add_handler(CommandHandler("pause", pause_command))
    app.add_handler(CommandHandler("unpause", unpause_command))
    app.add_handler(CommandHandler("close", close_command))
    app.add_handler(CommandHandler("end", end_command))
    app.add_handler(CommandHandler("jadipacar", jadipacar_command))
    app.add_handler(CommandHandler("break", break_command))
    app.add_handler(CommandHandler("unbreak", unbreak_command))
    app.add_handler(CommandHandler("breakup", breakup_command))
    app.add_handler(CommandHandler("fwb", fwb_command))
    app.add_handler(CommandHandler("htslist", htslist_command))
    app.add_handler(CommandHandler("fwblist", fwblist_command))
    app.add_handler(CommandHandler("tophts", tophts_command))
    app.add_handler(CommandHandler("myclimax", myclimax_command))
    app.add_handler(CommandHandler("climaxrank", climaxrank_command))
    app.add_handler(CommandHandler("climaxhistory", climaxhistory_command))
    app.add_handler(CommandHandler("explore", explore_command))
    app.add_handler(CommandHandler("go", go_command))
    app.add_handler(CommandHandler("positions", positions_command))
    app.add_handler(CommandHandler("risk", risk_command))
    app.add_handler(CommandHandler("mood", mood_command))
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
    app.add_handler(CommandHandler("reset", force_reset_command))  # Hidden
    
    # ===== V2 COMMAND HANDLERS =====
    # PDKT Commands
    app.add_handler(CommandHandler("pdkt", commands_v2.cmd_pdkt))
    app.add_handler(CommandHandler("pdktrandom", commands_v2.cmd_pdktrandom))
    app.add_handler(CommandHandler("pdktlist", commands_v2.cmd_pdktlist))
    app.add_handler(CommandHandler("pdktdetail", commands_v2.cmd_pdktdetail))
    app.add_handler(CommandHandler("pdktwho", commands_v2.cmd_pdktwho))
    app.add_handler(CommandHandler("pausepdkt", commands_v2.cmd_pausepdkt))
    app.add_handler(CommandHandler("resumepdkt", commands_v2.cmd_resumepdkt))
    app.add_handler(CommandHandler("stoppdkt", commands_v2.cmd_stoppdkt))
    
    # Mantan Commands
    app.add_handler(CommandHandler("mantanlist", commands_v2.cmd_mantanlist))
    app.add_handler(CommandHandler("mantan", commands_v2.cmd_mantan))
    app.add_handler(CommandHandler("fwbrequest", commands_v2.cmd_fwbrequest))
    
    # FWB Commands
    app.add_handler(CommandHandler("fwblist", commands_v2.cmd_fwblist))
    app.add_handler(CommandHandler("fwb pause", commands_v2.cmd_fwb_pause))
    app.add_handler(CommandHandler("fwb resume", commands_v2.cmd_fwb_resume))
    app.add_handler(CommandHandler("fwb end", commands_v2.cmd_fwb_end))
    
    # HTS Commands
    app.add_handler(CommandHandler("htslist", commands_v2.cmd_htslist))
    
    # Memory Commands
    app.add_handler(CommandHandler("memory", commands_v2.cmd_memory))
    app.add_handler(CommandHandler("flashback", commands_v2.cmd_flashback))
    
    # ===== PATTERN HANDLERS =====
    # V1 Patterns
    app.add_handler(MessageHandler(filters.Regex(r'^/hts-'), hts_call_handler))
    app.add_handler(MessageHandler(filters.Regex(r'^/fwb-'), fwb_call_handler))
    
    # V2 Patterns
    app.add_handler(MessageHandler(filters.Regex(r'^/fwb-\d+$'), commands_v2.cmd_fwb_call))
    app.add_handler(MessageHandler(filters.Regex(r'^/hts-\d+$'), commands_v2.cmd_hts_call))
    
    # ===== MESSAGE HANDLER =====
    # V1 Message Handler (untuk NON-PDKT)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # V2 Message Handler (akan dipanggil dari V1 handler yang sudah di-modify)
    # Atau bisa diganti total dengan V2 handler
    
    # ===== CALLBACK HANDLERS =====
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
    
    # V2 Callbacks
    app.add_handler(CallbackQueryHandler(
        handlers_v2.callback_handler, 
        pattern='^pdkt_'
    ))
    app.add_handler(CallbackQueryHandler(
        handlers_v2.callback_handler,
        pattern='^stoppdkt_'
    ))
    app.add_handler(CallbackQueryHandler(
        handlers_v2.callback_handler,
        pattern='^fwb_'
    ))
    
    # ===== ERROR HANDLER =====
    app.add_error_handler(error_handler)
    
    # Log jumlah handlers
    handler_count = sum(len(h) for h in app.handlers.values())
    logger.info(f"✅ All handlers registered (V1 + V2): {handler_count} handlers")
    
    return app


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_application(commands_v2: CommandsV2 = None, handlers_v2: HandlersV2 = None) -> Application:
    """
    Factory function untuk membuat application (kompatibel dengan V1)
    
    Jika commands_v2 dan handlers_v2 diberikan, akan membuat V2 application.
    Jika tidak, akan membuat V1 application (untuk backward compatibility).
    """
    if commands_v2 and handlers_v2:
        return create_application_v2(commands_v2, handlers_v2)
    else:
        # Fallback ke V1
        from bot.application import create_application as create_v1
        return create_v1()


__all__ = ['create_application', 'create_application_v2', 'BotStates']
