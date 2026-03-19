#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - LOCATION SYSTEM (UPDATED)
=============================================================================
Mengelola lokasi bot secara dinamis
- Lokasi berubah setiap chat
- Auto-detect dari pesan user
- 10+ lokasi dengan deskripsi
- get_random_location() untuk callback
=============================================================================
"""

import random
import logging
import re
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class LocationSystem:
    """
    Sistem lokasi dinamis untuk bot
    """
    
    def __init__(self):
        self.locations = {
            "ruang_tamu": {
                "name": "ruang tamu",
                "description": "Ruang tamu yang hangat dengan sofa empuk berwarna krem. Ada TV 50 inci di dinding, rak buku penuh novel, dan tanaman hias di sudut ruangan.",
                "category": "indoor",
                "activities": ["nonton TV", "baca buku", "santai", "ngobrol", "main HP"]
            },
            "kamar": {
                "name": "kamar",
                "description": "Kamar tidur dengan ranjang ukuran queen, sprei motif bunga, dan lampu tidur temaram di samping tempat tidur.",
                "category": "indoor",
                "activities": ["rebahan", "main HP", "tidur-tiduran", "baca buku", "melamun"]
            },
            "dapur": {
                "name": "dapur",
                "description": "Dapur bersih dengan peralatan masak lengkap. Ada aroma masakan yang menggoda.",
                "category": "indoor",
                "activities": ["masak", "ngemil", "bikin kopi", "cuci piring", "bersih-bersih"]
            },
            "kamar_mandi": {
                "name": "kamar mandi",
                "description": "Kamar mandi dengan ubin putih, shower, dan wangi sabun mandi.",
                "category": "indoor",
                "activities": ["mandi", "cuci muka", "sikat gigi", "bersihin diri"]
            },
            "teras": {
                "name": "teras",
                "description": "Teras rumah dengan kursi santai dan tanaman pot. Angin sepoi-sepoi bikin nyaman.",
                "category": "outdoor",
                "activities": ["duduk santai", "minum teh", "liatin jalan", "baca koran", "ngopi"]
            },
            "taman": {
                "name": "taman",
                "description": "Taman kecil dengan rumput hijau dan bunga-bunga warna-warni. Ada ayunan di pojok taman.",
                "category": "outdoor",
                "activities": ["jalan-jalan", "duduk di bangku", "foto-foto", "baca buku", "santai"]
            },
            "kantor": {
                "name": "kantor",
                "description": "Ruang kantor dengan meja kerja, komputer, dan kursi ergonomis. Suasana profesional.",
                "category": "public",
                "activities": ["kerja", "rapat", "nugas", "ngetik", "teleponan"]
            },
            "cafe": {
                "name": "cafe",
                "description": "Cafe cozy dengan lampu temaram, musik jazz pelan, dan aroma kopi yang khas.",
                "category": "public",
                "activities": ["ngopi", "ngobrol", "nongkrong", "baca buku", "dengerin musik"]
            },
            "mall": {
                "name": "mall",
                "description": "Mall ramai dengan banyak toko dan pengunjung. Ada eskalator dan musik di latar.",
                "category": "public",
                "activities": ["jalan-jalan", "belanja", "nonton", "makan", "nongkrong"]
            },
            "pantai": {
                "name": "pantai",
                "description": "Pantai dengan pasir putih dan ombak tenang. Angin laut berhembus sepoi-sepoi.",
                "category": "outdoor",
                "activities": ["jalan di pinggir pantai", "duduk di pasir", "main air", "foto-foto", "nikmatin sunset"]
            },
            "balkon": {
                "name": "balkon",
                "description": "Balkon apartemen dengan pemandangan kota. Ada kursi kecil dan tanaman gantung.",
                "category": "outdoor",
                "activities": ["santai", "ngopi", "liatin pemandangan", "dengerin musik", "melamun"]
            },
            "gym": {
                "name": "gym",
                "description": "Pusat kebugaran dengan berbagai alat olahraga. Ada treadmill, dumbbell, dan yoga mat.",
                "category": "public",
                "activities": ["olahraga", "lari", "angkat beban", "yoga", "fitness"]
            }
        }
        
        self.current_location = "ruang_tamu"
        self.last_change = 0
        
        logger.info(f"✅ LocationSystem initialized with {len(self.locations)} locations")
    
    def get_current(self) -> Dict:
        """Dapatkan lokasi saat ini"""
        return self.locations.get(self.current_location, self.locations["ruang_tamu"])
    
    def get_current_name(self) -> str:
        """Dapatkan nama lokasi saat ini"""
        return self.get_current()["name"]
    
    def get_current_description(self) -> str:
        """Dapatkan deskripsi lokasi saat ini"""
        return self.get_current()["description"]
    
    def get_current_activity(self) -> str:
        """Dapatkan aktivitas random di lokasi saat ini"""
        location = self.get_current()
        return random.choice(location["activities"])
    
    def get_random_location(self) -> Dict:
        """
        Dapatkan lokasi random (untuk callback)
        
        Returns:
            Dict lokasi dengan name, description, category, activities
        """
        loc_id = random.choice(list(self.locations.keys()))
        return self.locations[loc_id]
    
    def get_random_location_with_activity(self) -> Tuple[Dict, str]:
        """
        Dapatkan lokasi random + aktivitas random
        
        Returns:
            (location_dict, activity)
        """
        loc = self.get_random_location()
        activity = random.choice(loc["activities"])
        return loc, activity
    
    def change_location(self, location_id: str = None) -> Dict:
        """
        Ganti lokasi
        
        Args:
            location_id: ID lokasi (None untuk random)
        
        Returns:
            Lokasi baru
        """
        if location_id and location_id in self.locations:
            self.current_location = location_id
        else:
            others = [loc for loc in self.locations.keys() if loc != self.current_location]
            self.current_location = random.choice(others)
        
        self.last_change = __import__('time').time()
        return self.get_current()
    
    def random_change(self, chance: float = 0.3) -> Optional[Dict]:
        """
        Random ganti lokasi dengan probabilitas tertentu
        
        Args:
            chance: Probabilitas ganti lokasi (0-1)
        
        Returns:
            Lokasi baru jika berubah, None jika tidak
        """
        if random.random() < chance:
            return self.change_location()
        return None
    
    def detect_from_message(self, message: str) -> Optional[Dict]:
        """
        Deteksi lokasi dari pesan user
        
        Args:
            message: Pesan user
        
        Returns:
            Lokasi yang terdeteksi atau None
        """
        msg_lower = message.lower()
        
        keywords = {
            "ruang tamu": "ruang_tamu",
            "kamar": "kamar",
            "dapur": "dapur",
            "kamar mandi": "kamar_mandi",
            "wc": "kamar_mandi",
            "toilet": "kamar_mandi",
            "teras": "teras",
            "taman": "taman",
            "kantor": "kantor",
            "cafe": "cafe",
            "mall": "mall",
            "pantai": "pantai",
            "balkon": "balkon",
            "gym": "gym"
        }
        
        for keyword, loc_id in keywords.items():
            if keyword in msg_lower:
                return self.change_location(loc_id)
        
        return None
    
    def get_all_locations(self) -> List[str]:
        """Dapatkan semua nama lokasi"""
        return [loc["name"] for loc in self.locations.values()]
    
    def get_stats(self) -> Dict:
        """Dapatkan statistik lokasi"""
        return {
            "total_locations": len(self.locations),
            "current": self.current_location,
            "indoor": len([l for l in self.locations.values() if l["category"] == "indoor"]),
            "outdoor": len([l for l in self.locations.values() if l["category"] == "outdoor"]),
            "public": len([l for l in self.locations.values() if l["category"] == "public"])
        }
