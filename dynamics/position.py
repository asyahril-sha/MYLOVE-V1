#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - POSITION SYSTEM
=============================================================================
Mengelola posisi tubuh bot
- Posisi berubah sesuai aktivitas
- 6+ posisi tubuh
=============================================================================
"""

import random
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PositionSystem:
    """
    Sistem posisi tubuh dinamis
    """
    
    def __init__(self):
        self.positions = {
            "duduk": {
                "name": "duduk",
                "description": "duduk santai",
                "activities": ["ngobrol", "nonton TV", "baca buku", "main HP"]
            },
            "berdiri": {
                "name": "berdiri",
                "description": "berdiri tegak",
                "activities": ["masak", "cuci piring", "siap-siap"]
            },
            "berbaring": {
                "name": "berbaring",
                "description": "berbaring",
                "activities": ["tidur-tiduran", "rebahan", "istirahat"]
            },
            "bersandar": {
                "name": "bersandar",
                "description": "bersandar di dinding",
                "activities": ["santai", "ngobrol", "nunggu"]
            },
            "jongkok": {
                "name": "jongkok",
                "description": "jongkok",
                "activities": ["bersih-bersih", "main sama kucing"]
            },
            "merangkak": {
                "name": "merangkak",
                "description": "merangkak",
                "activities": ["nyari barang", "main"]
            }
        }
        
        self.current_position = "duduk"
        logger.info("✅ PositionSystem initialized")
    
    def get_current(self) -> Dict:
        """Dapatkan posisi saat ini"""
        return self.positions.get(self.current_position, self.positions["duduk"])
    
    def get_current_name(self) -> str:
        """Dapatkan nama posisi saat ini"""
        return self.get_current()["name"]
    
    def get_current_description(self) -> str:
        """Dapatkan deskripsi posisi saat ini"""
        return self.get_current()["description"]
    
    def change_position(self, position_id: str = None) -> Dict:
        """
        Ganti posisi
        
        Args:
            position_id: ID posisi (None untuk random)
        
        Returns:
            Posisi baru
        """
        if position_id and position_id in self.positions:
            self.current_position = position_id
        else:
            # Random position, beda dari yang sekarang
            others = [p for p in self.positions.keys() if p != self.current_position]
            self.current_position = random.choice(others)
        
        return self.get_current()
    
    def change_by_activity(self, activity: str) -> Dict:
        """
        Ganti posisi berdasarkan aktivitas
        
        Args:
            activity: Aktivitas yang dilakukan
        
        Returns:
            Posisi baru
        """
        for pos_id, pos_data in self.positions.items():
            if activity in pos_data["activities"]:
                self.current_position = pos_id
                break
        else:
            # Default ke random
            self.change_position()
        
        return self.get_current()
    
    def random_change(self, chance: float = 0.2) -> Optional[Dict]:
        """
        Random ganti posisi dengan probabilitas tertentu
        
        Args:
            chance: Probabilitas ganti posisi (0-1)
        
        Returns:
            Posisi baru jika berubah, None jika tidak
        """
        if random.random() < chance:
            return self.change_position()
        return None
    
    def format_position_text(self) -> str:
        """Format teks posisi untuk ditampilkan"""
        pos = self.get_current()
        return f"🧍 Aku lagi {pos['description']}."
    
    def get_all_positions(self) -> List[str]:
        """Dapatkan semua nama posisi"""
        return [pos["name"] for pos in self.positions.values()]
