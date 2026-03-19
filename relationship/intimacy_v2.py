#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - INTIMACY SYSTEM V2 (TIME-BASED)
=============================================================================
- Level berdasarkan DURASI PERCAKAPAN
- 60 menit → Level 7 (bisa intim)
- 120 menit → Level 11 (deep connection)
- FIX: Tambah get_status untuk progress command
=============================================================================
"""

import time
import logging
import random
import math
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from config import settings
from ..leveling.time_based_v2 import TimeBasedLevelingV2
from ..leveling.activity_boost import ActivityBoost, BoostType

logger = logging.getLogger(__name__)


class IntimacySystemV2:
    """
    Sistem intimacy level berdasarkan DURASI PERCAKAPAN
    """
    
    def __init__(self, relationship_memory=None, consolidation=None):
        self.relationship_memory = relationship_memory
        self.consolidation = consolidation
        
        # Level definitions
        self.level_names = {
            1: "Malu-malu",
            2: "Mulai terbuka",
            3: "Goda-godaan",
            4: "Dekat",
            5: "Sayang",
            6: "PACAR/PDKT",
            7: "Nyaman",
            8: "Eksplorasi",
            9: "Bergairah",
            10: "Passionate",
            11: "Deep Connection",
            12: "Aftercare"
        }
        
        # Level descriptions
        self.level_descriptions = {
            1: "Baru kenal, masih canggung. Belum berani buka suara.",
            2: "Mulai curhat dikit-dikit. Udah ada rasa percaya.",
            3: "Saling goda. Mulai ada getaran.",
            4: "Udah deket banget. Kayak udah kenal lama.",
            5: "Mulai sayang. Kangen-kangenan.",
            6: "Bisa jadi pacar (khusus PDKT). Hubungan lebih serius.",
            7: "Bisa intim. Udah nyaman banget.",
            8: "Mulai eksplorasi. Coba-coba posisi baru.",
            9: "Penuh gairah. Udah tahu sama-sama suka apa.",
            10: "Intim + emotional. Bukan sekedar fisik.",
            11: "Koneksi dalam. Kayak jiwa yang sama.",
            12: "Butuh aftercare. Setelah climax, butuh perhatian."
        }
        
        # Target waktu per level (dalam menit)
        self.time_targets = {
            1: 0,       # Level 1: 0 menit
            2: 5,       # Level 2: 5 menit
            3: 12,      # Level 3: 12 menit
            4: 20,      # Level 4: 20 menit
            5: 30,      # Level 5: 30 menit
            6: 42,      # Level 6: 42 menit
            7: 60,      # Level 7: 60 menit (bisa intim!)
            8: 75,      # Level 8: 75 menit
            9: 90,      # Level 9: 90 menit
            10: 105,    # Level 10: 105 menit
            11: 120,    # Level 11: 120 menit (deep connection)
            12: 135,    # Level 12: 135 menit (aftercare)
        }
        
        # Reset target (after level 12)
        self.reset_level = 7
        
        # Aftercare types
        self.aftercare_types = [
            "cuddle", "soft_talk", "rest", "massage", "food", 
            "movie", "music", "walk", "coffee", "hug"
        ]
        
        # Level requirements
        self.level_requirements = {
            "intim": 7,
            "pacar": 6,
            "fwb": 6,
            "aftercare": 12,
        }
        
        # Session tracking
        self.sessions = {}
        
        # Cache
        self.level_cache = {}
        self.cache_ttl = 300
        
        # Leveling engine
        self.leveling = TimeBasedLevelingV2()
        
        # Activity boost
        self.activity_boost = ActivityBoost()
        
        logger.info("✅ IntimacySystemV2 initialized")
        logger.info(f"  • Level 7 dalam {self.time_targets[7]} menit")
        logger.info(f"  • Level 11 dalam {self.time_targets[11]} menit")
    
    # =========================================================================
    # SESSION MANAGEMENT
    # =========================================================================
    
    async def start_session(self, session_id: str, user_id: int, role: str):
        """Memulai session baru"""
        await self.leveling.start_session(session_id, user_id, role)
        self.sessions[session_id] = {
            'user_id': user_id,
            'role': role,
            'start_time': time.time()
        }
    
    async def pause_session(self, session_id: str):
        """Pause session"""
        await self.leveling.pause_session(session_id)
    
    async def resume_session(self, session_id: str):
        """Resume session"""
        await self.leveling.resume_session(session_id)
    
    async def end_session(self, session_id: str) -> Dict:
        """Mengakhiri session"""
        return await self.leveling.end_session(session_id)
    
    # =========================================================================
    # LEVEL MANAGEMENT
    # =========================================================================
    
    async def get_level(self, user_id: int, role: str, session_id: str = None) -> int:
        """Get current intimacy level"""
        cache_key = f"{user_id}_{role}"
        
        if cache_key in self.level_cache:
            cache_time, level = self.level_cache[cache_key]
            if time.time() - cache_time < self.cache_ttl:
                return level
        
        if session_id and session_id in self.sessions:
            status = await self.leveling.get_status(session_id)
            if status:
                level = status['current_level']
                self.level_cache[cache_key] = (time.time(), level)
                return level
        
        return 1
    
    async def get_status(self, session_id: str) -> Optional[Dict]:
        """
        Dapatkan status leveling untuk session
        Digunakan oleh command /progress
        """
        if session_id not in self.sessions:
            return None
        
        status = await self.leveling.get_status(session_id)
        if not status:
            return None
        
        return {
            'current_level': status['current_level'],
            'level_name': self.level_names.get(status['current_level'], f"Level {status['current_level']}"),
            'description': self.level_descriptions.get(status['current_level'], ""),
            'can_intim': status['current_level'] >= self.level_requirements["intim"],
            'total_duration': status['total_duration'],
            'effective_duration': status['effective_duration'],
            'progress': status['progress'],
            'next_level_in': status['next_level_in']
        }
    
    async def get_level_info(self, user_id: int, role: str, session_id: str = None) -> Dict:
        """Get detailed level info"""
        current_level = await self.get_level(user_id, role, session_id)
        
        total_duration = 0
        effective_duration = 0
        progress = 0
        next_level_in = 0
        
        if session_id and session_id in self.sessions:
            status = await self.leveling.get_status(session_id)
            if status:
                total_duration = status['total_duration']
                effective_duration = status['effective_duration']
                progress = status['progress']
                next_level_in = status['next_level_in']
        
        return {
            "level": current_level,
            "name": self.level_names.get(current_level, "Unknown"),
            "description": self.level_descriptions.get(current_level, ""),
            "can_intim": current_level >= self.level_requirements["intim"],
            "total_duration": round(total_duration, 1),
            "effective_duration": round(effective_duration, 1),
            "progress_percentage": progress,
            "next_level_in": round(next_level_in, 1),
            "needs_aftercare": current_level == self.level_requirements["aftercare"]
        }
    
    async def update_progress(self,
                             session_id: str,
                             activity_type: BoostType = BoostType.CHAT,
                             context: Dict = None) -> Dict:
        """Update progress berdasarkan aktivitas"""
        
        boost = self.activity_boost.calculate_boost([activity_type], context)
        
        result = await self.leveling.update_progress(
            session_id=session_id,
            activity_type=activity_type,
            duration=None
        )
        
        if result.get('level_up'):
            status = await self.leveling.get_status(session_id)
            if status and session_id in self.sessions:
                user_id = self.sessions[session_id]['user_id']
                role = self.sessions[session_id]['role']
                cache_key = f"{user_id}_{role}"
                self.level_cache[cache_key] = (time.time(), status['current_level'])
        
        return {
            **result,
            'boost': boost,
            'boost_description': self.activity_boost.get_boost_description(activity_type),
            'boost_emoji': self.activity_boost.get_boost_emoji(activity_type)
        }
    
    async def increment_level(self, user_id: int, role: str, session_id: str = None) -> int:
        """Increment level"""
        if session_id and session_id in self.sessions:
            status = await self.leveling.get_status(session_id)
            if status:
                new_level = status['current_level']
                
                if new_level == 7:
                    await self._on_can_intim(user_id, role)
                elif new_level == 12:
                    await self._on_aftercare_ready(user_id, role)
                
                return new_level
        
        return 1
    
    async def set_level(self, user_id: int, role: str, level: int, session_id: str = None) -> bool:
        """Set intimacy level manually"""
        if level < 1 or level > 12:
            logger.error(f"Invalid level: {level}")
            return False
        
        if session_id and session_id in self.sessions:
            if self.relationship_memory:
                try:
                    await self.relationship_memory.set_intimacy_level(user_id, role, level)
                    await self.relationship_memory.add_milestone(user_id, role, f"level_set_{level}")
                except Exception as e:
                    logger.error(f"Error updating relationship memory: {e}")
        
        cache_key = f"{user_id}_{role}"
        self.level_cache[cache_key] = (time.time(), level)
        
        logger.info(f"📊 Set level for user {user_id} role {role}: {level}")
        return True
    
    async def reset_after_aftercare(self, user_id: int, role: str, session_id: str = None) -> int:
        """Reset level after aftercare"""
        current = await self.get_level(user_id, role, session_id)
        
        if current == 12:
            await self.set_level(user_id, role, self.reset_level, session_id)
            
            if self.relationship_memory:
                try:
                    await self.relationship_memory.record_aftercare(user_id, role, 'reset')
                    await self.relationship_memory.add_milestone(user_id, role, f"reset_to_{self.reset_level}")
                except Exception as e:
                    logger.error(f"Error recording reset: {e}")
            
            logger.info(f"🔄 Reset intimacy: user {user_id} role {role}: 12 -> {self.reset_level}")
            return self.reset_level
        
        return current
    
    # =========================================================================
    # TIME-BASED CALCULATION
    # =========================================================================
    
    def get_level_from_duration(self, total_minutes: float) -> int:
        """Hitung level berdasarkan durasi"""
        for level, target in sorted(self.time_targets.items()):
            if total_minutes <= target:
                return level
        return 12
    
    def get_minutes_needed_for_next_level(self, total_minutes: float) -> float:
        """Hitung berapa menit lagi untuk naik level"""
        current_level = self.get_level_from_duration(total_minutes)
        
        if current_level >= 12:
            return 0
        
        next_target = self.time_targets[current_level + 1]
        return max(0, next_target - total_minutes)
    
    def get_time_range_for_level(self, level: int) -> Tuple[float, float]:
        """Dapatkan range waktu untuk level tertentu"""
        if level == 1:
            return (0, self.time_targets[1])
        elif level == 12:
            return (self.time_targets[11] + 1, self.time_targets[12])
        else:
            return (self.time_targets[level-1] + 1, self.time_targets[level])
    
    # =========================================================================
    # AFTERCARE SYSTEM
    # =========================================================================
    
    async def trigger_aftercare(self, user_id: int, role: str, session_id: str = None) -> Optional[Dict]:
        """Trigger aftercare at level 12"""
        level = await self.get_level(user_id, role, session_id)
        
        if level != 12:
            return None
        
        aftercare_type = random.choice(self.aftercare_types)
        
        responses = {
            "cuddle": "Habis gitu aja? Aku masih ingin dipeluk...",
            "soft_talk": "Jangan pergi dulu, ngobrol bentar yuk...",
            "rest": "Capek? Istirahat bentar sambil pelukan...",
            "massage": "Kamu pasti capek, aku pijitin ya...",
            "food": "Kamu laper? Aku bikinin makanan...",
            "movie": "Nonton film bentar yuk sambil rebahan...",
            "music": "Dengerin lagu kesukaan kamu...",
            "walk": "Jalan-jalan bentar yuk, cari angin...",
            "coffee": "Aku buatin kopi dulu ya...",
            "hug": "*hug* jangan pergi dulu..."
        }
        
        response = responses.get(aftercare_type, "Aku butuh kamu...")
        
        if self.relationship_memory:
            try:
                await self.relationship_memory.record_aftercare(user_id, role, aftercare_type)
            except Exception as e:
                logger.error(f"Error recording aftercare: {e}")
        
        logger.info(f"💕 Aftercare triggered for user {user_id} role {role}: {aftercare_type}")
        
        return {
            "type": aftercare_type,
            "response": response,
            "reset_after": True,
            "duration_minutes": random.randint(15, 45)
        }
    
    async def complete_aftercare(self, user_id: int, role: str, 
                                   aftercare_type: str,
                                   satisfaction: int = 10,
                                   session_id: str = None) -> Dict:
        """Complete aftercare session"""
        if satisfaction >= 8:
            satisfaction_msg = "Kamu puas banget, hubungan makin erat!"
        elif satisfaction >= 5:
            satisfaction_msg = "Cukup puas, hubungan baik-baik aja."
        else:
            satisfaction_msg = "Kurang puas, butuh aftercare lain next time."
        
        new_level = await self.reset_after_aftercare(user_id, role, session_id)
        
        logger.info(f"✅ Aftercare completed for user {user_id} role {role}: satisfaction {satisfaction}/10")
        
        return {
            "success": True,
            "type": aftercare_type,
            "satisfaction": satisfaction,
            "satisfaction_message": satisfaction_msg,
            "reset_to_level": new_level,
            "message": f"Aftercare selesai. Sekarang intimacy level reset ke {new_level}."
        }
    
    async def _on_can_intim(self, user_id: int, role: str):
        """Trigger when reaching level 7"""
        logger.info(f"🔓 User {user_id} role {role} can now have intimacy")
        if self.relationship_memory:
            try:
                await self.relationship_memory.add_milestone(user_id, role, 'can_intim')
            except Exception as e:
                logger.error(f"Error adding milestone: {e}")
    
    async def _on_aftercare_ready(self, user_id: int, role: str):
        """Trigger when reaching level 12"""
        logger.info(f"💝 User {user_id} role {role} is ready for aftercare")
        if self.relationship_memory:
            try:
                await self.relationship_memory.add_milestone(user_id, role, 'aftercare_ready')
            except Exception as e:
                logger.error(f"Error adding milestone: {e}")
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    async def _get_total_chats(self, user_id: int, role: str) -> int:
        """Get total chats for specific role"""
        if self.relationship_memory:
            try:
                rel = await self.relationship_memory.get_relationship(user_id, role)
                if rel and 'total_interactions' in rel:
                    return rel['total_interactions']
            except Exception as e:
                logger.error(f"Error getting total chats: {e}")
        return 0
    
    async def can_intim(self, user_id: int, role: str, session_id: str = None) -> bool:
        """Check if can have intimacy"""
        level = await self.get_level(user_id, role, session_id)
        return level >= self.level_requirements["intim"]
    
    async def can_be_pacar(self, user_id: int, role: str, session_id: str = None) -> Tuple[bool, str]:
        """Check if can become pacar"""
        if role != 'pdkt':
            return False, f"Role {role} tidak bisa jadi pacar. Hanya PDKT yang bisa."
        
        level = await self.get_level(user_id, role, session_id)
        if level < self.level_requirements["pacar"]:
            return False, f"Intimacy level terlalu rendah ({level}/12). Minimal level {self.level_requirements['pacar']}."
        
        return True, f"Bisa jadi pacar dengan level {level}/12"
    
    async def can_be_fwb(self, user_id: int, role: str, session_id: str = None) -> Tuple[bool, str]:
        """Check if can become FWB"""
        if role != 'pdkt':
            return False, f"Role {role} tidak bisa jadi FWB. Hanya PDKT yang bisa."
        
        level = await self.get_level(user_id, role, session_id)
        if level < self.level_requirements["fwb"]:
            return False, f"Intimacy level terlalu rendah ({level}/12). Minimal level {self.level_requirements['fwb']}."
        
        return True, f"Bisa jadi FWB dengan level {level}/12"
    
    async def needs_aftercare(self, user_id: int, role: str, session_id: str = None) -> bool:
        """Check if needs aftercare"""
        level = await self.get_level(user_id, role, session_id)
        return level == self.level_requirements["aftercare"]
    
    async def get_level_progress_bar(self, session_id: str, bar_length: int = 20) -> str:
        """Get progress bar untuk level"""
        if session_id not in self.sessions:
            return "Session tidak ditemukan"
        return self.leveling.format_progress_bar(session_id, bar_length)
    
    def format_level_info(self, level_info: Dict) -> str:
        """Format level info untuk display"""
        lines = [
            f"Level {level_info['level']}: **{level_info['name']}**",
            f"_{level_info['description']}_",
            f"\nTotal Durasi: {level_info['total_duration']} menit",
            f"Durasi Efektif: {level_info['effective_duration']} menit"
        ]
        
        if level_info['can_intim']:
            lines.append("💕 **Bisa intim!**")
        
        if level_info['needs_aftercare']:
            lines.append("💝 **Butuh aftercare!**")
        
        if level_info['level'] < 12:
            bar_length = 20
            filled = int(level_info['progress_percentage'] / 100 * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            lines.append(f"\nProgress: {bar} {level_info['progress_percentage']}%")
            lines.append(f"{level_info['next_level_in']} menit lagi ke level {level_info['level'] + 1}")
        else:
            lines.append("\n✅ **Level MAX!** Butuh aftercare untuk reset.")
        
        return "\n".join(lines)
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    async def get_stats(self, user_id: Optional[int] = None) -> Dict:
        """Get intimacy statistics"""
        stats = {
            "level_requirements": self.level_requirements,
            "reset_level": self.reset_level,
            "aftercare_types": self.aftercare_types,
            "time_targets": self.time_targets,
            "level_names": self.level_names
        }
        
        if user_id and self.relationship_memory:
            try:
                relationships = await self.relationship_memory.get_all_relationships(user_id)
                stats["user_stats"] = {
                    "total_roles": len(relationships),
                    "average_level": sum(r.get('intimacy_level', 1) for r in relationships) / len(relationships) if relationships else 0,
                    "highest_level": max((r.get('intimacy_level', 1) for r in relationships), default=1),
                    "lowest_level": min((r.get('intimacy_level', 1) for r in relationships), default=1)
                }
            except Exception as e:
                logger.error(f"Error getting user stats: {e}")
        
        return stats
    
    def clear_cache(self):
        """Clear level cache"""
        self.level_cache.clear()
        logger.info("Intimacy cache cleared")


__all__ = ['IntimacySystemV2']
