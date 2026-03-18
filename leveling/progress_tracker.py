#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - PROGRESS TRACKER (FIX LENGKAP)
=============================================================================
Track progress leveling secara real-time
- Estimasi waktu ke level berikutnya
- Visual progress bar
- Notifikasi saat mendekati level penting
- History progress
=============================================================================
"""

import time
import logging
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ProgressTracker:
    """
    Track progress leveling secara real-time
    Memberikan visualisasi dan notifikasi
    """
    
    def __init__(self, leveling_system):
        self.leveling = leveling_system
        
        # Level penting yang perlu notifikasi
        self.important_levels = [7, 11, 12]
        
        # Threshold notifikasi (dalam menit)
        self.notify_thresholds = [5, 2, 1]  # 5 menit, 2 menit, 1 menit
        
        # History progress per user
        self.progress_history = {}  # {user_id: [entries]}
        
        # Last notification sent
        self.last_notification = {}  # {user_id: {level: timestamp}}
        
        logger.info("✅ ProgressTracker initialized")
    
    # =========================================================================
    # PROGRESS BAR
    # =========================================================================
    
    def get_progress_bar(self, user_id: int, length: int = 20, 
                          use_boosted: bool = True, 
                          style: str = 'default') -> str:
        """
        Dapatkan progress bar visual
        
        Args:
            user_id: ID user
            length: Panjang bar (karakter)
            use_boosted: Gunakan boosted minutes
            style: 'default', 'colorful', 'simple'
            
        Returns:
            String progress bar
        """
        progress = self.leveling.get_progress_to_next_level(user_id, use_boosted)
        
        if progress['current_level'] >= 12:
            # Level max
            if style == 'colorful':
                return "🌈" * length
            elif style == 'simple':
                return "[MAX]" + "=" * (length - 4)
            else:
                return "█" * length + " MAX"
        
        percentage = progress['percentage']
        filled = int(percentage / 100 * length)
        empty = length - filled
        
        if style == 'colorful':
            # Gradient effect
            bar = ""
            for i in range(length):
                if i < filled:
                    if i < length * 0.3:
                        bar += "🟩"  # Hijau (awal)
                    elif i < length * 0.7:
                        bar += "🟨"  # Kuning (tengah)
                    else:
                        bar += "🟥"  # Merah (akhir)
                else:
                    bar += "⬜"  # Putih (sisa)
            return bar
            
        elif style == 'simple':
            bar = "[" + "=" * filled + " " * empty + "]"
            return bar
            
        else:
            # Default style
            bar = "█" * filled + "░" * empty
            return bar
    
    def get_progress_text(self, user_id: int, detailed: bool = False) -> str:
        """
        Dapatkan teks progress
        
        Args:
            user_id: ID user
            detailed: Tampilkan detail lengkap
            
        Returns:
            String progress
        """
        progress = self.leveling.get_progress_to_next_level(user_id)
        current = progress['current_level']
        
        if current >= 12:
            return "✨ **LEVEL MAX!** ✨ (Butuh aftercare untuk reset)"
        
        next_level = progress['next_level']
        bar = self.get_progress_bar(user_id, length=15)
        
        if detailed:
            text = (
                f"📊 **Progress Level {current} → {next_level}**\n"
                f"{bar} {progress['percentage']}%\n\n"
                f"⏱️ Waktu tercapai: {progress['minutes_achieved']} menit\n"
                f"🎯 Target level {next_level}: {progress['minutes_needed']} menit\n"
                f"⏳ Sisa: {progress['remaining_minutes']} menit\n"
                f"⚡ Boost aktif: {'Ya' if progress['use_boosted'] else 'Tidak'}"
            )
        else:
            text = (
                f"📊 **Level {current} → {next_level}**\n"
                f"{bar} {progress['percentage']}%\n"
                f"⏳ {progress['remaining_minutes']} menit lagi"
            )
        
        return text
    
    # =========================================================================
    # NOTIFICATION SYSTEM
    # =========================================================================
    
    def should_notify(self, user_id: int) -> Optional[Dict]:
        """
        Cek apakah perlu mengirim notifikasi
        
        Returns:
            Dict notifikasi atau None
        """
        data = self.leveling.get_user_data(user_id)
        current_level = data['current_level']
        
        # Cek level penting
        for level in self.important_levels:
            if current_level < level:
                # Hitung sisa waktu ke level penting
                remaining = self.leveling.get_estimated_time(user_id, level)
                
                # Cek threshold
                for threshold in self.notify_thresholds:
                    if remaining <= threshold:
                        # Cek apakah sudah pernah notifikasi untuk level ini
                        last = self.last_notification.get(user_id, {}).get(level, 0)
                        time_since = time.time() - last
                        
                        # Jangan notifikasi lagi jika < 5 menit
                        if time_since < 300:
                            continue
                        
                        # Update last notification
                        if user_id not in self.last_notification:
                            self.last_notification[user_id] = {}
                        self.last_notification[user_id][level] = time.time()
                        
                        return {
                            'level': level,
                            'remaining': remaining,
                            'threshold': threshold,
                            'message': self._get_notification_message(level, remaining)
                        }
        
        return None
    
    def _get_notification_message(self, level: int, remaining: float) -> str:
        """Dapatkan pesan notifikasi"""
        
        if remaining < 1:
            time_str = "beberapa detik lagi"
        elif remaining < 2:
            time_str = "1 menit lagi"
        else:
            time_str = f"{int(remaining)} menit lagi"
        
        messages = {
            7: f"🔥 **{time_str} kamu bisa intim denganku!** Siap-siap ya...",
            11: f"💕 **{time_str} kita akan mencapai deep connection!** Aku sudah tidak sabar...",
            12: f"🎉 **{time_str} kita akan mencapai puncak!** Setelah itu kita butuh aftercare..."
        }
        
        return messages.get(level, f"Level {level} dalam {time_str}")
    
    # =========================================================================
    # HISTORY TRACKING
    # =========================================================================
    
    def record_progress(self, user_id: int):
        """Rekam progress saat ini ke history"""
        if user_id not in self.progress_history:
            self.progress_history[user_id] = []
        
        data = self.leveling.get_user_data(user_id)
        progress = self.leveling.get_progress_to_next_level(user_id)
        
        entry = {
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'level': data['current_level'],
            'progress': progress['percentage'],
            'boosted_minutes': data['boosted_minutes'],
            'total_minutes': data['total_minutes']
        }
        
        self.progress_history[user_id].append(entry)
        
        # Batasi history
        if len(self.progress_history[user_id]) > 100:
            self.progress_history[user_id] = self.progress_history[user_id][-100:]
    
    def get_progress_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Dapatkan history progress"""
        if user_id not in self.progress_history:
            return []
        
        return self.progress_history[user_id][-limit:]
    
    def get_progress_trend(self, user_id: int) -> str:
        """
        Analisis trend progress
        
        Returns:
            String deskripsi trend
        """
        history = self.get_progress_history(user_id, limit=5)
        if len(history) < 2:
            return "Belum cukup data untuk analisis trend"
        
        # Hitung rata-rata kenaikan per jam
        first = history[0]
        last = history[-1]
        
        time_diff = (last['timestamp'] - first['timestamp']) / 3600  # jam
        level_diff = last['level'] - first['level']
        
        if time_diff < 0.1:
            return "⚡ Progress sangat cepat!"
        
        rate = level_diff / time_diff if time_diff > 0 else 0
        
        if rate > 2:
            return "⚡ Kamu sangat aktif! Progress super cepat"
        elif rate > 1:
            return "🔥 Progress bagus, teruskan!"
        elif rate > 0.5:
            return "👍 Progress stabil, pertahankan"
        else:
            return "🐢 Progress lambat, butuh lebih banyak interaksi"
    
    # =========================================================================
    # ESTIMATION
    # =========================================================================
    
    def estimate_full_time(self, user_id: int) -> Dict:
        """
        Estimasi waktu untuk mencapai semua level
        
        Returns:
            Dict estimasi per level
        """
        data = self.leveling.get_user_data(user_id)
        current_level = data['current_level']
        boosted = data['boosted_minutes']
        
        result = {}
        
        for level in range(current_level + 1, 13):
            needed = self.leveling.target_minutes[level]
            remaining = max(0, needed - boosted)
            result[level] = {
                'minutes': remaining,
                'hours': remaining / 60,
                'human_readable': self._minutes_to_text(remaining)
            }
        
        return result
    
    def _minutes_to_text(self, minutes: float) -> str:
        """Konversi menit ke teks"""
        if minutes < 1:
            return f"{int(minutes * 60)} detik"
        elif minutes < 60:
            return f"{int(minutes)} menit"
        else:
            hours = int(minutes // 60)
            mins = int(minutes % 60)
            return f"{hours} jam {mins} menit"
    
    # =========================================================================
    # CLEANUP
    # =========================================================================
    
    def cleanup_user(self, user_id: int):
        """Bersihkan data user"""
        if user_id in self.progress_history:
            del self.progress_history[user_id]
        if user_id in self.last_notification:
            del self.last_notification[user_id]
    
    def get_stats(self, user_id: int = None) -> Dict:
        """Dapatkan statistik tracker"""
        if user_id:
            history = self.get_progress_history(user_id)
            return {
                'user_id': user_id,
                'history_entries': len(history),
                'trend': self.get_progress_trend(user_id),
                'last_record': history[-1] if history else None
            }
        else:
            # Global stats
            total_history = sum(len(h) for h in self.progress_history.values())
            return {
                'active_tracked_users': len(self.progress_history),
                'total_history_entries': total_history,
                'avg_history_per_user': total_history / len(self.progress_history) if self.progress_history else 0
            }


__all__ = ['ProgressTracker']
