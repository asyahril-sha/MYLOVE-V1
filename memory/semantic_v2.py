#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - SEMANTIC MEMORY V2
=============================================================================
Menyimpan fakta dan preferensi user seperti pengetahuan manusia
- Fakta-fakta tentang user (pekerjaan, hobi, makanan favorit)
- Preferensi seksual (posisi favorit, area sensitif)
- Kebiasaan dan rutinitas user
- Semua disimpan PERMANEN untuk 1 user
=============================================================================
"""

import time
import logging
import re
import random
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class FactCategory(str, Enum):
    """Kategori fakta tentang user"""
    IDENTITY = "identity"           # Nama, umur, dll
    OCCUPATION = "occupation"       # Pekerjaan
    HOBBY = "hobby"                 # Hobi
    FOOD = "food"                   # Makanan/minuman
    LIFESTYLE = "lifestyle"         # Gaya hidup
    PERSONALITY = "personality"      # Kepribadian
    RELATIONSHIP = "relationship"    # Status hubungan
    FAMILY = "family"                # Keluarga
    DREAM = "dream"                  # Mimpi/cita-cita
    FEAR = "fear"                    # Ketakutan
    LIKES = "likes"                  # Hal-hal yang disukai
    DISLIKES = "dislikes"            # Hal-hal yang tidak disukai
    HABIT = "habit"                  # Kebiasaan
    ROUTINE = "routine"               # Rutinitas harian


class PreferenceType(str, Enum):
    """Tipe preferensi"""
    POSITION = "position"            # Posisi seks favorit
    AREA = "area"                    # Area sensitif favorit
    ACTIVITY = "activity"            # Aktivitas favorit
    LOCATION = "location"             # Lokasi favorit
    FOREPLAY = "foreplay"             # Foreplay favorit
    AFTERCARE = "aftercare"           # Aftercare favorit
    ROLE = "role"                     # Role favorit
    CLOTHING = "clothing"             # Pakaian favorit


class SemanticMemoryV2:
    """
    Menyimpan fakta dan preferensi user seperti pengetahuan manusia
    - Semua data disimpan PERMANEN
    - Bisa diakses kapan saja untuk personalisasi
    - Belajar dari percakapan secara natural
    """
    
    def __init__(self):
        # Fakta-fakta tentang user
        self.facts = defaultdict(dict)  # {user_id: {category: {fact: value}}}
        
        # Preferensi user (dengan skor)
        self.preferences = defaultdict(lambda: defaultdict(dict))  # {user_id: {role: {type: {item: score}}}}
        
        # Kebiasaan dan rutinitas
        self.habits = defaultdict(list)  # {user_id: [(habit, timestamp)]}
        
        # Timeline perubahan fakta
        self.fact_history = defaultdict(list)  # {user_id: [(timestamp, category, old, new)]}
        
        # Confidence score untuk setiap fakta (0-1)
        self.confidence = defaultdict(lambda: defaultdict(float))  # {user_id: {fact_key: confidence}}
        
        # Keywords untuk ekstraksi fakta
        self.fact_patterns = self._init_fact_patterns()
        
        logger.info("✅ SemanticMemoryV2 initialized (PERMANENT storage for single user)")
    
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
    # EKSTRAKSI FAKTA DARI PERCAKAPAN
    # =========================================================================
    
    async def extract_facts(self, user_id: int, message: str, role: Optional[str] = None):
        """
        Ekstrak fakta dari pesan user secara otomatis
        
        Args:
            user_id: ID user
            message: Pesan user
            role: Role yang sedang aktif (untuk konteks)
        """
        message_lower = message.lower()
        
        for category, patterns in self.fact_patterns.items():
            for pattern, fact_type in patterns:
                match = re.search(pattern, message_lower)
                if match:
                    value = match.group(1) if match.groups() else match.group(0)
                    
                    # Simpan fakta dengan confidence awal
                    await self.add_fact(
                        user_id=user_id,
                        category=category,
                        fact_type=fact_type,
                        value=value,
                        confidence=0.7,  # Confidence sedang karena dari percakapan
                        source='conversation',
                        context={'role': role} if role else {}
                    )
                    
                    logger.debug(f"Extracted fact: {category.value}.{fact_type} = {value}")
    
    async def add_fact(self, 
                      user_id: int,
                      category: FactCategory,
                      fact_type: str,
                      value: Any,
                      confidence: float = 0.8,
                      source: str = 'manual',
                      context: Optional[Dict] = None):
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
        fact_key = f"{category.value}.{fact_type}"
        old_value = self.facts[user_id].get(fact_key)
        
        # Update fakta
        self.facts[user_id][fact_key] = {
            'value': value,
            'confidence': confidence,
            'updated_at': time.time(),
            'source': source,
            'context': context or {},
            'count': self.facts[user_id].get(fact_key, {}).get('count', 0) + 1
        }
        
        # Update confidence
        self.confidence[user_id][fact_key] = confidence
        
        # Catat perubahan
        if old_value and old_value.get('value') != value:
            self.fact_history[user_id].append({
                'timestamp': time.time(),
                'category': category,
                'fact_type': fact_type,
                'old_value': old_value.get('value'),
                'new_value': value,
                'confidence_change': confidence - old_value.get('confidence', 0)
            })
            
            logger.info(f"Fact updated for user {user_id}: {fact_key} = {value}")
        else:
            logger.debug(f"New fact for user {user_id}: {fact_key} = {value}")
    
    async def get_fact(self, user_id: int, category: FactCategory, fact_type: str) -> Optional[Any]:
        """
        Dapatkan fakta spesifik
        
        Args:
            user_id: ID user
            category: Kategori fakta
            fact_type: Tipe fakta
            
        Returns:
            Nilai fakta atau None
        """
        fact_key = f"{category.value}.{fact_type}"
        fact = self.facts[user_id].get(fact_key)
        
        if fact and fact.get('confidence', 0) > 0.3:  # Hanya kembalikan jika confidence cukup
            # Update access count
            fact['last_accessed'] = time.time()
            fact['access_count'] = fact.get('access_count', 0) + 1
            return fact['value']
        
        return None
    
    async def get_all_facts(self, user_id: int, min_confidence: float = 0.5) -> Dict:
        """
        Dapatkan semua fakta tentang user
        
        Args:
            user_id: ID user
            min_confidence: Minimal confidence
            
        Returns:
            Dictionary of facts
        """
        result = {}
        
        for fact_key, fact in self.facts[user_id].items():
            if fact.get('confidence', 0) >= min_confidence:
                result[fact_key] = fact['value']
        
        return result
    
    # =========================================================================
    # PREFERENSI USER
    # =========================================================================
    
    async def update_preference(self,
                               user_id: int,
                               role: str,
                               pref_type: PreferenceType,
                               item: str,
                               delta: float = 0.1,
                               context: Optional[Dict] = None):
        """
        Update preferensi user (naik/turun skor)
        
        Args:
            user_id: ID user
            role: Role terkait
            pref_type: Tipe preferensi
            item: Item (misal: 'doggy style')
            delta: Perubahan skor (+ suka, - tidak suka)
            context: Konteks (misal: climax = + lebih banyak)
        """
        current = self.preferences[user_id][role].get(pref_type.value, {}).get(item, 0.5)
        
        # Adjust berdasarkan konteks
        if context:
            if context.get('climax'):
                delta *= 1.5
            if context.get('intensity', 0) > 0.7:
                delta *= 1.2
        
        new_score = max(0.1, min(1.0, current + delta))
        
        # Simpan
        if pref_type.value not in self.preferences[user_id][role]:
            self.preferences[user_id][role][pref_type.value] = {}
        
        self.preferences[user_id][role][pref_type.value][item] = {
            'score': new_score,
            'count': self.preferences[user_id][role][pref_type.value].get(item, {}).get('count', 0) + 1,
            'last_updated': time.time(),
            'last_context': context
        }
        
        logger.debug(f"Preference updated: user {user_id} {role} {pref_type.value} {item} -> {new_score:.2f}")
    
    async def get_top_preferences(self,
                                 user_id: int,
                                 role: Optional[str],
                                 pref_type: PreferenceType,
                                 limit: int = 5) -> List[str]:
        """
        Dapatkan preferensi teratas
        
        Args:
            user_id: ID user
            role: Role (None untuk semua role)
            pref_type: Tipe preferensi
            limit: Jumlah maksimal
            
        Returns:
            List of items sorted by score
        """
        items = []
        
        if role:
            # Spesifik role
            if role in self.preferences[user_id]:
                prefs = self.preferences[user_id][role].get(pref_type.value, {})
                items = [(item, data['score']) for item, data in prefs.items()]
        else:
            # Semua role
            for r, prefs_by_type in self.preferences[user_id].items():
                prefs = prefs_by_type.get(pref_type.value, {})
                items.extend([(item, data['score']) for item, data in prefs.items()])
        
        # Sort by score
        items.sort(key=lambda x: x[1], reverse=True)
        
        return [item for item, _ in items[:limit]]
    
    # =========================================================================
    # KEBiasaan DAN RUTINITAS
    # =========================================================================
    
    async def record_habit(self, user_id: int, habit: str, context: Optional[Dict] = None):
        """
        Rekam kebiasaan user
        
        Args:
            user_id: ID user
            habit: Deskripsi kebiasaan
            context: Konteks (waktu, situasi)
        """
        self.habits[user_id].append({
            'habit': habit,
            'timestamp': time.time(),
            'context': context or {},
            'count': 1
        })
        
        # Keep last 100 habits
        if len(self.habits[user_id]) > 100:
            self.habits[user_id] = self.habits[user_id][-100:]
    
    async def get_common_habits(self, user_id: int, limit: int = 5) -> List[str]:
        """
        Dapatkan kebiasaan yang paling sering muncul
        
        Args:
            user_id: ID user
            limit: Jumlah maksimal
            
        Returns:
            List of common habits
        """
        from collections import Counter
        
        habit_counter = Counter()
        for h in self.habits[user_id]:
            habit_counter[h['habit']] += 1
        
        return [habit for habit, _ in habit_counter.most_common(limit)]
    
    # =========================================================================
    # PERSONALISASI RESPON
    # =========================================================================
    
    async def get_personalization_context(self, user_id: int, role: Optional[str] = None) -> Dict:
        """
        Dapatkan konteks personalisasi untuk prompt AI
        
        Args:
            user_id: ID user
            role: Role aktif
            
        Returns:
            Dictionary dengan fakta dan preferensi
        """
        context = {}
        
        # Fakta penting
        important_facts = [
            (FactCategory.IDENTITY, 'name'),
            (FactCategory.OCCUPATION, 'job'),
            (FactCategory.FOOD, 'food'),
            (FactCategory.HOBBY, 'hobby'),
            (FactCategory.LIFESTYLE, 'chronotype')
        ]
        
        facts_list = []
        for category, fact_type in important_facts:
            value = await self.get_fact(user_id, category, fact_type)
            if value:
                facts_list.append(f"{fact_type}: {value}")
        
        if facts_list:
            context['user_facts'] = facts_list
        
        # Preferensi untuk role ini
        if role:
            preferences = {}
            for pref_type in PreferenceType:
                top = await self.get_top_preferences(user_id, role, pref_type, limit=3)
                if top:
                    preferences[pref_type.value] = top
            
            if preferences:
                context['preferences'] = preferences
        
        # Kebiasaan umum
        habits = await self.get_common_habits(user_id, limit=3)
        if habits:
            context['common_habits'] = habits
        
        return context
    
    async def format_facts_for_prompt(self, user_id: int) -> str:
        """
        Format fakta untuk dimasukkan ke prompt AI
        
        Args:
            user_id: ID user
            
        Returns:
            String dengan fakta-fakta user
        """
        facts = await self.get_all_facts(user_id, min_confidence=0.6)
        
        if not facts:
            return ""
        
        lines = ["📌 **Yang aku tahu tentang kamu:**"]
        
        # Kelompokkan berdasarkan kategori
        categories = {}
        for fact_key, value in facts.items():
            cat, fact = fact_key.split('.')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(f"{fact.replace('_', ' ').title()}: {value}")
        
        for cat, items in categories.items():
            lines.append(f"• {cat.title()}:")
            for item in items[:3]:  # Max 3 per kategori
                lines.append(f"  - {item}")
        
        return "\n".join(lines)
    
    # =========================================================================
    # FORGETTING (PRIORITAS, BUKAN HAPUS)
    # =========================================================================
    
    async def adjust_confidence(self, user_id: int, fact_key: str, days_decay: float = 0.01):
        """
        Adjust confidence berdasarkan waktu (prioritas turun, bukan hapus)
        
        Args:
            user_id: ID user
            fact_key: Key fakta
            days_decay: Decay per hari
        """
        if user_id not in self.facts or fact_key not in self.facts[user_id]:
            return
        
        fact = self.facts[user_id][fact_key]
        last_accessed = fact.get('last_accessed', fact['updated_at'])
        days_old = (time.time() - last_accessed) / 86400
        
        # Turunkan confidence, tapi jangan sampai 0
        new_confidence = fact['confidence'] * (1 - (days_decay * days_old))
        fact['confidence'] = max(0.1, new_confidence)
        
        self.confidence[user_id][fact_key] = fact['confidence']
    
    # =========================================================================
    # STATISTIK
    # =========================================================================
    
    async def get_stats(self, user_id: int) -> Dict:
        """
        Dapatkan statistik semantic memory
        
        Args:
            user_id: ID user
            
        Returns:
            Dictionary statistik
        """
        total_facts = len(self.facts[user_id])
        avg_confidence = sum(f['confidence'] for f in self.facts[user_id].values()) / total_facts if total_facts > 0 else 0
        
        # Fakta per kategori
        by_category = {}
        for fact_key in self.facts[user_id]:
            cat = fact_key.split('.')[0]
            by_category[cat] = by_category.get(cat, 0) + 1
        
        # Preferensi
        total_preferences = sum(
            len(prefs)
            for role_data in self.preferences[user_id].values()
            for prefs in role_data.values()
        )
        
        # Habits
        total_habits = len(self.habits[user_id])
        
        return {
            'total_facts': total_facts,
            'avg_confidence': round(avg_confidence, 2),
            'facts_by_category': by_category,
            'total_preferences': total_preferences,
            'total_habits': total_habits,
            'memory_age_days': (time.time() - min(
                [f['updated_at'] for f in self.facts[user_id].values()] or [time.time()]
            )) / 86400
        }


__all__ = ['SemanticMemoryV2', 'FactCategory', 'PreferenceType']
