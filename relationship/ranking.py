#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - RANKING SYSTEM (HTS/FWB)
=============================================================================
- TOP 10 di database
- TOP 5 ditampilkan ke user
- Bisa pilih dari list untuk memulai petualangan
- Ranking berdasarkan total interaksi, intimacy level, durasi
"""

import logging
import math
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RankingSystem:
    """
    Sistem ranking untuk HTS dan FWB
    Menyimpan TOP 10 di database, menampilkan TOP 5 ke user
    """
    
    def __init__(self, relationship_memory):
        self.relationship_memory = relationship_memory
        self.rankings = {}  # {user_id: {type: [rankings]}}
        
        # Bobot untuk perhitungan score
        self.weights = {
            'total_interactions': 0.30,  # 30% - makin sering chat makin tinggi
            'intimacy_level': 0.40,       # 40% - level intimacy
            'duration': 0.20,              # 20% - lama hubungan (dalam chat)
            'climax_count': 0.10,           # 10% - jumlah climax
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
        # Makin banyak chat, makin tinggi
        duration_score = min(100, total_interactions) / 100  # Normalisasi ke 0-1
        
        # Normalisasi komponen
        interactions_score = min(100, total_interactions) / 100
        intimacy_score = intimacy_level / 12  # Level 1-12 -> 0-1
        climax_score = min(50, climax_count) / 50  # Max 50 climax
        
        # Hitung weighted score
        score = (
            interactions_score * self.weights['total_interactions'] +
            intimacy_score * self.weights['intimacy_level'] +
            duration_score * self.weights['duration'] +
            climax_score * self.weights['climax_count']
        ) * 100  # Skala 0-100
        
        return round(score, 2)
        
    # =========================================================================
    # UPDATE RANKINGS
    # =========================================================================
    
    async def update_rankings(self, user_id: int):
        """
        Update rankings untuk user
        Dipanggil setiap ada interaksi baru
        """
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
            'all': ranked[:10],  # TOP 10 overall
            'updated_at': time.time()
        }
        
        logger.info(f"📊 Updated rankings for user {user_id}: TOP 10 stored")
        
        return self.rankings[str(user_id)]
        
    # =========================================================================
    # GET RANKINGS (FOR DISPLAY)
    # =========================================================================
    
    async def get_top_5_hts(self, user_id: int) -> List[Dict]:
        """
        Get TOP 5 HTS untuk ditampilkan ke user
        (Database menyimpan TOP 10, tapi tampilkan TOP 5)
        """
        user_key = str(user_id)
        
        if user_key not in self.rankings:
            await self.update_rankings(user_id)
            
        rankings = self.rankings.get(user_key, {})
        hts_list = rankings.get('hts', [])
        
        # Return TOP 5
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
        """
        Get semua HTS (untuk selection)
        User bisa pilih dari list lengkap, bukan cuma TOP 5
        """
        user_key = str(user_id)
        
        if user_key not in self.rankings:
            await self.update_rankings(user_id)
            
        # Get all relationships
        relationships = await self.relationship_memory.get_all_relationships(user_id)
        
        # Filter HTS only
        hts_list = [r for r in relationships if r.get('status') == 'hts']
        
        # Sort by score
        for hts in hts_list:
            hts['score'] = await self.calculate_score(hts)
            
        hts_list.sort(key=lambda x: x['score'], reverse=True)
        
        return hts_list
        
    async def get_role_by_rank(self, user_id: int, rank: int, status: str = 'hts') -> Optional[Dict]:
        """
        Get role berdasarkan peringkat
        Misal: /hts-1 -> ambil ranking 1
        """
        if status == 'hts':
            top_list = await self.get_all_hts(user_id)
        else:
            # For other statuses
            relationships = await self.relationship_memory.get_all_relationships(user_id)
            top_list = [r for r in relationships if r.get('status') == status]
            
        if 1 <= rank <= len(top_list):
            return top_list[rank - 1]
            
        return None
        
    async def get_role_by_name(self, user_id: int, role_name: str) -> Optional[Dict]:
        """
        Get role by name (case insensitive)
        User bisa panggil langsung: /hts- ipar
        """
        relationships = await self.relationship_memory.get_all_relationships(user_id)
        
        for rel in relationships:
            if rel['role'].lower() == role_name.lower():
                return rel
                
        return None
        
    # =========================================================================
    # FORMAT FOR DISPLAY
    # =========================================================================
    
    def format_hts_list(self, hts_list: List[Dict], show_all: bool = False) -> str:
        """
        Format HTS list untuk ditampilkan
        
        Args:
            hts_list: List of HTS
            show_all: True untuk tampilkan semua, False untuk TOP 5
            
        Returns:
            Formatted string
        """
        if not hts_list:
            return "Belum ada HTS. Mulai role dulu dengan /start"
            
        lines = ["📋 **DAFTAR HTS**"]
        
        if show_all:
            lines.append("_(menampilkan semua, pilih dengan /hts- [nomor atau nama])_")
        else:
            lines.append("_(TOP 5, untuk lihat semua ketik /htslist all)_")
            
        lines.append("")
        
        for i, hts in enumerate(hts_list[:5] if not show_all else hts_list, 1):
            # Status symbol
            if hts.get('status') == 'fwb':
                status_symbol = "💕 FWB"
            elif hts.get('status') == 'pacar':
                status_symbol = "💘 Pacar"
            else:
                status_symbol = "🔹 HTS"
                
            # Format
            lines.append(
                f"{i}. **{hts['role'].title()}** {status_symbol}\n"
                f"   • Level {hts.get('intimacy_level', 1)}/12 | "
                f"{hts.get('total_interactions', 0)} chat | "
                f"{hts.get('total_climax', 0)} climax\n"
                f"   • Score: {hts.get('score', 0):.1f}"
            )
            
        # Add instruction
        lines.append("")
        lines.append("💡 **Cara memanggil:**")
        lines.append("• `/hts-1` - Panggil HTS ranking 1")
        lines.append("• `/hts- ipar` - Panggil role ipar")
        
        return "\n".join(lines)
        
    def format_fwb_list(self, fwb_list: List[Dict]) -> str:
        """Format FWB list"""
        if not fwb_list:
            return "Belum ada FWB. Gunakan /fwb untuk mengubah status HTS jadi FWB"
            
        lines = ["💕 **DAFTAR FWB**"]
        lines.append("_(Friends With Benefits - bisa intim tanpa komitment)_")
        lines.append("")
        
        for i, fwb in enumerate(fwb_list[:5], 1):
            lines.append(
                f"{i}. **{fwb['role'].title()}**\n"
                f"   • Level {fwb.get('intimacy_level', 1)}/12 | "
                f"{fwb.get('total_interactions', 0)} chat\n"
                f"   • Total intim: {fwb.get('total_intim_sessions', 0)}"
            )
            
        return "\n".join(lines)
        
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    async def get_ranking_stats(self, user_id: int) -> Dict:
        """Get ranking statistics"""
        user_key = str(user_id)
        
        if user_key not in self.rankings:
            await self.update_rankings(user_id)
            
        rankings = self.rankings.get(user_key, {})
        
        return {
            'total_hts': len(rankings.get('hts', [])),
            'total_fwb': len(rankings.get('fwb', [])),
            'total_pacar': len(rankings.get('pacar', [])),
            'top_score': rankings.get('all', [{}])[0].get('score', 0) if rankings.get('all') else 0,
            'updated_at': rankings.get('updated_at', 0)
        }


__all__ = ['RankingSystem']
