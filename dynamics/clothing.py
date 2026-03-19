#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - CLOTHING SYSTEM (UPDATED)
=============================================================================
Mengelola pakaian bot
- Pakaian berubah sesuai aktivitas
- 10+ jenis pakaian
- get_random_clothing() untuk callback
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
                "activities": ["santai", "rebahan", "nonton TV", "tidur", "masak"]
            },
            "piyama": {
                "name": "piyama lucu motif boneka",
                "description": "Piyama nyaman dengan motif boneka kesukaan",
                "category": "sleep",
                "activities": ["tidur", "rebahan", "santai malam", "nonton film"]
            },
            "kaos": {
                "name": "kaos oversized",
                "description": "Kaos longgar yang nyaman dipakai",
                "category": "casual",
                "activities": ["santai", "jalan", "nongkrong", "belanja", "olahraga"]
            },
            "kemeja": {
                "name": "kemeja putih",
                "description": "Kemeja putih rapi, cocok untuk kerja",
                "category": "formal",
                "activities": ["kerja", "rapat", "keluar", "meeting"]
            },
            "dress": {
                "name": "dress cantik",
                "description": "Dress warna pastel yang manis",
                "category": "formal",
                "activities": ["jalan", "nongkrong", "date", "pesta"]
            },
            "rok": {
                "name": "rok span hitam",
                "description": "Rok span hitam yang elegan",
                "category": "formal",
                "activities": ["kerja", "keluar", "kantor", "acara formal"]
            },
            "jeans": {
                "name": "celana jeans",
                "description": "Celana jeans kesayangan",
                "category": "casual",
                "activities": ["jalan", "nongkrong", "belanja", "kencan"]
            },
            "shorts": {
                "name": "celana pendek",
                "description": "Celana pendek nyaman buat di rumah",
                "category": "casual",
                "activities": ["santai", "olahraga", "beres-beres", "jemur"]
            },
            "tanktop": {
                "name": "tank top",
                "description": "Tank top tipis, adem dipakai",
                "category": "casual",
                "activities": ["santai", "olahraga", "panas-panasan", "jemur"]
            },
            "handuk": {
                "name": "handuk",
                "description": "Handuk setelah mandi, masih basah",
                "category": "special",
                "activities": ["mandi", "selesai mandi", "baru bangun"]
            },
            "sweater": {
                "name": "sweater hangat",
                "description": "Sweater rajut yang hangat, cocok buat malem",
                "category": "casual",
                "activities": ["santai malam", "nonton film", "jalan malem"]
            },
            "bathrobe": {
                "name": "jubah mandi",
                "description": "Jubah mandi setelah berendam",
                "category": "special",
                "activities": ["selesai mandi", "santai", "spa"]
            }
        }
        
        self.current_clothing = "daster"
        logger.info(f"✅ ClothingSystem initialized with {len(self.clothes)} clothes")
    
    def get_current(self) -> Dict:
        """Dapatkan pakaian saat ini"""
        return self.clothes.get(self.current_clothing, self.clothes["daster"])
    
    def get_current_name(self) -> str:
        """Dapatkan nama pakaian saat ini"""
        return self.get_current()["name"]
    
    def get_current_description(self) -> str:
        """Dapatkan deskripsi pakaian saat ini"""
        return self.get_current()["description"]
    
    def get_random_clothing(self) -> Dict:
        """
        Dapatkan pakaian random (untuk callback)
        
        Returns:
            Dict pakaian dengan name, description, category, activities
        """
        cloth_id = random.choice(list(self.clothes.keys()))
        return self.clothes[cloth_id]
    
    def get_random_clothing_with_activity(self) -> Dict:
        """Dapatkan pakaian random dan aktivitas random"""
        cloth = self.get_random_clothing()
        return cloth
    
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
            self.change_clothing()
        
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
            candidates = ["kaos", "daster", "piyama"]
        elif 11 <= hour < 18:  # Siang
            candidates = ["kemeja", "kaos", "dress", "rok"]
        elif 18 <= hour < 22:  # Malam
            candidates = ["dress", "kaos", "sweater", "piyama"]
        else:  # Tengah malam
            candidates = ["piyama", "handuk", "bathrobe"]
        
        self.current_clothing = random.choice(candidates)
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
    
    def get_all_clothes(self) -> List[str]:
        """Dapatkan semua nama pakaian"""
        return [cloth["name"] for cloth in self.clothes.values()]
