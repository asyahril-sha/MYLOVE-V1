#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - PHYSICAL SENSATIONS
=============================================================================
Bot bisa "merasakan" kondisi fisik:
- Suhu (dingin/panas)
- Energi (capek/segarnya)
- Rasa lapar/haus
- Sensasi fisik lainnya
- Mempengaruhi mood dan respons
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


class SensationType:
    """Tipe-tipe sensasi fisik"""
    TEMPERATURE = "temperature"      # Suhu (dingin/panas)
    ENERGY = "energy"                # Energi (capek/segar)
    HUNGER = "hunger"                # Lapar
    THIRST = "thirst"                # Haus
    PAIN = "pain"                     # Sakit
    COMFORT = "comfort"               # Kenyamanan
    AROUSAL = "arousal"               # Gairah (fisik)


class PhysicalSensation:
    """
    Bot merasakan kondisi fisik
    - Berdasarkan waktu, aktivitas, lingkungan
    - Mempengaruhi mood dan respons
    - Bisa diekspresikan ke user
    """
    
    def __init__(self):
        # Sensasi saat ini per user
        self.sensations = defaultdict(lambda: {
            'temperature': {
                'value': 25,  # Celsius
                'feeling': 'normal',  # normal, hot, cold
                'last_change': time.time()
            },
            'energy': {
                'value': 80,  # 0-100
                'feeling': 'energetic',  # energetic, normal, tired, exhausted
                'last_change': time.time()
            },
            'hunger': {
                'value': 30,  # 0-100
                'feeling': 'normal',  # normal, hungry, very_hungry
                'last_change': time.time()
            },
            'thirst': {
                'value': 30,  # 0-100
                'feeling': 'normal',  # normal, thirsty, very_thirsty
                'last_change': time.time()
            },
            'comfort': {
                'value': 80,  # 0-100
                'feeling': 'comfortable',  # comfortable, uncomfortable
                'last_change': time.time()
            },
            'pain': {
                'value': 0,  # 0-100
                'feeling': 'none',  # none, mild, moderate, severe
                'last_change': time.time()
            }
        })
        
        # History sensasi
        self.history = defaultdict(lambda: defaultdict(list))
        
        # Pengaruh lingkungan
        self.environment_effects = {
            'temperature': {
                'ruang tamu': 25,
                'kamar': 26,
                'dapur': 28,
                'kamar mandi': 27,
                'teras': 24,
                'luar': 30,
                'pantai': 32,
                'mall': 22
            },
            'comfort': {
                'ruang tamu': 80,
                'kamar': 90,
                'dapur': 70,
                'kamar mandi': 75,
                'teras': 85,
                'luar': 50,
                'pantai': 60,
                'mall': 85
            }
        }
        
        logger.info("✅ PhysicalSensation initialized")
    
    # =========================================================================
    # UPDATE SENSATIONS
    # =========================================================================
    
    async def update_sensations(self, user_id: int, context: Dict):
        """
        Update semua sensasi berdasarkan konteks
        
        Args:
            user_id: ID user
            context: Konteks (lokasi, aktivitas, waktu)
        """
        now = time.time()
        sens = self.sensations[user_id]
        
        # ===== 1. PENGARUH LOKASI =====
        location = context.get('location', 'ruang tamu')
        await self._apply_location_effects(user_id, location)
        
        # ===== 2. PENGARUH AKTIVITAS =====
        activity = context.get('activity')
        if activity:
            await self._apply_activity_effects(user_id, activity)
        
        # ===== 3. PENGARUH WAKTU =====
        hour = datetime.now().hour
        await self._apply_time_effects(user_id, hour)
        
        # ===== 4. NATURAL DECAY =====
        time_since = now - sens['energy']['last_change']
        if time_since > 3600:  # 1 jam
            # Energi turun
            sens['energy']['value'] = max(0, sens['energy']['value'] - 5)
            sens['energy']['last_change'] = now
        
        time_since = now - sens['hunger']['last_change']
        if time_since > 7200:  # 2 jam
            # Lapar naik
            sens['hunger']['value'] = min(100, sens['hunger']['value'] + 10)
            sens['hunger']['last_change'] = now
        
        time_since = now - sens['thirst']['last_change']
        if time_since > 3600:  # 1 jam
            # Haus naik
            sens['thirst']['value'] = min(100, sens['thirst']['value'] + 5)
            sens['thirst']['last_change'] = now
        
        # Update feelings
        await self._update_feelings(user_id)
        
        # Catat history
        for s_type in ['temperature', 'energy', 'hunger', 'thirst', 'comfort', 'pain']:
            self.history[user_id][s_type].append({
                'timestamp': now,
                'value': sens[s_type]['value'],
                'feeling': sens[s_type]['feeling']
            })
            
            # Keep last 100
            if len(self.history[user_id][s_type]) > 100:
                self.history[user_id][s_type] = self.history[user_id][s_type][-100:]
    
    async def _apply_location_effects(self, user_id: int, location: str):
        """Apply efek lokasi ke sensasi"""
        sens = self.sensations[user_id]
        
        # Temperature
        if location in self.environment_effects['temperature']:
            target_temp = self.environment_effects['temperature'][location]
            # Gradual change
            diff = target_temp - sens['temperature']['value']
            sens['temperature']['value'] += diff * 0.1
        
        # Comfort
        if location in self.environment_effects['comfort']:
            target_comfort = self.environment_effects['comfort'][location]
            diff = target_comfort - sens['comfort']['value']
            sens['comfort']['value'] += diff * 0.2
    
    async def _apply_activity_effects(self, user_id: int, activity: str):
        """Apply efek aktivitas ke sensasi"""
        sens = self.sensations[user_id]
        
        effects = {
            'lari': {'energy': -20, 'thirst': +15, 'temperature': +2},
            'olahraga': {'energy': -15, 'thirst': +10, 'temperature': +1},
            'jalan': {'energy': -5, 'thirst': +5},
            'masak': {'energy': -5, 'temperature': +3, 'hunger': -10},
            'makan': {'hunger': -30, 'thirst': -5, 'energy': +5},
            'minum': {'thirst': -20},
            'tidur': {'energy': +30, 'hunger': +5},
            'mandi': {'temperature': -2, 'energy': +5, 'comfort': +10},
            'kerja': {'energy': -10, 'hunger': +5, 'thirst': +5},
            'intim': {'energy': -15, 'temperature': +2, 'arousal': +20}
        }
        
        if activity in effects:
            for attr, change in effects[activity].items():
                if attr == 'energy':
                    sens['energy']['value'] = max(0, min(100, sens['energy']['value'] + change))
                elif attr == 'thirst':
                    sens['thirst']['value'] = max(0, min(100, sens['thirst']['value'] + change))
                elif attr == 'hunger':
                    sens['hunger']['value'] = max(0, min(100, sens['hunger']['value'] + change))
                elif attr == 'temperature':
                    sens['temperature']['value'] += change
                elif attr == 'comfort':
                    sens['comfort']['value'] = max(0, min(100, sens['comfort']['value'] + change))
    
    async def _apply_time_effects(self, user_id: int, hour: int):
        """Apply efek waktu ke sensasi"""
        sens = self.sensations[user_id]
        
        # Suhu berdasarkan waktu
        if 11 <= hour <= 14:  # Siang terik
            sens['temperature']['value'] += 2
        elif 0 <= hour <= 5:  # Malam dingin
            sens['temperature']['value'] -= 3
        
        # Energi berdasarkan waktu
        if 5 <= hour <= 10:  # Pagi segar
            sens['energy']['value'] = min(100, sens['energy']['value'] + 10)
        elif 13 <= hour <= 15:  # Siang ngantuk
            sens['energy']['value'] = max(0, sens['energy']['value'] - 10)
        elif 22 <= hour or hour <= 4:  # Malam capek
            sens['energy']['value'] = max(0, sens['energy']['value'] - 20)
    
    async def _update_feelings(self, user_id: int):
        """Update feeling berdasarkan nilai"""
        sens = self.sensations[user_id]
        
        # Temperature feeling
        if sens['temperature']['value'] < 20:
            sens['temperature']['feeling'] = 'cold'
        elif sens['temperature']['value'] > 30:
            sens['temperature']['feeling'] = 'hot'
        else:
            sens['temperature']['feeling'] = 'normal'
        
        # Energy feeling
        if sens['energy']['value'] > 80:
            sens['energy']['feeling'] = 'energetic'
        elif sens['energy']['value'] > 50:
            sens['energy']['feeling'] = 'normal'
        elif sens['energy']['value'] > 20:
            sens['energy']['feeling'] = 'tired'
        else:
            sens['energy']['feeling'] = 'exhausted'
        
        # Hunger feeling
        if sens['hunger']['value'] > 70:
            sens['hunger']['feeling'] = 'very_hungry'
        elif sens['hunger']['value'] > 40:
            sens['hunger']['feeling'] = 'hungry'
        else:
            sens['hunger']['feeling'] = 'normal'
        
        # Thirst feeling
        if sens['thirst']['value'] > 70:
            sens['thirst']['feeling'] = 'very_thirsty'
        elif sens['thirst']['value'] > 40:
            sens['thirst']['feeling'] = 'thirsty'
        else:
            sens['thirst']['feeling'] = 'normal'
        
        # Comfort feeling
        if sens['comfort']['value'] > 70:
            sens['comfort']['feeling'] = 'comfortable'
        else:
            sens['comfort']['feeling'] = 'uncomfortable'
        
        # Pain feeling
        if sens['pain']['value'] == 0:
            sens['pain']['feeling'] = 'none'
        elif sens['pain']['value'] < 30:
            sens['pain']['feeling'] = 'mild'
        elif sens['pain']['value'] < 60:
            sens['pain']['feeling'] = 'moderate'
        else:
            sens['pain']['feeling'] = 'severe'
    
    # =========================================================================
    # GET SENSATIONS
    # =========================================================================
    
    async def get_sensations(self, user_id: int) -> Dict:
        """
        Dapatkan semua sensasi saat ini
        
        Args:
            user_id: ID user
            
        Returns:
            Dict sensasi
        """
        if user_id not in self.sensations:
            return {}
        
        return self.sensations[user_id].copy()
    
    async def get_sensation_description(self, user_id: int) -> str:
        """
        Dapatkan deskripsi sensasi natural
        
        Args:
            user_id: ID user
            
        Returns:
            String deskripsi
        """
        sens = self.sensations[user_id]
        descriptions = []
        
        # Temperature
        if sens['temperature']['feeling'] == 'cold':
            descriptions.append("kedinginan")
        elif sens['temperature']['feeling'] == 'hot':
            descriptions.append("kegerahan")
        
        # Energy
        if sens['energy']['feeling'] == 'energetic':
            descriptions.append("segar")
        elif sens['energy']['feeling'] == 'tired':
            descriptions.append("capek")
        elif sens['energy']['feeling'] == 'exhausted':
            descriptions.append("lemes banget")
        
        # Hunger
        if sens['hunger']['feeling'] == 'very_hungry':
            descriptions.append("laper banget")
        elif sens['hunger']['feeling'] == 'hungry':
            descriptions.append("laper")
        
        # Thirst
        if sens['thirst']['feeling'] == 'very_thirsty':
            descriptions.append("haus banget")
        elif sens['thirst']['feeling'] == 'thirsty':
            descriptions.append("haus")
        
        # Comfort
        if sens['comfort']['feeling'] == 'uncomfortable':
            descriptions.append("gak nyaman")
        
        if not descriptions:
            return "biasa aja"
        
        return "lagi " + ", ".join(descriptions)
    
    # =========================================================================
    # ACTIONS
    # =========================================================================
    
    async def eat(self, user_id: int, food: str = "makanan"):
        """Makan untuk mengurangi lapar"""
        sens = self.sensations[user_id]
        sens['hunger']['value'] = max(0, sens['hunger']['value'] - 30)
        sens['energy']['value'] = min(100, sens['energy']['value'] + 10)
        sens['hunger']['last_change'] = time.time()
        
        await self._update_feelings(user_id)
        
        logger.info(f"🍽️ User {user_id} ate, hunger: {sens['hunger']['value']}")
    
    async def drink(self, user_id: int, drink: str = "air"):
        """Minum untuk mengurangi haus"""
        sens = self.sensations[user_id]
        sens['thirst']['value'] = max(0, sens['thirst']['value'] - 20)
        sens['thirst']['last_change'] = time.time()
        
        await self._update_feelings(user_id)
        
        logger.info(f"💧 User {user_id} drank, thirst: {sens['thirst']['value']}")
    
    async def sleep(self, user_id: int, hours: float = 1):
        """Tidur untuk memulihkan energi"""
        sens = self.sensations[user_id]
        sens['energy']['value'] = min(100, sens['energy']['value'] + (hours * 10))
        sens['hunger']['value'] = min(100, sens['hunger']['value'] + (hours * 5))
        sens['thirst']['value'] = min(100, sens['thirst']['value'] + (hours * 5))
        sens['energy']['last_change'] = time.time()
        
        await self._update_feelings(user_id)
        
        logger.info(f"😴 User {user_id} slept for {hours}h, energy: {sens['energy']['value']}")
    
    # =========================================================================
    # FORMAT UNTUK PROMPT
    # =========================================================================
    
    async def get_sensation_context(self, user_id: int) -> str:
        """
        Dapatkan konteks sensasi untuk prompt AI
        
        Args:
            user_id: ID user
            
        Returns:
            String konteks
        """
        sens = self.sensations[user_id]
        desc = await self.get_sensation_description(user_id)
        
        lines = [
            "🔋 **KONDISI FISIK:**",
            f"{desc}"
        ]
        
        # Detail tambahan
        details = []
        if sens['energy']['feeling'] in ['tired', 'exhausted']:
            details.append(f"energi {sens['energy']['value']}%")
        if sens['hunger']['feeling'] in ['hungry', 'very_hungry']:
            details.append(f"lapar {sens['hunger']['value']}%")
        if sens['thirst']['feeling'] in ['thirsty', 'very_thirsty']:
            details.append(f"haus {sens['thirst']['value']}%")
        
        if details:
            lines.append(f"({', '.join(details)})")
        
        return "\n".join(lines)


__all__ = ['PhysicalSensation', 'SensationType']
