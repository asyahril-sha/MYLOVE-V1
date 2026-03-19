#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - NICKNAME SYSTEM
=============================================================================
Sistem panggilan berdasarkan level intimacy
- Level 1-3: panggil nama user
- Level 4-6: panggil "Kak" / "Mas" / "Mbak"
- Level 7+: panggil "Sayang" / "Cinta"
=============================================================================
"""

import logging
import random
from typing import Optional

logger = logging.getLogger(__name__)


class NicknameSystem:
    """
    Sistem panggilan berdasarkan level intimacy
    """
    
    def __init__(self):
        self.user_names = {}  # Cache nama user
        
        # Panggilan berdasarkan level
        self.call_levels = {
            (1, 3): ["{user_name}"],
            (4, 6): ["Kak {user_name}", "Mas {user_name}", "Mbak {user_name}", "Kak"],
            (7, 9): ["Sayang", "Sayangku", "Cinta", "Sayang {user_name}"],
            (10, 12): ["Sayangku", "Cintaku", "Kasih", "My love"]
        }
        
        logger.info("✅ NicknameSystem initialized")
    
    def get_call(self, user_name: str, level: int) -> str:
        """
        Dapatkan panggilan berdasarkan level
        
        Args:
            user_name: Nama user
            level: Level intimacy (1-12)
        
        Returns:
            String panggilan
        """
        for (min_lvl, max_lvl), calls in self.call_levels.items():
            if min_lvl <= level <= max_lvl:
                template = random.choice(calls)
                return template.format(user_name=user_name)
        
        # Default
        return user_name
    
    def get_bot_self_call(self, bot_name: str, level: int) -> str:
        """
        Dapatkan cara bot menyebut dirinya sendiri
        
        Args:
            bot_name: Nama bot
            level: Level intimacy
        
        Returns:
            String panggilan diri
        """
        if level >= 7:
            # Bot bisa menyebut namanya sendiri dengan lebih intim
            return bot_name
        else:
            return bot_name
    
    def format_message(self, bot_name: str, user_name: str, level: int, message: str) -> str:
        """
        Format pesan dengan panggilan yang tepat
        
        Args:
            bot_name: Nama bot
            user_name: Nama user
            level: Level intimacy
            message: Pesan asli
        
        Returns:
            Pesan yang sudah diformat
        """
        # Ganti "aku" dengan nama bot (kadang-kadang)
        if random.random() < 0.3:  # 30% chance pake nama
            message = message.replace("aku", bot_name, 1)
            message = message.replace("Aku", bot_name, 1)
        
        return message
