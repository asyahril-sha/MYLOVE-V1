#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - CHEMISTRY SYSTEM (99% REALISME)
=============================================================================
Sistem chemistry yang menentukan seberapa cocok dua insan
- Bukan angka matematika, tapi perasaan natural
- Berdasarkan analisis AI terhadap interaksi
- Bisa berubah seiring waktu (chemistry bisa tumbuh)
- Rahasia! Tidak ditampilkan sebagai angka mentah
=============================================================================
"""

import random
import time
import logging
import json
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ChemistryLevel(str, Enum):
    """Level chemistry (bukan angka, tapi deskripsi natural)"""
    DINGIN = "dingin"                 # Tidak cocok sama sekali
    BIASA = "biasa"                   # Biasa aja
    HANGAT = "hangat"                  # Mulai ada rasa
    COCOK = "cocok"                    # Cocok
    SANGAT_COCOK = "sangat_cocok"       # Sangat cocok
    SOULMATE = "soulmate"               # Seperti belahan jiwa


class ChemistryScore:
    """
    Chemistry score yang TIDAK ditampilkan sebagai angka
    Hanya sebagai internal untuk AI
    """
    
    def __init__(self, score: float = 50.0):
        self.score = max(0.0, min(100.0, score))  # 0-100 internal
        self.history = []
        self.factors = {}
        self.last_update = time.time()
    
    def get_level(self) -> ChemistryLevel:
        """Konversi score ke level natural"""
        if self.score < 20:
            return ChemistryLevel.DINGIN
        elif self.score < 40:
            return ChemistryLevel.BIASA
        elif self.score < 60:
            return ChemistryLevel.HANGAT
        elif self.score < 80:
            return ChemistryLevel.COCOK
        elif self.score < 95:
            return ChemistryLevel.SANGAT_COCOK
        else:
            return ChemistryLevel.SOULMATE
    
    def get_description(self) -> str:
        """Dapatkan deskripsi natural (bukan angka)"""
        level = self.get_level()
        
        descriptions = {
            ChemistryLevel.DINGIN: [
                "Kayaknya kita kurang cocok...",
                "Gak ada getaran sama sekali.",
                "Biasa aja, kayak teman biasa."
            ],
            ChemistryLevel.BIASA: [
                "Masih biasa, belum ada yang spesial.",
                "Lumayan, tapi masih canggung.",
                "Mungkin butuh waktu lebih."
            ],
            ChemistryLevel.HANGAT: [
                "Mulai ada rasa hangat.",
                "Ada getaran kecil pas ngobrol.",
                "Lumayan nyaman sama kamu."
            ],
            ChemistryLevel.COCOK: [
                "Kita cocok ya?",
                "Ngobrol sama kamu tuh enak.",
                "Rasanya udah kayak kenal lama."
            ],
            ChemistryLevel.SANGAT_COCOK: [
                "Kok bisa ya kita cocok banget?",
                "Seperti ada yang nyambung gitu.",
                "Kamu ngerti aku tanpa aku bicara."
            ],
            ChemistryLevel.SOULMATE: [
                "Aku merasa... kita soulmate.",
                "Belahan jiwa yang selama ini aku cari.",
                "Kayak sudah saling kenal seumur hidup."
            ]
        }
        
        return random.choice(descriptions[level])
    
    def get_vibe(self) -> str:
        """Dapatkan 'vibe' hubungan"""
        vibes = {
            ChemistryLevel.DINGIN: "❄️ Dingin",
            ChemistryLevel.BIASA: "😐 Biasa",
            ChemistryLevel.HANGAT: "🔥 Hangat",
            ChemistryLevel.COCOK: "💕 Cocok",
            ChemistryLevel.SANGAT_COCOK: "💞 Sangat Cocok",
            ChemistryLevel.SOULMATE: "✨ Soulmate"
        }
        return vibes[self.get_level()]
    
    def __repr__(self):
        return f"<Chemistry: {self.get_level().value} ({self.score:.1f})>"


class ChemistrySystem:
    """
    Sistem chemistry yang benar-benar natural
    - Tidak ada rumus pasti
    - Berdasarkan analisis AI
    - Bisa berubah seiring waktu
    - Rahasia (tidak ditampilkan sebagai angka)
    """
    
    def __init__(self, ai_engine=None):
        self.ai_engine = ai_engine
        self.chemistries = {}  # {pdkt_id: ChemistryScore}
        self.attraction_factors = {}  # Faktor-faktor yang mempengaruhi
        
        # Faktor yang mempengaruhi chemistry (tapi tidak mutlak)
        self.factor_weights = {
            'similar_interests': 0.2,      # Kesamaan minat
            'communication_style': 0.25,    # Gaya komunikasi
            'emotional_depth': 0.2,         # Kedalaman emosi
            'physical_attraction': 0.15,    # Ketertarikan fisik
            'timing': 0.1,                   # Waktu yang tepat
            'mystery': 0.1                    # Faktor X (tak terduga)
        }
        
        logger.info("✅ ChemistrySystem initialized (99% realisme)")
    
    # =========================================================================
    # CREATE CHEMISTRY
    # =========================================================================
    
    def create_chemistry(self, pdkt_id: str, initial_score: float = None) -> ChemistryScore:
        """
        Buat chemistry baru untuk PDKT
        
        Args:
            pdkt_id: ID PDKT
            initial_score: Score awal (None = random alami)
        
        Returns:
            ChemistryScore object
        """
        if initial_score is None:
            # Score awal random alami (20-80)
            initial_score = random.randint(20, 80)
        
        chemistry = ChemistryScore(initial_score)
        self.chemistries[pdkt_id] = chemistry
        
        # Catat faktor awal
        self.attraction_factors[pdkt_id] = {
            'first_impression': initial_score,
            'created_at': time.time(),
            'factors': {}
        }
        
        logger.info(f"✨ Chemistry created for {pdkt_id}: {chemistry.get_vibe()}")
        
        return chemistry
    
    # =========================================================================
    # ANALYZE CHEMISTRY (MENGGUNAKAN AI)
    # =========================================================================
    
    async def analyze_interaction(self, pdkt_id: str, user_message: str, 
                                   bot_response: str, context: Dict) -> float:
        """
        Analisis interaksi untuk menentukan perubahan chemistry
        MENGGUNAKAN AI, BUKAN RUMUS
        
        Returns:
            Perubahan score (bisa positif/negatif)
        """
        if pdkt_id not in self.chemistries:
            self.create_chemistry(pdkt_id)
        
        if not self.ai_engine:
            # Fallback sederhana jika AI tidak tersedia
            return self._simple_analysis(user_message, bot_response)
        
        # Prompt untuk AI menganalisis chemistry
        prompt = f"""
        Analisis chemistry antara dua orang ini berdasarkan percakapan mereka.
        
        USER: "{user_message}"
        BOT: "{bot_response}"
        
        Konteks:
        - Level hubungan: {context.get('level', 1)}/12
        - Mood: {context.get('mood', 'netral')}
        - Status: {context.get('relationship_status', 'pdkt')}
        
        Tugas:
        1. Apakah mereka cocok?
        2. Berapa perubahan chemistry? (-10 sampai +10)
        3. Jelaskan alasannya secara natural
        
        Format response:
        CHANGE: [angka -10 sd +10]
        REASON: [penjelasan singkat]
        VIBE: [deskripsi vibe saat ini]
        """
        
        try:
            result = await self.ai_engine._call_deepseek_with_retry(
                messages=[{"role": "user", "content": prompt}],
                max_retries=2
            )
            
            # Parse result
            change = self._parse_change(result)
            reason = self._parse_reason(result)
            vibe = self._parse_vibe(result)
            
            # Update chemistry
            chemistry = self.chemistries[pdkt_id]
            old_score = chemistry.score
            chemistry.score = max(0, min(100, old_score + change))
            chemistry.last_update = time.time()
            
            # Catat history
            chemistry.history.append({
                'timestamp': time.time(),
                'change': change,
                'reason': reason,
                'vibe': vibe,
                'old_score': old_score,
                'new_score': chemistry.score
            })
            
            logger.debug(f"Chemistry changed: {old_score:.1f} → {chemistry.score:.1f} ({change:+.1f}) - {reason}")
            
            return change
            
        except Exception as e:
            logger.error(f"Error analyzing chemistry: {e}")
            return self._simple_analysis(user_message, bot_response)
    
    def _simple_analysis(self, user_message: str, bot_response: str) -> float:
        """Fallback sederhana jika AI tidak tersedia"""
        text = (user_message + " " + bot_response).lower()
        
        positive_words = ['suka', 'cocok', 'enak', 'nyaman', 'senang', 'happy']
        negative_words = ['gak suka', 'gak cocok', 'aneh', 'risih', 'ganjel']
        
        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)
        
        # Random dengan bias
        base = random.uniform(-3, 3)
        return base + (pos_count * 2) - (neg_count * 2)
    
    def _parse_change(self, result: str) -> float:
        """Parse perubahan dari response AI"""
        try:
            for line in result.split('\n'):
                if 'CHANGE:' in line:
                    change_str = line.replace('CHANGE:', '').strip()
                    # Ambil angka
                    import re
                    numbers = re.findall(r'-?\d+\.?\d*', change_str)
                    if numbers:
                        return float(numbers[0])
        except:
            pass
        return random.uniform(-2, 2)  # Default random kecil
    
    def _parse_reason(self, result: str) -> str:
        """Parse alasan dari response AI"""
        for line in result.split('\n'):
            if 'REASON:' in line:
                return line.replace('REASON:', '').strip()
        return "Ada sesuatu dalam percakapan ini..."
    
    def _parse_vibe(self, result: str) -> str:
        """Parse vibe dari response AI"""
        for line in result.split('\n'):
            if 'VIBE:' in line:
                return line.replace('VIBE:', '').strip()
        return chemistry.get_description() if 'chemistry' in locals() else "Biasa aja"
    
    # =========================================================================
    # GET CHEMISTRY INFO
    # =========================================================================
    
    def get_chemistry(self, pdkt_id: str) -> Optional[ChemistryScore]:
        """Dapatkan chemistry untuk PDKT"""
        return self.chemistries.get(pdkt_id)
    
    def get_vibe(self, pdkt_id: str) -> str:
        """Dapatkan vibe hubungan"""
        chemistry = self.get_chemistry(pdkt_id)
        if chemistry:
            return chemistry.get_vibe()
        return "Belum ada chemistry"
    
    def get_description(self, pdkt_id: str) -> str:
        """Dapatkan deskripsi natural"""
        chemistry = self.get_chemistry(pdkt_id)
        if chemistry:
            return chemistry.get_description()
        return "Masih mencari chemistry..."
    
    def get_chemistry_summary(self, pdkt_id: str) -> Dict:
        """Dapatkan summary chemistry (untuk internal)"""
        chemistry = self.get_chemistry(pdkt_id)
        if not chemistry:
            return {}
        
        return {
            'vibe': chemistry.get_vibe(),
            'description': chemistry.get_description(),
            'level': chemistry.get_level().value,
            'history_count': len(chemistry.history),
            'last_interaction': chemistry.last_update,
            'trend': self._get_trend(chemistry)
        }
    
    def _get_trend(self, chemistry: ChemistryScore) -> str:
        """Analisis trend chemistry"""
        if len(chemistry.history) < 3:
            return "masih baru"
        
        recent = chemistry.history[-3:]
        changes = [h['change'] for h in recent]
        avg_change = sum(changes) / len(changes)
        
        if avg_change > 1:
            return "memanas 🔥"
        elif avg_change > 0.3:
            return "menghangat 🌡️"
        elif avg_change > -0.3:
            return "stabil ⚖️"
        elif avg_change > -1:
            return "mendingin ❄️"
        else:
            return "membeku 🧊"
    
    # =========================================================================
    # RANDOM CHEMISTRY EVENT
    # =========================================================================
    
    async def random_chemistry_event(self, pdkt_id: str) -> Optional[Dict]:
        """
        Event chemistry random yang bisa terjadi
        - Tiba-tiba cocok
        - Tiba-tiba tidak cocok
        - Ada faktor X
        """
        if pdkt_id not in self.chemistries:
            return None
        
        chemistry = self.chemistries[pdkt_id]
        
        # 5% chance setiap interaksi
        if random.random() > 0.05:
            return None
        
        events = [
            {
                'type': 'spark',
                'message': 'Tiba-tiba ada getaran aneh...',
                'change': +5,
                'description': 'Chemistry meningkat drastis!'
            },
            {
                'type': 'cold',
                'message': 'Kayaknya ada yang aneh...',
                'change': -5,
                'description': 'Chemistry menurun drastis'
            },
            {
                'type': 'realization',
                'message': 'Aku sadar sesuatu...',
                'change': +3,
                'description': 'Kamu berbeda dari yang lain'
            },
            {
                'type': 'doubt',
                'message': 'Aku ragu...',
                'change': -3,
                'description': 'Ada keraguan dalam hati'
            },
            {
                'type': 'butterfly',
                'message': 'Jantungku berdebar...',
                'change': +2,
                'description': 'Ada kupu-kupu di perut'
            }
        ]
        
        event = random.choice(events)
        
        # Apply change
        old_score = chemistry.score
        chemistry.score = max(0, min(100, old_score + event['change']))
        chemistry.history.append({
            'timestamp': time.time(),
            'event': event['type'],
            'change': event['change'],
            'message': event['message'],
            'old_score': old_score,
            'new_score': chemistry.score
        })
        
        logger.info(f"🎲 Random chemistry event: {event['type']} ({event['change']:+.1f})")
        
        return {
            'event': event['type'],
            'message': event['message'],
            'description': event['description'],
            'new_vibe': chemistry.get_vibe()
        }


__all__ = ['ChemistrySystem', 'ChemistryScore', 'ChemistryLevel']
