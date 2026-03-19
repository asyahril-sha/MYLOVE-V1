#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - UNIQUE ID GENERATOR V2
=============================================================================
Berdasarkan V1 dengan penambahan:
- Format dengan NAMA BOT: MYLOVE-NAMA-ROLE-USERID-DATE-SEQ
- ID khusus untuk PDKT: PDKT-NAMA-USERID-TIMESTAMP-RANDOM
- ID untuk Mantan, FWB, HTS
- Tetap kompatibel dengan format V1
=============================================================================
"""

import time
import random
import string
from datetime import datetime
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class UniqueIDGeneratorV2:
    """
    Generate unique ID untuk session V2
    Format V1: MYLOVE-ROLE-USERID-DATE-SEQ
    Format V2: MYLOVE-NAMA-ROLE-USERID-DATE-SEQ
    """
    
    def __init__(self):
        self.prefix = "MYLOVE"
        self.counter = {}  # Untuk tracking sequence per hari
        
        logger.info("✅ UniqueIDGeneratorV2 initialized")
    
    # =========================================================================
    # GENERATE ID (V1 + V2)
    # =========================================================================
    
    def generate_v1(self, role: str, user_id: int) -> str:
        """
        Generate ID dengan format V1 (tanpa nama bot)
        Untuk kompatibilitas dengan sistem lama
        
        Args:
            role: Nama role (ipar, janda, dll)
            user_id: ID Telegram user
            
        Returns:
            String: MYLOVE-IPAR-12345678-20240315-001
        """
        role_upper = role.upper()
        user_str = str(user_id)
        date_str = datetime.now().strftime("%Y%m%d")
        seq = self._get_next_sequence(role_upper, user_str, date_str)
        seq_str = f"{seq:03d}"
        
        return f"{self.prefix}-{role_upper}-{user_str}-{date_str}-{seq_str}"
    
    def generate_v2(self, bot_name: str, role: str, user_id: int) -> str:
        """
        Generate ID dengan format V2 (dengan nama bot)
        
        Args:
            bot_name: Nama bot (Sari, Dewi, dll)
            role: Nama role
            user_id: ID Telegram user
            
        Returns:
            String: MYLOVE-SARI-IPAR-12345678-20240315-001
        """
        # Format nama bot (uppercase, spasi jadi underscore)
        bot_upper = bot_name.upper().replace(' ', '_')
        role_upper = role.upper()
        user_str = str(user_id)
        date_str = datetime.now().strftime("%Y%m%d")
        
        # Sequence per (bot+role+user+date)
        seq_key = f"{bot_upper}_{role_upper}_{user_str}_{date_str}"
        seq = self._get_next_sequence_key(seq_key)
        seq_str = f"{seq:03d}"
        
        return f"{self.prefix}-{bot_upper}-{role_upper}-{user_str}-{date_str}-{seq_str}"
    
    def generate_pdkt_id(self, bot_name: str, role: str, user_id: int) -> str:
        """
        Generate ID khusus untuk PDKT
        Format: PDKT-NAMA-ROLE-USERID-TIMESTAMP-RANDOM
        
        Args:
            bot_name: Nama bot
            role: Nama role
            user_id: ID user
            
        Returns:
            String: PDKT-SARI-IPAR-12345678-1647358291-ABC1
        """
        bot_upper = bot_name.upper().replace(' ', '_')
        role_upper = role.upper()
        timestamp = int(time.time())
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        return f"PDKT-{bot_upper}-{role_upper}-{user_id}-{timestamp}-{random_str}"
    
    def generate_mantan_id(self, bot_name: str, role: str, user_id: int) -> str:
        """
        Generate ID untuk mantan
        Format: MANTAN-NAMA-ROLE-USERID-TIMESTAMP-RANDOM
        """
        bot_upper = bot_name.upper().replace(' ', '_')
        role_upper = role.upper()
        timestamp = int(time.time())
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        return f"MANTAN-{bot_upper}-{role_upper}-{user_id}-{timestamp}-{random_str}"
    
    def generate_fwb_id(self, bot_name: str, role: str, user_id: int) -> str:
        """
        Generate ID untuk FWB
        Format: FWB-NAMA-ROLE-USERID-TIMESTAMP-RANDOM
        """
        bot_upper = bot_name.upper().replace(' ', '_')
        role_upper = role.upper()
        timestamp = int(time.time())
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        return f"FWB-{bot_upper}-{role_upper}-{user_id}-{timestamp}-{random_str}"
    
    def generate_hts_id(self, bot_name: str, role: str, user_id: int) -> str:
        """
        Generate ID untuk HTS
        Format: HTS-NAMA-ROLE-USERID-TIMESTAMP-RANDOM
        """
        bot_upper = bot_name.upper().replace(' ', '_')
        role_upper = role.upper()
        timestamp = int(time.time())
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        return f"HTS-{bot_upper}-{role_upper}-{user_id}-{timestamp}-{random_str}"
    
    def generate_temp_id(self, prefix: str = "TEMP") -> str:
        """
        Generate temporary ID
        Format: TEMP-TIMESTAMP-RANDOM
        """
        timestamp = int(time.time())
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        return f"{prefix}-{timestamp}-{random_str}"
    
    def _get_next_sequence(self, role: str, user_id: str, date: str) -> int:
        """Dapatkan sequence number (format V1)"""
        key = f"{role}_{user_id}_{date}"
        return self._get_next_sequence_key(key)
    
    def _get_next_sequence_key(self, key: str) -> int:
        """Dapatkan sequence number berdasarkan key"""
        if key not in self.counter:
            self.counter[key] = 1
        else:
            self.counter[key] += 1
        
        return self.counter[key]
    
    # =========================================================================
    # PARSE ID
    # =========================================================================
    
    def parse(self, unique_id: str) -> Optional[Dict]:
        """
        Parse unique ID menjadi komponennya
        Support V1 dan V2 format
        
        Args:
            unique_id: String ID
            
        Returns:
            Dict dengan komponen atau None jika invalid
        """
        try:
            parts = unique_id.split('-')
            
            # Cek berdasarkan prefix
            if parts[0] == "MYLOVE":
                return self._parse_mylove_id(parts)
            elif parts[0] == "PDKT":
                return self._parse_pdkt_id(parts)
            elif parts[0] == "MANTAN":
                return self._parse_mantan_id(parts)
            elif parts[0] == "FWB":
                return self._parse_fwb_id(parts)
            elif parts[0] == "HTS":
                return self._parse_hts_id(parts)
            elif parts[0] == "TEMP":
                return self._parse_temp_id(parts)
            else:
                logger.warning(f"Unknown ID format: {unique_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error parsing ID {unique_id}: {e}")
            return None
    
    def _parse_mylove_id(self, parts: List[str]) -> Optional[Dict]:
        """Parse MYLOVE ID (V1 atau V2)"""
        if len(parts) == 5:
            # Format V1: MYLOVE-ROLE-USERID-DATE-SEQ
            return {
                "type": "session_v1",
                "prefix": parts[0],
                "role": parts[1].lower(),
                "user_id": int(parts[2]),
                "date": parts[3],
                "sequence": int(parts[4]),
                "full_id": "-".join(parts)
            }
        elif len(parts) == 6:
            # Format V2: MYLOVE-NAMA-ROLE-USERID-DATE-SEQ
            return {
                "type": "session_v2",
                "prefix": parts[0],
                "bot_name": parts[1].title().replace('_', ' '),
                "role": parts[2].lower(),
                "user_id": int(parts[3]),
                "date": parts[4],
                "sequence": int(parts[5]),
                "full_id": "-".join(parts)
            }
        else:
            return None
    
    def _parse_pdkt_id(self, parts: List[str]) -> Optional[Dict]:
        """Parse PDKT ID"""
        if len(parts) == 6:
            # PDKT-NAMA-ROLE-USERID-TIMESTAMP-RANDOM
            return {
                "type": "pdkt",
                "prefix": parts[0],
                "bot_name": parts[1].title().replace('_', ' '),
                "role": parts[2].lower(),
                "user_id": int(parts[3]),
                "timestamp": int(parts[4]),
                "random": parts[5],
                "full_id": "-".join(parts)
            }
        return None
    
    def _parse_mantan_id(self, parts: List[str]) -> Optional[Dict]:
        """Parse MANTAN ID"""
        if len(parts) == 6:
            return {
                "type": "mantan",
                "prefix": parts[0],
                "bot_name": parts[1].title().replace('_', ' '),
                "role": parts[2].lower(),
                "user_id": int(parts[3]),
                "timestamp": int(parts[4]),
                "random": parts[5],
                "full_id": "-".join(parts)
            }
        return None
    
    def _parse_fwb_id(self, parts: List[str]) -> Optional[Dict]:
        """Parse FWB ID"""
        if len(parts) == 6:
            return {
                "type": "fwb",
                "prefix": parts[0],
                "bot_name": parts[1].title().replace('_', ' '),
                "role": parts[2].lower(),
                "user_id": int(parts[3]),
                "timestamp": int(parts[4]),
                "random": parts[5],
                "full_id": "-".join(parts)
            }
        return None
    
    def _parse_hts_id(self, parts: List[str]) -> Optional[Dict]:
        """Parse HTS ID"""
        if len(parts) == 6:
            return {
                "type": "hts",
                "prefix": parts[0],
                "bot_name": parts[1].title().replace('_', ' '),
                "role": parts[2].lower(),
                "user_id": int(parts[3]),
                "timestamp": int(parts[4]),
                "random": parts[5],
                "full_id": "-".join(parts)
            }
        return None
    
    def _parse_temp_id(self, parts: List[str]) -> Optional[Dict]:
        """Parse TEMP ID"""
        if len(parts) == 3:
            return {
                "type": "temp",
                "prefix": parts[0],
                "timestamp": int(parts[1]),
                "random": parts[2],
                "full_id": "-".join(parts)
            }
        return None
    
    # =========================================================================
    # UTILITY METHODS (DARI V1)
    # =========================================================================
    
    def is_valid_format(self, unique_id: str) -> bool:
        """Cek apakah format ID valid"""
        return self.parse(unique_id) is not None
    
    def get_date_from_id(self, unique_id: str) -> Optional[str]:
        """Ekstrak tanggal dari ID (untuk MYLOVE format)"""
        parsed = self.parse(unique_id)
        if parsed and parsed.get('type') in ['session_v1', 'session_v2']:
            return parsed.get('date')
        return None
    
    def get_role_from_id(self, unique_id: str) -> Optional[str]:
        """Ekstrak role dari ID"""
        parsed = self.parse(unique_id)
        return parsed.get('role') if parsed else None
    
    def get_user_from_id(self, unique_id: str) -> Optional[int]:
        """Ekstrak user ID dari ID"""
        parsed = self.parse(unique_id)
        return parsed.get('user_id') if parsed else None
    
    def get_bot_name_from_id(self, unique_id: str) -> Optional[str]:
        """Ekstrak nama bot dari ID (untuk V2 format)"""
        parsed = self.parse(unique_id)
        return parsed.get('bot_name') if parsed else None
    
    def format_for_display(self, unique_id: str) -> str:
        """
        Format ID untuk ditampilkan ke user
        
        Contoh:
        - MYLOVE-SARI-IPAR-123-20240315-001 -> Sari (Ipar) 15 Mar 2024 #001
        - PDKT-SARI-IPAR-123-1647358291-ABC1 -> PDKT Sari (Ipar)
        """
        parsed = self.parse(unique_id)
        if not parsed:
            return unique_id
        
        if parsed['type'] == 'session_v2':
            # Format V2 dengan nama
            date_obj = datetime.strptime(parsed['date'], "%Y%m%d")
            date_formatted = date_obj.strftime("%d %b %Y")
            return f"{parsed['bot_name']} ({parsed['role'].title()}) {date_formatted} #{parsed['sequence']:03d}"
        
        elif parsed['type'] == 'session_v1':
            # Format V1 tanpa nama
            date_obj = datetime.strptime(parsed['date'], "%Y%m%d")
            date_formatted = date_obj.strftime("%d %b %Y")
            return f"{parsed['role'].upper()} {date_formatted} #{parsed['sequence']:03d}"
        
        elif parsed['type'] == 'pdkt':
            return f"PDKT {parsed['bot_name']} ({parsed['role'].title()})"
        
        elif parsed['type'] == 'mantan':
            return f"💔 {parsed['bot_name']} ({parsed['role'].title()})"
        
        elif parsed['type'] == 'fwb':
            return f"💕 {parsed['bot_name']} ({parsed['role'].title()})"
        
        elif parsed['type'] == 'hts':
            return f"🔹 {parsed['bot_name']} ({parsed['role'].title()})"
        
        return unique_id
    
    def get_session_age_days(self, unique_id: str) -> Optional[int]:
        """Hitung umur session dalam hari (untuk MYLOVE format)"""
        parsed = self.parse(unique_id)
        if not parsed or parsed['type'] not in ['session_v1', 'session_v2']:
            return None
        
        try:
            session_date = datetime.strptime(parsed['date'], "%Y%m%d")
            today = datetime.now()
            delta = today - session_date
            return delta.days
        except:
            return None


# Singleton instance
id_generator_v2 = UniqueIDGeneratorV2()


__all__ = ['UniqueIDGeneratorV2', 'id_generator_v2']
