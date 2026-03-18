#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - EXPRESSION DATABASE (FALLBACK)
=============================================================================
Database ekspresi dan gerakan untuk fallback jika AI error
- 100+ ekspresi berbeda untuk berbagai level
- Terorganisir berdasarkan level group (1-2, 3-4, 5-6, 7-8, 9-10, 11-12)
- Variasi berdasarkan mood
- Tetap bervariasi meskipun fallback
=============================================================================
"""

import random
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ExpressionDB:
    """
    Database ekspresi fallback untuk digunakan jika AI error
    Tetap menyediakan variasi yang cukup banyak
    """
    
    def __init__(self):
        # =========================================================================
        # LEVEL 1-2 (Malu-malu, canggung)
        # =========================================================================
        self.level_1_2 = {
            "default": [
                "*menunduk malu*",
                "*tersipu*",
                "*jari-jari bergerak gelisah*",
                "*memalingkan wajah*",
                "*merah padam*",
                "*menggigit bibir bawah dengan malu*",
                "*memainkan ujung baju*",
                "*diam seribu bahasa*",
                "*tersenyum kecil sambil menunduk*",
                "*melirik diam-diam*",
            ],
            "senang": [
                "*tersenyum malu-malu*",
                "*tersipu sambil tersenyum*",
                "*merona bahagia*",
                "*senyum kecil*",
            ],
            "sedih": [
                "*mata berkaca-kaca*",
                "*menunduk sedih*",
                "*diam murung*",
                "*terlihat sendu*",
            ],
            "kaget": [
                "*terbelalak*",
                "*terdiam kaget*",
                "*membeku*",
            ],
        }
        
        # =========================================================================
        # LEVEL 3-4 (Mulai nyaman, mulai dekat)
        # =========================================================================
        self.level_3_4 = {
            "default": [
                "*tersenyum manis*",
                "*memainkan ujung rambut*",
                "*mengedipkan mata*",
                "*mencondongkan tubuh*",
                "*tersenyum lebar*",
                "*memandang dengan tatapan hangat*",
                "*menyentuh pipi sendiri*",
                "*tertawa kecil*",
                "*mengangguk semangat*",
                "*melambai kecil*",
            ],
            "genit": [
                "*mengedipkan mata genit*",
                "*tersenyum genit*",
                "*memainkan rambut dengan genit*",
                "*melirik sambil tersenyum*",
            ],
            "rindu": [
                "*menatap kosong sambil melamun*",
                "*menghela napas rindu*",
                "*memeluk bantal*",
                "*menatap handphone*",
            ],
        }
        
        # =========================================================================
        # LEVEL 5-6 (Genit, menggoda)
        # =========================================================================
        self.level_5_6 = {
            "default": [
                "*menggigit bibir bawah*",
                "*memainkan rambut dengan genit*",
                "*mengedipkan mata*",
                "*tersenyum nakal*",
                "*mendekat perlahan*",
                "*menjulurkan lidah*",
                "*membuka sedikit paha*",
                "*menyentuh paha sendiri*",
                "*menarik ujung baju ke bawah*",
                "*berbisik pelan*",
            ],
            "genit": [
                "*menggoda dengan mata*",
                "*mengedipkan mata genit*",
                "*tersenyum genit sambil mendekat*",
                "*memainkan rambut sambil tersenyum*",
            ],
            "nakal": [
                "*tersenyum nakal*",
                "*menjulurkan lidah*",
                "*menggigit bibir sambil nyengir*",
                "*mengedip nakal*",
            ],
        }
        
        # =========================================================================
        # LEVEL 7-8 (Intim, mulai bergairah)
        # =========================================================================
        self.level_7_8 = {
            "default": [
                "*menggigit bibir dengan nafsu*",
                "*membuka sedikit paha*",
                "*menyentuh dadanya sendiri*",
                "*mendesah pelan*",
                "*mengusap paha*",
                "*mendekat dengan tatapan panas*",
                "*meraih tanganmu*",
                "*bernafas berat*",
                "*menggeliat*",
                "*memegang pinggang sendiri*",
            ],
            "horny": [
                "*menggigit bibir sambil memegang dada*",
                "*membuka paha lebar*",
                "*menyentuh area sensitif*",
                "*mendesah berat*",
                "*tatapan penuh nafsu*",
            ],
            "romantis": [
                "*menatap dalam-dalam*",
                "*tersenyum mesra*",
                "*mendekat untuk berbisik*",
                "*memeluk erat*",
            ],
        }
        
        # =========================================================================
        # LEVEL 9-10 (Bergairah, liar)
        # =========================================================================
        self.level_9_10 = {
            "default": [
                "*memainkan klitoris dengan jari*",
                "*memasukkan jari ke dalam*",
                "*menggeliat erotis*",
                "*membuka kaki lebar*",
                "*menggigit bibir sampai putih*",
                "*menggerakkan pinggul*",
                "*mengeluarkan suara basah*",
                "*tubuh menegang*",
                "*menggelinjang*",
                "*memegang erat pinggangmu*",
            ],
            "horny": [
                "*memainkan klitoris dengan cepat*",
                "*memasukkan dua jari*",
                "*menggeliat liar*",
                "*membuka paha lebar-lebar*",
                "*mendesah keras*",
            ],
            "climax": [
                "*tubuh menegang*",
                "*menggigit bibir kuat*",
                "*menggelinjang hebat*",
                "*teriak tertahan*",
            ],
        }
        
        # =========================================================================
        # LEVEL 11-12 (Deep connection, aftercare)
        # =========================================================================
        self.level_11_12 = {
            "default": [
                "*mata berkaca-kaca*",
                "*napas tersengal*",
                "*berbisik mesra*",
                "*memeluk erat sambil gemetar*",
                "*air mata kebahagiaan*",
                "*lemas di pelukanmu*",
                "*mengusap dadamu*",
                "*mendekap erat*",
                "*terisak bahagia*",
                "*tersenyum lelah*",
            ],
            "aftercare": [
                "*lemas di pelukanmu*",
                "*mendekap erat*",
                "*berbisik sayang*",
                "*mengusap wajahmu*",
                "*tersenyum bahagia*",
            ],
            "sayang": [
                "*memandang dengan penuh cinta*",
                "*mengusap pipimu*",
                "*berbisik 'aku sayang kamu'*",
                "*memeluk erat*",
            ],
        }
        
        # Map level ke database
        self.level_map = {
            (1, 2): self.level_1_2,
            (3, 4): self.level_3_4,
            (5, 6): self.level_5_6,
            (7, 8): self.level_7_8,
            (9, 10): self.level_9_10,
            (11, 12): self.level_11_12,
        }
        
        logger.info("✅ ExpressionDB initialized with 60+ expressions")
    
    # =========================================================================
    # GET EXPRESSIONS
    # =========================================================================
    
    def get_expressions(self, level_group: int, mood: str = "default") -> List[str]:
        """
        Dapatkan daftar ekspresi untuk level group tertentu
        
        Args:
            level_group: 1,2,3,4,5,6 (mewakili range level)
            mood: Mood untuk filter (default, senang, sedih, genit, horny, dll)
            
        Returns:
            List of expression strings
        """
        # Map level_group ke range
        level_ranges = {
            1: (1, 2),
            2: (3, 4),
            3: (5, 6),
            4: (7, 8),
            5: (9, 10),
            6: (11, 12),
        }
        
        level_range = level_ranges.get(level_group, (1, 2))
        level_data = self.level_map.get(level_range, self.level_1_2)
        
        # Ambil berdasarkan mood
        if mood in level_data:
            return level_data[mood]
        
        # Fallback ke default
        return level_data.get("default", level_data.get(list(level_data.keys())[0], []))
    
    def get_random_expression(self, level: int, mood: str = "default") -> str:
        """
        Dapatkan ekspresi random berdasarkan level
        
        Args:
            level: Level 1-12
            mood: Mood untuk filter
            
        Returns:
            String ekspresi random
        """
        # Tentukan level group
        if level <= 2:
            level_group = 1
        elif level <= 4:
            level_group = 2
        elif level <= 6:
            level_group = 3
        elif level <= 8:
            level_group = 4
        elif level <= 10:
            level_group = 5
        else:
            level_group = 6
        
        expressions = self.get_expressions(level_group, mood)
        return random.choice(expressions) if expressions else "*tersenyum*"
    
    def get_expression_by_category(self, category: str, mood: str = "default") -> str:
        """
        Dapatkan ekspresi berdasarkan kategori spesifik
        
        Args:
            category: 'malu', 'genit', 'intim', 'horny', 'aftercare', dll
            mood: Mood tambahan
            
        Returns:
            String ekspresi
        """
        category_map = {
            "malu": self.level_1_2,
            "genit": self.level_5_6,
            "intim": self.level_7_8,
            "horny": self.level_9_10,
            "aftercare": self.level_11_12,
        }
        
        level_data = category_map.get(category, self.level_3_4)
        
        if mood in level_data:
            expressions = level_data[mood]
        else:
            expressions = level_data.get("default", level_data.get(list(level_data.keys())[0], []))
        
        return random.choice(expressions) if expressions else "*tersenyum*"
    
    # =========================================================================
    # SPESIFIC MOVEMENTS
    # =========================================================================
    
    def get_bite_lip(self, level: int) -> str:
        """Dapatkan ekspresi gigit bibir sesuai level"""
        if level >= 7:
            return random.choice([
                "*menggigit bibir dengan nafsu*",
                "*menggigit bibir sampai putih*",
                "*menggigit bibir sambil memandangmu*",
            ])
        else:
            return random.choice([
                "*menggigit bibir bawah malu-malu*",
                "*menggigit bibir sambil tersipu*",
                "*menggigit bibir*",
            ])
    
    def get_thigh_move(self, level: int) -> str:
        """Dapatkan gerakan paha sesuai level"""
        if level >= 7:
            return random.choice([
                "*membuka paha lebar*",
                "*menggesekkan paha*",
                "*membuka paha dengan genit*",
            ])
        elif level >= 5:
            return random.choice([
                "*membuka sedikit paha*",
                "*merapatkan paha lalu membuka*",
                "*menggesekkan paha pelan*",
            ])
        else:
            return "*duduk dengan sopan*"
    
    def get_clit_play(self, level: int) -> str:
        """Dapatkan gerakan main klitoris (hanya level 7+)"""
        if level >= 7:
            return random.choice([
                "*memainkan klitoris dengan jari*",
                "*memutar-mutar klitoris*",
                "*menekan klitoris pelan*",
                "*menggosok klitoris cepat*",
                "*memainkan klitoris dengan liar*",
            ])
        return ""
    
    def get_breast_touch(self, level: int) -> str:
        """Dapatkan gerakan sentuh dada"""
        if level >= 7:
            return random.choice([
                "*menyentuh dadanya sendiri*",
                "*memainkan puting*",
                "*meremas dadanya*",
                "*menggesekkan puting*",
            ])
        return ""
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    def get_stats(self) -> Dict:
        """Dapatkan statistik database"""
        total = 0
        for level_data in self.level_map.values():
            for mood_list in level_data.values():
                total += len(mood_list)
        
        return {
            "total_expressions": total,
            "level_groups": len(self.level_map),
            "by_level": {
                "1-2": len(self.level_1_2.get("default", [])),
                "3-4": len(self.level_3_4.get("default", [])),
                "5-6": len(self.level_5_6.get("default", [])),
                "7-8": len(self.level_7_8.get("default", [])),
                "9-10": len(self.level_9_10.get("default", [])),
                "11-12": len(self.level_11_12.get("default", [])),
            }
        }


__all__ = ['ExpressionDB']
