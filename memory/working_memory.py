#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - WORKING MEMORY (SHORT-TERM)
=============================================================================
Ingatan jangka pendek seperti manusia (12 jam)
- Menyimpan 7±2 item terakhir
- State saat ini (lokasi, baju, mood, aktivitas)
- Auto-expire setelah waktu tertentu
- Tracking aktivitas berkelanjutan
=============================================================================
"""

import time
import logging
from typing import Dict, List, Optional, Any
from collections import deque
from datetime import datetime

logger = logging.getLogger(__name__)


class WorkingMemory:
    """
    Working memory - ingatan jangka pendek
    Kapasitas terbatas, auto-expire
    """
    
    def __init__(self, capacity: int = 7, expire_seconds: int = 43200):  # 12 JAM
        """
        Args:
            capacity: Jumlah item yang bisa diingat (default 7)
            expire_seconds: Waktu expire dalam detik (default 12 jam)
        """
        self.capacity = capacity
        self.expire_seconds = expire_seconds
        
        # Items dalam working memory (FIFO)
        self.items = deque(maxlen=capacity)
        
        # State saat ini (selalu diingat)
        self.current_state = {
            # ===== LOKASI =====
            'location': None,           # Lagi di mana?
            'location_history': [],      # Riwayat lokasi hari ini
            'last_location_change': 0,   # Kapan terakhir pindah
            
            # ===== PAKAIAN =====
            'clothing': None,            # Lagi pakai apa?
            'clothing_history': [],      # Riwayat ganti baju
            'last_clothing_change': 0,   # Kapan terakhir ganti baju
            'clothing_reason': None,      # Alasan ganti baju (mandi, gerah, dll)
            
            # ===== POSISI TUBUH =====
            'position': None,             # Lagi posisi apa? (duduk, berdiri, berbaring)
            'position_history': [],      # Riwayat posisi
            'last_position_change': 0,    # Kapan terakhir ganti posisi
            
            # ===== MOOD & PERASAAN =====
            'mood': 'netral',              # Mood saat ini
            'mood_history': [],            # Riwayat mood
            'arousal_level': 0,            # Level gairah (0-10)
            'is_intimate': False,           # Lagi intim?
            'intimate_start_time': None,    # Kapan mulai intim
            
            # ===== AKTIVITAS =====
            'activity': None,               # Lagi ngapain?
            'activity_history': [],         # Riwayat aktivitas
            'activity_details': {},         # Detail aktivitas (misal: menu masakan)
            'activity_start_time': None,    # Kapan mulai aktivitas
            'last_activity': None,          # Aktivitas sebelumnya
            
            # ===== INTERAKSI =====
            'last_user_message': None,      # Pesan user terakhir
            'last_bot_response': None,      # Respon bot terakhir
            'last_response_time': 0,        # Kapan terakhir respon
            'last_interaction': time.time(), # Kapan terakhir chat
            
            # ===== KONTEKS =====
            'with_user': True,               # Lagi sendiri/berdua?
            'privacy_level': 1.0,            # 0 (rame) - 1 (sepi)
            'time_of_day': None,              # Pagi/siang/sore/malam
            
            # ===== UNTUK AI ENGINE =====
            'role': None,                     # Role bot (ipar, janda, dll)
            'bot_name': None,                  # Nama bot
            'rel_type': None,                   # Tipe hubungan (pdkt, hts, fwb)
            'instance_id': None,                 # ID instance (untuk multiple)
            'last_update': time.time(),           # Kapan terakhir diupdate
            
            # ===== AKTIVITAS BERKELANJUTAN (BARU) =====
            'current_activity': {
                'name': None,
                'details': {},
                'start_time': None,
                'last_update': None,
                'progress': None,
                'status': 'idle'  # idle, active, paused, completed
            },
            'activity_stack': [],               # Stack untuk aktivitas beruntun
            'paused_activities': [],            # Aktivitas yang di-pause
        }
        
        # Timeline (urutan kejadian singkat)
        self.timeline = deque(maxlen=20)
        
        logger.info(f"✅ WorkingMemory initialized (capacity: {capacity}, expire: {expire_seconds}s)")
    
    # =========================================================================
    # METHOD UNTUK AKTIVITAS BERKELANJUTAN (BARU)
    # =========================================================================
    
    def set_current_activity(self, activity: str, details: Optional[Dict] = None):
        """
        Set aktivitas saat ini
        
        Args:
            activity: Nama aktivitas (masak, tidur, mandi, dll)
            details: Detail aktivitas (misal: {'menu': 'ayam bakar'})
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
        
        # Set aktivitas baru
        self.current_state['current_activity'] = {
            'name': activity,
            'details': details or {},
            'start_time': now,
            'last_update': now,
            'progress': None,
            'status': 'active'
        }
        
        # Update juga field activity lama untuk backward compatibility
        self.current_state['activity'] = activity
        self.current_state['activity_details'] = details or {}
        self.current_state['activity_start_time'] = now
        
        # Catat di timeline
        self.timeline.append({
            'time': now,
            'type': 'activity_start',
            'data': f"Mulai {activity}"
        })
        
        logger.debug(f"🎯 Activity started: {activity} with details: {details}")
    
    def update_activity_progress(self, progress: str, details: Optional[Dict] = None):
        """
        Update progress aktivitas
        
        Args:
            progress: Progress (misal: '75% matang')
            details: Update detail (opsional)
        """
        if self.current_state['current_activity']['name']:
            self.current_state['current_activity']['progress'] = progress
            self.current_state['current_activity']['last_update'] = time.time()
            
            if details:
                self.current_state['current_activity']['details'].update(details)
                self.current_state['activity_details'].update(details)
            
            logger.debug(f"📊 Activity progress: {progress}")
    
    def pause_current_activity(self):
        """Pause aktivitas saat ini"""
        if self.current_state['current_activity']['name'] and self.current_state['current_activity']['status'] == 'active':
            self.current_state['current_activity']['status'] = 'paused'
            self.current_state['current_activity']['last_update'] = time.time()
            
            # Simpan ke paused activities
            self.current_state['paused_activities'].append(
                self.current_state['current_activity'].copy()
            )
            
            logger.debug(f"⏸️ Activity paused: {self.current_state['current_activity']['name']}")
    
    def resume_current_activity(self):
        """Resume aktivitas yang di-pause"""
        if self.current_state['paused_activities']:
            last_paused = self.current_state['paused_activities'].pop()
            self.current_state['current_activity'] = last_paused
            self.current_state['current_activity']['status'] = 'active'
            self.current_state['current_activity']['last_update'] = time.time()
            
            # Update juga field backward compatibility
            self.current_state['activity'] = last_paused['name']
            self.current_state['activity_details'] = last_paused['details']
            
            logger.debug(f"▶️ Activity resumed: {last_paused['name']}")
    
    def end_current_activity(self, completed: bool = True):
        """
        Akhiri aktivitas saat ini
        
        Args:
            completed: True jika selesai, False jika dibatalkan
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
            
            # Update backward compatibility
            self.current_state['activity'] = None
            self.current_state['activity_details'] = {}
            self.current_state['activity_start_time'] = None
            
            # Catat di timeline
            status = "selesai" if completed else "dibatalkan"
            self.timeline.append({
                'time': time.time(),
                'type': 'activity_end',
                'data': f"{activity} {status} (durasi: {duration:.0f}s)"
            })
            
            logger.debug(f"🏁 Activity ended: {activity} ({status})")
    
    def get_current_activity(self) -> Optional[Dict]:
        """Dapatkan aktivitas saat ini"""
        if self.current_state['current_activity']['name']:
            return self.current_state['current_activity'].copy()
        return None
    
    def get_activity_history(self, limit: int = 10) -> List[Dict]:
        """Dapatkan history aktivitas"""
        return self.current_state['activity_history'][-limit:]
    
    def push_activity_stack(self, activity: str, details: Optional[Dict] = None):
        """
        Push aktivitas ke stack (untuk aktivitas beruntun)
        Misal: masak → ngobrol → masak lagi
        """
        self.current_state['activity_stack'].append({
            'name': activity,
            'details': details,
            'pushed_at': time.time()
        })
        logger.debug(f"📌 Activity pushed to stack: {activity}")
    
    def pop_activity_stack(self) -> Optional[Dict]:
        """Pop aktivitas dari stack"""
        if self.current_state['activity_stack']:
            return self.current_state['activity_stack'].pop()
        return None
    
    def set_last_bot_response(self, response: str):
        """Simpan respons terakhir bot"""
        self.current_state['last_bot_response'] = response
        self.current_state['last_response_time'] = time.time()
    
    def get_last_bot_response(self) -> Optional[str]:
        """Dapatkan respons terakhir bot"""
        return self.current_state.get('last_bot_response')
    
    # =========================================================================
    # METHOD UPDATE STATE (YANG SUDAH ADA)
    # =========================================================================
    
    def update_state(self, role=None, bot_name=None, rel_type=None, instance_id=None):
        """
        Update state dengan data baru
        Method ini dipanggil oleh AI Engine
        """
        if role:
            self.current_state['role'] = role
        if bot_name:
            self.current_state['bot_name'] = bot_name
        if rel_type:
            self.current_state['rel_type'] = rel_type
        if instance_id:
            self.current_state['instance_id'] = instance_id
        
        # Update timestamp
        self.current_state['last_update'] = time.time()
        
        logger.debug(f"Working memory state updated: role={role}, bot_name={bot_name}")
    
    def update_location(self, location: str, category: str = "unknown"):
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
        
        # Update privacy level based on location
        if category == 'intimate':
            self.current_state['privacy_level'] = 0.9
        elif category == 'public':
            self.current_state['privacy_level'] = 0.3
        else:
            self.current_state['privacy_level'] = 0.6
        
        # Catat di timeline
        self.timeline.append({
            'time': time.time(),
            'type': 'location_change',
            'data': f"{old_location} → {location}"
        })
        
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
        self.timeline.append({
            'time': time.time(),
            'type': 'clothing_change',
            'data': f"{old_clothing} → {clothing} ({reason})"
        })
        
        logger.debug(f"👗 Clothing updated: {old_clothing} → {clothing} ({reason})")
    
    def update_position(self, position: str):
        """Update posisi tubuh"""
        old_position = self.current_state['position']
        
        self.current_state['position'] = position
        self.current_state['last_position_change'] = time.time()
        
        # Simpan ke history
        self.current_state['position_history'].append({
            'time': time.time(),
            'from': old_position,
            'to': position
        })
        
        self.timeline.append({
            'time': time.time(),
            'type': 'position_change',
            'data': f"{old_position} → {position}"
        })
    
    def update_mood(self, mood: str, reason: str = ""):
        """Update mood dan catat history"""
        old_mood = self.current_state['mood']
        
        self.current_state['mood'] = mood
        self.current_state['mood_history'].append({
            'time': time.time(),
            'from': old_mood,
            'to': mood,
            'reason': reason
        })
        
        self.timeline.append({
            'time': time.time(),
            'type': 'mood_change',
            'data': f"{old_mood} → {mood}"
        })
    
    def update_arousal(self, delta: int):
        """Update level gairah (0-10)"""
        old_arousal = self.current_state['arousal_level']
        new_arousal = max(0, min(10, old_arousal + delta))
        
        self.current_state['arousal_level'] = new_arousal
        
        # Auto-set is_intimate jika arousal >= 7
        if new_arousal >= 7 and not self.current_state['is_intimate']:
            self.start_intimacy()
        elif new_arousal < 7 and self.current_state['is_intimate']:
            self.end_intimacy()
        
        if abs(new_arousal - old_arousal) >= 2:
            self.timeline.append({
                'time': time.time(),
                'type': 'arousal_change',
                'data': f"{old_arousal} → {new_arousal}"
            })
    
    def start_intimacy(self):
        """Mulai sesi intim"""
        self.current_state['is_intimate'] = True
        self.current_state['intimate_start_time'] = time.time()
        self.current_state['arousal_level'] = max(7, self.current_state['arousal_level'])
        
        self.timeline.append({
            'time': time.time(),
            'type': 'intimacy_start',
            'data': 'Mulai intim'
        })
    
    def end_intimacy(self):
        """Akhiri sesi intim"""
        self.current_state['is_intimate'] = False
        self.current_state['intimate_start_time'] = None
        
        self.timeline.append({
            'time': time.time(),
            'type': 'intimacy_end',
            'data': 'Selesai intim'
        })
    
    def update_activity(self, activity: str):
        """Update aktivitas saat ini (untuk backward compatibility)"""
        # Method ini dipanggil oleh state tracker
        # Kita arahkan ke set_current_activity
        self.set_current_activity(activity)
    
    def add_interaction(self, user_message: str, bot_response: str, context: Dict):
        """Simpan interaksi ke working memory"""
        
        # Update state
        self.current_state['last_user_message'] = user_message
        self.current_state['last_bot_response'] = bot_response
        self.current_state['last_interaction'] = time.time()
        
        # Simpan item
        self.items.append({
            'time': time.time(),
            'user': user_message[:100],
            'bot': bot_response[:100],
            'context': context
        })
        
        # Update timeline
        self.timeline.append({
            'time': time.time(),
            'type': 'interaction',
            'data': f"User: {user_message[:50]}..."
        })
    
    # =========================================================================
    # GETTERS
    # =========================================================================
    
    def get_current_state(self) -> Dict:
        """Dapatkan state saat ini"""
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
    
    def get_recent_context(self, seconds: int = 300) -> Dict:
        """
        Dapatkan konteks dari beberapa detik terakhir
        Default: 5 menit (300 detik)
        """
        cutoff = time.time() - seconds
        recent_items = [i for i in self.items if i['time'] > cutoff]
        
        # Dapatkan timeline terbaru
        recent_timeline = list(self.timeline)[-5:]
        
        # Dapatkan aktivitas saat ini
        current_activity = self.get_current_activity()
        
        return {
            'current_state': self.get_current_state(),
            'recent_interactions': len(recent_items),
            'recent_timeline': recent_timeline,
            'current_activity': current_activity,
            'last_activity': self.current_state['activity'],
            'location': self.current_state['location'],
            'clothing': self.current_state['clothing'],
            'mood': self.current_state['mood'],
            'arousal': self.current_state['arousal_level'],
            'is_intimate': self.current_state['is_intimate']
        }
    
    def get_location_sequence(self, limit: int = 5) -> List[str]:
        """Dapatkan urutan lokasi terakhir"""
        locations = []
        for item in reversed(self.current_state['location_history'][-limit:]):
            locations.append(item['to'])
        return locations
    
    def get_clothing_sequence(self, limit: int = 5) -> List[str]:
        """Dapatkan urutan pakaian terakhir"""
        clothes = []
        for item in reversed(self.current_state['clothing_history'][-limit:]):
            clothes.append(item['to'])
        return clothes
    
    # =========================================================================
    # VALIDASI & KONSISTENSI
    # =========================================================================
    
    def is_location_consistent(self, new_location: str) -> bool:
        """Cek apakah pindah lokasi masuk akal"""
        current = self.current_state['location']
        if not current:
            return True
        
        # Transisi yang masuk akal
        plausible_transitions = {
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
        }
        
        current_lower = current.lower()
        new_lower = new_location.lower()
        
        for key, values in plausible_transitions.items():
            if key in current_lower:
                return any(v in new_lower for v in values)
        
        # Kalau gak ada aturan, cek selisih waktu
        last_change = self.current_state['last_location_change']
        if time.time() - last_change > 600:  # > 10 menit
            return True
        
        return False
    
    def is_clothing_consistent(self, new_clothing: str, reason: str = None) -> bool:
        """Cek apakah ganti baju masuk akal"""
        current = self.current_state['clothing']
        if not current:
            return True
        
        # Ganti baju harus ada alasan
        valid_reasons = ['mandi', 'gerah', 'dingin', 'ganti baju', 'habis mandi', 'buka baju', 'lepas baju']
        if reason and any(r in reason.lower() for r in valid_reasons):
            return True
        
        # Kalau alasan gak jelas, cek waktu
        last_change = self.current_state['last_clothing_change']
        if time.time() - last_change > 3600:  # > 1 jam
            return True
        
        return False
    
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
            maxlen=20
        )
        
        # Bersihkan history yang terlalu lama
        self.current_state['location_history'] = [
            h for h in self.current_state['location_history'] if h['time'] > cutoff
        ]
        self.current_state['clothing_history'] = [
            h for h in self.current_state['clothing_history'] if h['time'] > cutoff
        ]
        self.current_state['position_history'] = [
            h for h in self.current_state['position_history'] if h['time'] > cutoff
        ]
        self.current_state['activity_history'] = [
            h for h in self.current_state['activity_history'] if h['time'] > cutoff
        ]
        
        logger.debug(f"Forgot memories older than {self.expire_seconds}s")
    
    # =========================================================================
    # FORMATTING UNTUK PROMPT
    # =========================================================================
    
    def format_for_prompt(self) -> str:
        """Format working memory untuk dimasukkan ke prompt AI"""
        state = self.get_current_state()
        current_activity = self.get_current_activity()
        
        lines = [
            "📝 **WORKING MEMORY (12 jam terakhir)**",
            f"📍 Lokasi: {state['location'] or 'tidak diketahui'}",
            f"👕 Pakaian: {state['clothing'] or 'tidak diketahui'}",
            f"🧍 Posisi: {state['position'] or 'tidak diketahui'}",
            f"🎭 Mood: {state['mood']} (gairah: {state['arousal_level']}/10)",
            f"💕 Lagi intim: {'Ya' if state['is_intimate'] else 'Tidak'}",
            f"🕐 Waktu: {state['time_of_day']}",
        ]
        
        if current_activity:
            activity = current_activity
            duration = time.time() - (activity['start_time'] or time.time())
            duration_str = f"{int(duration/60)} menit" if duration > 60 else f"{int(duration)} detik"
            lines.append(f"🎯 Aktivitas: {activity['name']} ({duration_str})")
            if activity['details']:
                for key, value in activity['details'].items():
                    lines.append(f"   • {key}: {value}")
        
        lines.append("")
        lines.append("**Timeline terakhir:**")
        for t in list(self.timeline)[-3:]:
            lines.append(f"• {t['data']}")
        
        return "\n".join(lines)


__all__ = ['WorkingMemory']
