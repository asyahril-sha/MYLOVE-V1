#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - TIME BASED LEVELING V2
=============================================================================
Sistem leveling berdasarkan DURASI PERCAKAPAN (bukan jumlah chat)
- 60 menit → Level 7 (bisa intim)
- 120 menit → Level 11 (deep connection)
- Activity boost untuk mempercepat progress
- Realistis seperti hubungan manusia
=============================================================================
"""

import time
import logging
import math
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ActivityType(str, Enum):
    """Tipe aktivitas yang mempengaruhi progress"""
    CHAT = "chat"               # Chat biasa
    FLIRT = "flirt"             # Godaan
    KISS = "kiss"               # Ciuman
    TOUCH = "touch"             # Sentuhan
    INTIM = "intim"             # Intim
    CLIMAX = "climax"           # Climax
    AFTERCARE = "aftercare"     # Aftercare
    DEEP_TALK = "deep_talk"     # Ngobrol dalam
    CURHAT = "curhat"           # Curhat


class TimeBasedLevelingV2:
    """
    Leveling berdasarkan durasi percakapan
    - Waktu dihitung saat user dan bot aktif chat
    - Bukan jumlah chat, tapi lama interaksi
    - Activity boost untuk aktivitas tertentu
    """
    
    def __init__(self):
        # Target waktu per level (dalam menit)
        self.level_targets = {
            1: 0,       # Level 1: 0 menit
            2: 5,       # Level 2: 5 menit
            3: 12,      # Level 3: 12 menit
            4: 20,      # Level 4: 20 menit
            5: 30,      # Level 5: 30 menit
            6: 42,      # Level 6: 42 menit
            7: 60,      # Level 7: 60 menit (bisa intim!)
            8: 75,      # Level 8: 75 menit
            9: 90,      # Level 9: 90 menit
            10: 105,    # Level 10: 105 menit
            11: 120,    # Level 11: 120 menit (deep connection)
            12: 135     # Level 12: 135 menit (aftercare)
        }
        
        # Activity boost multipliers
        self.activity_boost = {
            ActivityType.CHAT: 1.0,        # Chat biasa
            ActivityType.FLIRT: 1.3,        # Godaan (30% lebih cepat)
            ActivityType.KISS: 1.5,          # Ciuman (50% lebih cepat)
            ActivityType.TOUCH: 1.5,         # Sentuhan (50% lebih cepat)
            ActivityType.INTIM: 2.0,          # Intim (2x lebih cepat)
            ActivityType.CLIMAX: 3.0,         # Climax (3x lebih cepat)
            ActivityType.AFTERCARE: 0.5,      # Aftercare (lebih lambat, untuk reset)
            ActivityType.DEEP_TALK: 1.2,       # Ngobrol dalam (20% lebih cepat)
            ActivityType.CURHAT: 1.1           # Curhat (10% lebih cepat)
        }
        
        # Session tracking
        self.sessions = {}  # {session_id: session_data}
        
        logger.info("✅ TimeBasedLevelingV2 initialized")
    
    # =========================================================================
    # SESSION MANAGEMENT
    # =========================================================================
    
    async def start_session(self, session_id: str, user_id: int, role: str):
        """
        Memulai session baru
        
        Args:
            session_id: ID sesi
            user_id: ID user
            role: Nama role
        """
        self.sessions[session_id] = {
            'session_id': session_id,
            'user_id': user_id,
            'role': role,
            'start_time': time.time(),
            'last_message_time': time.time(),
            'total_duration': 0.0,  # Total menit
            'effective_duration': 0.0,  # Durasi dengan boost
            'current_level': 1,
            'message_count': 0,
            'activities': [],
            'activity_log': [],
            'is_paused': False,
            'paused_time': None,
            'total_paused_duration': 0.0,
            'level_up_messages': []
        }
        
        logger.info(f"Leveling session started: {session_id}")
    
    async def pause_session(self, session_id: str):
        """
        Pause session (waktu berhenti)
        
        Args:
            session_id: ID sesi
        """
        if session_id not in self.sessions:
            return
        
        self.sessions[session_id]['is_paused'] = True
        self.sessions[session_id]['paused_time'] = time.time()
        
        logger.info(f"Session paused: {session_id}")
    
    async def resume_session(self, session_id: str):
        """
        Resume session (waktu jalan lagi)
        
        Args:
            session_id: ID sesi
        """
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        if session['is_paused'] and session['paused_time']:
            paused_duration = time.time() - session['paused_time']
            session['total_paused_duration'] += paused_duration
            session['is_paused'] = False
            session['paused_time'] = None
            session['last_message_time'] = time.time()
            
            logger.info(f"Session resumed after {paused_duration:.1f}s pause: {session_id}")
    
    async def end_session(self, session_id: str) -> Dict:
        """
        Mengakhiri session
        
        Args:
            session_id: ID sesi
            
        Returns:
            Dict dengan statistik session
        """
        if session_id not in self.sessions:
            return {}
        
        session = self.sessions[session_id]
        
        # Hitung total durasi
        if not session['is_paused']:
            last_segment = time.time() - session['last_message_time']
            session['total_duration'] += last_segment / 60
        
        result = {
            'session_id': session_id,
            'total_duration_minutes': round(session['total_duration'], 1),
            'effective_duration_minutes': round(session['effective_duration'], 1),
            'final_level': session['current_level'],
            'message_count': session['message_count'],
            'activities': session['activities'],
            'level_ups': session['level_up_messages']
        }
        
        del self.sessions[session_id]
        logger.info(f"Session ended: {session_id}")
        
        return result
    
    # =========================================================================
    # PROGRESS CALCULATION
    # =========================================================================
    
    async def update_progress(self, 
                             session_id: str, 
                             activity_type: ActivityType = ActivityType.CHAT,
                             duration: float = None) -> Dict:
        """
        Update progress berdasarkan aktivitas
        
        Args:
            session_id: ID sesi
            activity_type: Tipe aktivitas
            duration: Durasi aktivitas (None = auto dari last message)
            
        Returns:
            Dict dengan status leveling
        """
        if session_id not in self.sessions:
            return {'error': 'Session not found'}
        
        session = self.sessions[session_id]
        
        if session['is_paused']:
            return {'error': 'Session is paused'}
        
        now = time.time()
        
        # Hitung durasi sejak pesan terakhir
        if duration is None:
            duration = (now - session['last_message_time']) / 60  # Konversi ke menit
        
        # Batasi durasi maksimal per update (misal 10 menit)
        duration = min(duration, 10.0)
        
        # Update total durasi
        session['total_duration'] += duration
        
        # Hitung durasi efektif dengan boost
        boost = self.activity_boost.get(activity_type, 1.0)
        effective_duration = duration * boost
        session['effective_duration'] += effective_duration
        
        # Update message count
        session['message_count'] += 1
        session['last_message_time'] = now
        
        # Catat aktivitas
        session['activities'].append(activity_type.value)
        session['activity_log'].append({
            'timestamp': now,
            'type': activity_type.value,
            'duration': duration,
            'boost': boost,
            'effective': effective_duration
        })
        
        # Cek level baru
        old_level = session['current_level']
        new_level = self._calculate_level(session['effective_duration'])
        
        level_up = False
        level_up_message = None
        
        if new_level > old_level:
            session['current_level'] = new_level
            level_up = True
            level_up_message = self._get_level_up_message(old_level, new_level, session['role'])
            
            session['level_up_messages'].append({
                'timestamp': now,
                'old_level': old_level,
                'new_level': new_level,
                'message': level_up_message
            })
            
            logger.info(f"Level UP! {session_id}: {old_level} → {new_level}")
        
        return {
            'session_id': session_id,
            'old_level': old_level,
            'new_level': new_level,
            'level_up': level_up,
            'level_up_message': level_up_message,
            'total_duration': round(session['total_duration'], 1),
            'effective_duration': round(session['effective_duration'], 1),
            'progress_to_next': self._get_progress_to_next(session['effective_duration'], new_level),
            'next_level_in': self._get_time_to_next(session['effective_duration'], new_level),
            'activity': activity_type.value,
            'boost': boost
        }
    
    def _calculate_level(self, effective_minutes: float) -> int:
        """
        Hitung level berdasarkan durasi efektif
        
        Args:
            effective_minutes: Durasi efektif dalam menit
            
        Returns:
            Level 1-12
        """
        for level, target in sorted(self.level_targets.items()):
            if effective_minutes <= target:
                return level
        return 12
    
    def _get_progress_to_next(self, effective_minutes: float, current_level: int) -> float:
        """
        Hitung progress ke level berikutnya (0-100%)
        
        Args:
            effective_minutes: Durasi efektif
            current_level: Level saat ini
            
        Returns:
            Persentase progress
        """
        if current_level >= 12:
            return 100.0
        
        current_target = self.level_targets[current_level]
        next_target = self.level_targets[current_level + 1]
        
        progress = ((effective_minutes - current_target) / 
                   (next_target - current_target)) * 100
        
        return max(0, min(100, progress))
    
    def _get_time_to_next(self, effective_minutes: float, current_level: int) -> float:
        """
        Hitung waktu yang dibutuhkan ke level berikutnya (menit)
        
        Args:
            effective_minutes: Durasi efektif
            current_level: Level saat ini
            
        Returns:
            Menit yang dibutuhkan
        """
        if current_level >= 12:
            return 0
        
        next_target = self.level_targets[current_level + 1]
        return max(0, next_target - effective_minutes)
    
    def _get_level_up_message(self, old_level: int, new_level: int, role: str) -> str:
        """
        Dapatkan pesan level up
        
        Args:
            old_level: Level lama
            new_level: Level baru
            role: Nama role
            
        Returns:
            Pesan level up
        """
        level_names = {
            1: "Malu-malu",
            2: "Mulai terbuka",
            3: "Goda-godaan",
            4: "Dekat",
            5: "Sayang",
            6: "PACAR/PDKT",
            7: "Nyaman (Bisa intim!)",
            8: "Eksplorasi",
            9: "Bergairah",
            10: "Passionate",
            11: "Deep Connection",
            12: "Aftercare"
        }
        
        old_name = level_names.get(old_level, f"Level {old_level}")
        new_name = level_names.get(new_level, f"Level {new_level}")
        
        messages = {
            7: f"🎉 **Level UP!** {old_name} → **{new_name}**\nSekarang kamu bisa intim dengan {role}!",
            11: f"🎉 **Level UP!** {old_name} → **{new_name}**\nKoneksi kalian semakin dalam...",
            12: f"🎉 **Level UP!** {old_name} → **{new_name}**\nButuh aftercare setelah ini ya..."
        }
        
        if new_level in messages:
            return messages[new_level]
        
        return f"📈 **Level UP!** {old_name} → **{new_name}**"
    
    # =========================================================================
    # GET STATUS
    # =========================================================================
    
    async def get_status(self, session_id: str) -> Optional[Dict]:
        """
        Dapatkan status leveling untuk session
        
        Args:
            session_id: ID sesi
            
        Returns:
            Dict status atau None
        """
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        level = session['current_level']
        effective = session['effective_duration']
        
        return {
            'session_id': session_id,
            'current_level': level,
            'level_name': self._get_level_name(level),
            'can_intim': level >= 7,
            'total_duration': round(session['total_duration'], 1),
            'effective_duration': round(effective, 1),
            'progress': self._get_progress_to_next(effective, level),
            'next_level_in': self._get_time_to_next(effective, level),
            'message_count': session['message_count'],
            'activities': session['activities'][-10:],  # 10 terakhir
            'is_paused': session['is_paused']
        }
    
    def _get_level_name(self, level: int) -> str:
        """Dapatkan nama level"""
        names = {
            1: "Malu-malu",
            2: "Mulai terbuka",
            3: "Goda-godaan",
            4: "Dekat",
            5: "Sayang",
            6: "PACAR/PDKT",
            7: "Nyaman",
            8: "Eksplorasi",
            9: "Bergairah",
            10: "Passionate",
            11: "Deep Connection",
            12: "Aftercare"
        }
        return names.get(level, f"Level {level}")
    
    def format_progress_bar(self, session_id: str, length: int = 20) -> str:
        """
        Format progress bar untuk display
        
        Args:
            session_id: ID sesi
            length: Panjang bar
            
        Returns:
            String progress bar
        """
        if session_id not in self.sessions:
            return "Session tidak ditemukan"
        
        session = self.sessions[session_id]
        level = session['current_level']
        progress = self._get_progress_to_next(session['effective_duration'], level)
        
        filled = int(progress / 100 * length)
        bar = "█" * filled + "░" * (length - filled)
        
        if level >= 12:
            next_text = "MAX"
        else:
            next_level = level + 1
            next_name = self._get_level_name(next_level)
            next_text = f"{next_name} (Level {next_level})"
        
        return f"{bar} {progress:.0f}% menuju {next_text}"
    
    # =========================================================================
    # RESET MECHANISM
    # =========================================================================
    
    async def reset_after_aftercare(self, session_id: str) -> int:
        """
        Reset level setelah aftercare (Level 12 → Level 7)
        
        Args:
            session_id: ID sesi
            
        Returns:
            Level baru
        """
        if session_id not in self.sessions:
            return 1
        
        session = self.sessions[session_id]
        old_level = session['current_level']
        
        if old_level == 12:
            # Reset ke level 7
            session['current_level'] = 7
            # Kurangi effective duration sesuai
            session['effective_duration'] = self.level_targets[7]
            
            logger.info(f"Reset after aftercare: {session_id} 12 → 7")
            
            return 7
        
        return old_level


__all__ = ['TimeBasedLevelingV2', 'ActivityType']
