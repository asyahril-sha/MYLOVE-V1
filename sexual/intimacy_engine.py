#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - INTIMACY ENGINE
=============================================================================
Engine untuk menangani sesi intim
- Memulai sesi intim
- Update progress selama sesi
- Handle climax
- Trigger aftercare
=============================================================================
"""

import time
import logging
import asyncio
from typing import Dict, List, Optional, Any
from enum import Enum

from .scene_generator import SexSceneGenerator, ScenePhase
from ..leveling.activity_boost import ActivityBoost, BoostType
from ..pdkt_natural.chemistry import ChemistrySystem
from ..pdkt_natural.mood import MoodSystem

logger = logging.getLogger(__name__)


class IntimacyStatus(str, Enum):
    """Status sesi intim"""
    PENDING = "pending"      # Menunggu konfirmasi
    FOREPLAY = "foreplay"    # Sedang foreplay
    ACTIVE = "active"        # Sedang intim
    CLIMAX = "climax"        # Mencapai climax
    AFTERCARE = "aftercare"  # Aftercare
    ENDED = "ended"          # Selesai


class IntimacyEngine:
    """
    Engine untuk menangani sesi intim
    """
    
    def __init__(self,
                 scene_generator: SexSceneGenerator,
                 activity_boost: ActivityBoost,
                 chemistry_system: ChemistrySystem,
                 mood_system: MoodSystem):
        
        self.scene_generator = scene_generator
        self.activity_boost = activity_boost
        self.chemistry = chemistry_system
        self.mood = mood_system
        
        # Session aktif
        self.active_sessions = {}  # {session_id: session_data}
        
        logger.info("✅ IntimacyEngine initialized")
    
    async def start_intimacy(self,
                            session_id: str,
                            user_id: int,
                            role: str,
                            context: Dict) -> Dict:
        """
        Memulai sesi intim
        
        Args:
            session_id: ID sesi
            user_id: ID user
            role: Role
            context: Konteks
            
        Returns:
            Data sesi intim
        """
        
        # Cek level
        level = context.get('level', 1)
        if level < 7:
            return {
                'success': False,
                'reason': f'Level {level}/12 terlalu rendah. Butuh minimal level 7.'
            }
        
        # Cek mood
        mood = context.get('mood', {})
        if mood.get('current') in ['sad', 'angry', 'tired']:
            if random.random() < 0.5:  # 50% chance tetap mau
                pass
            else:
                return {
                    'success': False,
                    'reason': f"{context.get('bot', {}).get('name', 'Aku')} lagi {mood.get('description', 'tidak enak')}."
                }
        
        # Generate scene
        scene = await self.scene_generator.generate_full_session(context)
        
        # Simpan session
        session_data = {
            'session_id': session_id,
            'user_id': user_id,
            'role': role,
            'status': IntimacyStatus.FOREPLAY,
            'start_time': time.time(),
            'last_update': time.time(),
            'scene': scene,
            'current_phase': ScenePhase.FOREPLAY,
            'progress': 0,
            'climax_count': 0,
            'messages': []
        }
        
        self.active_sessions[session_id] = session_data
        
        # Record activity boost
        boost = self.activity_boost.calculate_boost([BoostType.INTIM], context)
        
        logger.info(f"🔥 Intimacy started: {session_id}")
        
        return {
            'success': True,
            'session': session_data,
            'boost': boost,
            'first_message': scene['foreplay']['narrative'] if scene['foreplay'] else scene['main']['narrative']
        }
    
    async def update_intimacy(self,
                             session_id: str,
                             user_message: str,
                             context: Dict) -> Dict:
        """
        Update sesi intim berdasarkan pesan user
        
        Args:
            session_id: ID sesi
            user_message: Pesan user
            context: Konteks
            
        Returns:
            Update sesi
        """
        
        if session_id not in self.active_sessions:
            return {'error': 'Session not found'}
        
        session = self.active_sessions[session_id]
        
        # Analisis intent user
        message_lower = user_message.lower()
        
        # Deteksi climax
        if any(word in message_lower for word in ['climax', 'come', 'keluar', 'habis', 'puas']):
            return await self._handle_climax(session_id, context)
        
        # Deteksi ganti posisi
        if any(word in message_lower for word in ['ganti', 'posisi', 'ubah', 'balik']):
            return await self._change_position(session_id, context)
        
        # Deteksi stop
        if any(word in message_lower for word in ['stop', 'berhenti', 'selesai', 'cukup']):
            return await self._end_intimacy(session_id, context)
        
        # Lanjut normal
        session['last_update'] = time.time()
        session['progress'] += 1
        
        # Dapatkan scene untuk fase saat ini
        current_phase = session['current_phase']
        phase_scene = session['scene'].get(current_phase.value)
        
        if phase_scene:
            # Pilih ekspresi dan suara berdasarkan progress
            expr_idx = min(session['progress'], len(phase_scene['expressions']) - 1)
            sound_idx = min(session['progress'], len(phase_scene['sounds']) - 1)
            
            response = f"{phase_scene['expressions'][expr_idx]} {phase_scene['sounds'][sound_idx]}"
        else:
            response = "..."
        
        return {
            'session_id': session_id,
            'phase': current_phase.value,
            'progress': session['progress'],
            'response': response,
            'boost': self.activity_boost.calculate_boost([BoostType.INTIM], context)
        }
    
    async def _handle_climax(self, session_id: str, context: Dict) -> Dict:
        """Handle climax"""
        
        session = self.active_sessions[session_id]
        
        # Update status
        session['status'] = IntimacyStatus.CLIMAX
        session['climax_count'] += 1
        
        # Dapatkan scene climax
        climax_scene = session['scene']['climax']
        
        # Update chemistry
        if hasattr(self.chemistry, 'update_chemistry'):
            await self.chemistry.update_chemistry(
                context.get('pdkt_id'),
                change=+5  # Chemistry naik
            )
        
        # Update mood
        if hasattr(self.mood, 'update_mood'):
            await self.mood.update_mood(
                context.get('pdkt_id'),
                interaction_type='climax',
                chemistry_change=5,
                context=context
            )
        
        # Record boost
        boost = self.activity_boost.calculate_boost([BoostType.CLIMAX], context)
        
        # Cek apakah perlu aftercare
        level = context.get('level', 1)
        needs_aftercare = level >= 12
        
        if needs_aftercare:
            session['status'] = IntimacyStatus.AFTERCARE
            session['current_phase'] = ScenePhase.AFTERCARE
        
        logger.info(f"💦 Climax reached in {session_id}")
        
        return {
            'success': True,
            'climax': climax_scene,
            'boost': boost,
            'needs_aftercare': needs_aftercare,
            'message': climax_scene['narrative']
        }
    
    async def _change_position(self, session_id: str, context: Dict) -> Dict:
        """Ganti posisi"""
        
        session = self.active_sessions[session_id]
        
        # Generate posisi baru
        new_position = await self.scene_generator._select_position(context)
        
        session['scene']['main']['position'] = new_position
        
        return {
            'success': True,
            'new_position': new_position['name'],
            'message': f"Ganti posisi jadi {new_position['name']}..."
        }
    
    async def _end_intimacy(self, session_id: str, context: Dict) -> Dict:
        """Akhiri sesi intim"""
        
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session['status'] = IntimacyStatus.ENDED
            session['end_time'] = time.time()
            
            duration = (session['end_time'] - session['start_time']) / 60
            
            del self.active_sessions[session_id]
            
            logger.info(f"✅ Intimacy ended: {session_id} ({duration:.1f} minutes)")
            
            return {
                'success': True,
                'duration': duration,
                'climax_count': session['climax_count'],
                'message': "Selesai... puas banget."
            }
        
        return {'error': 'Session not found'}


__all__ = ['IntimacyEngine', 'IntimacyStatus']
