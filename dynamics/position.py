#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - POSITION SYSTEM (UPDATED)
=============================================================================
Mengelola posisi tubuh bot
- Posisi berubah sesuai aktivitas
- 6+ posisi tubuh
- get_random_position() untuk callback
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
                "activities": ["ngobrol", "nonton TV", "baca buku", "main HP", "kerja"]
            },
            "berdiri": {
                "name": "berdiri",
                "description": "berdiri tegak",
                "activities": ["masak", "cuci piring", "siap-siap", "ngantri", "stretch"]
            },
            "berbaring": {
                "name": "berbaring",
                "description": "berbaring",
                "activities": ["tidur-tiduran", "rebahan", "istirahat", "baca buku", "main HP"]
            },
            "bersandar": {
                "name": "bersandar",
                "description": "bersandar",
                "activities": ["santai", "ngobrol", "nunggu", "ngopi", "melamun"]
            },
            "jongkok": {
                "name": "jongkok",
                "description": "jongkok",
                "activities": ["bersih-bersih", "main sama kucing", "foto", "ngambil barang"]
            },
            "merangkak": {
                "name": "merangkak",
                "description": "merangkak",
                "activities": ["nyari barang", "main", "bersih-bersih"]
            },
            "miring": {
                "name": "miring",
                "description": "berbaring miring",
                "activities": ["tidur", "rebahan", "nonton HP", "baca buku"]
            },
            "telentang": {
                "name": "telentang",
                "description": "telentang",
                "activities": ["tidur", "rebahan", "stretch", "meditasi"]
            }
        }
        
        self.current_position = "duduk"
        logger.info(f"✅ PositionSystem initialized with {len(self.positions)} positions")
    
    def get_current(self) -> Dict:
        """Dapatkan posisi saat ini"""
        return self.positions.get(self.current_position, self.positions["duduk"])
    
    def get_current_name(self) -> str:
        """Dapatkan nama posisi saat ini"""
        return self.get_current()["name"]
    
    def get_current_description(self) -> str:
        """Dapatkan deskripsi posisi saat ini"""
        return self.get_current()["description"]
    
    def get_random_position(self) -> Dict:
        """
        Dapatkan posisi random (untuk callback)
        
        Returns:
            Dict posisi dengan name, description, activities
        """
        pos_id = random.choice(list(self.positions.keys()))
        return self.positions[pos_id]
    
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
    
    def get_all_positions(self) -> List[str]:
        """Dapatkan semua nama posisi"""
        return [pos["name"] for pos in self.positions.values()]
