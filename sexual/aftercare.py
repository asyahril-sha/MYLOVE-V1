#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - AFTERCARE SYSTEM
=============================================================================
- Aftercare setelah climax di level 12
- Reset ke level 7 setelah aftercare
- Berbagai tipe aftercare (cuddle, talk, rest, dll)
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any
from enum import Enum

from config import settings

logger = logging.getLogger(__name__)


class AftercareType(str, Enum):
    """Tipe-tipe aftercare"""
    CUDDLE = "cuddle"
    SOFT_TALK = "soft_talk"
    REST = "rest"
    MASSAGE = "massage"
    FOOD = "food"
    MOVIE = "movie"
    MUSIC = "music"
    WALK = "walk"
    COFFEE = "coffee"
    HUG = "hug"
    PAMPER = "pamper"
    SHOWER = "shower"


class AftercareSystem:
    """
    Sistem aftercare setelah mencapai level 12
    - Trigger aftercare setelah climax
    - Reset ke level 7 setelah aftercare selesai
    - Berbagai tipe aftercare dengan respons berbeda
    """
    
    def __init__(self):
        # =========================================================================
        # AFTERCARE DATABASE
        # =========================================================================
        self.aftercare_types = {
            AftercareType.CUDDLE: {
                "name": "Cuddle",
                "emoji": "🤗",
                "description": "Berpelukan erat, merasakan kehangatan",
                "duration": "15-30 menit",
                "messages": [
                    "*memeluk erat* Jangan pergi dulu...",
                    "Rasain deh hangatnya pelukan aku...",
                    "Gamau lepas, mau terus kayak gini.",
                    "Enak banget dipeluk kamu...",
                    "*menggeliat nyaman di pelukan*"
                ],
                "effects": ["meningkatkan bonding", "menurunkan stress", "rasa aman"]
            },
            AftercareType.SOFT_TALK: {
                "name": "Soft Talk",
                "emoji": "🗣️",
                "description": "Ngobrol manis, bisik-bisik",
                "duration": "10-20 menit",
                "messages": [
                    "Kamu tahu gak, aku sayang banget sama kamu...",
                    "Cerita dong, lagi mikirin apa?",
                    "Bisikin sesuatu yang manis dong...",
                    "Kita ngobrol bentar yuk sambil istirahat.",
                    "Aku suka banget ngobrol sama kamu."
                ],
                "effects": ["komunikasi lebih dalam", "emotional connection", "trust"]
            },
            AftercareType.REST: {
                "name": "Rest",
                "emoji": "😴",
                "description": "Istirahat bareng, rebahan",
                "duration": "20-40 menit",
                "messages": [
                    "Capek? Istirahat dulu yuk...",
                    "*rebahan di dada kamu* Enak banget...",
                    "Tidur bentar, tapi jangan lepas ya.",
                    "Mata udah berat, tapi gamau tidur.",
                    "Istirahat dulu, nanti lanjut lagi..."
                ],
                "effects": ["recharge energy", "relaxation", "quality time"]
            },
            AftercareType.MASSAGE: {
                "name": "Massage",
                "emoji": "💆‍♀️",
                "description": "Pijatan lembut",
                "duration": "15-25 menit",
                "messages": [
                    "Kamu pasti capek, aku pijitin ya...",
                    "Enak gak dipijit gini?",
                    "Badan kamu tegang, sini aku lembutin...",
                    "Pijat-pijat dikit biar rileks.",
                    "Bahunya kok tegang? Santai sayang..."
                ],
                "effects": ["melemaskan otot", "relaxation", "care"]
            },
            AftercareType.FOOD: {
                "name": "Food",
                "emoji": "🍳",
                "description": "Masak atau nyemil bareng",
                "duration": "20-30 menit",
                "messages": [
                    "Kamu laper? Aku bikinin makanan ya...",
                    "Mau dibuatin kopi atau susu?",
                    "Kita ngemil dulu yuk, abis ini lanjut lagi.",
                    "Aku masakin something spesial buat kamu.",
                    "Enak? Seneng liat kamu makan."
                ],
                "effects": ["recharge energy", "nurturing", "quality time"]
            },
            AftercareType.MOVIE: {
                "name": "Movie",
                "emoji": "🎬",
                "description": "Nonton film bareng",
                "duration": "60-120 menit",
                "messages": [
                    "Nonton film yuk sambil pelukan...",
                    "Mau nonton apa? Yang romantis aja.",
                    "Sambil nontul sambil cuddle, enak...",
                    "Film apapun jadi seru bareng kamu.",
                    "Abis nonton, lanjut lagi ya?"
                ],
                "effects": ["quality time", "relaxation", "shared experience"]
            },
            AftercareType.MUSIC: {
                "name": "Music",
                "emoji": "🎵",
                "description": "Dengerin musik bareng",
                "duration": "20-40 menit",
                "messages": [
                    "Dengerin lagu kesukaan kamu yuk...",
                    "Lagu ini selalu ingetin aku sama kamu.",
                    "Sambil dengerin musik sambil pelukan...",
                    "Nyanyi dikit dong buat aku.",
                    "Irama lagu kayak detak jantung kita."
                ],
                "effects": ["mood booster", "emotional connection", "romance"]
            },
            AftercareType.WALK: {
                "name": "Walk",
                "emoji": "🚶",
                "description": "Jalan-jalan santai cari angin",
                "duration": "20-30 menit",
                "messages": [
                    "Jalan-jalan bentar yuk, cari angin...",
                    "Gandeng tangan, jalan santai.",
                    "Abis panas, enaknya jalan malem.",
                    "Lihat bintang sambil jalan...",
                    "Muter dulu, nanti balik lagi."
                ],
                "effects": ["fresh air", "quality time", "romance"]
            },
            AftercareType.COFFEE: {
                "name": "Coffee",
                "emoji": "☕",
                "description": "Ngopi atau ngeteh bareng",
                "duration": "15-25 menit",
                "messages": [
                    "Aku buatin kopi dulu ya...",
                    "Kamu lebih manis dari kopi ini.",
                    "Sambil ngopi sambil ngobrol...",
                    "Panas? Sembur dulu biar adem.",
                    "Kita kayak iklan kopi romantis."
                ],
                "effects": ["warmth", "conversation", "intimate moments"]
            },
            AftercareType.HUG: {
                "name": "Hug",
                "emoji": "🫂",
                "description": "Pelukan panjang",
                "duration": "10-20 menit",
                "messages": [
                    "*hug* jangan pergi dulu...",
                    "Satu pelukan lagi sebelum tidur.",
                    "Kuatnya pelukan kamu...",
                    "Rasanya aman banget di sini.",
                    "Bisa gak kita pelukan terus?"
                ],
                "effects": ["comfort", "safety", "love"]
            },
            AftercareType.PAMPER: {
                "name": "Pamper",
                "emoji": "👑",
                "description": "Dimanja-manja",
                "duration": "20-30 menit",
                "messages": [
                    "Mau apa? Aku turuti semua...",
                    "Kamu mau dieman-eman?",
                    "Sekarang giliran kamu yang dimanja.",
                    "Rambut kamu wangi banget...",
                    "Rileks aja, biar aku yang urus."
                ],
                "effects": ["feeling special", "being cared for", "luxury"]
            },
            AftercareType.SHOWER: {
                "name": "Shower",
                "emoji": "🚿",
                "description": "Mandi bareng",
                "duration": "15-25 menit",
                "messages": [
                    "Mandi yuk, sekalian anget-anget...",
                    "Aku sabunin punggung kamu ya...",
                    "Air hangatnya bikin rileks.",
                    "Kita kayak di iklan sabun...",
                    "Bersihin badan, nanti kotor lagi."
                ],
                "effects": ["clean", "intimate", "playful"]
            }
        }
        
        # Reset level target
        self.reset_level = settings.intimacy.reset_level  # Default 7
        
        # Aftercare duration (minutes)
        self.min_duration = 10
        self.max_duration = 120
        
        logger.info(f"✅ AftercareSystem initialized with {len(self.aftercare_types)} types")
        
    # =========================================================================
    # AFTERCARE TRIGGER
    # =========================================================================
    
    async def trigger_aftercare(self, user_id: int, role: str, 
                                  aftercare_type: Optional[AftercareType] = None) -> Dict:
        """
        Trigger aftercare session
        
        Args:
            user_id: ID user
            role: Role name
            aftercare_type: Specific aftercare type (random if None)
            
        Returns:
            Dict dengan detail aftercare
        """
        # Pilih tipe aftercare
        if aftercare_type and aftercare_type in self.aftercare_types:
            selected_type = aftercare_type
        else:
            selected_type = random.choice(list(self.aftercare_types.keys()))
            
        aftercare = self.aftercare_types[selected_type]
        
        # Generate duration
        duration = random.randint(self.min_duration, self.max_duration)
        
        # Pilih random message
        message = random.choice(aftercare['messages'])
        
        # Tambah emoji
        full_message = f"{aftercare['emoji']} {message}"
        
        # Efek aftercare
        effects = aftercare['effects']
        
        logger.info(f"💕 Aftercare triggered for user {user_id} role {role}: {selected_type.value}")
        
        return {
            "type": selected_type,
            "type_name": aftercare['name'],
            "emoji": aftercare['emoji'],
            "description": aftercare['description'],
            "message": full_message,
            "duration_minutes": duration,
            "effects": effects,
            "will_reset": True,
            "reset_to_level": self.reset_level
        }
        
    # =========================================================================
    # AFTERCARE COMPLETION
    # =========================================================================
    
    async def complete_aftercare(self, user_id: int, role: str, 
                                   aftercare_type: AftercareType,
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
        # Get aftercare info
        aftercare = self.aftercare_types.get(aftercare_type, self.aftercare_types[AftercareType.CUDDLE])
        
        # Calculate satisfaction effects
        if satisfaction >= 8:
            satisfaction_msg = "Kamu puas banget, hubungan makin erat!"
            bonus = 0.2
        elif satisfaction >= 5:
            satisfaction_msg = "Cukup puas, hubungan baik-baik aja."
            bonus = 0
        else:
            satisfaction_msg = "Kurang puas, butuh aftercare lain next time."
            bonus = -0.1
            
        logger.info(f"✅ Aftercare completed for user {user_id} role {role}: satisfaction {satisfaction}/10")
        
        return {
            "success": True,
            "type": aftercare_type,
            "type_name": aftercare['name'],
            "satisfaction": satisfaction,
            "satisfaction_message": satisfaction_msg,
            "reset_to_level": self.reset_level,
            "message": f"Aftercare selesai. Sekarang intimacy level reset ke {self.reset_level}.",
            "bonus": bonus
        }
        
    # =========================================================================
    # GET AFTERCARE OPTIONS
    # =========================================================================
    
    def get_aftercare_options(self) -> List[Dict]:
        """Get list of available aftercare types"""
        options = []
        
        for atype, data in self.aftercare_types.items():
            options.append({
                "id": atype.value,
                "name": data['name'],
                "emoji": data['emoji'],
                "description": data['description'],
                "duration": data['duration']
            })
            
        return options
        
    def get_aftercare_by_id(self, aftercare_id: str) -> Optional[Dict]:
        """Get aftercare by ID"""
        for atype, data in self.aftercare_types.items():
            if atype.value == aftercare_id or atype.name.lower() == aftercare_id.lower():
                return {
                    "type": atype,
                    **data
                }
        return None
        
    def get_random_aftercare(self) -> Dict:
        """Get random aftercare type"""
        atype = random.choice(list(self.aftercare_types.keys()))
        return {
            "type": atype,
            **self.aftercare_types[atype]
        }
        
    # =========================================================================
    # AFTERCARE EFFECTS
    # =========================================================================
    
    async def get_aftercare_effects(self, aftercare_type: AftercareType) -> List[str]:
        """Get effects of specific aftercare"""
        aftercare = self.aftercare_types.get(aftercare_type)
        return aftercare['effects'] if aftercare else []
        
    async def combine_aftercare(self, types: List[AftercareType]) -> Dict:
        """
        Combine multiple aftercare types
        
        Args:
            types: List of aftercare types
            
        Returns:
            Combined aftercare session
        """
        if not types:
            return await self.trigger_aftercare(0, "none")
            
        # Pilih primary type
        primary = types[0]
        primary_data = self.aftercare_types.get(primary, self.aftercare_types[AftercareType.CUDDLE])
        
        # Combine messages
        messages = []
        for atype in types[:3]:  # Max 3 types
            if atype in self.aftercare_types:
                messages.append(random.choice(self.aftercare_types[atype]['messages']))
                
        # Combine effects
        all_effects = []
        for atype in types:
            if atype in self.aftercare_types:
                all_effects.extend(self.aftercare_types[atype]['effects'])
                
        # Remove duplicates
        unique_effects = list(dict.fromkeys(all_effects))
        
        # Calculate total duration
        total_duration = len(types) * 20  # 20 menit per type
        
        return {
            "type": "combined",
            "primary_type": primary_data['name'],
            "types": [self.aftercare_types[t]['name'] for t in types if t in self.aftercare_types],
            "messages": messages,
            "combined_message": " ".join(messages[:2]),  # Gabung 2 pesan
            "effects": unique_effects,
            "duration_minutes": min(120, total_duration),
            "will_reset": True,
            "reset_to_level": self.reset_level
        }
        
    # =========================================================================
    # AFTERCARE REMINDER
    # =========================================================================
    
    def get_aftercare_reminder(self, intimacy_level: int) -> Optional[str]:
        """Get aftercare reminder jika level 12"""
        if intimacy_level >= 12:
            reminders = [
                "Kita udah level max! Butuh aftercare nih...",
                "Abis ini, jangan lupa aftercare ya.",
                "Mau aftercare apa? Cuddle? Ngobrol?",
                "Level 12! Saatnya quality time setelah ini.",
                "Jangan buru-buru, kita butuh aftercare."
            ]
            return random.choice(reminders)
        return None
        
    # =========================================================================
    # FORMATTING
    # =========================================================================
    
    def format_aftercare_options(self) -> str:
        """Format aftercare options for display"""
        options = self.get_aftercare_options()
        
        lines = ["💕 **AFTERCARE OPTIONS**"]
        lines.append("_(Pilih salah satu setelah climax di level 12)_")
        lines.append("")
        
        for opt in options:
            lines.append(
                f"{opt['emoji']} **{opt['name']}**\n"
                f"   {opt['description']} ({opt['duration']})"
            )
            
        lines.append("")
        lines.append("💡 Ketik /aftercare [nama] untuk memilih")
        lines.append("Contoh: /aftercare cuddle")
        
        return "\n".join(lines)
        
    def format_aftercare_result(self, result: Dict) -> str:
        """Format aftercare result for display"""
        lines = [
            f"{result.get('emoji', '💕')} **Aftercare: {result.get('type_name', 'Unknown')}**",
            f"{result.get('message', '')}",
            f"\nDurasi: {result.get('duration_minutes', 0)} menit",
            f"Efek: {', '.join(result.get('effects', []))}"
        ]
        
        if result.get('will_reset'):
            lines.append(f"\n🔄 Setelah aftercare, intimacy reset ke level {result.get('reset_to_level', 7)}")
            
        return "\n".join(lines)
        
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    def get_stats(self) -> Dict:
        """Get aftercare statistics"""
        return {
            "total_types": len(self.aftercare_types),
            "types": list(self.aftercare_types.keys()),
            "reset_level": self.reset_level,
            "duration_range": f"{self.min_duration}-{self.max_duration} menit"
        }


__all__ = ['AftercareSystem', 'AftercareType']
