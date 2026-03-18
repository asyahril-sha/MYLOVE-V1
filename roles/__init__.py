#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - ROLE NAMES DATABASE (FIX FULL + PDKT)
=============================================================================
Database nama untuk setiap role
Bot akan memilih nama random saat pertama kali memilih role
Nama ini akan menjadi identitas permanen bot dan masuk ke UniqueID

**PDKT SUPER SPESIAL**: Nama-nama khusus dengan chemistry hint
=============================================================================
"""

import random
import logging
from typing import Dict, List, Optional, Tuple

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
    
    # ===== PDKT (Pendekatan) - NAMA SUPER SPESIAL =====
    "pdkt": [
        # Nama-nama dengan hint chemistry tinggi
        {"nama": "Aurora", "hint": "Cahaya fajar, mempesona", "chemistry_bias": 80},
        {"nama": "Cinta", "hint": "Penuh kasih sayang", "chemistry_bias": 85},
        {"nama": "Kirana", "hint": "Sinar yang terang", "chemistry_bias": 75},
        {"nama": "Zahra", "hint": "Bunga yang cantik", "chemistry_bias": 70},
        {"nama": "Nadia", "hint": "Penuh harapan", "chemistry_bias": 65},
        {"nama": "Amara", "hint": "Anggun dan manis", "chemistry_bias": 80},
        {"nama": "Bianca", "hint": "Putih bersih", "chemistry_bias": 75},
        {"nama": "Callysta", "hint": "Sangat cantik", "chemistry_bias": 85},
        {"nama": "Danica", "hint": "Bintang pagi", "chemistry_bias": 70},
        {"nama": "Eleora", "hint": "Cahaya Tuhan", "chemistry_bias": 80},
        {"nama": "Felicia", "hint": "Bahagia", "chemistry_bias": 75},
        {"nama": "Giselle", "hint": "Anggun", "chemistry_bias": 70},
        {"nama": "Hana", "hint": "Karunia", "chemistry_bias": 65},
        {"nama": "Isabel", "hint": "Cantik", "chemistry_bias": 75},
        {"nama": "Jasmine", "hint": "Bunga melati", "chemistry_bias": 80},
        {"nama": "Kayla", "hint": "Mahkota", "chemistry_bias": 70},
        {"nama": "Luna", "hint": "Bulan", "chemistry_bias": 85},
        {"nama": "Maya", "hint": "Ilusi", "chemistry_bias": 75},
        {"nama": "Nayla", "hint": "Pencapaian", "chemistry_bias": 70},
        {"nama": "Olivia", "hint": "Kedamaian", "chemistry_bias": 80},
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
# PDKT SPECIFIC NAMES (dengan chemistry bias)
# =============================================================================

def get_pdkt_names_with_bias() -> List[Dict]:
    """Dapatkan daftar nama PDKT dengan chemistry bias"""
    return ROLE_NAMES.get("pdkt", [])


def get_pdkt_name_with_chemistry() -> Tuple[str, str, int]:
    """
    Dapatkan nama PDKT random dengan chemistry bias
    
    Returns:
        Tuple (nama, hint, chemistry_bias)
    """
    pdkt_names = get_pdkt_names_with_bias()
    selected = random.choice(pdkt_names)
    
    if isinstance(selected, dict):
        return selected['nama'], selected['hint'], selected['chemistry_bias']
    else:
        # Fallback untuk format lama
        return selected, "nama yang indah", 50


# =============================================================================
# NAMA UNISEX (untuk role yang mungkin ingin variasi)
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
        role: Nama role (ipar, janda, pdkt, dll)
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
    
    # Untuk PDKT, nama bisa berupa dict atau string
    if role == "pdkt":
        selected = random.choice(names)
        if isinstance(selected, dict):
            return selected['nama']
    
    return random.choice(names)


def get_random_name_with_hint(role: str) -> tuple:
    """
    Dapatkan nama random beserta hint tentang namanya
    
    Returns:
        (nama, hint) - hint bisa digunakan untuk deskripsi
    """
    if role == "pdkt":
        nama, hint, bias = get_pdkt_name_with_chemistry()
        return nama, hint
    
    # Untuk role lain
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


def get_pdkt_chemistry_bias(nama: str) -> int:
    """
    Dapatkan chemistry bias untuk nama PDKT tertentu
    
    Args:
        nama: Nama bot PDKT
        
    Returns:
        Chemistry bias (0-100)
    """
    pdkt_names = get_pdkt_names_with_bias()
    
    for item in pdkt_names:
        if isinstance(item, dict) and item['nama'] == nama:
            return item['chemistry_bias']
    
    return 50  # Default


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
        selected = names[rank - 1]
        if isinstance(selected, dict):
            return selected['nama']
        return selected
    
    # Fallback ke random
    return get_random_name(role)


def get_all_names_for_role(role: str) -> List[str]:
    """Dapatkan semua nama yang tersedia untuk role tertentu"""
    names = ROLE_NAMES.get(role, ROLE_NAMES["pdkt"])
    
    result = []
    for item in names:
        if isinstance(item, dict):
            result.append(item['nama'])
        else:
            result.append(item)
    
    return result


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
    
    # Cek apakah sudah ada
    for item in ROLE_NAMES[role]:
        if isinstance(item, dict) and item['nama'] == name:
            return False
        if item == name:
            return False
    
    ROLE_NAMES[role].append(name)
    logger.info(f"Added custom name '{name}' to role '{role}'")
    return True


def add_custom_pdkt_name(name: str, hint: str, chemistry_bias: int) -> bool:
    """
    Tambah nama PDKT kustom dengan chemistry bias
    
    Args:
        name: Nama
        hint: Hint tentang nama
        chemistry_bias: Bias chemistry (0-100)
        
    Returns:
        True jika berhasil
    """
    if "pdkt" not in ROLE_NAMES:
        ROLE_NAMES["pdkt"] = []
    
    # Cek duplikasi
    for item in ROLE_NAMES["pdkt"]:
        if isinstance(item, dict) and item['nama'] == name:
            return False
    
    ROLE_NAMES["pdkt"].append({
        'nama': name,
        'hint': hint,
        'chemistry_bias': chemistry_bias
    })
    
    logger.info(f"Added custom PDKT name '{name}' with bias {chemistry_bias}")
    return True


def remove_custom_name(role: str, name: str) -> bool:
    """
    Hapus nama kustom dari role (untuk admin)
    
    Args:
        role: Nama role
        name: Nama yang akan dihapus
        
    Returns:
        True jika berhasil, False jika tidak ditemukan
    """
    if role in ROLE_NAMES:
        for i, item in enumerate(ROLE_NAMES[role]):
            if isinstance(item, dict) and item['nama'] == name:
                ROLE_NAMES[role].pop(i)
                logger.info(f"Removed custom name '{name}' from role '{role}'")
                return True
            elif item == name:
                ROLE_NAMES[role].pop(i)
                logger.info(f"Removed custom name '{name}' from role '{role}'")
                return True
    
    return False


def get_name_statistics() -> Dict:
    """Dapatkan statistik database nama"""
    stats = {
        "total_names": 0,
        "roles": {}
    }
    
    for role, names in ROLE_NAMES.items():
        role_count = len(names)
        stats["total_names"] += role_count
        
        # Sample 5 nama pertama
        samples = []
        for item in names[:5]:
            if isinstance(item, dict):
                samples.append(f"{item['nama']} (bias:{item['chemistry_bias']})")
            else:
                samples.append(item)
        
        stats["roles"][role] = {
            "count": role_count,
            "names": samples
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
    
    if role == "pdkt":
        return f"{name} ✨"
    
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
    
    def get_pdkt_bias(self, name: str) -> int:
        return get_pdkt_chemistry_bias(name)


# Inisialisasi singleton
name_db = NameDatabase()

logger.info(f"✅ Name database initialized with {get_name_statistics()['total_names']} names across 9 roles")
logger.info(f"   PDKT: {len(ROLE_NAMES['pdkt'])} names with chemistry bias")


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    'ROLE_NAMES',
    'UNISEX_NAMES',
    'INTERNATIONAL_NAMES',
    'get_random_name',
    'get_random_name_with_hint',
    'get_pdkt_chemistry_bias',
    'get_name_by_popularity',
    'get_all_names_for_role',
    'add_custom_name',
    'add_custom_pdkt_name',
    'remove_custom_name',
    'get_name_statistics',
    'format_name_for_display',
    'name_db'
]
