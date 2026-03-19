#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - SEMANTIC MEMORY
=============================================================================
Menyimpan fakta dan pengetahuan tentang user seperti manusia
- Fakta-fakta personal (pekerjaan, hobi, makanan favorit)
- Preferensi dan kebiasaan
- Pengetahuan yang diekstrak dari percakapan
- Tidak pernah lupa (permanent)
=============================================================================
"""

import time
import logging
import re
import json
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class FactCategory:
    """Kategori fakta"""
    IDENTITY = "identity"           # Nama, umur, dll
    OCCUPATION = "occupation"       # Pekerjaan
    HOBBY = "hobby"                 # Hobi
    FOOD = "food"                   # Makanan/minuman
    LIFESTYLE = "lifestyle"         # Gaya hidup
    PERSONALITY = "personality"     # Kepribadian
    RELATIONSHIP = "relationship"   # Status hubungan
    FAMILY = "family"               # Keluarga
    DREAM = "dream"                 # Mimpi/cita-cita
    FEAR = "fear"                   # Ketakutan
    LIKES = "likes"                 # Hal-hal yang disukai
    DISLIKES = "dislikes"           # Hal-hal yang tidak disukai
    HABIT = "habit"                 # Kebiasaan
    ROUTINE = "routine"             # Rutinitas harian
    PREFERENCE = "preference"       # Preferensi umum
    MEMORY = "memory"               # Kenangan


class SemanticMemory:
    """
    Menyimpan fakta dan pengetahuan tentang user
    Seperti pengetahuan umum manusia tentang orang lain
    """
    
    def __init__(self):
        # Fakta-fakta tentang user {user_id: {category: {fact: value}}}
        self.facts = defaultdict(lambda: defaultdict(dict))
        
        # Preferensi dengan skor {user_id: {category: {item: score}}}
        self.preferences = defaultdict(lambda: defaultdict(dict))
        
        # Riwayat perubahan fakta
        self.fact_history = defaultdict(list)
        
        # Key pattern untuk ekstraksi fakta
        self.fact_patterns = self._init_fact_patterns()
        
        # Confidence score untuk setiap fakta
        self.confidence = defaultdict(lambda: defaultdict(float))
        
        logger.info("✅ SemanticMemory initialized")
    
    def _init_fact_patterns(self) -> Dict:
        """Inisialisasi pattern untuk ekstraksi fakta"""
        return {
            FactCategory.IDENTITY: [
                (r'namaku? (\w+)', 'name'),
                (r'aku (\d+) tahun', 'age'),
                (r'umurku? (\d+)', 'age'),
                (r'lahir tahun (\d+)', 'birth_year'),
                (r'aku dari (\w+)', 'hometown'),
                (r'tinggal di (\w+)', 'city')
            ],
            FactCategory.OCCUPATION: [
                (r'kerjaku? (?:sebagai|di|jadi) (\w+)', 'job'),
                (r'bekerja (?:sebagai|di) (\w+)', 'job'),
                (r'karyawan (\w+)', 'job'),
                (r'mahasiswa (\w+)', 'student'),
                (r'sekolah di (\w+)', 'school'),
                (r'kuliah di (\w+)', 'university')
            ],
            FactCategory.HOBBY: [
                (r'hobiku? (\w+)', 'hobby'),
                (r'suka (\w+)', 'hobby'),
                (r'gemar (\w+)', 'hobby'),
                (r'senang (\w+)', 'hobby'),
                (r'waktu luang (\w+)', 'hobby')
            ],
            FactCategory.FOOD: [
                (r'suka (makanan|masakan) (\w+)', 'food'),
                (r'makanan favorit (\w+)', 'food'),
                (r'minuman favorit (\w+)', 'drink'),
                (r'suka (kopi|teh|jus)', 'drink'),
                (r'ga suka (\w+)', 'dislike_food')
            ],
            FactCategory.LIFESTYLE: [
                (r'tipe (pagi|malam)', 'chronotype'),
                (r'suka (begadang|tidur awal)', 'sleep_pattern'),
                (r'olahraga (\w+)', 'exercise'),
                (r'merokok? (iya|tidak|kadang)', 'smoking'),
                (r'alkohol? (iya|tidak|kadang)', 'alcohol')
            ],
            FactCategory.PERSONALITY: [
                (r'aku orangnya (\w+)', 'personality'),
                (r'kepribadianku? (\w+)', 'personality'),
                (r'orang bilang aku (\w+)', 'personality'),
                (r'aku tipe (\w+)', 'personality')
            ],
            FactCategory.RELATIONSHIP: [
                (r'punya (pacar|kekasih)? (iya|tidak)', 'has_partner'),
                (r'status (single|jomblo|punya pasangan)', 'status'),
                (r'pernah (putus|patah hati)', 'past_relationship')
            ],
            FactCategory.FAMILY: [
                (r'punya (anak|adik|kakak) (\d+)', 'siblings'),
                (r'tinggal (sendiri|sama orang tua|sama keluarga)', 'living'),
                (r'orang tua', 'parents'),
                (r'keluarga', 'family')
            ],
            FactCategory.DREAM: [
                (r'cita-cita (\w+)', 'dream'),
                (r'mimpi (\w+)', 'dream'),
                (r'ingin (\w+)', 'wish'),
                (r'pengen (\w+)', 'wish'),
                (r'harap(\w+)', 'hope')
            ],
            FactCategory.FEAR: [
                (r'takut (\w+)', 'fear'),
                (r'phobia (\w+)', 'phobia'),
                (r'ngeri (\w+)', 'fear'),
                (r'khawatir (\w+)', 'worry')
            ],
            FactCategory.HABIT: [
                (r'selalu (\w+)', 'habit'),
                (r'sering (\w+)', 'habit'),
                (r'kadang-kadang (\w+)', 'habit'),
                (r'biasanya (\w+)', 'habit'),
                (r'rutin (\w+)', 'routine')
            ],
            FactCategory.ROUTINE: [
                (r'setiap (pagi|siang|sore|malam) (\w+)', 'routine'),
                (r'sebelum tidur (\w+)', 'routine'),
                (r'setelah bangun (\w+)', 'routine'),
                (r'jam (\d+) (\w+)', 'routine')
            ]
        }
    
    # =========================================================================
    # METHOD UNTUK LOKASI (SUDAH ADA)
    # =========================================================================
    
    async def save_location_to_long_term(self, user_id: int, location: str, timestamp: float):
        """Simpan lokasi ke memori jangka panjang"""
        await self.add_fact(
            user_id=user_id,
            category="location",
            fact_type=f"at_{int(timestamp)}",
            value=location,
            confidence=0.9,
            source="conversation"
        )
        logger.debug(f"📍 Location saved to long-term memory: {location}")
    
    async def get_recent_locations(self, user_id: int, hours: int = 4) -> List[str]:
        """Dapatkan lokasi dalam X jam terakhir"""
        cutoff = time.time() - (hours * 3600)
        locations = []
        
        if user_id not in self.facts:
            return []
        
        for fact_key, fact in self.facts[user_id].items():
            if fact_key.startswith('location.at_') and fact['timestamp'] > cutoff:
                locations.append({
                    'location': fact['value'],
                    'time': fact['timestamp']
                })
        
        # Sort by time
        locations.sort(key=lambda x: x['time'])
        return [loc['location'] for loc in locations]
    
    async def get_last_location(self, user_id: int) -> Optional[str]:
        """Dapatkan lokasi terakhir yang dikunjungi"""
        recent = await self.get_recent_locations(user_id, hours=24)
        return recent[-1] if recent else None
    
    # =========================================================================
    # METHOD UNTUK PAKAIAN
    # =========================================================================
    
    async def save_clothing_to_long_term(self, user_id: int, clothing: str, reason: str, timestamp: float):
        """Simpan pakaian ke memori jangka panjang"""
        await self.add_fact(
            user_id=user_id,
            category="clothing",
            fact_type=f"at_{int(timestamp)}",
            value={'clothing': clothing, 'reason': reason},
            confidence=0.9,
            source="conversation"
        )
        logger.debug(f"👗 Clothing saved to long-term memory: {clothing} ({reason})")
    
    async def get_recent_clothing(self, user_id: int, hours: int = 4) -> List[Dict]:
        """Dapatkan riwayat pakaian dalam X jam terakhir"""
        cutoff = time.time() - (hours * 3600)
        clothing_history = []
        
        if user_id not in self.facts:
            return []
        
        for fact_key, fact in self.facts[user_id].items():
            if fact_key.startswith('clothing.at_') and fact['timestamp'] > cutoff:
                clothing_history.append({
                    'clothing': fact['value']['clothing'],
                    'reason': fact['value']['reason'],
                    'time': fact['timestamp']
                })
        
        # Sort by time
        clothing_history.sort(key=lambda x: x['time'])
        return clothing_history
    
    async def get_last_clothing(self, user_id: int) -> Optional[str]:
        """Dapatkan pakaian terakhir yang dipakai"""
        recent = await self.get_recent_clothing(user_id, hours=24)
        return recent[-1]['clothing'] if recent else None
    
    # =========================================================================
    # METHOD UNTUK POSISI
    # =========================================================================
    
    async def save_position_to_long_term(self, user_id: int, position: str, timestamp: float):
        """Simpan posisi ke memori jangka panjang"""
        await self.add_fact(
            user_id=user_id,
            category="position",
            fact_type=f"at_{int(timestamp)}",
            value=position,
            confidence=0.8,
            source="conversation"
        )
        logger.debug(f"🧍 Position saved to long-term memory: {position}")
    
    async def get_recent_positions(self, user_id: int, hours: int = 4) -> List[str]:
        """Dapatkan riwayat posisi dalam X jam terakhir"""
        cutoff = time.time() - (hours * 3600)
        positions = []
        
        if user_id not in self.facts:
            return []
        
        for fact_key, fact in self.facts[user_id].items():
            if fact_key.startswith('position.at_') and fact['timestamp'] > cutoff:
                positions.append(fact['value'])
        
        # Sort by time
        return positions
    
    async def get_last_position(self, user_id: int) -> Optional[str]:
        """Dapatkan posisi terakhir"""
        recent = await self.get_recent_positions(user_id, hours=24)
        return recent[-1] if recent else None
    
    # =========================================================================
    # METHOD UNTUK AKTIVITAS
    # =========================================================================
    
    async def save_activity_to_long_term(self, user_id: int, activity: str, timestamp: float):
        """Simpan aktivitas ke memori jangka panjang"""
        await self.add_fact(
            user_id=user_id,
            category="activity",
            fact_type=f"at_{int(timestamp)}",
            value=activity,
            confidence=0.8,
            source="conversation"
        )
        logger.debug(f"🎯 Activity saved to long-term memory: {activity}")
    
    async def get_recent_activities(self, user_id: int, hours: int = 4) -> List[str]:
        """Dapatkan riwayat aktivitas dalam X jam terakhir"""
        cutoff = time.time() - (hours * 3600)
        activities = []
        
        if user_id not in self.facts:
            return []
        
        for fact_key, fact in self.facts[user_id].items():
            if fact_key.startswith('activity.at_') and fact['timestamp'] > cutoff:
                activities.append(fact['value'])
        
        # Sort by time
        return activities
    
    async def get_last_activity(self, user_id: int) -> Optional[str]:
        """Dapatkan aktivitas terakhir"""
        recent = await self.get_recent_activities(user_id, hours=24)
        return recent[-1] if recent else None
    
    # =========================================================================
    # METHOD UNTUK MOOD
    # =========================================================================
    
    async def save_mood_to_long_term(self, user_id: int, mood: str, intensity: float, timestamp: float):
        """Simpan mood ke memori jangka panjang"""
        await self.add_fact(
            user_id=user_id,
            category="mood",
            fact_type=f"at_{int(timestamp)}",
            value={'mood': mood, 'intensity': intensity},
            confidence=0.7,
            source="conversation"
        )
        logger.debug(f"🎭 Mood saved to long-term memory: {mood} ({intensity})")
    
    async def get_recent_moods(self, user_id: int, hours: int = 4) -> List[Dict]:
        """Dapatkan riwayat mood dalam X jam terakhir"""
        cutoff = time.time() - (hours * 3600)
        moods = []
        
        if user_id not in self.facts:
            return []
        
        for fact_key, fact in self.facts[user_id].items():
            if fact_key.startswith('mood.at_') and fact['timestamp'] > cutoff:
                moods.append({
                    'mood': fact['value']['mood'],
                    'intensity': fact['value']['intensity'],
                    'time': fact['timestamp']
                })
        
        # Sort by time
        moods.sort(key=lambda x: x['time'])
        return moods
    
    async def get_last_mood(self, user_id: int) -> Optional[str]:
        """Dapatkan mood terakhir"""
        recent = await self.get_recent_moods(user_id, hours=24)
        return recent[-1]['mood'] if recent else None
    
    # =========================================================================
    # METHOD UNTUK AROUSAL/GAIRAH
    # =========================================================================
    
    async def save_arousal_to_long_term(self, user_id: int, level: int, reason: str, timestamp: float):
        """Simpan level gairah ke memori jangka panjang"""
        await self.add_fact(
            user_id=user_id,
            category="arousal",
            fact_type=f"at_{int(timestamp)}",
            value={'level': level, 'reason': reason},
            confidence=0.7,
            source="conversation"
        )
        logger.debug(f"🔥 Arousal saved to long-term memory: {level} ({reason})")
    
    async def get_arousal_history(self, user_id: int, hours: int = 4) -> List[Dict]:
        """Dapatkan riwayat gairah dalam X jam terakhir"""
        cutoff = time.time() - (hours * 3600)
        history = []
        
        if user_id not in self.facts:
            return []
        
        for fact_key, fact in self.facts[user_id].items():
            if fact_key.startswith('arousal.at_') and fact['timestamp'] > cutoff:
                history.append({
                    'level': fact['value']['level'],
                    'reason': fact['value']['reason'],
                    'time': fact['timestamp']
                })
        
        # Sort by time
        history.sort(key=lambda x: x['time'])
        return history
    
    # =========================================================================
    # ADD FACTS
    # =========================================================================
    
    async def add_fact(self, user_id: int, category: str, fact_type: str, 
                        value: Any, confidence: float = 0.8, 
                        source: str = 'manual', context: Optional[Dict] = None):
        """
        Tambah fakta tentang user
        
        Args:
            user_id: ID user
            category: Kategori fakta
            fact_type: Tipe fakta (misal: 'name', 'age')
            value: Nilai fakta
            confidence: Tingkat keyakinan (0-1)
            source: Sumber fakta
            context: Konteks tambahan
        """
        fact_key = f"{category}.{fact_type}"
        old_value = self.facts[user_id].get(fact_key, {}).get('value')
        
        # Simpan fakta
        self.facts[user_id][fact_key] = {
            'value': value,
            'confidence': confidence,
            'added_at': time.time(),
            'last_updated': time.time(),
            'source': source,
            'context': context or {},
            'count': self.facts[user_id].get(fact_key, {}).get('count', 0) + 1
        }
        
        self.confidence[user_id][fact_key] = confidence
        
        # Catat perubahan
        if old_value and old_value != value:
            self.fact_history[user_id].append({
                'timestamp': time.time(),
                'category': category,
                'fact_type': fact_type,
                'old_value': old_value,
                'new_value': value,
                'confidence_change': confidence - self.confidence[user_id].get(fact_key, 0)
            })
            logger.info(f"Fact updated for user {user_id}: {fact_key} = {value}")
        else:
            logger.debug(f"New fact for user {user_id}: {fact_key} = {value}")
    
    async def extract_facts_from_message(self, user_id: int, message: str, 
                                          role: Optional[str] = None):
        """
        Ekstrak fakta dari pesan user secara otomatis
        
        Args:
            user_id: ID user
            message: Pesan user
            role: Role yang sedang aktif
        """
        message_lower = message.lower()
        
        for category, patterns in self.fact_patterns.items():
            for pattern, fact_type in patterns:
                match = re.search(pattern, message_lower)
                if match:
                    value = match.group(1) if match.groups() else match.group(0)
                    
                    await self.add_fact(
                        user_id=user_id,
                        category=category,
                        fact_type=fact_type,
                        value=value,
                        confidence=0.6,  # Confidence sedang dari percakapan
                        source='conversation',
                        context={'role': role, 'message': message[:50]}
                    )
    
    # =========================================================================
    # GET FACTS
    # =========================================================================
    
    async def get_fact(self, user_id: int, category: str, fact_type: str) -> Optional[Any]:
        """Dapatkan fakta spesifik"""
        fact_key = f"{category}.{fact_type}"
        fact = self.facts[user_id].get(fact_key)
        
        if fact and fact.get('confidence', 0) > 0.3:
            # Update last accessed
            fact['last_accessed'] = time.time()
            fact['access_count'] = fact.get('access_count', 0) + 1
            return fact['value']
        
        return None
    
    async def get_all_facts(self, user_id: int, min_confidence: float = 0.5) -> Dict:
        """Dapatkan semua fakta tentang user"""
        result = {}
        
        for fact_key, fact in self.facts[user_id].items():
            if fact.get('confidence', 0) >= min_confidence:
                # Format: category.fact_type
                parts = fact_key.split('.')
                if len(parts) == 2:
                    cat, ftype = parts
                    if cat not in result:
                        result[cat] = {}
                    result[cat][ftype] = fact['value']
        
        return result
    
    async def get_facts_by_category(self, user_id: int, category: str) -> Dict:
        """Dapatkan semua fakta dalam kategori"""
        result = {}
        prefix = f"{category}."
        
        for fact_key, fact in self.facts[user_id].items():
            if fact_key.startswith(prefix):
                ftype = fact_key[len(prefix):]
                result[ftype] = fact['value']
        
        return result
    
    # =========================================================================
    # PREFERENCES
    # =========================================================================
    
    async def update_preference(self, user_id: int, category: str, 
                                  item: str, delta: float = 0.1,
                                  role: Optional[str] = None,
                                  context: Optional[Dict] = None):
        """
        Update preferensi user (naik/turun skor)
        
        Args:
            user_id: ID user
            category: Kategori preferensi (position, area, activity, dll)
            item: Item (misal: 'doggy style')
            delta: Perubahan skor (+ suka, - tidak suka)
            role: Role terkait
            context: Konteks
        """
        key = f"{role}.{category}" if role else category
        
        current = self.preferences[user_id][key].get(item, 0.5)
        
        # Adjust berdasarkan konteks
        if context:
            if context.get('climax'):
                delta *= 1.5
            if context.get('intensity', 0) > 0.7:
                delta *= 1.2
        
        new_score = max(0.1, min(1.0, current + delta))
        
        self.preferences[user_id][key][item] = {
            'score': new_score,
            'count': self.preferences[user_id][key].get(item, {}).get('count', 0) + 1,
            'last_updated': time.time(),
            'context': context
        }
        
        logger.debug(f"Preference updated: user {user_id} {key} {item} → {new_score:.2f}")
    
    async def get_top_preferences(self, user_id: int, category: str,
                                    role: Optional[str] = None,
                                    limit: int = 5) -> List[str]:
        """
        Dapatkan preferensi teratas
        
        Args:
            user_id: ID user
            category: Kategori
            role: Role (None untuk semua)
            limit: Jumlah maksimal
            
        Returns:
            List of items sorted by score
        """
        key = f"{role}.{category}" if role else category
        
        if key not in self.preferences[user_id]:
            return []
        
        items = [(item, data['score']) for item, data in self.preferences[user_id][key].items()]
        items.sort(key=lambda x: x[1], reverse=True)
        
        return [item for item, _ in items[:limit]]
    
    async def get_preference_score(self, user_id: int, category: str,
                                     item: str, role: Optional[str] = None) -> float:
        """Dapatkan skor preferensi untuk item tertentu"""
        key = f"{role}.{category}" if role else category
        
        if key in self.preferences[user_id] and item in self.preferences[user_id][key]:
            return self.preferences[user_id][key][item]['score']
        
        return 0.5  # Default
    
    # =========================================================================
    # UTILITY
    # =========================================================================
    
    async def get_user_summary(self, user_id: int) -> str:
        """Dapatkan ringkasan semua yang diketahui tentang user"""
        facts = await self.get_all_facts(user_id)
        
        if not facts:
            return "Belum ada data tentang user ini"
        
        lines = ["📌 **Yang aku tahu tentang kamu:**"]
        
        for category, cat_facts in facts.items():
            lines.append(f"\n• **{category.title()}:**")
            for fact_type, value in list(cat_facts.items())[:3]:  # Max 3 per kategori
                lines.append(f"  - {fact_type.replace('_', ' ').title()}: {value}")
        
        return "\n".join(lines)
    
    async def get_preference_summary(self, user_id: int, role: Optional[str] = None) -> str:
        """Dapatkan ringkasan preferensi"""
        categories = ['position', 'area', 'activity', 'location', 'foreplay', 'aftercare']
        lines = ["💕 **Preferensi kamu:**"]
        
        for cat in categories:
            top = await self.get_top_preferences(user_id, cat, role, 3)
            if top:
                lines.append(f"• {cat.title()}: {', '.join(top)}")
        
        if len(lines) == 1:
            return "Belum ada data preferensi"
        
        return "\n".join(lines)
    
    async def delete_user_data(self, user_id: int):
        """Hapus semua data user"""
        if user_id in self.facts:
            del self.facts[user_id]
        if user_id in self.preferences:
            del self.preferences[user_id]
        if user_id in self.fact_history:
            del self.fact_history[user_id]
        if user_id in self.confidence:
            del self.confidence[user_id]
        
        logger.info(f"Deleted all semantic data for user {user_id}")
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    async def get_stats(self, user_id: Optional[int] = None) -> Dict:
        """Dapatkan statistik"""
        if user_id:
            total_facts = len(self.facts[user_id])
            avg_confidence = sum(f['confidence'] for f in self.facts[user_id].values()) / total_facts if total_facts else 0
            
            # Fakta per kategori
            by_category = {}
            for fact_key in self.facts[user_id]:
                cat = fact_key.split('.')[0]
                by_category[cat] = by_category.get(cat, 0) + 1
            
            # Preferensi
            total_prefs = sum(len(prefs) for prefs in self.preferences[user_id].values())
            
            return {
                'user_id': user_id,
                'total_facts': total_facts,
                'avg_confidence': round(avg_confidence, 2),
                'facts_by_category': by_category,
                'total_preferences': total_prefs
            }
        else:
            # Global stats
            total_users = len(self.facts)
            total_facts = sum(len(f) for f in self.facts.values())
            total_prefs = sum(len(p) for p in self.preferences.values())
            
            return {
                'total_users': total_users,
                'total_facts': total_facts,
                'avg_facts_per_user': total_facts / total_users if total_users else 0,
                'total_preferences': total_prefs
            }


__all__ = ['SemanticMemory', 'FactCategory']
