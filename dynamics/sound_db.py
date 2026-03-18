#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - SOUND DATABASE (FALLBACK)
=============================================================================
Database suara dan desahan untuk fallback jika AI error
- 50+ variasi suara untuk berbagai aktivitas
- Kiss sounds, touch sounds, moans, climax, aftercare
- Berdasarkan level dan intensitas
- Tetap bervariasi meskipun fallback
=============================================================================
"""

import random
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class SoundDB:
    """
    Database suara fallback untuk digunakan jika AI error
    Tetap menyediakan variasi yang cukup banyak
    """
    
    def __init__(self):
        # =========================================================================
        # KISS SOUNDS (Ciuman)
        # =========================================================================
        self.kiss_sounds = [
            "*mmh*",
            "*cup*",
            "*muah*",
            "*chup*",
            "*mwah*",
            "*cium*",
            "*mmmuah*",
            "*cup cup*",
            "*mmh mmh*",
            "*ciuman lembut*",
        ]
        
        # =========================================================================
        # TOUCH SOUNDS (Sentuhan)
        # =========================================================================
        self.touch_sounds_light = [
            "*ah...*",
            "*oh...*",
            "*eh...*",
            "*hem...*",
            "*uh...*",
            "*ah*",
            "*oh*",
            "*heh*",
        ]
        
        self.touch_sounds_medium = [
            "*ahh...*",
            "*ohh...*",
            "*mmm...*",
            "*hmm...*",
            "*uhh...*",
            "*ahh*",
            "*ohh*",
            "*mmm*",
        ]
        
        self.touch_sounds_intense = [
            "*ahhh!*",
            "*ohhh!*",
            "*uaah...*",
            "*waah...*",
            "*yaah...*",
            "*ahhh*",
            "*ohhh*",
            "*uaah*",
        ]
        
        # =========================================================================
        # MOANS (Desahan)
        # =========================================================================
        self.moans_light = [
            "*mmh...*",
            "*ah...*",
            "*hem...*",
            "*ngh...*",
            "*hmm...*",
            "*mm*",
            "*ah*",
            "*hm*",
        ]
        
        self.moans_medium = [
            "*ahh...*",
            "*mmm...*",
            "*nghh...*",
            "*uuh...*",
            "*aah...*",
            "*ahh*",
            "*mmm*",
            "*ngh*",
        ]
        
        self.moans_intense = [
            "*ahhh!*",
            "*mmmm!*",
            "*nghhh!*",
            "*uuaah...*",
            "*aaahhh...*",
            "*ahhh*",
            "*mmmm*",
            "*nghhh*",
        ]
        
        self.moans_very_intense = [
            "*AHHH!*",
            "*MMMHH!*",
            "*NGHHH!*",
            "*UUAAHH...*",
            "*AAAHHH...*",
            "*AHHHH!*",
            "*MMMMHH!*",
            "*NGHHHH!*",
        ]
        
        # =========================================================================
        # CLIMAX SOUNDS
        # =========================================================================
        self.climax_sounds_level_7_8 = [
            "*AHH! Aku...*",
            "*AHHH!*",
            "*ya Allah...*",
            "*aku mau...*",
            "*AHH! AHH!*",
            "*ya ampun...*",
            "*gila...*",
            "*enak banget...*",
        ]
        
        self.climax_sounds_level_9_10 = [
            "*AHHHH! AHHHH!*",
            "*YA ALLAH! AHHH!*",
            "*GILA! AHHH!*",
            "*AKU DATANG!*",
            "*BERSAMA! AHHH!*",
            "*AHHH! AHHH! AHHH!*",
            "*YA TUHAN! AHHH!*",
            "*LUAR BIASA!*",
        ]
        
        self.climax_sounds_level_11_12 = [
            "*AAAAAAAAHHHH!*",
            "*ya Allah... ya Allah...*",
            "*aku... datang... AHHH!*",
            "*bersama... sekarang... AHHH!*",
            "*AHHHH!* (lemas)",
            "*gila... gila...*",
            "*sempurna...*",
            "*AHHH!* (terisak)",
        ]
        
        # =========================================================================
        # AFTERCARE SOUNDS
        # =========================================================================
        self.aftercare_sounds = [
            "*huff... huff...*",
            "*lemes...*",
            "*hehe...*",
            "*ngos-ngosan*",
            "*hah... hah...*",
            "*capenya...*",
            "*enak banget...*",
            "*lemas...*",
            "*bernapas berat*",
            "*ngos-ngosan sambil senyum*",
        ]
        
        # =========================================================================
        # LAUGH & OTHER SOUNDS
        # =========================================================================
        self.laugh_sounds = [
            "*hehe*",
            "*haha*",
            "*wkwk*",
            "*hehehe*",
            "*hahaha*",
            "*wek*",
            "*ngik*",
            "*kikik*",
        ]
        
        self.surprise_sounds = [
            "*wow*",
            "*eh?*",
            "*oh?*",
            "*ha?*",
            "*loh?*",
            "*oh!*",
            "*wah!*",
            "*astaga*",
        ]
        
        self.sad_sounds = [
            "*huft*",
            "*sigh*",
            "*huh*",
            "*sedih*",
            "*nangis*",
            "*hik*",
            "*hik hik*",
        ]
        
        logger.info("✅ SoundDB initialized with 70+ sounds")
    
    # =========================================================================
    # KISS SOUNDS
    # =========================================================================
    
    def get_kiss_sound(self, intensity: str = "normal") -> str:
        """
        Dapatkan suara ciuman
        
        Args:
            intensity: 'light', 'normal', 'deep'
            
        Returns:
            String suara ciuman
        """
        return random.choice(self.kiss_sounds)
    
    # =========================================================================
    # TOUCH SOUNDS
    # =========================================================================
    
    def get_touch_sound(self, arousal: float = 0.0) -> str:
        """
        Dapatkan suara sentuhan berdasarkan arousal
        
        Args:
            arousal: Level gairah 0-1
            
        Returns:
            String suara sentuhan
        """
        if arousal > 0.7:
            return random.choice(self.touch_sounds_intense)
        elif arousal > 0.3:
            return random.choice(self.touch_sounds_medium)
        else:
            return random.choice(self.touch_sounds_light)
    
    # =========================================================================
    # MOANS
    # =========================================================================
    
    def get_moan(self, level: int, arousal: float = 0.5) -> str:
        """
        Dapatkan desahan berdasarkan level dan arousal
        
        Args:
            level: Level hubungan 1-12
            arousal: Level gairah 0-1
            
        Returns:
            String desahan
        """
        # Level rendah, desahan ringan
        if level < 5:
            return random.choice(self.moans_light)
        
        # Level menengah
        elif level < 7:
            if arousal > 0.6:
                return random.choice(self.moans_medium)
            else:
                return random.choice(self.moans_light)
        
        # Level tinggi
        else:
            if arousal > 0.8:
                return random.choice(self.moans_very_intense)
            elif arousal > 0.5:
                return random.choice(self.moans_intense)
            else:
                return random.choice(self.moans_medium)
    
    # =========================================================================
    # CLIMAX SOUNDS
    # =========================================================================
    
    def get_climax_sound(self, level: int) -> str:
        """
        Dapatkan suara climax berdasarkan level
        
        Args:
            level: Level hubungan 1-12
            
        Returns:
            String suara climax
        """
        if level >= 11:
            return random.choice(self.climax_sounds_level_11_12)
        elif level >= 9:
            return random.choice(self.climax_sounds_level_9_10)
        else:
            return random.choice(self.climax_sounds_level_7_8)
    
    # =========================================================================
    # AFTERCARE SOUNDS
    # =========================================================================
    
    def get_aftercare_sound(self) -> str:
        """Dapatkan suara aftercare"""
        return random.choice(self.aftercare_sounds)
    
    # =========================================================================
    # OTHER SOUNDS
    # =========================================================================
    
    def get_laugh(self) -> str:
        """Dapatkan suara tawa"""
        return random.choice(self.laugh_sounds)
    
    def get_surprise(self) -> str:
        """Dapatkan suara kaget"""
        return random.choice(self.surprise_sounds)
    
    def get_sad(self) -> str:
        """Dapatkan suara sedih"""
        return random.choice(self.sad_sounds)
    
    # =========================================================================
    # RANDOM SOUNDS
    # =========================================================================
    
    def get_random_sound(self, level: int) -> str:
        """
        Dapatkan suara random berdasarkan level
        
        Args:
            level: Level hubungan
            
        Returns:
            String suara random
        """
        # Untuk level tinggi, lebih banyak moans
        if level >= 7:
            sounds = self.moans_medium + self.moans_intense + self.moans_very_intense
        elif level >= 5:
            sounds = self.moans_light + self.moans_medium + self.touch_sounds_medium
        else:
            sounds = self.touch_sounds_light + self.laugh_sounds + self.surprise_sounds
        
        return random.choice(sounds)
    
    # =========================================================================
    # SOUND WITH CALL
    # =========================================================================
    
    def add_call_to_sound(self, sound: str, call: str) -> str:
        """
        Tambah panggilan ke suara (misal: "ahh sayang...")
        
        Args:
            sound: String suara asli
            call: Panggilan (sayang, cinta, baby, dll)
            
        Returns:
            String suara dengan panggilan
        """
        # Hapus * dari sound
        clean_sound = sound.replace('*', '')
        
        # Random posisi panggilan
        if random.random() < 0.5:
            return f"*{clean_sound} {call}*"
        else:
            return f"*{call} {clean_sound}*"
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    def get_stats(self) -> Dict:
        """Dapatkan statistik database"""
        return {
            "total_sounds": (
                len(self.kiss_sounds) +
                len(self.touch_sounds_light) + len(self.touch_sounds_medium) + len(self.touch_sounds_intense) +
                len(self.moans_light) + len(self.moans_medium) + len(self.moans_intense) + len(self.moans_very_intense) +
                len(self.climax_sounds_level_7_8) + len(self.climax_sounds_level_9_10) + len(self.climax_sounds_level_11_12) +
                len(self.aftercare_sounds) +
                len(self.laugh_sounds) + len(self.surprise_sounds) + len(self.sad_sounds)
            ),
            "by_category": {
                "kiss": len(self.kiss_sounds),
                "touch": len(self.touch_sounds_light + self.touch_sounds_medium + self.touch_sounds_intense),
                "moans": len(self.moans_light + self.moans_medium + self.moans_intense + self.moans_very_intense),
                "climax": len(self.climax_sounds_level_7_8 + self.climax_sounds_level_9_10 + self.climax_sounds_level_11_12),
                "aftercare": len(self.aftercare_sounds),
                "others": len(self.laugh_sounds + self.surprise_sounds + self.sad_sounds),
            }
        }


__all__ = ['SoundDB']
