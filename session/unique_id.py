#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - UNIQUE ID GENERATOR
=============================================================================
Format: MYLOVE-{NAMA_BOT}-{ROLE}-{USERID}-{YYYYMMDD}-{SEQ}
Contoh: MYLOVE-SARI-IPAR-12345678-20240319-001

- Menambahkan NAMA_BOT ke dalam format ID
- Nama bot dipilih random saat role selection dan menjadi identitas permanen
=============================================================================
"""

import time
import random
import string
from datetime import datetime
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class UniqueIDGenerator:
    """
    Generate unique ID untuk session
    Format: MYLOVE-{NAMA_BOT}-{ROLE}-{USERID}-{YYYYMMDD}-{SEQ}
    """
    
    def __init__(self):
        self.prefix = "MYLOVE"
        self.counter = {}  # Untuk tracking sequence per hari
        
    # ===== TAMBAHAN MYLOVE V2 =====
    def generate(self, nama_bot: str, role: str, user_id: int) -> str:
        """
        Generate unique ID dengan format baru:
        MYLOVE-{NAMA_BOT}-{ROLE}-{USERID}-{YYYYMMDD}-{SEQ}
        
        Args:
            nama_bot: Nama bot yang dipilih (contoh: "Sari", "Dewi")
            role: Nama role (ipar, janda, dll)
            user_id: ID Telegram user
            
        Returns:
            String: MYLOVE-SARI-IPAR-12345678-20240319-001
        """
        # Format nama bot (uppercase, remove spaces, replace special chars)
        nama_upper = nama_bot.upper().replace(' ', '_').replace('-', '_')
        
        # Format role (uppercase)
        role_upper = role.upper()
        
        # User ID
        user_str = str(user_id)
        
        # Date
        date_str = datetime.now().strftime("%Y%m%d")
        
        # Sequence number
        seq = self._get_next_sequence(nama_upper, role_upper, user_str, date_str)
        
        # Format with leading zeros
        seq_str = f"{seq:03d}"
        
        # Combine
        unique_id = f"{self.prefix}-{nama_upper}-{role_upper}-{user_str}-{date_str}-{seq_str}"
        
        logger.debug(f"Generated unique ID V2: {unique_id}")
        
        return unique_id
    
    def _get_next_sequence(self, nama_bot: str, role: str, user_id: str, date: str) -> int:
        """Dapatkan sequence number berikutnya untuk kombinasi nama+role+user+date"""
        key = f"{nama_bot}_{role}_{user_id}_{date}"
        
        if key not in self.counter:
            self.counter[key] = 1
        else:
            self.counter[key] += 1
            
        return self.counter[key]
    # ===== END TAMBAHAN =====
    
    # ===== BACKWARD COMPATIBILITY =====
    def generate_old(self, role: str, user_id: int) -> str:
        """
        Versi lama untuk backward compatibility
        Format: MYLOVE-ROLE-USERID-DATE-SEQ
        """
        role_upper = role.upper()
        user_str = str(user_id)
        date_str = datetime.now().strftime("%Y%m%d")
        seq = self._get_next_sequence_old(role_upper, user_str, date_str)
        seq_str = f"{seq:03d}"
        
        unique_id = f"{self.prefix}-{role_upper}-{user_str}-{date_str}-{seq_str}"
        return unique_id
    
    def _get_next_sequence_old(self, role: str, user_id: str, date: str) -> int:
        """Versi lama untuk sequence"""
        key = f"{role}_{user_id}_{date}"
        if key not in self.counter:
            self.counter[key] = 1
        else:
            self.counter[key] += 1
        return self.counter[key]
    
    def parse(self, unique_id: str) -> Optional[Dict]:
        """
        Parse unique ID menjadi komponennya
        Support format lama dan baru
        
        Args:
            unique_id: String ID 
                       Format lama: MYLOVE-IPAR-12345678-20240315-001
                       Format baru: MYLOVE-SARI-IPAR-12345678-20240319-001
            
        Returns:
            Dict dengan komponen atau None jika invalid
        """
        try:
            parts = unique_id.split('-')
            
            if len(parts) < 5 or parts[0] != self.prefix:
                logger.warning(f"Invalid unique ID format: {unique_id}")
                return None
            
            # ===== TAMBAHAN MYLOVE V2 =====
            # Cek apakah format baru (ada nama bot)
            if len(parts) == 6:
                # Format baru: MYLOVE-NAMA-ROLE-USER-DATE-SEQ
                return {
                    "prefix": parts[0],
                    "nama_bot": parts[1].lower(),  # Nama bot
                    "role": parts[2].lower(),
                    "user_id": int(parts[3]),
                    "date": parts[4],
                    "sequence": int(parts[5]),
                    "full_id": unique_id,
                    "format": "v2"
                }
            else:
                # Format lama: MYLOVE-ROLE-USER-DATE-SEQ
                return {
                    "prefix": parts[0],
                    "nama_bot": None,  # Tidak ada nama bot
                    "role": parts[1].lower(),
                    "user_id": int(parts[2]),
                    "date": parts[3],
                    "sequence": int(parts[4]),
                    "full_id": unique_id,
                    "format": "v1"
                }
            # ===== END TAMBAHAN =====
            
        except Exception as e:
            logger.error(f"Error parsing unique ID {unique_id}: {e}")
            return None
    
    # ===== TAMBAHAN MYLOVE V2 =====
    def generate_temp_id(self, nama_bot: str, role: str, user_id: int) -> str:
        """
        Generate temporary ID untuk session yang belum disimpan
        Format: TEMP-{NAMA_BOT}-{ROLE}-{USERID}-{TIMESTAMP}-{RANDOM}
        """
        timestamp = int(time.time())
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        nama_upper = nama_bot.upper().replace(' ', '_')
        role_upper = role.upper()
        
        return f"TEMP-{nama_upper}-{role_upper}-{user_id}-{timestamp}-{random_str}"
    # ===== END TAMBAHAN =====
    
    def is_valid_format(self, unique_id: str) -> bool:
        """Cek apakah format ID valid"""
        return self.parse(unique_id) is not None
    
    def get_date_from_id(self, unique_id: str) -> Optional[str]:
        """Ekstrak tanggal dari ID"""
        parsed = self.parse(unique_id)
        return parsed.get('date') if parsed else None
    
    def get_role_from_id(self, unique_id: str) -> Optional[str]:
        """Ekstrak role dari ID"""
        parsed = self.parse(unique_id)
        return parsed.get('role') if parsed else None
    
    # ===== TAMBAHAN MYLOVE V2 =====
    def get_nama_from_id(self, unique_id: str) -> Optional[str]:
        """Ekstrak nama bot dari ID"""
        parsed = self.parse(unique_id)
        return parsed.get('nama_bot') if parsed else None
    # ===== END TAMBAHAN =====
    
    def get_user_from_id(self, unique_id: str) -> Optional[int]:
        """Ekstrak user ID dari ID"""
        parsed = self.parse(unique_id)
        return parsed.get('user_id') if parsed else None
    
    def format_for_display(self, unique_id: str) -> str:
        """
        Format ID untuk ditampilkan ke user
        Contoh baru: MYLOVE-SARI-IPAR-12345678-20240319-001 -> SARI (Ipar, 19 Mar 2024) #001
        """
        parsed = self.parse(unique_id)
        if not parsed:
            return unique_id
        
        # ===== TAMBAHAN MYLOVE V2 =====
        if parsed.get('format') == 'v2' and parsed.get('nama_bot'):
            # Format baru dengan nama bot
            date_obj = datetime.strptime(parsed['date'], "%Y%m%d")
            date_formatted = date_obj.strftime("%d %b %Y")
            
            nama_display = parsed['nama_bot'].upper()
            role_display = parsed['role'].title()
            
            return f"{nama_display} ({role_display}, {date_formatted}) #{parsed['sequence']:03d}"
        else:
            # Format lama
            date_obj = datetime.strptime(parsed['date'], "%Y%m%d")
            date_formatted = date_obj.strftime("%d %b %Y")
            
            return f"{parsed['role'].upper()} ({date_formatted}) #{parsed['sequence']:03d}"
        # ===== END TAMBAHAN =====
    
    def get_session_age_days(self, unique_id: str) -> Optional[int]:
        """Hitung umur session dalam hari"""
        parsed = self.parse(unique_id)
        if not parsed:
            return None
            
        try:
            session_date = datetime.strptime(parsed['date'], "%Y%m%d")
            today = datetime.now()
            delta = today - session_date
            return delta.days
        except:
            return None
    
    # ===== TAMBAHAN MYLOVE V2 =====
    def get_session_summary(self, unique_id: str) -> str:
        """
        Dapatkan ringkasan session dari ID
        """
        parsed = self.parse(unique_id)
        if not parsed:
            return "Invalid ID"
        
        if parsed.get('format') == 'v2' and parsed.get('nama_bot'):
            return f"Session dengan {parsed['nama_bot'].title()} ({parsed['role'].title()}) - {parsed['date']}"
        else:
            return f"Session dengan role {parsed['role'].title()} - {parsed['date']}"
    # ===== END TAMBAHAN =====


# Singleton instance
id_generator = UniqueIDGenerator()


__all__ = ['UniqueIDGenerator', 'id_generator']
