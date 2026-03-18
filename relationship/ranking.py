#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - RANKING SYSTEM (FIXED)
=============================================================================
- TOP 10 di database, TOP 5 ditampilkan
- Ranking berdasarkan total interaksi, intimacy level, durasi
- FIX: Constructor dengan default None untuk relationship_memory
"""

import logging
import time
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class RankingSystem:
    """
    Sistem ranking untuk HTS dan FWB
    Menyimpan TOP 10 di database, menampilkan TOP 5 ke user
    """
    
    def __init__(self, relationship_memory=None):
        """
        Args:
            relationship_memory: opsional, untuk akses data hubungan
        """
        self.relationship_memory = relationship_memory
        self.rankings = {}  # {user_id: {type: [rankings]}}
        
        # Bobot untuk perhitungan score
        self.weights = {
            'total_interactions': 0.30,
            'intimacy_level': 0.40,
            'duration': 0.20,
            'climax_count': 0.10,
        }
        
        logger.info("✅ RankingSystem initialized")
        
    # =========================================================================
    # CALCULATE SCORE
    # =========================================================================
    
    async def calculate_score(self, relationship_data: Dict) -> float:
        """
        Hitung score untuk ranking
        
        Formula:
        Score = (total_interactions * 0.3) + 
                (intimacy_level * 0.4) + 
                (duration_in_chats * 0.2) + 
                (climax_count * 0.1)
        """
        total_interactions = relationship_data.get('total_interactions', 0)
        intimacy_level = relationship_data.get('intimacy_level', 1)
        climax_count = relationship_data.get('total_climax', 0)
        
        # Duration dalam chats (bukan waktu real)
        duration_score = min(100, total_interactions) / 100
        
        # Normalisasi komponen
        interactions_score = min(100, total_interactions) / 100
        intimacy_score = intimacy_level / 12
        climax_score = min(50, climax_count) / 50
        
        # Hitung weighted score
        score = (
            interactions_score * self.weights['total_interactions'] +
            intimacy_score * self.weights['intimacy_level'] +
            duration_score * self.weights['duration'] +
            climax_score * self.weights['climax_count']
        ) * 100
        
        return round(score, 2)
        
    # =========================================================================
    # UPDATE RANKINGS
    # =========================================================================
    
    async def update_rankings(self, user_id: int):
        """
        Update rankings untuk user
        Dipanggil setiap ada interaksi baru
        """
        if not self.relationship_memory:
            logger.warning("relationship_memory not set, cannot update rankings")
            return
            
        # Get all relationships for user
        relationships = await self.relationship_memory.get_all_relationships(user_id)
        
        if not relationships:
            return
            
        # Calculate scores for each
        ranked = []
        for rel in relationships:
            score = await self.calculate_score(rel)
            ranked.append({
                'role': rel['role'],
                'status': rel.get('status', 'hts'),
                'score': score,
                'total_interactions': rel.get('total_interactions', 0),
                'intimacy_level': rel.get('intimacy_level', 1),
                'total_climax': rel.get('total_climax', 0),
                'last_interaction': rel.get('last_interaction', 0),
                'created_at': rel.get('created_at', 0)
            })
            
        # Sort by score (descending)
        ranked.sort(key=lambda x: x['score'], reverse=True)
        
        # Store TOP 10 in database
        self.rankings[str(user_id)] = {
            'hts': [r for r in ranked if r['status'] == 'hts'][:10],
            'fwb': [r for r in ranked if r['status'] == 'fwb'][:10],
            'pacar': [r for r in ranked if r['status'] == 'pacar'][:10],
            'all': ranked[:10],
            'updated_at': time.time()
        }
        
        logger.info(f"📊 Updated rankings for user {user_id}: TOP 10 stored")
        
        return self.rankings[str(user_id)]
        
    # =========================================================================
    # GET RANKINGS (FOR DISPLAY)
    # =========================================================================
    
    async def get_top_5_hts(self, user_id: int) -> List[Dict]:
        """Get TOP 5 HTS untuk ditampilkan ke user"""
        user_key = str(user_id)
        
        if user_key not in self.rankings:
            await self.update_rankings(user_id)
            
        rankings = self.rankings.get(user_key, {})
        hts_list = rankings.get('hts', [])
        
        return hts_list[:5]
        
    async def get_top_5_fwb(self, user_id: int) -> List[Dict]:
        """Get TOP 5 FWB untuk ditampilkan"""
        user_key = str(user_id)
        
        if user_key not in self.rankings:
            await self.update_rankings(user_id)
            
        rankings = self.rankings.get(user_key, {})
        fwb_list = rankings.get('fwb', [])
        
        return fwb_list[:5]
        
    async def get_top_5_all(self, user_id: int) -> List[Dict]:
        """Get TOP 5 semua role"""
        user_key = str(user_id)
        
        if user_key not in self.rankings:
            await self.update_rankings(user_id)
            
        rankings = self.rankings.get(user_key, {})
        all_list = rankings.get('all', [])
        
        return all_list[:5]
        
    # =========================================================================
    # GET FULL LIST (FOR SELECTION)
    # =========================================================================
    
    async def get_all_hts(self, user_id: int) -> List[Dict]:
        """Get semua HTS (untuk selection)"""
        if not self.relationship_memory:
            return []
            
        relationships = await self.relationship_memory.get_all_relationships(user_id)
        hts_list = [r for r in relationships if r.get('status') == 'hts']
        
        for hts in hts_list:
            hts['score'] = await self.calculate_score(hts)
            
        hts_list.sort(key=lambda x: x['score'], reverse=True)
        
        return hts_list
        
    async def get_role_by_rank(self, user_id: int, rank: int, status: str = 'hts') -> Optional[Dict]:
        """Get role berdasarkan peringkat"""
        if status == 'hts':
            top_list = await self.get_all_hts(user_id)
        else:
            if not self.relationship_memory:
                return None
            relationships = await self.relationship_memory.get_all_relationships(user_id)
            top_list = [r for r in relationships if r.get('status') == status]
            
        if 1 <= rank <= len(top_list):
            return top_list[rank - 1]
            
        return None
        
    # =========================================================================
    # FORMAT FOR DISPLAY
    # =========================================================================
    
    def format_hts_list(self, hts_list: List[Dict], show_all: bool = False) -> str:
        """Format HTS list untuk ditampilkan"""
        if not hts_list:
            return "Belum ada HTS. Mulai role dulu dengan /start"
            
        lines = ["📋 **DAFTAR HTS**"]
        
        if show_all:
            lines.append("_(menampilkan semua, pilih dengan /hts- [nomor atau nama])_")
        else:
            lines.append("_(TOP 5, untuk lihat semua ketik /htslist all)_")
            
        lines.append("")
        
        for i, hts in enumerate(hts_list[:5] if not show_all else hts_list, 1):
            status_symbol = "💕 FWB" if hts.get('status') == 'fwb' else "💘 Pacar" if hts.get('status') == 'pacar' else "🔹 HTS"
            lines.append(
                f"{i}. **{hts['role'].title()}** {status_symbol}\n"
                f"   • Level {hts.get('intimacy_level', 1)}/12 | "
                f"{hts.get('total_interactions', 0)} chat | "
                f"{hts.get('total_climax', 0)} climax\n"
                f"   • Score: {hts.get('score', 0):.1f}"
            )
            
        lines.append("")
        lines.append("💡 **Cara memanggil:**")
        lines.append("• `/hts-1` - Panggil HTS ranking 1")
        lines.append("• `/hts- ipar` - Panggil role ipar")
        
        return "\n".join(lines)


__all__ = ['RankingSystem']
