#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - ROLE NAMES DATABASE
=============================================================================
Database nama untuk setiap role
Bot akan memilih nama random saat pertama kali memilih role
Nama ini akan menjadi identitas permanen bot dan masuk ke UniqueID
=============================================================================
"""

import random
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


# =============================================================================
# DATABASE NAMA PER ROLE
# =============================================================================
# Setiap role memiliki daftar nama yang bisa dipilih random
# Nama-nama ini terinspirasi dari nama Indonesia yang populer
# =============================================================================

ROLE_NAMES = {
    # ===== IPAR (Saudara ipar) =====
    "ipar": [
        "Sari", "Dewi", "Rina", "Maya", "Wulan", 
        "Indah", "Lestari", "Fitri", "Nadia", "Ayu",
        "Rini", "Sri", "Yuni", "Dian", "Eka",
        "Nova", "Putri", "Ratna", "Sinta", "Wati"
    ],
    
    # ===== TEMAN KANTOR =====
    "teman_kantor": [
        "Diana", "Linda", "Ayu", "Dita", "Vina",
        "Santi", "Rini", "Mega", "Cici", "Rani",
        "Anita", "Bella", "Cynthia", "Dini", "Elsa",
        "Fani", "Gita", "Hana", "Ira", "Jessica"
    ],
    
    # ===== JANDA =====
    "janda": [
        "Rina", "Tuti", "Nina", "Susi", "Wati",
        "Lilis", "Marni", "Yati", "Mira", "Santi",
        "Eva", "Fera", "Gina", "Hesti", "Ika",
        "Juli", "Kiki", "Lia", "Mona", "Nana"
    ],
    
    # ===== PELAKOR =====
    "pelakor": [
        "Vina", "Sasha", "Bella", "Cantika", "Karina",
        "Mira", "Selsa", "Cindy", "Gita", "Tara",
        "Alya", "Bunga", "Cinta", "Diva", "Evelyn",
        "Fira", "Gendis", "Happy", "Inez", "Julia"
    ],
    
    # ===== ISTRI ORANG =====
    "istri_orang": [
        "Dewi", "Sari", "Rina", "Linda", "Wulan",
        "Indah", "Ratna", "Maya", "Nia", "Rita",
        "Ani", "Betty", "Cici", "Diana", "Erna",
        "Fifi", "Galuh", "Heni", "Ira", "Juni"
    ],
    
    # ===== PDKT (Pendekatan) =====
    "pdkt": [
        "Aurora", "Cinta", "Dewi", "Kirana", "Laras",
        "Maharani", "Zahra", "Nova", "Cantika", "Maya",
        "Amara", "Bianca", "Callysta", "Danica", "Eleora",
        "Felicia", "Giselle", "Hana", "Isabel", "Jasmine"
    ],
    
    # ===== SEPUPU =====
    "sepupu": [
        "Putri", "Nadia", "Sari", "Dina", "Luna",
        "Bella", "Cika", "Naya", "Rara", "Vina",
        "Alya", "Beby", "Caca", "Dafa", "Ella",
        "Fifi", "Ghea", "Hilda", "Indri", "Jihan"
    ],
    
    # ===== TEMAN SMA =====
    "teman_sma": [
        "Anita", "Bella", "Cici", "Dina", "Eka",
        "Fina", "Gita", "Hani", "Indah", "Julia",
        "Kartika", "Leni", "Mira", "Nita", "Oktavia",
        "Puspa", "Queenza", "Rini", "Sari", "Tia"
    ],
    
    # ===== MANTAN =====
    "mantan": [
        "Sarah", "Nadia", "Maya", "Rina", "Dewi",
        "Cinta", "Ayu", "Laras", "Vina", "Tara",
        "Anisa", "Bunga", "Chika", "Dinda", "Elsa",
        "Fika", "Gita", "Hanna", "Intan", "Jessica"
    ]
}


# =============================================================================
# NAMA UNISEX (untuk role yang mungkin ingin variasi)
# =============================================================================
# Bisa digunakan untuk role tertentu jika ingin ada opsi nama cowok
# =============================================================================

UNISEX_NAMES = [
    "Alex", "Andi", "Ari", "Bimo", "Cakra", "Dani", "Edo", "Fajar",
    "Gilang", "Hadi", "Indra", "Joko", "Krisna", "Lukas", "Miko",
    "Nanda", "Oka", "Putra", "Raka", "Sandy", "Tommy", "Umar",
    "Vino", "Wahyu", "Yoga", "Zaki"
]


# =============================================================================
# NAMA INTERNASIONAL (untuk variasi)
# =============================================================================

INTERNATIONAL_NAMES = {
    "korean": [
        "Jiyeon", "Soyeon", "Yuna", "Mina", "Sana",
        "Jihyo", "Nayeon", "Tzuyu", "Chaeyoung", "Dahyun",
        "Irene", "Seulgi", "Wendy", "Joy", "Yeri"
    ],
    "japanese": [
        "Yuki", "Sakura", "Hana", "Rin", "Miko",
        "Akari", "Hinata", "Yui", "Miu", "Rina"
    ],
    "western": [
        "Alice", "Bella", "Chloe", "Daisy", "Emma",
        "Fiona", "Grace", "Hannah", "Ivy", "Julia",
        "Kelly", "Lily", "Mia", "Nora", "Olivia"
    ]
}


# =============================================================================
# FUNGSI UTAMA
# =============================================================================

def get_random_name(role: str, style: str = "indonesia") -> str:
    """
    Dapatkan nama random untuk role tertentu
    
    Args:
        role: Nama role (ipar, janda, dll)
        style: Gaya nama ('indonesia', 'korean', 'japanese', 'western', 'unisex')
        
    Returns:
        String nama yang dipilih random
    """
    if style == "unisex":
        return random.choice(UNISEX_NAMES)
    
    elif style in INTERNATIONAL_NAMES:
        return random.choice(INTERNATIONAL_NAMES[style])
    
    # Default: indonesia
    names = ROLE_NAMES.get(role, ROLE_NAMES["pdkt"])
    return random.choice(names)


def get_random_name_with_hint(role: str) -> tuple:
    """
    Dapatkan nama random beserta hint tentang namanya
    
    Returns:
        (nama, hint) - hint bisa digunakan untuk deskripsi
    """
    nama = get_random_name(role)
    
    # Daftar hint berdasarkan nama (untuk personalisasi)
    hints = {
        "Sari": "nama yang manis dan lembut",
        "Dewi": "nama yang anggun seperti dewi",
        "Rina": "nama yang ceria dan ramah",
        "Maya": "nama yang misterius dan menarik",
        "Aurora": "seperti cahaya fajar, indah dan menawan",
        "Cinta": "nama yang penuh kasih sayang",
        "Kirana": "sinar yang terang, mempesona",
        "Zahra": "bunga yang cantik dan harum",
        "Nadia": "penuh harapan dan kebahagiaan",
        "Putri": "anggun seperti putri kerajaan"
    }
    
    hint = hints.get(nama, "nama yang indah dan bermakna")
    return nama, hint


def get_name_by_popularity(role: str, rank: int = 1) -> str:
    """
    Dapatkan nama berdasarkan popularitas (1 = paling populer)
    
    Args:
        role: Nama role
        rank: Peringkat popularitas (1-5)
        
    Returns:
        String nama
    """
    names = ROLE_NAMES.get(role, ROLE_NAMES["pdkt"])
    
    # 5 nama pertama dianggap paling populer
    if 1 <= rank <= 5 and rank <= len(names):
        return names[rank - 1]
    
    # Fallback ke random
    return random.choice(names)


def get_all_names_for_role(role: str) -> List[str]:
    """Dapatkan semua nama yang tersedia untuk role tertentu"""
    return ROLE_NAMES.get(role, ROLE_NAMES["pdkt"]).copy()


def add_custom_name(role: str, name: str) -> bool:
    """
    Tambah nama kustom untuk role tertentu (untuk admin)
    
    Args:
        role: Nama role
        name: Nama baru
        
    Returns:
        True jika berhasil, False jika sudah ada
    """
    if role not in ROLE_NAMES:
        ROLE_NAMES[role] = []
    
    if name not in ROLE_NAMES[role]:
        ROLE_NAMES[role].append(name)
        logger.info(f"Added custom name '{name}' to role '{role}'")
        return True
    
    return False


def remove_custom_name(role: str, name: str) -> bool:
    """
    Hapus nama kustom dari role (untuk admin)
    
    Args:
        role: Nama role
        name: Nama yang akan dihapus
        
    Returns:
        True jika berhasil, False jika tidak ditemukan
    """
    if role in ROLE_NAMES and name in ROLE_NAMES[role]:
        ROLE_NAMES[role].remove(name)
        logger.info(f"Removed custom name '{name}' from role '{role}'")
        return True
    
    return False


def get_name_statistics() -> Dict:
    """Dapatkan statistik database nama"""
    stats = {
        "total_names": sum(len(names) for names in ROLE_NAMES.values()),
        "roles": {}
    }
    
    for role, names in ROLE_NAMES.items():
        stats["roles"][role] = {
            "count": len(names),
            "names": names[:5]  # 5 nama pertama sebagai sample
        }
    
    return stats


def format_name_for_display(name: str, role: str) -> str:
    """
    Format nama untuk ditampilkan ke user
    
    Args:
        name: Nama bot
        role: Role bot
        
    Returns:
        String format untuk display
    """
    role_display = {
        "ipar": "Ipar",
        "teman_kantor": "Teman Kantor",
        "janda": "Janda",
        "pelakor": "Pelakor",
        "istri_orang": "Istri Orang",
        "pdkt": "PDKT",
        "sepupu": "Sepupu",
        "teman_sma": "Teman SMA",
        "mantan": "Mantan"
    }
    
    role_name = role_display.get(role, role.capitalize())
    return f"{name} ({role_name})"


# =============================================================================
# SINGLETON INSTANCE (untuk akses global)
# =============================================================================

class NameDatabase:
    """Singleton class untuk akses database nama"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.names = ROLE_NAMES.copy()
        return cls._instance
    
    def get_random(self, role: str) -> str:
        return get_random_name(role)
    
    def get_all(self, role: str) -> List[str]:
        return get_all_names_for_role(role)
    
    def add(self, role: str, name: str) -> bool:
        return add_custom_name(role, name)
    
    def remove(self, role: str, name: str) -> bool:
        return remove_custom_name(role, name)


# Inisialisasi singleton
name_db = NameDatabase()

logger.info(f"✅ Name database initialized with {get_name_statistics()['total_names']} names across 9 roles")


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    'ROLE_NAMES',
    'UNISEX_NAMES',
    'INTERNATIONAL_NAMES',
    'get_random_name',
    'get_random_name_with_hint',
    'get_name_by_popularity',
    'get_all_names_for_role',
    'add_custom_name',
    'remove_custom_name',
    'get_name_statistics',
    'format_name_for_display',
    'name_db'
]
