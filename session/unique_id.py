#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - UNIQUE ID GENERATOR
=============================================================================
Format: MYLOVE-{ROLE}-{USERID}-{YYYYMMDD}-{SEQ}
Contoh: MYLOVE-IPAR-12345678-20240315-001

Setiap interaksi memiliki unique ID untuk melanjutkan session
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
    Format: MYLOVE-ROLE-USERID-DATE-SEQ
    """
    
    def __init__(self):
        self.prefix = "MYLOVE"
        self.counter = {}  # Untuk tracking sequence per hari
        
    def generate(self, role: str, user_id: int) -> str:
        """
        Generate unique ID
        
        Args:
            role: Nama role (ipar, janda, dll)
            user_id: ID Telegram user
            
        Returns:
            String: MYLOVE-IPAR-12345678-20240315-001
        """
        # Format role (uppercase)
        role_upper = role.upper()
        
        # User ID
        user_str = str(user_id)
        
        # Date
        date_str = datetime.now().strftime("%Y%m%d")
        
        # Sequence number
        seq = self._get_next_sequence(role_upper, user_str, date_str)
        
        # Format with leading zeros
        seq_str = f"{seq:03d}"
        
        # Combine
        unique_id = f"{self.prefix}-{role_upper}-{user_str}-{date_str}-{seq_str}"
        
        logger.debug(f"Generated unique ID: {unique_id}")
        
        return unique_id
        
    def _get_next_sequence(self, role: str, user_id: str, date: str) -> int:
        """Dapatkan sequence number berikutnya untuk hari ini"""
        key = f"{role}_{user_id}_{date}"
        
        if key not in self.counter:
            self.counter[key] = 1
        else:
            self.counter[key] += 1
            
        return self.counter[key]
        
    def parse(self, unique_id: str) -> Optional[Dict]:
        """
        Parse unique ID menjadi komponennya
        
        Args:
            unique_id: String ID (MYLOVE-IPAR-12345678-20240315-001)
            
        Returns:
            Dict dengan komponen atau None jika invalid
        """
        try:
            parts = unique_id.split('-')
            
            if len(parts) != 5 or parts[0] != self.prefix:
                logger.warning(f"Invalid unique ID format: {unique_id}")
                return None
                
            return {
                "prefix": parts[0],
                "role": parts[1].lower(),
                "user_id": int(parts[2]),
                "date": parts[3],
                "sequence": int(parts[4]),
                "full_id": unique_id
            }
            
        except Exception as e:
            logger.error(f"Error parsing unique ID {unique_id}: {e}")
            return None
            
    def generate_temp_id(self, role: str, user_id: int) -> str:
        """
        Generate temporary ID untuk session yang belum disimpan
        Format: TEMP-{ROLE}-{USERID}-{TIMESTAMP}-{RANDOM}
        """
        timestamp = int(time.time())
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        return f"TEMP-{role.upper()}-{user_id}-{timestamp}-{random_str}"
        
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
        
    def get_user_from_id(self, unique_id: str) -> Optional[int]:
        """Ekstrak user ID dari ID"""
        parsed = self.parse(unique_id)
        return parsed.get('user_id') if parsed else None
        
    def format_for_display(self, unique_id: str) -> str:
        """
        Format ID untuk ditampilkan ke user
        Contoh: MYLOVE-IPAR-12345678-20240315-001 -> IPAR (15 Mar 2024) #001
        """
        parsed = self.parse(unique_id)
        if not parsed:
            return unique_id
            
        # Format date
        date_obj = datetime.strptime(parsed['date'], "%Y%m%d")
        date_formatted = date_obj.strftime("%d %b %Y")
        
        return f"{parsed['role'].upper()} ({date_formatted}) #{parsed['sequence']:03d}"
        
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


# Singleton instance
id_generator = UniqueIDGenerator()


__all__ = ['UniqueIDGenerator', 'id_generator']
