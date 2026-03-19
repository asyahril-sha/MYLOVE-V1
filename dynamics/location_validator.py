#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - LOCATION VALIDATOR
=============================================================================
Memvalidasi perubahan lokasi agar masuk akal
- Tidak bisa pindah dari kamar mandi langsung ke pantai
- Minimal waktu antar pindah
=============================================================================
"""

class LocationValidator:
    """
    Validator untuk perubahan lokasi
    """
    
    def __init__(self):
        # Transisi yang masuk akal
        self.valid_transitions = {
            'ruang tamu': ['kamar', 'dapur', 'teras', 'kamar mandi', 'taman'],
            'kamar': ['kamar mandi', 'ruang tamu', 'balkon'],
            'kamar mandi': ['kamar', 'ruang tamu'],
            'dapur': ['ruang tamu', 'teras'],
            'teras': ['ruang tamu', 'taman'],
            'taman': ['teras', 'ruang tamu'],
            'pantai': ['mobil', 'kafe', 'rumah'],
            'mall': ['parkiran', 'mobil', 'kafe'],
            'mobil': ['pantai', 'mall', 'rumah', 'parkiran'],
            'kafe': ['mall', 'pantai', 'jalan'],
            'kantor': ['ruang tamu', 'mobil'],
        }
        
        # Minimal waktu antar pindah (detik)
        self.min_time_between = 60  # 1 menit
        
    def validate_location_change(self, from_loc: str, to_loc: str, is_intimate: bool = False) -> tuple:
        """
        Validasi apakah perubahan lokasi diperbolehkan
        
        Returns:
            (allowed, reason)
        """
        from_lower = from_loc.lower() if from_loc else ""
        to_lower = to_loc.lower() if to_loc else ""
        
        # Jika dari None (awal session) - boleh
        if not from_loc:
            return True, "OK"
            
        # Jika sedang intim - tidak boleh pindah
        if is_intimate:
            return False, "Lagi intim, jangan pindah dulu..."
            
        # Cek di dictionary transisi
        for key, values in self.valid_transitions.items():
            if key in from_lower:
                if any(v in to_lower for v in values):
                    return True, "OK"
                break
                
        # Default: tidak boleh pindah terlalu jauh
        return False, f"Gak bisa langsung dari {from_loc} ke {to_loc}. Cari tempat yang lebih dekat."
