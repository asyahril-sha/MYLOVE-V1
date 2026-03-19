#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - STATE TRACKER
=============================================================================
Melacak semua state dinamis yang berubah selama interaksi
- Lokasi, pakaian, posisi tubuh
- Mood, gairah, status intim
- Aktivitas saat ini
- Semua perubahan tercatat dan bisa dilacak
- Activity stack untuk aktivitas beruntun
=============================================================================
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class StateType(str, Enum):
    """Tipe state yang dilacak"""
    LOCATION = "location"
    CLOTHING = "clothing"
    POSITION = "position"
    MOOD = "mood"
    AROUSAL = "arousal"
    ACTIVITY = "activity"
    INTIMACY = "intimacy"
    PRIVACY = "privacy"


class StateTracker:
    """
    Melacak semua state dinamis dan perubahannya
    - Menyimpan history perubahan
    - Bisa melihat trend (misal: mood sering berubah)
    - Validasi perubahan yang masuk akal
    - Activity stack untuk aktivitas beruntun
    """
    
    def __init__(self, user_id: int, session_id: str):
        """
        Args:
            user_id: ID user
            session_id: ID session
        """
        self.user_id = user_id
        self.session_id = session_id
        
        # State saat ini
        self.current = {
            # ===== LOKASI =====
            'location': {
                'name': None,
                'category': None,
                'privacy_level': 1.0,
                'last_change': 0
            },
            
            # ===== PAKAIAN =====
            'clothing': {
                'name': None,
                'category': None,
                'last_change': 0,
                'change_reason': None
            },
            
            # ===== POSISI TUBUH =====
            'position': {
                'name': None,
                'description': None,
                'last_change': 0
            },
            
            # ===== MOOD =====
            'mood': {
                'primary': 'netral',
                'secondary': None,
                'intensity': 0.5,
                'last_change': 0
            },
            
            # ===== GAIrah =====
            'arousal': {
                'level': 0,  # 0-10
                'last_change': 0,
                'peak_level': 0,
                'climax_count': 0
            },
            
            # ===== INTIMASI =====
            'intimacy': {
                'is_active': False,
                'start_time': None,
                'duration': 0,
                'last_activity': None,
                'positions_used': [],
                'climax_count': 0
            },
            
            # ===== AKTIVITAS (BARU - LEBIH DETAIL) =====
            'activity': {
                'name': None,
                'details': {},
                'start_time': None,
                'last_update': None,
                'progress': None,
                'status': 'idle',  # idle, active, paused
                'history': []
            },
            
            # ===== ACTIVITY STACK (BARU) =====
            'activity_stack': [],  # Stack untuk aktivitas beruntun
            
            # ===== INTERAKSI =====
            'interaction': {
                'last_user_message': None,
                'last_bot_response': None,
                'total_messages': 0,
                'last_active': time.time()
            }
        }
        
        # History perubahan (untuk tracking)
        self.history = {
            'location': [],
            'clothing': [],
            'position': [],
            'mood': [],
            'arousal': [],
            'activity': [],
            'intimacy': []
        }
        
        # Rule validasi perubahan
        self.validation_rules = self._init_validation_rules()
        
        logger.info(f"✅ StateTracker initialized for user {user_id}, session {session_id}")
    
    def _init_validation_rules(self) -> Dict:
        """Inisialisasi rule validasi"""
        return {
            'location': {
                'plausible_transitions': {
                    'ruang tamu': ['kamar', 'dapur', 'teras', 'kamar mandi', 'taman'],
                    'kamar': ['kamar mandi', 'ruang tamu', 'balkon'],
                    'kamar mandi': ['kamar', 'ruang tamu'],
                    'dapur': ['ruang tamu', 'kamar mandi'],
                    'teras': ['ruang tamu', 'taman'],
                    'taman': ['teras', 'ruang tamu'],
                    'pantai': ['mobil', 'kafe', 'rumah'],
                    'mall': ['parkiran', 'mobil', 'kafe'],
                    'mobil': ['pantai', 'mall', 'rumah', 'parkiran'],
                    'kafe': ['mall', 'pantai', 'jalan'],
                    'kantor': ['ruang tamu', 'mobil'],
                },
                'min_time_between_change': 60,  # Minimal 1 menit antar pindah
                'require_transition': True
            },
            'clothing': {
                'require_reason': True,
                'valid_reasons': ['mandi', 'gerah', 'dingin', 'ganti baju', 'habis mandi', 'mau tidur', 'bangun tidur', 'buka baju', 'lepas baju'],
                'min_time_between_change': 300  # Minimal 5 menit antar ganti baju
            },
            'position': {
                'min_time_between_change': 10,  # 10 detik minimal
                'max_changes_per_hour': 20
            },
            'activity': {
                'min_duration': 60,  # Minimal 1 menit per aktivitas
                'max_pause_duration': 1800,  # Max pause 30 menit
                'valid_transitions': {
                    'masak': ['makan', 'bersih-bersih'],
                    'makan': ['masak', 'santai'],
                    'tidur': ['bangun', 'mimpi'],
                    'mandi': ['ganti baju', 'santai'],
                    'kerja': ['istirahat', 'makan'],
                }
            },
            'arousal': {
                'max_increase_per_minute': 5,  # Maksimal naik 5 per menit
                'max_decrease_per_minute': 3,
                'climax_cooldown': 300  # 5 menit cooldown setelah climax
            }
        }
    
    # =========================================================================
    # ACTIVITY MANAGEMENT (BARU)
    # =========================================================================
    
    def start_activity(self, activity: str, details: Optional[Dict] = None):
        """
        Mulai aktivitas baru
        
        Args:
            activity: Nama aktivitas (masak, tidur, mandi, dll)
            details: Detail aktivitas
        """
        now = time.time()
        
        # Simpan aktivitas sebelumnya ke history
        if self.current['activity']['name']:
            self.current['activity']['history'].append({
                'name': self.current['activity']['name'],
                'details': self.current['activity']['details'],
                'start_time': self.current['activity']['start_time'],
                'end_time': now,
                'duration': now - (self.current['activity']['start_time'] or now),
                'status': 'completed'
            })
        
        # Set aktivitas baru
        old_activity = self.current['activity']['name']
        self.current['activity'] = {
            'name': activity,
            'details': details or {},
            'start_time': now,
            'last_update': now,
            'progress': None,
            'status': 'active',
            'history': self.current['activity']['history']
        }
        
        # Catat history perubahan
        self.history['activity'].append({
            'timestamp': now,
            'from': old_activity,
            'to': activity,
            'details': details
        })
        
        logger.info(f"📌 Activity started: {activity}")
    
    def update_activity(self, activity: str, details: Optional[Dict] = None):
        """
        Update aktivitas (untuk backward compatibility)
        Arahkan ke start_activity
        """
        self.start_activity(activity, details)
    
    def update_activity_progress(self, progress: str, details: Optional[Dict] = None):
        """
        Update progress aktivitas
        
        Args:
            progress: Progress (misal: '75% matang')
            details: Detail tambahan
        """
        if self.current['activity']['name']:
            self.current['activity']['progress'] = progress
            self.current['activity']['last_update'] = time.time()
            
            if details:
                self.current['activity']['details'].update(details)
            
            logger.debug(f"📊 Activity progress: {progress}")
    
    def pause_activity(self):
        """Pause aktivitas saat ini"""
        if self.current['activity']['name'] and self.current['activity']['status'] == 'active':
            self.current['activity']['status'] = 'paused'
            self.current['activity']['last_update'] = time.time()
            
            # Push ke stack
            self.current['activity_stack'].append({
                'name': self.current['activity']['name'],
                'details': self.current['activity']['details'].copy(),
                'start_time': self.current['activity']['start_time'],
                'progress': self.current['activity']['progress'],
                'paused_at': time.time()
            })
            
            logger.info(f"⏸️ Activity paused: {self.current['activity']['name']}")
    
    def resume_activity(self) -> bool:
        """Resume aktivitas terakhir dari stack"""
        if self.current['activity_stack']:
            last = self.current['activity_stack'].pop()
            
            # Hitung durasi pause
            pause_duration = time.time() - last['paused_at']
            
            # Set aktivitas kembali
            self.current['activity'] = {
                'name': last['name'],
                'details': last['details'],
                'start_time': last['start_time'],
                'last_update': time.time(),
                'progress': last['progress'],
                'status': 'active',
                'history': self.current['activity']['history']
            }
            
            logger.info(f"▶️ Activity resumed: {last['name']} (paused for {pause_duration:.0f}s)")
            return True
        
        return False
    
    def end_activity(self, completed: bool = True):
        """
        Akhiri aktivitas saat ini
        
        Args:
            completed: True jika selesai, False jika dibatalkan
        """
        if self.current['activity']['name']:
            activity = self.current['activity']['name']
            duration = time.time() - (self.current['activity']['start_time'] or time.time())
            
            # Catat ke history
            self.current['activity']['history'].append({
                'name': activity,
                'details': self.current['activity']['details'].copy(),
                'start_time': self.current['activity']['start_time'],
                'end_time': time.time(),
                'duration': duration,
                'completed': completed
            })
            
            # Reset current activity
            old_activity = self.current['activity']['name']
            self.current['activity'] = {
                'name': None,
                'details': {},
                'start_time': None,
                'last_update': None,
                'progress': None,
                'status': 'idle',
                'history': self.current['activity']['history']
            }
            
            # Catat history
            self.history['activity'].append({
                'timestamp': time.time(),
                'from': old_activity,
                'to': None,
                'completed': completed,
                'duration': duration
            })
            
            status = "selesai" if completed else "dibatalkan"
            logger.info(f"🏁 Activity ended: {activity} ({status})")
    
    def get_current_activity(self) -> Optional[Dict]:
        """Dapatkan aktivitas saat ini"""
        if self.current['activity']['name']:
            return {
                'name': self.current['activity']['name'],
                'details': self.current['activity']['details'].copy(),
                'duration': time.time() - (self.current['activity']['start_time'] or time.time()),
                'progress': self.current['activity']['progress'],
                'status': self.current['activity']['status']
            }
        return None
    
    def get_activity_history(self, limit: int = 10) -> List[Dict]:
        """Dapatkan history aktivitas"""
        return self.current['activity']['history'][-limit:]
    
    # =========================================================================
    # LOCATION TRACKING
    # =========================================================================
    
    def update_location(self, name: str, category: str = "unknown") -> Tuple[bool, str]:
        """
        Update lokasi saat ini
        
        Returns:
            (success, message)
        """
        old_name = self.current['location']['name']
        
        # Validasi
        valid, msg = self._validate_location_change(old_name, name)
        if not valid:
            return False, msg
        
        # Update
        self.current['location'] = {
            'name': name,
            'category': category,
            'last_change': time.time()
        }
        
        # Set privacy level based on category
        if category == 'intimate':
            self.current['location']['privacy_level'] = 0.9
        elif category == 'public':
            self.current['location']['privacy_level'] = 0.3
        else:
            self.current['location']['privacy_level'] = 0.6
        
        # Catat history
        self.history['location'].append({
            'timestamp': time.time(),
            'from': old_name,
            'to': name,
            'category': category
        })
        
        logger.debug(f"📍 Location updated: {old_name} → {name}")
        return True, f"Pindah ke {name}"
    
    def _validate_location_change(self, old: Optional[str], new: str) -> Tuple[bool, str]:
        """Validasi perubahan lokasi"""
        if not old:
            return True, "OK"
        
        rules = self.validation_rules['location']
        
        # Cek waktu minimal antar perubahan
        last_change = self.current['location']['last_change']
        if time.time() - last_change < rules['min_time_between_change']:
            return False, f"Masih di {old}, tunggu bentar ya baru bisa pindah."
        
        # Cek transisi yang masuk akal
        if rules['require_transition']:
            old_lower = old.lower()
            new_lower = new.lower()
            
            for key, values in rules['plausible_transitions'].items():
                if key in old_lower:
                    if not any(v in new_lower for v in values):
                        return False, f"Gak bisa langsung dari {old} ke {new}."
                    break
        
        return True, "OK"
    
    # =========================================================================
    # CLOTHING TRACKING
    # =========================================================================
    
    def update_clothing(self, name: str, reason: str = "ganti baju") -> Tuple[bool, str]:
        """
        Update pakaian saat ini
        
        Returns:
            (success, message)
        """
        old_name = self.current['clothing']['name']
        
        # Validasi
        valid, msg = self._validate_clothing_change(old_name, reason)
        if not valid:
            return False, msg
        
        # Update
        self.current['clothing'] = {
            'name': name,
            'last_change': time.time(),
            'change_reason': reason
        }
        
        # Catat history
        self.history['clothing'].append({
            'timestamp': time.time(),
            'from': old_name,
            'to': name,
            'reason': reason
        })
        
        logger.debug(f"👗 Clothing updated: {old_name} → {name} ({reason})")
        return True, f"Ganti {name}"
    
    def _validate_clothing_change(self, old: Optional[str], reason: str) -> Tuple[bool, str]:
        """Validasi perubahan pakaian"""
        if not old:
            return True, "OK"
        
        rules = self.validation_rules['clothing']
        
        # Cek alasan
        if rules['require_reason']:
            if not reason or not any(r in reason.lower() for r in rules['valid_reasons']):
                return False, "Ganti baju harus ada alasannya dong. Mandi? Gerah?"
        
        # Cek waktu minimal
        last_change = self.current['clothing']['last_change']
        if time.time() - last_change < rules['min_time_between_change']:
            return False, "Baru aja ganti baju, kok ganti lagi?"
        
        return True, "OK"
    
    # =========================================================================
    # POSITION TRACKING
    # =========================================================================
    
    def update_position(self, name: str, description: str = "") -> Tuple[bool, str]:
        """Update posisi tubuh"""
        old_name = self.current['position']['name']
        
        # Validasi
        valid, msg = self._validate_position_change()
        if not valid:
            return False, msg
        
        # Update
        self.current['position'] = {
            'name': name,
            'description': description,
            'last_change': time.time()
        }
        
        # Catat history
        self.history['position'].append({
            'timestamp': time.time(),
            'from': old_name,
            'to': name
        })
        
        return True, f"Ganti posisi jadi {name}"
    
    def _validate_position_change(self) -> Tuple[bool, str]:
        """Validasi perubahan posisi"""
        rules = self.validation_rules['position']
        
        # Cek waktu minimal
        last_change = self.current['position']['last_change']
        if time.time() - last_change < rules['min_time_between_change']:
            return False, "Kebanyakan gerak, santai dulu."
        
        # Cek frekuensi per jam
        last_hour = time.time() - 3600
        changes_last_hour = [h for h in self.history['position'] 
                            if h['timestamp'] > last_hour]
        
        if len(changes_last_hour) > rules['max_changes_per_hour']:
            return False, "Kamu kok gelisah banget? Sering banget ganti posisi."
        
        return True, "OK"
    
    # =========================================================================
    # MOOD TRACKING
    # =========================================================================
    
    def update_mood(self, primary: str, secondary: Optional[str] = None, 
                     intensity: float = 0.5, reason: str = "") -> None:
        """Update mood saat ini"""
        old_mood = self.current['mood']['primary']
        
        self.current['mood'] = {
            'primary': primary,
            'secondary': secondary,
            'intensity': intensity,
            'last_change': time.time()
        }
        
        self.history['mood'].append({
            'timestamp': time.time(),
            'from': old_mood,
            'to': primary,
            'intensity': intensity,
            'reason': reason
        })
        
        logger.debug(f"🎭 Mood changed: {old_mood} → {primary}")
    
    # =========================================================================
    # AROUSAL TRACKING
    # =========================================================================
    
    def update_arousal(self, delta: int, reason: str = "") -> Tuple[bool, str]:
        """
        Update level gairah (0-10)
        
        Args:
            delta: Perubahan (-10 sd +10)
            reason: Alasan perubahan
            
        Returns:
            (success, message)
        """
        old_level = self.current['arousal']['level']
        new_level = max(0, min(10, old_level + delta))
        
        # Validasi
        valid, msg = self._validate_arousal_change(old_level, new_level, delta)
        if not valid:
            return False, msg
        
        # Update
        self.current['arousal']['level'] = new_level
        self.current['arousal']['last_change'] = time.time()
        
        if new_level > self.current['arousal']['peak_level']:
            self.current['arousal']['peak_level'] = new_level
        
        # Cek climax (naik drastis lalu turun)
        if delta >= 3 and old_level >= 7:
            self.current['arousal']['climax_count'] += 1
            self.current['intimacy']['climax_count'] += 1
            self.current['intimacy']['is_active'] = False
            self.history['intimacy'].append({
                'timestamp': time.time(),
                'type': 'climax',
                'level': old_level,
                'intensity': new_level
            })
        
        # Auto-set intimacy status
        if new_level >= 7 and not self.current['intimacy']['is_active']:
            self.start_intimacy()
        elif new_level < 7 and self.current['intimacy']['is_active']:
            self.end_intimacy()
        
        self.history['arousal'].append({
            'timestamp': time.time(),
            'from': old_level,
            'to': new_level,
            'delta': delta,
            'reason': reason
        })
        
        return True, f"Arousal: {old_level} → {new_level}"
    
    def _validate_arousal_change(self, old: int, new: int, delta: int) -> Tuple[bool, str]:
        """Validasi perubahan gairah"""
        rules = self.validation_rules['arousal']
        
        # Cek cooldown setelah climax
        if delta < 0 and old >= 8:
            last_climax = None
            for h in reversed(self.history['intimacy']):
                if h['type'] == 'climax':
                    last_climax = h['timestamp']
                    break
            
            if last_climax and time.time() - last_climax < rules['climax_cooldown']:
                return False, "Selesai climax, butuh istirahat dulu..."
        
        # Cek kecepatan naik
        if delta > 0:
            last_change = self.current['arousal']['last_change']
            if last_change:
                time_diff = time.time() - last_change
                rate = delta / (time_diff / 60) if time_diff > 0 else delta
                
                if rate > rules['max_increase_per_minute']:
                    return False, "Kok cepet banget? Santai dulu..."
        
        return True, "OK"
    
    # =========================================================================
    # INTIMACY TRACKING
    # =========================================================================
    
    def start_intimacy(self) -> None:
        """Mulai sesi intim"""
        if not self.current['intimacy']['is_active']:
            self.current['intimacy']['is_active'] = True
            self.current['intimacy']['start_time'] = time.time()
            
            self.history['intimacy'].append({
                'timestamp': time.time(),
                'type': 'start'
            })
            
            logger.debug("💕 Intimacy started")
    
    def end_intimacy(self) -> None:
        """Akhiri sesi intim"""
        if self.current['intimacy']['is_active']:
            duration = time.time() - self.current['intimacy']['start_time']
            self.current['intimacy']['is_active'] = False
            self.current['intimacy']['duration'] += duration
            self.current['intimacy']['start_time'] = None
            
            self.history['intimacy'].append({
                'timestamp': time.time(),
                'type': 'end',
                'duration': duration
            })
            
            logger.debug(f"💕 Intimacy ended (duration: {duration:.0f}s)")
    
    def add_intimacy_position(self, position: str):
        """Tambah posisi yang digunakan saat intim"""
        if position not in self.current['intimacy']['positions_used']:
            self.current['intimacy']['positions_used'].append(position)
    
    # =========================================================================
    # ACTIVITY TRACKING (OLD - UNTUK BACKWARD COMPATIBILITY)
    # =========================================================================
    
    def update_activity_old(self, name: str) -> None:
        """Update aktivitas saat ini (OLD METHOD)"""
        # Method ini dipanggil oleh kode lama
        # Arahkan ke start_activity
        self.start_activity(name)
    
    # =========================================================================
    # INTERACTION TRACKING
    # =========================================================================
    
    def register_interaction(self, user_message: str, bot_response: str) -> None:
        """Catat interaksi"""
        self.current['interaction']['last_user_message'] = user_message
        self.current['interaction']['last_bot_response'] = bot_response
        self.current['interaction']['total_messages'] += 1
        self.current['interaction']['last_active'] = time.time()
    
    # =========================================================================
    # GETTERS
    # =========================================================================
    
    def get_current_state(self) -> Dict:
        """Dapatkan semua state saat ini"""
        return {
            'location': self.current['location']['name'],
            'location_category': self.current['location']['category'],
            'privacy_level': self.current['location']['privacy_level'],
            'clothing': self.current['clothing']['name'],
            'position': self.current['position']['name'],
            'position_desc': self.current['position']['description'],
            'mood': self.current['mood']['primary'],
            'mood_intensity': self.current['mood']['intensity'],
            'arousal': self.current['arousal']['level'],
            'is_intimate': self.current['intimacy']['is_active'],
            'activity': self.current['activity']['name'],
            'activity_details': self.current['activity']['details'],
            'activity_status': self.current['activity']['status'],
            'total_messages': self.current['interaction']['total_messages'],
            'idle_seconds': time.time() - self.current['interaction']['last_active']
        }
    
    def get_state_for_prompt(self) -> str:
        """Format state untuk prompt AI"""
        state = self.get_current_state()
        activity = self.get_current_activity()
        
        parts = []
        
        if state['location']:
            parts.append(f"di {state['location']}")
        
        if state['clothing']:
            parts.append(f"pake {state['clothing']}")
        
        if state['position']:
            parts.append(f"lagi {state['position_desc'] or state['position']}")
        
        if activity:
            duration = activity.get('duration', 0)
            if duration < 60:
                duration_str = "baru mulai"
            else:
                duration_str = f"{int(duration/60)} menit"
            
            parts.append(f"sedang {activity['name']} ({duration_str})")
            
            if activity['details']:
                for key, value in activity['details'].items():
                    parts.append(f"{key}: {value}")
        
        if state['is_intimate']:
            parts.append("lagi intim")
        elif state['arousal'] >= 7:
            parts.append("horny")
        
        if state['privacy_level'] > 0.7:
            parts.append("sepi")
        elif state['privacy_level'] < 0.4:
            parts.append("rame")
        
        return "lagi " + ", ".join(parts) if parts else "santai"
    
    def get_state_summary(self) -> str:
        """Dapatkan ringkasan state"""
        activity = self.get_current_activity()
        activity_text = f"{activity['name']} ({activity['duration']:.0f}s)" if activity else "tidak ada"
        
        lines = [
            "📊 **STATE SAAT INI:**",
            f"📍 Lokasi: {self.current['location']['name'] or '?'}",
            f"👕 Pakaian: {self.current['clothing']['name'] or '?'}",
            f"🧍 Posisi: {self.current['position']['description'] or self.current['position']['name'] or '?'}",
            f"🎭 Mood: {self.current['mood']['primary']} ({self.current['mood']['intensity']:.0%})",
            f"🔥 Gairah: {self.current['arousal']['level']}/10",
            f"💕 Intim: {'Ya' if self.current['intimacy']['is_active'] else 'Tidak'}",
            f"🎯 Aktivitas: {activity_text}",
            f"💬 Total chat: {self.current['interaction']['total_messages']}"
        ]
        
        return "\n".join(lines)
    
    # =========================================================================
    # HISTORY
    # =========================================================================
    
    def get_history(self, state_type: StateType, limit: int = 10) -> List[Dict]:
        """Dapatkan history perubahan untuk state tertentu"""
        if state_type.value in self.history:
            return self.history[state_type.value][-limit:]
        return []
    
    def get_timeline(self, limit: int = 20) -> List[Dict]:
        """Dapatkan timeline semua perubahan"""
        timeline = []
        
        for state_type, events in self.history.items():
            for event in events:
                timeline.append({
                    'time': event['timestamp'],
                    'type': state_type,
                    'data': event
                })
        
        # Sort by time
        timeline.sort(key=lambda x: x['time'], reverse=True)
        
        return timeline[:limit]
    
    def format_timeline(self, limit: int = 10) -> str:
        """Format timeline untuk ditampilkan"""
        timeline = self.get_timeline(limit)
        
        if not timeline:
            return "Belum ada perubahan"
        
        lines = ["📜 **TIMELINE PERUBAHAN:**"]
        
        for t in timeline:
            time_str = datetime.fromtimestamp(t['time']).strftime("%H:%M:%S")
            data = t['data']
            
            if t['type'] == 'location':
                lines.append(f"• [{time_str}] Lokasi: {data['from']} → {data['to']}")
            elif t['type'] == 'clothing':
                lines.append(f"• [{time_str}] Baju: {data['from']} → {data['to']} ({data['reason']})")
            elif t['type'] == 'position':
                lines.append(f"• [{time_str}] Posisi: {data['from']} → {data['to']}")
            elif t['type'] == 'mood':
                lines.append(f"• [{time_str}] Mood: {data['from']} → {data['to']}")
            elif t['type'] == 'arousal':
                lines.append(f"• [{time_str}] Gairah: {data['from']} → {data['to']}")
            elif t['type'] == 'activity':
                if data.get('to'):
                    lines.append(f"• [{time_str}] Aktivitas: {data['from']} → {data['to']}")
                else:
                    lines.append(f"• [{time_str}] {data['from']} selesai ({data.get('duration', 0):.0f}s)")
            elif t['type'] == 'intimacy':
                if data['type'] == 'start':
                    lines.append(f"• [{time_str}] 🔥 Mulai intim")
                elif data['type'] == 'end':
                    lines.append(f"• [{time_str}] 💤 Selesai intim ({data.get('duration', 0):.0f}s)")
                elif data['type'] == 'climax':
                    lines.append(f"• [{time_str}] 💦 Climax! (intensitas: {data.get('intensity', 0)})")
        
        return "\n".join(lines)


__all__ = ['StateTracker', 'StateType']
