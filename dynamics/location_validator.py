#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - LOCATION VALIDATOR
=============================================================================
Memvalidasi perubahan lokasi agar masuk akal
- Tidak bisa pindah dari kamar mandi langsung ke pantai
- Minimal waktu antar pindah
- Validasi aktivitas berdasarkan lokasi
=============================================================================
"""

import time
import logging
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)


class LocationValidator:
    """
    Validator untuk perubahan lokasi
    - Memastikan perpindahan lokasi masuk akal
    - Mencegah lompatan logika
    - Validasi aktivitas berdasarkan lokasi
    """
    
    def __init__(self):
        # Transisi yang masuk akal antar lokasi
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
        
        # Aturan khusus untuk aktivitas tertentu
        self.activity_location_rules = {
            'masak': {
                'allowed_locations': ['dapur'],
                'message': 'Harus di dapur untuk masak',
                'auto_transition': True
            },
            'makan': {
                'allowed_locations': ['dapur', 'ruang tamu', 'kafe', 'restoran'],
                'message': 'Mending di dapur atau ruang makan',
                'auto_transition': False
            },
            'tidur': {
                'allowed_locations': ['kamar'],
                'message': 'Enaknya tidur di kamar',
                'auto_transition': True
            },
            'mandi': {
                'allowed_locations': ['kamar mandi'],
                'message': 'Harus di kamar mandi untuk mandi',
                'auto_transition': True
            },
            'sikat gigi': {
                'allowed_locations': ['kamar mandi'],
                'message': 'Sikat gigi di kamar mandi dong',
                'auto_transition': True
            },
            'cuci muka': {
                'allowed_locations': ['kamar mandi'],
                'message': 'Cuci muka di kamar mandi',
                'auto_transition': True
            },
            'kerja': {
                'allowed_locations': ['kantor', 'ruang tamu', 'kamar'],
                'message': 'Bisa kerja di kantor atau di rumah',
                'auto_transition': False
            },
            'nonton tv': {
                'allowed_locations': ['ruang tamu', 'kamar'],
                'message': 'Nonton TV di ruang tamu atau kamar',
                'auto_transition': False
            },
            'baca buku': {
                'allowed_locations': ['ruang tamu', 'kamar', 'teras', 'taman'],
                'message': 'Bisa baca di tempat yang tenang',
                'auto_transition': False
            },
        }
        
        # Jarak antar lokasi (untuk validasi waktu)
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
        
        # Minimal waktu antar pindah berdasarkan jarak (detik)
        self.base_time_between = 30  # 30 detik dasar
        self.distance_multiplier = 15  # 15 detik per unit jarak
        
        logger.info("✅ LocationValidator initialized with enhanced rules")
    
    # =========================================================================
    # VALIDASI PERPINDAHAN LOKASI
    # =========================================================================
    
    def validate_location_change(self, from_loc: str, to_loc: str, is_intimate: bool = False) -> Tuple[bool, str]:
        """
        Validasi apakah perubahan lokasi diperbolehkan
        
        Args:
            from_loc: Lokasi asal
            to_loc: Lokasi tujuan
            is_intimate: Apakah sedang dalam sesi intim
            
        Returns:
            (allowed, reason)
        """
        if not from_loc or not to_loc:
            return True, "OK"
        
        from_lower = from_loc.lower()
        to_lower = to_loc.lower()
        
        # ===== 1. CEK JIKA SEDANG INTIM =====
        if is_intimate:
            return False, "Lagi intim, jangan pindah dulu... selesaikan dulu ya 😊"
        
        # ===== 2. CEK APAKAH LOKASI SAMA =====
        if from_lower == to_lower:
            return False, f"Kamu sudah di {from_loc}"
        
        # ===== 3. VALIDASI TRANSISI =====
        transition_allowed = self._check_transition(from_lower, to_lower)
        
        if not transition_allowed:
            # Coba cari rute alternatif
            alternative = self._find_alternative_route(from_lower, to_lower)
            if alternative:
                return False, f"Gak bisa langsung dari {from_loc} ke {to_loc}. Coba lewat {alternative} dulu."
            else:
                return False, f"Gak bisa pindah dari {from_loc} ke {to_loc}. Kayaknya jauh banget."
        
        # ===== 4. CEK WAKTU MINIMAL =====
        # Ini akan diimplementasikan di state tracker
        # Di sini hanya validasi logika
        
        return True, "OK"
    
    def _check_transition(self, from_loc: str, to_loc: str) -> bool:
        """Cek apakah transisi langsung diperbolehkan"""
        
        # Cari di dictionary transisi
        for key, values in self.valid_transitions.items():
            if key in from_loc:
                # Cek apakah tujuan ada dalam daftar yang diizinkan
                for val in values:
                    if val in to_loc:
                        return True
                break
        
        # Coba reverse lookup
        for key, values in self.valid_transitions.items():
            if key in to_loc:
                if any(v in from_loc for v in values):
                    return True
        
        # Kasus khusus: pindah ke lokasi yang berdekatan secara umum
        common_transitions = [
            ('kamar', 'ruang tamu'),
            ('kamar mandi', 'kamar'),
            ('dapur', 'ruang tamu'),
            ('teras', 'ruang tamu'),
        ]
        
        for a, b in common_transitions:
            if (a in from_loc and b in to_loc) or (b in from_loc and a in to_loc):
                return True
        
        return False
    
    def _find_alternative_route(self, from_loc: str, to_loc: str) -> Optional[str]:
        """Cari rute alternatif jika tidak bisa langsung"""
        
        # Cek apakah ada lokasi perantara yang umum
        common_hubs = ['ruang tamu', 'kamar']
        
        for hub in common_hubs:
            if self._check_transition(from_loc, hub) and self._check_transition(hub, to_loc):
                return hub
        
        return None
    
    # =========================================================================
    # VALIDASI AKTIVITAS BERDASARKAN LOKASI
    # =========================================================================
    
    def validate_activity_location(self, activity: str, current_loc: str) -> Tuple[bool, str, Optional[str]]:
        """
        Validasi apakah aktivitas sesuai dengan lokasi saat ini
        
        Args:
            activity: Nama aktivitas (masak, tidur, dll)
            current_loc: Lokasi saat ini
            
        Returns:
            (allowed, message, suggested_location)
        """
        if not activity or not current_loc:
            return True, "OK", None
        
        activity_lower = activity.lower()
        current_lower = current_loc.lower()
        
        # Cari aturan untuk aktivitas ini
        for act, rules in self.activity_location_rules.items():
            if act in activity_lower:
                allowed_locations = rules['allowed_locations']
                
                # Cek apakah lokasi saat ini diizinkan
                for allowed in allowed_locations:
                    if allowed in current_lower:
                        return True, "OK", None
                
                # Lokasi tidak sesuai, cari saran
                suggestion = allowed_locations[0] if allowed_locations else None
                return False, rules['message'], suggestion
        
        # Aktivitas tidak memiliki aturan khusus
        return True, "OK", None
    
    # =========================================================================
    # VALIDASI WAKTU PERPINDAHAN
    # =========================================================================
    
    def get_min_time_between(self, from_loc: str, to_loc: str) -> int:
        """
        Dapatkan minimal waktu yang dibutuhkan untuk pindah (dalam detik)
        """
        if not from_loc or not to_loc:
            return 0
        
        from_lower = from_loc.lower()
        to_lower = to_loc.lower()
        
        # Cari jarak di dictionary
        for (a, b), distance in self.location_distance.items():
            if (a in from_lower and b in to_lower) or (b in from_lower and a in to_lower):
                return self.base_time_between + (distance * self.distance_multiplier)
        
        # Default jarak sedang
        return self.base_time_between + (2 * self.distance_multiplier)
    
    # =========================================================================
    # DETEKSI LOKASI DARI AKTIVITAS
    # =========================================================================
    
    def get_suggested_location(self, activity: str) -> Optional[str]:
        """
        Dapatkan lokasi yang disarankan untuk suatu aktivitas
        
        Args:
            activity: Nama aktivitas
            
        Returns:
            Nama lokasi atau None
        """
        activity_lower = activity.lower()
        
        for act, rules in self.activity_location_rules.items():
            if act in activity_lower:
                return rules['allowed_locations'][0] if rules['allowed_locations'] else None
        
        return None
    
    def should_auto_transition(self, activity: str) -> bool:
        """
        Cek apakah aktivitas ini harus otomatis memindahkan bot
        
        Args:
            activity: Nama aktivitas
            
        Returns:
            True jika bot harus otomatis pindah
        """
        activity_lower = activity.lower()
        
        for act, rules in self.activity_location_rules.items():
            if act in activity_lower:
                return rules.get('auto_transition', False)
        
        return False
    
    # =========================================================================
    # INFORMASI LOKASI
    # =========================================================================
    
    def get_location_category(self, location: str) -> str:
        """
        Dapatkan kategori lokasi
        
        Returns:
            'indoor', 'outdoor', 'public', 'intimate'
        """
        loc_lower = location.lower()
        
        intimate_places = ['kamar', 'kamar mandi', 'toilet', 'balkon']
        public_places = ['mall', 'pantai', 'kantor', 'kafe', 'restoran', 'jalan']
        outdoor_places = ['taman', 'pantai', 'teras', 'jalan']
        
        if any(p in loc_lower for p in intimate_places):
            return 'intimate'
        elif any(p in loc_lower for p in public_places):
            return 'public'
        elif any(p in loc_lower for p in outdoor_places):
            return 'outdoor'
        else:
            return 'indoor'
    
    def get_distance_description(self, from_loc: str, to_loc: str) -> str:
        """
        Dapatkan deskripsi jarak antara dua lokasi
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
    # UTILITY
    # =========================================================================
    
    def get_allowed_locations(self, current_loc: str) -> List[str]:
        """
        Dapatkan daftar lokasi yang bisa dituju dari lokasi saat ini
        """
        current_lower = current_loc.lower()
        allowed = []
        
        for key, values in self.valid_transitions.items():
            if key in current_lower:
                allowed.extend(values)
                break
        
        # Tambahkan lokasi umum
        common_locations = ['ruang tamu', 'kamar', 'dapur', 'kamar mandi', 'teras']
        allowed.extend([loc for loc in common_locations if loc not in allowed])
        
        return list(set(allowed))  # Unique
    
    def format_location_info(self, location: str) -> str:
        """
        Format informasi lokasi untuk ditampilkan
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
