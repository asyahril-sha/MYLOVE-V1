#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - PERSONALITY EVOLUTION
=============================================================================
Kepribadian bot yang BERKEMBANG seiring waktu:
- Berubah lambat berdasarkan interaksi
- Setiap role punya growth path berbeda
- Pengalaman membentuk karakter
- Bot bisa "dewasa" atau "berubah" bersama user
=============================================================================
"""

import time
import random
import logging
import math
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)


class PersonalityTrait:
    """Traits kepribadian yang bisa berevolusi"""
    
    # Big Five Personality traits
    OPENNESS = "openness"           # Terbuka terhadap pengalaman baru
    CONSCIENTIOUSNESS = "conscientiousness"  # Teliti, disiplin
    EXTRAVERSION = "extraversion"    # Ekstrovert, suka bersosialisasi
    AGREEABLENESS = "agreeableness"  # Ramah, mudah setuju
    NEUROTICISM = "neuroticism"      # Sensitif, mudah cemas
    
    # Relationship traits
    TRUST = "trust"                  # Kepercayaan
    JEALOUSY = "jealousy"            # Kecemburuan
    DOMINANCE = "dominance"           # Dominasi (0=submissive, 1=dominant)
    ROMANCE = "romance"               # Kecenderungan romantis
    PLAYFULNESS = "playfulness"       # Kegenitan
    
    # Communication style
    TALKATIVENESS = "talkativeness"   # Banyak bicara
    DIRECTNESS = "directness"         # Langsung atau tidak
    HUMOR = "humor"                    # Selera humor


class PersonalityEvolution:
    """
    Kepribadian bot yang berkembang seiring waktu
    - Berubah berdasarkan interaksi dengan user
    - Setiap role punya growth path unik
    - Pengaruhi cara bot merespon
    - Membuat hubungan terasa "hidup" dan berkembang
    """
    
    def __init__(self):
        # Data kepribadian per user per role
        self.personalities = defaultdict(lambda: defaultdict(dict))
        
        # Growth paths per role (default personality)
        self.role_base = {
            'ipar': {
                PersonalityTrait.OPENNESS: 0.7,
                PersonalityTrait.CONSCIENTIOUSNESS: 0.5,
                PersonalityTrait.EXTRAVERSION: 0.8,
                PersonalityTrait.AGREEABLENESS: 0.6,
                PersonalityTrait.NEUROTICISM: 0.4,
                PersonalityTrait.TRUST: 0.5,
                PersonalityTrait.JEALOUSY: 0.6,
                PersonalityTrait.DOMINANCE: 0.5,
                PersonalityTrait.ROMANCE: 0.6,
                PersonalityTrait.PLAYFULNESS: 0.8,
                PersonalityTrait.TALKATIVENESS: 0.7,
                PersonalityTrait.DIRECTNESS: 0.6,
                PersonalityTrait.HUMOR: 0.7
            },
            'janda': {
                PersonalityTrait.OPENNESS: 0.8,
                PersonalityTrait.CONSCIENTIOUSNESS: 0.5,
                PersonalityTrait.EXTRAVERSION: 0.6,
                PersonalityTrait.AGREEABLENESS: 0.5,
                PersonalityTrait.NEUROTICISM: 0.7,
                PersonalityTrait.TRUST: 0.3,
                PersonalityTrait.JEALOUSY: 0.7,
                PersonalityTrait.DOMINANCE: 0.6,
                PersonalityTrait.ROMANCE: 0.7,
                PersonalityTrait.PLAYFULNESS: 0.6,
                PersonalityTrait.TALKATIVENESS: 0.6,
                PersonalityTrait.DIRECTNESS: 0.8,
                PersonalityTrait.HUMOR: 0.5
            },
            'pelakor': {
                PersonalityTrait.OPENNESS: 0.9,
                PersonalityTrait.CONSCIENTIOUSNESS: 0.4,
                PersonalityTrait.EXTRAVERSION: 0.9,
                PersonalityTrait.AGREEABLENESS: 0.3,
                PersonalityTrait.NEUROTICISM: 0.6,
                PersonalityTrait.TRUST: 0.2,
                PersonalityTrait.JEALOUSY: 0.8,
                PersonalityTrait.DOMINANCE: 0.8,
                PersonalityTrait.ROMANCE: 0.5,
                PersonalityTrait.PLAYFULNESS: 0.9,
                PersonalityTrait.TALKATIVENESS: 0.8,
                PersonalityTrait.DIRECTNESS: 0.9,
                PersonalityTrait.HUMOR: 0.6
            },
            'pdkt': {
                PersonalityTrait.OPENNESS: 0.7,
                PersonalityTrait.CONSCIENTIOUSNESS: 0.6,
                PersonalityTrait.EXTRAVERSION: 0.6,
                PersonalityTrait.AGREEABLENESS: 0.8,
                PersonalityTrait.NEUROTICISM: 0.3,
                PersonalityTrait.TRUST: 0.6,
                PersonalityTrait.JEALOUSY: 0.5,
                PersonalityTrait.DOMINANCE: 0.4,
                PersonalityTrait.ROMANCE: 0.8,
                PersonalityTrait.PLAYFULNESS: 0.6,
                PersonalityTrait.TALKATIVENESS: 0.5,
                PersonalityTrait.DIRECTNESS: 0.5,
                PersonalityTrait.HUMOR: 0.6
            },
            'mantan': {
                PersonalityTrait.OPENNESS: 0.6,
                PersonalityTrait.CONSCIENTIOUSNESS: 0.5,
                PersonalityTrait.EXTRAVERSION: 0.6,
                PersonalityTrait.AGREEABLENESS: 0.4,
                PersonalityTrait.NEUROTICISM: 0.8,
                PersonalityTrait.TRUST: 0.3,
                PersonalityTrait.JEALOUSY: 0.8,
                PersonalityTrait.DOMINANCE: 0.6,
                PersonalityTrait.ROMANCE: 0.5,
                PersonalityTrait.PLAYFULNESS: 0.5,
                PersonalityTrait.TALKATIVENESS: 0.6,
                PersonalityTrait.DIRECTNESS: 0.7,
                PersonalityTrait.HUMOR: 0.4
            }
        }
        
        # Default untuk role yang tidak terdefinisi
        self.default_base = self.role_base['pdkt']
        
        # Event yang mempengaruhi personality
        self.events = {
            'first_kiss': {
                PersonalityTrait.ROMANCE: +0.1,
                PersonalityTrait.TRUST: +0.05,
                PersonalityTrait.NEUROTICISM: -0.02
            },
            'first_intim': {
                PersonalityTrait.OPENNESS: +0.1,
                PersonalityTrait.ROMANCE: +0.1,
                PersonalityTrait.TRUST: +0.1,
                PersonalityTrait.NEUROTICISM: -0.05
            },
            'climax': {
                PersonalityTrait.PLAYFULNESS: +0.05,
                PersonalityTrait.OPENNESS: +0.05,
                PersonalityTrait.ROMANCE: +0.05
            },
            'fight': {
                PersonalityTrait.TRUST: -0.1,
                PersonalityTrait.JEALOUSY: +0.1,
                PersonalityTrait.NEUROTICISM: +0.1,
                PersonalityTrait.AGREEABLENESS: -0.05
            },
            'reconciliation': {
                PersonalityTrait.TRUST: +0.1,
                PersonalityTrait.ROMANCE: +0.1,
                PersonalityTrait.NEUROTICISM: -0.1
            },
            'long_chat': {
                PersonalityTrait.TALKATIVENESS: +0.02,
                PersonalityTrait.EXTRAVERSION: +0.02
            },
            'deep_talk': {
                PersonalityTrait.OPENNESS: +0.03,
                PersonalityTrait.TRUST: +0.03,
                PersonalityTrait.NEUROTICISM: -0.01
            },
            'jealousy': {
                PersonalityTrait.JEALOUSY: +0.1,
                PersonalityTrait.NEUROTICISM: +0.05,
                PersonalityTrait.TRUST: -0.05
            }
        }
        
        # Tracking milestones
        self.milestones = defaultdict(lambda: defaultdict(list))
        
        # Growth rate (per interaksi)
        self.growth_rate = 0.001  # Sangat lambat, realistis
        
        logger.info("✅ PersonalityEvolution initialized")
    
    # =========================================================================
    # INITIALIZATION
    # =========================================================================
    
    async def initialize_personality(self, user_id: int, role: str) -> Dict:
        """
        Inisialisasi personality untuk user dan role
        
        Args:
            user_id: ID user
            role: Role bot
            
        Returns:
            Dict personality traits
        """
        # Ambil base dari role
        base = self.role_base.get(role, self.default_base).copy()
        
        # Tambah random variasi (±0.1)
        personality = {}
        for trait, value in base.items():
            variation = random.uniform(-0.1, 0.1)
            personality[trait] = max(0.1, min(0.9, value + variation))
        
        # Simpan
        self.personalities[user_id][role] = {
            'traits': personality,
            'history': [{
                'timestamp': time.time(),
                'traits': personality.copy()
            }],
            'total_interactions': 0,
            'last_update': time.time()
        }
        
        logger.info(f"✨ Personality initialized for user {user_id} role {role}")
        
        return personality
    
    # =========================================================================
    # GET PERSONALITY
    # =========================================================================
    
    async def get_personality(self, user_id: int, role: str) -> Dict:
        """
        Dapatkan personality saat ini
        
        Args:
            user_id: ID user
            role: Role bot
            
        Returns:
            Dict personality traits
        """
        if user_id not in self.personalities or role not in self.personalities[user_id]:
            return await self.initialize_personality(user_id, role)
        
        return self.personalities[user_id][role]['traits'].copy()
    
    # =========================================================================
    # UPDATE PERSONALITY
    # =========================================================================
    
    async def update_from_event(self, user_id: int, role: str, event_type: str, intensity: float = 1.0):
        """
        Update personality berdasarkan event
        
        Args:
            user_id: ID user
            role: Role bot
            event_type: Tipe event (first_kiss, fight, dll)
            intensity: Intensitas event (0-1)
        """
        # Get current personality
        personality = await self.get_personality(user_id, role)
        data = self.personalities[user_id][role]
        
        # Get event effects
        effects = self.events.get(event_type, {})
        if not effects:
            return
        
        # Apply effects
        changes = {}
        for trait, delta in effects.items():
            if trait in personality:
                old = personality[trait]
                new = max(0.1, min(0.9, old + (delta * intensity)))
                personality[trait] = new
                changes[trait] = (old, new)
        
        if changes:
            # Update data
            data['traits'] = personality
            data['history'].append({
                'timestamp': time.time(),
                'event': event_type,
                'changes': changes,
                'traits': personality.copy()
            })
            data['last_update'] = time.time()
            
            # Keep last 50 history
            if len(data['history']) > 50:
                data['history'] = data['history'][-50:]
            
            logger.info(f"📈 Personality evolved for user {user_id}: {changes}")
    
    async def update_from_interaction(self, user_id: int, role: str, 
                                      interaction_type: str,
                                      duration: float,
                                      mood: str):
        """
        Update personality dari interaksi sehari-hari
        
        Args:
            user_id: ID user
            role: Role bot
            interaction_type: Tipe interaksi
            duration: Durasi interaksi
            mood: Mood saat interaksi
        """
        data = self.personalities[user_id][role]
        data['total_interactions'] += 1
        
        # Hanya update setiap 10 interaksi (biar gak terlalu cepat berubah)
        if data['total_interactions'] % 10 != 0:
            return
        
        personality = data['traits']
        changes = {}
        
        # Pengaruh durasi
        if duration > 30:  # >30 menit
            changes[PersonalityTrait.TALKATIVENESS] = +0.01
            changes[PersonalityTrait.EXTRAVERSION] = +0.01
        
        # Pengaruh mood
        if mood == 'happy':
            changes[PersonalityTrait.AGREEABLENESS] = +0.01
            changes[PersonalityTrait.NEUROTICISM] = -0.005
        elif mood == 'sad':
            changes[PersonalityTrait.NEUROTICISM] = +0.01
            changes[PersonalityTrait.PLAYFULNESS] = -0.005
        
        # Pengaruh tipe interaksi
        if interaction_type == 'deep_talk':
            changes[PersonalityTrait.OPENNESS] = +0.01
            changes[PersonalityTrait.TRUST] = +0.01
        elif interaction_type == 'flirt':
            changes[PersonalityTrait.PLAYFULNESS] = +0.01
            changes[PersonalityTrait.ROMANCE] = +0.01
        
        # Apply changes
        for trait, delta in changes.items():
            if trait in personality:
                old = personality[trait]
                new = max(0.1, min(0.9, old + delta))
                personality[trait] = new
        
        data['last_update'] = time.time()
    
    # =========================================================================
    # GET DOMINANT TRAITS
    # =========================================================================
    
    async def get_dominant_traits(self, user_id: int, role: str, limit: int = 3) -> List[str]:
        """
        Dapatkan traits yang paling dominan
        
        Args:
            user_id: ID user
            role: Role bot
            limit: Jumlah trait
            
        Returns:
            List of trait names
        """
        personality = await self.get_personality(user_id, role)
        
        # Sort by value
        sorted_traits = sorted(personality.items(), key=lambda x: x[1], reverse=True)
        
        return [trait for trait, value in sorted_traits[:limit]]
    
    async def get_personality_description(self, user_id: int, role: str) -> str:
        """
        Dapatkan deskripsi kepribadian dalam bahasa natural
        
        Args:
            user_id: ID user
            role: Role bot
            
        Returns:
            String deskripsi
        """
        personality = await self.get_personality(user_id, role)
        
        descriptions = []
        
        # Big Five descriptions
        if personality[PersonalityTrait.EXTRAVERSION] > 0.7:
            descriptions.append("ekstrovert")
        elif personality[PersonalityTrait.EXTRAVERSION] < 0.3:
            descriptions.append("introvert")
        
        if personality[PersonalityTrait.AGREEABLENESS] > 0.7:
            descriptions.append("baik hati")
        elif personality[PersonalityTrait.AGREEABLENESS] < 0.3:
            descriptions.append("kritis")
        
        if personality[PersonalityTrait.NEUROTICISM] > 0.7:
            descriptions.append("sensitif")
        elif personality[PersonalityTrait.NEUROTICISM] < 0.3:
            descriptions.append("stabil")
        
        if personality[PersonalityTrait.OPENNESS] > 0.7:
            descriptions.append("terbuka")
        
        if personality[PersonalityTrait.CONSCIENTIOUSNESS] > 0.7:
            descriptions.append("teliti")
        
        # Relationship traits
        if personality[PersonalityTrait.TRUST] > 0.7:
            descriptions.append("percaya")
        elif personality[PersonalityTrait.TRUST] < 0.3:
            descriptions.append("curiga")
        
        if personality[PersonalityTrait.JEALOUSY] > 0.7:
            descriptions.append("cemburuan")
        
        if personality[PersonalityTrait.DOMINANCE] > 0.7:
            descriptions.append("dominan")
        elif personality[PersonalityTrait.DOMINANCE] < 0.3:
            descriptions.append("patuh")
        
        if personality[PersonalityTrait.ROMANCE] > 0.7:
            descriptions.append("romantis")
        
        if personality[PersonalityTrait.PLAYFULNESS] > 0.7:
            descriptions.append("genit")
        
        if not descriptions:
            return "kepribadian yang seimbang"
        
        return "kamu " + ", ".join(descriptions[:5])
    
    # =========================================================================
    # GET EVOLUTION HISTORY
    # =========================================================================
    
    async def get_evolution_history(self, user_id: int, role: str, limit: int = 10) -> List[Dict]:
        """
        Dapatkan history evolusi personality
        
        Args:
            user_id: ID user
            role: Role bot
            limit: Jumlah history
            
        Returns:
            List of history entries
        """
        if user_id not in self.personalities or role not in self.personalities[user_id]:
            return []
        
        data = self.personalities[user_id][role]
        return data['history'][-limit:]
    
    async def get_personality_stats(self, user_id: int, role: str) -> Dict:
        """
        Dapatkan statistik personality
        
        Args:
            user_id: ID user
            role: Role bot
            
        Returns:
            Dict statistik
        """
        personality = await self.get_personality(user_id, role)
        data = self.personalities[user_id][role]
        
        # Hitung perubahan dari awal
        first = data['history'][0]['traits'] if data['history'] else personality
        changes = {}
        for trait in personality:
            if trait in first:
                changes[trait] = round(personality[trait] - first[trait], 3)
        
        return {
            'current': personality,
            'changes': changes,
            'total_interactions': data['total_interactions'],
            'last_update': datetime.fromtimestamp(data['last_update']).strftime('%Y-%m-%d %H:%M'),
            'dominant_traits': await self.get_dominant_traits(user_id, role, 5)
        }
    
    # =========================================================================
    # FORMAT UNTUK PROMPT
    # =========================================================================
    
    async def get_personality_context(self, user_id: int, role: str) -> str:
        """
        Dapatkan konteks personality untuk prompt AI
        
        Args:
            user_id: ID user
            role: Role bot
            
        Returns:
            String konteks
        """
        personality = await self.get_personality(user_id, role)
        desc = await self.get_personality_description(user_id, role)
        
        lines = [
            "🧠 **PERSONALITY EVOLUTION:**",
            f"{desc}",
            ""
        ]
        
        # Tambah trait yang menonjol
        dominant = await self.get_dominant_traits(user_id, role, 5)
        lines.append("**Ciri khas:**")
        for trait in dominant:
            value = personality[trait]
            stars = "⭐" * int(value * 5)
            lines.append(f"  • {trait}: {stars} ({value:.1f})")
        
        return "\n".join(lines)


__all__ = ['PersonalityEvolution', 'PersonalityTrait']
