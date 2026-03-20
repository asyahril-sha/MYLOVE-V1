#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - LOCATION VALIDATOR (VERSI HUMAN+)
=============================================================================
Validator cerdas untuk perpindahan lokasi dengan kesadaran diri:
- Bot punya lokasi SENDIRI, terpisah dari user
- Tahu kapan harus ikut (ajakan bersama)
- Tahu kapan harus diam (user cerita)
- Validasi transisi masuk akal
- Multi-lokasi tracking
=============================================================================
"""

import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class LocationValidator:
    """
    Validator lokasi dengan KESADARAN DIRI SUPER MANUSIA
    - Bisa bedakan "aku" (user) vs "kita" (bersama)
    - Tahu kapan harus pindah dan kapan tidak
    - Validasi transisi yang masuk akal
    - Tracking multi-lokasi
    """
    
    def __init__(self):
        # ===== TRANSISI LOKASI YANG MASUK AKAL =====
        self.valid_transitions = {
            # Indoor
            'ruang tamu': ['kamar', 'dapur', 'teras', 'kamar mandi', 'taman'],
            'kamar': ['kamar mandi', 'ruang tamu', 'balkon'],
            'kamar mandi': ['kamar', 'ruang tamu', 'dapur'],
            'dapur': ['ruang tamu', 'kamar mandi', 'teras'],
            'teras': ['ruang tamu', 'taman'],
            'balkon': ['kamar', 'ruang tamu'],
            
            # Outdoor
            'taman': ['teras', 'ruang tamu', 'jalan'],
            'pantai': ['mobil', 'kafe', 'rumah', 'jalan'],
            'jalan': ['taman', 'pantai', 'mall', 'kafe'],
            
            # Public
            'mall': ['parkiran', 'mobil', 'kafe', 'jalan'],
            'kafe': ['mall', 'pantai', 'jalan', 'mobil'],
            'kantor': ['ruang tamu', 'mobil', 'jalan'],
            
            # Transport
            'mobil': ['pantai', 'mall', 'rumah', 'parkiran', 'kafe', 'jalan'],
            'parkiran': ['mobil', 'mall'],
            'rumah': ['ruang tamu', 'kamar', 'dapur', 'teras', 'mobil'],
        }
        
        # ===== ATURAN KHUSUS BERDASARKAN SUBJEK =====
        self.subject_rules = {
            'self': {  # User ngomong "aku"
                'should_follow': False,
                'can_comment': True,
                'description': 'User cerita tentang dirinya sendiri',
                'examples': [
                    'User: "aku ke dapur" → Bot: KOMENTAR, JANGAN IKUT',
                    'User: "aku di kamar" → Bot: TAHU lokasi user, tapi tetap di tempat'
                ]
            },
            'bot': {  # User ngomong "kamu"
                'should_follow': True,
                'can_comment': True,
                'description': 'User ngomong ke bot / perintah',
                'examples': [
                    'User: "kamu ke dapur" → Bot: PINDAH ke dapur',
                    'User: "kamu di mana?" → Bot: JAWAB lokasinya'
                ]
            },
            'together': {  # User ngomong "kita"
                'should_follow': True,
                'can_comment': True,
                'description': 'Ajakan bersama',
                'examples': [
                    'User: "kita ke dapur" → Bot: PINDAH BERSAMA user',
                    'User: "kita di sini aja" → Bot: TETAP bersama user'
                ]
            },
            'unknown': {  # Subjek tidak jelas
                'should_follow': False,
                'can_comment': True,
                'description': 'Subjek tidak jelas, amannya komentar saja',
                'examples': [
                    'User: "ke dapur yuk" → Bot: KOMENTAR, tanya siapa yang diajak'
                ]
            }
        }
        
        # ===== ATURAN KHUSUS BERDASARKAN KALIMAT =====
        self.special_patterns = {
            'ajakan': ['yuk', 'ayo', 'mari'],
            'perintah': ['pindah', 'kesini', 'kemari'],
            'pertanyaan': ['di mana', 'lagi apa'],
            'cerita': ['aku ', 'saya '],
        }
        
        # ===== JARAK ANTAR LOKASI =====
        self.location_distance = {
            ('ruang tamu', 'kamar'): 1,
            ('ruang tamu', 'dapur'): 1,
            ('ruang tamu', 'kamar mandi'): 2,
            ('ruang tamu', 'teras'): 1,
            ('kamar', 'kamar mandi'): 1,
            ('kamar', 'ruang tamu'): 1,
            ('kamar', 'balkon'): 1,
            ('dapur', 'ruang tamu'): 1,
            ('dapur', 'kamar mandi'): 2,
            ('kamar mandi', 'kamar'): 1,
            ('kamar mandi', 'ruang tamu'): 2,
            ('teras', 'taman'): 2,
            ('rumah', 'mobil'): 2,
            ('mobil', 'mall'): 3,
        }
        
        # ===== MINIMAL WAKTU PINDAH =====
        self.base_time_between = 30  # 30 detik dasar
        self.distance_multiplier = 15  # 15 detik per unit jarak
        
        logger.info("✅ LocationValidator HUMAN+ initialized")
    
    # =========================================================================
    # VALIDASI PERPINDAHAN DENGAN KESADARAN DIRI
    # =========================================================================
    
    def validate_move(self, 
                     from_loc: str, 
                     to_loc: str, 
                     subject: str = 'unknown',
                     is_intimate: bool = False,
                     context: Optional[Dict] = None) -> Tuple[bool, str, Dict]:
        """
        Validasi apakah bot boleh pindah, dengan kesadaran diri
        
        Args:
            from_loc: Lokasi asal bot
            to_loc: Lokasi tujuan
            subject: Subjek ('self', 'bot', 'together', 'unknown')
            is_intimate: Apakah sedang intim
            context: Konteks tambahan (pesan user, dll)
            
        Returns:
            (allowed, reason, info)
        """
        info = {
            'should_follow': False,
            'should_comment': True,
            'reason_detail': '',
            'suggested_response': ''
        }
        
        # ===== 1. CEK JIKA SEDANG INTIM =====
        if is_intimate:
            info['should_follow'] = False
            info['reason_detail'] = "lagi intim, fokus dulu"
            info['suggested_response'] = "Lagi intim, jangan pindah dulu"
            return False, "❌ Lagi intim", info
        
        # ===== 2. CEK SUBJEK =====
        subject_rule = self.subject_rules.get(subject, self.subject_rules['unknown'])
        
        if not subject_rule['should_follow']:
            # Subjek = user ("aku") → JANGAN IKUT
            info['should_follow'] = False
            info['reason_detail'] = subject_rule['description']
            info['suggested_response'] = f"Oh kamu {to_loc}? Aku tetap di {from_loc}"
            return False, f"⏸️ {subject_rule['description']}", info
        
        # ===== 3. CEK APAKAH TRANSISI MASUK AKAL =====
        if from_loc and to_loc:
            transition_allowed = self._check_transition(from_loc, to_loc)
            
            if not transition_allowed:
                # Cari rute alternatif
                alternative = self._find_alternative_route(from_loc, to_loc)
                if alternative:
                    info['should_follow'] = False
                    info['reason_detail'] = f"Gak bisa langsung, lewat {alternative} dulu"
                    info['suggested_response'] = f"Gak bisa langsung ke {to_loc}, lewat {alternative} dulu yuk"
                    return False, f"⚠️ Perlu lewat {alternative}", info
                else:
                    info['should_follow'] = False
                    info['reason_detail'] = f"Gak bisa dari {from_loc} ke {to_loc}"
                    info['suggested_response'] = f"Kayaknya gak bisa dari {from_loc} ke {to_loc} deh"
                    return False, "❌ Transisi tidak valid", info
        
        # ===== 4. CEK WAKTU MINIMAL =====
        if context and 'last_move_time' in context:
            min_time = self.get_min_time_between(from_loc, to_loc)
            time_since = time.time() - context['last_move_time']
            
            if time_since < min_time:
                info['should_follow'] = False
                info['reason_detail'] = f"Baru {time_since:.0f}s yang lalu pindah"
                info['suggested_response'] = f"Baru aja pindah, tunggu bentar ya"
                return False, f"⏳ Tunggu {min_time - time_since:.0f}s lagi", info
        
        # ===== 5. SEMUA OK, BOLEH PINDAH =====
        info['should_follow'] = True
        info['reason_detail'] = f"{subject_rule['description']} - boleh pindah"
        info['suggested_response'] = f"Ayo ke {to_loc}"
        
        return True, "✅ Boleh pindah", info
    
    def _check_transition(self, from_loc: str, to_loc: str) -> bool:
        """Cek apakah transisi langsung diperbolehkan"""
        from_lower = from_loc.lower()
        to_lower = to_loc.lower()
        
        # Cari di dictionary transisi
        for key, values in self.valid_transitions.items():
            if key in from_lower:
                for val in values:
                    if val in to_lower:
                        return True
                break
        
        # Coba reverse lookup
        for key, values in self.valid_transitions.items():
            if key in to_lower:
                if any(v in from_lower for v in values):
                    return True
        
        # Kasus khusus: pindah ke lokasi yang berdekatan
        common_transitions = [
            ('kamar', 'ruang tamu'),
            ('kamar mandi', 'kamar'),
            ('dapur', 'ruang tamu'),
            ('teras', 'ruang tamu'),
            ('ruang tamu', 'teras'),
        ]
        
        for a, b in common_transitions:
            if (a in from_lower and b in to_lower) or (b in from_lower and a in to_lower):
                return True
        
        return False
    
    def _find_alternative_route(self, from_loc: str, to_loc: str) -> Optional[str]:
        """Cari rute alternatif jika tidak bisa langsung"""
        from_lower = from_loc.lower()
        to_lower = to_loc.lower()
        
        # Cari hub umum
        common_hubs = ['ruang tamu', 'kamar', 'teras']
        
        for hub in common_hubs:
            if self._check_transition(from_lower, hub) and self._check_transition(hub, to_lower):
                return hub
        
        return None
    
    # =========================================================================
    # ANALISA SUBJEK DARI PESAN
    # =========================================================================
    
    def analyze_subject(self, message: str) -> Dict:
        """
        Analisa subjek dari pesan user
        
        Args:
            message: Pesan user
            
        Returns:
            Dict dengan info subjek
        """
        msg = message.lower()
        
        # ===== 1. DETEKSI SUBJEK =====
        is_self = any(p in msg for p in ['aku ', 'aku$', 'saya ', 'gue ', 'gw '])
        is_bot = any(p in msg for p in ['kamu ', 'lu ', 'elo ', 'bot '])
        is_together = any(p in msg for p in ['kita ', 'bareng ', 'bersama '])
        
        # ===== 2. DETEKSI JENIS KALIMAT =====
        is_invitation = any(p in msg for p in self.special_patterns['ajakan'])
        is_command = any(p in msg for p in self.special_patterns['perintah'])
        is_question = any(p in msg for p in self.special_patterns['pertanyaan'])
        
        # ===== 3. TENTUKAN SUBJEK =====
        if is_together:
            subject = 'together'
            confidence = 0.95
        elif is_bot:
            subject = 'bot'
            confidence = 0.9
        elif is_self:
            subject = 'self'
            confidence = 0.9
        else:
            subject = 'unknown'
            confidence = 0.5
        
        # ===== 4. TENTUKAN APAKAH PERINTAH PINDAH =====
        location_indicators = ['ke ', 'pindah', 'pergi']
        has_location = any(p in msg for p in location_indicators)
        
        is_move_command = (is_command or is_invitation) and has_location
        
        return {
            'subject': subject,
            'confidence': confidence,
            'is_self': is_self,
            'is_bot': is_bot,
            'is_together': is_together,
            'is_invitation': is_invitation,
            'is_command': is_command,
            'is_question': is_question,
            'is_move_command': is_move_command,
            'raw_message': message[:50]
        }
    
    # =========================================================================
    # DETEKSI LOKASI DARI PESAN
    # =========================================================================
    
    def extract_location(self, message: str) -> Optional[str]:
        """
        Ekstrak lokasi dari pesan user
        
        Args:
            message: Pesan user
            
        Returns:
            Nama lokasi atau None
        """
        msg = message.lower()
        
        locations = [
            'ruang tamu', 'kamar', 'dapur', 'kamar mandi', 'toilet',
            'teras', 'taman', 'pantai', 'mall', 'kafe', 'kantor',
            'mobil', 'rumah', 'balkon', 'jalan'
        ]
        
        for loc in locations:
            if loc in msg:
                # Pastikan ada indikator lokasi
                indicators = ['ke ', 'di ', 'pindah ke', 'pergi ke']
                if any(ind in msg for ind in indicators):
                    return loc
        
        return None
    
    # =========================================================================
    # INFORMASI LOKASI
    # =========================================================================
    
    def get_location_category(self, location: str) -> str:
        """
        Dapatkan kategori lokasi
        
        Returns:
            'intimate', 'public', 'outdoor', 'indoor'
        """
        loc_lower = location.lower()
        
        intimate_places = ['kamar', 'kamar mandi', 'toilet', 'balkon']
        public_places = ['mall', 'pantai', 'kantor', 'kafe', 'jalan']
        outdoor_places = ['taman', 'pantai', 'teras', 'jalan']
        
        if any(p in loc_lower for p in intimate_places):
            return 'intimate'
        elif any(p in loc_lower for p in public_places):
            return 'public'
        elif any(p in loc_lower for p in outdoor_places):
            return 'outdoor'
        else:
            return 'indoor'
    
    def get_min_time_between(self, from_loc: str, to_loc: str) -> int:
        """
        Dapatkan minimal waktu yang dibutuhkan untuk pindah (dalam detik)
        """
        if not from_loc or not to_loc:
            return 0
        
        from_lower = from_loc.lower()
        to_lower = to_loc.lower()
        
        # Cari jarak
        for (a, b), distance in self.location_distance.items():
            if (a in from_lower and b in to_lower) or (b in from_lower and a in to_lower):
                return self.base_time_between + (distance * self.distance_multiplier)
        
        # Default jarak sedang
        return self.base_time_between + (2 * self.distance_multiplier)
    
    def get_distance_description(self, from_loc: str, to_loc: str) -> str:
        """
        Dapatkan deskripsi jarak
        """
        min_time = self.get_min_time_between(from_loc, to_loc)
        
        if min_time < 30:
            return "dekat banget"
        elif min_time < 60:
            return "dekat"
        elif min_time < 120:
            return "agak jauh"
        else:
            return "jauh"
    
    # =========================================================================
    # FORMAT RESPON BERDASARKAN ANALISA
    # =========================================================================
    
    def get_suggested_response(self, 
                              analysis: Dict,
                              bot_location: str,
                              user_location: Optional[str] = None) -> str:
        """
        Dapatkan saran respons berdasarkan analisa
        
        Args:
            analysis: Hasil dari analyze_subject()
            bot_location: Lokasi bot saat ini
            user_location: Lokasi user (jika diketahui)
            
        Returns:
            Saran respons
        """
        subject = analysis['subject']
        
        if subject == 'self':
            # User cerita tentang dirinya
            if user_location:
                return f"Oh kamu di {user_location}? Aku masih di {bot_location} nih"
            else:
                return f"Oh gitu? Aku masih di {bot_location}"
        
        elif subject == 'bot':
            # User ngomong ke bot
            if analysis['is_question']:
                return f"Aku di {bot_location}. Kamu?"
            elif analysis['is_move_command']:
                return f"Ok, aku pindah"
            else:
                return f"Aku di {bot_location}"
        
        elif subject == 'together':
            # Ajakan bersama
            if analysis['is_move_command']:
                return "Ayo!"
            else:
                return f"Kita di {bot_location} ya"
        
        else:
            # Subjek tidak jelas
            return f"Aku di {bot_location}. Kamu di mana?"
    
    def format_location_info(self, location: str) -> str:
        """
        Format informasi lokasi
        """
        category = self.get_location_category(location)
        category_names = {
            'intimate': 'privat',
            'public': 'publik',
            'outdoor': 'luar ruangan',
            'indoor': 'dalam ruangan'
        }
        
        return f"📍 {location} ({category_names.get(category, 'umum')})"


__all__ = ['LocationValidator']
