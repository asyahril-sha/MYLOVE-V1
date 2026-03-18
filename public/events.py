#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - RANDOM EVENTS SYSTEM
=============================================================================
- Random events saat public sex
- Events bisa positif atau negatif
- Mempengaruhi risk, thrill, dan kelanjutan sesi
"""

import random
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class RandomEvents:
    """
    Sistem random events untuk public sex
    Events terjadi secara random dengan probabilitas tertentu
    """
    
    def __init__(self):
        # =========================================================================
        # POSITIVE EVENTS (menguntungkan)
        # =========================================================================
        self.positive_events = [
            {
                "id": "lampu_mati",
                "name": "💡 Lampu Mati Mendadak",
                "description": "Lampu tiba-tiba mati, suasana jadi lebih gelap",
                "risk_change": -20,
                "thrill_change": 15,
                "continuation": "lanjut",
                "message": "Wah lampu mati! Makin gelap, makin berani!",
                "probability": 0.1
            },
            {
                "id": "hujan_deras",
                "name": "🌧️ Hujan Deras",
                "description": "Hujan turun deras, orang-orang pada berlindung",
                "risk_change": -30,
                "thrill_change": 25,
                "continuation": "lanjut",
                "message": "Hujan deras! Tempat jadi sepi, bisa lebih leluasa",
                "probability": 0.15
            },
            {
                "id": "cctv_mati",
                "name": "📹 CCTV Mati",
                "description": "CCTV tiba-tiba mati, tidak ada yang merekam",
                "risk_change": -40,
                "thrill_change": 20,
                "continuation": "lanjut",
                "message": "CCTV mati! Aman dari rekaman!",
                "probability": 0.05
            },
            {
                "id": "satpam_tidur",
                "name": "💤 Satpam Ketiduran",
                "description": "Satpam yang jaga lagi tidur pulas",
                "risk_change": -30,
                "thrill_change": 10,
                "continuation": "lanjut",
                "message": "Satpam-nya tidur... gas pol!",
                "probability": 0.08
            },
            {
                "id": "musik_rame",
                "name": "🎵 Musik Ramai",
                "description": "Ada acara dengan musik keras, menutupi suara",
                "risk_change": -25,
                "thrill_change": 15,
                "continuation": "lanjut",
                "message": "Musik keras, bisa teriak-teriak!",
                "probability": 0.12
            },
            {
                "id": "listrik_padam",
                "name": "⚡ Listrik Padam",
                "description": "Listrik padam total, gelap gulita",
                "risk_change": -35,
                "thrill_change": 30,
                "continuation": "lanjut",
                "message": "Gelap total! Bebas bergerak!",
                "probability": 0.05
            },
            {
                "id": "kabut_tebal",
                "name": "🌫️ Kabut Tebal",
                "description": "Kabut turun sangat tebal, jarak pandang pendek",
                "risk_change": -40,
                "thrill_change": 25,
                "continuation": "lanjut",
                "message": "Kabut tebal... kayak di film horor tapi romantis",
                "probability": 0.07
            },
            {
                "id": "angin_kencang",
                "name": "💨 Angin Kencang",
                "description": "Angin kencang, orang pada tutup mata",
                "risk_change": -15,
                "thrill_change": 10,
                "continuation": "lanjut",
                "message": "Angin kencang, waktu yang tepat!",
                "probability": 0.1
            }
        ]
        
        # =========================================================================
        # NEGATIVE EVENTS (merugikan)
        # =========================================================================
        self.negative_events = [
            {
                "id": "orang_lewat",
                "name": "👥 Ada Orang Lewat",
                "description": "Seseorang tiba-tiba lewat dan melihat",
                "risk_change": 30,
                "thrill_change": 40,
                "continuation": "berhenti",
                "message": "Ada orang lihat! Cepet cabut!",
                "probability": 0.2
            },
            {
                "id": "satpam_rontgen",
                "name": "🔦 Satpam Ronda",
                "description": "Satpam lagi ronda bawa senter",
                "risk_change": 40,
                "thrill_change": 35,
                "continuation": "berhenti",
                "message": "Satpam! Sembunyi!",
                "probability": 0.15
            },
            {
                "id": "hp_berdering",
                "name": "📱 HP Berdering",
                "description": "HP tiba-tiba bunyi kencang",
                "risk_change": 25,
                "thrill_change": 20,
                "continuation": "berhenti",
                "message": "HP bunyi! Dimatiin cepet!",
                "probability": 0.15
            },
            {
                "id": "anak_anak",
                "name": "🧒 Anak-anak Lewat",
                "description": "Anak-anak main ke tempat ini",
                "risk_change": 50,
                "thrill_change": 45,
                "continuation": "berhenti",
                "message": "Ada anak-anak! Kabur!",
                "probability": 0.1
            },
            {
                "id": "polisi",
                "name": "👮 Polisi Patroli",
                "description": "Polisi lagi patroli, lihat mencurigakan",
                "risk_change": 70,
                "thrill_change": 60,
                "continuation": "berhenti",
                "message": "POLISI! CEPET SEMBUNYI!",
                "probability": 0.05
            },
            {
                "id": "fotografer",
                "name": "📸 Ada yang Foto",
                "description": "Seseorang memfoto ke arah kalian",
                "risk_change": 60,
                "thrill_change": 50,
                "continuation": "berhenti",
                "message": "WAH KEFOTO! Cepet cabut!",
                "probability": 0.05
            },
            {
                "id": "kepeleset",
                "name": "😵 Kepeleset",
                "description": "Kepeleset waktu gerak, jatuh",
                "risk_change": 20,
                "thrill_change": -10,
                "continuation": "lanjut",
                "message": "Aduh kepeleset! Sakit...",
                "probability": 0.08
            },
            {
                "id": "ketahuan_pasangan",
                "name": "💔 Dilihat Pasangan Lain",
                "description": "Pasangan lain lihat dan teriak",
                "risk_change": 50,
                "thrill_change": 45,
                "continuation": "berhenti",
                "message": "WAH KETAHUAN! Malu!",
                "probability": 0.05
            },
            {
                "id": "kejatuhan_burung",
                "name": "🐦 Kejatuhan Burung",
                "description": "Kejatuhan kotoran burung",
                "risk_change": 5,
                "thrill_change": -20,
                "continuation": "lanjut",
                "message": "Ih kejatuhan burung... jorok",
                "probability": 0.03
            },
            {
                "id": "dikejar_anjing",
                "name": "🐕 Dikejar Anjing",
                "description": "Anjing liar datang dan menggonggong",
                "risk_change": 40,
                "thrill_change": 35,
                "continuation": "berhenti",
                "message": "Ada anjing! Lari!",
                "probability": 0.04
            }
        ]
        
        # =========================================================================
        # NEUTRAL EVENTS (hanya untuk thrill)
        # =========================================================================
        self.neutral_events = [
            {
                "id": "bintang_jatuh",
                "name": "⭐ Bintang Jatuh",
                "description": "Bintang jatuh, momen romantis",
                "risk_change": 0,
                "thrill_change": 15,
                "continuation": "lanjut",
                "message": "Wah bintang jatuh! Cepat minta!",
                "probability": 0.05
            },
            {
                "id": "kucing_lewat",
                "name": "🐱 Kucing Lewat",
                "description": "Kucing lewat dan mengeong",
                "risk_change": 0,
                "thrill_change": 5,
                "continuation": "lanjut",
                "message": "Meong... kucing lihatin",
                "probability": 0.1
            },
            {
                "id": "suara_aneh",
                "name": "👻 Suara Aneh",
                "description": "Suara aneh dari kejauhan",
                "risk_change": 5,
                "thrill_change": 15,
                "continuation": "lanjut",
                "message": "Suara apa itu? Serem...",
                "probability": 0.1
            },
            {
                "id": "hujan_rintik",
                "name": "🌦️ Hujan Rintik",
                "description": "Hujan rintik-rintik, romantis",
                "risk_change": -5,
                "thrill_change": 10,
                "continuation": "lanjut",
                "message": "Hujan rintik... dingin tapi romantis",
                "probability": 0.15
            },
            {
                "id": "angin_sepoi",
                "name": "🍃 Angin Sepoi",
                "description": "Angin sepoi-sepoi, sejuk",
                "risk_change": -5,
                "thrill_change": 5,
                "continuation": "lanjut",
                "message": "Angin sepoi... adem",
                "probability": 0.15
            }
        ]
        
        # Gabungkan semua events
        self.all_events = (
            self.positive_events + 
            self.negative_events + 
            self.neutral_events
        )
        
        logger.info(f"✅ RandomEvents initialized: {len(self.all_events)} events")
        
    # =========================================================================
    # GET RANDOM EVENT
    # =========================================================================
    
    async def get_random_event(
        self,
        location_category: str,
        risk_level: int,
        time_category: str
    ) -> Optional[Dict]:
        """
        Dapatkan random event berdasarkan kondisi
        
        Args:
            location_category: Kategori lokasi
            risk_level: Risk level saat ini
            time_category: Kategori waktu
            
        Returns:
            Event atau None
        """
        # Base probability
        base_prob = 0.3  # 30% chance of event
        
        # Adjust based on risk
        if risk_level > 70:
            base_prob *= 1.5  # High risk = lebih banyak event
        elif risk_level < 30:
            base_prob *= 0.7  # Low risk = lebih sedikit event
            
        # Adjust based on time
        if time_category in ["tengah_malam", "malam"]:
            base_prob *= 1.3  # Malam lebih banyak event
        elif time_category in ["pagi", "siang"]:
            base_prob *= 0.8  # Siang lebih sedikit
            
        # Roll for event
        if random.random() > base_prob:
            return None
            
        # Filter events by category bias
        if location_category == "extreme":
            # Extreme places have more negative events
            events_pool = self.negative_events * 2 + self.positive_events + self.neutral_events
        elif location_category == "nature":
            # Nature has more neutral events
            events_pool = self.neutral_events * 2 + self.positive_events + self.negative_events
        else:
            events_pool = self.all_events
            
        # Random pick
        event = random.choice(events_pool)
        
        # Check probability
        if random.random() > event['probability']:
            return None
            
        logger.info(f"🎲 Random event triggered: {event['name']}")
        
        return event.copy()
        
    # =========================================================================
    # EVENT BY LOCATION
    # =========================================================================
    
    def get_events_by_location(self, location_id: str) -> List[Dict]:
        """Dapatkan events spesifik untuk lokasi"""
        # Ini bisa dikustom per lokasi
        # Untuk sekarang return semua events
        return self.all_events
        
    def get_events_by_category(self, category: str) -> Dict:
        """Dapatkan events berdasarkan kategori"""
        if category == "positive":
            return self.positive_events
        elif category == "negative":
            return self.negative_events
        elif category == "neutral":
            return self.neutral_events
        else:
            return self.all_events
            
    # =========================================================================
    # EVENT HANDLING
    # =========================================================================
    
    async def process_event(
        self,
        event: Dict,
        current_risk: int,
        current_thrill: int
    ) -> Dict:
        """
        Proses event dan dapatkan hasilnya
        
        Args:
            event: Event yang terjadi
            current_risk: Risk saat ini
            current_thrill: Thrill saat ini
            
        Returns:
            Updated risk, thrill, dan consequences
        """
        # Apply changes
        new_risk = current_risk + event.get('risk_change', 0)
        new_thrill = current_thrill + event.get('thrill_change', 0)
        
        # Ensure bounds
        new_risk = max(0, min(100, new_risk))
        new_thrill = max(0, min(100, new_thrill))
        
        # Generate response based on event
        response = self._generate_event_response(event, new_risk, new_thrill)
        
        return {
            "event": event,
            "old_risk": current_risk,
            "new_risk": new_risk,
            "old_thrill": current_thrill,
            "new_thrill": new_thrill,
            "continuation": event.get('continuation', 'lanjut'),
            "response": response
        }
        
    def _generate_event_response(self, event: Dict, new_risk: int, new_thrill: int) -> str:
        """Generate response text untuk event"""
        
        base_msg = event.get('message', event['name'])
        
        if event.get('risk_change', 0) > 0:
            risk_msg = f"⚠️ Risk naik {event['risk_change']}%!"
        elif event.get('risk_change', 0) < 0:
            risk_msg = f"✅ Risk turun {abs(event['risk_change'])}%!"
        else:
            risk_msg = ""
            
        if event.get('thrill_change', 0) > 0:
            thrill_msg = f"🎢 Thrill naik {event['thrill_change']}%!"
        elif event.get('thrill_change', 0) < 0:
            thrill_msg = f"😰 Thrill turun {abs(event['thrill_change'])}%!"
        else:
            thrill_msg = ""
            
        messages = [base_msg]
        if risk_msg:
            messages.append(risk_msg)
        if thrill_msg:
            messages.append(thrill_msg)
            
        return "\n".join(messages)
        
    # =========================================================================
    # EVENT STATISTICS
    # =========================================================================
    
    def get_event_stats(self) -> Dict:
        """Get event statistics"""
        return {
            "total_events": len(self.all_events),
            "positive": len(self.positive_events),
            "negative": len(self.negative_events),
            "neutral": len(self.neutral_events),
            "avg_risk_change": sum(e.get('risk_change', 0) for e in self.all_events) / len(self.all_events),
            "avg_thrill_change": sum(e.get('thrill_change', 0) for e in self.all_events) / len(self.all_events),
        }
        
    def format_event_description(self, event: Dict) -> str:
        """Format event description untuk display"""
        return (
            f"**{event['name']}**\n"
            f"{event['description']}\n"
            f"Risk: {event.get('risk_change', 0):+}% | "
            f"Thrill: {event.get('thrill_change', 0):+}%"
        )


__all__ = ['RandomEvents']
