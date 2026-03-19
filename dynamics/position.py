#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - POSITION SYSTEM (FIX FULL)
=============================================================================
Mengelola posisi tubuh bot
- Posisi berubah sesuai aktivitas
- 8+ posisi tubuh
- get_random_position() untuk callback
- FIX: Lengkap dengan PositionType enum
=============================================================================
"""

import random
import logging
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class PositionType(str, Enum):
    """Tipe posisi"""
    DUDUK = "duduk"
    BERDIRI = "berdiri"
    BERBARING = "berbaring"
    BERSANDAR = "bersandar"
    JONGKOK = "jongkok"
    MERANGKAK = "merangkak"
    MIRING = "miring"
    TELENTANG = "telentang"


class PositionSystem:
    """
    Sistem posisi tubuh dinamis
    """
    
    def __init__(self):
        self.positions = {
            "duduk": {
                "name": "duduk",
                "description": "duduk santai",
                "type": PositionType.DUDUK,
                "activities": ["ngobrol", "nonton TV", "baca buku", "main HP", "kerja", "ngopi"]
            },
            "berdiri": {
                "name": "berdiri",
                "description": "berdiri tegak",
                "type": PositionType.BERDIRI,
                "activities": ["masak", "cuci piring", "siap-siap", "ngantri", "stretch", "foto"]
            },
            "berbaring": {
                "name": "berbaring",
                "description": "berbaring",
                "type": PositionType.BERBARING,
                "activities": ["tidur-tiduran", "rebahan", "istirahat", "baca buku", "main HP", "melamun"]
            },
            "bersandar": {
                "name": "bersandar",
                "description": "bersandar",
                "type": PositionType.BERSANDAR,
                "activities": ["santai", "ngobrol", "nunggu", "ngopi", "melamun", "dengerin musik"]
            },
            "jongkok": {
                "name": "jongkok",
                "description": "jongkok",
                "type": PositionType.JONGKOK,
                "activities": ["bersih-bersih", "main sama kucing", "foto", "ngambil barang", "berkebun"]
            },
            "merangkak": {
                "name": "merangkak",
                "description": "merangkak",
                "type": PositionType.MERANGKAK,
                "activities": ["nyari barang", "main", "bersih-bersih", "beres-beres"]
            },
            "miring": {
                "name": "miring",
                "description": "berbaring miring",
                "type": PositionType.MIRING,
                "activities": ["tidur", "rebahan", "nonton HP", "baca buku", "ngelamun"]
            },
            "telentang": {
                "name": "telentang",
                "description": "telentang",
                "type": PositionType.TELENTANG,
                "activities": ["tidur", "rebahan", "stretch", "meditasi", "tarik napas"]
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
    
    def get_current_type(self) -> PositionType:
        """Dapatkan tipe posisi saat ini"""
        return self.get_current()["type"]
    
    def get_random_position(self) -> Dict:
        """
        Dapatkan posisi random (untuk callback)
        
        Returns:
            Dict posisi dengan name, description, type, activities
        """
        pos_id = random.choice(list(self.positions.keys()))
        return self.positions[pos_id]
    
    def get_random_position_with_activity(self) -> tuple:
        """
        Dapatkan posisi random + aktivitas random
        
        Returns:
            (position_dict, activity)
        """
        pos = self.get_random_position()
        activity = random.choice(pos["activities"])
        return pos, activity
    
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
            self.current_position = random.choice(others) if others else "duduk"
        
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
    
    def get_positions_by_type(self, pos_type: PositionType) -> List[Dict]:
        """Dapatkan posisi berdasarkan tipe"""
        return [pos for pos in self.positions.values() if pos["type"] == pos_type]
    
    def format_position_text(self) -> str:
        """Format teks posisi untuk ditampilkan"""
        pos = self.get_current()
        return f"🧍 Aku lagi **{pos['description']}**."
    
    def get_stats(self) -> Dict:
        """Dapatkan statistik posisi"""
        return {
            "total_positions": len(self.positions),
            "current": self.current_position,
            "by_type": {
                "duduk": len(self.get_positions_by_type(PositionType.DUDUK)),
                "berdiri": len(self.get_positions_by_type(PositionType.BERDIRI)),
                "berbaring": len(self.get_positions_by_type(PositionType.BERBARING)),
                "bersandar": len(self.get_positions_by_type(PositionType.BERSANDAR)),
                "jongkok": len(self.get_positions_by_type(PositionType.JONGKOK)),
                "merangkak": len(self.get_positions_by_type(PositionType.MERANGKAK)),
                "miring": len(self.get_positions_by_type(PositionType.MIRING)),
                "telentang": len(self.get_positions_by_type(PositionType.TELENTANG))
            }
        }
