#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - AUTO LOCATION SELECTOR
=============================================================================
- Auto-detect lokasi dari chat user
- Tidak perlu command khusus
- Natural language processing sederhana
"""

import re
import random
import logging
from typing import Dict, List, Optional, Tuple
from difflib import get_close_matches

from .locations import PublicLocations

logger = logging.getLogger(__name__)


class LocationAutoSelector:
    """
    Auto-detect lokasi dari chat user
    User bisa ngomong natural, bot akan detect
    """
    
    def __init__(self):
        self.locations_db = PublicLocations()
        
        # =========================================================================
        # KEYWORDS DATABASE
        # =========================================================================
        self.location_keywords = {
            # Toilet
            "toilet": ["toilet", "wc", "kamar kecil", "restroom", "wc umum"],
            "toilet_mall": ["toilet mall", "wc mall", "kamar kecil mall"],
            "toilet_spbu": ["toilet pom", "wc pom", "toilet spbu", "wc spbu"],
            "toilet_restoran": ["toilet restoran", "wc restoran", "toilet restaurant"],
            "toilet_stasiun": ["toilet stasiun", "wc stasiun", "toilet station"],
            "toilet_terminal": ["toilet terminal", "wc terminal"],
            
            # Mall & Shopping
            "mall": ["mall", "mal", "shopping mall", "plaza", "shopping center"],
            "parkir_mall": ["parkir mall", "parkiran mall", "basement mall", "parking mall"],
            "tangga_darurat": ["tangga darurat", "emergency stairs", "tangga belakang"],
            "rooftop": ["rooftop", "atap", "roof", "atas mall", "puncak"],
            "fitting_room": ["kamar pas", "fitting room", "ruang ganti", "coba baju"],
            
            # Parkiran
            "parkir": ["parkir", "parkiran", "parking", "basement", "parking lot"],
            "parkir_gedung": ["parkir gedung", "parkiran kantor"],
            "parkir_apartemen": ["parkir apartemen", "basement apartemen"],
            "parkir_rumah_sakit": ["parkir rs", "parkir rumah sakit"],
            
            # Lift & Tangga
            "lift": ["lift", "elevator", "elevator", "lif"],
            "lift_hotel": ["lift hotel", "elevator hotel"],
            "lift_kantor": ["lift kantor", "elevator kantor"],
            "tangga": ["tangga", "stairs", "anak tangga"],
            
            # Transportasi
            "mobil": ["mobil", "car", "mobil pribadi", "dalem mobil"],
            "taksi": ["taksi", "taxi", "grab", "gojek", "go-car"],
            "ojek": ["ojek", "motor", "gojek", "grab motor"],
            "bus": ["bus", "bis", "bus malam", "bis malam"],
            "kereta": ["kereta", "train", "krl", "commuter"],
            "kapal": ["kapal", "feri", "ship", "boat"],
            "pesawat": ["pesawat", "plane", "garuda", "airplane"],
            
            # Alam
            "pantai": ["pantai", "beach", "laut", "pinggir laut"],
            "hutan": ["hutan", "forest", "hutan kota", "rimba"],
            "taman": ["taman", "park", "taman kota"],
            "kebun": ["kebun", "perkebunan", "garden"],
            "sawah": ["sawah", "padi", "rice field"],
            "bukit": ["bukit", "hill", "perbukitan"],
            "air_terjun": ["air terjun", "waterfall", "curug"],
            "danau": ["danau", "lake", "telaga"],
            
            # Extreme
            "masjid": ["masjid", "mushola", "mosque"],
            "gereja": ["gereja", "church"],
            "polisi": ["polisi", "kantor polisi", "police"],
            "sekolah": ["sekolah", "school", "kampus"],
            "rumah_sakit": ["rumah sakit", "rs", "hospital"],
            "kuburan": ["kuburan", "makam", "cemetery"],
            
            # Halte & Terminal
            "halte": ["halte", "halte bus", "bus stop"],
            "terminal": ["terminal", "terminal bus"],
            "stasiun": ["stasiun", "station", "stasiun kereta"],
        }
        
        # =========================================================================
        # PHRASE PATTERNS
        # =========================================================================
        self.phrase_patterns = [
            # Ajakan
            (r"ajak (?:ke|di) (\w+)", "invite"),
            (r"yuk (?:ke|di) (\w+)", "invite"),
            (r"ayo (?:ke|di) (\w+)", "invite"),
            (r"mau (?:ke|di) (\w+)", "want"),
            (r"pengen (?:ke|di) (\w+)", "want"),
            
            # Tanya
            (r"ada (?:tempat|lokasi) (\w+)", "ask"),
            (r"cari (?:tempat|lokasi) (\w+)", "ask"),
            (r"tempat (\w+) (?:ada|ga)", "ask"),
            
            # Lokasi spesifik
            (r"di (\w+) aja", "specific"),
            (r"ke (\w+) yuk", "specific"),
            (r"main ke (\w+)", "specific"),
        ]
        
        logger.info("✅ LocationAutoSelector initialized")
        
    # =========================================================================
    # DETECT LOCATION FROM MESSAGE
    # =========================================================================
    
    async def detect_location(self, message: str) -> Optional[Dict]:
        """
        Detect lokasi dari pesan user
        
        Args:
            message: Pesan dari user
            
        Returns:
            Location dict or None
        """
        message_lower = message.lower().strip()
        
        # Cek pattern phrases
        location_name = self._check_phrases(message_lower)
        if location_name:
            # Cari lokasi berdasarkan nama
            location = self._find_location_by_name(location_name)
            if location:
                logger.info(f"📍 Detected location from phrase: {location['name']}")
                return location
                
        # Cek keywords
        for loc_id, keywords in self.location_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    # Cari lokasi berdasarkan ID
                    location = self.locations_db.get_location_by_id(loc_id)
                    if location:
                        logger.info(f"📍 Detected location from keyword: {location['name']}")
                        return location
                        
        # Fuzzy match (jika ada kata yang mirip)
        words = message_lower.split()
        for word in words:
            if len(word) > 3:  # Skip kata pendek
                matches = self._fuzzy_match_location(word)
                if matches:
                    logger.info(f"📍 Detected location from fuzzy match: {matches[0]['name']}")
                    return matches[0]
                    
        return None
        
    def _check_phrases(self, message: str) -> Optional[str]:
        """Check phrase patterns"""
        for pattern, pattern_type in self.phrase_patterns:
            match = re.search(pattern, message)
            if match and len(match.groups()) > 0:
                return match.group(1)
        return None
        
    def _find_location_by_name(self, name: str) -> Optional[Dict]:
        """Cari lokasi berdasarkan nama"""
        name_lower = name.lower()
        
        # Cek semua lokasi
        for loc in self.locations_db.all_locations:
            if name_lower in loc['name'].lower():
                return loc
                
        return None
        
    def _fuzzy_match_location(self, word: str, cutoff: float = 0.7) -> List[Dict]:
        """Fuzzy match untuk kata yang mirip"""
        matches = []
        
        for loc in self.locations_db.all_locations:
            # Compare with location name
            similarity = self._similarity(word, loc['name'].lower())
            if similarity > cutoff:
                matches.append((loc, similarity))
                
        # Sort by similarity
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return [m[0] for m in matches[:3]]
        
    def _similarity(self, a: str, b: str) -> float:
        """Simple similarity ratio"""
        # Gunakan set intersection
        set_a = set(a)
        set_b = set(b)
        
        if not set_a or not set_b:
            return 0.0
            
        intersection = set_a.intersection(set_b)
        union = set_a.union(set_b)
        
        return len(intersection) / len(union)
        
    # =========================================================================
    # GET LOCATION SUGGESTIONS
    # =========================================================================
    
    async def get_suggestions(self, message: str, limit: int = 3) -> List[Dict]:
        """
        Dapatkan suggestions lokasi berdasarkan message
        
        Args:
            message: Pesan user
            limit: Jumlah suggestions
            
        Returns:
            List of locations
        """
        message_lower = message.lower()
        
        # Cari keyword yang match
        matched_keywords = []
        for loc_id, keywords in self.location_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    matched_keywords.append(loc_id)
                    
        # Ambil lokasi berdasarkan matched keywords
        suggestions = []
        for loc_id in matched_keywords[:limit]:
            loc = self.locations_db.get_location_by_id(loc_id)
            if loc and loc not in suggestions:
                suggestions.append(loc)
                
        # Jika kurang, tambah random
        if len(suggestions) < limit:
            random_locs = random.sample(
                self.locations_db.all_locations,
                min(limit - len(suggestions), len(self.locations_db.all_locations))
            )
            for loc in random_locs:
                if loc not in suggestions:
                    suggestions.append(loc)
                    
        return suggestions[:limit]
        
    # =========================================================================
    # FORMAT SUGGESTIONS
    # =========================================================================
    
    def format_suggestions(self, suggestions: List[Dict]) -> str:
        """Format suggestions untuk ditampilkan"""
        if not suggestions:
            return "Tidak ada suggestions"
            
        lines = ["📍 **Tempat yang tersedia:**"]
        
        for i, loc in enumerate(suggestions, 1):
            lines.append(
                f"{i}. **{loc['name']}**\n"
                f"   Risk: {loc['base_risk']}% | Thrill: {loc['base_thrill']}%\n"
                f"   _{loc['description'][:50]}..._"
            )
            
        lines.append("")
        lines.append("💡 _Ketik tempat yang kamu mau, misal: 'ke pantai yuk'_")
        
        return "\n".join(lines)
        
    # =========================================================================
    # AUTO-SELECT BY MOOD/CONTEXT
    # =========================================================================
    
    async def select_by_mood(self, mood: str, intimacy_level: int) -> Dict:
        """
        Select location based on mood
        
        Args:
            mood: Mood saat ini
            intimacy_level: Level intimacy
            
        Returns:
            Selected location
        """
        if mood in ["rindu", "sayang"]:
            # Romantic places
            candidates = self.locations_db.get_locations_by_category("nature")
        elif mood in ["nakal", "genit"]:
            # Risky places
            candidates = self.locations_db.get_locations_by_risk(60, 100)
        elif mood in ["capek", "malas"]:
            # Easy places
            candidates = self.locations_db.get_locations_by_risk(0, 40)
        else:
            # Random
            candidates = self.locations_db.all_locations
            
        # Adjust by intimacy
        if intimacy_level > 7:
            # High intimacy = more risky
            candidates = [c for c in candidates if c['base_risk'] > 50]
            
        return random.choice(candidates) if candidates else self.locations_db.get_random_location()
        
    async def select_random(self, risk_preference: str = "medium") -> Dict:
        """
        Select random location with risk preference
        
        Args:
            risk_preference: "low", "medium", "high"
            
        Returns:
            Selected location
        """
        if risk_preference == "low":
            candidates = self.locations_db.get_locations_by_risk(0, 40)
        elif risk_preference == "high":
            candidates = self.locations_db.get_locations_by_risk(60, 100)
        else:
            candidates = self.locations_db.get_locations_by_risk(30, 70)
            
        return random.choice(candidates) if candidates else self.locations_db.get_random_location()
        
    # =========================================================================
    # UTILITY
    # =========================================================================
    
    def get_location_stats(self) -> Dict:
        """Get location selector statistics"""
        return {
            "total_locations": len(self.locations_db.all_locations),
            "keyword_categories": len(self.location_keywords),
            "total_keywords": sum(len(kw) for kw in self.location_keywords.values()),
            "phrase_patterns": len(self.phrase_patterns)
        }
        
    def get_help_text(self) -> str:
        """Get help text for location selection"""
        return (
            "📍 **Cara Pilih Lokasi Public Sex**\n\n"
            "Kamu bisa langsung ngomong natural:\n"
            "• 'Ajak ke toilet yuk'\n"
            "• 'Main di mobil aja'\n"
            "• 'Ke pantai malam yuk'\n"
            "• 'Cari tempat sepi'\n\n"
            "Bot akan otomatis detect dan kasih tau risk-nya!\n\n"
            "**Kategori Lokasi:**\n"
            "🏙️ Urban (mall, toilet, parkiran)\n"
            "🌳 Alam (pantai, hutan, kebun)\n"
            "⚡ Extreme (masjid, polisi, kuburan)\n"
            "🚗 Transport (mobil, kereta, pesawat)"
        )


__all__ = ['LocationAutoSelector']
