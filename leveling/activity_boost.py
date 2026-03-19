#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - ACTIVITY BOOST SYSTEM
=============================================================================
Memberikan boost untuk berbagai aktivitas dalam percakapan
- Sentuhan: 1.3x
- Kiss: 1.5x
- Intim: 2.0x
- Climax: 3.0x
- Boost mempengaruhi progress leveling
=============================================================================
"""

import logging
import random
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class BoostType(str, Enum):
    """Tipe-tipe boost"""
    NONE = "none"               # Tidak ada boost
    FLIRT = "flirt"             # Godaan ringan
    COMPLIMENT = "compliment"    # Pujian
    TOUCH = "touch"              # Sentuhan
    KISS = "kiss"                # Ciuman
    INTIM = "intim"              # Intim
    CLIMAX = "climax"            # Climax
    DEEP_TALK = "deep_talk"      # Ngobrol dalam
    CURHAT = "curhat"            # Curhat
    ROMANTIC = "romantic"        # Romantis
    PLAYFUL = "playful"          # Playful
    AFTERCARE = "aftercare"      # Aftercare


class ActivityBoost:
    """
    Memberikan boost untuk berbagai aktivitas
    - Setiap aktivitas punya multiplier berbeda
    - Boost mempengaruhi kecepatan progress leveling
    - Bisa dikombinasikan untuk efek lebih besar
    """
    
    def __init__(self):
        # Base multipliers untuk setiap aktivitas
        self.base_multipliers = {
            BoostType.NONE: 1.0,
            BoostType.FLIRT: 1.2,
            BoostType.COMPLIMENT: 1.1,
            BoostType.TOUCH: 1.3,
            BoostType.KISS: 1.5,
            BoostType.INTIM: 2.0,
            BoostType.CLIMAX: 3.0,
            BoostType.DEEP_TALK: 1.2,
            BoostType.CURHAT: 1.1,
            BoostType.ROMANTIC: 1.4,
            BoostType.PLAYFUL: 1.2,
            BoostType.AFTERCARE: 0.5  # Aftercare lebih lambat (untuk reset)
        }
        
        # Kombinasi boost (jika multiple activities)
        self.combination_bonus = {
            ('kiss', 'touch'): 1.2,           # Kiss + touch = extra 20%
            ('intim', 'kiss'): 1.3,            # Intim + kiss = extra 30%
            ('climax', 'intim'): 1.5,          # Climax + intim = extra 50%
            ('romantic', 'kiss'): 1.2,         # Romantic + kiss = extra 20%
            ('playful', 'flirt'): 1.1,          # Playful + flirt = extra 10%
        }
        
        # Keyword patterns untuk deteksi aktivitas
        self.activity_keywords = {
            BoostType.FLIRT: [
                'goda', 'rayu', 'flirt', 'cubit', 'jail', 
                'godain', 'merayu', 'menggoda'
            ],
            BoostType.COMPLIMENT: [
                'cantik', 'ganteng', 'keren', 'manis', 'seksi',
                'hot', 'beautiful', 'handsome', 'cool', 'sweet'
            ],
            BoostType.TOUCH: [
                'sentuh', 'pegang', 'elus', 'usap', 'raba',
                'menyentuh', 'memegang', 'mengelus', 'mengusap'
            ],
            BoostType.KISS: [
                'cium', 'kiss', 'kecup', 'cupang',
                'mencium', 'berciuman', 'kissing'
            ],
            BoostType.INTIM: [
                'intim', 'ml', 'tidur', 'bercinta', 'sex',
                'make love', 'berhubungan', 'masuk', 'dalam'
            ],
            BoostType.CLIMAX: [
                'climax', 'come', 'keluar', 'ejakulasi',
                'orgasme', 'puncak', 'nikmat'
            ],
            BoostType.DEEP_TALK: [
                'dalam', 'serius', 'berarti', 'hidup',
                'masa depan', 'tujuan', 'arti', 'makna'
            ],
            BoostType.CURHAT: [
                'curhat', 'cerita', 'masalah', 'keluh',
                'kesah', 'kisah', 'pengalaman'
            ],
            BoostType.ROMANTIC: [
                'romantis', 'sayang', 'cinta', 'love',
                'rindu', 'kangen', 'miss', 'sweet'
            ],
            BoostType.PLAYFUL: [
                'lucu', 'funny', 'haha', 'wkwk', 'ngakak',
                'joke', 'bercanda', 'kidding'
            ]
        }
        
        # Level threshold untuk berbagai aktivitas
        self.level_requirements = {
            BoostType.FLIRT: 1,
            BoostType.COMPLIMENT: 1,
            BoostType.TOUCH: 4,
            BoostType.KISS: 5,
            BoostType.INTIM: 7,
            BoostType.CLIMAX: 8,
            BoostType.DEEP_TALK: 3,
            BoostType.CURHAT: 2,
            BoostType.ROMANTIC: 3,
            BoostType.PLAYFUL: 1,
            BoostType.AFTERCARE: 12
        }
        
        logger.info("✅ ActivityBoost initialized")
    
    def detect_activity(self, message: str, current_level: int) -> List[BoostType]:
        """
        Deteksi aktivitas dari pesan user
        
        Args:
            message: Pesan user
            current_level: Level saat ini
            
        Returns:
            List aktivitas yang terdeteksi
        """
        message_lower = message.lower()
        detected = []
        
        for boost_type, keywords in self.activity_keywords.items():
            # Cek level requirement
            min_level = self.level_requirements.get(boost_type, 1)
            if current_level < min_level:
                continue
            
            for keyword in keywords:
                if keyword in message_lower:
                    detected.append(boost_type)
                    break
        
        # Jika tidak ada yang terdeteksi, return NONE
        if not detected:
            return [BoostType.NONE]
        
        return detected
    
    def calculate_boost(self, activities: List[BoostType], context: Dict = None) -> float:
        """
        Hitung total boost multiplier dari aktivitas
        
        Args:
            activities: List aktivitas
            context: Konteks tambahan (mood, dll)
            
        Returns:
            Total multiplier
        """
        if not activities:
            return 1.0
        
        # Hitung base dari aktivitas pertama
        main_activity = activities[0]
        multiplier = self.base_multipliers.get(main_activity, 1.0)
        
        # Cek kombinasi bonus
        if len(activities) >= 2:
            # Urutkan untuk konsistensi
            acts = sorted([a.value for a in activities[:2]])
            combo_key = tuple(acts)
            
            if combo_key in self.combination_bonus:
                multiplier *= self.combination_bonus[combo_key]
        
        # Bonus berdasarkan mood
        if context:
            mood = context.get('mood', 'netral')
            if mood == 'romantic' and BoostType.ROMANTIC in activities:
                multiplier *= 1.2
            elif mood == 'happy' and BoostType.PLAYFUL in activities:
                multiplier *= 1.1
            elif mood == 'excited' and BoostType.FLIRT in activities:
                multiplier *= 1.1
        
        # Random small variation (±5%)
        multiplier *= random.uniform(0.95, 1.05)
        
        return round(multiplier, 2)
    
    def get_boost_description(self, boost_type: BoostType) -> str:
        """
        Dapatkan deskripsi boost
        
        Args:
            boost_type: Tipe boost
            
        Returns:
            Deskripsi
        """
        descriptions = {
            BoostType.NONE: "Percakapan biasa",
            BoostType.FLIRT: "Godaan ringan (+20% progress)",
            BoostType.COMPLIMENT: "Pujian manis (+10% progress)",
            BoostType.TOUCH: "Sentuhan hangat (+30% progress)",
            BoostType.KISS: "Ciuman mesra (+50% progress)",
            BoostType.INTIM: "Keintiman (2x progress!)",
            BoostType.CLIMAX: "Climax! (3x progress!!!)",
            BoostType.DEEP_TALK: "Obrolan dalam (+20% progress)",
            BoostType.CURHAT: "Curhat hangat (+10% progress)",
            BoostType.ROMANTIC: "Momen romantis (+40% progress)",
            BoostType.PLAYFUL: "Suasana playful (+20% progress)",
            BoostType.AFTERCARE: "Aftercare (progress lebih lambat)"
        }
        return descriptions.get(boost_type, "Aktivitas spesial")
    
    def get_boost_emoji(self, boost_type: BoostType) -> str:
        """
        Dapatkan emoji untuk boost
        
        Args:
            boost_type: Tipe boost
            
        Returns:
            Emoji
        """
        emojis = {
            BoostType.NONE: "💬",
            BoostType.FLIRT: "😜",
            BoostType.COMPLIMENT: "💝",
            BoostType.TOUCH: "👆",
            BoostType.KISS: "💋",
            BoostType.INTIM: "🔥",
            BoostType.CLIMAX: "💦",
            BoostType.DEEP_TALK: "🤔",
            BoostType.CURHAT: "📖",
            BoostType.ROMANTIC: "🥰",
            BoostType.PLAYFUL: "😊",
            BoostType.AFTERCARE: "🤗"
        }
        return emojis.get(boost_type, "✨")
    
    def format_boost_message(self, activities: List[BoostType], multiplier: float) -> str:
        """
        Format pesan boost untuk ditampilkan
        
        Args:
            activities: List aktivitas
            multiplier: Total multiplier
            
        Returns:
            Pesan boost
        """
        if not activities or activities[0] == BoostType.NONE:
            return ""
        
        main = activities[0]
        emoji = self.get_boost_emoji(main)
        desc = self.get_boost_description(main)
        
        if multiplier > 2.0:
            intensity = "🔥 SANGAT INTENS! 🔥"
        elif multiplier > 1.5:
            intensity = "✨ LUAR BIASA! ✨"
        elif multiplier > 1.2:
            intensity = "⭐ MANTAP! ⭐"
        else:
            intensity = ""
        
        return f"{emoji} {desc} {intensity} (x{multiplier})"
    
    def get_available_activities(self, current_level: int) -> List[Dict]:
        """
        Dapatkan daftar aktivitas yang tersedia di level ini
        
        Args:
            current_level: Level saat ini
            
        Returns:
            List aktivitas dengan info
        """
        available = []
        
        for boost_type, min_level in self.level_requirements.items():
            if current_level >= min_level:
                available.append({
                    'type': boost_type.value,
                    'name': boost_type.value.replace('_', ' ').title(),
                    'multiplier': self.base_multipliers[boost_type],
                    'emoji': self.get_boost_emoji(boost_type),
                    'description': self.get_boost_description(boost_type)
                })
        
        return available
    
    def get_next_unlock(self, current_level: int) -> Optional[Dict]:
        """
        Dapatkan aktivitas yang akan terbuka di level berikutnya
        
        Args:
            current_level: Level saat ini
            
        Returns:
            Info aktivitas yang akan terbuka
        """
        next_unlock = None
        next_level = current_level + 1
        
        for boost_type, min_level in self.level_requirements.items():
            if min_level == next_level:
                next_unlock = {
                    'type': boost_type.value,
                    'name': boost_type.value.replace('_', ' ').title(),
                    'multiplier': self.base_multipliers[boost_type],
                    'emoji': self.get_boost_emoji(boost_type),
                    'description': self.get_boost_description(boost_type),
                    'unlock_at': next_level
                }
                break
        
        return next_unlock
    
    def combine_activities(self, activities: List[BoostType]) -> BoostType:
        """
        Gabungkan multiple activities menjadi satu tipe utama
        
        Args:
            activities: List aktivitas
            
        Returns:
            Tipe utama (prioritas tertinggi)
        """
        # Urutan prioritas (tertinggi ke terendah)
        priority = [
            BoostType.CLIMAX,
            BoostType.INTIM,
            BoostType.KISS,
            BoostType.TOUCH,
            BoostType.ROMANTIC,
            BoostType.DEEP_TALK,
            BoostType.CURHAT,
            BoostType.FLIRT,
            BoostType.COMPLIMENT,
            BoostType.PLAYFUL
        ]
        
        for p in priority:
            if p in activities:
                return p
        
        return BoostType.NONE
    
    def should_show_boost(self, multiplier: float) -> bool:
        """
        Cek apakah perlu menampilkan pesan boost
        
        Args:
            multiplier: Total multiplier
            
        Returns:
            True jika multiplier > 1.0
        """
        return multiplier > 1.0


__all__ = ['ActivityBoost', 'BoostType']
