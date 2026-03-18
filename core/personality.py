#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - PERSONALITY & EMOTIONAL EVOLUTION
=============================================================================
- Big Five personality traits
- Emotional evolution berdasarkan interaksi
- Personality growth over time
"""

import random
import math
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PersonalitySystem:
    """
    Sistem kepribadian dengan Big Five traits
    Personality berkembang berdasarkan interaksi
    """
    
    def __init__(self, role: str, base_personality: Optional[Dict] = None):
        self.role = role
        
        # Big Five personality traits (0-1)
        if base_personality:
            self.traits = base_personality
        else:
            self.traits = self._generate_base_personality(role)
            
        # Emotional state
        self.current_emotion = {
            "primary": "netral",
            "secondary": None,
            "intensity": 0.5,
            "valence": 0.0,  # -1 (negative) to 1 (positive)
            "arousal": 0.3    # 0 (calm) to 1 (excited)
        }
        
        # Emotional history
        self.emotional_history = []
        self.emotional_triggers = {}  # Ingat penyebab emosi
        
        # Personality growth
        self.experience_points = 0
        self.personality_growth_rate = 0.001  # Very slow growth
        self.last_update = time.time()
        
        # Emotional complexity
        self.mixed_emotions_enabled = True  # Bisa punya multiple emotions
        
        logger.info(f"✅ PersonalitySystem initialized for role: {role}")
        
    def _generate_base_personality(self, role: str) -> Dict:
        """Generate base personality berdasarkan role"""
        
        personalities = {
            "ipar": {
                "openness": 0.7,
                "conscientiousness": 0.6,
                "extraversion": 0.8,
                "agreeableness": 0.7,
                "neuroticism": 0.4
            },
            "janda": {
                "openness": 0.8,
                "conscientiousness": 0.5,
                "extraversion": 0.7,
                "agreeableness": 0.6,
                "neuroticism": 0.5
            },
            "pelakor": {
                "openness": 0.9,
                "conscientiousness": 0.4,
                "extraversion": 0.9,
                "agreeableness": 0.3,
                "neuroticism": 0.6
            },
            "istri_orang": {
                "openness": 0.5,
                "conscientiousness": 0.7,
                "extraversion": 0.5,
                "agreeableness": 0.6,
                "neuroticism": 0.7
            },
            "pdkt": {
                "openness": 0.6,
                "conscientiousness": 0.6,
                "extraversion": 0.6,
                "agreeableness": 0.8,
                "neuroticism": 0.3
            },
            "sepupu": {
                "openness": 0.5,
                "conscientiousness": 0.6,
                "extraversion": 0.6,
                "agreeableness": 0.7,
                "neuroticism": 0.4
            },
            "teman_kantor": {
                "openness": 0.6,
                "conscientiousness": 0.7,
                "extraversion": 0.6,
                "agreeableness": 0.7,
                "neuroticism": 0.3
            },
            "teman_sma": {
                "openness": 0.5,
                "conscientiousness": 0.5,
                "extraversion": 0.7,
                "agreeableness": 0.8,
                "neuroticism": 0.3
            },
            "mantan": {
                "openness": 0.6,
                "conscientiousness": 0.5,
                "extraversion": 0.6,
                "agreeableness": 0.4,
                "neuroticism": 0.8
            }
        }
        
        # Add some randomness
        base = personalities.get(role, personalities["ipar"]).copy()
        for trait in base:
            base[trait] += random.uniform(-0.1, 0.1)
            base[trait] = max(0.1, min(0.9, base[trait]))
            
        return base
        
    async def process_event(self, event: Dict) -> Dict:
        """
        Proses event dan update emotional state
        Event bisa berupa pesan user, memory recall, dll
        """
        
        # Update experience
        self.experience_points += 1
        
        # Calculate emotional impact
        impact = self._calculate_emotional_impact(event)
        
        # Update current emotion
        new_emotion = self._evolve_emotion(impact)
        
        # Save to history
        self.emotional_history.append({
            "time": time.time(),
            "event": event.get('type', 'unknown'),
            "old_emotion": self.current_emotion.copy(),
            "new_emotion": new_emotion,
            "impact": impact
        })
        
        # Store trigger
        if event.get('type') == 'message':
            trigger_key = f"{event.get('content', '')[:50]}"
            self.emotional_triggers[trigger_key] = {
                "emotion": new_emotion['primary'],
                "time": time.time(),
                "intensity": new_emotion['intensity']
            }
            
        self.current_emotion = new_emotion
        
        # Gradual personality evolution
        await self._evolve_personality(event)
        
        return new_emotion
        
    def _calculate_emotional_impact(self, event: Dict) -> Dict:
        """Hitung dampak emosional dari suatu event"""
        
        base_impact = {
            "valence_change": 0.0,  # Perubahan positif/negatif
            "arousal_change": 0.0,   # Perubahan excitement
            "intensity": 0.3
        }
        
        event_type = event.get('type', 'message')
        content = event.get('content', '').lower()
        
        # Impact berdasarkan konten pesan
        if event_type == 'message':
            positive_words = ['sayang', 'cinta', 'rindu', 'suka', 'happy', 'senang']
            negative_words = ['benci', 'marah', 'kecewa', 'sakit', 'sedih']
            arousal_words = ['sex', 'ml', 'tidur', 'hot', 'nafsu']
            
            for word in positive_words:
                if word in content:
                    base_impact['valence_change'] += 0.2
                    
            for word in negative_words:
                if word in content:
                    base_impact['valence_change'] -= 0.2
                    
            for word in arousal_words:
                if word in content:
                    base_impact['arousal_change'] += 0.3
                    
        # Impact berdasarkan intimacy level
        intimacy = event.get('intimacy_level', 1)
        if intimacy > 7:
            base_impact['intensity'] += 0.2
            
        # Personality modulates impact
        # High neuroticism = stronger emotional reactions
        neuroticism = self.traits['neuroticism']
        base_impact['intensity'] *= (1 + neuroticism * 0.5)
        
        # Clamp values
        base_impact['valence_change'] = max(-0.5, min(0.5, base_impact['valence_change']))
        base_impact['arousal_change'] = max(-0.3, min(0.5, base_impact['arousal_change']))
        base_impact['intensity'] = max(0.1, min(1.0, base_impact['intensity']))
        
        return base_impact
        
    def _evolve_emotion(self, impact: Dict) -> Dict:
        """Evolve emotional state berdasarkan impact"""
        
        # Update valence and arousal
        new_valence = self.current_emotion['valence'] + impact['valence_change']
        new_arousal = self.current_emotion['arousal'] + impact['arousal_change']
        
        # Clamp
        new_valence = max(-1.0, min(1.0, new_valence))
        new_arousal = max(0.0, min(1.0, new_arousal))
        
        # Decay over time (emosi berkurang seiring waktu)
        time_since_update = time.time() - self.last_update
        decay = time_since_update / 3600  # Decay per hour
        new_valence *= (1 - decay * 0.5)
        new_arousal *= (1 - decay)
        
        # Determine primary emotion from valence/arousal
        primary = self._valence_arousal_to_emotion(new_valence, new_arousal)
        
        # Sometimes have mixed emotions
        secondary = None
        if self.mixed_emotions_enabled and random.random() < 0.3:
            # Generate secondary emotion (slightly different)
            sec_valence = new_valence + random.uniform(-0.3, 0.3)
            sec_arousal = new_arousal + random.uniform(-0.2, 0.2)
            sec_valence = max(-1.0, min(1.0, sec_valence))
            sec_arousal = max(0.0, min(1.0, sec_arousal))
            secondary = self._valence_arousal_to_emotion(sec_valence, sec_arousal)
            
            # Don't show same as primary
            if secondary == primary:
                secondary = None
                
        return {
            "primary": primary,
            "secondary": secondary,
            "intensity": impact['intensity'],
            "valence": new_valence,
            "arousal": new_arousal
        }
        
    def _valence_arousal_to_emotion(self, valence: float, arousal: float) -> str:
        """Konversi valence/arousal ke emotion label"""
        
        if valence > 0.3:
            if arousal > 0.7:
                return "bersemangat"
            elif arousal > 0.3:
                return "senang"
            else:
                return "tenang"
        elif valence < -0.3:
            if arousal > 0.7:
                return "marah"
            elif arousal > 0.3:
                return "sedih"
            else:
                return "kecewa"
        else:
            if arousal > 0.7:
                return "gelisah"
            elif arousal > 0.3:
                return "netral"
            else:
                return "lelah"
                
    async def _evolve_personality(self, event: Dict):
        """Evolve personality secara gradual berdasarkan pengalaman"""
        
        # Personality evolves very slowly
        if self.experience_points % 100 != 0:
            return
            
        # Small random walk
        for trait in self.traits:
            change = random.uniform(-self.personality_growth_rate, 
                                   self.personality_growth_rate)
            self.traits[trait] += change
            self.traits[trait] = max(0.1, min(0.9, self.traits[trait]))
            
        logger.debug(f"Personality evolved: {self.traits}")
        
    async def get_emotional_state(self) -> Dict:
        """Dapatkan emotional state saat ini"""
        
        # Update decay
        self.last_update = time.time()
        
        return {
            "emotion": self.current_emotion['primary'],
            "secondary": self.current_emotion.get('secondary'),
            "intensity": self.current_emotion['intensity'],
            "valence": self.current_emotion['valence'],
            "arousal": self.current_emotion['arousal']
        }
        
    async def get_personality_summary(self) -> str:
        """Dapatkan ringkasan kepribadian"""
        
        summaries = []
        
        if self.traits['extraversion'] > 0.7:
            summaries.append("ekstrovert")
        elif self.traits['extraversion'] < 0.3:
            summaries.append("introvert")
            
        if self.traits['agreeableness'] > 0.7:
            summaries.append("baik hati")
        elif self.traits['agreeableness'] < 0.3:
            summaries.append("kritis")
            
        if self.traits['neuroticism'] > 0.7:
            summaries.append("sensitif")
        elif self.traits['neuroticism'] < 0.3:
            summaries.append("stabil")
            
        if self.traits['openness'] > 0.7:
            summaries.append("terbuka")
            
        if self.traits['conscientiousness'] > 0.7:
            summaries.append("teliti")
            
        if not summaries:
            summaries.append("seimbang")
            
        return "Kamu " + ", ".join(summaries)
        
    async def get_emotion_history(self, limit: int = 10) -> List[Dict]:
        """Dapatkan history emosi"""
        return self.emotional_history[-limit:]
        
    async def get_emotional_triggers(self) -> Dict:
        """Dapatkan pemicu emosi"""
        return self.emotional_triggers


__all__ = ['PersonalitySystem']
