#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - INTIMACY SYSTEM (CHAT-BASED) (FIX FULL)
=============================================================================
- Level 1-12 berdasarkan jumlah chat
- Reset mechanism ke level 7 setelah level 12
- Aftercare system
- FIX: Semua method lengkap, tidak missing arguments
"""

import time
import logging
import random
import math
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from config import settings

logger = logging.getLogger(__name__)


class IntimacySystem:
    """
    Sistem intimacy level berdasarkan jumlah chat
    BUKAN real time - menggunakan hitungan interaksi
    """
    
    def __init__(self, relationship_memory=None, consolidation=None):
        """
        Args:
            relationship_memory: RelationshipMemory instance (optional)
            consolidation: MemoryConsolidation instance (optional)
        """
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
        
        # Chat targets per level (BUKAN waktu real)
        self.chat_targets = {
            1: 5,      # Level 1: 0-5 chat
            2: 15,     # Level 2: 6-15 chat
            3: 30,     # Level 3: 16-30 chat
            4: 50,     # Level 4: 31-50 chat
            5: 75,     # Level 5: 51-75 chat
            6: 100,    # Level 6: 76-100 chat
            7: 130,    # Level 7: 101-130 chat
            8: 165,    # Level 8: 131-165 chat
            9: 205,    # Level 9: 166-205 chat
            10: 250,   # Level 10: 206-250 chat
            11: 300,   # Level 11: 251-300 chat
            12: 350,   # Level 12: 301-350 chat
        }
        
        # Level requirements untuk berbagai action
        self.level_requirements = {
            "intim": 7,        # Minimal level 7 untuk intim
            "pacar": 6,         # Minimal level 6 untuk jadi pacar (khusus PDKT)
            "fwb": 6,           # Minimal level 6 untuk FWB
            "aftercare": 12,     # Level 12 untuk aftercare
        }
        
        # Cache untuk performa
        self.level_cache = {}  # {user_id_role: level}
        self.cache_ttl = 300   # 5 menit
        
        logger.info("✅ IntimacySystem initialized (CHAT-BASED)")
        
    # =========================================================================
    # LEVEL MANAGEMENT
    # =========================================================================
    
    async def get_level(self, user_id: int, role: str) -> int:
        """
        Get current intimacy level for role
        Berdasarkan jumlah chat, bukan waktu
        """
        cache_key = f"{user_id}_{role}"
        
        # Cek cache
        if cache_key in self.level_cache:
            cache_time, level = self.level_cache[cache_key]
            if time.time() - cache_time < self.cache_ttl:
                return level
        
        # Get from relationship memory if available
        if self.relationship_memory:
            try:
                rel = await self.relationship_memory.get_relationship(user_id, role)
                if rel and 'intimacy_level' in rel:
                    level = rel['intimacy_level']
                    self.level_cache[cache_key] = (time.time(), level)
                    return level
            except Exception as e:
                logger.error(f"Error getting level from relationship memory: {e}")
        
        # Default level 1
        return 1
        
    async def get_level_info(self, user_id: int, role: str, total_chats: int = None) -> Dict:
        """
        Get detailed level info
        
        Args:
            user_id: ID user
            role: Role name
            total_chats: Total chats (if None, will try to get from relationship)
            
        Returns:
            Dict with level info
        """
        # Get current level
        current_level = await self.get_level(user_id, role)
        
        # Get total chats
        if total_chats is None:
            total_chats = await self._get_total_chats(user_id, role)
        
        # Get progress
        progress = await self.get_level_progress(user_id, role, total_chats)
        
        return {
            "level": current_level,
            "name": self.level_names.get(current_level, "Unknown"),
            "description": self.level_descriptions.get(current_level, ""),
            "can_intim": current_level >= self.level_requirements["intim"],
            "total_chats": total_chats,
            "next_level_in": progress['next_level_in'],
            "progress_percentage": progress['progress_percentage'],
            "needs_aftercare": current_level == self.level_requirements["aftercare"]
        }
        
    async def increment_level(self, user_id: int, role: str, total_chats: int = None) -> int:
        """
        Increment intimacy level based on chat count
        Dipanggil setiap kali user chat
        
        Args:
            user_id: ID user
            role: Role name
            total_chats: Total chats (if None, will get from relationship)
            
        Returns:
            New level
        """
        # Get current level
        current = await self.get_level(user_id, role)
        
        # Get total chats for this role
        if total_chats is None:
            total_chats = await self._get_total_chats(user_id, role)
        
        # Calculate level from chats
        new_level = self.get_intimacy_level_from_chats(total_chats)
        
        # If level changed
        if new_level > current:
            logger.info(f"📈 Level UP! user {user_id} role {role}: {current} -> {new_level}")
            
            # Update relationship memory if available
            if self.relationship_memory:
                try:
                    await self.relationship_memory.set_intimacy_level(user_id, role, new_level)
                    
                    # Add milestone
                    await self.relationship_memory.add_milestone(
                        user_id, role, f"level_{new_level}"
                    )
                except Exception as e:
                    logger.error(f"Error updating relationship memory: {e}")
            
            # Update cache
            cache_key = f"{user_id}_{role}"
            self.level_cache[cache_key] = (time.time(), new_level)
            
            # Check for special events
            if new_level == 7:
                await self._on_can_intim(user_id, role)
            elif new_level == 12:
                await self._on_aftercare_ready(user_id, role)
                
        return new_level
        
    async def set_level(self, user_id: int, role: str, level: int) -> bool:
        """
        Set intimacy level manually
        
        Args:
            user_id: ID user
            role: Role name
            level: New level (1-12)
            
        Returns:
            True if successful
        """
        if level < 1 or level > 12:
            logger.error(f"Invalid level: {level}")
            return False
        
        # Update relationship memory if available
        if self.relationship_memory:
            try:
                await self.relationship_memory.set_intimacy_level(user_id, role, level)
                
                # Add milestone
                await self.relationship_memory.add_milestone(
                    user_id, role, f"level_set_{level}"
                )
            except Exception as e:
                logger.error(f"Error updating relationship memory: {e}")
        
        # Update cache
        cache_key = f"{user_id}_{role}"
        self.level_cache[cache_key] = (time.time(), level)
        
        logger.info(f"📊 Set level for user {user_id} role {role}: {level}")
        
        return True
        
    async def reset_after_aftercare(self, user_id: int, role: str) -> int:
        """
        Reset level after aftercare
        Level 12 -> Reset ke level 7
        
        Args:
            user_id: ID user
            role: Role name
            
        Returns:
            New level (reset_level)
        """
        current = await self.get_level(user_id, role)
        
        if current == 12:
            # Reset ke level 7
            await self.set_level(user_id, role, self.reset_level)
            
            # Record reset
            if self.relationship_memory:
                try:
                    await self.relationship_memory.record_aftercare(user_id, role, 'reset')
                    await self.relationship_memory.add_milestone(
                        user_id, role, f"reset_to_{self.reset_level}"
                    )
                except Exception as e:
                    logger.error(f"Error recording reset: {e}")
            
            logger.info(f"🔄 Reset intimacy: user {user_id} role {role}: 12 -> {self.reset_level}")
            
            return self.reset_level
        
        return current
        
    # =========================================================================
    # CHAT-BASED LEVEL CALCULATION
    # =========================================================================
    
    def get_intimacy_level_from_chats(self, total_chats: int) -> int:
        """
        Hitung intimacy level berdasarkan jumlah chat
        BUKAN berdasarkan waktu real
        
        Args:
            total_chats: Total jumlah chat dengan role ini
            
        Returns:
            Level 1-12
        """
        for level, target in sorted(self.chat_targets.items()):
            if total_chats <= target:
                return level
        return 12  # Maximum level
        
    def get_chats_needed_for_next_level(self, total_chats: int) -> int:
        """Hitung berapa chat lagi untuk naik level"""
        current_level = self.get_intimacy_level_from_chats(total_chats)
        
        if current_level >= 12:
            return 0  # Already max
            
        next_target = self.chat_targets[current_level + 1]
        return max(0, next_target - total_chats)
        
    def get_chat_range_for_level(self, level: int) -> Tuple[int, int]:
        """Dapatkan range chat untuk level tertentu"""
        if level == 1:
            return (0, self.chat_targets[1])
        elif level == 12:
            return (self.chat_targets[11] + 1, self.chat_targets[12])
        else:
            return (self.chat_targets[level-1] + 1, self.chat_targets[level])
            
    async def get_level_progress(self, user_id: int, role: str, total_chats: int = None) -> Dict:
        """
        Get progress to next level
        
        Args:
            user_id: ID user
            role: Role name
            total_chats: Total chats (if None, will get from relationship)
            
        Returns:
            Dict with progress info
        """
        if total_chats is None:
            total_chats = await self._get_total_chats(user_id, role)
        
        current_level = self.get_intimacy_level_from_chats(total_chats)
        next_level_chats = self.get_chats_needed_for_next_level(total_chats)
        
        # Calculate percentage to next level
        if current_level >= 12:
            percentage = 100
        else:
            current_range = self.get_chat_range_for_level(current_level)
            progress = total_chats - current_range[0]
            total_needed = current_range[1] - current_range[0]
            percentage = min(100, int((progress / total_needed) * 100)) if total_needed > 0 else 0
            
        return {
            "current_level": current_level,
            "total_chats": total_chats,
            "next_level_in": next_level_chats,
            "progress_percentage": percentage,
            "chat_range": self.get_chat_range_for_level(current_level)
        }
        
    # =========================================================================
    # AFTERCARE SYSTEM
    # =========================================================================
    
    async def trigger_aftercare(self, user_id: int, role: str) -> Optional[Dict]:
        """
        Trigger aftercare at level 12
        
        Args:
            user_id: ID user
            role: Role name
            
        Returns:
            Aftercare data or None if not level 12
        """
        level = await self.get_level(user_id, role)
        
        if level != 12:
            logger.debug(f"Not level 12 (current: {level}), no aftercare needed")
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
        if self.relationship_memory:
            try:
                await self.relationship_memory.record_aftercare(user_id, role, aftercare_type)
            except Exception as e:
                logger.error(f"Error recording aftercare: {e}")
        
        logger.info(f"💕 Aftercare triggered for user {user_id} role {role}: {aftercare_type}")
        
        return {
            "type": aftercare_type,
            "response": response,
            "reset_after": True,  # Will reset after this
            "duration_minutes": random.randint(15, 45)
        }
        
    async def complete_aftercare(self, user_id: int, role: str, 
                                   aftercare_type: str,
                                   satisfaction: int = 10) -> Dict:
        """
        Complete aftercare session and reset intimacy
        
        Args:
            user_id: ID user
            role: Role name
            aftercare_type: Tipe aftercare yang dilakukan
            satisfaction: Tingkat kepuasan (1-10)
            
        Returns:
            Dict dengan hasil aftercare
        """
        # Calculate satisfaction effects
        if satisfaction >= 8:
            satisfaction_msg = "Kamu puas banget, hubungan makin erat!"
        elif satisfaction >= 5:
            satisfaction_msg = "Cukup puas, hubungan baik-baik aja."
        else:
            satisfaction_msg = "Kurang puas, butuh aftercare lain next time."
        
        # Reset level
        new_level = await self.reset_after_aftercare(user_id, role)
        
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
        """Trigger when reaching level 7 (can intim)"""
        logger.info(f"🔓 User {user_id} role {role} can now have intimacy")
        
        # Add milestone
        if self.relationship_memory:
            try:
                await self.relationship_memory.add_milestone(user_id, role, 'can_intim')
            except Exception as e:
                logger.error(f"Error adding milestone: {e}")
        
    async def _on_aftercare_ready(self, user_id: int, role: str):
        """Trigger when reaching level 12 (aftercare ready)"""
        logger.info(f"💝 User {user_id} role {role} is ready for aftercare")
        
        # Add milestone
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
        
    async def can_intim(self, user_id: int, role: str) -> bool:
        """Check if can have intimacy"""
        level = await self.get_level(user_id, role)
        return level >= self.level_requirements["intim"]
        
    async def can_be_pacar(self, user_id: int, role: str) -> Tuple[bool, str]:
        """
        Check if can become pacar (khusus PDKT)
        
        Returns:
            (can, reason)
        """
        if role != 'pdkt':
            return False, f"Role {role} tidak bisa jadi pacar. Hanya PDKT yang bisa."
        
        level = await self.get_level(user_id, role)
        if level < self.level_requirements["pacar"]:
            return False, f"Intimacy level terlalu rendah ({level}/12). Minimal level {self.level_requirements['pacar']}."
        
        return True, f"Bisa jadi pacar dengan level {level}/12"
        
    async def can_be_fwb(self, user_id: int, role: str) -> Tuple[bool, str]:
        """
        Check if can become FWB
        
        Returns:
            (can, reason)
        """
        if role != 'pdkt':
            return False, f"Role {role} tidak bisa jadi FWB. Hanya PDKT yang bisa."
        
        level = await self.get_level(user_id, role)
        if level < self.level_requirements["fwb"]:
            return False, f"Intimacy level terlalu rendah ({level}/12). Minimal level {self.level_requirements['fwb']}."
        
        return True, f"Bisa jadi FWB dengan level {level}/12"
        
    async def needs_aftercare(self, user_id: int, role: str) -> bool:
        """Check if needs aftercare"""
        level = await self.get_level(user_id, role)
        return level == self.level_requirements["aftercare"]
        
    async def get_level_progress_bar(self, user_id: int, role: str, total_chats: int = None, bar_length: int = 20) -> str:
        """
        Get progress bar untuk level
        
        Args:
            user_id: ID user
            role: Role name
            total_chats: Total chats
            bar_length: Panjang progress bar
            
        Returns:
            String progress bar
        """
        if total_chats is None:
            total_chats = await self._get_total_chats(user_id, role)
        
        progress = await self.get_level_progress(user_id, role, total_chats)
        percentage = progress['progress_percentage']
        
        filled = int(percentage / 100 * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        return bar
        
    def format_level_info(self, level_info: Dict) -> str:
        """Format level info untuk display"""
        lines = [
            f"Level {level_info['level']}: **{level_info['name']}**",
            f"_{level_info['description']}_",
            f"\nTotal Chat: {level_info['total_chats']} pesan"
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
            lines.append(f"{level_info['next_level_in']} chat lagi ke level {level_info['level'] + 1}")
        
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
            "chat_targets": self.chat_targets
        }
        
        if user_id and self.relationship_memory:
            try:
                # Get all relationships for user
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


__all__ = ['IntimacySystem']
