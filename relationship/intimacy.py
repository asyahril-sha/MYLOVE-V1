#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - INTIMACY SYSTEM (CHAT-BASED)
=============================================================================
- Level 1-12 berdasarkan jumlah chat
- Reset mechanism ke level 7 setelah level 12
- Aftercare system
- BUKAN real time, berdasarkan akumulasi chat
"""

import logging
import random
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class IntimacySystem:
    """
    Sistem intimacy level berdasarkan jumlah chat
    BUKAN real time - menggunakan hitungan interaksi
    """
    
    def __init__(self, relationship_memory, consolidation):
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
        
        # Reset target (after level 12)
        self.reset_level = 7
        
        # Aftercare types
        self.aftercare_types = [
            "cuddle", "soft_talk", "rest", "massage", "food", 
            "movie", "music", "walk", "coffee", "hug"
        ]
        
        logger.info("✅ IntimacySystem initialized (CHAT-BASED)")
        
    # =========================================================================
    # LEVEL MANAGEMENT
    # =========================================================================
    
    async def get_level(self, user_id: int, role: str) -> int:
        """Get current intimacy level for role"""
        rel = await self.relationship_memory.get_relationship(user_id, role)
        return rel.get('intimacy_level', 1) if rel else 1
        
    async def get_level_info(self, user_id: int, role: str) -> Dict:
        """Get detailed level info"""
        level = await self.get_level(user_id, role)
        total_chats = await self._get_total_chats(user_id, role)
        progress = await self.consolidation.get_intimacy_progress(total_chats)
        
        return {
            "level": level,
            "name": self.level_names.get(level, "Unknown"),
            "description": self.level_descriptions.get(level, ""),
            "can_intim": level >= 7,
            "total_chats": total_chats,
            "next_level_in": progress['next_level_in'],
            "progress_percentage": progress['progress_percentage']
        }
        
    async def increment_level(self, user_id: int, role: str) -> int:
        """
        Increment intimacy level based on chat count
        Dipanggil setiap kali user chat
        """
        # Get current level
        current = await self.get_level(user_id, role)
        
        # Get total chats for this role
        total_chats = await self._get_total_chats(user_id, role)
        
        # Calculate level from chats
        new_level = self.consolidation.get_intimacy_level_from_chats(total_chats)
        
        # If level changed
        if new_level > current:
            logger.info(f"📈 Level UP! user {user_id} role {role}: {current} -> {new_level}")
            
            # Update relationship
            await self.relationship_memory.set_intimacy_level(user_id, role, new_level)
            
            # Check for special events
            if new_level == 7:
                await self._on_can_intim(user_id, role)
            elif new_level == 12:
                await self._on_aftercare_ready(user_id, role)
                
        return new_level
        
    async def reset_after_aftercare(self, user_id: int, role: str) -> int:
        """
        Reset level after aftercare
        Level 12 -> Reset ke 7
        """
        current = await self.get_level(user_id, role)
        
        if current == 12:
            await self.relationship_memory.reset_intimacy(user_id, role, self.reset_level)
            logger.info(f"🔄 Reset intimacy: user {user_id} role {role}: 12 -> {self.reset_level}")
            
            # Record reset
            await self.relationship_memory.record_aftercare(user_id, role, 'reset')
            
            return self.reset_level
            
        return current
        
    # =========================================================================
    # AFTERCARE SYSTEM
    # =========================================================================
    
    async def trigger_aftercare(self, user_id: int, role: str) -> Dict:
        """Trigger aftercare at level 12"""
        level = await self.get_level(user_id, role)
        
        if level != 12:
            return None
            
        # Choose random aftercare type
        aftercare_type = random.choice(self.aftercare_types)
        
        # Generate response based on type
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
        
        # Record aftercare
        await self.relationship_memory.record_aftercare(user_id, role, aftercare_type)
        
        return {
            "type": aftercare_type,
            "response": response,
            "reset_after": True  # Will reset after this
        }
        
    async def _on_can_intim(self, user_id: int, role: str):
        """Trigger when reaching level 7 (can intim)"""
        # Add milestone
        await self.relationship_memory.add_milestone(user_id, role, 'can_intim')
        
    async def _on_aftercare_ready(self, user_id: int, role: str):
        """Trigger when reaching level 12 (aftercare ready)"""
        # Add milestone
        await self.relationship_memory.add_milestone(user_id, role, 'aftercare_ready')
        
    # =========================================================================
    # UTILITY
    # =========================================================================
    
    async def _get_total_chats(self, user_id: int, role: str) -> int:
        """Get total chats for specific role"""
        rel = await self.relationship_memory.get_relationship(user_id, role)
        return rel.get('total_interactions', 0) if rel else 0
        
    async def can_intim(self, user_id: int, role: str) -> bool:
        """Check if can have intimacy"""
        level = await self.get_level(user_id, role)
        return level >= 7
        
    async def needs_aftercare(self, user_id: int, role: str) -> bool:
        """Check if needs aftercare"""
        level = await self.get_level(user_id, role)
        return level == 12
        
    async def get_level_progress(self, user_id: int, role: str) -> str:
        """Get human-readable progress"""
        info = await self.get_level_info(user_id, role)
        
        bar_length = 20
        filled = int(info['progress_percentage'] / 100 * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        return (
            f"Level {info['level']}: {info['name']}\n"
            f"{bar} {info['progress_percentage']}%\n"
            f"{info['next_level_in']} chat lagi ke level {info['level'] + 1 if info['level'] < 12 else 'max'}"
        )


__all__ = ['IntimacySystem']
