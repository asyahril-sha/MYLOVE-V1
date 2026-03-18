#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - LOCATION SYSTEM (FIX LENGKAP)
=============================================================================
Sistem lokasi dinamis untuk bot
- 10+ lokasi dengan deskripsi detail
- Perpindahan random (5% chance per pesan)
- Efek lokasi ke mood, pakaian, dan aktivitas
- Cooldown perpindahan
=============================================================================
"""

import random
import time
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class LocationType(str, Enum):
    """Enum untuk tipe lokasi"""
    LIVING_ROOM = "living_room"
    BEDROOM = "bedroom"
    KITCHEN = "kitchen"
    BATHROOM = "bathroom"
    BALCONY = "balcony"
    TERRACE = "terrace"
    GARDEN = "garden"
    DINING_ROOM = "dining_room"
    GUEST_ROOM = "guest_room"
    STUDY_ROOM = "study_room"


class LocationSystem:
    """
    Sistem lokasi dinamis
    Bot bisa pindah-pindah lokasi secara random
    Setiap lokasi punya deskripsi, aktivitas, dan efek berbeda
    """
    
    # Database lengkap lokasi dengan deskripsi detail
    LOCATIONS = {
        LocationType.LIVING_ROOM: {
            "name": "ruang tamu",
            "emoji": "🛋️",
            "description": (
                "Ruang tamu yang hangat dengan sofa empuk berwarna krem. "
                "Ada TV 50 inci di dinding, rak buku penuh novel, dan "
                "tanaman hias di sudut ruangan. Lampu temaram membuat "
                "suasana jadi cozy banget buat ngobrol santai."
            ),
            "activities": [
                "nonton TV sambil nyemil", 
                "baca buku di sofa", 
                "rebahan sambil dengerin musik",
                "main game di PS",
                "ngobrol santai sambil minum teh"
            ],
            "clothing_style": "casual",
            "mood_effects": ["ceria", "rileks", "malas"],
            "intimacy_allowed": False,
            "sound": "suara TV dari kejauhan",
            "scent": "wangi pewangi ruangan vanilla",
            "objects": ["sofa empuk", "bantal guling", "remote TV", "majalah"]
        },
        
        LocationType.BEDROOM: {
            "name": "kamar tidur",
            "emoji": "🛏️",
            "description": (
                "Kamar tidur pribadi dengan ranjang ukuran queen yang dilengkapi "
                "sprei motif bunga dan banyak bantal empuk. Ada lampu tidur "
                "dengan cahaya redup, lemari pakaian, dan meja rias dengan "
                "cermin besar. Di pojok kamar ada kursi malas buat santai."
            ),
            "activities": [
                "rebahan di ranjang", 
                "ganti baju", 
                "bercermin",
                "tidur siang",
                "bermalas-malasan"
            ],
            "clothing_style": "sexy",
            "mood_effects": ["romantis", "horny", "rindu", "malas"],
            "intimacy_allowed": True,
            "sound": "suara jam dinding tik-tok",
            "scent": "wangi parfum vanilla dari lemari",
            "objects": ["ranjang empuk", "bantal guling", "selimut tipis", "cermin"]
        },
        
        LocationType.KITCHEN: {
            "name": "dapur",
            "emoji": "🍳",
            "description": (
                "Dapur bersih dengan kitchen set minimalis. Ada kompor gas 4 tungku, "
                "kulkas 2 pintu, dan rak bumbu yang tertata rapi. Meja dapur "
                "marmer putih cocok buat tempat masak bareng. Wangi masakan "
                "selalu menggoda di sini."
            ),
            "activities": [
                "masak", 
                "makan", 
                "minum kopi",
                "cuci piring",
                "nyemil"
            ],
            "clothing_style": "casual",
            "mood_effects": ["ceria", "lapar", "bersemangat"],
            "intimacy_allowed": False,
            "sound": "suara air mengalir dan kompor",
            "scent": "aroma masakan dan kopi",
            "objects": ["kompor", "kulkas", "panci", "gelas", "piring"]
        },
        
        LocationType.BATHROOM: {
            "name": "kamar mandi",
            "emoji": "🚿",
            "description": (
                "Kamar mandi dengan ubin putih bersih. Ada shower air panas, "
                "bathtub buat berendam, dan wastafel dengan cermin besar. "
                "Handuk bersih tergantung rapi. Uap air membuat suasana "
                "jadi hangat dan rileks."
            ),
            "activities": [
                "mandi", 
                "keramas", 
                "berendam",
                "bercermin",
                "gosok gigi"
            ],
            "clothing_style": "towel",
            "mood_effects": ["rileks", "sendiri", "segar"],
            "intimacy_allowed": False,
            "sound": "suara air mengalir",
            "scent": "wangi sabun dan shampoo",
            "objects": ["shower", "bathtub", "handuk", "sikat gigi"]
        },
        
        LocationType.BALCONY: {
            "name": "balkon",
            "emoji": "🌆",
            "description": (
                "Balkon mungil dengan pemandangan kota. Ada kursi malas dan "
                "meja kecil tempat minum kopi. Tanaman hias dalam pot "
                "membuat suasana asri. Angin sepoi-sepoi bikin betah "
                "lama-lama di sini."
            ),
            "activities": [
                "lihat pemandangan", 
                "minum kopi", 
                "melamun",
                "vaping",
                "foto-foto"
            ],
            "clothing_style": "casual",
            "mood_effects": ["romantis", "rindu", "galau", "tenang"],
            "intimacy_allowed": True,
            "sound": "suara kendaraan dari kejauhan",
            "scent": "wangi bunga dan udara segar",
            "objects": ["kursi malas", "meja kecil", "tanaman pot"]
        },
        
        LocationType.TERRACE: {
            "name": "teras",
            "emoji": "🏡",
            "description": (
                "Teras depan dengan kursi kayu panjang. Ada tanaman rambat "
                "yang merambat di pagar. Bisa lihat tetangga lewat dan "
                "anak-anak main sepak bola. Tempat yang adem buat santai sore."
            ),
            "activities": [
                "duduk santai", 
                "baca koran", 
                "lihat orang lewat",
                "minum teh sore"
            ],
            "clothing_style": "casual",
            "mood_effects": ["ceria", "rileks", "ingin tahu"],
            "intimacy_allowed": False,
            "sound": "suara anak-anak bermain",
            "scent": "wangi tanah dan bunga",
            "objects": ["kursi kayu", "meja teras", "tanaman"]
        },
        
        LocationType.GARDEN: {
            "name": "taman",
            "emoji": "🌺",
            "description": (
                "Taman belakang dengan rumput hijau dan berbagai bunga warna-warni. "
                "Ada pohon mangga rindang dan ayunan kayu. Suara burung "
                "berkicau bikin suasana adem. Tempat yang romantis buat "
                "jalan-jalan sore."
            ),
            "activities": [
                "siram tanaman", 
                "jalan-jalan", 
                "duduk di rumput",
                "baca buku",
                "ayunan"
            ],
            "clothing_style": "casual",
            "mood_effects": ["ceria", "bersemangat", "romantis"],
            "intimacy_allowed": True,
            "sound": "suara burung dan angin",
            "scent": "wangi bunga dan tanah basah",
            "objects": ["ayunan", "bangku taman", "tanaman bunga"]
        }
    }
    
    def __init__(self):
        self.current_location = LocationType.LIVING_ROOM
        self.last_move_time = time.time()
        self.location_since = time.time()
        self.move_cooldown = 60  # minimal 1 menit di satu lokasi
        self.visited_locations = []  # history lokasi
        
        logger.info("✅ LocationSystem initialized with 7 locations")
    
    def get_current(self) -> LocationType:
        """Dapatkan lokasi saat ini"""
        return self.current_location
    
    def get_current_info(self) -> Dict:
        """Dapatkan info lengkap lokasi saat ini"""
        info = self.LOCATIONS.get(self.current_location, self.LOCATIONS[LocationType.LIVING_ROOM])
        return {
            "location": self.current_location,
            "name": info["name"],
            "emoji": info["emoji"],
            "description": info["description"],
            "activities": info["activities"],
            "clothing_style": info["clothing_style"],
            "mood_effects": info["mood_effects"],
            "intimacy_allowed": info["intimacy_allowed"],
            "time_here": self.get_time_here(),
            "objects": info["objects"]
        }
    
    def get_time_here(self) -> int:
        """Dapatkan durasi di lokasi saat ini (detik)"""
        return int(time.time() - self.location_since)
    
    def get_time_here_str(self) -> str:
        """Dapatkan durasi dalam format string"""
        seconds = self.get_time_here()
        if seconds < 60:
            return f"{seconds} detik"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes} menit"
        else:
            hours = seconds // 3600
            return f"{hours} jam"
    
    def can_move(self) -> bool:
        """Cek apakah boleh pindah lokasi"""
        return self.get_time_here() >= self.move_cooldown
    
    def move_to(self, new_location: LocationType) -> bool:
        """
        Pindah ke lokasi baru
        
        Returns:
            sukses atau tidak
        """
        if not self.can_move():
            logger.debug(f"Cannot move, cooldown: {self.get_time_here()} < {self.move_cooldown}")
            return False
        
        if new_location == self.current_location:
            return False
        
        # Catat lokasi sebelumnya
        old_info = self.LOCATIONS.get(self.current_location)
        
        self.visited_locations.append({
            "location": self.current_location,
            "name": old_info["name"],
            "duration": self.get_time_here(),
            "timestamp": self.location_since
        })
        
        # Pindah ke lokasi baru
        self.current_location = new_location
        self.last_move_time = time.time()
        self.location_since = time.time()
        
        logger.info(f"📍 Moved from {old_info['name']} to {self.LOCATIONS[new_location]['name']}")
        return True
    
    def move_random(self, force: bool = False) -> Tuple[bool, Optional[LocationType]]:
        """
        Pindah ke lokasi random
        
        Args:
            force: paksa pindah (abaikan cooldown)
            
        Returns:
            (sukses, lokasi_baru)
        """
        if not force and not self.can_move():
            return False, None
        
        # Pilih lokasi random selain yang sekarang
        available = [loc for loc in LocationType if loc != self.current_location]
        new_loc = random.choice(available)
        
        success = self.move_to(new_loc)
        return success, new_loc if success else None
    
    def get_move_message(self, new_location: LocationType) -> str:
        """
        Dapatkan pesan saat pindah lokasi
        """
        info = self.LOCATIONS.get(new_location, self.LOCATIONS[LocationType.LIVING_ROOM])
        old_info = self.LOCATIONS.get(self.current_location, self.LOCATIONS[LocationType.LIVING_ROOM])
        
        messages = [
            f"*pindah ke {info['name']}* {info['emoji']}\n\n"
            f"Aku masuk ke {info['name']}. {info['description']} "
            f"Wangi {info['scent']} langsung tercium. {info['sound']} terdengar pelan. "
            f"Ada {random.choice(info['objects'])} di dekatku. Nyaman banget di sini...",
            
            f"*jalan menuju {info['name']}*\n\n"
            f"Aku ninggalin {old_info['name']} yang tadi. Sekarang aku di {info['name']}. "
            f"{info['description']} Suasana berubah total. {info['scent']} bikin rileks. "
            f"Cocok banget buat ngobrol lama-lama.",
            
            f"*masuk ke {info['name']}*\n\n"
            f"Pintu terbuka... aku masuk ke {info['name']}. "
            f"{info['description'][:200]}... Aku duduk di sini bentar ya, "
            f"nikmatin suasananya. {info['sound']} bikin adem."
        ]
        
        return random.choice(messages)
    
    def get_activity_description(self) -> str:
        """
        Dapatkan deskripsi aktivitas di lokasi saat ini
        """
        info = self.get_current_info()
        activity = random.choice(info["activities"])
        
        return f"Aku lagi {activity} nih. Asyik banget..."
    
    def get_location_context(self) -> str:
        """
        Dapatkan konteks lokasi untuk prompt AI
        """
        info = self.get_current_info()
        
        return (
            f"📍 **Lokasi: {info['emoji']} {info['name']}**\n"
            f"{info['description']}\n\n"
            f"Aktivitas saat ini: {random.choice(info['activities'])}\n"
            f"Sudah di sini selama: {self.get_time_here_str()}\n"
            f"Suasana: {info['sound']}, wangi {info['scent']}\n"
            f"Ada {random.choice(info['objects'])} di dekatku."
        )
    
    def get_visited_history(self, limit: int = 5) -> List[str]:
        """Dapatkan history lokasi yang pernah dikunjungi"""
        history = []
        for visit in self.visited_locations[-limit:]:
            minutes = visit['duration'] // 60
            history.append(f"• {visit['name']} ({minutes} menit)")
        return history
    
    def reset(self):
        """Reset ke lokasi awal"""
        self.current_location = LocationType.LIVING_ROOM
        self.last_move_time = time.time()
        self.location_since = time.time()
        self.visited_locations = []
        logger.info("Location system reset")


__all__ = ['LocationSystem', 'LocationType']
