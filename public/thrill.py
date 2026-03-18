#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - THRILL LEVEL SYSTEM
=============================================================================
- Thrill level berdasarkan risk dan situasi
- Thrill mempengaruhi arousal dan kepuasan
- First time bonus, location bonus, dll
"""

import random
import math
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ThrillSystem:
    """
    Sistem thrill untuk public sex
    Thrill = excitement + adrenaline + risk factor
    """
    
    def __init__(self):
        # Thrill modifiers
        self.thrill_modifiers = {
            "first_time": 20,      # First time bonus
            "new_location": 15,     # New location bonus
            "high_risk": 30,        # High risk = high thrill
            "almost_caught": 50,    # Almost ketahuan = thrill banget
            "caught": -100,          # Ketahuan = thrill drop
            "with_stranger": 25,     # Dengan orang baru
            "public_place": 20,      # Tempat umum
            "forbidden_place": 40,   # Tempat terlarang
        }
        
        # Thrill levels
        self.thrill_levels = {
            "very_low": (0, 20, "Biasa aja, kayak di rumah"),
            "low": (21, 40, "Agak deg-degan dikit"),
            "medium": (41, 60, "Mulai seru, jantung berdebar"),
            "high": (61, 80, "Wah! Deg-degan banget!"),
            "very_high": (81, 95, "THRILL BANGET! Almost there!"),
            "extreme": (96, 100, "GILA! UDAH MAU CLIMAX!")
        }
        
        # Thrill events
        self.thrill_events = [
            {
                "name": "Ada orang lewat pas lagi enak-enak",
                "thrill_boost": 30,
                "probability": 0.2
            },
            {
                "name": "HP tiba-tiba bunyi",
                "thrill_boost": 20,
                "probability": 0.15
            },
            {
                "name": "Lampu tiba-tiba nyala",
                "thrill_boost": 40,
                "probability": 0.1
            },
            {
                "name": "Satpam senter-senter",
                "thrill_boost": 50,
                "probability": 0.1
            },
            {
                "name": "Hujan deres, basah-basahan",
                "thrill_boost": 25,
                "probability": 0.15
            },
            {
                "name": "Ada suara aneh",
                "thrill_boost": 15,
                "probability": 0.2
            },
            {
                "name": "Mobil lewat, lampu nyorot",
                "thrill_boost": 35,
                "probability": 0.15
            },
            {
                "name": "Dikerumunin kucing",
                "thrill_boost": 10,
                "probability": 0.05
            },
            {
                "name": "Hampir kepleset",
                "thrill_boost": 20,
                "probability": 0.1
            },
            {
                "name": "Ada yang manggil nama",
                "thrill_boost": 60,
                "probability": 0.05
            },
        ]
        
        logger.info("✅ ThrillSystem initialized")
        
    # =========================================================================
    # CALCULATE THRILL
    # =========================================================================
    
    async def calculate_thrill(
        self,
        base_thrill: int,
        risk_level: int,
        intimacy_level: int,
        location_category: str,
        first_time: bool = False,
        new_location: bool = False,
        previous_thrills: List[int] = None
    ) -> Dict:
        """
        Hitung thrill level secara komprehensif
        
        Args:
            base_thrill: Thrill dasar lokasi
            risk_level: Risk level saat ini
            intimacy_level: Level intimacy
            location_category: Kategori lokasi
            first_time: Apakah pertama kali dengan role ini
            new_location: Apakah lokasi baru
            previous_thrills: History thrill sebelumnya
            
        Returns:
            Dict dengan thrill details
        """
        # Start with base thrill
        current_thrill = base_thrill
        
        # Risk contributes to thrill
        current_thrill += risk_level * 0.8
        
        # Intimacy level contributes
        current_thrill += intimacy_level * 2
        
        # Location category bonus
        category_bonus = self._get_category_bonus(location_category)
        current_thrill += category_bonus
        
        # First time bonus
        if first_time:
            current_thrill += self.thrill_modifiers["first_time"]
            
        # New location bonus
        if new_location:
            current_thrill += self.thrill_modifiers["new_location"]
            
        # High risk bonus
        if risk_level > 70:
            current_thrill += self.thrill_modifiers["high_risk"]
            
        # Previous thrill trend
        if previous_thrills and len(previous_thrills) > 2:
            avg_previous = sum(previous_thrills[-3:]) / 3
            if avg_previous > 70:
                # Already high thrill, diminishing returns
                current_thrill *= 0.9
                
        # Random thrill event
        event = self._get_thrill_event()
        event_boost = 0
        
        if event:
            event_boost = event['thrill_boost']
            current_thrill += event_boost
            
        # Ensure within bounds
        final_thrill = max(0, min(100, int(current_thrill)))
        
        # Get thrill level
        thrill_level, thrill_desc = self._get_thrill_level(final_thrill)
        
        # Calculate climax chance
        climax_chance = self._calculate_climax_chance(final_thrill, risk_level)
        
        return {
            "final_thrill": final_thrill,
            "thrill_level": thrill_level,
            "description": thrill_desc,
            "base_thrill": base_thrill,
            "factors": {
                "risk_contribution": int(risk_level * 0.8),
                "intimacy_contribution": intimacy_level * 2,
                "category_bonus": category_bonus,
                "first_time_bonus": self.thrill_modifiers["first_time"] if first_time else 0,
                "new_location_bonus": self.thrill_modifiers["new_location"] if new_location else 0,
                "event_boost": event_boost
            },
            "event": event,
            "climax_chance": climax_chance
        }
        
    def _get_category_bonus(self, category: str) -> int:
        """Dapatkan bonus thrill berdasarkan kategori lokasi"""
        bonuses = {
            "urban": 10,
            "nature": 15,
            "transport": 20,
            "extreme": 30
        }
        return bonuses.get(category, 0)
        
    def _get_thrill_event(self) -> Optional[Dict]:
        """Dapatkan random thrill event"""
        if random.random() < 0.25:  # 25% chance
            events = [e for e in self.thrill_events if random.random() < e['probability']]
            if events:
                return random.choice(events)
        return None
        
    def _get_thrill_level(self, thrill: int) -> tuple:
        """Dapatkan level thrill berdasarkan nilai"""
        for level, (min_val, max_val, desc) in self.thrill_levels.items():
            if min_val <= thrill <= max_val:
                return level, desc
        return "medium", "Deg-degan"
        
    def _calculate_climax_chance(self, thrill: int, risk: int) -> int:
        """
        Hitung chance of climax berdasarkan thrill dan risk
        Thrill tinggi + risk tinggi = high chance
        """
        base_chance = thrill * 0.6
        risk_factor = risk * 0.3
        total_chance = base_chance + risk_factor
        
        return min(95, int(total_chance))
        
    # =========================================================================
    # THRILL EFFECTS
    # =========================================================================
    
    async def get_thrill_effects(self, thrill_data: Dict) -> Dict:
        """
        Dapatkan efek dari thrill level
        """
        thrill = thrill_data['final_thrill']
        
        effects = {
            "heart_rate": self._calculate_heart_rate(thrill),
            "breathing": self._get_breathing_pattern(thrill),
            "sensitivity": self._get_sensitivity(thrill),
            "duration": self._get_duration(thrill),
        }
        
        # Special effects based on thrill level
        if thrill_data['thrill_level'] == "extreme":
            effects['special'] = "Almost climax! Hold on!"
        elif thrill_data['thrill_level'] == "very_high":
            effects['special'] = "Jantung mau copot!"
        elif thrill_data['thrill_level'] == "high":
            effects['special'] = "Deg-degan banget!"
            
        return effects
        
    def _calculate_heart_rate(self, thrill: int) -> str:
        """Hitung heart rate based on thrill"""
        if thrill < 30:
            return "Normal (70-80 bpm)"
        elif thrill < 60:
            return "Agak cepat (90-100 bpm)"
        elif thrill < 80:
            return "Cepat (110-120 bpm)"
        else:
            return "SANGAT CEPAT (130+ bpm)"
            
    def _get_breathing_pattern(self, thrill: int) -> str:
        """Dapatkan pola napas"""
        if thrill < 30:
            return "Normal"
        elif thrill < 60:
            return "Napas agak berat"
        elif thrill < 80:
            return "Napas ngos-ngosan"
        else:
            return "Megap-megap"
            
    def _get_sensitivity(self, thrill: int) -> str:
        """Dapatkan tingkat sensitivitas"""
        if thrill < 30:
            return "Normal"
        elif thrill < 60:
            return "Lebih sensitif"
        elif thrill < 80:
            return "Sangat sensitif"
        else:
            return "EXTREME SENSITIVE"
            
    def _get_duration(self, thrill: int) -> str:
        """Dapatkan durasi (thrill tinggi = cepet)"""
        if thrill < 30:
            return "Bisa tahan lama"
        elif thrill < 60:
            return "Masih bisa tahan"
        elif thrill < 80:
            return "Udah pengen cepet"
        else:
            return "Gak bakal tahan lama"
            
    # =========================================================================
    # THRILL REPORT
    # =========================================================================
    
    def format_thrill_report(self, thrill_data: Dict, location_name: str) -> str:
        """Format thrill report untuk ditampilkan"""
        
        lines = [
            f"📍 **{location_name}**",
            f"🎢 **Thrill Level:** {thrill_data['final_thrill']}% ({thrill_data['thrill_level'].replace('_', ' ').title()})",
            f"📝 {thrill_data['description']}",
            "",
            "**Faktor-faktor:**",
            f"• Kontribusi Risk: +{thrill_data['factors']['risk_contribution']}%",
            f"• Kontribusi Intimacy: +{thrill_data['factors']['intimacy_contribution']}%",
            f"• Bonus Kategori: +{thrill_data['factors']['category_bonus']}%",
        ]
        
        if thrill_data['factors']['first_time_bonus'] > 0:
            lines.append(f"• First Time Bonus: +{thrill_data['factors']['first_time_bonus']}%")
            
        if thrill_data['factors']['new_location_bonus'] > 0:
            lines.append(f"• New Location Bonus: +{thrill_data['factors']['new_location_bonus']}%")
            
        if thrill_data['factors']['event_boost'] > 0:
            lines.append(f"• Event: +{thrill_data['factors']['event_boost']}%")
            
        lines.append("")
        lines.append(f"🎯 **Climax Chance:** {thrill_data['climax_chance']}%")
        
        if thrill_data.get('event'):
            lines.append("")
            lines.append(f"🎲 **Thrill Event:** {thrill_data['event']['name']}")
            
        return "\n".join(lines)
        
    async def get_thrill_history_summary(self, thrills: List[int]) -> str:
        """Get summary dari history thrill"""
        if not thrills:
            return "Belum ada data thrill"
            
        avg_thrill = sum(thrills) / len(thrills)
        max_thrill = max(thrills)
        min_thrill = min(thrills)
        
        trend = "meningkat" if thrills[-1] > thrills[0] else "menurun"
        
        return (
            f"📊 **Thrill History Summary**\n"
            f"Rata-rata: {avg_thrill:.1f}%\n"
            f"Tertinggi: {max_thrill}%\n"
            f"Terendah: {min_thrill}%\n"
            f"Trend: {trend}"
        )


__all__ = ['ThrillSystem']
