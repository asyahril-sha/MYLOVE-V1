#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - TIME-BASED LEVELING SYSTEM (FIX LENGKAP)
=============================================================================
Leveling berdasarkan durasi percakapan (bukan jumlah pesan)

Target:
- Level 7 (bisa intim) dalam 60 menit
- Level 11 (deep connection) dalam 120 menit
- Level 12 (aftercare) dalam 135 menit

Activity Boost:
- Sentuhan biasa: 1.1x
- Sentuhan sensitif: 1.3x
- Kiss: 1.5x
- Intimacy: 2.0x
- Climax: 3.0x
"""

import time
import logging
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


class TimeBasedLeveling:
    """
    Sistem leveling berbasis durasi percakapan
    Level naik berdasarkan akumulasi waktu chat + activity boost
    """
    
    def __init__(self):
        # Target waktu per level (dalam menit)
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
            11: 120,   # Level 11: 120 menit (deep connection)
            12: 135,   # Level 12: 135 menit (aftercare)
        }
        
        # Activity boost multiplier
        self.activity_boost = {
            ActivityType.NONE: 1.0,
            ActivityType.TOUCH: 1.1,           # +10%
            ActivityType.SENSITIVE_TOUCH: 1.3,  # +30%
            ActivityType.KISS: 1.5,             # +50%
            ActivityType.INTIMACY: 2.0,          # +100%
            ActivityType.CLIMAX: 3.0,            # +200%
        }
        
        # User data storage
        self.user_data = {}  # {user_id: UserLevelData}
        
        logger.info("✅ TimeBasedLeveling initialized")
        logger.info(f"   Target: Level 7 in 60 menit, Level 11 in 120 menit")
    
    # =========================================================================
    # USER DATA MANAGEMENT
    # =========================================================================
    
    def init_user(self, user_id: int):
        """Inisialisasi data user baru"""
        self.user_data[user_id] = {
            'user_id': user_id,
            'current_level': 1,
            'total_minutes': 0.0,           # Total waktu chat (menit)
            'boosted_minutes': 0.0,          # Waktu setelah boost
            'session_start': time.time(),
            'last_update': time.time(),
            'activity_history': [],          # History aktivitas
            'total_boosts': 0,
            'achievements': [],
            'level_up_time': {}               # Catatan kapan naik level
        }
        logger.debug(f"Initialized leveling data for user {user_id}")
    
    def get_user_data(self, user_id: int) -> Dict:
        """Dapatkan data user, buat jika belum ada"""
        if user_id not in self.user_data:
            self.init_user(user_id)
        return self.user_data[user_id]
    
    # =========================================================================
    # CORE LEVELING CALCULATION
    # =========================================================================
    
    def update_duration(self, user_id: int, session_duration: float = None) -> float:
        """
        Update durasi percakapan
        
        Args:
            user_id: ID user
            session_duration: Durasi sesi dalam menit (opsional)
            
        Returns:
            Total durasi terkini
        """
        data = self.get_user_data(user_id)
        now = time.time()
        
        if session_duration is None:
            # Hitung durasi sejak last_update
            elapsed = (now - data['last_update']) / 60.0  # Konversi ke menit
            data['total_minutes'] += elapsed
        else:
            # Gunakan durasi yang diberikan
            data['total_minutes'] = session_duration
        
        data['last_update'] = now
        
        # Update level berdasarkan total minutes (tanpa boost)
        new_level = self.get_level_from_time(data['total_minutes'])
        if new_level > data['current_level']:
            old_level = data['current_level']
            data['current_level'] = new_level
            data['level_up_time'][new_level] = now
            logger.info(f"📈 User {user_id} leveled up: {old_level} → {new_level}")
        
        return data['total_minutes']
    
    def apply_activity_boost(self, user_id: int, activity: ActivityType, 
                               duration: float = 1.0) -> float:
        """
        Terapkan boost dari aktivitas
        
        Args:
            user_id: ID user
            activity: Tipe aktivitas
            duration: Durasi aktivitas dalam menit (default 1 menit)
            
        Returns:
            Boosted minutes yang ditambahkan
        """
        data = self.get_user_data(user_id)
        
        # Dapatkan multiplier
        multiplier = self.activity_boost.get(activity, 1.0)
        
        # Hitung boosted minutes
        boosted = duration * multiplier
        data['boosted_minutes'] += boosted
        data['total_boosts'] += 1
        
        # Catat history
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
        
        # Update level berdasarkan boosted minutes
        new_level = self.get_level_from_time(data['boosted_minutes'])
        if new_level > data['current_level']:
            old_level = data['current_level']
            data['current_level'] = new_level
            data['level_up_time'][new_level] = time.time()
            logger.info(f"📈 User {user_id} leveled up (boosted): {old_level} → {new_level}")
        
        logger.debug(f"Boost applied: {activity.value} x{multiplier} = +{boosted:.2f} menit")
        
        return boosted
    
    def get_level_from_time(self, minutes: float) -> int:
        """
        Dapatkan level berdasarkan total waktu
        
        Args:
            minutes: Total waktu dalam menit
            
        Returns:
            Level 1-12
        """
        for level, target in sorted(self.target_minutes.items()):
            if minutes <= target:
                return level
        return 12  # Maksimum level
    
    def get_time_needed_for_level(self, target_level: int) -> float:
        """
        Dapatkan waktu yang dibutuhkan untuk mencapai level tertentu
        
        Args:
            target_level: Level target (1-12)
            
        Returns:
            Waktu dalam menit
        """
        if target_level < 1:
            target_level = 1
        if target_level > 12:
            target_level = 12
        
        return self.target_minutes.get(target_level, 135)
    
    # =========================================================================
    # PROGRESS CALCULATION
    # =========================================================================
    
    def get_progress_to_next_level(self, user_id: int, use_boosted: bool = True) -> Dict:
        """
        Dapatkan progress menuju level berikutnya
        
        Args:
            user_id: ID user
            use_boosted: Gunakan boosted minutes (True) atau real minutes (False)
            
        Returns:
            Dict dengan progress info
        """
        data = self.get_user_data(user_id)
        current_level = data['current_level']
        
        if current_level >= 12:
            return {
                'current_level': 12,
                'next_level': None,
                'progress': 1.0,
                'percentage': 100,
                'minutes_achieved': self.target_minutes[12],
                'minutes_needed': self.target_minutes[12],
                'remaining_minutes': 0
            }
        
        next_level = current_level + 1
        minutes_achieved = data['boosted_minutes'] if use_boosted else data['total_minutes']
        minutes_needed = self.target_minutes[next_level]
        minutes_current = self.target_minutes[current_level]
        
        # Progress menuju level berikutnya
        progress = (minutes_achieved - minutes_current) / (minutes_needed - minutes_current)
        progress = max(0.0, min(1.0, progress))
        
        # Sisa waktu ke level berikutnya
        remaining = max(0, minutes_needed - minutes_achieved)
        
        return {
            'current_level': current_level,
            'next_level': next_level,
            'progress': progress,
            'percentage': round(progress * 100, 1),
            'minutes_achieved': round(minutes_achieved, 1),
            'minutes_needed': minutes_needed,
            'minutes_current_target': minutes_current,
            'remaining_minutes': round(remaining, 1),
            'use_boosted': use_boosted
        }
    
    def get_estimated_time(self, user_id: int, target_level: int = None) -> float:
        """
        Estimasi waktu ke level target
        
        Args:
            user_id: ID user
            target_level: Level target (None = level berikutnya)
            
        Returns:
            Estimasi waktu dalam menit
        """
        data = self.get_user_data(user_id)
        current_level = data['current_level']
        
        if current_level >= 12:
            return 0
        
        if target_level is None:
            target_level = current_level + 1
        
        if target_level > 12:
            target_level = 12
        
        minutes_needed = self.target_minutes[target_level]
        minutes_achieved = data['boosted_minutes']
        
        return max(0, minutes_needed - minutes_achieved)
    
    def get_estimated_time_string(self, user_id: int) -> str:
        """Dapatkan estimasi waktu dalam format string"""
        remaining = self.get_estimated_time(user_id)
        
        if remaining <= 0:
            return "Sekarang!"
        
        if remaining < 1:
            return f"{int(remaining * 60)} detik"
        elif remaining < 60:
            return f"{int(remaining)} menit"
        else:
            hours = int(remaining // 60)
            minutes = int(remaining % 60)
            return f"{hours} jam {minutes} menit"
    
    # =========================================================================
    # ACTIVITY DETECTION HELPERS
    # =========================================================================
    
    def detect_activity_from_text(self, text: str) -> List[ActivityType]:
        """
        Deteksi aktivitas dari teks pesan
        (Untuk digunakan oleh ActivityDetector nanti)
        
        Args:
            text: Pesan user
            
        Returns:
            List aktivitas yang terdeteksi
        """
        text_lower = text.lower()
        detected = []
        
        # Keywords untuk setiap aktivitas
        keywords = {
            ActivityType.CLIMAX: ['climax', 'keluar', 'orgasme', 'crot', 'come', 'ahhh', 'aaahhh'],
            ActivityType.INTIMACY: ['masuk', 'gerak', 'dalam', 'entot', 'doggy', 'misionaris', 'pancung'],
            ActivityType.KISS: ['cium', 'kiss', 'bibir', 'kecup', 'lidah'],
            ActivityType.SENSITIVE_TOUCH: ['leher', 'dada', 'puting', 'paha dalam', 'vagina', 'klitoris'],
            ActivityType.TOUCH: ['sentuh', 'pegang', 'raba', 'elus', 'touch', 'usap'],
        }
        
        for activity, words in keywords.items():
            for word in words:
                if word in text_lower:
                    detected.append(activity)
                    break
        
        return detected
    
    # =========================================================================
    # RESET & CLEANUP
    # =========================================================================
    
    def reset_user(self, user_id: int):
        """Reset data user"""
        if user_id in self.user_data:
            del self.user_data[user_id]
            logger.info(f"Reset leveling data for user {user_id}")
    
    def cleanup_inactive_users(self, max_age_hours: int = 24):
        """Hapus data user yang tidak aktif"""
        now = time.time()
        cutoff = now - (max_age_hours * 3600)
        
        to_delete = []
        for user_id, data in self.user_data.items():
            if data['last_update'] < cutoff:
                to_delete.append(user_id)
        
        for user_id in to_delete:
            del self.user_data[user_id]
        
        if to_delete:
            logger.info(f"Cleaned up {len(to_delete)} inactive users")
        
        return len(to_delete)
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    def get_stats(self, user_id: int = None) -> Dict:
        """Dapatkan statistik leveling"""
        if user_id:
            data = self.get_user_data(user_id)
            progress = self.get_progress_to_next_level(user_id)
            
            return {
                'user_id': user_id,
                'current_level': data['current_level'],
                'total_minutes': round(data['total_minutes'], 1),
                'boosted_minutes': round(data['boosted_minutes'], 1),
                'total_boosts': data['total_boosts'],
                'progress': progress,
                'estimated_time': self.get_estimated_time_string(user_id),
                'session_duration': round((time.time() - data['session_start']) / 60, 1),
                'activity_count': len(data['activity_history'])
            }
        else:
            # Global stats
            active_users = len(self.user_data)
            avg_level = sum(d['current_level'] for d in self.user_data.values()) / active_users if active_users else 0
            
            return {
                'active_users': active_users,
                'avg_level': round(avg_level, 1),
                'total_boosts': sum(d['total_boosts'] for d in self.user_data.values()),
                'target_levels': self.target_minutes
            }


__all__ = ['TimeBasedLeveling', 'ActivityType']
