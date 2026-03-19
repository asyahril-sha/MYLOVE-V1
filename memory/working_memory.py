#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - WORKING MEMORY (VERSI HUMAN+)
=============================================================================
Ingatan jangka pendek SUPER MANUSIA (24 jam):
- Menyimpan 20±5 item terakhir (lebih banyak dari manusia)
- State saat ini (lokasi, baju, mood, aktivitas)
- Auto-expire setelah waktu tertentu
- Tracking aktivitas berkelanjutan
- Multiple state parallel (bisa ingat beberapa hal sekaligus)
- get_recent_context default 12 jam
=============================================================================
"""

import time
import logging
from typing import Dict, List, Optional, Any, Union
from collections import deque
from datetime import datetime

logger = logging.getLogger(__name__)


class WorkingMemory:
    """
    Working memory - ingatan jangka pendek SUPER MANUSIA
    Kapasitas lebih besar, expire lebih lama, tracking lebih detail
    """
    
    def __init__(self, capacity: int = 20, expire_seconds: int = 86400):  # 24 JAM (86400 detik)
        """
        Args:
            capacity: Jumlah item yang bisa diingat (default 20, manusia 7±2)
            expire_seconds: Waktu expire dalam detik (default 24 jam)
        """
        self.capacity = capacity
        self.expire_seconds = expire_seconds
        
        # ===== ITEMS DALAM WORKING MEMORY =====
        self.items = deque(maxlen=capacity)  # Pesan-pesan terakhir
        
        # ===== STATE SAAT INI (SELALU DIINGAT) =====
        self.current_state = {
            # ===== LOKASI =====
            'location': None,
            'location_history': [],
            'last_location_change': 0,
            'location_category': None,
            
            # ===== PAKAIAN =====
            'clothing': None,
            'clothing_history': [],
            'last_clothing_change': 0,
            'clothing_reason': None,
            
            # ===== POSISI TUBUH =====
            'position': None,
            'position_history': [],
            'last_position_change': 0,
            'position_description': None,
            
            # ===== AKTIVITAS =====
            'activity': None,
            'activity_history': [],
            'activity_start_time': None,
            'activity_details': {},
            
            # ===== MOOD & PERASAAN =====
            'mood': 'netral',
            'mood_history': [],
            'mood_intensity': 0.5,
            'mood_reason': None,
            
            # ===== GAIRAH =====
            'arousal_level': 0,
            'arousal_history': [],
            'last_arousal_change': 0,
            'is_intimate': False,
            'intimate_start_time': None,
            
            # ===== INTERAKSI =====
            'last_user_message': None,
            'last_bot_response': None,
            'last_response_time': 0,
            'last_interaction': time.time(),
            'total_messages_today': 0,
            
            # ===== KONTEKS =====
            'with_user': True,
            'privacy_level': 1.0,  # 0 (rame) - 1 (sepi)
            'time_of_day': None,
            
            # ===== IDENTITAS BOT =====
            'bot_name': None,
            'role': None,
            'rel_type': None,
            'instance_id': None,
            
            # ===== AKTIVITAS BERKELANJUTAN =====
            'current_activity': {
                'name': None,
                'details': {},
                'start_time': None,
                'last_update': None,
                'progress': None,
                'status': 'idle'  # idle, active, paused, completed
            },
            'activity_stack': [],  # Stack untuk multi-aktivitas
            'paused_activities': [],  # Aktivitas yang di-pause
            
            # ===== MULTI-TRACKING =====
            'parallel_states': {},  # Untuk tracking beberapa hal sekaligus
        }
        
        # ===== TIMELINE (URUTAN KEJADIAN) =====
        self.timeline = deque(maxlen=50)  # 50 kejadian terakhir
        
        # ===== MULTI-STATE TRACKING =====
        self.parallel_timelines = {}  # {category: deque}
        
        logger.info(f"✅ WorkingMemory HUMAN+ initialized (capacity: {capacity}, expire: {expire_seconds}s)")
    
    # =========================================================================
    # METHOD UNTUK AKTIVITAS BERKELANJUTAN
    # =========================================================================
    
    def start_activity(self, activity: str, details: Optional[Dict] = None):
        """
        Mulai aktivitas baru
        """
        now = time.time()
        
        # Simpan aktivitas sebelumnya ke history
        if self.current_state['current_activity']['name']:
            self.current_state['activity_history'].append({
                'name': self.current_state['current_activity']['name'],
                'details': self.current_state['current_activity']['details'],
                'start_time': self.current_state['current_activity']['start_time'],
                'end_time': now,
                'duration': now - (self.current_state['current_activity']['start_time'] or now)
            })
        
        # Push ke stack
        if self.current_state['current_activity']['name']:
            self.current_state['activity_stack'].append(
                self.current_state['current_activity'].copy()
            )
        
        # Set aktivitas baru
        self.current_state['current_activity'] = {
            'name': activity,
            'details': details or {},
            'start_time': now,
            'last_update': now,
            'progress': None,
            'status': 'active'
        }
        
        # Update juga field activity
        self.current_state['activity'] = activity
        self.current_state['activity_details'] = details or {}
        self.current_state['activity_start_time'] = now
        
        # Catat di timeline
        self._add_to_timeline('activity_start', f"Mulai {activity}")
        
        logger.debug(f"🎯 Activity started: {activity}")
    
    def pause_activity(self, reason: str = "pause"):
        """
        Pause aktivitas saat ini
        """
        if self.current_state['current_activity']['name']:
            self.current_state['current_activity']['status'] = 'paused'
            self.current_state['current_activity']['last_update'] = time.time()
            self.current_state['current_activity']['pause_reason'] = reason
            
            self.current_state['paused_activities'].append(
                self.current_state['current_activity'].copy()
            )
            
            self._add_to_timeline('activity_pause', 
                                 f"Pause {self.current_state['current_activity']['name']}")
            
            logger.debug(f"⏸️ Activity paused: {self.current_state['current_activity']['name']}")
    
    def resume_activity(self) -> bool:
        """
        Resume aktivitas terakhir yang di-pause
        """
        if self.current_state['paused_activities']:
            last = self.current_state['paused_activities'].pop()
            last['status'] = 'active'
            last['last_update'] = time.time()
            last['resumed_at'] = time.time()
            
            self.current_state['current_activity'] = last
            
            self._add_to_timeline('activity_resume', 
                                 f"Resume {last['name']}")
            
            logger.debug(f"▶️ Activity resumed: {last['name']}")
            return True
        
        elif self.current_state['activity_stack']:
            # Kembali ke aktivitas sebelumnya di stack
            last = self.current_state['activity_stack'].pop()
            last['status'] = 'active'
            last['last_update'] = time.time()
            
            self.current_state['current_activity'] = last
            
            self._add_to_timeline('activity_resume', 
                                 f"Kembali ke {last['name']}")
            
            logger.debug(f"↩️ Returned to activity: {last['name']}")
            return True
        
        return False
    
    def end_activity(self, completed: bool = True):
        """
        Akhiri aktivitas saat ini
        """
        if self.current_state['current_activity']['name']:
            activity = self.current_state['current_activity']['name']
            duration = time.time() - (self.current_state['current_activity']['start_time'] or time.time())
            
            # Catat ke history
            self.current_state['activity_history'].append({
                'name': activity,
                'details': self.current_state['current_activity']['details'],
                'start_time': self.current_state['current_activity']['start_time'],
                'end_time': time.time(),
                'duration': duration,
                'completed': completed
            })
            
            # Reset current activity
            self.current_state['current_activity'] = {
                'name': None,
                'details': {},
                'start_time': None,
                'last_update': None,
                'progress': None,
                'status': 'idle'
            }
            
            self.current_state['activity'] = None
            self.current_state['activity_details'] = {}
            self.current_state['activity_start_time'] = None
            
            status = "selesai" if completed else "dibatalkan"
            self._add_to_timeline('activity_end', f"{activity} {status}")
            
            logger.debug(f"🏁 Activity ended: {activity}")
    
    def update_activity_progress(self, progress: str, details: Optional[Dict] = None):
        """
        Update progress aktivitas
        """
        if self.current_state['current_activity']['name']:
            self.current_state['current_activity']['progress'] = progress
            self.current_state['current_activity']['last_update'] = time.time()
            
            if details:
                self.current_state['current_activity']['details'].update(details)
    
    def get_current_activity(self) -> Optional[Dict]:
        """
        Dapatkan aktivitas saat ini
        """
        if self.current_state['current_activity']['name']:
            activity = self.current_state['current_activity'].copy()
            if activity['start_time']:
                activity['duration'] = time.time() - activity['start_time']
            return activity
        return None
    
    # =========================================================================
    # METHOD UNTUK PARALLEL STATE TRACKING
    # =========================================================================
    
    def set_parallel_state(self, category: str, key: str, value: Any):
        """
        Set state paralel (untuk tracking beberapa hal sekaligus)
        """
        if category not in self.current_state['parallel_states']:
            self.current_state['parallel_states'][category] = {}
        
        self.current_state['parallel_states'][category][key] = {
            'value': value,
            'timestamp': time.time()
        }
    
    def get_parallel_state(self, category: str, key: str) -> Optional[Any]:
        """
        Get state paralel
        """
        if category in self.current_state['parallel_states']:
            if key in self.current_state['parallel_states'][category]:
                return self.current_state['parallel_states'][category][key]['value']
        return None
    
    def get_all_parallel(self, category: str) -> Dict:
        """
        Get semua state dalam kategori paralel
        """
        return self.current_state['parallel_states'].get(category, {})
    
    # =========================================================================
    # UPDATE METHODS UNTUK SETIAP ASPEK
    # =========================================================================
    
    def update_location(self, location: str, category: str = "private"):
        """Update lokasi dan catat history"""
        old_location = self.current_state['location']
        
        self.current_state['location'] = location
        self.current_state['location_category'] = category
        self.current_state['last_location_change'] = time.time()
        
        # Simpan ke history
        self.current_state['location_history'].append({
            'time': time.time(),
            'from': old_location,
            'to': location,
            'category': category
        })
        
        # Update privacy level
        if category == 'intimate':
            self.current_state['privacy_level'] = 0.9
        elif category == 'public':
            self.current_state['privacy_level'] = 0.3
        else:
            self.current_state['privacy_level'] = 0.6
        
        # Catat di timeline
        self._add_to_timeline('location_change', f"{old_location} → {location}")
        
        logger.debug(f"📍 Location updated: {old_location} → {location}")
    
    def update_clothing(self, clothing: str, reason: str = "ganti baju"):
        """Update pakaian dan catat history"""
        old_clothing = self.current_state['clothing']
        
        self.current_state['clothing'] = clothing
        self.current_state['clothing_reason'] = reason
        self.current_state['last_clothing_change'] = time.time()
        
        # Simpan ke history
        self.current_state['clothing_history'].append({
            'time': time.time(),
            'from': old_clothing,
            'to': clothing,
            'reason': reason
        })
        
        # Catat di timeline
        self._add_to_timeline('clothing_change', f"{old_clothing} → {clothing} ({reason})")
        
        logger.debug(f"👗 Clothing updated: {old_clothing} → {clothing}")
    
    def update_position(self, position: str, description: str = ""):
        """Update posisi tubuh"""
        old_position = self.current_state['position']
        
        self.current_state['position'] = position
        self.current_state['position_description'] = description or position
        self.current_state['last_position_change'] = time.time()
        
        # Simpan ke history
        self.current_state['position_history'].append({
            'time': time.time(),
            'from': old_position,
            'to': position,
            'description': description
        })
        
        self._add_to_timeline('position_change', f"{old_position} → {position}")
        
        logger.debug(f"🧍 Position updated: {old_position} → {position}")
    
    def update_mood(self, mood: str, intensity: float = 0.5, reason: str = ""):
        """Update mood"""
        old_mood = self.current_state['mood']
        
        self.current_state['mood'] = mood
        self.current_state['mood_intensity'] = intensity
        self.current_state['mood_reason'] = reason
        
        self.current_state['mood_history'].append({
            'time': time.time(),
            'from': old_mood,
            'to': mood,
            'intensity': intensity,
            'reason': reason
        })
        
        self._add_to_timeline('mood_change', f"{old_mood} → {mood}")
        
        logger.debug(f"🎭 Mood updated: {old_mood} → {mood}")
    
    def update_arousal(self, delta: int, reason: str = ""):
        """Update level gairah"""
        old_arousal = self.current_state['arousal_level']
        new_arousal = max(0, min(10, old_arousal + delta))
        
        self.current_state['arousal_level'] = new_arousal
        self.current_state['last_arousal_change'] = time.time()
        
        self.current_state['arousal_history'].append({
            'time': time.time(),
            'from': old_arousal,
            'to': new_arousal,
            'delta': delta,
            'reason': reason
        })
        
        if abs(new_arousal - old_arousal) >= 2:
            self._add_to_timeline('arousal_change', f"{old_arousal} → {new_arousal}")
        
        logger.debug(f"🔥 Arousal updated: {old_arousal} → {new_arousal}")
    
    def start_intimacy(self):
        """Mulai sesi intim"""
        self.current_state['is_intimate'] = True
        self.current_state['intimate_start_time'] = time.time()
        self.current_state['arousal_level'] = max(7, self.current_state['arousal_level'])
        
        self._add_to_timeline('intimacy_start', 'Mulai intim')
        logger.info("💕 Intimacy started")
    
    def end_intimacy(self):
        """Akhiri sesi intim"""
        self.current_state['is_intimate'] = False
        self.current_state['intimate_start_time'] = None
        
        self._add_to_timeline('intimacy_end', 'Selesai intim')
        logger.info("💕 Intimacy ended")
    
    def add_interaction(self, user_message: str, bot_response: str, context: Dict):
        """Simpan interaksi ke working memory"""
        now = time.time()
        
        self.current_state['last_user_message'] = user_message
        self.current_state['last_bot_response'] = bot_response
        self.current_state['last_response_time'] = now
        self.current_state['last_interaction'] = now
        self.current_state['total_messages_today'] += 1
        
        self.items.append({
            'time': now,
            'user': user_message[:100],
            'bot': bot_response[:100],
            'context': context
        })
        
        self._add_to_timeline('interaction', f"User: {user_message[:50]}...")
    
    def set_last_bot_response(self, response: str):
        """Simpan respons terakhir"""
        self.current_state['last_bot_response'] = response
        self.current_state['last_response_time'] = time.time()
    
    def get_last_bot_response(self) -> Optional[str]:
        """Dapatkan respons terakhir"""
        return self.current_state.get('last_bot_response')
    
    # =========================================================================
    # TIMELINE MANAGEMENT
    # =========================================================================
    
    def _add_to_timeline(self, event_type: str, data: str):
        """Tambahkan ke timeline"""
        self.timeline.append({
            'time': time.time(),
            'type': event_type,
            'data': data
        })
    
    def get_timeline(self, limit: int = 20) -> List[Dict]:
        """Dapatkan timeline"""
        return list(self.timeline)[-limit:]
    
    # =========================================================================
    # GET RECENT CONTEXT (DEFAULT 12 JAM)
    # =========================================================================
    
    def get_recent_context(self, seconds: int = 43200) -> Dict:
        """
        Dapatkan konteks dari beberapa detik terakhir
        Default: 12 jam (43200 detik)
        
        Args:
            seconds: Jumlah detik ke belakang (default 12 jam)
        
        Returns:
            Dict berisi konteks recent
        """
        cutoff = time.time() - seconds
        recent_items = [i for i in self.items if i['time'] > cutoff]
        recent_timeline = [t for t in self.timeline if t['time'] > cutoff]
        
        current_activity = self.get_current_activity()
        
        return {
            'current_state': self.get_current_state(),
            'recent_interactions': len(recent_items),
            'recent_timeline': recent_timeline[-10:],
            'current_activity': current_activity,
            'location': self.current_state['location'],
            'clothing': self.current_state['clothing'],
            'mood': self.current_state['mood'],
            'arousal': self.current_state['arousal_level'],
            'is_intimate': self.current_state['is_intimate']
        }
    
    def get_current_state(self) -> Dict:
        """Dapatkan semua state saat ini"""
        # Update time of day
        hour = datetime.now().hour
        if 5 <= hour < 11:
            self.current_state['time_of_day'] = 'pagi'
        elif 11 <= hour < 15:
            self.current_state['time_of_day'] = 'siang'
        elif 15 <= hour < 18:
            self.current_state['time_of_day'] = 'sore'
        else:
            self.current_state['time_of_day'] = 'malam'
        
        return self.current_state.copy()
    
    # =========================================================================
    # FORGETTING
    # =========================================================================
    
    def forget_old_memories(self):
        """Lupakan ingatan yang terlalu lama"""
        cutoff = time.time() - self.expire_seconds
        
        # Bersihkan items
        self.items = deque(
            [i for i in self.items if i['time'] > cutoff],
            maxlen=self.capacity
        )
        
        # Bersihkan timeline
        self.timeline = deque(
            [t for t in self.timeline if t['time'] > cutoff],
            maxlen=50
        )
        
        # Bersihkan history
        for hist in ['location_history', 'clothing_history', 'position_history', 
                    'activity_history', 'mood_history', 'arousal_history']:
            self.current_state[hist] = [
                h for h in self.current_state[hist] 
                if h['time'] > cutoff
            ]
        
        logger.debug(f"Forgot memories older than {self.expire_seconds}s")
    
    # =========================================================================
    # FORMAT UNTUK PROMPT
    # =========================================================================
    
    def format_for_prompt(self) -> str:
        """Format working memory untuk prompt"""
        state = self.get_current_state()
        activity = self.get_current_activity()
        
        lines = [
            "🧠 **WORKING MEMORY (24 jam):**",
            f"📍 Lokasi: {state['location'] or '?'}",
            f"👕 Pakaian: {state['clothing'] or '?'}",
            f"🧍 Posisi: {state['position_description'] or state['position'] or '?'}",
            f"🎭 Mood: {state['mood']} ({state['mood_intensity']:.0%})",
            f"🔥 Gairah: {state['arousal_level']}/10",
            f"💕 Lagi intim: {'Ya' if state['is_intimate'] else 'Tidak'}",
            f"🕐 Waktu: {state['time_of_day']}",
        ]
        
        if activity:
            duration = time.time() - (activity['start_time'] or time.time())
            duration_str = f"{int(duration/60)} menit" if duration > 60 else f"{int(duration)} detik"
            lines.append(f"🎯 Aktivitas: {activity['name']} ({duration_str})")
            if activity['details']:
                for key, value in activity['details'].items():
                    lines.append(f"   • {key}: {value}")
        
        lines.append("")
        lines.append("**Timeline terakhir:**")
        for t in list(self.timeline)[-5:]:
            time_str = datetime.fromtimestamp(t['time']).strftime("%H:%M")
            lines.append(f"• [{time_str}] {t['data']}")
        
        return "\n".join(lines)


__all__ = ['WorkingMemory']
