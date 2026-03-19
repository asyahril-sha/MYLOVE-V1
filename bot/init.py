#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - BOT PACKAGE INIT
=============================================================================
Inisialisasi package bot
- Tetap mempertahankan semua export V1
- Menambah export untuk V2
=============================================================================
"""

# =============================================================================
# EXPORT V1 (TETAP)
# =============================================================================
from .application import create_application
from .commands import *
from .handlers import *
from .callbacks import *
from .webhook import setup_webhook_sync

# =============================================================================
# EXPORT V2 (BARU)
# =============================================================================
from .commands_v2 import CommandsV2
from .handlers_v2 import HandlersV2

__all__ = [
    # V1
    'create_application',
    'setup_webhook_sync',
    'start_command', 'help_command', 'status_command', 'cancel_command',
    'dominant_command', 'pause_command', 'unpause_command',
    'close_command', 'end_command', 'jadipacar_command',
    'break_command', 'unbreak_command', 'breakup_command', 'fwb_command',
    'htslist_command', 'fwblist_command', 'hts_call_handler',
    'fwb_call_handler', 'continue_handler', 'tophts_command',
    'myclimax_command', 'climaxrank_command', 'climaxhistory_command',
    'explore_command', 'go_command', 'positions_command', 'risk_command',
    'mood_command', 'admin_command', 'stats_command', 'db_stats_command',
    'list_users_command', 'get_user_command', 'force_reset_command',
    'backup_db_command', 'vacuum_command', 'memory_stats_command',
    'reload_command', 'message_handler', 'callback_handler',
    'agree_18_callback', 'start_pause_callback',
    'role_ipar_callback', 'role_teman_kantor_callback',
    'role_janda_callback', 'role_pelakor_callback',
    'role_istri_orang_callback', 'role_pdkt_callback',
    'role_sepupu_callback', 'role_teman_sma_callback',
    'role_mantan_callback', 'end_callback', 'close_callback',
    'jadipacar_callback', 'break_callback', 'breakup_callback',
    'fwb_callback',
    
    # V2
    'CommandsV2',
    'HandlersV2',
]

__version__ = "2.0.0"
