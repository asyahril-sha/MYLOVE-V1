#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - NAME GENERATOR (FIX FULL)
=============================================================================
Membangkitkan nama permanent untuk bot
- Setiap role punya database nama sendiri
- Nama dipilih random saat pertama memulai
- Nama tidak akan sama untuk user yang sama (kecuali semua sudah dipakai)
- Dilengkapi arti nama untuk personalisasi
=============================================================================
"""

import random
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class NameGenerator:
    """
    Generator nama permanent untuk bot
    - Menyediakan nama random per role
    - Tracking nama yang sudah dipakai per user
    - Menghindari nama ganda untuk user yang sama
    """
    
    def __init__(self):
        # =========================================================================
        # DATABASE NAMA PER ROLE (8+ nama per role)
        # =========================================================================
        self.role_names = {
            "ipar": [
                "Sari", "Dewi", "Rina", "Maya", "Putri", "Anita", "Lestari", "Wulan",
                "Ratna", "Kartika", "Indah", "Tasya"
            ],
            "teman_kantor": [
                "Diana", "Linda", "Ayu", "Dita", "Vera", "Nina", "Rani", "Mira",
                "Sarah", "Tina", "Vina", "Rita"
            ],
            "janda": [
                "Rina", "Tuti", "Nina", "Susi", "Wati", "Maya", "Ira", "Vina",
                "Lina", "Mira", "Santi", "Dewi"
            ],
            "pelakor": [
                "Vina", "Sasha", "Bella", "Cantika", "Mira", "Ira", "Gita", "Lala",
                "Sasa", "Kiki", "Maya", "Rara"
            ],
            "istri_orang": [
                "Dewi", "Sari", "Rina", "Linda", "Tina", "Maya", "Ani", "Nita",
                "Rita", "Susan", "Julia", "Mira"
            ],
            "pdkt": [
                "Aurora", "Cinta", "Dewi", "Kirana", "Fika", "Nadia", "Amara", "Kayla",
                "Zahra", "Alya", "Sari", "Maya"
            ],
            "sepupu": [
                "Putri", "Nadia", "Sari", "Dina", "Lina", "Tari", "Nuri", "Mila",
                "Dara", "Wulan", "Indah", "Rani"
            ],
            "teman_sma": [
                "Anita", "Bella", "Cici", "Dina", "Eva", "Fani", "Gita", "Hani",
                "Indah", "Julia", "Kiki", "Lala"
            ],
            "mantan": [
                "Sarah", "Nadia", "Maya", "Rina", "Vina", "Dewi", "Linda", "Ayu",
                "Tina", "Mira", "Sari", "Rani"
            ]
        }
        
        # =========================================================================
        # DATABASE ARTI NAMA
        # =========================================================================
        self.meanings = {
            # Ipar
            "Sari": "esensi/intisari",
            "Dewi": "dewi",
            "Rina": "cahaya",
            "Maya": "ilusi",
            "Putri": "putri",
            "Anita": "anugerah",
            "Lestari": "abadi",
            "Wulan": "bulan",
            "Ratna": "permata",
            "Kartika": "bintang",
            "Indah": "cantik",
            "Candra": "bulan",
            
            # Teman Kantor
            "Diana": "dewi bulan",
            "Linda": "cantik",
            "Ayu": "cantik",
            "Dita": "anugerah",
            "Vera": "kebenaran",
            "Nina": "cahaya",
            "Rani": "ratu",
            "Mira": "laut",
            "Sarah": "putri",
            "Tina": "murni",
            "Vina": "cinta",
            "Rita": "mutiara",
            
            # Janda
            "Tuti": "tulus",
            "Susi": "bunga lili",
            "Wati": "perempuan",
            "Ira": "pengajar",
            "Lina": "cahaya",
            "Santi": "damai",
            
            # Pelakor
            "Sasha": "pembela",
            "Bella": "cantik",
            "Cantika": "cantik",
            "Gita": "lagu",
            "Lala": "bunga",
            "Sasa": "lili",
            "Kiki": "kebahagiaan",
            "Rara": "gadis",
            
            # Istri Orang
            "Ani": "anugerah",
            "Nita": "berkat",
            "Susan": "bunga lili",
            "Julia": "muda",
            
            # PDKT
            "Aurora": "fajar",
            "Cinta": "cinta",
            "Kirana": "cahaya",
            "Fika": "cerdas",
            "Nadia": "harapan",
            "Amara": "abadi",
            "Kayla": "murni",
            "Zahra": "bunga",
            "Alya": "langit",
            
            # Sepupu
            "Dina": "adil",
            "Tari": "penari",
            "Nuri": "burung",
            "Mila": "cinta",
            "Dara": "gadis",
            
            # Teman SMA
            "Bella": "cantik",
            "Cici": "kakak",
            "Eva": "hidup",
            "Fani": "bersinar",
            "Gita": "lagu",
            "Hani": "bahagia",
            
            # Mantan
            "Sarah": "putri",
        }
        
        # =========================================================================
        # TRACKING NAMA YANG SUDAH DIPAKAI
        # Format: {user_id: {role: [nama1, nama2, ...]}}
        # =========================================================================
        self.used_names = {}
        
        logger.info(f"✅ NameGenerator initialized with {self._count_total_names()} names across 9 roles")
    
    def _count_total_names(self) -> int:
        """Hitung total nama dalam database"""
        return sum(len(names) for names in self.role_names.values())
    
    def get_random_name(self, role: str, user_id: int = None) -> str:
        """
        Dapatkan nama random untuk role
        
        Args:
            role: Nama role (ipar, janda, dll)
            user_id: ID user (untuk tracking nama yang sudah dipakai)
            
        Returns:
            String nama
        """
        if role not in self.role_names:
            logger.warning(f"Role {role} not found, using pdkt")
            role = "pdkt"
        
        names = self.role_names[role]
        
        # Jika user_id diberikan, filter nama yang sudah dipakai
        if user_id:
            used = self.used_names.get(user_id, {}).get(role, [])
            available = [n for n in names if n not in used]
            
            if available:
                selected = random.choice(available)
                logger.debug(f"Available names for {role}: {len(available)}")
            else:
                # Semua nama sudah dipakai, pilih random dan reset
                selected = random.choice(names)
                logger.info(f"All names for {role} used by user {user_id}, resetting tracking")
                # Reset tracking untuk role ini
                if user_id in self.used_names and role in self.used_names[user_id]:
                    self.used_names[user_id][role] = []
        else:
            selected = random.choice(names)
        
        # Tandai sebagai terpakai
        if user_id:
            if user_id not in self.used_names:
                self.used_names[user_id] = {}
            if role not in self.used_names[user_id]:
                self.used_names[user_id][role] = []
            self.used_names[user_id][role].append(selected)
        
        logger.debug(f"Selected name: {selected} for {role}")
        return selected
    
    def get_name_with_meaning(self, role: str, user_id: int = None) -> dict:
        """
        Dapatkan nama lengkap dengan artinya
        
        Args:
            role: Nama role
            user_id: ID user (untuk tracking)
            
        Returns:
            Dict: {
                'name': 'Sari',
                'meaning': 'esensi/intisari'
            }
        """
        name = self.get_random_name(role, user_id)
        meaning = self.meanings.get(name, "berharga")
        
        return {
            "name": name,
            "meaning": meaning
        }
    
    def get_all_names_for_role(self, role: str) -> List[str]:
        """
        Dapatkan semua nama yang tersedia untuk role
        
        Args:
            role: Nama role
            
        Returns:
            List of names
        """
        return self.role_names.get(role, [])
    
    def get_all_meanings(self) -> Dict[str, str]:
        """Dapatkan semua arti nama"""
        return self.meanings.copy()
    
    def get_meaning(self, name: str) -> str:
        """
        Dapatkan arti dari sebuah nama
        
        Args:
            name: Nama yang dicari
            
        Returns:
            Arti nama atau "berharga" jika tidak ditemukan
        """
        return self.meanings.get(name, "berharga")
    
    def add_custom_name(self, role: str, name: str, meaning: str = ""):
        """
        Tambah nama kustom untuk role tertentu
        
        Args:
            role: Nama role
            name: Nama yang ditambahkan
            meaning: Arti nama (opsional)
        """
        if role not in self.role_names:
            self.role_names[role] = []
        
        if name not in self.role_names[role]:
            self.role_names[role].append(name)
            
            if meaning and name not in self.meanings:
                self.meanings[name] = meaning
            
            logger.info(f"Added custom name '{name}' to role {role}")
        else:
            logger.warning(f"Name '{name}' already exists in role {role}")
    
    def reset_used_names(self, user_id: int, role: Optional[str] = None):
        """
        Reset tracking nama yang sudah dipakai
        
        Args:
            user_id: ID user
            role: Role spesifik (None untuk semua role)
        """
        if user_id in self.used_names:
            if role:
                if role in self.used_names[user_id]:
                    del self.used_names[user_id][role]
                    logger.info(f"Reset used names for user {user_id} role {role}")
            else:
                del self.used_names[user_id]
                logger.info(f"Reset all used names for user {user_id}")
    
    def get_used_names(self, user_id: int, role: Optional[str] = None) -> List[str]:
        """
        Dapatkan daftar nama yang sudah dipakai user
        
        Args:
            user_id: ID user
            role: Role spesifik (None untuk semua)
            
        Returns:
            List of used names
        """
        if user_id not in self.used_names:
            return []
        
        if role:
            return self.used_names[user_id].get(role, [])
        else:
            all_names = []
            for r, names in self.used_names[user_id].items():
                all_names.extend(names)
            return all_names
    
    def get_available_names(self, user_id: int, role: str) -> List[str]:
        """
        Dapatkan nama yang masih tersedia untuk user pada role tertentu
        
        Args:
            user_id: ID user
            role: Nama role
            
        Returns:
            List of available names
        """
        if role not in self.role_names:
            return []
        
        all_names = self.role_names[role]
        used = self.get_used_names(user_id, role)
        
        return [n for n in all_names if n not in used]
    
    def get_stats(self, user_id: Optional[int] = None) -> Dict:
        """
        Dapatkan statistik name generator
        
        Args:
            user_id: ID user (opsional)
            
        Returns:
            Dictionary statistik
        """
        stats = {
            "total_names": self._count_total_names(),
            "total_roles": len(self.role_names),
            "names_per_role": {role: len(names) for role, names in self.role_names.items()}
        }
        
        if user_id:
            if user_id in self.used_names:
                total_used = sum(len(names) for names in self.used_names[user_id].values())
                stats["user_stats"] = {
                    "user_id": user_id,
                    "total_used": total_used,
                    "used_by_role": {
                        role: len(names) for role, names in self.used_names[user_id].items()
                    }
                }
            else:
                stats["user_stats"] = {
                    "user_id": user_id,
                    "total_used": 0,
                    "used_by_role": {}
                }
        
        return stats


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================
_name_generator = None


def get_name_generator() -> NameGenerator:
    """Dapatkan instance NameGenerator (singleton)"""
    global _name_generator
    if _name_generator is None:
        _name_generator = NameGenerator()
    return _name_generator


__all__ = ['NameGenerator', 'get_name_generator']
