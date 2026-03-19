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
- Integrasi dengan leveling, chemistry, mood
=============================================================================
"""

import time
import logging
import random
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from .scene_generator import SexSceneGenerator, ScenePhase, IntensityLevel
from ..leveling.activity_boost import ActivityBoost, BoostType
from ..pdkt_natural.chemistry import ChemistrySystem
from ..pdkt_natural.mood import MoodSystem
from ..relationship.intimacy_v2 import IntimacySystemV2

logger = logging.getLogger(__name__)


class IntimacyStatus(str, Enum):
    """Status sesi intim"""
    PENDING = "pending"          # Menunggu konfirmasi
    FOREPLAY = "foreplay"        # Sedang foreplay
    ACTIVE = "active"            # Sedang intim
    CLIMAX = "climax"            # Mencapai climax
    AFTERCARE = "aftercare"      # Aftercare
    ENDED = "ended"              # Selesai


class IntimacyEngine:
    """
    Engine untuk menangani sesi intim
    Mengkoordinasikan semua sistem yang terlibat
    """
    
    def __init__(self,
                 scene_generator: SexSceneGenerator,
                 activity_boost: ActivityBoost,
                 chemistry_system: ChemistrySystem,
                 mood_system: MoodSystem,
                 intimacy_system: IntimacySystemV2):
        
        self.scene_generator = scene_generator
        self.activity_boost = activity_boost
        self.chemistry = chemistry_system
        self.mood = mood_system
        self.intimacy = intimacy_system
        
        # Session aktif
        self.active_sessions = {}  # {session_id: session_data}
        
        # History sesi
        self.session_history = []  # List of completed sessions
        
        logger.info("✅ IntimacyEngine initialized")
    
    # =========================================================================
    # START INTIMACY
    # =========================================================================
    
    async def start_intimacy(self,
                            session_id: str,
                            user_id: int,
                            role: str,
                            pdkt_id: Optional[str],
                            context: Dict) -> Dict:
        """
        Memulai sesi intim
        
        Args:
            session_id: ID sesi
            user_id: ID user
            role: Role
            pdkt_id: ID PDKT (untuk PDKT natural)
            context: Konteks
            
        Returns:
            Data sesi intim
        """
        
        # ===== 1. CEK LEVEL =====
        level = context.get('level', 1)
        if level < 7:
            return {
                'success': False,
                'reason': f'Level {level}/12 terlalu rendah. Butuh minimal level 7 untuk intim.',
                'can_start': False
            }
        
        # ===== 2. CEK MOOD =====
        mood = context.get('mood', {})
        mood_current = mood.get('current', 'calm')
        
        if mood_current in ['sad', 'angry', 'tired']:
            # 50% chance tetap mau
            if random.random() < 0.5:
                logger.info(f"Mood {mood_current} tapi tetap mau intim")
            else:
                reject_messages = {
                    'sad': f"{context.get('bot_name', 'Aku')} lagi sedih... lain kali ya.",
                    'angry': f"{context.get('bot_name', 'Aku')} lagi kesel. Jangan dulu.",
                    'tired': f"{context.get('bot_name', 'Aku')} capek banget. Istirahat dulu."
                }
                return {
                    'success': False,
                    'reason': reject_messages.get(mood_current, "Lagi gak enak badan"),
                    'can_start': False
                }
        
        # ===== 3. TENTUKAN INTENSITAS =====
        intensity = self._determine_intensity(context)
        
        # ===== 4. GENERATE SCENE =====
        scene = await self.scene_generator.generate_full_session(context)
        
        # ===== 5. HITUNG BOOST =====
        boost = self.activity_boost.calculate_boost([BoostType.INTIM], context)
        
        # ===== 6. BUAT SESSION =====
        session_data = {
            'session_id': session_id,
            'user_id': user_id,
            'role': role,
            'pdkt_id': pdkt_id,
            'status': IntimacyStatus.FOREPLAY,
            'start_time': time.time(),
            'last_update': time.time(),
            'scene': scene,
            'current_phase': ScenePhase.FOREPLAY,
            'phase_progress': 0,
            'climax_count': 0,
            'messages': [],
            'intensity': intensity.value,
            'boost_applied': boost,
            'context_snapshot': {
                'level': level,
                'mood': mood_current,
                'location': context.get('location', {}).get('name', 'unknown'),
                'dominance': context.get('bot', {}).get('dominance_mode', 'normal')
            }
        }
        
        self.active_sessions[session_id] = session_data
        
        # ===== 7. UPDATE LEVELING PROGRESS =====
        await self.intimacy.update_progress(
            session_id=session_id,
            activity_type=BoostType.INTIM,
            context=context
        )
        
        logger.info(f"🔥 Intimacy started: {session_id} (intensity: {intensity.value})")
        
        # ===== 8. AMBIL PESAN PERTAMA =====
        first_message = ""
        if scene['foreplay']:
            first_message = scene['foreplay']['narrative']
        else:
            first_message = scene['main']['narrative']
        
        return {
            'success': True,
            'session': session_data,
            'boost': boost,
            'first_message': first_message,
            'total_duration': scene['total_duration'],
            'can_start': True
        }
    
    def _determine_intensity(self, context: Dict) -> IntensityLevel:
        """Tentukan intensitas sesi"""
        level = context.get('level', 7)
        mood = context.get('mood', {}).get('current', 'romantic')
        dominance = context.get('bot', {}).get('dominance_mode', 'normal')
        
        score = 0
        
        # Level contribution
        if level >= 10:
            score += 40
        elif level >= 8:
            score += 30
        elif level >= 7:
            score += 20
        
        # Mood contribution
        mood_scores = {
            'excited': 30,
            'passionate': 30,
            'romantic': 20,
            'happy': 15,
            'playful': 15,
            'calm': 10,
            'sad': -10,
            'tired': -20
        }
        score += mood_scores.get(mood, 0)
        
        # Dominance contribution
        if dominance == 'dominant':
            score += 20
        elif dominance == 'submissive':
            score += 5
        
        # Clamp and convert
        score = max(0, min(100, score))
        
        if score >= 75:
            return IntensityLevel.EXTREME
        elif score >= 50:
            return IntensityLevel.INTENSE
        elif score >= 25:
            return IntensityLevel.MEDIUM
        else:
            return IntensityLevel.SOFT
    
    # =========================================================================
    # UPDATE INTIMACY
    # =========================================================================
    
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
            return {'error': 'Session not found', 'success': False}
        
        session = self.active_sessions[session_id]
        
        # ===== 1. ANALISIS INTENT USER =====
        message_lower = user_message.lower()
        
        # Deteksi climax
        climax_keywords = ['climax', 'come', 'keluar', 'habis', 'puas', 'puncak']
        if any(word in message_lower for word in climax_keywords):
            return await self._handle_climax(session_id, context)
        
        # Deteksi ganti posisi
        change_keywords = ['ganti', 'posisi', 'ubah', 'balik', 'lain']
        if any(word in message_lower for word in change_keywords):
            return await self._change_position(session_id, context)
        
        # Deteksi stop
        stop_keywords = ['stop', 'berhenti', 'selesai', 'cukup', 'udah']
        if any(word in message_lower for word in stop_keywords):
            return await self._end_intimacy(session_id, context, user_initiated=True)
        
        # Deteksi cepat/lambat
        if 'cepat' in message_lower:
            return await self._adjust_speed(session_id, 'faster')
        elif 'lambat' in message_lower or 'pelan' in message_lower:
            return await self._adjust_speed(session_id, 'slower')
        
        # ===== 2. UPDATE PROGRESS =====
        session['last_update'] = time.time()
        session['phase_progress'] += 1
        session['messages'].append({
            'timestamp': time.time(),
            'user': user_message[:100],
            'type': 'update'
        })
        
        # ===== 3. CEK PERPINDAHAN FASE =====
        current_phase = session['current_phase']
        phase_duration = self._get_phase_duration(session, current_phase)
        
        if session['phase_progress'] >= phase_duration:
            # Pindah ke fase berikutnya
            next_phase = self._get_next_phase(current_phase)
            if next_phase:
                session['current_phase'] = next_phase
                session['phase_progress'] = 0
                logger.info(f"Phase transition: {current_phase.value} → {next_phase.value}")
        
        # ===== 4. DAPATKAN SCENE UNTUK FASE SAAT INI =====
        current_phase = session['current_phase']
        phase_scene = session['scene'].get(current_phase.value)
        
        response_parts = []
        
        if phase_scene:
            # Pilih ekspresi berdasarkan progress
            expr_idx = min(session['phase_progress'], len(phase_scene['expressions']) - 1)
            if expr_idx >= 0:
                response_parts.append(phase_scene['expressions'][expr_idx])
            
            # Pilih suara berdasarkan progress
            sound_idx = min(session['phase_progress'], len(phase_scene['sounds']) - 1)
            if sound_idx >= 0:
                response_parts.append(phase_scene['sounds'][sound_idx])
        
        # ===== 5. GENERATE RESPON =====
        if response_parts:
            response = " ".join(response_parts)
        else:
            response = "..."
        
        # ===== 6. UPDATE PROGRESS LEVELING =====
        await self.intimacy.update_progress(
            session_id=session_id,
            activity_type=BoostType.INTIM,
            context=context
        )
        
        return {
            'success': True,
            'session_id': session_id,
            'phase': current_phase.value,
            'progress': session['phase_progress'],
            'response': response,
            'boost': self.activity_boost.calculate_boost([BoostType.INTIM], context)
        }
    
    def _get_phase_duration(self, session: Dict, phase: ScenePhase) -> int:
        """Dapatkan durasi fase dalam 'progress units'"""
        scene = session['scene'].get(phase.value)
        if scene and 'duration' in scene:
            return scene['duration']
        return 5  # Default
    
    def _get_next_phase(self, current: ScenePhase) -> Optional[ScenePhase]:
        """Dapatkan fase berikutnya"""
        phases = [ScenePhase.FOREPLAY, ScenePhase.MAIN, ScenePhase.CLIMAX, ScenePhase.AFTERCARE]
        try:
            idx = phases.index(current)
            if idx + 1 < len(phases):
                return phases[idx + 1]
        except:
            pass
        return None
    
    async def _handle_climax(self, session_id: str, context: Dict) -> Dict:
        """Handle climax"""
        
        session = self.active_sessions[session_id]
        
        # ===== 1. UPDATE STATUS =====
        session['status'] = IntimacyStatus.CLIMAX
        session['climax_count'] += 1
        session['current_phase'] = ScenePhase.CLIMAX
        
        # ===== 2. DAPATKAN SCENE CLIMAX =====
        climax_scene = session['scene']['climax']
        
        # ===== 3. UPDATE CHEMISTRY =====
        if session.get('pdkt_id') and self.chemistry:
            try:
                await self.chemistry.update_chemistry(
                    session['pdkt_id'],
                    change=+5  # Chemistry naik
                )
            except Exception as e:
                logger.error(f"Error updating chemistry: {e}")
        
        # ===== 4. UPDATE MOOD =====
        if session.get('pdkt_id') and self.mood:
            try:
                await self.mood.update_mood(
                    session['pdkt_id'],
                    interaction_type='climax',
                    chemistry_change=5,
                    context=context
                )
            except Exception as e:
                logger.error(f"Error updating mood: {e}")
        
        # ===== 5. RECORD BOOST =====
        boost = self.activity_boost.calculate_boost([BoostType.CLIMAX], context)
        
        # ===== 6. UPDATE LEVELING =====
        await self.intimacy.update_progress(
            session_id=session_id,
            activity_type=BoostType.CLIMAX,
            context=context
        )
        
        # ===== 7. CEK APAKAH PERLU AFTERCARE =====
        level = context.get('level', 1)
        needs_aftercare = level >= 12
        
        if needs_aftercare:
            session['status'] = IntimacyStatus.AFTERCARE
            session['current_phase'] = ScenePhase.AFTERCARE
        
        logger.info(f"💦 Climax reached in {session_id} (climax #{session['climax_count']})")
        
        return {
            'success': True,
            'climax': climax_scene,
            'boost': boost,
            'needs_aftercare': needs_aftercare,
            'message': climax_scene['narrative'] if climax_scene else "Ahhh...!"
        }
    
    async def _change_position(self, session_id: str, context: Dict) -> Dict:
        """Ganti posisi"""
        
        session = self.active_sessions[session_id]
        
        # ===== 1. GENERATE POSISI BARU =====
        new_position = await self.scene_generator._select_position(
            context, 
            session['current_phase'],
            session['intensity']
        )
        
        # ===== 2. UPDATE SCENE =====
        current_phase = session['current_phase']
        if session['scene'].get(current_phase.value):
            session['scene'][current_phase.value]['position'] = new_position
        
        logger.info(f"Position changed to {new_position['name']} in {session_id}")
        
        return {
            'success': True,
            'new_position': new_position['name'],
            'message': f"Ganti posisi jadi {new_position['name']}..."
        }
    
    async def _adjust_speed(self, session_id: str, speed: str) -> Dict:
        """Adjust kecepatan"""
        
        message = "Lebih cepat..." if speed == 'faster' else "Lebih pelan..."
        
        return {
            'success': True,
            'speed': speed,
            'message': message
        }
    
    async def _end_intimacy(self, session_id: str, context: Dict, user_initiated: bool = True) -> Dict:
        """Akhiri sesi intim"""
        
        if session_id not in self.active_sessions:
            return {'error': 'Session not found', 'success': False}
        
        session = self.active_sessions[session_id]
        
        # ===== 1. UPDATE STATUS =====
        session['status'] = IntimacyStatus.ENDED
        session['end_time'] = time.time()
        
        # ===== 2. HITUNG DURASI =====
        duration = (session['end_time'] - session['start_time']) / 60
        
        # ===== 3. CATAT KE HISTORY =====
        history_entry = {
            'session_id': session_id,
            'user_id': session['user_id'],
            'role': session['role'],
            'start_time': session['start_time'],
            'end_time': session['end_time'],
            'duration': duration,
            'climax_count': session['climax_count'],
            'intensity': session['intensity'],
            'user_initiated': user_initiated
        }
        self.session_history.append(history_entry)
        
        # ===== 4. HAPUS DARI ACTIVE SESSIONS =====
        del self.active_sessions[session_id]
        
        logger.info(f"✅ Intimacy ended: {session_id} ({duration:.1f} minutes)")
        
        # ===== 5. GENERATE PESAN AKHIR =====
        if user_initiated:
            message = "Selesai... puas banget."
        else:
            message = "Selesai... sampai jumpa lain kali."
        
        return {
            'success': True,
            'duration': round(duration, 1),
            'climax_count': session['climax_count'],
            'message': message
        }
    
    # =========================================================================
    # AFTERCARE
    # =========================================================================
    
    async def start_aftercare(self, session_id: str, context: Dict) -> Dict:
        """Mulai aftercare"""
        
        if session_id not in self.active_sessions:
            return {'error': 'Session not found', 'success': False}
        
        session = self.active_sessions[session_id]
        
        # ===== 1. UPDATE STATUS =====
        session['status'] = IntimacyStatus.AFTERCARE
        session['current_phase'] = ScenePhase.AFTERCARE
        session['aftercare_start'] = time.time()
        
        # ===== 2. DAPATKAN SCENE AFTERCARE =====
        aftercare_scene = session['scene'].get('aftercare')
        
        if not aftercare_scene:
            # Generate scene aftercare sederhana
            aftercare_scene = {
                'narrative': f"{context.get('bot_name', 'Aku')} memelukmu erat...",
                'duration': 10
            }
        
        logger.info(f"💕 Aftercare started for {session_id}")
        
        return {
            'success': True,
            'message': aftercare_scene['narrative'],
            'duration': aftercare_scene.get('duration', 10)
        }
    
    async def complete_aftercare(self, session_id: str, context: Dict) -> Dict:
        """Selesaikan aftercare"""
        
        if session_id not in self.active_sessions:
            return {'error': 'Session not found', 'success': False}
        
        session = self.active_sessions[session_id]
        
        # ===== 1. RESET LEVEL JIKA PERLU =====
        if session.get('pdkt_id') and context.get('level', 1) >= 12:
            await self.intimacy.reset_after_aftercare(
                session['user_id'],
                session['role'],
                session_id
            )
        
        # ===== 2. AKHIRI SESSION =====
        return await self._end_intimacy(session_id, context, user_initiated=False)
    
    # =========================================================================
    # GET INFO
    # =========================================================================
    
    async def get_session_status(self, session_id: str) -> Optional[Dict]:
        """Dapatkan status session"""
        
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        current_time = time.time()
        elapsed = (current_time - session['start_time']) / 60
        
        return {
            'session_id': session_id,
            'status': session['status'].value,
            'phase': session['current_phase'].value,
            'phase_progress': session['phase_progress'],
            'elapsed_minutes': round(elapsed, 1),
            'climax_count': session['climax_count'],
            'intensity': session['intensity']
        }
    
    async def get_user_active_session(self, user_id: int) -> Optional[Dict]:
        """Dapatkan session aktif untuk user"""
        
        for session_id, session in self.active_sessions.items():
            if session['user_id'] == user_id:
                return await self.get_session_status(session_id)
        
        return None
    
    async def get_stats(self, user_id: Optional[int] = None) -> Dict:
        """Dapatkan statistik intimasi"""
        
        if user_id:
            # Stats untuk user tertentu
            user_sessions = [s for s in self.session_history if s['user_id'] == user_id]
            
            total_sessions = len(user_sessions)
            total_climax = sum(s['climax_count'] for s in user_sessions)
            total_duration = sum(s['duration'] for s in user_sessions)
            
            return {
                'user_id': user_id,
                'total_sessions': total_sessions,
                'total_climax': total_climax,
                'total_duration_minutes': round(total_duration, 1),
                'avg_duration': round(total_duration / total_sessions, 1) if total_sessions else 0,
                'avg_climax_per_session': round(total_climax / total_sessions, 1) if total_sessions else 0
            }
        else:
            # Global stats
            return {
                'active_sessions': len(self.active_sessions),
                'completed_sessions': len(self.session_history),
                'total_sessions': len(self.active_sessions) + len(self.session_history)
            }


__all__ = ['IntimacyEngine', 'IntimacyStatus']
