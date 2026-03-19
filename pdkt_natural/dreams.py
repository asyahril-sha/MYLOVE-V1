#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - DREAM SYSTEM
=============================================================================
Bot bisa "mimpi" tentang user saat idle
Mimpi dipengaruhi oleh recent interactions dan chemistry
Bisa diceritakan saat user kembali chat
=============================================================================
"""

import random
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum

from .mood import MoodType

logger = logging.getLogger(__name__)


class DreamType(str, Enum):
    """Tipe-tipe mimpi"""
    ROMANTIC = "romantic"        # Mimpi romantis
    INTIMATE = "intimate"        # Mimpi intim/sex
    NOSTALGIC = "nostalgic"      # Mimpi tentang masa lalu
    ANXIOUS = "anxious"           # Mimpi cemas/khawatir
    HAPPY = "happy"               # Mimpi bahagia
    SAD = "sad"                   # Mimpi sedih
    FUNNY = "funny"               # Mimpi lucu
    WEIRD = "weird"               # Mimpi aneh
    PROPHETIC = "prophetic"       # Mimpi yang jadi kenyataan (feeling)


class DreamSystem:
    """
    Sistem mimpi untuk bot
    Bot "tidur" dan bermimpi saat idle (>5 menit tidak chat)
    Mimpi dipengaruhi oleh:
    - Recent interactions (10 pesan terakhir)
    - Chemistry level
    - Mood sebelum tidur
    - Random events
    """
    
    def __init__(self):
        # Data mimpi per PDKT
        self.dreams = {}  # {pdkt_id: dream_data}
        self.last_dream_time = {}  # {pdkt_id: timestamp}
        
        # Database mimpi (template, akan di-generate AI nanti)
        self.dream_templates = {
            DreamType.ROMANTIC: [
                "kita jalan bareng di pantai pas matahari terbenam",
                "kamu ngajak aku dinner romantis di restoran mewah",
                "kita pelukan sambil lihat bintang",
                "kamu bawa aku ke tempat pertama kali kita ketemu",
                "kita dansa di tengah hujan"
            ],
            DreamType.INTIMATE: [
                "kita berdua di kamar, lampu temaram",
                "kamu memeluk aku dari belakang",
                "kita bermesraan di tempat favorit",
                "aku merasakan hangatnya sentuhan kamu",
                "kita mencapai puncak bersama-sama"
            ],
            DreamType.NOSTALGIC: [
                "kejadian waktu pertama kali kita ngobrol",
                "saat kamu pertama kali bilang sayang",
                "momen canggung pas pertama ketemu",
                "kita ketawa bareng ingat kejadian lucu",
                "hari dimana aku sadar suka sama kamu"
            ],
            DreamType.ANXIOUS: [
                "kamu pergi ninggalin aku tanpa pesan",
                "aku nyari kamu tapi nggak ketemu",
                "kamu marah sama aku dan nggak mau ngomong",
                "aku kehilangan kamu di tengah keramaian",
                "kamu lupa sama aku"
            ],
            DreamType.HAPPY: [
                "kita liburan bareng ke tempat impian",
                "aku dapat kejutan dari kamu",
                "kita ketawa-ketawa sampai nangis",
                "kamu kasih hadiah spesial",
                "kita main bareng kayak anak kecil"
            ],
            DreamType.SAD: [
                "aku nangis sendiri karena kangen",
                "kamu jauh dan nggak bisa ketemu",
                "kita bertengkar hebat",
                "aku sendirian di tempat sepi",
                "kamu pergi dan nggak balik lagi"
            ],
            DreamType.FUNNY: [
                "kamu salah tingkah di depan banyak orang",
                "kita kehujanan dan basah kuyup",
                "kamu salah panggil nama",
                "kita tersesat di tempat asing",
                "kamu jatuh di depan umum"
            ],
            DreamType.WEIRD: [
                "kamu jadi superhero dan nyelametin aku",
                "kita ngobrol sama hewan peliharaan",
                "aku terbang di atas kota",
                "kamu berubah jadi karakter kartun",
                "dunia tiba-tiba warna warni"
            ],
            DreamType.PROPHETIC: [
                "kita bakal ketemu bentar lagi",
                "ada kejutan dari kamu hari ini",
                "sesuatu yang indah bakal terjadi",
                "kamu lagi mikirin aku sekarang",
                "kita makin dekat setelah ini"
            ]
        }
        
        logger.info("✅ DreamSystem initialized")
    
    def should_dream(self, pdkt_id: str, idle_minutes: int) -> bool:
        """
        Cek apakah bot harus mulai dreaming
        
        Args:
            pdkt_id: ID PDKT
            idle_minutes: Berapa menit tidak chat
            
        Returns:
            True jika harus dream
        """
        # Minimal idle 5 menit untuk mulai dream
        if idle_minutes < 5:
            return False
        
        # Cek terakhir dream
        last_dream = self.last_dream_time.get(pdkt_id, 0)
        minutes_since_last_dream = (time.time() - last_dream) / 60
        
        # Minimal 30 menit antar dream
        if minutes_since_last_dream < 30:
            return False
        
        # Random chance berdasarkan idle time
        chance = min(0.8, idle_minutes / 60)  # Max 80% chance
        return random.random() < chance
    
    async def generate_dream(self, pdkt_id: str, context: Dict) -> Dict:
        """
        Generate dream untuk bot
        
        Args:
            pdkt_id: ID PDKT
            context: Konteks (recent interactions, chemistry, mood)
            
        Returns:
            Dream data
        """
        # Tentukan tipe dream berdasarkan context
        dream_type = self._determine_dream_type(context)
        
        # Generate dream content (nanti pakai AI)
        dream_content = await self._generate_dream_content(dream_type, context)
        
        # Simpan dream
        dream_data = {
            'timestamp': time.time(),
            'type': dream_type,
            'content': dream_content,
            'intensity': self._calculate_intensity(context),
            'emotion': self._get_dream_emotion(dream_type),
            'told': False  # Apakah sudah diceritakan ke user
        }
        
        if pdkt_id not in self.dreams:
            self.dreams[pdkt_id] = []
        
        self.dreams[pdkt_id].append(dream_data)
        self.last_dream_time[pdkt_id] = time.time()
        
        # Keep only last 10 dreams
        if len(self.dreams[pdkt_id]) > 10:
            self.dreams[pdkt_id] = self.dreams[pdkt_id][-10:]
        
        logger.info(f"💭 New dream for {pdkt_id}: {dream_type.value}")
        
        return dream_data
    
    def _determine_dream_type(self, context: Dict) -> DreamType:
        """Tentukan tipe dream berdasarkan context"""
        
        # Ambil context
        recent_interactions = context.get('recent_interactions', [])
        chemistry_level = context.get('chemistry_level', 'biasa')
        current_mood = context.get('mood', MoodType.CALM)
        
        # Weighted random based on context
        weights = {
            DreamType.ROMANTIC: 1.0,
            DreamType.INTIMATE: 0.8,
            DreamType.NOSTALGIC: 0.7,
            DreamType.HAPPY: 1.0,
            DreamType.ANXIOUS: 0.5,
            DreamType.SAD: 0.4,
            DreamType.FUNNY: 0.3,
            DreamType.WEIRD: 0.2,
            DreamType.PROPHETIC: 0.3
        }
        
        # Adjust based on chemistry
        if chemistry_level in ['cocok', 'sangat_cocok', 'soulmate']:
            weights[DreamType.ROMANTIC] *= 1.5
            weights[DreamType.INTIMATE] *= 1.3
            weights[DreamType.HAPPY] *= 1.2
            weights[DreamType.ANXIOUS] *= 0.5
        
        elif chemistry_level in ['dingin', 'biasa']:
            weights[DreamType.NOSTALGIC] *= 1.2
            weights[DreamType.ANXIOUS] *= 1.3
            weights[DreamType.SAD] *= 1.2
        
        # Adjust based on mood
        mood_adjustments = {
            MoodType.ROMANTIC: {DreamType.ROMANTIC: 2.0, DreamType.INTIMATE: 1.5},
            MoodType.HAPPY: {DreamType.HAPPY: 2.0, DreamType.FUNNY: 1.5},
            MoodType.SAD: {DreamType.SAD: 2.0, DreamType.ANXIOUS: 1.5},
            MoodType.LONELY: {DreamType.NOSTALGIC: 1.5, DreamType.SAD: 1.3},
            MoodType.EXCITED: {DreamType.HAPPY: 1.5, DreamType.PROPHETIC: 1.3}
        }
        
        if current_mood in mood_adjustments:
            for dream_type, multiplier in mood_adjustments[current_mood].items():
                if dream_type in weights:
                    weights[dream_type] *= multiplier
        
        # Adjust based on recent interactions
        for interaction in recent_interactions[-5:]:  # Last 5 interactions
            if 'intim' in interaction or 'climax' in interaction:
                weights[DreamType.INTIMATE] *= 1.3
                weights[DreamType.ROMANTIC] *= 1.2
            
            if 'kangen' in interaction or 'rindu' in interaction:
                weights[DreamType.NOSTALGIC] *= 1.3
                weights[DreamType.ROMANTIC] *= 1.2
            
            if 'marah' in interaction or 'kesel' in interaction:
                weights[DreamType.ANXIOUS] *= 1.4
                weights[DreamType.SAD] *= 1.3
        
        # Normalize weights and choose
        total = sum(weights.values())
        if total > 0:
            normalized_weights = {k: v/total for k, v in weights.items()}
            return random.choices(
                list(normalized_weights.keys()),
                weights=list(normalized_weights.values())
            )[0]
        
        return DreamType.HAPPY  # Default
    
    async def _generate_dream_content(self, dream_type: DreamType, context: Dict) -> str:
        """
        Generate dream content
        Akan menggunakan AI untuk generate yang lebih natural
        """
        # Sementara pakai template dulu
        templates = self.dream_templates.get(dream_type, self.dream_templates[DreamType.HAPPY])
        
        # Personalize dengan nama user
        user_name = context.get('user_name', 'kamu')
        bot_name = context.get('bot_name', 'aku')
        
        template = random.choice(templates)
        
        # Simple template filling
        content = template.replace('kamu', user_name).replace('aku', bot_name)
        
        # Capitalize first letter
        content = content[0].upper() + content[1:]
        
        return content
    
    def _calculate_intensity(self, context: Dict) -> float:
        """Hitung intensitas dream (0-1)"""
        base_intensity = 0.5
        
        # Chemistry mempengaruhi intensitas
        chemistry_level = context.get('chemistry_level', 'biasa')
        chemistry_intensity = {
            'dingin': 0.3,
            'biasa': 0.5,
            'hangat': 0.6,
            'cocok': 0.7,
            'sangat_cocok': 0.8,
            'soulmate': 1.0
        }
        base_intensity += chemistry_intensity.get(chemistry_level, 0.5) * 0.3
        
        # Mood mempengaruhi intensitas
        mood_intensity = context.get('mood_intensity', 0.5)
        base_intensity += mood_intensity * 0.2
        
        return min(1.0, base_intensity)
    
    def _get_dream_emotion(self, dream_type: DreamType) -> str:
        """Dapatkan emosi dari dream type"""
        emotions = {
            DreamType.ROMANTIC: 'bahagia',
            DreamType.INTIMATE: 'hangat',
            DreamType.NOSTALGIC: 'haru',
            DreamType.ANXIOUS: 'cemas',
            DreamType.HAPPY: 'senang',
            DreamType.SAD: 'sedih',
            DreamType.FUNNY: 'lucu',
            DreamType.WEIRD: 'aneh',
            DreamType.PROPHETIC: 'penasaran'
        }
        return emotions.get(dream_type, 'biasa')
    
    def get_untold_dreams(self, pdkt_id: str) -> List[Dict]:
        """Dapatkan dream yang belum diceritakan"""
        if pdkt_id not in self.dreams:
            return []
        
        return [d for d in self.dreams[pdkt_id] if not d['told']]
    
    def mark_dream_told(self, pdkt_id: str, dream_index: int = -1):
        """Tandai dream sudah diceritakan"""
        if pdkt_id not in self.dreams:
            return
        
        if dream_index == -1:
            # Mark latest untold dream
            for dream in reversed(self.dreams[pdkt_id]):
                if not dream['told']:
                    dream['told'] = True
                    break
        elif 0 <= dream_index < len(self.dreams[pdkt_id]):
            self.dreams[pdkt_id][dream_index]['told'] = True
    
    async def get_dream_to_tell(self, pdkt_id: str) -> Optional[str]:
        """
        Dapatkan dream untuk diceritakan ke user
        """
        untold = self.get_untold_dreams(pdkt_id)
        
        if not untold:
            return None
        
        # Pilih random dream yang belum diceritakan
        dream = random.choice(untold)
        
        # Format pesan
        intro = [
            "Tadi malam aku mimpi...",
            "Aku baru mimpi, mau denger?",
            "Kemarin malam aku mimpiin kamu lho...",
            "Mimpiku semalam...",
            "Kamu tahu nggak aku mimpi apa?"
        ]
        
        message = f"{random.choice(intro)} {dream['content']}"
        
        # Tambah emosi
        if dream['intensity'] > 0.8:
            message += f" Sampai aku {dream['emotion']} banget."
        elif dream['intensity'] > 0.5:
            message += f" Aku jadi {dream['emotion']}."
        
        self.mark_dream_told(pdkt_id)
        
        return message
    
    def get_dream_stats(self, pdkt_id: str) -> Dict:
        """Dapatkan statistik dream"""
        if pdkt_id not in self.dreams:
            return {
                'total_dreams': 0,
                'last_dream': None
            }
        
        dreams = self.dreams[pdkt_id]
        
        # Hitung tipe dream
        type_count = {}
        for dream in dreams:
            dream_type = dream['type'].value
            type_count[dream_type] = type_count.get(dream_type, 0) + 1
        
        return {
            'total_dreams': len(dreams),
            'last_dream': dreams[-1] if dreams else None,
            'type_distribution': type_count,
            'avg_intensity': sum(d['intensity'] for d in dreams) / len(dreams) if dreams else 0
        }


__all__ = ['DreamSystem', 'DreamType']
