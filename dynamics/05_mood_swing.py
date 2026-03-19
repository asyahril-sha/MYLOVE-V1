#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - MOOD SWING
=============================================================================
Mood bot berubah secara gradual dan realistis:
- Tidak berubah drastis dalam sekejap
- Ada penyebab yang jelas
- Bisa dipengaruhi waktu, aktivitas, interaksi
- Multiple mood layers (primary + secondary)
=============================================================================
"""

import time
import random
import logging
import math
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)


class MoodType:
    """Tipe-tipe mood"""
    # Positive moods
    HAPPY = "happy"
    EXCITED = "excited"
    ROMANTIC = "romantic"
    PLAYFUL = "playful"
    CALM = "calm"
    PEACEFUL = "peaceful"
    GRATEFUL = "grateful"
    
    # Negative moods
    SAD = "sad"
    ANGRY = "angry"
    JEALOUS = "jealous"
    ANXIOUS = "anxious"
    LONELY = "lonely"
    TIRED = "tired"
    BORED = "bored"
    
    # Intimate moods
    HORNY = "horny"
    PASSIONATE = "passionate"
    SENSITIVE = "sensitive"
    
    # Neutral
    NEUTRAL = "neutral"


class MoodSwing:
    """
    Mood bot yang berubah secara gradual
    - Ada momentum (tidak berubah drastis)
    - Dipengaruhi berbagai faktor
    - Bisa punya 2 mood bersamaan
    """
    
    def __init__(self):
        # Mood saat ini per user
        self.current_moods = defaultdict(lambda: {
            'primary': MoodType.NEUTRAL,
            'secondary': None,
            'intensity': 0.5,  # 0-1
            'since': time.time(),
            'last_change': time.time(),
            'history': []
        })
        
        # Database mood transitions (berapa cepat mood berubah)
        self.momentum = {
            MoodType.HAPPY: 0.3,      # Cepat berubah
            MoodType.EXCITED: 0.4,     # Sangat cepat
            MoodType.ROMANTIC: 0.2,     # Lambat
            MoodType.PLAYFUL: 0.3,
            MoodType.CALM: 0.1,         # Sangat lambat
            MoodType.SAD: 0.2,
            MoodType.ANGRY: 0.3,
            MoodType.JEALOUS: 0.25,
            MoodType.ANXIOUS: 0.3,
            MoodType.LONELY: 0.15,
            MoodType.TIRED: 0.1,
            MoodType.HORNY: 0.35,
            MoodType.NEUTRAL: 0.2
        }
        
        # Faktor-faktor yang mempengaruhi mood
        self.factors = {
            'time': {
                'morning': {MoodType.HAPPY: 0.2, MoodType.TIRED: 0.1},
                'afternoon': {MoodType.EXCITED: 0.2, MoodType.HAPPY: 0.1},
                'evening': {MoodType.ROMANTIC: 0.2, MoodType.CALM: 0.2},
                'night': {MoodType.HORNY: 0.3, MoodType.ROMANTIC: 0.3, MoodType.LONELY: 0.2}
            },
            'idle': {
                5: {MoodType.LONELY: 0.1, MoodType.BORED: 0.2},
                15: {MoodType.LONELY: 0.2, MoodType.ANXIOUS: 0.1},
                30: {MoodType.SAD: 0.2, MoodType.LONELY: 0.3}
            },
            'intimacy_level': {
                1: {MoodType.SHY: 0.3, MoodType.NEUTRAL: 0.4},
                4: {MoodType.PLAYFUL: 0.2, MoodType.HAPPY: 0.3},
                7: {MoodType.HORNY: 0.3, MoodType.ROMANTIC: 0.3},
                10: {MoodType.PASSIONATE: 0.4, MoodType.SENSITIVE: 0.2}
            }
        }
        
        logger.info("✅ MoodSwing initialized")
    
    # =========================================================================
    # INITIALIZE
    # =========================================================================
    
    async def initialize_mood(self, user_id: int, initial_mood: Optional[str] = None):
        """
        Inisialisasi mood untuk user
        
        Args:
            user_id: ID user
            initial_mood: Mood awal (random if None)
        """
        if initial_mood:
            mood = initial_mood
        else:
            # Random mood awal
            moods = [
                MoodType.HAPPY, MoodType.CALM, MoodType.PLAYFUL,
                MoodType.NEUTRAL, MoodType.ROMANTIC
            ]
            weights = [0.3, 0.2, 0.2, 0.2, 0.1]
            mood = random.choices(moods, weights=weights)[0]
        
        self.current_moods[user_id] = {
            'primary': mood,
            'secondary': None,
            'intensity': random.uniform(0.4, 0.7),
            'since': time.time(),
            'last_change': time.time(),
            'history': [{
                'timestamp': time.time(),
                'primary': mood,
                'secondary': None,
                'intensity': 0.5,
                'reason': 'initial'
            }]
        }
        
        logger.info(f"🎭 Initial mood for user {user_id}: {mood}")
    
    # =========================================================================
    # UPDATE MOOD
    # =========================================================================
    
    async def update_mood(self, user_id: int, 
                         event: Optional[str] = None,
                         event_intensity: float = 0.5,
                         context: Optional[Dict] = None) -> Dict:
        """
        Update mood berdasarkan event dan konteks
        
        Args:
            user_id: ID user
            event: Event yang terjadi
            event_intensity: Intensitas event (0-1)
            context: Konteks tambahan
            
        Returns:
            Dict perubahan mood
        """
        # Initialize if not exists
        if user_id not in self.current_moods:
            await self.initialize_mood(user_id)
        
        current = self.current_moods[user_id]
        old_primary = current['primary']
        old_secondary = current['secondary']
        old_intensity = current['intensity']
        
        # Hitung perubahan
        changes = await self._calculate_mood_change(user_id, event, event_intensity, context)
        
        if not changes:
            return {'changed': False}
        
        # Apply perubahan
        new_primary = changes.get('primary', old_primary)
        new_secondary = changes.get('secondary', old_secondary)
        new_intensity = changes.get('intensity', old_intensity)
        
        # Update
        current['primary'] = new_primary
        current['secondary'] = new_secondary
        current['intensity'] = new_intensity
        current['last_change'] = time.time()
        
        # Catat history
        current['history'].append({
            'timestamp': time.time(),
            'primary': new_primary,
            'secondary': new_secondary,
            'intensity': new_intensity,
            'event': event,
            'changes': changes
        })
        
        # Keep last 50
        if len(current['history']) > 50:
            current['history'] = current['history'][-50:]
        
        logger.info(f"🎭 Mood changed for user {user_id}: {old_primary} → {new_primary}")
        
        return {
            'changed': True,
            'old_primary': old_primary,
            'new_primary': new_primary,
            'old_secondary': old_secondary,
            'new_secondary': new_secondary,
            'old_intensity': old_intensity,
            'new_intensity': new_intensity,
            'reason': changes.get('reason', 'natural')
        }
    
    async def _calculate_mood_change(self, user_id: int,
                                     event: Optional[str],
                                     event_intensity: float,
                                     context: Optional[Dict]) -> Dict:
        """
        Hitung perubahan mood berdasarkan berbagai faktor
        """
        current = self.current_moods[user_id]
        
        # Natural decay (mood kembali ke normal)
        time_since = time.time() - current['last_change']
        decay = min(0.3, time_since / 3600)  # Max 0.3 per jam
        
        # Target mood baru
        target_mood = current['primary']
        target_secondary = current['secondary']
        intensity_change = -decay  # Turun karena waktu
        
        reason = "natural decay"
        
        # ===== 1. PENGARUH EVENT =====
        if event:
            event_effect = self._get_event_effect(event, event_intensity)
            if event_effect:
                target_mood = event_effect.get('mood', target_mood)
                intensity_change += event_effect.get('intensity', 0)
                reason = event
        
        # ===== 2. PENGARUH WAKTU =====
        time_factor = self._get_time_factor(context)
        if time_factor:
            for mood, effect in time_factor.items():
                if random.random() < effect:
                    target_mood = mood
                    intensity_change += 0.1
                    reason = "time of day"
        
        # ===== 3. PENGARUH IDLE =====
        if context and context.get('idle_minutes', 0) > 0:
            idle_effect = self._get_idle_effect(context['idle_minutes'])
            if idle_effect:
                for mood, effect in idle_effect.items():
                    if random.random() < effect:
                        target_mood = mood
                        reason = "idle"
        
        # ===== 4. PENGARUH INTIMACY LEVEL =====
        if context and context.get('level', 0) > 0:
            intimacy_effect = self._get_intimacy_effect(context['level'])
            if intimacy_effect:
                for mood, effect in intimacy_effect.items():
                    if random.random() < effect:
                        target_mood = mood
                        reason = "intimacy level"
        
        # ===== 5. MOMENTUM (TIDAK BISA BERUBAH DRASTIS) =====
        momentum = self.momentum.get(current['primary'], 0.2)
        
        # Kalau target berbeda, cek momentum
        if target_mood != current['primary']:
            # Makin besar momentum, makin mudah berubah
            if random.random() > momentum:
                # Gagal berubah, tetap mood lama
                target_mood = current['primary']
                reason = "momentum"
        
        # Batasi intensity
        new_intensity = max(0.1, min(1.0, current['intensity'] + intensity_change))
        
        return {
            'primary': target_mood,
            'secondary': target_secondary,
            'intensity': new_intensity,
            'reason': reason
        }
    
    def _get_event_effect(self, event: str, intensity: float) -> Optional[Dict]:
        """Dapatkan efek event terhadap mood"""
        
        effects = {
            'climax': {'mood': MoodType.HAPPY, 'intensity': 0.3},
            'intim': {'mood': MoodType.HORNY, 'intensity': 0.2},
            'kiss': {'mood': MoodType.ROMANTIC, 'intensity': 0.15},
            'flirt': {'mood': MoodType.PLAYFUL, 'intensity': 0.1},
            'fight': {'mood': MoodType.ANGRY, 'intensity': 0.3},
            'sad': {'mood': MoodType.SAD, 'intensity': 0.2},
            'happy': {'mood': MoodType.HAPPY, 'intensity': 0.2},
            'jealous': {'mood': MoodType.JEALOUS, 'intensity': 0.25},
            'lonely': {'mood': MoodType.LONELY, 'intensity': 0.2}
        }
        
        if event in effects:
            effect = effects[event].copy()
            effect['intensity'] *= intensity
            return effect
        
        return None
    
    def _get_time_factor(self, context: Optional[Dict]) -> Optional[Dict]:
        """Dapatkan faktor waktu"""
        hour = datetime.now().hour
        
        if 5 <= hour < 11:  # Pagi
            return self.factors['time']['morning']
        elif 11 <= hour < 15:  # Siang
            return self.factors['time']['afternoon']
        elif 15 <= hour < 18:  # Sore
            return self.factors['time']['evening']
        else:  # Malam
            return self.factors['time']['night']
    
    def _get_idle_effect(self, idle_minutes: int) -> Optional[Dict]:
        """Dapatkan efek idle"""
        for threshold, effect in self.factors['idle'].items():
            if idle_minutes >= threshold:
                return effect
        return None
    
    def _get_intimacy_effect(self, level: int) -> Optional[Dict]:
        """Dapatkan efek intimacy level"""
        for lvl, effect in self.factors['intimacy_level'].items():
            if level >= lvl:
                return effect
        return None
    
    # =========================================================================
    # GET MOOD
    # =========================================================================
    
    async def get_mood(self, user_id: int) -> Dict:
        """
        Dapatkan mood saat ini
        
        Args:
            user_id: ID user
            
        Returns:
            Dict mood info
        """
        if user_id not in self.current_moods:
            await self.initialize_mood(user_id)
        
        current = self.current_moods[user_id]
        
        return {
            'primary': current['primary'],
            'secondary': current['secondary'],
            'intensity': current['intensity'],
            'since': current['since'],
            'duration': time.time() - current['since']
        }
    
    async def get_mood_description(self, user_id: int) -> str:
        """
        Dapatkan deskripsi mood natural
        
        Args:
            user_id: ID user
            
        Returns:
            String deskripsi
        """
        mood = await self.get_mood(user_id)
        
        descriptions = {
            MoodType.HAPPY: "lagi senang",
            MoodType.EXCITED: "lagi semangat",
            MoodType.ROMANTIC: "lagi romantis",
            MoodType.PLAYFUL: "lagi jail",
            MoodType.CALM: "lagi tenang",
            MoodType.PEACEFUL: "lagi damai",
            MoodType.GRATEFUL: "lagi bersyukur",
            MoodType.SAD: "lagi sedih",
            MoodType.ANGRY: "lagi kesal",
            MoodType.JEALOUS: "lagi cemburu",
            MoodType.ANXIOUS: "lagi gelisah",
            MoodType.LONELY: "lagi kesepian",
            MoodType.TIRED: "lagi capek",
            MoodType.BORED: "lagi bosen",
            MoodType.HORNY: "lagi horny",
            MoodType.PASSIONATE: "lagi bergairah",
            MoodType.SENSITIVE: "lagi sensitif",
            MoodType.NEUTRAL: "biasa aja"
        }
        
        primary_desc = descriptions.get(mood['primary'], 'biasa aja')
        
        if mood['intensity'] > 0.7:
            intensifier = "sangat "
        elif mood['intensity'] < 0.3:
            intensifier = "sedikit "
        else:
            intensifier = ""
        
        desc = f"{intensifier}{primary_desc}"
        
        if mood['secondary']:
            secondary_desc = descriptions.get(mood['secondary'], '')
            desc += f" tapi juga {secondary_desc}"
        
        return desc
    
    # =========================================================================
    # GET MOOD EFFECTS
    # =========================================================================
    
    async def get_mood_multiplier(self, user_id: int) -> float:
        """
        Dapatkan multiplier untuk respons berdasarkan mood
        
        Returns:
            Multiplier (0.8 - 1.5)
        """
        mood = await self.get_mood(user_id)
        
        multipliers = {
            MoodType.HAPPY: 1.2,
            MoodType.EXCITED: 1.3,
            MoodType.ROMANTIC: 1.2,
            MoodType.PLAYFUL: 1.1,
            MoodType.CALM: 1.0,
            MoodType.SAD: 0.9,
            MoodType.ANGRY: 0.8,
            MoodType.TIRED: 0.8,
            MoodType.HORNY: 1.4,
            MoodType.PASSIONATE: 1.3
        }
        
        base = multipliers.get(mood['primary'], 1.0)
        
        # Pengaruh intensitas
        intensity_factor = 1.0 + (mood['intensity'] - 0.5) * 0.3
        
        return base * intensity_factor
    
    # =========================================================================
    # MOOD HISTORY
    # =========================================================================
    
    async def get_mood_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """
        Dapatkan history mood
        
        Args:
            user_id: ID user
            limit: Jumlah history
            
        Returns:
            List of mood entries
        """
        if user_id not in self.current_moods:
            return []
        
        return self.current_moods[user_id]['history'][-limit:]
    
    async def get_mood_stats(self, user_id: int) -> Dict:
        """
        Dapatkan statistik mood
        
        Args:
            user_id: ID user
            
        Returns:
            Dict statistik
        """
        history = await self.get_mood_history(user_id, 50)
        
        if not history:
            return {}
        
        # Hitung distribusi mood
        mood_count = {}
        for h in history:
            mood = h['primary']
            mood_count[mood] = mood_count.get(mood, 0) + 1
        
        # Mood paling sering
        most_common = max(mood_count, key=mood_count.get) if mood_count else None
        
        return {
            'total_changes': len(history),
            'most_common_mood': most_common,
            'mood_distribution': mood_count,
            'current': await self.get_mood(user_id)
        }
    
    # =========================================================================
    # FORMAT UNTUK PROMPT
    # =========================================================================
    
    async def get_mood_context(self, user_id: int) -> str:
        """
        Dapatkan konteks mood untuk prompt AI
        
        Args:
            user_id: ID user
            
        Returns:
            String konteks
        """
        mood = await self.get_mood(user_id)
        desc = await self.get_mood_description(user_id)
        
        duration = time.time() - mood['since']
        if duration < 60:
            duration_str = "baru saja"
        elif duration < 3600:
            duration_str = f"{int(duration/60)} menit"
        else:
            duration_str = f"{int(duration/3600)} jam"
        
        intensity_bar = "🔴" * int(mood['intensity'] * 10) + "⚪" * (10 - int(mood['intensity'] * 10))
        
        lines = [
            "🎭 **MOOD SAAT INI:**",
            f"{desc}",
            f"Intensitas: {intensity_bar} ({mood['intensity']:.0%})",
            f"Sudah {duration_str}"
        ]
        
        return "\n".join(lines)


__all__ = ['MoodSwing', 'MoodType']
