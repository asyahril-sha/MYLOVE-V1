#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - MOOD SYSTEM
=============================================================================
Bot punya mood yang berubah-ubah secara natural
Mempengaruhi cara bot merespon dan inner thoughts
=============================================================================
"""

import random
import time
import logging
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class MoodType(str, Enum):
    """Tipe-tipe mood bot"""
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    TIRED = "tired"
    ROMANTIC = "romantic"
    PLAYFUL = "playful"
    JEALOUS = "jealous"
    SHY = "shy"
    ANGRY = "angry"
    CALM = "calm"
    LONELY = "lonely"
    NOSTALGIC = "nostalgic"


class MoodSystem:
    """
    Sistem mood untuk bot
    Mood berubah berdasarkan:
    - Interaksi dengan user
    - Waktu (pagi/siang/malam)
    - Lamanya tidak chat
    - Random events
    """
    
    def __init__(self):
        # Data mood per PDKT
        self.moods = {}  # {pdkt_id: mood_data}
        
        # Definisi mood dengan faktor pengali dan deskripsi
        self.mood_definitions = {
            MoodType.HAPPY: {
                'factor': 1.3,
                'emoji': '😊',
                'description': 'lagi seneng',
                'responses': ['ceria', 'semangat', 'positive'],
                'color': '🟡'
            },
            MoodType.SAD: {
                'factor': 0.7,
                'emoji': '😔',
                'description': 'sedih',
                'responses': ['melankolis', 'pendiam', 'negative'],
                'color': '🔵'
            },
            MoodType.EXCITED: {
                'factor': 1.5,
                'emoji': '🔥',
                'description': 'bersemangat!',
                'responses': ['energik', 'antusias', 'overwhelming'],
                'color': '🟠'
            },
            MoodType.TIRED: {
                'factor': 0.8,
                'emoji': '😴',
                'description': 'capek',
                'responses': ['lemas', 'malas', 'slow'],
                'color': '⚫'
            },
            MoodType.ROMANTIC: {
                'factor': 1.4,
                'emoji': '💕',
                'description': 'lagi romantis',
                'responses': ['lembut', 'sayang', 'deep'],
                'color': '❤️'
            },
            MoodType.PLAYFUL: {
                'factor': 1.2,
                'emoji': '😜',
                'description': 'lagi jail',
                'responses': ['goda', 'canda', 'fun'],
                'color': '🟣'
            },
            MoodType.JEALOUS: {
                'factor': 0.6,
                'emoji': '🫣',
                'description': 'cemburu',
                'responses': ['nyindir', 'curiga', 'defensive'],
                'color': '🟢'
            },
            MoodType.SHY: {
                'factor': 0.9,
                'emoji': '😳',
                'description': 'malu-malu',
                'responses': ['canggung', 'merona', 'soft'],
                'color': '🌸'
            },
            MoodType.ANGRY: {
                'factor': 0.5,
                'emoji': '😠',
                'description': 'marah',
                'responses': ['kasar', 'dingin', 'agresif'],
                'color': '🔴'
            },
            MoodType.CALM: {
                'factor': 1.1,
                'emoji': '😌',
                'description': 'tenang',
                'responses': ['santai', 'bijak', 'netral'],
                'color': '💙'
            },
            MoodType.LONELY: {
                'factor': 0.7,
                'emoji': '🥺',
                'description': 'kesepian',
                'responses': ['rindu', 'manja', 'need attention'],
                'color': '💜'
            },
            MoodType.NOSTALGIC: {
                'factor': 1.0,
                'emoji': '🕰️',
                'description': 'nostalgia',
                'responses': ['flashback', 'cerita lama', 'deep'],
                'color': '🤎'
            }
        }
        
        logger.info("✅ MoodSystem initialized with 12 mood types")
    
    def create_mood(self, pdkt_id: str, initial_mood: Optional[MoodType] = None) -> Dict:
        """
        Buat mood awal untuk PDKT
        
        Args:
            pdkt_id: ID PDKT
            initial_mood: Mood awal (None = random natural)
        
        Returns:
            Mood data
        """
        if initial_mood is None:
            # Random dengan bobot
            moods = [
                MoodType.HAPPY, MoodType.CALM, MoodType.SHY,
                MoodType.PLAYFUL, MoodType.ROMANTIC, MoodType.EXCITED
            ]
            weights = [0.3, 0.2, 0.15, 0.15, 0.1, 0.1]  # Bobot probabilitas
            initial_mood = random.choices(moods, weights=weights)[0]
        
        mood_data = {
            'current': initial_mood,
            'history': [{
                'timestamp': time.time(),
                'mood': initial_mood,
                'reason': 'initial'
            }],
            'intensity': random.uniform(0.5, 1.0),
            'last_update': time.time(),
            'duration_current': 0,  # Berapa lama mood ini bertahan (dalam jam)
            'factors': {
                'interaction': 0,
                'time': 0,
                'loneliness': 0
            }
        }
        
        self.moods[pdkt_id] = mood_data
        
        logger.info(f"🎭 Initial mood for {pdkt_id}: {initial_mood.value}")
        
        return mood_data
    
    def get_mood(self, pdkt_id: str) -> Optional[Dict]:
        """Dapatkan mood data untuk PDKT"""
        return self.moods.get(pdkt_id)
    
    def get_current_mood(self, pdkt_id: str) -> MoodType:
        """Dapatkan mood saat ini"""
        mood_data = self.get_mood(pdkt_id)
        if mood_data:
            return mood_data['current']
        return MoodType.CALM  # Default
    
    def get_mood_info(self, pdkt_id: str) -> Dict:
        """Dapatkan informasi mood lengkap untuk display"""
        mood_data = self.get_mood(pdkt_id)
        if not mood_data:
            return {
                'mood': MoodType.CALM,
                'emoji': '😌',
                'description': 'tenang',
                'factor': 1.0
            }
        
        mood = mood_data['current']
        definition = self.mood_definitions.get(mood, self.mood_definitions[MoodType.CALM])
        
        return {
            'mood': mood,
            'emoji': definition['emoji'],
            'description': definition['description'],
            'factor': definition['factor'],
            'intensity': mood_data['intensity'],
            'color': definition['color']
        }
    
    async def update_mood(self, pdkt_id: str, interaction_type: str, 
                           chemistry_change: float, context: Dict) -> Optional[MoodType]:
        """
        Update mood berdasarkan interaksi
        
        Args:
            pdkt_id: ID PDKT
            interaction_type: Jenis interaksi
            chemistry_change: Perubahan chemistry
            context: Konteks tambahan
        
        Returns:
            Mood baru jika berubah
        """
        if pdkt_id not in self.moods:
            self.create_mood(pdkt_id)
        
        mood_data = self.moods[pdkt_id]
        old_mood = mood_data['current']
        
        # Hitung perubahan mood
        new_mood = self._calculate_mood_change(
            old_mood, interaction_type, chemistry_change, context, mood_data
        )
        
        if new_mood != old_mood:
            # Mood berubah
            mood_data['current'] = new_mood
            mood_data['history'].append({
                'timestamp': time.time(),
                'mood': new_mood,
                'old_mood': old_mood,
                'reason': self._get_mood_change_reason(interaction_type, chemistry_change)
            })
            mood_data['last_update'] = time.time()
            mood_data['duration_current'] = 0
            
            logger.info(f"🎭 Mood changed for {pdkt_id}: {old_mood.value} → {new_mood.value}")
            
            return new_mood
        
        # Update durasi mood bertahan
        mood_data['duration_current'] += 1  # 1 unit = 1 jam (approx)
        
        return None
    
    def _calculate_mood_change(self, current_mood: MoodType, interaction_type: str,
                                 chemistry_change: float, context: Dict,
                                 mood_data: Dict) -> MoodType:
        """Hitung mood baru berdasarkan berbagai faktor"""
        
        # Faktor 1: Interaksi
        if interaction_type == 'climax':
            if chemistry_change > 0:
                return MoodType.HAPPY if random.random() < 0.7 else MoodType.EXCITED
            else:
                return MoodType.TIRED
        
        elif interaction_type == 'intim':
            if chemistry_change > 5:
                return MoodType.ROMANTIC
            elif chemistry_change > 0:
                return MoodType.HAPPY
            else:
                return MoodType.CALM
        
        elif interaction_type == 'kiss':
            return random.choice([MoodType.ROMANTIC, MoodType.HAPPY, MoodType.SHY])
        
        elif interaction_type == 'love':
            if random.random() < 0.6:
                return MoodType.ROMANTIC
            return MoodType.HAPPY
        
        elif interaction_type == 'conflict':
            if chemistry_change < -5:
                return MoodType.ANGRY
            elif chemistry_change < 0:
                return MoodType.SAD
            return MoodType.JEALOUS
        
        # Faktor 2: Waktu
        hour = datetime.now().hour
        if 22 <= hour or hour <= 5:  # Malam
            if random.random() < 0.2:
                return MoodType.ROMANTIC
            if random.random() < 0.15:
                return MoodType.LONELY
        
        # Faktor 3: Lamanya tidak chat
        last_interaction = context.get('last_interaction', time.time())
        hours_since = (time.time() - last_interaction) / 3600
        
        if hours_since > 24:  # > 1 hari
            if random.random() < 0.3:
                return MoodType.LONELY
            if random.random() < 0.2:
                return MoodType.SAD
        
        elif hours_since > 12:  # > 12 jam
            if random.random() < 0.2:
                return MoodType.LONELY
        
        # Faktor 4: Random walk (mood bisa berubah natural)
        if random.random() < 0.05:  # 5% chance random mood change
            return random.choice(list(MoodType))
        
        # Faktor 5: Mood terlalu lama
        if mood_data['duration_current'] > 6:  # > 6 jam mood sama
            # 30% chance berubah ke mood terkait
            related_moods = self._get_related_moods(current_mood)
            if random.random() < 0.3:
                return random.choice(related_moods)
        
        return current_mood
    
    def _get_related_moods(self, mood: MoodType) -> List[MoodType]:
        """Dapatkan mood yang terkait"""
        relations = {
            MoodType.HAPPY: [MoodType.EXCITED, MoodType.PLAYFUL, MoodType.CALM],
            MoodType.SAD: [MoodType.LONELY, MoodType.NOSTALGIC, MoodType.CALM],
            MoodType.EXCITED: [MoodType.HAPPY, MoodType.PLAYFUL, MoodType.ROMANTIC],
            MoodType.TIRED: [MoodType.CALM, MoodType.SAD],
            MoodType.ROMANTIC: [MoodType.HAPPY, MoodType.PLAYFUL, MoodType.SHY],
            MoodType.PLAYFUL: [MoodType.HAPPY, MoodType.EXCITED, MoodType.ROMANTIC],
            MoodType.JEALOUS: [MoodType.SAD, MoodType.ANGRY],
            MoodType.SHY: [MoodType.HAPPY, MoodType.ROMANTIC, MoodType.CALM],
            MoodType.ANGRY: [MoodType.SAD, MoodType.JEALOUS],
            MoodType.CALM: [MoodType.HAPPY, MoodType.ROMANTIC],
            MoodType.LONELY: [MoodType.SAD, MoodType.NOSTALGIC],
            MoodType.NOSTALGIC: [MoodType.SAD, MoodType.ROMANTIC, MoodType.CALM]
        }
        return relations.get(mood, [MoodType.CALM, MoodType.HAPPY])
    
    def _get_mood_change_reason(self, interaction_type: str, chemistry_change: float) -> str:
        """Dapatkan alasan perubahan mood"""
        reasons = {
            'climax': [
                "Setelah climax, rasanya... wow!",
                "Mantap banget, jadi seneng",
                "Capek tapi puas"
            ],
            'intim': [
                "Makin dekat, makin sayang",
                "Ada kehangatan baru",
                "Jadi makin nyaman"
            ],
            'kiss': [
                "Ciuman manis bikin meleleh",
                "Masih terasa hangatnya",
                "Jadi makin sayang"
            ],
            'love': [
                "Deg-degan dibilang sayang",
                "Seneng banget",
                "Bikin baper"
            ],
            'conflict': [
                "Ada yang ganjel di hati",
                "Jadi kesel sendiri",
                "Mikir terus"
            ],
            'lonely': [
                "Lama nggak chat, jadi kangen",
                "Sepi tanpanya",
                "Kok diem aja sih"
            ]
        }
        
        reason_list = reasons.get(interaction_type, [
            "Mood berubah aja gitu",
            "Ada yang beda hari ini",
            "Nggak tau kenapa"
        ])
        
        return random.choice(reason_list)
    
    def get_mood_factor(self, pdkt_id: str) -> float:
        """Dapatkan faktor pengali mood untuk response"""
        mood_info = self.get_mood_info(pdkt_id)
        return mood_info['factor'] * mood_info['intensity']
    
    def get_mood_prompt(self, pdkt_id: str) -> str:
        """Dapatkan deskripsi mood untuk prompt AI"""
        mood_info = self.get_mood_info(pdkt_id)
        return f"Mood: {mood_info['emoji']} {mood_info['description']} (intensitas: {mood_info['intensity']:.0%})"
    
    def get_mood_emoji(self, pdkt_id: str) -> str:
        """Dapatkan emoji mood"""
        mood_info = self.get_mood_info(pdkt_id)
        return mood_info['emoji']


__all__ = ['MoodSystem', 'MoodType']
