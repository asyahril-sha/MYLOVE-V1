#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - BOT PACKAGE INIT
=============================================================================
Inisialisasi package bot dan export semua komponen
"""

# Import dari application
from .application import create_application

# Import dari commands
from .commands import *

# Import dari handlers
from .handlers import *

# Import dari callbacks (file baru)
from .callbacks import *

# Import dari webhook
from .webhook import setup_webhook_sync

__all__ = [
    # Application
    'create_application',
    
    # Webhook
    'setup_webhook_sync',
    
    # ===== COMMAND HANDLERS =====
    # Basic commands
    'start_command',
    'help_command',
    'status_command',
    'cancel_command',
    
    # Dominance commands
    'dominant_command',
    
    # Session commands
    'pause_command',
    'unpause_command',
    'close_command',
    'end_command',
    
    # Relationship commands
    'jadipacar_command',
    'break_command',
    'unbreak_command',
    'breakup_command',
    'fwb_command',
    
    # HTS/FWB commands
    'htslist_command',
    'fwblist_command',
    'hts_call_handler',
    'fwb_call_handler',
    'continue_handler',
    
    # Ranking commands
    'tophts_command',
    'myclimax_command',
    'climaxrank_command',
    'climaxhistory_command',
    
    # Public area commands
    'explore_command',
    'go_command',
    'positions_command',
    'risk_command',
    'mood_command',
    
    # Admin commands
    'admin_command',
    'stats_command',
    'db_stats_command',
    'list_users_command',
    'get_user_command',
    'force_reset_command',
    'backup_db_command',
    'vacuum_command',
    'memory_stats_command',
    'reload_command',
    
    # ===== MAIN HANDLERS =====
    'message_handler',
    'callback_handler',
    
    # ===== SPECIAL HANDLERS =====
    'hts_call_handler',
    'fwb_call_handler',
    'continue_handler',
    
    # ===== CALLBACKS =====
    'agree_18_callback',
    'start_pause_callback',
    'role_ipar_callback',
    'role_teman_kantor_callback',
    'role_janda_callback',
    'role_pelakor_callback',
    'role_istri_orang_callback',
    'role_pdkt_callback',
    'role_sepupu_callback',
    'role_teman_sma_callback',
    'role_mantan_callback',
    'end_callback',
    'close_callback',
    'jadipacar_callback',
    'break_callback',
    'breakup_callback',
    'fwb_callback',
]

# Version info
__version__ = "1.0.0"
__author__ = "MYLOVE Team"
__description__ = "MYLOVE Ultimate V1 - Telegram Bot Package"
