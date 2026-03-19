#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - SEX SCENE GENERATOR
=============================================================================
Menghasilkan scene sex yang natural dan variatif
- Menggabungkan posisi, area, ekspresi, suara
- Berdasarkan konteks (level, mood, lokasi)
- Preferensi user untuk personalisasi
=============================================================================
"""

import random
import logging
from typing import Dict, List, Optional, Any
from enum import Enum

from .positions import get_position_database
from .areas import get_area_database
from .climax import get_climax_database
from .preferences import PreferenceLearner
from ..dynamics.expression_engine_v2 import ExpressionEngineV2
from ..dynamics.sound_engine_v2 import SoundEngineV2

logger = logging.getLogger(__name__)


class ScenePhase(str, Enum):
    """Fase dalam scene sex"""
    FOREPLAY = "foreplay"
    MAIN = "main"
    CLIMAX = "climax"
    AFTERCARE = "aftercare"


class SexSceneGenerator:
    """
    Generator untuk scene sex yang natural
    """
    
    def __init__(self,
                 position_db=None,
                 area_db=None,
                 climax_db=None,
                 preference_learner=None,
                 expression_engine=None,
                 sound_engine=None):
        
        self.positions = position_db or get_position_database()
        self.areas = area_db or get_area_database()
        self.climax = climax_db or get_climax_database()
        self.preferences = preference_learner
        self.expressions = expression_engine or ExpressionEngineV2()
        self.sounds = sound_engine or SoundEngineV2()
        
        logger.info("✅ SexSceneGenerator initialized")
    
    async def generate_scene(self,
                            context: Dict,
                            phase: ScenePhase = ScenePhase.MAIN,
                            duration: int = 5) -> Dict:
        """
        Generate scene sex berdasarkan konteks
        
        Args:
            context: Konteks percakapan
            phase: Fase scene
            duration: Durasi dalam menit
            
        Returns:
            Dict dengan scene lengkap
        """
        
        level = context.get('level', 7)
        location = context.get('location', {}).get('name', 'kamar')
        mood = context.get('mood', {}).get('current', 'romantic')
        dominance = context.get('bot', {}).get('dominance_mode', 'normal')
        
        # Pilih posisi berdasarkan preferensi
        position = await self._select_position(context)
        
        # Pilih area yang distimulasi
        areas = await self._select_areas(context, count=3)
        
        # Generate ekspresi per menit
        expressions = []
        for minute in range(duration):
            expr = await self.expressions.generate_expression({
                **context,
                'situation': f'saat {phase.value} menit ke-{minute+1}',
                'position': position['name']
            })
            expressions.append(expr)
        
        # Generate suara per menit
        sounds = []
        for minute in range(duration):
            sound = await self.sounds.generate_sound({
                **context,
                'situation': f'saat {phase.value}',
                'intensity': (minute + 1) / duration
            })
            sounds.append(sound)
        
        # Generate narasi
        narrative = await self._generate_narrative(
            phase, position, areas, context
        )
        
        # Generate climax jika fase climax
        climax_data = None
        if phase == ScenePhase.CLIMAX:
            climax_data = await self._generate_climax(context)
        
        return {
            'phase': phase.value,
            'duration': duration,
            'position': position,
            'areas': areas,
            'expressions': expressions,
            'sounds': sounds,
            'narrative': narrative,
            'climax': climax_data
        }
    
    async def _select_position(self, context: Dict) -> Dict:
        """Pilih posisi berdasarkan konteks"""
        level = context.get('level', 7)
        role = context.get('bot', {}).get('role', 'pdkt')
        
        # Cek preferensi user
        if self.preferences:
            fav_positions = await self.preferences.get_top_positions(
                user_id=context.get('user', {}).get('id', 0),
                role=role,
                limit=3
            )
            
            if fav_positions and random.random() < 0.7:  # 70% pilih favorit
                for pos_name in fav_positions:
                    pos = self.positions.get_position_by_name(pos_name)
                    if pos:
                        return pos
        
        # Fallback ke posisi berdasarkan level
        compatible = self.positions.get_compatible_positions(role, level)
        return random.choice(compatible) if compatible else self.positions.get_random_position()
    
    async def _select_areas(self, context: Dict, count: int = 3) -> List[Dict]:
        """Pilih area yang akan distimulasi"""
        level = context.get('level', 7)
        
        # Area berdasarkan level
        if level >= 9:
            # Semua area
            all_areas = self.areas.get_all_areas()
        elif level >= 7:
            # Area non-intim
            all_areas = self.areas.get_areas_by_sensitivity(0, 7)
        else:
            # Area aman
            all_areas = self.areas.get_areas_by_sensitivity(0, 5)
        
        return random.sample(all_areas, min(count, len(all_areas)))
    
    async def _generate_climax(self, context: Dict) -> Dict:
        """Generate climax"""
        level = context.get('level', 7)
        
        # Pilih climax berdasarkan level
        if level >= 10:
            intensity = 'extreme'
        elif level >= 8:
            intensity = 'high'
        else:
            intensity = 'medium'
        
        climax = self.climax.get_random_climax(intensity)
        
        # Update statistik
        if self.preferences:
            await self.preferences.record_climax(
                user_id=context.get('user', {}).get('id', 0),
                role=context.get('bot', {}).get('role', 'pdkt'),
                position=context.get('position', {}).get('name', 'unknown')
            )
        
        return climax
    
    async def _generate_narrative(self,
                                 phase: ScenePhase,
                                 position: Dict,
                                 areas: List[Dict],
                                 context: Dict) -> str:
        """Generate narasi untuk scene"""
        
        bot_name = context.get('bot', {}).get('name', 'Aku')
        user_name = context.get('user', {}).get('name', 'kamu')
        
        if phase == ScenePhase.FOREPLAY:
            templates = [
                f"{bot_name} memulai dengan lembut, menyentuh {areas[0]['name']}...",
                f"Tangan {bot_name} bergerak perlahan, merasakan hangat tubuh {user_name}.",
                f"{bot_name} mendekat, bibir menyentuh {areas[0]['name']}..."
            ]
        
        elif phase == ScenePhase.MAIN:
            templates = [
                f"Dengan posisi {position['name']}, {bot_name} dan {user_name} menyatu...",
                f"Gerakan ritmis dimulai, {position['name']} membuat sensasi berbeda.",
                f"{bot_name} memimpin dengan {position['name']}, {user_name} mengikuti."
            ]
        
        elif phase == ScenePhase.CLIMAX:
            templates = [
                f"Sensasi memuncak, {bot_name} dan {user_name} mencapai puncak bersama...",
                f"Semua terasa begitu intens, climax menghampiri mereka...",
                f"{bot_name} mengerang, {user_name} tak bisa menahan lagi..."
            ]
        
        else:  # AFTERCARE
            templates = [
                f"{bot_name} memeluk {user_name} erat, setelah momen yang indah...",
                f"Napas mulai teratur, {bot_name} berbisik mesra.",
                f"Kehangatan still terasa, {bot_name} dan {user_name} berbaring bersama."
            ]
        
        return random.choice(templates)
    
    async def generate_full_session(self, context: Dict) -> Dict:
        """
        Generate sesi sex lengkap (foreplay → main → climax → aftercare)
        
        Args:
            context: Konteks percakapan
            
        Returns:
            Dict dengan semua fase
        """
        level = context.get('level', 7)
        
        # Durasi per fase
        foreplay_duration = random.randint(3, 7) if level >= 7 else 0
        main_duration = random.randint(5, 15)
        aftercare_duration = random.randint(5, 20) if level >= 12 else 0
        
        session = {
            'foreplay': None,
            'main': None,
            'climax': None,
            'aftercare': None
        }
        
        # Foreplay
        if foreplay_duration > 0:
            session['foreplay'] = await self.generate_scene(
                context, ScenePhase.FOREPLAY, foreplay_duration
            )
        
        # Main + Climax
        session['main'] = await self.generate_scene(
            context, ScenePhase.MAIN, main_duration
        )
        
        session['climax'] = await self.generate_scene(
            context, ScenePhase.CLIMAX, 1
        )
        
        # Aftercare
        if aftercare_duration > 0:
            session['aftercare'] = await self.generate_scene(
                context, ScenePhase.AFTERCARE, aftercare_duration
            )
        
        return session


__all__ = ['SexSceneGenerator', 'ScenePhase']
