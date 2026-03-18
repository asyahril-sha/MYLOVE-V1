#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - RISK CALCULATION SYSTEM
=============================================================================
- Dynamic risk calculation berdasarkan banyak faktor
- Risk berubah sesuai waktu, tempat, situasi
- Consequences jika ketahuan
"""

import random
import math
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class RiskCalculator:
    """
    Menghitung risk level secara dinamis
    Risk berubah berdasarkan:
    - Waktu (pagi/siang/malam)
    - Hari (weekday/weekend)
    - Cuaca (hujan/cerah)
    - Lokasi spesifik
    - Random events
    """
    
    def __init__(self):
        # Faktor pengali risk
        self.time_multipliers = {
            "pagi": 0.8,      # 05-10: risk lebih rendah
            "siang": 1.2,      # 10-14: risk tinggi (banyak orang)
            "sore": 1.1,       # 14-18: risk medium
            "malam": 0.7,      # 18-22: risk mulai turun
            "tengah_malam": 0.5,  # 22-05: risk paling rendah
        }
        
        self.day_multipliers = {
            "weekday": 1.2,    # Senin-Jumat: risk tinggi
            "weekend": 0.8,     # Sabtu-Minggu: risk rendah
        }
        
        self.weather_multipliers = {
            "cerah": 1.0,
            "gerimis": 0.9,
            "hujan": 0.7,
            "badai": 0.5,
        }
        
        # Random events yang bisa terjadi
        self.random_events = [
            {
                "name": "ada orang lewat",
                "risk_increase": 20,
                "thrill_increase": 15,
                "probability": 0.3
            },
            {
                "name": "satpam keliling",
                "risk_increase": 40,
                "thrill_increase": 30,
                "probability": 0.2
            },
            {
                "name": "CCTV mati",
                "risk_decrease": 30,
                "thrill_increase": 20,
                "probability": 0.1
            },
            {
                "name": "anak kecil lewat",
                "risk_increase": 50,
                "thrill_increase": 40,
                "probability": 0.15
            },
            {
                "name": "lampu mati",
                "risk_decrease": 40,
                "thrill_increase": 30,
                "probability": 0.1
            },
            {
                "name": "ada pasangan lain",
                "risk_increase": 60,
                "thrill_increase": 50,
                "probability": 0.05
            },
            {
                "name": "kejatuhan kotoran burung",
                "risk_decrease": 10,
                "thrill_decrease": 30,
                "probability": 0.02
            },
            {
                "name": "hujan deras",
                "risk_decrease": 50,
                "thrill_increase": 40,
                "probability": 0.1
            },
        ]
        
        logger.info("✅ RiskCalculator initialized")
        
    # =========================================================================
    # GET CURRENT CONDITIONS
    # =========================================================================
    
    def get_current_time_category(self) -> str:
        """Dapatkan kategori waktu saat ini"""
        hour = datetime.now().hour
        
        if 5 <= hour < 10:
            return "pagi"
        elif 10 <= hour < 14:
            return "siang"
        elif 14 <= hour < 18:
            return "sore"
        elif 18 <= hour < 22:
            return "malam"
        else:
            return "tengah_malam"
            
    def get_current_day_category(self) -> str:
        """Dapatkan kategori hari"""
        # 0 = Monday, 6 = Sunday
        weekday = datetime.now().weekday()
        
        if weekday < 5:  # Senin-Jumat
            return "weekday"
        else:
            return "weekend"
            
    def get_weather_category(self, weather: str = "cerah") -> str:
        """Dapatkan kategori cuaca (default cerah)"""
        if weather in self.weather_multipliers:
            return weather
        return "cerah"
        
    # =========================================================================
    # CALCULATE RISK
    # =========================================================================
    
    async def calculate_risk(
        self,
        base_risk: int,
        time_category: Optional[str] = None,
        day_category: Optional[str] = None,
        weather: str = "cerah",
        intimacy_level: int = 1,
        previous_visits: int = 0
    ) -> Dict:
        """
        Hitung risk level dinamis
        
        Args:
            base_risk: Risk dasar lokasi (0-100)
            time_category: Kategori waktu
            day_category: Kategori hari
            weather: Kondisi cuaca
            intimacy_level: Level intimacy (makin tinggi makin berani)
            previous_visits: Jumlah kunjungan sebelumnya
            
        Returns:
            Dict dengan risk details
        """
        # Get current conditions if not provided
        if not time_category:
            time_category = self.get_current_time_category()
        if not day_category:
            day_category = self.get_current_day_category()
            
        # Start with base risk
        current_risk = base_risk
        
        # Apply time multiplier
        time_mult = self.time_multipliers.get(time_category, 1.0)
        current_risk *= time_mult
        
        # Apply day multiplier
        day_mult = self.day_multipliers.get(day_category, 1.0)
        current_risk *= day_mult
        
        # Apply weather multiplier
        weather_mult = self.weather_multipliers.get(weather, 1.0)
        current_risk *= weather_mult
        
        # Intimacy level effect (makin tinggi makin berani, risk naik)
        intimacy_factor = 1.0 + (intimacy_level / 100)  # Max +12%
        current_risk *= intimacy_factor
        
        # Previous visits (makin sering makin tahu tempat, risk turun)
        if previous_visits > 0:
            experience_factor = max(0.7, 1.0 - (previous_visits * 0.02))
            current_risk *= experience_factor
            
        # Random events
        event = self._get_random_event()
        event_effect = {}
        
        if event:
            if 'risk_increase' in event:
                current_risk += event['risk_increase']
                event_effect['risk_change'] = event['risk_increase']
            elif 'risk_decrease' in event:
                current_risk -= event['risk_decrease']
                event_effect['risk_change'] = -event['risk_decrease']
                
        # Ensure within bounds
        final_risk = max(0, min(100, int(current_risk)))
        
        # Determine risk level category
        if final_risk < 30:
            risk_level = "RENDAH"
            risk_desc = "Aman banget, santai aja"
        elif final_risk < 50:
            risk_level = "SEDANG"
            risk_desc = "Lumayan aman, tapi tetep hati-hati"
        elif final_risk < 70:
            risk_level = "TINGGI"
            risk_desc = "Wah risk tinggi, harus cepet"
        elif final_risk < 90:
            risk_level = "SANGAT TINGGI"
            risk_desc = "Berani banget! Cepet-cepet!"
        else:
            risk_level = "EXTREME"
            risk_desc = "GILA! Nyaris ketahuan!"
            
        return {
            "final_risk": final_risk,
            "risk_level": risk_level,
            "description": risk_desc,
            "base_risk": base_risk,
            "factors": {
                "time": {
                    "category": time_category,
                    "multiplier": time_mult
                },
                "day": {
                    "category": day_category,
                    "multiplier": day_mult
                },
                "weather": {
                    "condition": weather,
                    "multiplier": weather_mult
                },
                "intimacy": {
                    "level": intimacy_level,
                    "factor": intimacy_factor
                },
                "experience": {
                    "visits": previous_visits,
                    "factor": experience_factor if previous_visits > 0 else 1.0
                }
            },
            "event": event
        }
        
    def _get_random_event(self) -> Optional[Dict]:
        """Dapatkan random event berdasarkan probabilitas"""
        if random.random() < 0.3:  # 30% chance of event
            # Filter events by probability
            events = [e for e in self.random_events if random.random() < e['probability']]
            if events:
                return random.choice(events)
        return None
        
    # =========================================================================
    # CONSEQUENCES
    # =========================================================================
    
    async def get_consequence(self, risk_level: int) -> Dict:
        """
        Dapatkan konsekuensi berdasarkan risk level
        Dipanggil jika ketahuan
        """
        consequences = {
            "very_low": [
                "Cuma diliatin doang",
                "Ditegor terus pergi",
                "Dikira orang mabuk",
            ],
            "low": [
                "Dimarahi satpam",
                "Disuruh pergi",
                "Dikata-katain",
            ],
            "medium": [
                "Diusir paksa",
                "Dilaporkan ke keamanan",
                "Difotoin",
            ],
            "high": [
                "Dibawa ke kantor polisi",
                "Viral di sosmed",
                "Dikenalin ke keluarga",
            ],
            "extreme": [
                "Ditangkap",
                "Dijeblosin penjara",
                "Rumah digeruduk warga",
            ]
        }
        
        # Pilih berdasarkan risk
        if risk_level < 20:
            cons = random.choice(consequences["very_low"])
            severity = "Ringan"
        elif risk_level < 40:
            cons = random.choice(consequences["low"])
            severity = "Sedang"
        elif risk_level < 60:
            cons = random.choice(consequences["medium"])
            severity = "Berat"
        elif risk_level < 80:
            cons = random.choice(consequences["high"])
            severity = "Sangat Berat"
        else:
            cons = random.choice(consequences["extreme"])
            severity = "EXTREME"
            
        return {
            "consequence": cons,
            "severity": severity,
            "risk_level": risk_level,
            "intimacy_penalty": int(risk_level / 10),  # Turun level intimacy
            "public_shame": risk_level > 70
        }
        
    # =========================================================================
    # THRILL CALCULATION
    # =========================================================================
    
    async def calculate_thrill(
        self,
        base_thrill: int,
        risk: int,
        intimacy_level: int,
        first_time: bool = False
    ) -> int:
        """
        Hitung thrill level
        
        Thrill = base_thrill + (risk * 0.5) + (intimacy * 2) + (first_time ? 20 : 0)
        """
        thrill = base_thrill
        
        # Higher risk = higher thrill
        thrill += risk * 0.5
        
        # Intimacy level adds thrill
        thrill += intimacy_level * 2
        
        # First time bonus
        if first_time:
            thrill += 20
            
        return min(100, int(thrill))
        
    # =========================================================================
    # RISK REPORT
    # =========================================================================
    
    def format_risk_report(self, risk_data: Dict, location_name: str) -> str:
        """Format risk report untuk ditampilkan"""
        
        lines = [
            f"📍 **{location_name}**",
            f"⚠️ **Risk Level:** {risk_data['final_risk']}% ({risk_data['risk_level']})",
            f"📝 {risk_data['description']}",
            "",
            "**Faktor-faktor:**",
        ]
        
        # Faktor waktu
        time_factor = risk_data['factors']['time']
        lines.append(f"• Waktu ({time_factor['category']}): x{time_factor['multiplier']:.1f}")
        
        # Faktor hari
        day_factor = risk_data['factors']['day']
        lines.append(f"• Hari ({day_factor['category']}): x{day_factor['multiplier']:.1f}")
        
        # Faktor cuaca
        weather_factor = risk_data['factors']['weather']
        lines.append(f"• Cuaca ({weather_factor['condition']}): x{weather_factor['multiplier']:.1f}")
        
        # Faktor pengalaman
        exp_factor = risk_data['factors']['experience']
        if exp_factor['visits'] > 0:
            lines.append(f"• Pengalaman ({exp_factor['visits']}x): x{exp_factor['factor']:.1f}")
            
        # Random event
        if risk_data.get('event'):
            event = risk_data['event']
            lines.append("")
            lines.append(f"🎲 **Random Event:** {event.get('name', '')}")
            if 'risk_increase' in event:
                lines.append(f"⚠️ Risk +{event['risk_increase']}%")
            elif 'risk_decrease' in event:
                lines.append(f"✅ Risk -{event['risk_decrease']}%")
                
        return "\n".join(lines)


__all__ = ['RiskCalculator']
