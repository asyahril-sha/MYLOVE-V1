#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - BOT PACKAGE INIT
=============================================================================
Inisialisasi package bot dan export semua komponen
"""

from .application import BotApplication
from .commands import *
from .handlers import *
from .webhook import WebhookManager, setup_webhook_with_fallback
from bot.application import create_application

__all__ = [
    # Application
    'BotApplication',
    
    # Webhook
    'WebhookManager',
    'setup_webhook_with_fallback',
    
    # Commands - Basic
    'start_command',
    'help_command',
    'status_command',
    'cancel_command',
    
    # Commands - Relationship
    'jadipacar_command',
    'break_command',
    'unbreak_command',
    'breakup_command',
    'fwb_command',
    
    # Commands - HTS/FWB
    'htslist_command',
    'fwblist_command',
    
    # Commands - Session
    'close_command',
    'sessions_command',
    
    # Commands - Public Area
    'explore_command',
    'locations_command',
    'risk_command',
    
    # Commands - Ranking
    'tophts_command',
    'myclimax_command',
    'climaxhistory_command',
    
    # Commands - Admin
    'stats_command',
    'db_stats_command',
    'backup_command',
    'recover_command',
    'debug_command',
    
    # Handlers
    'message_handler',
    'callback_handler',
    'hts_call_handler',
    'fwb_call_handler',
    'continue_handler',
]

# Version info
__version__ = "1.0.0"
__author__ = "MYLOVE Team"
__description__ = "MYLOVE Ultimate V1 - Telegram Bot Package"
