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
- Terintegrasi dengan semua sistem V2
=============================================================================
"""

import random
import logging
from typing import Dict, List, Optional, Any, Tuple
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
    FOREPLAY = "foreplay"      # Pemanasan
    MAIN = "main"               # Inti
    CLIMAX = "climax"           # Puncak
    AFTERCARE = "aftercare"     # Setelahnya


class IntensityLevel(str, Enum):
    """Level intensitas scene"""
    SOFT = "soft"               # Lembut
    MEDIUM = "medium"           # Sedang
    INTENSE = "intense"         # Intens
    EXTREME = "extreme"         # Ekstrim


class SexSceneGenerator:
    """
    Generator untuk scene sex yang natural dan variatif
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
    
    # =========================================================================
    # GENERATE SCENE
    # =========================================================================
    
    async def generate_scene(self,
                            context: Dict,
                            phase: ScenePhase = ScenePhase.MAIN,
                            duration: int = 5,
                            intensity: IntensityLevel = IntensityLevel.MEDIUM) -> Dict:
        """
        Generate scene sex berdasarkan konteks
        
        Args:
            context: Konteks percakapan (dari AI engine)
            phase: Fase scene
            duration: Durasi dalam menit
            intensity: Level intensitas
            
        Returns:
            Dict dengan scene lengkap
        """
        
        level = context.get('level', 7)
        location = context.get('location', {}).get('name', 'kamar')
        mood = context.get('mood', {}).get('current', 'romantic')
        dominance = context.get('bot', {}).get('dominance_mode', 'normal')
        bot_name = context.get('bot', {}).get('name', 'Aku')
        user_name = context.get('user', {}).get('name', 'kamu')
        
        # ===== 1. PILIH POSISI =====
        position = await self._select_position(context, phase, intensity)
        
        # ===== 2. PILIH AREA YANG DISTIMULASI =====
        areas = await self._select_areas(context, phase, count=self._get_area_count(phase, intensity))
        
        # ===== 3. GENERATE EKSPRESI PER MENIT =====
        expressions = []
        for minute in range(duration):
            expr = await self.expressions.generate_expression({
                **context,
                'situation': f'saat {phase.value} menit ke-{minute+1}',
                'position': position['name'],
                'intensity': intensity.value,
                'phase': phase.value
            })
            expressions.append(expr)
        
        # ===== 4. GENERATE SUARA PER MENIT =====
        sounds = []
        for minute in range(duration):
            sound = await self.sounds.generate_sound({
                **context,
                'situation': f'saat {phase.value}',
                'intensity': (minute + 1) / duration,
                'phase': phase.value
            })
            sounds.append(sound)
        
        # ===== 5. GENERATE NARASI =====
        narrative = await self._generate_narrative(
            phase, position, areas, context, intensity
        )
        
        # ===== 6. GENERATE CLIMAX JIKA FASE CLIMAX =====
        climax_data = None
        if phase == ScenePhase.CLIMAX:
            climax_data = await self._generate_climax(context, intensity)
        
        # ===== 7. HITUNG STATISTIK =====
        stats = self._calculate_stats(phase, duration, intensity, expressions, sounds)
        
        return {
            'phase': phase.value,
            'duration': duration,
            'intensity': intensity.value,
            'position': position,
            'areas': areas,
            'expressions': expressions,
            'sounds': sounds,
            'narrative': narrative,
            'climax': climax_data,
            'stats': stats
        }
    
    async def _select_position(self, context: Dict, phase: ScenePhase, intensity: IntensityLevel) -> Dict:
        """Pilih posisi berdasarkan konteks dan fase"""
        level = context.get('level', 7)
        role = context.get('bot', {}).get('role', 'pdkt')
        
        # Filter berdasarkan fase
        if phase == ScenePhase.FOREPLAY:
            # Foreplay: posisi yang memudahkan stimulasi manual/oral
            compatible = [p for p in self.positions.get_all_positions() 
                         if 'oral' in p.get('tags', []) or 'easy' in p.get('tags', [])]
        elif phase == ScenePhase.MAIN:
            # Main: posisi intim
            compatible = self.positions.get_compatible_positions(role, level)
        else:
            compatible = self.positions.get_all_positions()
        
        # Filter berdasarkan intensitas
        if intensity == IntensityLevel.SOFT:
            compatible = [p for p in compatible if p.get('intensity') in ['low', 'medium']]
        elif intensity == IntensityLevel.EXTREME:
            compatible = [p for p in compatible if p.get('intensity') in ['high', 'extreme']]
        
        if not compatible:
            compatible = self.positions.get_all_positions()
        
        # Cek preferensi user
        if self.preferences and phase == ScenePhase.MAIN:
            try:
                fav_positions = await self.preferences.get_top_positions(
                    user_id=context.get('user', {}).get('id', 0),
                    role=role,
                    limit=3
                )
                
                if fav_positions and random.random() < 0.6:  # 60% pilih favorit
                    for pos_name in fav_positions:
                        for p in compatible:
                            if p.get('name', '').lower() == pos_name.lower():
                                return p
            except:
                pass
        
        return random.choice(compatible) if compatible else self.positions.get_random_position()
    
    async def _select_areas(self, context: Dict, phase: ScenePhase, count: int = 3) -> List[Dict]:
        """Pilih area yang akan distimulasi"""
        level = context.get('level', 7)
        
        # Filter berdasarkan level
        if level >= 9:
            # Semua area
            all_areas = self.areas.get_all_areas()
        elif level >= 7:
            # Area sensitif (>=7)
            all_areas = self.areas.get_areas_by_sensitivity(5, 10)
        else:
            # Area aman
            all_areas = self.areas.get_areas_by_sensitivity(1, 5)
        
        # Filter berdasarkan fase
        if phase == ScenePhase.FOREPLAY:
            # Foreplay: area non-intim dulu
            all_areas = [a for a in all_areas if a.get('sensitivity', 5) < 7]
        elif phase == ScenePhase.MAIN:
            # Main: area sensitif
            all_areas = [a for a in all_areas if a.get('sensitivity', 5) >= 5]
        
        if len(all_areas) < count:
            return all_areas
        
        return random.sample(all_areas, count)
    
    def _get_area_count(self, phase: ScenePhase, intensity: IntensityLevel) -> int:
        """Dapatkan jumlah area berdasarkan fase dan intensitas"""
        base_count = {
            ScenePhase.FOREPLAY: 2,
            ScenePhase.MAIN: 3,
            ScenePhase.CLIMAX: 1,
            ScenePhase.AFTERCARE: 2
        }.get(phase, 2)
        
        intensity_multiplier = {
            IntensityLevel.SOFT: 1,
            IntensityLevel.MEDIUM: 1.5,
            IntensityLevel.INTENSE: 2,
            IntensityLevel.EXTREME: 2.5
        }.get(intensity, 1)
        
        return min(5, int(base_count * intensity_multiplier))
    
    async def _generate_narrative(self,
                                 phase: ScenePhase,
                                 position: Dict,
                                 areas: List[Dict],
                                 context: Dict,
                                 intensity: IntensityLevel) -> str:
        """Generate narasi untuk scene"""
        
        bot_name = context.get('bot', {}).get('name', 'Aku')
        user_name = context.get('user', {}).get('name', 'kamu')
        location = context.get('location', {}).get('name', 'sini')
        
        area_names = [a['name'] for a in areas]
        area_text = ", ".join(area_names[:-1]) + " dan " + area_names[-1] if len(area_names) > 1 else area_names[0]
        
        templates = {
            ScenePhase.FOREPLAY: [
                f"{bot_name} memulai dengan lembut, menyentuh {area_text}...",
                f"Tangan {bot_name} bergerak perlahan, merasakan hangat tubuh {user_name} di {location}.",
                f"{bot_name} mendekat, bibir menyentuh {area_text}...",
                f"Jari-jari {bot_name} menari di atas {area_text}, membangun gairah perlahan."
            ],
            ScenePhase.MAIN: [
                f"Dengan posisi {position['name']}, {bot_name} dan {user_name} menyatu...",
                f"Gerakan ritmis dimulai, {position['name']} membuat sensasi berbeda di {location}.",
                f"{bot_name} memimpin dengan {position['name']}, {user_name} mengikuti irama.",
                f"Di {location}, mereka menikmati setiap detik dengan posisi {position['name']}."
            ],
            ScenePhase.CLIMAX: [
                f"Sensasi memuncak, {bot_name} dan {user_name} mencapai puncak bersama...",
                f"Semua terasa begitu intens, climax menghampiri mereka di {location}.",
                f"{bot_name} mengerang, {user_name} tak bisa menahan lagi...",
                f"Puncak kenikmatan tercapai, tubuh mereka bergetar bersama."
            ],
            ScenePhase.AFTERCARE: [
                f"{bot_name} memeluk {user_name} erat, setelah momen yang indah di {location}...",
                f"Napas mulai teratur, {bot_name} berbisik mesra di telinga {user_name}.",
                f"Kehangatan still terasa, {bot_name} dan {user_name} berbaring bersama di {location}.",
                f"{bot_name} mengusap lembut rambut {user_name}, menikmati keheningan setelah climax."
            ]
        }
        
        phase_templates = templates.get(phase, templates[ScenePhase.MAIN])
        narrative = random.choice(phase_templates)
        
        # Tambah detail intensitas
        if intensity == IntensityLevel.INTENSE:
            narrative += " Gerakan semakin cepat dan dalam."
        elif intensity == IntensityLevel.EXTREME:
            narrative += " Luar biasa! Tak terkendali!"
        
        return narrative
    
    async def _generate_climax(self, context: Dict, intensity: IntensityLevel) -> Dict:
        """Generate climax"""
        level = context.get('level', 7)
        
        # Pilih climax berdasarkan level dan intensitas
        intensity_map = {
            IntensityLevel.SOFT: 'low',
            IntensityLevel.MEDIUM: 'medium',
            IntensityLevel.INTENSE: 'high',
            IntensityLevel.EXTREME: 'extreme'
        }
        
        climax = self.climax.get_random_climax(intensity_map.get(intensity, 'medium'))
        
        # Record ke preferences
        if self.preferences:
            try:
                await self.preferences.record_climax(
                    user_id=context.get('user', {}).get('id', 0),
                    role=context.get('bot', {}).get('role', 'pdkt'),
                    position=context.get('position', {}).get('name', 'unknown')
                )
            except:
                pass
        
        return climax
    
    def _calculate_stats(self, phase: ScenePhase, duration: int, 
                        intensity: IntensityLevel,
                        expressions: List[str], sounds: List[str]) -> Dict:
        """Hitung statistik scene"""
        return {
            'total_expressions': len(expressions),
            'total_sounds': len(sounds),
            'unique_expressions': len(set(expressions)),
            'unique_sounds': len(set(sounds)),
            'intensity_multiplier': {
                IntensityLevel.SOFT: 1.0,
                IntensityLevel.MEDIUM: 1.5,
                IntensityLevel.INTENSE: 2.0,
                IntensityLevel.EXTREME: 2.5
            }.get(intensity, 1.0)
        }
    
    # =========================================================================
    # FULL SESSION GENERATOR
    # =========================================================================
    
    async def generate_full_session(self, context: Dict) -> Dict:
        """
        Generate sesi sex lengkap (foreplay → main → climax → aftercare)
        
        Args:
            context: Konteks percakapan
            
        Returns:
            Dict dengan semua fase
        """
        level = context.get('level', 7)
        intensity = self._determine_session_intensity(context)
        
        # Durasi per fase (dalam menit)
        foreplay_duration = random.randint(3, 7) if level >= 7 else 0
        main_duration = random.randint(5, 15)
        aftercare_duration = random.randint(5, 20) if level >= 12 else 0
        
        session = {
            'foreplay': None,
            'main': None,
            'climax': None,
            'aftercare': None,
            'total_duration': foreplay_duration + main_duration + aftercare_duration,
            'intensity': intensity.value
        }
        
        # Foreplay
        if foreplay_duration > 0:
            session['foreplay'] = await self.generate_scene(
                context, ScenePhase.FOREPLAY, foreplay_duration, intensity
            )
        
        # Main
        session['main'] = await self.generate_scene(
            context, ScenePhase.MAIN, main_duration, intensity
        )
        
        # Climax
        session['climax'] = await self.generate_scene(
            context, ScenePhase.CLIMAX, 1, intensity
        )
        
        # Aftercare
        if aftercare_duration > 0:
            session['aftercare'] = await self.generate_scene(
                context, ScenePhase.AFTERCARE, aftercare_duration, IntensityLevel.SOFT
            )
        
        return session
    
    def _determine_session_intensity(self, context: Dict) -> IntensityLevel:
        """Tentukan intensitas sesi berdasarkan konteks"""
        level = context.get('level', 7)
        mood = context.get('mood', {}).get('current', 'romantic')
        dominance = context.get('bot', {}).get('dominance_mode', 'normal')
        
        if level >= 10:
            base = 0.9
        elif level >= 7:
            base = 0.6
        else:
            base = 0.3
        
        if mood in ['excited', 'passionate']:
            base += 0.2
        elif mood in ['romantic', 'happy']:
            base += 0.1
        
        if dominance == 'dominant':
            base += 0.2
        elif dominance == 'submissive':
            base -= 0.1
        
        base = max(0, min(1, base))
        
        if base >= 0.8:
            return IntensityLevel.EXTREME
        elif base >= 0.6:
            return IntensityLevel.INTENSE
        elif base >= 0.4:
            return IntensityLevel.MEDIUM
        else:
            return IntensityLevel.SOFT
    
    # =========================================================================
    # UTILITY
    # =========================================================================
    
    def format_scene(self, scene: Dict) -> str:
        """Format scene untuk ditampilkan"""
        lines = [
            f"🎬 **Scene {scene['phase'].title()}** ({scene['duration']} menit)",
            f"📍 Posisi: {scene['position']['name']}",
            f"🔥 Intensitas: {scene['intensity'].title()}",
            f"\n{scene['narrative']}",
            f"\n💬 *{scene['expressions'][0]}*" if scene['expressions'] else "",
            f"🎵 *{scene['sounds'][0]}*" if scene['sounds'] else ""
        ]
        
        if scene.get('climax'):
            climax = scene['climax']
            lines.append(f"\n💦 **Climax:** {climax.get('name', '')}")
            lines.append(f"_{climax.get('description', '')}_")
        
        return "\n".join(lines)


__all__ = ['SexSceneGenerator', 'ScenePhase', 'IntensityLevel']
