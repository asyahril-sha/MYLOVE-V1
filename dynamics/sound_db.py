#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - SOUND DATABASE
=============================================================================
Database suara untuk fallback
- 50+ suara
- Kategorisasi
=============================================================================
"""

import random
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class SoundDatabase:
    """
    Database suara untuk fallback
    """
    
    def __init__(self):
        self.sounds = {
            "desah": [
                "*mendesah pelan*",
                "*mendesah*",
                "*mendesah panjang*",
                "*mengerang ringan*",
                "*mengerang*"
            ],
            "napas": [
                "*napas sedikit tersengal*",
                "*bernapas lebih cepat*",
                "*napas berat*",
                "*megap-megap*",
                "*terengah-engah*"
            ],
            "tawa": [
                "*tertawa kecil*",
                "*terkekeh*",
                "*cekikikan*",
                "*ngakak*",
                "*tertawa*"
            ],
            "bisik": [
                "*berbisik*",
                "*berbisik pelan*",
                "*berbisik mesra*",
                "*bisik-bisik*"
            ],
            "gumam": [
                "*bergumam*",
                "*bersenandung*",
                "*bergumam pelan*",
                "*ngomong sendiri*"
            ],
            "kaget": [
                "*tersentak*",
                "*menarik napas*",
                "*terkesiap*",
                "*kaget*"
            ],
            "senang": [
                "*bersorak kecil*",
                "*berteriak girang*",
                "*hore*",
                "*yey*"
            ],
            "sedih": [
                "*terisak*",
                "*tersedu-sedu*",
                "*nangis*",
                "*sedih*"
            ],
            "intim": [
                "*mendesah kenikmatan*",
                "*mengerang puas*",
                "*napas tersengal*",
                "*berbisik dengan suara serak*"
            ],
            "climax": [
                "*mendesah panjang*",
                "*mengerang keras*",
                "*teriak kecil*",
                "*napas terhenti*"
            ]
        }
        
        logger.info(f"✅ SoundDatabase initialized with {self.count()} sounds")
    
    def get_random(self, category: str = None) -> str:
        """
        Dapatkan suara random
        
        Args:
            category: Kategori suara (None untuk semua)
        
        Returns:
            String suara
        """
        if category and category in self.sounds:
            return random.choice(self.sounds[category])
        else:
            all_sounds = []
            for sound_list in self.sounds.values():
                all_sounds.extend(sound_list)
            return random.choice(all_sounds)
    
    def get_by_category(self, category: str) -> List[str]:
        """Dapatkan semua suara dalam kategori"""
        return self.sounds.get(category, [])
    
    def get_categories(self) -> List[str]:
        """Dapatkan semua kategori"""
        return list(self.sounds.keys())
    
    def count(self) -> int:
        """Hitung total suara"""
        return sum(len(sound) for sound in self.sounds.values())
    
    def add_sound(self, category: str, sound: str):
        """Tambah suara baru"""
        if category not in self.sounds:
            self.sounds[category] = []
        if sound not in self.sounds[category]:
            self.sounds[category].append(sound)
    
    def format_for_prompt(self, category: str = None, count: int = 3) -> str:
        """
        Format contoh suara untuk prompt
        
        Args:
            category: Kategori
            count: Jumlah contoh
        
        Returns:
            String contoh
        """
        if category:
            examples = random.sample(self.sounds[category], min(count, len(self.sounds[category])))
        else:
            all_sounds = []
            for sound_list in self.sounds.values():
                all_sounds.extend(sound_list)
            examples = random.sample(all_sounds, min(count, len(all_sounds)))
        
        return "\n".join([f"  • {ex}" for ex in examples])
