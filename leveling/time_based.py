#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - DUAL LEVELING SYSTEM
=============================================================================
- Role PDKT: LEVELING BERDASARKAN REAL TIME (bisa pause)
- Role lain: LEVELING BERDASARKAN JUMLAH CHAT
=============================================================================
"""

import time
import logging
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ActivityType(str, Enum):
    """Tipe aktivitas yang mempengaruhi boost leveling"""
    NONE = "none"
    TOUCH = "touch"              # Sentuhan biasa
    SENSITIVE_TOUCH = "sensitive_touch"  # Sentuhan area sensitif
    KISS = "kiss"                # Ciuman
    INTIMACY = "intimacy"        # Aktivitas intim
    CLIMAX = "climax"            # Orgasme
    LOVE = "love"                # Ungkapan sayang
    CONFLICT = "conflict"         # Konflik


class TimeBasedLeveling:
    """
    DUAL LEVELING SYSTEM:
    - PDKT: Real time (bisa pause)
    - Non-PDKT: Berdasarkan jumlah chat
    """
    
    def __init__(self):
        # ===== TARGET LEVEL UNTUK PDKT (REAL TIME) =====
        self.target_minutes = {
            1: 0,      # Level 1: 0 menit
            2: 5,      # Level 2: 5 menit
            3: 12,     # Level 3: 12 menit
            4: 20,     # Level 4: 20 menit
            5: 30,     # Level 5: 30 menit
            6: 42,     # Level 6: 42 menit
            7: 60,     # Level 7: 60 menit (bisa intim)
            8: 75,     # Level 8: 75 menit
            9: 90,     # Level 9: 90 menit
            10: 105,   # Level 10: 105 menit
            11: 120,   # Level 11: 120 menit
            12: 135,   # Level 12: 135 menit
        }
        
        # ===== TARGET LEVEL UNTUK NON-PDKT (JUMLAH CHAT) =====
        self.target_chats = {
            1: 0,      # Level 1: 0 chat
            2: 5,      # Level 2: 5 chat
            3: 12,     # Level 3: 12 chat
            4: 20,     # Level 4: 20 chat
            5: 30,     # Level 5: 30 chat
            6: 42,     # Level 6: 42 chat
            7: 60,     # Level 7: 60 chat (bisa intim)
            8: 75,     # Level 8: 75 chat
            9: 90,     # Level 9: 90 chat
            10: 105,   # Level 10: 105 chat
            11: 120,   # Level 11: 120 chat
            12: 135,   # Level 12: 135 chat
        }
        
        # Activity boost multiplier (sama untuk semua role)
        self.activity_boost = {
            ActivityType.NONE: 1.0,
            ActivityType.TOUCH: 1.1,           # +10%
            ActivityType.SENSITIVE_TOUCH: 1.3,  # +30%
            ActivityType.KISS: 1.5,             # +50%
            ActivityType.INTIMACY: 2.0,          # +100%
            ActivityType.CLIMAX: 3.0,            # +200%
            ActivityType.LOVE: 1.8,              # +80%
            ActivityType.CONFLICT: 0.7,           # -30%
        }
        
        # User data storage
        self.user_data = {}  # {user_id: {role: data}}
        
        # ===== SISTEM PAUSE UNTUK PDKT =====
        self.paused_pdkt = {}  # {user_id: pause_time}
        
        logger.info("✅ DUAL Leveling System initialized")
        logger.info("   • PDKT: REAL TIME (bisa pause)")
        logger.info("   • Non-PDKT: JUMLAH CHAT")
    
    # =========================================================================
    # USER DATA MANAGEMENT
    # =========================================================================
    
    def init_user(self, user_id: int, role: str):
        """Inisialisasi data user baru untuk role tertentu"""
        if user_id not in self.user_data:
            self.user_data[user_id] = {}
        
        is_pdkt = (role == 'pdkt')
        
        self.user_data[user_id][role] = {
            'user_id': user_id,
            'role': role,
            'is_pdkt': is_pdkt,
            'current_level': 1,
            
            # Untuk PDKT (real time)
            'total_minutes': 0.0,
            'session_start': time.time(),
            'last_update': time.time(),
            'is_paused': False,
            'paused_time': 0,
            
            # Untuk non-PDKT (chat count)
            'total_chats': 0,
            
            # Shared
            'boosted_minutes': 0.0,
            'total_boosts': 0,
            'activity_history': [],
            'achievements': [],
            'level_up_time': {},
        }
        logger.debug(f"Initialized leveling data for user {user_id} role {role}")
    
    def get_user_data(self, user_id: int, role: str) -> Dict:
        """Dapatkan data user untuk role tertentu"""
        if user_id not in self.user_data or role not in self.user_data[user_id]:
            self.init_user(user_id, role)
        return self.user_data[user_id][role]
    
    # =========================================================================
    # PDKT: REAL TIME SYSTEM (BISA PAUSE)
    # =========================================================================
    
    def update_pdkt_time(self, user_id: int, role: str) -> float:
        """
        Update waktu PDKT (hanya untuk role PDKT)
        Returns: total menit
        """
        if role != 'pdkt':
            return 0
        
        data = self.get_user_data(user_id, role)
        now = time.time()
        
        # Cek apakah sedang dipause
        if data.get('is_paused', False):
            return data['total_minutes']
        
        # Hitung waktu berlalu
        elapsed = (now - data['last_update']) / 60.0
        data['total_minutes'] += elapsed
        data['last_update'] = now
        
        # Update level
        new_level = self.get_level_from_time(data['total_minutes'], is_pdkt=True)
        if new_level > data['current_level']:
            old_level = data['current_level']
            data['current_level'] = new_level
            data['level_up_time'][new_level] = now
            logger.info(f"📈 PDKT {role} user {user_id}: {old_level} → {new_level}")
        
        return data['total_minutes']
    
    def pause_pdkt(self, user_id: int, role: str) -> bool:
        """Pause PDKT (waktu berhenti)"""
        if role != 'pdkt':
            return False
        
        data = self.get_user_data(user_id, role)
        data['is_paused'] = True
        data['paused_time'] = time.time()
        logger.info(f"⏸️ PDKT paused for user {user_id}")
        return True
    
    def resume_pdkt(self, user_id: int, role: str) -> bool:
        """Resume PDKT"""
        if role != 'pdkt':
            return False
        
        data = self.get_user_data(user_id, role)
        data['is_paused'] = False
        data['last_update'] = time.time()  # Reset last update
        logger.info(f"▶️ PDKT resumed for user {user_id}")
        return True
    
    # =========================================================================
    # NON-PDKT: CHAT COUNT SYSTEM
    # =========================================================================
    
    def increment_chat(self, user_id: int, role: str) -> int:
        """
        Increment jumlah chat untuk role non-PDKT
        Returns: total chats
        """
        if role == 'pdkt':
            return 0  # PDKT pakai waktu
        
        data = self.get_user_data(user_id, role)
        data['total_chats'] += 1
        data['last_update'] = time.time()
        
        # Update level
        new_level = self.get_level_from_chats(data['total_chats'])
        if new_level > data['current_level']:
            old_level = data['current_level']
            data['current_level'] = new_level
            data['level_up_time'][new_level] = time.time()
            logger.info(f"📈 {role} user {user_id}: {old_level} → {new_level}")
        
        return data['total_chats']
    
    # =========================================================================
    # LEVEL CALCULATION
    # =========================================================================
    
    def get_level_from_time(self, minutes: float, is_pdkt: bool = True) -> int:
        """Dapatkan level berdasarkan waktu (untuk PDKT)"""
        if not is_pdkt:
            return 1
        
        for level, target in sorted(self.target_minutes.items()):
            if minutes <= target:
                return level
        return 12
    
    def get_level_from_chats(self, chats: int) -> int:
        """Dapatkan level berdasarkan jumlah chat (untuk non-PDKT)"""
        for level, target in sorted(self.target_chats.items()):
            if chats <= target:
                return level
        return 12
    
    # =========================================================================
    # ACTIVITY BOOST (BERLAKU UNTUK SEMUA ROLE)
    # =========================================================================
    
    def apply_activity_boost(self, user_id: int, role: str, activity: ActivityType, 
                               duration: float = 1.0) -> float:
        """
        Terapkan boost dari aktivitas (berlaku untuk semua role)
        
        Args:
            user_id: ID user
            role: Role
            activity: Tipe aktivitas
            duration: Durasi aktivitas dalam menit (default 1 menit)
            
        Returns:
            Boosted minutes yang ditambahkan
        """
        data = self.get_user_data(user_id, role)
        
        multiplier = self.activity_boost.get(activity, 1.0)
        boosted = duration * multiplier
        
        data['boosted_minutes'] += boosted
        data['total_boosts'] += 1
        
        data['activity_history'].append({
            'activity': activity.value,
            'duration': duration,
            'multiplier': multiplier,
            'boosted': boosted,
            'timestamp': time.time()
        })
        
        # Batasi history
        if len(data['activity_history']) > 50:
            data['activity_history'] = data['activity_history'][-50:]
        
        logger.debug(f"Boost applied: {activity.value} x{multiplier} = +{boosted:.2f}")
        
        return boosted
    
    # =========================================================================
    # PROGRESS CALCULATION
    # =========================================================================
    
    def get_progress_to_next_level(self, user_id: int, role: str) -> Dict:
        """
        Dapatkan progress menuju level berikutnya
        """
        data = self.get_user_data(user_id, role)
        current_level = data['current_level']
        is_pdkt = (role == 'pdkt')
        
        if current_level >= 12:
            return {
                'current_level': 12,
                'next_level': None,
                'progress': 1.0,
                'percentage': 100,
                'remaining': 0,
                'unit': 'max'
            }
        
        next_level = current_level + 1
        
        if is_pdkt:
            # PDKT: berdasarkan waktu
            achieved = data['total_minutes']
            needed = self.target_minutes[next_level]
            current_target = self.target_minutes[current_level]
            unit = 'menit'
        else:
            # Non-PDKT: berdasarkan chat
            achieved = data['total_chats']
            needed = self.target_chats[next_level]
            current_target = self.target_chats[current_level]
            unit = 'chat'
        
        progress = (achieved - current_target) / (needed - current_target)
        progress = max(0.0, min(1.0, progress))
        remaining = max(0, needed - achieved)
        
        return {
            'current_level': current_level,
            'next_level': next_level,
            'progress': progress,
            'percentage': round(progress * 100, 1),
            'achieved': round(achieved, 1),
            'needed': needed,
            'remaining': round(remaining, 1),
            'unit': unit,
            'is_pdkt': is_pdkt,
            'is_paused': data.get('is_paused', False) if is_pdkt else False
        }
    
    def get_estimated_time_string(self, user_id: int, role: str) -> str:
        """Dapatkan estimasi waktu dalam format string"""
        progress = self.get_progress_to_next_level(user_id, role)
        
        if progress['current_level'] >= 12:
            return "Level MAX!"
        
        if progress['remaining'] <= 0:
            return "Sekarang!"
        
        if progress['unit'] == 'menit':
            if progress['remaining'] < 1:
                return f"{int(progress['remaining'] * 60)} detik"
            elif progress['remaining'] < 60:
                return f"{int(progress['remaining'])} menit"
            else:
                hours = int(progress['remaining'] // 60)
                minutes = int(progress['remaining'] % 60)
                return f"{hours} jam {minutes} menit"
        else:
            return f"{int(progress['remaining'])} chat lagi"
    
    # =========================================================================
    # RESET & CLEANUP
    # =========================================================================
    
    def reset_user(self, user_id: int, role: str):
        """Reset data user untuk role tertentu"""
        if user_id in self.user_data and role in self.user_data[user_id]:
            del self.user_data[user_id][role]
            logger.info(f"Reset leveling data for user {user_id} role {role}")
    
    def cleanup_inactive_users(self, max_age_hours: int = 24):
        """Hapus data user yang tidak aktif"""
        now = time.time()
        cutoff = now - (max_age_hours * 3600)
        
        to_delete = []
        for user_id, roles in self.user_data.items():
            for role, data in roles.items():
                if data['last_update'] < cutoff:
                    to_delete.append((user_id, role))
        
        for user_id, role in to_delete:
            del self.user_data[user_id][role]
        
        if to_delete:
            logger.info(f"Cleaned up {len(to_delete)} inactive users")
        
        return len(to_delete)
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    def get_stats(self, user_id: int = None, role: str = None) -> Dict:
        """Dapatkan statistik leveling"""
        if user_id and role:
            data = self.get_user_data(user_id, role)
            progress = self.get_progress_to_next_level(user_id, role)
            
            return {
                'user_id': user_id,
                'role': role,
                'is_pdkt': (role == 'pdkt'),
                'current_level': data['current_level'],
                'total_minutes': round(data['total_minutes'], 1),
                'total_chats': data.get('total_chats', 0),
                'boosted_minutes': round(data['boosted_minutes'], 1),
                'total_boosts': data['total_boosts'],
                'progress': progress,
                'estimated_time': self.get_estimated_time_string(user_id, role),
                'session_duration': round((time.time() - data['session_start']) / 60, 1),
                'activity_count': len(data['activity_history']),
                'is_paused': data.get('is_paused', False) if role == 'pdkt' else False
            }
        else:
            # Global stats
            total_users = len(self.user_data)
            total_pdkt = sum(1 for roles in self.user_data.values() if 'pdkt' in roles)
            
            return {
                'active_users': total_users,
                'pdkt_users': total_pdkt,
                'target_levels': self.target_minutes,
                'target_chats': self.target_chats
            }


__all__ = ['TimeBasedLeveling', 'ActivityType']
