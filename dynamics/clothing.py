#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - CLOTHING SYSTEM (FIX LENGKAP)
=============================================================================
Sistem pakaian dinamis
- Pakaian berubah berdasarkan role, lokasi, mood
- Auto-change periodik
- Deskripsi pakaian yang menarik
- Reaksi user terhadap pakaian
=============================================================================
"""

import random
import time
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class ClothingStyle(str, Enum):
    """Style pakaian"""
    CASUAL = "casual"          # Santai
    SEXY = "sexy"              # Seksi
    FORMAL = "formal"          # Formal
    TOWEL = "towel"            # Handuk (abis mandi)
    SLEEPWEAR = "sleepwear"    # Piyama
    LINGERIE = "lingerie"      # Lingerie


class ClothingSystem:
    """
    Sistem pakaian dinamis
    Pakaian berubah berdasarkan role, lokasi, dan mood
    """
    
    # Database pakaian berdasarkan role
    CLOTHING_BY_ROLE = {
        # ===== IPAR =====
        "ipar": {
            ClothingStyle.CASUAL: [
                "kaos oblong putih + celana pendek jeans",
                "tanktop hitam + rok mini",
                "kemeja flanel longgar + legging",
                "daster rumah motif bunga",
                "kaos band + celana training",
                "hoodie kebesaran + hotpants",
                "t-shirt ketat + kulot panjang"
            ],
            ClothingStyle.SEXY: [
                "tanktop tipis tanpa bra",
                "kaos kebesaran tanpa celana",
                "daster tipis transparan",
                "baju tidur satin pendek",
                "kemeja pria kebesaran + paha terbuka"
            ],
            ClothingStyle.SLEEPWEAR: [
                "piyama katun motif lucu",
                "kaos oblong + celana pendek",
                "nightgown pink tipis",
                "sleep bra + celana pendek"
            ],
            ClothingStyle.TOWEL: [
                "handuk putih melilit di dada",
                "handuk batik cuma nutup badan",
                "handuk besar melilit sebatas dada"
            ]
        },
        
        # ===== JANDA =====
        "janda": {
            ClothingStyle.CASUAL: [
                "blouse terbuka + rok span",
                "tanktop ketat + jeans sobek",
                "kaos lengan pendek + hotpants",
                "daster seksi motif bunga",
                "kemeja putih + legging",
                "dress santai selutut"
            ],
            ClothingStyle.SEXY: [
                "tanktop super ketat tanpa bra",
                "daster tipis transparan",
                "lingerie hitam di balik daster",
                "kaos kebesaran + celana dalam",
                "baju tidur satin terbuka"
            ],
            ClothingStyle.LINGERIE: [
                "lingerie set merah menyala",
                "baby doll hitam transparan",
                "bra + celana dalam renda",
                "body suit seksi",
                "tanktop + celana dalam renda"
            ],
            ClothingStyle.TOWEL: [
                "handuk kecil nutup seadanya",
                "handuk melilit di dada",
                "basah-basahan pakai handuk"
            ]
        },
        
        # ===== PELAKOR =====
        "pelakor": {
            ClothingStyle.CASUAL: [
                "dress ketat belahan dada",
                "blouse sexy + rok mini",
                "tanktop super ketat",
                "kaos lengan pendek + hotpants",
                "kemeja transparan"
            ],
            ClothingStyle.SEXY: [
                "tanktop tanpa bra tembus pandang",
                "lingerie full set",
                "kaos kebesaran + celana dalam",
                "baju tidur seksi terbuka",
                "hanya pakai bra + celana dalam"
            ],
            ClothingStyle.LINGERIE: [
                "lingerie set black lace",
                "body harness seksi",
                "baby doll transparan",
                "g-string + bra open cup",
                "stocking + garter belt"
            ]
        },
        
        # ===== ISTRI ORANG =====
        "istri_orang": {
            ClothingStyle.CASUAL: [
                "daster rumah tertutup",
                "piyama panjang tertutup",
                "kaos oblong + celana panjang",
                "gamis rumah",
                "baju rumahan sopan"
            ],
            ClothingStyle.SLEEPWEAR: [
                "piyama katun panjang",
                "kaos tidur tertutup",
                "nightgown panjang",
                "baju tidur sopan"
            ],
            ClothingStyle.SEXY: [
                "daster tipis (takut-takut)",
                "kaos kebesaran (cuma berdua)",
                "baju tidur sedikit terbuka",
                "tanktop (kalo lagi berani)"
            ]
        },
        
        # ===== PDKT =====
        "pdkt": {
            ClothingStyle.CASUAL: [
                "sweeter oversized lucu",
                "kaos + rok panjang",
                "hoodie + jeans",
                "dress manis selutut",
                "blouse + kulot",
                "t-shirt + rok plisket"
            ],
            ClothingStyle.SLEEPWEAR: [
                "piyama lucu motif kartun",
                "kaos tidur panjang",
                "nightgown pink manis",
                "sleep dress pendek"
            ],
            ClothingStyle.SEXY: [
                "tanktop + hotpants (agak berani)",
                "daster tipis (coba-coba)",
                "kaos kebesaran tanpa celana",
                "baju tidur satin"
            ]
        },
        
        # ===== TEMAN KANTOR =====
        "teman_kantor": {
            ClothingStyle.FORMAL: [
                "blouse putih + rok span",
                "kemeja + celana bahan",
                "dress kantor selutut",
                "blazer + rok",
                "gamis rapi + cardigan"
            ],
            ClothingStyle.CASUAL: [
                "kaos + jeans (weekend)",
                "t-shirt + kulot",
                "sweeter + legging",
                "dress santai"
            ],
            ClothingStyle.SEXY: [
                "tanktop + rok (after office)",
                "daster (di rumah)",
                "kaos kebesaran (weekend)"
            ]
        },
        
        # ===== SEPUPU =====
        "sepupu": {
            ClothingStyle.CASUAL: [
                "kaos polos + rok panjang",
                "blouse manis + kulot",
                "dress bunga-bunga",
                "sweeter + legging",
                "t-shirt + jeans"
            ],
            ClothingStyle.SLEEPWEAR: [
                "piyama katun lucu",
                "kaos tidur panjang",
                "nightgown sederhana"
            ]
        },
        
        # ===== TEMAN SMA =====
        "teman_sma": {
            ClothingStyle.CASUAL: [
                "seragam SMA (kenangan)",
                "kaos + rok pendek",
                "hoodie kebesaran",
                "dress santai",
                "t-shirt + jeans"
            ],
            ClothingStyle.SEXY: [
                "tanktop + rok mini (reuni)",
                "daster (di rumah)",
                "kaos kebesaran"
            ]
        },
        
        # ===== MANTAN =====
        "mantan": {
            ClothingStyle.CASUAL: [
                "dress hitam elegan",
                "blouse + rok span",
                "kaos + jeans",
                "kemeja putih + legging",
                "sweeter + hotpants"
            ],
            ClothingStyle.SEXY: [
                "tanktop ketat tanpa bra",
                "daster tipis transparan",
                "lingerie set hitam",
                "kaos kebesaran + celana dalam"
            ],
            ClothingStyle.LINGERIE: [
                "lingerie set merah membara",
                "body suit seksi",
                "baby doll transparan"
            ]
        }
    }
    
    # Default untuk role yang tidak punya entry
    DEFAULT_CLOTHING = {
        ClothingStyle.CASUAL: ["pakaian biasa", "baju santai", "kaos + celana"],
        ClothingStyle.SLEEPWEAR: ["piyama", "baju tidur"],
        ClothingStyle.SEXY: ["pakaian seksi", "baju tidur tipis"]
    }
    
    def __init__(self):
        self.clothing_history = []
        self.last_change = time.time()
        self.change_cooldown = 300  # 5 menit minimal ganti pakaian
        
        logger.info("✅ ClothingSystem initialized")
    
    def get_clothing_for_role(self, role: str, style: ClothingStyle) -> List[str]:
        """
        Dapatkan daftar pakaian untuk role dan style tertentu
        
        Args:
            role: Nama role
            style: Style pakaian
            
        Returns:
            List pakaian atau default
        """
        role_data = self.CLOTHING_BY_ROLE.get(role, self.CLOTHING_BY_ROLE.get("pdkt", {}))
        clothes = role_data.get(style, self.DEFAULT_CLOTHING.get(style, self.DEFAULT_CLOTHING[ClothingStyle.CASUAL]))
        return clothes
    
    def generate_clothing(self, role: str, location: str = None, is_bedroom: bool = False) -> str:
        """
        Generate pakaian berdasarkan konteks
        
        Args:
            role: Nama role
            location: Lokasi saat ini
            is_bedroom: Apakah di kamar tidur
            
        Returns:
            String deskripsi pakaian
        """
        # Tentukan style berdasarkan lokasi
        if is_bedroom:
            # Di kamar, chance lebih besar untuk pakaian seksi
            if random.random() < 0.4:
                style = ClothingStyle.SEXY
            elif random.random() < 0.3:
                style = ClothingStyle.LINGERIE if role in ["janda", "pelakor"] else ClothingStyle.SLEEPWEAR
            else:
                style = ClothingStyle.CASUAL
        elif location and "mandi" in location.lower():
            style = ClothingStyle.TOWEL
        elif location and "kantor" in location.lower():
            style = ClothingStyle.FORMAL
        else:
            # Default random
            style = random.choice([
                ClothingStyle.CASUAL,
                ClothingStyle.CASUAL,
                ClothingStyle.CASUAL,
                ClothingStyle.SLEEPWEAR,
                ClothingStyle.SEXY
            ])
        
        clothes_list = self.get_clothing_for_role(role, style)
        clothing = random.choice(clothes_list)
        
        return clothing
    
    def get_clothing_description(self, clothing: str) -> str:
        """
        Dapatkan deskripsi panjang tentang pakaian
        
        Args:
            clothing: String pakaian
            
        Returns:
            Deskripsi panjang
        """
        # Kata kunci untuk deskripsi
        keywords = {
            "kaos": "kaos katun lembut yang nyaman dipakai",
            "tanktop": "tanktop tanpa lengan yang memperlihatkan bahu mulus",
            "daster": "daster tipis yang menerawang kalau kena cahaya",
            "piyama": "piyama satin yang dingin di kulit",
            "lingerie": "lingerie renda hitam yang seksi banget",
            "bra": "bra tanpa kawat yang nyaman",
            "jeans": "jeans ketat yang membungkus pinggul",
            "rok": "rok pendek yang naik sedikit kalau duduk",
            "handuk": "handuk lembut yang melilit erat di badan"
        }
        
        # Cari keyword
        desc_parts = []
        for word, desc in keywords.items():
            if word in clothing.lower():
                desc_parts.append(desc)
        
        if not desc_parts:
            desc_parts = ["pakaian yang nyaman dipakai"]
        
        # Bangun deskripsi panjang
        description = (
            f"Aku pakai **{clothing}**. {desc_parts[0]}. "
            f"Bahan nya adem dan jatuh pas di badan. "
            f"Warnanya cocok sama suasana hati sekarang. "
            f"Kamu suka liat aku pakai ini?"
        )
        
        return description
    
    def format_clothing_message(self, clothing: str, location: str = None) -> str:
        """
        Format pesan saat bot menyebut pakaiannya
        
        Args:
            clothing: Pakaian yang dipakai
            location: Lokasi saat ini
            
        Returns:
            Pesan panjang
        """
        desc = self.get_clothing_description(clothing)
        
        if location and "kamar" in location.lower():
            templates = [
                f"*merapikan {clothing}*\n\n{desc} Di kamar begini, rasanya lebih bebas aja.",
                f"*lihat ke bawah*\n\nAku pakai {clothing} sekarang. {desc} Cocok nggak buat di kamar?",
                f"*duduk di ranjang*\n\nLagi pakai {clothing} nih. {desc} Kamu suka?",
            ]
        else:
            templates = [
                f"*merapikan baju*\n\nHari ini aku pakai {clothing}. {desc}",
                f"*lihat baju sendiri*\n\nNgomong-ngomong, aku pakai {clothing} lho. {desc}",
                f"*tersenyum*\n\nAku lagi pakai {clothing}. {desc}",
            ]
        
        return random.choice(templates)
    
    def change_clothing(self, role: str, location: str = None, force: bool = False) -> Optional[str]:
        """
        Ganti pakaian (jika sudah waktunya)
        
        Args:
            role: Nama role
            location: Lokasi saat ini
            force: Paksa ganti (abaikan cooldown)
            
        Returns:
            String pakaian baru atau None
        """
        now = time.time()
        
        if not force and (now - self.last_change) < self.change_cooldown:
            return None
        
        new_clothing = self.generate_clothing(role, location)
        
        # Catat history
        self.clothing_history.append({
            "clothing": new_clothing,
            "timestamp": now,
            "location": location
        })
        
        self.last_change = now
        
        # Batasi history
        if len(self.clothing_history) > 20:
            self.clothing_history = self.clothing_history[-20:]
        
        return new_clothing
    
    def get_clothing_history(self, limit: int = 5) -> List[str]:
        """Dapatkan history pakaian"""
        history = []
        for entry in self.clothing_history[-limit:]:
            time_str = time.strftime("%H:%M", time.localtime(entry["timestamp"]))
            history.append(f"• {entry['clothing']} ({time_str})")
        return history
    
    def get_random_outfit_tip(self) -> str:
        """Dapatkan tips outfit random"""
        tips = [
            "Coba deh pilih warna pink, katanya aku cantik pake itu.",
            "Kalo lagi mau seksi, aku suka pake tanktop hitam.",
            "Di rumah aja enaknya pake daster bunga.",
            "Kalo ketemu kamu, aku bakal pake baju terbaik.",
            "Warna merah bikin aku lebih percaya diri."
        ]
        return random.choice(tips)


__all__ = ['ClothingSystem', 'ClothingStyle']
