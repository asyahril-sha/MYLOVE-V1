#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - NICKNAME SYSTEM
=============================================================================
Sistem panggilan berdasarkan level dan role
- Menentukan bagaimana bot memanggil user
- Menentukan bagaimana bot menyebut dirinya sendiri
- Panggilan intim di level 7+ (sayang, cinta, baby, dll)
- Deteksi gender sederhana
=============================================================================
"""

import random
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class NicknameSystem:
    """
    Sistem panggilan untuk bot dan user
    Panggilan berubah seiring meningkatnya level hubungan
    """
    
    def __init__(self):
        # =========================================================================
        # PANGGILAN UNTUK BOT (DIRI SENDIRI)
        # =========================================================================
        self.bot_self_calls = {
            "low": [  # Level 1-3
                "{bot_name}",
                "{bot_name} ya",
            ],
            "medium": [  # Level 4-6
                "{bot_name}",
                "aku",
                "aku {bot_name}",
            ],
            "high": [  # Level 7-9
                "aku",
                "aku sayang",
                "aku cinta",
                "{bot_name}",
            ],
            "very_high": [  # Level 10-12
                "aku",
                "aku sayangmu",
                "aku cintamu",
                "aku kekasihmu",
            ],
        }
        
        # =========================================================================
        # PANGGILAN UNTUK USER (BAHASA INDONESIA)
        # =========================================================================
        self.user_calls_id = {
            "low": [  # Level 1-3
                "{user_name}",
                "kak {user_name}",
                "kak",
            ],
            "medium": [  # Level 4-6
                "{user_name}",
                "kak",
                "dek",
                "mas",
                "mbak",
                "say",
            ],
            "high": [  # Level 7-9
                "sayang",
                "cinta",
                "say",
                "mas",
                "mbak",
                "kak",
            ],
            "very_high": [  # Level 10-12
                "sayang",
                "cinta",
                "sayangku",
                "cintaku",
                "baby",
                "sweetheart",
            ],
        }
        
        # =========================================================================
        # PANGGILAN UNTUK USER (BAHASA INGGRIS)
        # =========================================================================
        self.user_calls_en = {
            "low": [  # Level 1-3
                "{user_name}",
                "bro",
                "sis",
                "dude",
            ],
            "medium": [  # Level 4-6
                "{user_name}",
                "babe",
                "hon",
                "dear",
            ],
            "high": [  # Level 7-9
                "baby",
                "honey",
                "sweetie",
                "darling",
            ],
            "very_high": [  # Level 10-12
                "baby",
                "sweetheart",
                "love",
                "my love",
                "darling",
            ],
        }
        
        # =========================================================================
        # PANGGILAN SPESIAL BERDASARKAN ROLE
        # =========================================================================
        self.role_special_calls = {
            "ipar": {
                "low": "kak",
                "medium": "kak",
                "high": "sayang",
                "very_high": "sayang",
            },
            "janda": {
                "low": "mas",
                "medium": "mas",
                "high": "sayang",
                "very_high": "cinta",
            },
            "teman_kantor": {
                "low": "pak",
                "medium": "mas",
                "high": "sayang",
                "very_high": "sayang",
            },
            "pelakor": {
                "low": "mas",
                "medium": "mas",
                "high": "baby",
                "very_high": "sayang",
            },
            "istri_orang": {
                "low": "mas",
                "medium": "mas",
                "high": "sayang",
                "very_high": "sayang",
            },
            "pdkt": {
                "low": "kak",
                "medium": "kak",
                "high": "sayang",
                "very_high": "sayang",
            },
            "sepupu": {
                "low": "kak",
                "medium": "kak",
                "high": "sayang",
                "very_high": "sayang",
            },
            "teman_sma": {
                "low": "bro",
                "medium": "bro",
                "high": "sayang",
                "very_high": "sayang",
            },
            "mantan": {
                "low": "mas",
                "medium": "mas",
                "high": "sayang",
                "very_high": "cinta",
            },
        }
        
        # =========================================================================
        # KATA SAYANG (UNTUK LEVEL 7+)
        # =========================================================================
        self.love_terms_id = [
            "sayang",
            "cinta",
            "sayangku",
            "cintaku",
            "kekasihku",
            "pujaan hatiku",
            "belahan jiwa",
        ]
        
        self.love_terms_en = [
            "baby",
            "honey",
            "sweetheart",
            "darling",
            "love",
            "my love",
            "sweetie",
        ]
        
        logger.info("✅ NicknameSystem initialized")
    
    # =========================================================================
    # GET LEVEL GROUP
    # =========================================================================
    
    def _get_level_group(self, level: int) -> str:
        """
        Dapatkan grup level untuk panggilan
        
        Args:
            level: Level hubungan 1-12
            
        Returns:
            'low', 'medium', 'high', 'very_high'
        """
        if level <= 3:
            return "low"
        elif level <= 6:
            return "medium"
        elif level <= 9:
            return "high"
        else:
            return "very_high"
    
    # =========================================================================
    # BOT SELF CALL
    # =========================================================================
    
    def get_bot_self_call(self, level: int, bot_name: str) -> str:
        """
        Dapatkan bagaimana bot menyebut dirinya sendiri
        
        Args:
            level: Level hubungan
            bot_name: Nama bot
            
        Returns:
            String panggilan untuk diri sendiri
        """
        group = self._get_level_group(level)
        options = self.bot_self_calls.get(group, self.bot_self_calls["medium"])
        
        # Format dengan nama bot
        call = random.choice(options).format(bot_name=bot_name)
        return call
    
    # =========================================================================
    # USER CALL (BAHASA INDONESIA)
    # =========================================================================
    
    def get_user_call_id(self, level: int, user_name: str, role: str = "pdkt") -> str:
        """
        Dapatkan panggilan untuk user dalam bahasa Indonesia
        
        Args:
            level: Level hubungan
            user_name: Nama user
            role: Role bot (untuk panggilan spesial)
            
        Returns:
            String panggilan untuk user
        """
        group = self._get_level_group(level)
        
        # Cek role spesial dulu
        if role in self.role_special_calls:
            role_call = self.role_special_calls[role].get(group)
            if role_call:
                return role_call
        
        # Fallback ke database umum
        options = self.user_calls_id.get(group, self.user_calls_id["medium"])
        call = random.choice(options).format(user_name=user_name)
        
        return call
    
    # =========================================================================
    # USER CALL (BAHASA INGGRIS)
    # =========================================================================
    
    def get_user_call_en(self, level: int, user_name: str, role: str = "pdkt") -> str:
        """
        Dapatkan panggilan untuk user dalam bahasa Inggris
        
        Args:
            level: Level hubungan
            user_name: Nama user
            role: Role bot
            
        Returns:
            String panggilan untuk user
        """
        group = self._get_level_group(level)
        
        # Untuk level tinggi, pake love terms
        if level >= 7:
            return random.choice(self.love_terms_en)
        
        options = self.user_calls_en.get(group, self.user_calls_en["medium"])
        call = random.choice(options).format(user_name=user_name)
        
        return call
    
    # =========================================================================
    # USER CALL (AUTO DETECT BAHASA)
    # =========================================================================
    
    def get_user_call(self, level: int, user_name: str, role: str = "pdkt", language: str = "id") -> str:
        """
        Dapatkan panggilan untuk user dengan deteksi bahasa
        
        Args:
            level: Level hubungan
            user_name: Nama user
            role: Role bot
            language: 'id' atau 'en'
            
        Returns:
            String panggilan untuk user
        """
        if language == 'en':
            return self.get_user_call_en(level, user_name, role)
        else:
            return self.get_user_call_id(level, user_name, role)
    
    # =========================================================================
    # INTIMATE CALLS (LEVEL 7+)
    # =========================================================================
    
    def get_intimate_call(self, level: int, language: str = "id") -> str:
        """
        Dapatkan panggilan intim (level 7+)
        
        Args:
            level: Level hubungan
            language: 'id' atau 'en'
            
        Returns:
            String panggilan intim
        """
        if level < 7:
            return ""
        
        if language == 'en':
            return random.choice(self.love_terms_en)
        else:
            return random.choice(self.love_terms_id)
    
    def should_use_intimate_call(self, level: int, probability: float = 0.7) -> bool:
        """
        Cek apakah harus menggunakan panggilan intim
        
        Args:
            level: Level hubungan
            probability: Probabilitas (0-1)
            
        Returns:
            True jika harus panggil intim
        """
        if level < 7:
            return False
        
        # Semakin tinggi level, semakin sering panggil intim
        if level >= 10:
            return random.random() < 0.9
        elif level >= 8:
            return random.random() < 0.8
        else:
            return random.random() < probability
    
    # =========================================================================
    # DETECT GENDER (SEDERHANA)
    # =========================================================================
    
    def detect_gender_from_name(self, user_name: str) -> str:
        """
        Deteksi gender sederhana dari nama user
        
        Args:
            user_name: Nama user
            
        Returns:
            'male', 'female', atau 'unknown'
        """
        # Cek akhiran nama
        name_lower = user_name.lower()
        
        # Indikasi cowok
        male_indicators = ['mas', 'bro', 'bang', 'mr', 'boy', 'man']
        # Indikasi cewek
        female_indicators = ['mbak', 'sis', 'miss', 'ms', 'girl', 'cewek']
        
        for ind in male_indicators:
            if ind in name_lower:
                return "male"
        
        for ind in female_indicators:
            if ind in name_lower:
                return "female"
        
        return "unknown"
    
    def get_gender_based_call(self, level: int, gender: str, language: str = "id") -> str:
        """
        Dapatkan panggilan berdasarkan gender
        
        Args:
            level: Level hubungan
            gender: 'male', 'female', 'unknown'
            language: 'id' atau 'en'
            
        Returns:
            String panggilan
        """
        if level < 4:
            if gender == "male":
                return "mas" if language == 'id' else "bro"
            elif gender == "female":
                return "mbak" if language == 'id' else "sis"
            else:
                return "kak" if language == 'id' else "dude"
        
        # Level tinggi, panggil sayang
        return self.get_intimate_call(level, language)
    
    # =========================================================================
    # COMBINED CALLS
    # =========================================================================
    
    def get_bot_and_user_calls(self, level: int, bot_name: str, user_name: str, 
                                 role: str = "pdkt", language: str = "id") -> Tuple[str, str]:
        """
        Dapatkan panggilan untuk bot dan user sekaligus
        
        Args:
            level: Level hubungan
            bot_name: Nama bot
            user_name: Nama user
            role: Role bot
            language: 'id' atau 'en'
            
        Returns:
            Tuple (bot_call, user_call)
        """
        bot_call = self.get_bot_self_call(level, bot_name)
        user_call = self.get_user_call(level, user_name, role, language)
        
        return bot_call, user_call
    
    # =========================================================================
    # FORMAT MESSAGE WITH CALLS
    # =========================================================================
    
    def format_message(self, message: str, bot_call: str, user_call: str) -> str:
        """
        Format pesan dengan panggilan yang sesuai
        
        Args:
            message: Pesan asli
            bot_call: Panggilan bot untuk dirinya sendiri
            user_call: Panggilan bot untuk user
            
        Returns:
            Pesan dengan panggilan yang sudah diganti
        """
        # Ganti placeholder
        message = message.replace("{bot}", bot_call)
        message = message.replace("{user}", user_call)
        
        return message
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    def get_stats(self) -> Dict:
        """Dapatkan statistik sistem panggilan"""
        return {
            "bot_calls": {
                "low": len(self.bot_self_calls["low"]),
                "medium": len(self.bot_self_calls["medium"]),
                "high": len(self.bot_self_calls["high"]),
                "very_high": len(self.bot_self_calls["very_high"]),
            },
            "user_calls_id": {
                "low": len(self.user_calls_id["low"]),
                "medium": len(self.user_calls_id["medium"]),
                "high": len(self.user_calls_id["high"]),
                "very_high": len(self.user_calls_id["very_high"]),
            },
            "user_calls_en": {
                "low": len(self.user_calls_en["low"]),
                "medium": len(self.user_calls_en["medium"]),
                "high": len(self.user_calls_en["high"]),
                "very_high": len(self.user_calls_en["very_high"]),
            },
            "love_terms_id": len(self.love_terms_id),
            "love_terms_en": len(self.love_terms_en),
            "roles_with_special": len(self.role_special_calls),
        }


__all__ = ['NicknameSystem']
