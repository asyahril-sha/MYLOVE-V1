#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - NAME DETECTOR (FILE BARU)
=============================================================================
Fitur deteksi nama bot yang SUPER PINTAR
- Generate alias untuk nama bot
- Deteksi panggilan dalam pesan user
- Analisa subjek (aku/kamu/kita/panggilan nama)
- TIDAK MENGUBAH file existing
=============================================================================
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)


class NameDetector:
    """
    Detektor nama bot yang SUPER PINTAR
    - Generate berbagai variasi panggilan
    - Deteksi apakah user memanggil bot
    - Bisa digunakan oleh file lain tanpa mengubah strukturnya
    """
    
    def __init__(self):
        # Database panggilan umum Indonesia
        self.common_calls = {
            'dewi': ['wi', 'dew', 'dedew'],
            'sari': ['sa', 'ari', 'sasa'],
            'putri': ['put', 'tri', 'putput'],
            'ratna': ['rat', 'atna', 'rara'],
            'wulan': ['wul', 'lan', 'wuwul'],
            'kartika': ['tika', 'karti', 'ika', 'kaka'],
            'lestari': ['tari', 'lesta', 'ari', 'lala'],
            'puspa': ['pus', 'pa', 'puspus'],
            'aurora': ['rora', 'auri', 'ora', 'rara'],
            'kirana': ['kira', 'rana', 'nana'],
            'amanda': ['mand', 'anda', 'mama'],
            'cantika': ['tika', 'cantik', 'ika', 'caca'],
            'maharani': ['rani', 'maha', 'ara', 'nana'],
            'prilly': ['pil', 'lili', 'pri'],
            'natasha': ['tasha', 'nana', 'asha'],
        }
        
        logger.info("✅ NameDetector initialized")
    
    # =========================================================================
    # GENERATE ALIAS UNTUK NAMA BOT
    # =========================================================================
    
    def generate_aliases(self, bot_name: str) -> List[str]:
        """
        Generate alias yang MANUSIAWI untuk nama bot
        Bot bisa dipanggil dengan berbagai variasi natural
        
        Args:
            bot_name: Nama bot (contoh: "Kartika")
            
        Returns:
            List of aliases (contoh: ['kartika', 'tika', 'karti', 'ika', ...])
        """
        name = bot_name.lower()
        aliases = {name}  # Pakai set dulu untuk hindari duplikat
        
        # ===== ATURAN 1: Ambil suku kata yang umum di Indonesia =====
        common_suffixes = ['ka', 'ta', 'na', 'ra', 'ni', 'ti', 'ri', 'ya', 'ma']
        common_prefixes = ['de', 'wi', 'pu', 'su', 'ra', 'ma', 'sa', 'ci']
        
        # Cek suffix yang umum
        for suffix in common_suffixes:
            if name.endswith(suffix):
                # Ambil nama tanpa suffix + 1 huruf suffix
                base = name[:-len(suffix)]
                if base:
                    aliases.add(base + suffix[0])
                aliases.add(suffix)
        
        # Cek prefix yang umum
        for prefix in common_prefixes:
            if name.startswith(prefix):
                aliases.add(prefix)
                if len(name) > len(prefix):
                    aliases.add(name[len(prefix):])
        
        # ===== ATURAN 2: 2-4 huruf pertama/akhir =====
        if len(name) >= 3:
            aliases.add(name[:3])  # 3 huruf pertama
            aliases.add(name[-3:])  # 3 huruf terakhir
        
        if len(name) >= 4:
            aliases.add(name[:4])  # 4 huruf pertama
            aliases.add(name[-4:])  # 4 huruf terakhir
        
        if len(name) >= 5:
            aliases.add(name[:2] + name[-2:])  # 2 awal + 2 akhir
            aliases.add(name[0] + name[-2:])   # 1 awal + 2 akhir
        
        # ===== ATURAN 3: Nama panggilan umum Indonesia =====
        for key, values in self.common_calls.items():
            if key in name or name in key:
                for val in values:
                    aliases.add(val)
        
        # ===== ATURAN 4: Nama dengan huruf diganti =====
        # Ganti 'a' dengan 'i' untuk variasi
        if 'a' in name:
            aliases.add(name.replace('a', 'i'))
        
        # Ganti 'i' dengan 'e'
        if 'i' in name:
            aliases.add(name.replace('i', 'e'))
        
        # ===== ATURAN 5: Buang huruf vokal =====
        vowels = 'aiueo'
        without_vowels = ''.join([c for c in name if c not in vowels])
        if 2 <= len(without_vowels) <= 5:
            aliases.add(without_vowels)
        
        # ===== ATURAN 6: Nama dengan pengulangan =====
        if len(name) >= 4:
            aliases.add(name[:2] + name[:2])  # 2 huruf pertama diulang
            aliases.add(name[-2:] + name[-2:])  # 2 huruf terakhir diulang
        
        # ===== ATURAN 7: Nama dengan tambahan 'y' =====
        if len(name) >= 3:
            aliases.add(name + 'y')
            aliases.add(name[:3] + 'y')
        
        # Konversi set ke list, filter yang terlalu pendek (<2) atau terlalu panjang (>10)
        aliases = [a for a in aliases if 2 <= len(a) <= 10]
        
        # Urutkan berdasarkan panjang (pendek duluan)
        aliases.sort(key=len)
        
        logger.debug(f"📇 Generated {len(aliases)} aliases for '{bot_name}': {aliases[:5]}...")
        
        return aliases
    
    # =========================================================================
    # DETEKSI NAMA DALAM PESAN
    # =========================================================================
    
    def detect_name_in_message(self, message: str, aliases: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Deteksi apakah user memanggil bot dengan namanya
        
        Args:
            message: Pesan user
            aliases: Daftar alias nama bot
            
        Returns:
            (terdeteksi, alias_yang_dipakai)
        """
        msg_lower = message.lower()
        
        # Pattern umum panggilan nama
        patterns = [
            r'^{}\s',           # Di awal kalimat + spasi
            r'\s{}\s',          # Di tengah kalimat
            r'\s{}$',           # Di akhir kalimat
            r'^{}$',            # Satu kata saja
            r'{}[!.,;?]',       # Diikuti tanda baca
            r'{}[,.]',          # Diikuti koma/titik
        ]
        
        for alias in aliases:
            alias_lower = alias.lower()
            
            # Skip kalau terlalu pendek
            if len(alias_lower) < 2:
                continue
            
            # Cek berbagai pattern
            for pattern_template in patterns:
                pattern = pattern_template.format(re.escape(alias_lower))
                if re.search(pattern, msg_lower):
                    return True, alias
        
        # Cek juga panggilan dengan "kak" + nama
        for alias in aliases[:5]:  # Cek 5 alias terpendek
            if f"kak {alias}" in msg_lower or f"kak{alias}" in msg_lower:
                return True, f"kak {alias}"
        
        return False, None
    
    # =========================================================================
    # ANALISA SUBJEK LENGKAP
    # =========================================================================
    
    def analyze_subject(self, message: str, bot_aliases: List[str]) -> Dict[str, Any]:
        """
        Analisa subjek dari pesan user secara lengkap
        
        Args:
            message: Pesan user
            bot_aliases: Daftar alias nama bot
            
        Returns:
            Dict dengan info subjek
        """
        msg_lower = message.lower()
        
        # ===== 1. DETEKSI NAMA BOT =====
        bot_mentioned, used_alias = self.detect_name_in_message(message, bot_aliases)
        
        # ===== 2. DETEKSI SUBJEK DASAR =====
        has_self = any(word in msg_lower for word in ['aku ', 'aku$', 'saya ', 'gue ', 'gw '])
        has_bot = any(word in msg_lower for word in ['kamu ', 'lu ', 'elo ', 'bot '])
        has_together = any(word in msg_lower for word in ['kita ', 'bareng ', 'bersama '])
        
        # ===== 3. DETEKSI JENIS KALIMAT =====
        is_question = '?' in msg_lower or any(q in msg_lower for q in ['apa', 'siapa', 'kenapa', 'bagaimana'])
        is_command = any(cmd in msg_lower for cmd in ['ke ', 'pindah', 'kesini', 'sini', 'ayo'])
        
        # ===== 4. LOGIKA KEPUTUSAN =====
        if bot_mentioned:
            # User memanggil nama bot → subjek = bot
            subject = 'bot'
            confidence = 0.95
            reason = f"dipanggil dengan '{used_alias}'"
        elif has_together:
            subject = 'together'
            confidence = 0.9
            reason = "ada kata 'kita'"
        elif has_bot:
            subject = 'bot'
            confidence = 0.85
            reason = "ada kata 'kamu'"
        elif has_self:
            subject = 'self'
            confidence = 0.9
            reason = "ada kata 'aku'"
        elif is_question:
            subject = 'question'
            confidence = 0.7
            reason = "pertanyaan"
        elif is_command:
            # Perintah tanpa subjek jelas, asumsikan untuk bot
            subject = 'bot'
            confidence = 0.6
            reason = "perintah tanpa subjek"
        else:
            subject = 'unknown'
            confidence = 0.5
            reason = "tidak jelas"
        
        return {
            'subject': subject,
            'confidence': round(confidence, 2),
            'reason': reason,
            'mentioned_bot': bot_mentioned,
            'bot_alias': used_alias,
            'has_self': has_self,
            'has_bot': has_bot,
            'has_together': has_together,
            'is_question': is_question,
            'is_command': is_command,
            'raw_message': message[:50]
        }
    
    # =========================================================================
    # FORMAT RESPON BERDASARKAN ANALISA
    # =========================================================================
    
    def get_suggested_response(self, analysis: Dict, bot_name: str, bot_location: str) -> str:
        """
        Dapatkan saran respons berdasarkan analisa subjek
        
        Args:
            analysis: Hasil dari analyze_subject()
            bot_name: Nama bot
            bot_location: Lokasi bot saat ini
            
        Returns:
            Saran respons
        """
        subject = analysis['subject']
        
        if subject == 'self':
            return f"Kamu cerita tentang dirimu? Aku dengerin."
        
        elif subject == 'bot':
            if analysis['mentioned_bot']:
                alias = analysis['bot_alias'] or bot_name
                return f"Iya {alias}, ada apa?"
            else:
                return f"Aku di {bot_location}. Ada yang bisa dibantu?"
        
        elif subject == 'together':
            return "Ayo!"
        
        elif subject == 'question':
            return f"Aku di {bot_location}. Kamu?"
        
        else:
            return f"Aku di {bot_location}."


# Singleton instance
_name_detector = None

def get_name_detector() -> NameDetector:
    """Dapatkan instance NameDetector (singleton)"""
    global _name_detector
    if _name_detector is None:
        _name_detector = NameDetector()
    return _name_detector


__all__ = ['NameDetector', 'get_name_detector']
