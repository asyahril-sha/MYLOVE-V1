#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - WORKING MEMORY (SHORT-TERM)
=============================================================================
Ingatan jangka pendek seperti manusia (5-10 menit)
- Menyimpan 7±2 item terakhir
- State saat ini (lokasi, baju, mood, aktivitas)
- Auto-expire setelah waktu tertentu
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
    
    def __init__(self, capacity: int = 7, expire_seconds: int = 14400):
        """
        Args:
            capacity: Jumlah item yang bisa diingat (default 7)
            expire_seconds: Waktu expire dalam detik (default 10 menit)
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
            'last_position_change': 0,    # Kapan terakhir ganti posisi
            
            # ===== MOOD & PERASAAN =====
            'mood': 'netral',              # Mood saat ini
            'mood_history': [],            # Riwayat mood
            'arousal_level': 0,            # Level gairah (0-10)
            'is_intimate': False,           # Lagi intim?
            'intimate_start_time': None,    # Kapan mulai intim
            
            # ===== AKTIVITAS =====
            'activity': None,               # Lagi ngapain?
            'last_activity': None,          # Aktivitas sebelumnya
            
            # ===== INTERAKSI =====
            'last_user_message': None,      # Pesan user terakhir
            'last_bot_response': None,      # Respon bot terakhir
            'last_interaction': time.time(), # Kapan terakhir chat
            
            # ===== KONTEKS =====
            'with_user': True,               # Lagi sendiri/berdua?
            'privacy_level': 1.0,            # 0 (rame) - 1 (sepi)
            'time_of_day': None,              # Pagi/siang/sore/malam
            
            # ===== UNTUK AI ENGINE (TAMBAHAN) =====
            'role': None,                     # Role bot (ipar, janda, dll)
            'bot_name': None,                  # Nama bot
            'rel_type': None,                   # Tipe hubungan (pdkt, hts, fwb)
            'instance_id': None,                 # ID instance (untuk multiple)
            'last_update': time.time()            # Kapan terakhir diupdate
        }
        
        # Timeline (urutan kejadian singkat)
        self.timeline = deque(maxlen=20)
        
        logger.info(f"✅ WorkingMemory initialized (capacity: {capacity}, expire: {expire_seconds}s)")
    
    # =========================================================================
    # METHOD BARU - UPDATE STATE (DIPANGGIL AI ENGINE)
    # =========================================================================
    
    def update_state(self, role=None, bot_name=None, rel_type=None, instance_id=None):
        """
        Update state dengan data baru
        Method ini dipanggil oleh AI Engine saat start_session
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
    
    # =========================================================================
    # METHOD YANG SUDAH ADA (UPDATE STATE LAINNYA)
    # =========================================================================
    
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
        
        logger.debug(f"Location updated: {old_location} → {location}")
    
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
        
        logger.debug(f"Clothing updated: {old_clothing} → {clothing} ({reason})")
    
    def update_position(self, position: str):
        """Update posisi tubuh"""
        old_position = self.current_state['position']
        
        self.current_state['position'] = position
        self.current_state['last_position_change'] = time.time()
        
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
        """Update aktivitas saat ini"""
        self.current_state['last_activity'] = self.current_state['activity']
        self.current_state['activity'] = activity
        
        self.timeline.append({
            'time': time.time(),
            'type': 'activity_change',
            'data': activity
        })
    
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
        
        # Hitung statistik
        total_interactions = len(recent_items)
        avg_response_time = 0  # TODO: hitung nanti
        
        # Dapatkan timeline terbaru
        recent_timeline = list(self.timeline)[-5:]
        
        return {
            'current_state': self.get_current_state(),
            'recent_interactions': total_interactions,
            'recent_timeline': recent_timeline,
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
            'ruang tamu': ['kamar', 'dapur', 'teras', 'kamar mandi'],
            'kamar': ['kamar mandi', 'ruang tamu'],
            'kamar mandi': ['kamar', 'ruang tamu'],
            'dapur': ['ruang tamu'],
            'teras': ['ruang tamu'],
            'pantai': ['mobil', 'kafe'],
            'mall': ['parkiran', 'mobil'],
            'mobil': ['pantai', 'mall', 'rumah'],
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
        valid_reasons = ['mandi', 'gerah', 'dingin', 'ganti baju', 'habis mandi']
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
        
        logger.debug(f"Forgot memories older than {self.expire_seconds}s")
    
    # =========================================================================
    # FORMATTING UNTUK PROMPT
    # =========================================================================
    
    def format_for_prompt(self) -> str:
        """Format working memory untuk dimasukkan ke prompt AI"""
        state = self.get_current_state()
        
        lines = [
            "📝 **WORKING MEMORY (5 menit terakhir)**",
            f"📍 Lokasi: {state['location'] or 'tidak diketahui'}",
            f"👕 Pakaian: {state['clothing'] or 'tidak diketahui'}",
            f"🧍 Posisi: {state['position'] or 'tidak diketahui'}",
            f"🎭 Mood: {state['mood']} (gairah: {state['arousal_level']}/10)",
            f"💕 Lagi intim: {'Ya' if state['is_intimate'] else 'Tidak'}",
            f"🕐 Waktu: {state['time_of_day']}",
            "",
            "**Timeline terakhir:**"
        ]
        
        for t in list(self.timeline)[-3:]:
            lines.append(f"• {t['data']}")
        
        return "\n".join(lines)


__all__ = ['WorkingMemory']
