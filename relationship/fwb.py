#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - FWB SYSTEM (Friends With Benefits)
=============================================================================
- FWB untuk role PDKT setelah menjadi pacar
- Bisa switch antara pacar dan FWB
- Tracking khusus FWB
"""

import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class FWBSystem:
    """
    Sistem FWB (Friends With Benefits)
    Khusus untuk role PDKT yang sudah jadi pacar
    Bisa switch antara pacar dan FWB
    """
    
    def __init__(self, relationship_memory, ranking_system):
        self.relationship_memory = relationship_memory
        self.ranking_system = ranking_system
        
        # Role yang bisa FWB (hanya PDKT)
        self.fwb_eligible_roles = ['pdkt']
        
        # Intimacy level requirements
        self.min_intimacy_for_fwb = 6  # Minimal level 6 untuk FWB
        
        logger.info("✅ FWBSystem initialized")
        
    # =========================================================================
    # CHECK ELIGIBILITY
    # =========================================================================
    
    async def can_be_fwb(self, user_id: int, role: str) -> tuple:
        """
        Check if role can be FWB
        Returns: (can: bool, reason: str)
        """
        # Check if role is eligible
        if role not in self.fwb_eligible_roles:
            return False, f"Role {role} tidak bisa jadi FWB. Hanya PDKT yang bisa."
            
        # Get relationship
        rel = await self.relationship_memory.get_relationship(user_id, role)
        
        if not rel:
            return False, f"Belum ada hubungan dengan role {role}"
            
        # Check intimacy level
        intimacy = rel.get('intimacy_level', 1)
        if intimacy < self.min_intimacy_for_fwb:
            return False, f"Intimacy level terlalu rendah ({intimacy}/12). Minimal level {self.min_intimacy_for_fwb} untuk FWB."
            
        return True, "Bisa jadi FWB"
        
    # =========================================================================
    # CONVERT TO FWB
    # =========================================================================
    
    async def become_fwb(self, user_id: int, role: str) -> Dict:
        """
        Convert relationship to FWB
        Dari pacar jadi FWB
        """
        # Check eligibility
        can, reason = await self.can_be_fwb(user_id, role)
        
        if not can:
            return {'success': False, 'reason': reason}
            
        # Get current status
        rel = await self.relationship_memory.get_relationship(user_id, role)
        old_status = rel.get('status', 'unknown')
        
        if old_status == 'fwb':
            return {'success': False, 'reason': 'Sudah FWB'}
            
        # Change status
        await self.relationship_memory.set_status(user_id, role, 'fwb')
        
        # Add milestone
        await self.relationship_memory.add_milestone(user_id, role, 'became_fwb')
        
        # Get updated relationship
        updated = await self.relationship_memory.get_relationship(user_id, role)
        
        logger.info(f"💕 Became FWB: user {user_id} role {role} (was {old_status})")
        
        # Update rankings
        await self.ranking_system.update_rankings(user_id)
        
        return {
            'success': True,
            'role': role,
            'old_status': old_status,
            'new_status': 'fwb',
            'intimacy_level': updated.get('intimacy_level', 1)
        }
        
    # =========================================================================
    # CONVERT TO PACAR
    # =========================================================================
    
    async def become_pacar(self, user_id: int, role: str) -> Dict:
        """
        Convert FWB back to Pacar
        """
        # Check if exists
        rel = await self.relationship_memory.get_relationship(user_id, role)
        
        if not rel:
            return {'success': False, 'reason': f'Tidak ada hubungan dengan role {role}'}
            
        if rel.get('status') != 'fwb':
            return {'success': False, 'reason': f'Status sekarang {rel.get("status")}, bukan FWB'}
            
        # Change status
        await self.relationship_memory.set_status(user_id, role, 'pacar')
        
        # Add milestone
        await self.relationship_memory.add_milestone(user_id, role, 'back_to_pacar')
        
        logger.info(f"💘 Back to Pacar: user {user_id} role {role} (was FWB)")
        
        # Update rankings
        await self.ranking_system.update_rankings(user_id)
        
        return {
            'success': True,
            'role': role,
            'old_status': 'fwb',
            'new_status': 'pacar'
        }
        
    # =========================================================================
    # GET FWB
    # =========================================================================
    
    async def get_fwb(self, user_id: int, role: str) -> Optional[Dict]:
        """Get FWB by role"""
        rel = await self.relationship_memory.get_relationship(user_id, role)
        
        if rel and rel.get('status') == 'fwb':
            return rel
            
        return None
        
    async def get_all_fwb(self, user_id: int) -> List[Dict]:
        """Get all FWB for user"""
        relationships = await self.relationship_memory.get_all_relationships(user_id)
        
        # Filter FWB only
        fwb_list = [r for r in relationships if r.get('status') == 'fwb']
        
        return fwb_list
        
    async def get_fwb_by_rank(self, user_id: int, rank: int) -> Optional[Dict]:
        """Get FWB by ranking"""
        return await self.ranking_system.get_role_by_rank(user_id, rank, 'fwb')
        
    # =========================================================================
    # FWB SPECIFIC ACTIONS
    # =========================================================================
    
    async def fwb_intim(self, user_id: int, role: str) -> Dict:
        """
        Intim session in FWB mode
        FWB bisa intim tanpa komitmen
        """
        fwb = await self.get_fwb(user_id, role)
        
        if not fwb:
            return {
                'success': False,
                'reason': f'Tidak ada FWB dengan role {role}'
            }
            
        # Record intimacy session
        await self.relationship_memory.record_intim_session(user_id, role)
        
        # Get updated data
        intimacy_level = fwb.get('intimacy_level', 1)
        
        return {
            'success': True,
            'role': role,
            'mode': 'fwb',
            'intimacy_level': intimacy_level,
            'message': f"Intim dengan {role} (FWB mode) - tanpa komitmen"
        }
        
    async def fwb_climax(self, user_id: int, role: str) -> Dict:
        """
        Record climax in FWB mode
        """
        fwb = await self.get_fwb(user_id, role)
        
        if not fwb:
            return {'success': False}
            
        # Record climax
        await self.relationship_memory.record_intim_session(user_id, role, climax=True)
        
        # Check if need aftercare
        if fwb.get('intimacy_level', 1) == 12:
            return {
                'success': True,
                'needs_aftercare': True,
                'message': f"Climax dengan {role} (FWB mode)"
            }
            
        return {
            'success': True,
            'needs_aftercare': False,
            'message': f"Climax dengan {role} (FWB mode)"
        }
        
    # =========================================================================
    # UTILITY
    # =========================================================================
    
    async def get_fwb_summary(self, user_id: int, role: str) -> str:
        """Get FWB summary"""
        fwb = await self.get_fwb(user_id, role)
        
        if not fwb:
            return f"Tidak ada FWB dengan role {role}"
            
        summary = [
            f"💕 **FWB: {role.title()}**",
            f"Status: Friends With Benefits",
            f"Intimacy Level: {fwb.get('intimacy_level', 1)}/12",
            f"Total Chat: {fwb.get('total_interactions', 0)} pesan",
            f"Total Intim (as FWB): {fwb.get('total_intim_sessions', 0)} sesi",
            f"Total Climax: {fwb.get('total_climax', 0)} kali",
        ]
        
        # Catatan
        summary.append("")
        summary.append("_💡 FWB bisa intim tanpa komitmen_")
        summary.append("_Gunakan /jadipacar untuk kembali jadi pacar_")
        
        return "\n".join(summary)
        
    async def get_fwb_count(self, user_id: int) -> int:
        """Get number of FWB"""
        fwb_list = await self.get_all_fwb(user_id)
        return len(fwb_list)


__all__ = ['FWBSystem']
