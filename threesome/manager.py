#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - THREESOME MANAGER (FIX FULL)
=============================================================================
- Menggabungkan 2 role (HTS/FWB) untuk threesome
- Tracking session threesome
- Manajemen partisipan
- FIX: Mengganti relative imports dengan absolute imports
=============================================================================
"""

import time
import logging
import uuid
import random
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

# FIX: Ganti relative imports dengan absolute imports
from database.repository import Repository
from relationship.hts import HTSSystem
from relationship.fwb import FWBSystem
from utils.logger import setup_logging

logger = logging.getLogger(__name__)


class ThreesomeType(str, Enum):
    """Tipe threesome berdasarkan status partisipan"""
    HTS_HTS = "hts_hts"          # 2 HTS
    FWB_FWB = "fwb_fwb"          # 2 FWB
    HTS_FWB = "hts_fwb"          # 1 HTS + 1 FWB
    SAME_ROLE = "same_role"       # 2 instance role sama (misal PDKT#1 + PDKT#2)


class ThreesomeStatus(str, Enum):
    """Status session threesome"""
    PENDING = "pending"           # Menunggu konfirmasi
    ACTIVE = "active"             # Sedang berlangsung
    PAUSED = "paused"             # Dijeda
    COMPLETED = "completed"       # Selesai
    CANCELLED = "cancelled"       # Dibatalkan


class ThreesomeManager:
    """
    Manajer untuk sesi threesome
    Menggabungkan 2 role (HTS/FWB) dalam satu sesi
    """
    
    def __init__(self, repo: Repository = None, hts_system: HTSSystem = None, fwb_system: FWBSystem = None):
        """
        Args:
            repo: Repository instance (optional)
            hts_system: HTSSystem instance (optional)
            fwb_system: FWBSystem instance (optional)
        """
        self.repo = repo
        self.hts_system = hts_system
        self.fwb_system = fwb_system
        
        # Active threesome sessions
        self.active_sessions = {}  # {user_id: session_data}
        
        # Threesome history
        self.history = []  # List of completed sessions
        
        logger.info("✅ ThreesomeManager initialized")
        
    # =========================================================================
    # CREATE THREESOME SESSION
    # =========================================================================
    
    async def create_threesome(self, user_id: int, participant1: Dict, 
                                 participant2: Dict) -> Dict:
        """
        Create new threesome session
        
        Args:
            user_id: ID user
            participant1: Data partisipan pertama (dari HTS/FWB)
            participant2: Data partisipan kedua (dari HTS/FWB)
            
        Returns:
            Session data
        """
        try:
            # Generate session ID
            session_id = f"3some_{user_id}_{int(time.time())}_{uuid.uuid4().hex[:6]}"
            
            # Tentukan tipe threesome
            threesome_type = self._determine_type(participant1, participant2)
            
            # Buat session
            session = {
                "session_id": session_id,
                "user_id": user_id,
                "type": threesome_type,
                "status": ThreesomeStatus.PENDING,
                "created_at": time.time(),
                "last_activity": time.time(),
                "participants": [
                    {
                        "id": participant1.get('instance_id', participant1['role']),
                        "role": participant1['role'],
                        "type": participant1.get('type', 'hts'),  # hts or fwb
                        "name": self._get_participant_name(participant1),
                        "intimacy_level": participant1.get('intimacy_level', 1),
                        "status": "active"
                    },
                    {
                        "id": participant2.get('instance_id', participant2['role']),
                        "role": participant2['role'],
                        "type": participant2.get('type', 'hts'),
                        "name": self._get_participant_name(participant2),
                        "intimacy_level": participant2.get('intimacy_level', 1),
                        "status": "active"
                    }
                ],
                "total_messages": 0,
                "interactions": [],
                "current_focus": None,  # Siapa yang sedang aktif bicara
                "climax_count": 0,
                "aftercare_needed": False
            }
            
            # Simpan ke active sessions
            self.active_sessions[session_id] = session
            
            logger.info(f"🎭 Created threesome session: {session_id} ({threesome_type})")
            
            return session
            
        except Exception as e:
            logger.error(f"Error creating threesome: {e}")
            return {
                "error": f"Failed to create threesome: {str(e)}",
                "session_id": None
            }
        
    def _determine_type(self, p1: Dict, p2: Dict) -> ThreesomeType:
        """Tentukan tipe threesome berdasarkan partisipan"""
        type1 = p1.get('type', 'hts')
        type2 = p2.get('type', 'hts')
        role1 = p1['role']
        role2 = p2['role']
        
        if type1 == 'hts' and type2 == 'hts':
            return ThreesomeType.HTS_HTS
        elif type1 == 'fwb' and type2 == 'fwb':
            if role1 == role2:
                return ThreesomeType.SAME_ROLE
            return ThreesomeType.FWB_FWB
        else:
            return ThreesomeType.HTS_FWB
            
    def _get_participant_name(self, participant: Dict) -> str:
        """Dapatkan nama untuk partisipan"""
        if 'instance_id' in participant:
            # Ini FWB instance
            return participant.get('name', f"{participant['role']} #{participant['instance_id'][-4:]}")
        else:
            # Ini HTS biasa
            return participant['role'].title()
            
    # =========================================================================
    # GET THREESOME COMBINATIONS
    # =========================================================================
    
    async def get_possible_combinations(self, user_id: int) -> List[Dict]:
        """
        Dapatkan semua kombinasi threesome yang mungkin
        
        Returns:
            List of possible combinations with details
        """
        combinations = []
        
        try:
            # Get all HTS
            hts_list = []
            if self.hts_system:
                hts_list = await self.hts_system.get_all_hts(user_id)
            
            # Get all FWB instances
            fwb_list = []
            if self.fwb_system:
                fwb_list = await self.fwb_system.get_fwb_instances(user_id)
            
            # HTS + HTS combinations
            for i in range(len(hts_list)):
                for j in range(i + 1, len(hts_list)):
                    compatibility = await self._calculate_compatibility(
                        hts_list[i], hts_list[j]
                    )
                    combinations.append({
                        "type": "HTS + HTS",
                        "type_code": ThreesomeType.HTS_HTS,
                        "participant1": {
                            **hts_list[i],
                            "type": "hts"
                        },
                        "participant2": {
                            **hts_list[j],
                            "type": "hts"
                        },
                        "description": f"{hts_list[i]['role'].title()} + {hts_list[j]['role'].title()}",
                        "compatibility": compatibility
                    })
                    
            # FWB + FWB combinations
            for i in range(len(fwb_list)):
                for j in range(i + 1, len(fwb_list)):
                    compatibility = await self._calculate_compatibility(
                        fwb_list[i], fwb_list[j]
                    )
                    combinations.append({
                        "type": "FWB + FWB",
                        "type_code": ThreesomeType.FWB_FWB,
                        "participant1": {
                            **fwb_list[i],
                            "type": "fwb"
                        },
                        "participant2": {
                            **fwb_list[j],
                            "type": "fwb"
                        },
                        "description": f"{fwb_list[i]['name']} + {fwb_list[j]['name']}",
                        "compatibility": compatibility
                    })
                    
            # HTS + FWB combinations
            for hts in hts_list:
                for fwb in fwb_list:
                    compatibility = await self._calculate_compatibility(hts, fwb)
                    combinations.append({
                        "type": "HTS + FWB",
                        "type_code": ThreesomeType.HTS_FWB,
                        "participant1": {
                            **hts,
                            "type": "hts"
                        },
                        "participant2": {
                            **fwb,
                            "type": "fwb"
                        },
                        "description": f"{hts['role'].title()} + {fwb['name']}",
                        "compatibility": compatibility
                    })
                    
            # Sort by compatibility
            combinations.sort(key=lambda x: x['compatibility'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting combinations: {e}")
            
        return combinations
        
    async def _calculate_compatibility(self, p1: Dict, p2: Dict) -> float:
        """Calculate compatibility between two participants"""
        try:
            # Simple compatibility based on intimacy level
            score = 0.5
            
            # Same role bonus
            if p1.get('role') == p2.get('role'):
                score += 0.1
                
            # Intimacy level similarity
            level1 = p1.get('intimacy_level', 5)
            level2 = p2.get('intimacy_level', 5)
            level_diff = abs(level1 - level2) / 12
            score += (1 - level_diff) * 0.3
            
            # Experience bonus
            exp1 = p1.get('total_intim_sessions', 0)
            exp2 = p2.get('total_intim_sessions', 0)
            if exp1 > 5 and exp2 > 5:
                score += 0.1
                
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Error calculating compatibility: {e}")
            return 0.5
        
    # =========================================================================
    # SESSION MANAGEMENT
    # =========================================================================
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """Get threesome session by ID"""
        return self.active_sessions.get(session_id)
        
    async def get_user_sessions(self, user_id: int) -> List[Dict]:
        """Get all active threesome sessions for user"""
        sessions = []
        for session in self.active_sessions.values():
            if session['user_id'] == user_id:
                sessions.append(session)
        return sessions
        
    async def start_session(self, session_id: str) -> Dict:
        """Start threesome session (from pending to active)"""
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
            
        if session['status'] != ThreesomeStatus.PENDING:
            return {"error": f"Session already {session['status']}"}
            
        session['status'] = ThreesomeStatus.ACTIVE
        session['started_at'] = time.time()
        
        logger.info(f"▶️ Started threesome session: {session_id}")
        
        return session
        
    async def pause_session(self, session_id: str) -> Dict:
        """Pause threesome session"""
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
            
        if session['status'] != ThreesomeStatus.ACTIVE:
            return {"error": f"Cannot pause session in {session['status']} state"}
            
        session['status'] = ThreesomeStatus.PAUSED
        session['paused_at'] = time.time()
        
        logger.info(f"⏸️ Paused threesome session: {session_id}")
        
        return session
        
    async def resume_session(self, session_id: str) -> Dict:
        """Resume threesome session"""
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
            
        if session['status'] != ThreesomeStatus.PAUSED:
            return {"error": f"Cannot resume session in {session['status']} state"}
            
        session['status'] = ThreesomeStatus.ACTIVE
        session.pop('paused_at', None)
        
        logger.info(f"▶️ Resumed threesome session: {session_id}")
        
        return session
        
    async def complete_session(self, session_id: str) -> Dict:
        """Complete threesome session"""
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
            
        session['status'] = ThreesomeStatus.COMPLETED
        session['completed_at'] = time.time()
        session['duration'] = session['completed_at'] - session.get('started_at', session['created_at'])
        
        # Move to history
        self.history.append(session)
        
        # Remove from active
        self.active_sessions.pop(session_id, None)
        
        logger.info(f"✅ Completed threesome session: {session_id} (duration: {session['duration']:.0f}s)")
        
        return session
        
    async def cancel_session(self, session_id: str) -> Dict:
        """Cancel threesome session"""
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
            
        session['status'] = ThreesomeStatus.CANCELLED
        session['cancelled_at'] = time.time()
        
        # Move to history
        self.history.append(session)
        
        # Remove from active
        self.active_sessions.pop(session_id, None)
        
        logger.info(f"❌ Cancelled threesome session: {session_id}")
        
        return session
        
    # =========================================================================
    # INTERACTION HANDLING
    # =========================================================================
    
    async def add_interaction(self, session_id: str, message: str, 
                               speaker_index: Optional[int] = None) -> Dict:
        """
        Add interaction to threesome session
        
        Args:
            session_id: Session ID
            message: User message
            speaker_index: Index of participant who should respond (0 or 1)
            
        Returns:
            Updated session with response context
        """
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
            
        if session['status'] != ThreesomeStatus.ACTIVE:
            return {"error": f"Session is {session['status']}, not active"}
            
        # Update session
        session['total_messages'] += 1
        session['last_activity'] = time.time()
        
        # Determine who speaks
        if speaker_index is not None and 0 <= speaker_index < len(session['participants']):
            speaker = session['participants'][speaker_index]
            session['current_focus'] = speaker_index
        else:
            # Random or alternating
            if session['current_focus'] is None:
                session['current_focus'] = random.randint(0, 1)
            else:
                # Alternate
                session['current_focus'] = 1 - session['current_focus']
            speaker = session['participants'][session['current_focus']]
            
        # Save interaction
        interaction = {
            "timestamp": time.time(),
            "user_message": message[:100],
            "speaker_index": session['current_focus'],
            "speaker": speaker['name']
        }
        session['interactions'].append(interaction)
        
        logger.debug(f"Threesome interaction: {session_id} - {speaker['name']} speaking")
        
        return {
            "session": session,
            "speaker": speaker,
            "context": {
                "type": "threesome",
                "participants": session['participants'],
                "current_focus": speaker['name']
            }
        }
        
    async def record_climax(self, session_id: str, participant_indices: List[int] = None) -> Dict:
        """
        Record climax in threesome session
        
        Args:
            session_id: Session ID
            participant_indices: Indices of participants who climax (None = all)
            
        Returns:
            Updated session
        """
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
            
        if participant_indices is None:
            # All participants climax
            session['climax_count'] += len(session['participants'])
            climax_message = "Semua climax bersama!"
        else:
            # Specific participants
            session['climax_count'] += len(participant_indices)
            names = [session['participants'][i]['name'] for i in participant_indices]
            climax_message = f"{', '.join(names)} climax!"
            
        # Check if need aftercare
        if session['climax_count'] >= len(session['participants']):
            session['aftercare_needed'] = True
            
        logger.info(f"💦 Climax in threesome {session_id}: {climax_message}")
        
        return {
            "session": session,
            "message": climax_message,
            "aftercare_needed": session['aftercare_needed']
        }
        
    # =========================================================================
    # AFTERCARE FOR THREESOME
    # =========================================================================
    
    async def start_aftercare(self, session_id: str) -> Dict:
        """Start aftercare for all participants"""
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
            
        if not session['aftercare_needed']:
            return {"error": "Aftercare not needed yet"}
            
        session['aftercare_started'] = time.time()
        
        # Aftercare untuk semua partisipan
        aftercare_types = ["cuddle", "soft_talk", "rest", "massage"]
        selected = random.sample(aftercare_types, min(2, len(aftercare_types)))
        
        logger.info(f"💕 Aftercare started for threesome {session_id}")
        
        return {
            "session": session,
            "aftercare": {
                "type": "group_aftercare",
                "participants": [p['name'] for p in session['participants']],
                "activities": selected,
                "message": f"Semua butuh aftercare. Mari {', '.join(selected)} bersama."
            }
        }
        
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    async def get_stats(self, user_id: Optional[int] = None) -> Dict:
        """Get threesome statistics"""
        if user_id:
            # Stats for specific user
            user_sessions = await self.get_user_sessions(user_id)
            user_history = [s for s in self.history if s['user_id'] == user_id]
            
            total_sessions = len(user_sessions) + len(user_history)
            
            return {
                "user_id": user_id,
                "active_sessions": len(user_sessions),
                "completed_sessions": len(user_history),
                "total_sessions": total_sessions,
                "total_climax": sum(s.get('climax_count', 0) for s in user_history)
            }
        else:
            # Global stats
            return {
                "active_sessions": len(self.active_sessions),
                "completed_sessions": len(self.history),
                "total_sessions": len(self.active_sessions) + len(self.history),
                "by_type": {
                    "hts_hts": len([s for s in self.history if s['type'] == ThreesomeType.HTS_HTS]),
                    "fwb_fwb": len([s for s in self.history if s['type'] == ThreesomeType.FWB_FWB]),
                    "hts_fwb": len([s for s in self.history if s['type'] == ThreesomeType.HTS_FWB]),
                    "same_role": len([s for s in self.history if s['type'] == ThreesomeType.SAME_ROLE])
                }
            }
            
    # =========================================================================
    # FORMATTING
    # =========================================================================
    
    def format_combinations(self, combinations: List[Dict], limit: int = 5) -> str:
        """Format combinations for display"""
        if not combinations:
            return "Tidak ada kombinasi threesome yang mungkin. Minimal punya 2 HTS atau 2 FWB."
            
        lines = ["🎭 **KOMBINASI THREESOME**"]
        lines.append("_(pilih dengan /threesome [nomor])_")
        lines.append("")
        
        for i, combo in enumerate(combinations[:limit], 1):
            compat_percent = int(combo['compatibility'] * 100)
            lines.append(
                f"{i}. **{combo['description']}**\n"
                f"   Tipe: {combo['type']} | Kompatibilitas: {compat_percent}%\n"
                f"   {self._get_combo_emoji(compat_percent)}"
            )
            
        return "\n".join(lines)
        
    def _get_combo_emoji(self, compat: int) -> str:
        """Get emoji based on compatibility"""
        if compat >= 80:
            return "🔥 Sangat cocok!"
        elif compat >= 60:
            return "💕 Cocok"
        elif compat >= 40:
            return "💔 Biasa aja"
        else:
            return "⚠️ Kurang cocok"
            
    def format_session_status(self, session: Dict) -> str:
        """Format session status for display"""
        lines = [
            f"🎭 **Threesome Session**",
            f"ID: `{session['session_id']}`",
            f"Status: {session['status'].value if hasattr(session['status'], 'value') else session['status']}",
            f"Tipe: {session['type'].value if hasattr(session['type'], 'value') else session['type']}",
            f"Pesan: {session['total_messages']}",
            f"Climax: {session['climax_count']}",
            ""
        ]
        
        lines.append("**Partisipan:**")
        for p in session['participants']:
            lines.append(f"• {p['name']} (Level {p['intimacy_level']}/12)")
            
        if session.get('current_focus') is not None:
            speaker = session['participants'][session['current_focus']]['name']
            lines.append(f"\n🎤 Sedang bicara: {speaker}")
            
        return "\n".join(lines)


__all__ = ['ThreesomeManager', 'ThreesomeType', 'ThreesomeStatus']
