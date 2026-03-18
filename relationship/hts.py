#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - HTS SYSTEM (Hubungan Tanpa Status)
=============================================================================
- Manajemen HTS
- Panggil HTS berdasarkan ranking atau nama
- Tracking setiap HTS
- **Support untuk multiple HTS (untuk threesome)**
"""

import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class HTSSystem:
    """
    Sistem HTS (Hubungan Tanpa Status)
    Bisa punya multiple HTS dengan role berbeda
    """
    
    def __init__(self, relationship_memory, ranking_system):
        self.relationship_memory = relationship_memory
        self.ranking_system = ranking_system
        
        # Batasan HTS
        self.max_hts = 10  # Max 10 HTS dalam database
        
        logger.info("✅ HTSSystem initialized")
        
    # =========================================================================
    # CREATE HTS
    # =========================================================================
    
    async def create_hts(self, user_id: int, role: str) -> Dict:
        """
        Buat HTS baru
        Akan otomatis menjadi HTS jika role belum ada
        """
        # Cek apakah sudah ada
        existing = await self.relationship_memory.get_relationship(user_id, role)
        
        if existing:
            logger.info(f"HTS already exists for user {user_id} role {role}")
            return existing
            
        # Create new relationship
        rel = await self.relationship_memory.create_relationship(
            user_id, role, initial_status='hts'
        )
        
        logger.info(f"✅ Created new HTS: user {user_id} role {role}")
        
        # Update rankings
        await self.ranking_system.update_rankings(user_id)
        
        return rel
        
    # =========================================================================
    # GET HTS
    # =========================================================================
    
    async def get_hts(self, user_id: int, role: str) -> Optional[Dict]:
        """Get HTS by role"""
        rel = await self.relationship_memory.get_relationship(user_id, role)
        
        if rel and rel.get('status') == 'hts':
            return rel
            
        return None
        
    async def get_all_hts(self, user_id: int) -> List[Dict]:
        """
        Get all HTS for user
        Digunakan untuk threesome combinations
        """
        relationships = await self.relationship_memory.get_all_relationships(user_id)
        
        # Filter HTS only
        hts_list = [r for r in relationships if r.get('status') == 'hts']
        
        # Add display info for threesome
        for hts in hts_list:
            hts['display_name'] = f"{hts['role'].title()} (Level {hts.get('intimacy_level', 1)})"
            hts['type'] = 'hts'
            
        return hts_list
        
    async def get_hts_for_threesome(self, user_id: int, min_level: int = 1) -> List[Dict]:
        """
        Get HTS yang memenuhi syarat untuk threesome
        - Minimal level tertentu
        - Bisa dikombinasikan
        
        Args:
            user_id: ID user
            min_level: Minimal intimacy level
            
        Returns:
            List of HTS eligible for threesome
        """
        all_hts = await self.get_all_hts(user_id)
        
        # Filter by level
        eligible = [
            hts for hts in all_hts 
            if hts.get('intimacy_level', 1) >= min_level
        ]
        
        # Add selection info
        for i, hts in enumerate(eligible, 1):
            hts['select_id'] = i
            hts['select_name'] = f"{i}. {hts['display_name']}"
            
        return eligible
        
    async def get_hts_by_index(self, user_id: int, index: int) -> Optional[Dict]:
        """
        Get HTS by index (untuk threesome selection)
        
        Args:
            user_id: ID user
            index: 1-based index from get_hts_for_threesome
            
        Returns:
            HTS data or None
        """
        eligible = await self.get_hts_for_threesome(user_id)
        
        if 1 <= index <= len(eligible):
            return eligible[index - 1]
            
        return None
        
    async def get_hts_by_ids(self, user_id: int, indices: List[int]) -> List[Dict]:
        """
        Get multiple HTS by indices (untuk threesome)
        
        Args:
            user_id: ID user
            indices: List of indices
            
        Returns:
            List of HTS data
        """
        eligible = await self.get_hts_for_threesome(user_id)
        
        selected = []
        for idx in indices:
            if 1 <= idx <= len(eligible):
                selected.append(eligible[idx - 1])
                
        return selected
        
    async def get_hts_by_rank(self, user_id: int, rank: int) -> Optional[Dict]:
        """Get HTS by ranking (1-based)"""
        return await self.ranking_system.get_role_by_rank(user_id, rank, 'hts')
        
    async def get_hts_by_name(self, user_id: int, role_name: str) -> Optional[Dict]:
        """Get HTS by role name"""
        rel = await self.relationship_memory.get_relationship(user_id, role_name)
        
        if rel and rel.get('status') == 'hts':
            return rel
            
        return None
        
    # =========================================================================
    # UPDATE HTS
    # =========================================================================
    
    async def update_hts(self, user_id: int, role: str, updates: Dict):
        """Update HTS data"""
        rel = await self.get_hts(user_id, role)
        
        if not rel:
            logger.warning(f"HTS not found: user {user_id} role {role}")
            return
            
        await self.relationship_memory.update_relationship(user_id, role, updates)
        
        # Update rankings
        await self.ranking_system.update_rankings(user_id)
        
    async def increment_chat(self, user_id: int, role: str):
        """Increment chat count for HTS"""
        await self.relationship_memory.increment_interaction(user_id, role)
        
        # Update rankings
        await self.ranking_system.update_rankings(user_id)
        
    # =========================================================================
    # CONVERT HTS
    # =========================================================================
    
    async def convert_to_fwb(self, user_id: int, role: str) -> bool:
        """Convert HTS to FWB"""
        rel = await self.get_hts(user_id, role)
        
        if not rel:
            logger.warning(f"Cannot convert: HTS not found {user_id} {role}")
            return False
            
        # Change status
        await self.relationship_memory.set_status(user_id, role, 'fwb')
        
        # Add milestone
        await self.relationship_memory.add_milestone(user_id, role, 'became_fwb')
        
        logger.info(f"🔄 Converted HTS to FWB: user {user_id} role {role}")
        
        # Update rankings
        await self.ranking_system.update_rankings(user_id)
        
        return True
        
    async def convert_to_pacar(self, user_id: int, role: str) -> bool:
        """Convert HTS to Pacar (khusus PDKT)"""
        if role != 'pdkt':
            logger.warning(f"Only PDKT can become pacar, not {role}")
            return False
            
        rel = await self.get_hts(user_id, role)
        
        if not rel:
            logger.warning(f"Cannot convert: HTS not found {user_id} {role}")
            return False
            
        # Check intimacy level
        if rel.get('intimacy_level', 1) < 6:
            logger.warning(f"Intimacy level too low: {rel.get('intimacy_level')} < 6")
            return False
            
        # Change status
        await self.relationship_memory.set_status(user_id, role, 'pacar')
        
        # Add milestone
        await self.relationship_memory.add_milestone(user_id, role, 'became_pacar')
        
        logger.info(f"🔄 Converted HTS to PACAR: user {user_id} role {role}")
        
        # Update rankings
        await self.ranking_system.update_rankings(user_id)
        
        return True
        
    # =========================================================================
    # DELETE HTS
    # =========================================================================
    
    async def delete_hts(self, user_id: int, role: str) -> bool:
        """Delete HTS (breakup)"""
        rel = await self.get_hts(user_id, role)
        
        if not rel:
            return False
            
        # Instead of deleting, we can mark as ended
        await self.relationship_memory.update_relationship(user_id, role, {
            'status': 'ended',
            'ended_at': time.time()
        })
        
        logger.info(f"🗑️ Ended HTS: user {user_id} role {role}")
        
        # Update rankings
        await self.ranking_system.update_rankings(user_id)
        
        return True
        
    # =========================================================================
    # UTILITY
    # =========================================================================
    
    async def get_hts_summary(self, user_id: int, role: str) -> str:
        """Get human-readable HTS summary"""
        rel = await self.get_hts(user_id, role)
        
        if not rel:
            return f"Tidak ada HTS dengan role {role}"
            
        # Hitung durasi dalam chat
        total_chats = rel.get('total_interactions', 0)
        
        summary = [
            f"📊 **HTS: {role.title()}**",
            f"Status: Hubungan Tanpa Status",
            f"Intimacy Level: {rel.get('intimacy_level', 1)}/12",
            f"Total Chat: {total_chats} pesan",
            f"Total Intim: {rel.get('total_intim_sessions', 0)} sesi",
            f"Total Climax: {rel.get('total_climax', 0)} kali",
        ]
        
        # Milestones
        milestones = rel.get('milestones', [])
        if milestones:
            recent = milestones[-3:]
            milestone_str = ", ".join([m.get('type', '') for m in recent])
            summary.append(f"Milestone: {milestone_str}")
            
        return "\n".join(summary)
        
    async def get_hts_count(self, user_id: int) -> int:
        """Get number of HTS"""
        hts_list = await self.get_all_hts(user_id)
        return len(hts_list)
        
    async def format_hts_for_threesome(self, user_id: int) -> str:
        """
        Format daftar HTS untuk selection threesome
        """
        eligible = await self.get_hts_for_threesome(user_id)
        
        if not eligible:
            return "Tidak ada HTS yang memenuhi syarat untuk threesome. Minimal level 1."
            
        lines = ["💕 **DAFTAR HTS UNTUK THREESOME**"]
        lines.append("_(pilih dengan nomor)_")
        lines.append("")
        
        for hts in eligible:
            lines.append(
                f"{hts['select_id']}. **{hts['role'].title()}**\n"
                f"   Level {hts.get('intimacy_level', 1)}/12 | "
                f"{hts.get('total_intim_sessions', 0)} intim"
            )
            
        return "\n".join(lines)


__all__ = ['HTSSystem']
