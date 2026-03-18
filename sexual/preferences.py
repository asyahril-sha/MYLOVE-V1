#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - PREFERENCE LEARNING SYSTEM
=============================================================================
- Belajar preferensi user berdasarkan interaksi
- Track favorite positions, areas, activities
- Scoring system untuk setiap preferensi
"""

import time
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
from datetime import datetime

from ..database.repository import Repository
from ..database.models import Preference
from ..utils.logger import setup_logging

logger = logging.getLogger(__name__)


class PreferenceLearner:
    """
    Sistem pembelajaran preferensi user
    Merekam dan memberi score pada preferensi user
    """
    
    def __init__(self, repo: Repository):
        self.repo = repo
        self.cache = {}  # Cache preferences untuk performance
        
        # Bobot untuk update score
        self.weights = {
            'explicit_like': 0.3,      # User explicitly said suka
            'implicit_signal': 0.1,     # Dari konteks (misal: sering dipilih)
            'climax_correlation': 0.2,   # Sering climax dengan item ini
            'duration': 0.1,              # Lama sesi dengan item ini
            'repeat_count': 0.2,          # Berapa kali dipilih
            'recent_boost': 0.1            # Interaksi terakhir
        }
        
        # Preference types
        self.pref_types = [
            'position',      # Posisi sex
            'area',          # Area sensitif
            'activity',      # Aktivitas sexual
            'location',      # Lokasi public sex
            'role',          # Role favorit
            'foreplay',      # Jenis foreplay
            'aftercare'      # Tipe aftercare
        ]
        
        logger.info("✅ PreferenceLearner initialized")
        
    # =========================================================================
    # UPDATE PREFERENCES
    # =========================================================================
    
    async def update_preference(self, user_id: int, pref_type: str, item: str, 
                                  role: Optional[str] = None, signal: float = 0.1,
                                  context: Optional[Dict] = None):
        """
        Update preference score untuk item tertentu
        
        Args:
            user_id: ID user
            pref_type: Tipe preferensi (position, area, etc)
            item: Nama item
            role: Role spesifik (opsional)
            signal: Signal strength (0-1)
            context: Konteks tambahan
        """
        # Ambil preference yang ada
        existing = await self.repo.get_top_preferences(
            user_id, pref_type, role, limit=1
        )
        
        # Hitung delta berdasarkan konteks
        delta = self._calculate_delta(signal, context)
        
        if existing:
            # Update existing
            pref = existing[0]
            new_score = min(1.0, pref.score + delta)
            
            # Simpan ke database
            pref.score = new_score
            pref.count += 1
            pref.last_updated = time.time()
            
            await self.repo.add_preference(pref)
            
        else:
            # Create new
            pref = Preference(
                user_id=user_id,
                role=role,
                pref_type=pref_type,
                item=item,
                score=0.5 + delta,
                count=1,
                last_updated=time.time()
            )
            
            await self.repo.add_preference(pref)
            
        # Update cache
        cache_key = f"{user_id}:{pref_type}:{item}"
        self.cache[cache_key] = {
            'score': 0.5 + delta if not existing else existing[0].score + delta,
            'timestamp': time.time()
        }
        
        logger.debug(f"Updated preference: user {user_id} - {pref_type}:{item} -> {delta:+.2f}")
        
    def _calculate_delta(self, signal: float, context: Optional[Dict]) -> float:
        """Hitung delta score berdasarkan signal dan konteks"""
        delta = signal * self.weights['explicit_like']
        
        if context:
            if context.get('climax'):
                delta += self.weights['climax_correlation']
                
            if context.get('duration', 0) > 10:  # >10 menit
                delta += self.weights['duration'] * 0.5
                
            if context.get('repeat'):
                delta += self.weights['repeat_count'] * 0.3
                
            if context.get('recent'):
                delta += self.weights['recent_boost']
                
        return min(0.3, max(-0.3, delta))  # Batasi perubahan
        
    # =========================================================================
    # RECORD INTERACTIONS
    # =========================================================================
    
    async def record_position(self, user_id: int, position: str, role: str,
                               climax: bool = False, duration: float = 0):
        """Record penggunaan posisi"""
        context = {
            'climax': climax,
            'duration': duration,
            'repeat': True
        }
        
        await self.update_preference(
            user_id=user_id,
            pref_type='position',
            item=position,
            role=role,
            signal=0.2 if climax else 0.1,
            context=context
        )
        
    async def record_area(self, user_id: int, area: str, role: str,
                           reaction: str = 'positive'):
        """Record stimulasi area"""
        signal = 0.15 if reaction == 'positive' else -0.1
        
        await self.update_preference(
            user_id=user_id,
            pref_type='area',
            item=area,
            role=role,
            signal=signal
        )
        
    async def record_activity(self, user_id: int, activity: str, role: str,
                               climax: bool = False):
        """Record aktivitas sexual"""
        await self.update_preference(
            user_id=user_id,
            pref_type='activity',
            item=activity,
            role=role,
            signal=0.15 if climax else 0.05
        )
        
    async def record_location(self, user_id: int, location: str, role: str,
                               thrill_level: int):
        """Record lokasi public sex"""
        signal = thrill_level / 100  # 0-1
        
        await self.update_preference(
            user_id=user_id,
            pref_type='location',
            item=location,
            role=role,
            signal=signal * 0.2
        )
        
    async def record_foreplay(self, user_id: int, foreplay_type: str, role: str,
                               duration: float):
        """Record foreplay"""
        signal = min(0.2, duration / 600)  # Max 10 menit = 0.2
        
        await self.update_preference(
            user_id=user_id,
            pref_type='foreplay',
            item=foreplay_type,
            role=role,
            signal=signal
        )
        
    async def record_aftercare(self, user_id: int, aftercare_type: str, role: str,
                                 satisfaction: int):
        """Record aftercare"""
        signal = satisfaction / 10  # 0-1
        
        await self.update_preference(
            user_id=user_id,
            pref_type='aftercare',
            item=aftercare_type,
            role=role,
            signal=signal * 0.2
        )
        
    # =========================================================================
    # GET PREFERENCES
    # =========================================================================
    
    async def get_top_positions(self, user_id: int, role: Optional[str] = None,
                                  limit: int = 5) -> List[str]:
        """Get top favorite positions"""
        prefs = await self.repo.get_top_preferences(
            user_id, 'position', role, limit
        )
        return [p.item for p in prefs]
        
    async def get_top_areas(self, user_id: int, role: Optional[str] = None,
                              limit: int = 5) -> List[str]:
        """Get top sensitive areas"""
        prefs = await self.repo.get_top_preferences(
            user_id, 'area', role, limit
        )
        return [p.item for p in prefs]
        
    async def get_top_locations(self, user_id: int, role: Optional[str] = None,
                                  limit: int = 5) -> List[str]:
        """Get top public locations"""
        prefs = await self.repo.get_top_preferences(
            user_id, 'location', role, limit
        )
        return [p.item for p in prefs]
        
    async def get_top_activities(self, user_id: int, role: Optional[str] = None,
                                   limit: int = 5) -> List[str]:
        """Get top sexual activities"""
        prefs = await self.repo.get_top_preferences(
            user_id, 'activity', role, limit
        )
        return [p.item for p in prefs]
        
    async def get_top_foreplay(self, user_id: int, role: Optional[str] = None,
                                 limit: int = 5) -> List[str]:
        """Get top foreplay types"""
        prefs = await self.repo.get_top_preferences(
            user_id, 'foreplay', role, limit
        )
        return [p.item for p in prefs]
        
    async def get_top_aftercare(self, user_id: int, role: Optional[str] = None,
                                  limit: int = 5) -> List[str]:
        """Get top aftercare preferences"""
        prefs = await self.repo.get_top_preferences(
            user_id, 'aftercare', role, limit
        )
        return [p.item for p in prefs]
        
    # =========================================================================
    # PREFERENCE ANALYSIS
    # =========================================================================
    
    async def get_role_preferences(self, user_id: int, role: str) -> Dict[str, List[str]]:
        """Get all preferences untuk role tertentu"""
        return {
            'positions': await self.get_top_positions(user_id, role, 3),
            'areas': await self.get_top_areas(user_id, role, 3),
            'locations': await self.get_top_locations(user_id, role, 3),
            'activities': await self.get_top_activities(user_id, role, 3),
            'foreplay': await self.get_top_foreplay(user_id, role, 3),
            'aftercare': await self.get_top_aftercare(user_id, role, 3)
        }
        
    async def get_user_summary(self, user_id: int) -> str:
        """Get summary of user preferences"""
        all_prefs = []
        
        for pref_type in self.pref_types:
            top = await self.repo.get_top_preferences(user_id, pref_type, limit=3)
            if top:
                items = [f"{p.item} ({p.score:.1f})" for p in top]
                all_prefs.append(f"{pref_type.title()}: {', '.join(items)}")
                
        if not all_prefs:
            return "Belum ada data preferensi. Terus berinteraksi untuk belajar!"
            
        return "📊 **Preferensi Kamu:**\n" + "\n".join(all_prefs)
        
    async def get_recommendations(self, user_id: int, role: str) -> Dict[str, List[str]]:
        """
        Dapatkan rekomendasi berdasarkan preferensi
        
        Returns:
            Dict dengan rekomendasi untuk berbagai kategori
        """
        recommendations = {}
        
        # Rekomendasi posisi baru (mirip dengan favorit)
        top_positions = await self.get_top_positions(user_id, role, 3)
        if top_positions:
            # Ini akan diisi dengan posisi serupa dari database
            recommendations['similar_positions'] = [
                f"Mirip dengan {p}" for p in top_positions
            ]
            
        # Rekomendasi area (yang belum dicoba tapi related)
        top_areas = await self.get_top_areas(user_id, role, 3)
        if top_areas:
            recommendations['related_areas'] = [
                f"Eksplorasi area dekat {a}" for a in top_areas
            ]
            
        # Rekomendasi lokasi baru
        top_locations = await self.get_top_locations(user_id, role, 3)
        if top_locations:
            recommendations['new_locations'] = [
                "Coba lokasi baru dengan risk berbeda"
            ]
            
        return recommendations
        
    # =========================================================================
    # PREFERENCE STRENGTH
    # =========================================================================
    
    async def get_preference_strength(self, user_id: int, pref_type: str, 
                                        item: str) -> float:
        """Get strength of specific preference (0-1)"""
        cache_key = f"{user_id}:{pref_type}:{item}"
        
        # Check cache
        if cache_key in self.cache:
            cache_age = time.time() - self.cache[cache_key]['timestamp']
            if cache_age < 3600:  # Cache valid 1 jam
                return self.cache[cache_key]['score']
                
        # Get from database
        prefs = await self.repo.get_top_preferences(user_id, pref_type, limit=20)
        
        for pref in prefs:
            if pref.item.lower() == item.lower():
                self.cache[cache_key] = {
                    'score': pref.score,
                    'timestamp': time.time()
                }
                return pref.score
                
        return 0.5  # Default
        
    async def compare_preferences(self, user_id: int, role1: str, role2: str) -> Dict:
        """
        Compare preferences between two roles
        
        Returns:
            Dict with similarities and differences
        """
        prefs1 = await self.get_role_preferences(user_id, role1)
        prefs2 = await self.get_role_preferences(user_id, role2)
        
        similarities = {}
        differences = {}
        
        for category in prefs1.keys():
            set1 = set(prefs1[category])
            set2 = set(prefs2[category])
            
            common = set1.intersection(set2)
            only1 = set1.difference(set2)
            only2 = set2.difference(set1)
            
            if common:
                similarities[category] = list(common)
            if only1 or only2:
                differences[category] = {
                    role1: list(only1),
                    role2: list(only2)
                }
                
        return {
            'similarities': similarities,
            'differences': differences,
            'compatibility_score': self._calculate_compatibility(prefs1, prefs2)
        }
        
    def _calculate_compatibility(self, prefs1: Dict, prefs2: Dict) -> float:
        """Calculate compatibility score between two preference sets"""
        total_score = 0
        total_categories = 0
        
        for category in prefs1.keys():
            set1 = set(prefs1[category])
            set2 = set(prefs2[category])
            
            if not set1 or not set2:
                continue
                
            # Jaccard similarity
            intersection = len(set1.intersection(set2))
            union = len(set1.union(set2))
            
            if union > 0:
                category_score = intersection / union
                total_score += category_score
                total_categories += 1
                
        return total_score / total_categories if total_categories > 0 else 0.5
        
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    async def get_stats(self, user_id: Optional[int] = None) -> Dict:
        """Get preference statistics"""
        if user_id:
            # Stats for specific user
            total_prefs = 0
            for pref_type in self.pref_types:
                prefs = await self.repo.get_top_preferences(user_id, pref_type, limit=100)
                total_prefs += len(prefs)
                
            return {
                'user_id': user_id,
                'total_preferences': total_prefs,
                'by_type': {
                    pref_type: len(await self.repo.get_top_preferences(user_id, pref_type, limit=100))
                    for pref_type in self.pref_types
                }
            }
        else:
            # Global stats
            return {
                'preference_types': self.pref_types,
                'learning_rate': self.weights
            }
            
    async def clear_cache(self):
        """Clear preference cache"""
        self.cache.clear()
        logger.info("Preference cache cleared")


__all__ = ['PreferenceLearner']
