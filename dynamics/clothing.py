#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - CLOTHING SYSTEM
=============================================================================
Mengelola pakaian bot
- Pakaian berubah sesuai aktivitas
- 10+ jenis pakaian
=============================================================================
"""

import random
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ClothingSystem:
    """
    Sistem pakaian dinamis
    """
    
    def __init__(self):
        self.clothes = {
            "daster": {
                "name": "daster rumah motif bunga",
                "description": "Daster tipis motif bunga yang nyaman dipakai di rumah",
                "category": "casual",
                "activities": ["santai", "rebahan", "nonton TV", "tidur"]
            },
            "piyama": {
                "name": "piyama lucu motif boneka",
                "description": "Piyama nyaman dengan motif boneka kesukaan",
                "category": "sleep",
                "activities": ["tidur", "rebahan", "santai malam"]
            },
            "kaos": {
                "name": "kaos oversized",
                "description": "Kaos longgar yang nyaman dipakai",
                "category": "casual",
                "activities": ["santai", "jalan", "nongkrong"]
            },
            "kemeja": {
                "name": "kemeja putih",
                "description": "Kemeja putih rapi, cocok untuk kerja",
                "category": "formal",
                "activities": ["kerja", "rapat", "keluar"]
            },
            "dress": {
                "name": "dress cantik",
                "description": "Dress warna pastel yang manis",
                "category": "formal",
                "activities": ["jalan", "nongkrong", "date"]
            },
            "rok": {
                "name": "rok span hitam",
                "description": "Rok span hitam yang elegan",
                "category": "formal",
                "activities": ["kerja", "keluar"]
            },
            "jeans": {
                "name": "celana jeans",
                "description": "Celana jeans kesayangan",
                "category": "casual",
                "activities": ["jalan", "nongkrong", "belanja"]
            },
            "shorts": {
                "name": "celana pendek",
                "description": "Celana pendek nyaman buat di rumah",
                "category": "casual",
                "activities": ["santai", "olahraga", "beres-beres"]
            },
            "tanktop": {
                "name": "tank top",
                "description": "Tank top tipis, adem dipakai",
                "category": "casual",
                "activities": ["santai", "olahraga", "panas-panasan"]
            },
            "handuk": {
                "name": "handuk",
                "description": "Handuk setelah mandi, masih basah",
                "category": "special",
                "activities": ["mandi", "selesai mandi"]
            }
        }
        
        self.current_clothing = "daster"
        logger.info("✅ ClothingSystem initialized")
    
    def get_current(self) -> Dict:
        """Dapatkan pakaian saat ini"""
        return self.clothes.get(self.current_clothing, self.clothes["daster"])
    
    def get_current_name(self) -> str:
        """Dapatkan nama pakaian saat ini"""
        return self.get_current()["name"]
    
    def get_current_description(self) -> str:
        """Dapatkan deskripsi pakaian saat ini"""
        return self.get_current()["description"]
    
    def change_clothing(self, clothing_id: str = None) -> Dict:
        """
        Ganti pakaian
        
        Args:
            clothing_id: ID pakaian (None untuk random)
        
        Returns:
            Pakaian baru
        """
        if clothing_id and clothing_id in self.clothes:
            self.current_clothing = clothing_id
        else:
            # Random clothing, beda dari yang sekarang
            others = [c for c in self.clothes.keys() if c != self.current_clothing]
            self.current_clothing = random.choice(others)
        
        return self.get_current()
    
    def change_by_activity(self, activity: str) -> Dict:
        """
        Ganti pakaian berdasarkan aktivitas
        
        Args:
            activity: Aktivitas yang dilakukan
        
        Returns:
            Pakaian baru
        """
        for cloth_id, cloth_data in self.clothes.items():
            if activity in cloth_data["activities"]:
                self.current_clothing = cloth_id
                break
        else:
            # Default ke random
            self.change_position()
        
        return self.get_current()
    
    def change_by_time(self, hour: int) -> Dict:
        """
        Ganti pakaian berdasarkan waktu
        
        Args:
            hour: Jam (0-23)
        
        Returns:
            Pakaian baru
        """
        if 5 <= hour < 11:  # Pagi
            self.current_clothing = "kaos" if random.random() < 0.5 else "daster"
        elif 11 <= hour < 18:  # Siang
            self.current_clothing = "kemeja" if random.random() < 0.3 else "kaos"
        elif 18 <= hour < 22:  # Malam
            self.current_clothing = "piyama" if random.random() < 0.4 else "daster"
        else:  # Tengah malam
            self.current_clothing = "piyama"
        
        return self.get_current()
    
    def random_change(self, chance: float = 0.1) -> Optional[Dict]:
        """
        Random ganti pakaian dengan probabilitas tertentu
        
        Args:
            chance: Probabilitas ganti pakaian (0-1)
        
        Returns:
            Pakaian baru jika berubah, None jika tidak
        """
        if random.random() < chance:
            return self.change_clothing()
        return None
    
    def format_clothing_text(self) -> str:
        """Format teks pakaian untuk ditampilkan"""
        cloth = self.get_current()
        return f"👗 Aku pakai **{cloth['name']}**."
    
    def get_all_clothes(self) -> List[str]:
        """Dapatkan semua nama pakaian"""
        return [cloth["name"] for cloth in self.clothes.values()]
