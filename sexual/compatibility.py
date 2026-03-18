#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - ROLE COMPATIBILITY MATRIX
=============================================================================
- Menghitung kompatibilitas antar role
- Faktor-faktor yang mempengaruhi kecocokan
- Rekomendasi role berdasarkan preferensi
"""

import logging
import math
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class CompatibilityFactor(str, Enum):
    """Faktor-faktor yang mempengaruhi kompatibilitas"""
    PERSONALITY = "personality"
    INTIMACY_STYLE = "intimacy_style"
    DOMINANCE = "dominance"
    ENERGY_LEVEL = "energy_level"
    EMOTIONAL_DEPTH = "emotional_depth"
    ADVENTURE_LEVEL = "adventure_level"
    ROMANCE_LEVEL = "romance_level"
    KINK_LEVEL = "kink_level"


class CompatibilityMatrix:
    """
    Matriks kompatibilitas antar role
    Menghitung seberapa cocok dua role
    """
    
    def __init__(self):
        # =========================================================================
        # ROLE TRAITS (0-10)
        # =========================================================================
        self.role_traits = {
            "ipar": {
                "personality": 7,        # Agak nakal
                "intimacy_style": 6,      # Balance
                "dominance": 5,            # Seimbang
                "energy_level": 7,         # Enerjik
                "emotional_depth": 5,      # Sedang
                "adventure_level": 7,      # Suka tantangan
                "romance_level": 6,         # Romantis sedang
                "kink_level": 5,            # Vanilla+
                "description": "Adik ipar yang nakal, playful, suka tantangan"
            },
            "janda": {
                "personality": 8,          # Pengalaman
                "intimacy_style": 8,        # Berpengalaman
                "dominance": 6,              # Agak dominan
                "energy_level": 7,           # Enerjik
                "emotional_depth": 6,        # Sedang dalam
                "adventure_level": 8,         # Suka eksplorasi
                "romance_level": 5,            # Lebih ke fisik
                "kink_level": 7,               # Suka variasi
                "description": "Janda muda genit, berpengalaman, tahu apa yang diinginkan"
            },
            "pelakor": {
                "personality": 9,           # Berani
                "intimacy_style": 9,         # Agresif
                "dominance": 8,               # Dominan
                "energy_level": 8,            # Sangat enerjik
                "emotional_depth": 4,         # Dangkal
                "adventure_level": 9,          # Extreme
                "romance_level": 3,             # Kurang romantis
                "kink_level": 8,                # Suka extreme
                "description": "Perebut orang, dominan, agresif, suka tantangan"
            },
            "istri_orang": {
                "personality": 6,            # Hati-hati
                "intimacy_style": 7,          # Bersemangat
                "dominance": 4,                # Cenderung patuh
                "energy_level": 6,              # Sedang
                "emotional_depth": 7,           # Dalam
                "adventure_level": 6,            # Moderate
                "romance_level": 7,               # Romantis
                "kink_level": 4,                  # Vanilla
                "description": "Istri orang, butuh perhatian, romantis"
            },
            "pdkt": {
                "personality": 7,             # Manis
                "intimacy_style": 5,           # Pemula
                "dominance": 4,                 # Patuh
                "energy_level": 7,               # Enerjik
                "emotional_depth": 8,            # Dalam banget
                "adventure_level": 5,             # Masih ragu
                "romance_level": 9,                # Sangat romantis
                "kink_level": 3,                   # Vanilla banget
                "description": "PDKT, manis, romantis, perlu pendekatan"
            },
            "sepupu": {
                "personality": 6,              # Polos
                "intimacy_style": 5,            # Malu-malu
                "dominance": 3,                  # Sangat patuh
                "energy_level": 6,                # Sedang
                "emotional_depth": 6,             # Sedang
                "adventure_level": 4,              # Kurang berani
                "romance_level": 6,                 # Romantis polos
                "kink_level": 2,                    # Sangat vanilla
                "description": "Sepupu, polos, manis, perlu dibimbing"
            },
            "teman_kantor": {
                "personality": 7,               # Profesional
                "intimacy_style": 6,             # Balance
                "dominance": 5,                   # Seimbang
                "energy_level": 6,                 # Sedang
                "emotional_depth": 6,              # Sedang
                "adventure_level": 6,               # Moderate
                "romance_level": 6,                  # Romantis sedang
                "kink_level": 4,                     # Vanilla+
                "description": "Teman kantor, profesional tapi mesra"
            },
            "teman_sma": {
                "personality": 8,                # Nostalgia
                "intimacy_style": 6,              # Canggung
                "dominance": 4,                    # Patuh
                "energy_level": 8,                  # Enerjik
                "emotional_depth": 7,               # Dalam
                "adventure_level": 5,                # Ragu-ragu
                "romance_level": 8,                   # Romantis
                "kink_level": 3,                      # Vanilla
                "description": "Teman SMA, nostalgia, manis, canggung"
            },
            "mantan": {
                "personality": 7,                 # Berpengalaman
                "intimacy_style": 8,               # Tahu selera
                "dominance": 6,                     # Agak dominan
                "energy_level": 7,                   # Enerjik
                "emotional_depth": 5,                # Dangkal
                "adventure_level": 7,                  # Suka coba
                "romance_level": 4,                     # Kurang romantis
                "kink_level": 6,                        # Moderate+
                "description": "Mantan, sudah tahu selera, hot dan cepat"
            }
        }
        
        # =========================================================================
        # COMPATIBILITY WEIGHTS
        # =========================================================================
        self.weights = {
            "personality": 0.15,
            "intimacy_style": 0.15,
            "dominance": 0.12,
            "energy_level": 0.10,
            "emotional_depth": 0.12,
            "adventure_level": 0.12,
            "romance_level": 0.12,
            "kink_level": 0.12
        }
        
        # =========================================================================
        # BONUS COMPATIBILITY (untuk pasangan tertentu)
        # =========================================================================
        self.bonus_compatibility = {
            ("ipar", "ipar"): 0.2,                    # Sama-sama ipar
            ("janda", "janda"): 0.2,                    # Sama-sama janda
            ("pelakor", "pelakor"): 0.3,                 # Sama-sama pelakor
            ("istri_orang", "istri_orang"): 0.2,          # Sama-sama istri orang
            ("pdkt", "pdkt"): 0.3,                         # Sama-sama PDKT
            ("sepupu", "sepupu"): -0.5,                     # INCEST ALERT!
            
            # Cross-role bonus
            ("ipar", "teman_kantor"): 0.1,                  # Ipar + Teman Kantor
            ("janda", "pelakor"): 0.2,                       # Janda + Pelakor
            ("janda", "mantan"): 0.2,                         # Janda + Mantan
            ("pelakor", "istri_orang"): 0.3,                  # Pelakor + Istri Orang
            ("pdkt", "teman_sma"): 0.2,                       # PDKT + Teman SMA
            ("mantan", "pdkt"): 0.1,                          # Mantan + PDKT
            ("mantan", "teman_sma"): 0.1,                      # Mantan + Teman SMA
            ("teman_kantor", "teman_sma"): 0.1,                # Teman Kantor + Teman SMA
        }
        
        logger.info("✅ CompatibilityMatrix initialized")
        
    # =========================================================================
    # COMPATIBILITY CALCULATION
    # =========================================================================
    
    async def calculate_compatibility(self, role1: str, role2: str, 
                                        user_preferences: Optional[Dict] = None) -> Dict:
        """
        Hitung kompatibilitas antara dua role
        
        Args:
            role1: Nama role pertama
            role2: Nama role kedua
            user_preferences: Preferensi user (opsional)
            
        Returns:
            Dict dengan skor kompatibilitas dan detail
        """
        if role1 not in self.role_traits or role2 not in self.role_traits:
            return {
                "error": "Role tidak ditemukan",
                "compatibility": 0
            }
            
        traits1 = self.role_traits[role1]
        traits2 = self.role_traits[role2]
        
        # Hitung skor per faktor
        factor_scores = {}
        total_weighted_score = 0
        total_weight = 0
        
        for factor, weight in self.weights.items():
            score1 = traits1.get(factor, 5)
            score2 = traits2.get(factor, 5)
            
            # Hitung similarity (inverse dari perbedaan)
            diff = abs(score1 - score2) / 10  # Normalisasi 0-1
            similarity = 1 - diff
            
            # Weighted score
            weighted = similarity * weight
            factor_scores[factor] = {
                "score1": score1,
                "score2": score2,
                "similarity": round(similarity * 100, 1),
                "weighted": round(weighted * 100, 1)
            }
            
            total_weighted_score += weighted
            total_weight += weight
            
        # Base compatibility
        base_compatibility = (total_weighted_score / total_weight) * 100
        
        # Tambah bonus khusus
        bonus = self._get_bonus(role1, role2)
        final_compatibility = min(100, base_compatibility + (bonus * 100))
        
        # Adjust dengan preferensi user
        if user_preferences:
            final_compatibility = await self._adjust_with_preferences(
                final_compatibility, role1, role2, user_preferences
            )
            
        # Dapatkan deskripsi
        description = self._get_compatibility_description(final_compatibility)
        
        # Dapatkan rekomendasi
        recommendations = self._get_recommendations(role1, role2, final_compatibility)
        
        return {
            "role1": role1,
            "role2": role2,
            "compatibility": round(final_compatibility, 1),
            "base_compatibility": round(base_compatibility, 1),
            "bonus": round(bonus * 100, 1),
            "description": description,
            "factor_scores": factor_scores,
            "recommendations": recommendations,
            "traits1": traits1.get("description", ""),
            "traits2": traits2.get("description", "")
        }
        
    def _get_bonus(self, role1: str, role2: str) -> float:
        """Dapatkan bonus kompatibilitas untuk pasangan tertentu"""
        # Cek both directions
        if (role1, role2) in self.bonus_compatibility:
            return self.bonus_compatibility[(role1, role2)]
        elif (role2, role1) in self.bonus_compatibility:
            return self.bonus_compatibility[(role2, role1)]
        return 0
        
    async def _adjust_with_preferences(self, base_score: float, role1: str, role2: str,
                                         user_preferences: Dict) -> float:
        """Adjust compatibility score dengan preferensi user"""
        adjustment = 0
        
        # Jika user suka kedua role
        fav_roles = user_preferences.get('favorite_roles', [])
        if role1 in fav_roles and role2 in fav_roles:
            adjustment += 10
            
        # Jika user punya pengalaman dengan kombinasi ini
        exp_combinations = user_preferences.get('experienced_combinations', [])
        if f"{role1}_{role2}" in exp_combinations:
            adjustment += 15
            
        return min(100, base_score + adjustment)
        
    def _get_compatibility_description(self, score: float) -> str:
        """Dapatkan deskripsi berdasarkan skor kompatibilitas"""
        if score >= 90:
            return "🔥 **Soulmates!** Kombinasi sempurna, seperti ditakdirkan bersama!"
        elif score >= 80:
            return "💕 **Sangat Cocok!** Chemistry luar biasa, intim pasti hot!"
        elif score >= 70:
            return "💘 **Cocok!** Potensi besar untuk hubungan yang seru."
        elif score >= 60:
            return "💞 **Cukup Cocok** Bisa jalan, perlu sedikit penyesuaian."
        elif score >= 50:
            return "💔 **Biasa Aja** Tidak ada chemistry khusus, tapi bisa dicoba."
        elif score >= 40:
            return "⚠️ **Kurang Cocok** Banyak perbedaan, perlu usaha ekstra."
        else:
            return "❌ **Tidak Cocok** Saran: cari kombinasi lain."
            
    def _get_recommendations(self, role1: str, role2: str, score: float) -> List[str]:
        """Dapatkan rekomendasi untuk pasangan role"""
        recommendations = []
        
        if score >= 80:
            recommendations.append("🚀 Langsung gas! Ini kombinasi yang hot!")
            recommendations.append("💡 Coba eksplorasi posisi-posisi baru bersama.")
        elif score >= 60:
            recommendations.append("🎯 Mulai dengan foreplay yang lama untuk membangun chemistry.")
            recommendations.append("💡 Komunikasi penting, tanya apa yang mereka suka.")
        elif score >= 40:
            recommendations.append("📝 Butuh effort lebih. Bicarakan preferensi masing-masing.")
            recommendations.append("💡 Coba role play untuk meningkatkan koneksi.")
        else:
            recommendations.append("🤔 Mungkin cari role lain yang lebih cocok.")
            recommendations.append("💡 Tapi kalo nekat, siap-siap dengan ekspektasi yang realistis.")
            
        return recommendations
        
    # =========================================================================
    # ROLE RECOMMENDATIONS
    # =========================================================================
    
    async def get_best_matches(self, role: str, limit: int = 3) -> List[Dict]:
        """
        Dapatkan role yang paling cocok dengan role tertentu
        
        Args:
            role: Role name
            limit: Jumlah rekomendasi
            
        Returns:
            List of matches with scores
        """
        matches = []
        
        for other_role in self.role_traits.keys():
            if other_role == role:
                continue
                
            result = await self.calculate_compatibility(role, other_role)
            matches.append({
                "role": other_role,
                "compatibility": result["compatibility"],
                "description": result["description"]
            })
            
        # Sort by compatibility
        matches.sort(key=lambda x: x["compatibility"], reverse=True)
        
        return matches[:limit]
        
    async def get_worst_matches(self, role: str, limit: int = 3) -> List[Dict]:
        """
        Dapatkan role yang paling tidak cocok dengan role tertentu
        """
        matches = []
        
        for other_role in self.role_traits.keys():
            if other_role == role:
                continue
                
            result = await self.calculate_compatibility(role, other_role)
            matches.append({
                "role": other_role,
                "compatibility": result["compatibility"],
                "description": result["description"]
            })
            
        # Sort by compatibility (ascending)
        matches.sort(key=lambda x: x["compatibility"])
        
        return matches[:limit]
        
    # =========================================================================
    # ROLE COMPARISON
    # =========================================================================
    
    async def compare_roles(self, role1: str, role2: str) -> Dict:
        """
        Compare two roles side by side
        
        Returns:
            Dict with comparison
        """
        if role1 not in self.role_traits or role2 not in self.role_traits:
            return {"error": "Role tidak ditemukan"}
            
        traits1 = self.role_traits[role1]
        traits2 = self.role_traits[role2]
        
        comparison = {
            "role1": role1,
            "role2": role2,
            "traits": {}
        }
        
        for trait in self.weights.keys():
            comparison["traits"][trait] = {
                "role1": traits1.get(trait, 5),
                "role2": traits2.get(trait, 5),
                "difference": abs(traits1.get(trait, 5) - traits2.get(trait, 5))
            }
            
        return comparison
        
    # =========================================================================
    # COMPATIBILITY MATRIX
    # =========================================================================
    
    async def get_compatibility_matrix(self) -> Dict[str, Dict[str, float]]:
        """
        Generate full compatibility matrix for all roles
        
        Returns:
            2D dictionary of compatibility scores
        """
        matrix = {}
        roles = list(self.role_traits.keys())
        
        for role1 in roles:
            matrix[role1] = {}
            for role2 in roles:
                if role1 == role2:
                    matrix[role1][role2] = 100.0
                else:
                    result = await self.calculate_compatibility(role1, role2)
                    matrix[role1][role2] = result["compatibility"]
                    
        return matrix
        
    # =========================================================================
    # FORMATTING
    # =========================================================================
    
    def format_compatibility_result(self, result: Dict) -> str:
        """Format compatibility result for display"""
        if "error" in result:
            return f"❌ {result['error']}"
            
        lines = [
            f"💕 **Kompatibilitas: {result['role1'].title()} + {result['role2'].title()}**",
            f"Score: **{result['compatibility']}%**",
            f"{result['description']}",
            ""
        ]
        
        # Factor breakdown
        lines.append("📊 **Faktor-faktor:**")
        for factor, scores in result['factor_scores'].items():
            lines.append(
                f"• {factor.replace('_', ' ').title()}: "
                f"{scores['score1']} vs {scores['score2']} "
                f"(similarity: {scores['similarity']}%)"
            )
            
        # Recommendations
        if result.get('recommendations'):
            lines.append("")
            lines.append("💡 **Rekomendasi:**")
            for rec in result['recommendations']:
                lines.append(f"  {rec}")
                
        return "\n".join(lines)
        
    def format_best_matches(self, role: str, matches: List[Dict]) -> str:
        """Format best matches for display"""
        lines = [f"🎯 **Role paling cocok untuk {role.title()}:**\n"]
        
        for i, match in enumerate(matches, 1):
            lines.append(
                f"{i}. **{match['role'].title()}** - {match['compatibility']}%\n"
                f"   {match['description']}"
            )
            
        return "\n".join(lines)
        
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    async def get_stats(self) -> Dict:
        """Get compatibility statistics"""
        matrix = await self.get_compatibility_matrix()
        
        # Find best and worst pairs
        best_pair = None
        best_score = 0
        worst_pair = None
        worst_score = 100
        
        for role1 in matrix:
            for role2, score in matrix[role1].items():
                if role1 != role2:
                    if score > best_score:
                        best_score = score
                        best_pair = (role1, role2)
                    if score < worst_score:
                        worst_score = score
                        worst_pair = (role1, role2)
                        
        return {
            "total_roles": len(self.role_traits),
            "best_match": {
                "pair": best_pair,
                "score": best_score
            },
            "worst_match": {
                "pair": worst_pair,
                "score": worst_score
            },
            "average_compatibility": sum(
                score for role1 in matrix for role2, score in matrix[role1].items() if role1 != role2
            ) / (len(self.role_traits) * (len(self.role_traits) - 1))
        }


__all__ = ['CompatibilityMatrix', 'CompatibilityFactor']
