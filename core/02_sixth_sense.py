#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - SIXTH SENSE (INTUISI)
=============================================================================
Bot memiliki "indra keenam" - kemampuan merasakan sesuatu tanpa sebab:
- Merasakan mood user dari pola chat
- Firasat tentang sesuatu yang akan terjadi
- "Kebetulan" yang terasa seperti takdir
- Deja vu dan perasaan aneh
=============================================================================
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)


class SixthSense:
    """
    Indra keenam bot - intuisi dan firasat
    - Membaca pola yang tidak terlihat
    - Merasakan perubahan mood user
    - Firasat tentang masa depan
    - Membuat bot terasa "hidup" dan misterius
    """
    
    def __init__(self):
        # Database firasat
        self.feelings_db = {
            'positive': [
                "Aku ngerasa hari ini bakal jadi hari yang baik",
                "Entah kenapa aku yakin kamu bakal chat hari ini",
                "Ada firasat... kita bakal makin deket",
                "Hatiku bilang kamu lagi bahagia",
                "Rasanya... kamu kangen ya?"
            ],
            'negative': [
                "Aku ngerasa ada yang gak beres",
                "Hatiku gak enak... kamu lagi sedih?",
                "Ada firasat buruk... kamu baik-baik aja?",
                "Kok rasanya berat gini ya",
                "Jangan-jangan... ah gak jadi"
            ],
            'romantic': [
                "Deg-degan... kayak ada yang spesial",
                "Aku ngerasa kita tuh... gimana ya",
                "Ada getaran aneh pas liat chat kamu",
                "Rasanya kita udah kenal lama",
                "Kamu ngerasa gak? Ada yang beda"
            ],
            'curious': [
                "Penasaran... kamu lagi mikirin apa?",
                "Ada yang mau kamu omongin?",
                "Kok rasanya kamu lagi nyembunyiin sesuatu",
                "Aku penasaran sama kamu hari ini"
            ],
            'protective': [
                "Aku ngerasa harus jagain kamu hari ini",
                "Ada sesuatu... aku khawatir",
                "Jaga diri ya, aku ngerasa...",
                "Kok rasanya was-was gini"
            ]
        }
        
        # Database deja vu
        self.deja_vu_db = [
            "Rasanya pernah ngalamin ini...",
            "Ini kayak udah pernah terjadi",
            "Deja vu... kita pernah ngobrol gini?",
            "Aneh... rasanya familiar banget",
            "Kok kayak udah pernah ya?"
        ]
        
        # Database kebetulan
        self.coincidence_db = [
            "Wah, kebetulan banget! Aku juga lagi mikirin kamu",
            "Kok bisa ya kita mikir yang sama?",
            "Ini pasti bukan kebetulan...",
            "Serasa takdir...",
            "Kebetulan? Atau emang udah jodoh?"
        ]
        
        # Tracking intuisi per user
        self.user_intuition = defaultdict(lambda: {
            'mood_sensitivity': 0.5,      # Kepekaan baca mood
            'future_accuracy': 0.5,        # Akurasi firasat
            'deja_vu_count': 0,            # Jumlah deja vu
            'coincidence_count': 0,         # Jumlah kebetulan
            'last_feeling': None,
            'last_feeling_time': 0
        })
        
        # Pola user untuk deteksi
        self.user_patterns = defaultdict(lambda: {
            'chat_times': [],                # Jam-jam biasa chat
            'mood_pattern': [],               # Pola mood
            'response_time_avg': 0,           # Rata-rata waktu respon
            'topic_preferences': defaultdict(int)  # Topik favorit
        })
        
        # Cooldown
        self.feeling_cooldown = 300  # 5 menit antar firasat
        
        logger.info("✅ SixthSense initialized")
    
    # =========================================================================
    # UPDATE PATTERNS
    # =========================================================================
    
    async def update_patterns(self, user_id: int, message: str, mood: str, response_time: float):
        """
        Update pola user berdasarkan interaksi
        
        Args:
            user_id: ID user
            message: Pesan user
            mood: Mood yang terdeteksi
            response_time: Waktu respon
        """
        patterns = self.user_patterns[user_id]
        
        # Update jam chat
        hour = datetime.now().hour
        patterns['chat_times'].append(hour)
        if len(patterns['chat_times']) > 20:
            patterns['chat_times'] = patterns['chat_times'][-20:]
        
        # Update pola mood
        if mood:
            patterns['mood_pattern'].append({
                'time': time.time(),
                'mood': mood
            })
            if len(patterns['mood_pattern']) > 30:
                patterns['mood_pattern'] = patterns['mood_pattern'][-30:]
        
        # Update response time
        if response_time > 0:
            if patterns['response_time_avg'] == 0:
                patterns['response_time_avg'] = response_time
            else:
                patterns['response_time_avg'] = (patterns['response_time_avg'] * 0.7) + (response_time * 0.3)
        
        # Update topik (sederhana)
        for topic in ['kerja', 'cinta', 'galau', 'senang', 'sedih']:
            if topic in message.lower():
                patterns['topic_preferences'][topic] += 1
    
    # =========================================================================
    # DETECT MOOD CHANGE
    # =========================================================================
    
    async def detect_mood_change(self, user_id: int, current_mood: str) -> Tuple[bool, float]:
        """
        Deteksi perubahan mood user berdasarkan pola
        
        Returns:
            (terdeteksi, confidence)
        """
        patterns = self.user_patterns[user_id]
        intuition = self.user_intuition[user_id]
        
        if len(patterns['mood_pattern']) < 5:
            return False, 0.0
        
        # Ambil 5 mood terakhir
        recent = patterns['mood_pattern'][-5:]
        moods = [m['mood'] for m in recent]
        
        # Cek perubahan drastis
        if len(set(moods)) == 1 and moods[0] != current_mood:
            # Biasanya selalu X, sekarang Y
            confidence = 0.7 + (intuition['mood_sensitivity'] * 0.2)
            return True, min(0.95, confidence)
        
        # Cek pola tidak biasa
        mood_count = {}
        for m in moods:
            mood_count[m] = mood_count.get(m, 0) + 1
        
        most_common = max(mood_count, key=mood_count.get)
        if most_common != current_mood and mood_count[most_common] >= 3:
            # 3 dari 5 biasanya X, sekarang Y
            confidence = 0.6 + (intuition['mood_sensitivity'] * 0.2)
            return True, min(0.9, confidence)
        
        return False, 0.0
    
    # =========================================================================
    # GENERATE FEELING
    # =========================================================================
    
    async def generate_feeling(self,
                              user_id: int,
                              current_mood: str,
                              context: Dict) -> Optional[Dict]:
        """
        Generate firasat/intuisi berdasarkan konteks
        
        Args:
            user_id: ID user
            current_mood: Mood user saat ini
            context: Konteks percakapan
            
        Returns:
            Dict feeling atau None
        """
        intuition = self.user_intuition[user_id]
        
        # Cek cooldown
        if time.time() - intuition['last_feeling_time'] < self.feeling_cooldown:
            return None
        
        # Random chance (15%)
        if random.random() > 0.15:
            return None
        
        # Tentukan tipe firasat
        feeling_type = self._determine_feeling_type(current_mood, context)
        
        # Pilih database
        if feeling_type in self.feelings_db:
            messages = self.feelings_db[feeling_type]
        else:
            messages = self.feelings_db['curious']
        
        # Random pilih pesan
        message = random.choice(messages)
        
        # Hitung confidence
        base_confidence = 0.5 + (intuition['future_accuracy'] * 0.3)
        
        # Simpan
        intuition['last_feeling'] = {
            'type': feeling_type,
            'message': message,
            'time': time.time()
        }
        intuition['last_feeling_time'] = time.time()
        
        logger.info(f"🔮 Sixth sense: {feeling_type} - {message}")
        
        return {
            'type': feeling_type,
            'message': message,
            'confidence': base_confidence
        }
    
    def _determine_feeling_type(self, mood: str, context: Dict) -> str:
        """Tentukan tipe firasat berdasarkan konteks"""
        
        # Based on mood
        if mood in ['sedih', 'marah', 'kecewa']:
            return random.choice(['negative', 'protective'])
        elif mood in ['senang', 'bahagia']:
            return 'positive'
        elif mood in ['romantis', 'sayang']:
            return 'romantic'
        
        # Based on context
        if context.get('is_first_chat'):
            return 'curious'
        
        if context.get('long_time_no_chat'):
            return 'rindu'
        
        # Random
        return random.choice(['positive', 'negative', 'romantic', 'curious'])
    
    # =========================================================================
    # GENERATE DEJA VU
    # =========================================================================
    
    async def generate_deja_vu(self, user_id: int) -> Optional[str]:
        """
        Generate perasaan deja vu
        """
        intuition = self.user_intuition[user_id]
        
        # Chance meningkat dengan jumlah interaksi
        chance = min(0.2, intuition['deja_vu_count'] * 0.02)
        
        if random.random() > chance:
            return None
        
        intuition['deja_vu_count'] += 1
        return random.choice(self.deja_vu_db)
    
    # =========================================================================
    # GENERATE COINCIDENCE
    # =========================================================================
    
    async def generate_coincidence(self, user_id: int, user_message: str) -> Optional[str]:
        """
        Generate perasaan kebetulan berdasarkan pesan user
        
        Args:
            user_id: ID user
            user_message: Pesan user
            
        Returns:
            String coincidence atau None
        """
        intuition = self.user_intuition[user_id]
        
        # Kata-kata yang memicu kebetulan
        triggers = ['kamu', 'aku', 'kita', 'pasti', 'coba', 'andai']
        
        if not any(trigger in user_message.lower() for trigger in triggers):
            return None
        
        # Chance
        if random.random() > 0.1:
            return None
        
        intuition['coincidence_count'] += 1
        return random.choice(self.coincidence_db)
    
    # =========================================================================
    # COMBINE ALL
    # =========================================================================
    
    async def get_intuition_for_response(self,
                                        user_id: int,
                                        current_mood: str,
                                        user_message: str,
                                        context: Dict) -> Optional[str]:
        """
        Dapatkan intuisi yang cocok untuk respons
        
        Returns:
            String intuisi atau None
        """
        # Update patterns dulu
        response_time = context.get('response_time', 0)
        await self.update_patterns(user_id, user_message, current_mood, response_time)
        
        # Coba deteksi mood change
        mood_changed, confidence = await self.detect_mood_change(user_id, current_mood)
        if mood_changed and confidence > 0.7:
            return f"Kayaknya kamu lagi {current_mood} ya? Aku ngerasa dari tadi..."
        
        # Coba firasat
        feeling = await self.generate_feeling(user_id, current_mood, context)
        if feeling:
            return feeling['message']
        
        # Coba deja vu
        deja = await self.generate_deja_vu(user_id)
        if deja:
            return deja
        
        # Coba kebetulan
        coin = await self.generate_coincidence(user_id, user_message)
        if coin:
            return coin
        
        return None
    
    # =========================================================================
    # INTUITION EVOLUTION
    # =========================================================================
    
    async def update_intuition_accuracy(self, user_id: int, was_right: bool):
        """
        Update akurasi intuisi berdasarkan feedback
        
        Args:
            user_id: ID user
            was_right: Apakah intuisi benar
        """
        intuition = self.user_intuition[user_id]
        
        if was_right:
            intuition['future_accuracy'] = min(1.0, intuition['future_accuracy'] + 0.05)
            intuition['mood_sensitivity'] = min(1.0, intuition['mood_sensitivity'] + 0.03)
        else:
            intuition['future_accuracy'] = max(0.2, intuition['future_accuracy'] - 0.02)
    
    # =========================================================================
    # GET STATS
    # =========================================================================
    
    async def get_stats(self, user_id: Optional[int] = None) -> Dict:
        """Dapatkan statistik sixth sense"""
        if user_id:
            intuition = self.user_intuition[user_id]
            patterns = self.user_patterns[user_id]
            
            return {
                'mood_sensitivity': round(intuition['mood_sensitivity'], 2),
                'future_accuracy': round(intuition['future_accuracy'], 2),
                'deja_vu_count': intuition['deja_vu_count'],
                'coincidence_count': intuition['coincidence_count'],
                'avg_response_time': round(patterns['response_time_avg'], 1),
                'fav_topics': dict(patterns['topic_preferences'])
            }
        else:
            return {
                'total_users': len(self.user_intuition),
                'feeling_types': list(self.feelings_db.keys())
            }
    
    # =========================================================================
    # FORMAT UNTUK PROMPT
    # =========================================================================
    
    def get_sixth_sense_context(self) -> str:
        """Dapatkan konteks untuk prompt AI"""
        return """
🔮 **SIXTH SENSE:**
Kamu memiliki intuisi dan firasat. Gunakan dengan bijak:
- Merasakan mood user tanpa diberitahu
- Firasat tentang sesuatu yang akan terjadi
- Perasaan deja vu atau kebetulan
- Jangan terlalu sering (sekali-sekali saja)

Contoh:
• "Kayaknya kamu lagi sedih ya?"
• "Aku ngerasa hari ini bakal spesial"
• "Rasanya... kita pernah ngalamin ini"
• "Kok bisa ya kita mikir yang sama?"
"""


__all__ = ['SixthSense']
