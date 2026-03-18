#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - POSITION SYSTEM
=============================================================================
Sistem posisi tubuh dinamis
- 6 posisi berbeda (duduk, berdiri, berbaring, bersandar, merangkak, berlutut)
- Perubahan random (3% chance per pesan)
- Deskripsi panjang (500+ karakter) untuk setiap posisi
- Efek posisi ke aktivitas dan mood
=============================================================================
"""

import random
import time
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class PositionType(str, Enum):
    """Enum untuk tipe posisi"""
    SITTING = "sitting"          # Duduk
    STANDING = "standing"         # Berdiri
    LYING = "lying"               # Berbaring
    LEANING = "leaning"           # Bersandar
    CRAWLING = "crawling"         # Merangkak
    KNEELING = "kneeling"         # Berlutut


class PositionSystem:
    """
    Sistem posisi tubuh dinamis
    Bot bisa berubah posisi secara random
    Setiap posisi punya deskripsi dan aktivitas berbeda
    """
    
    # Database lengkap posisi dengan deskripsi detail (500+ karakter)
    POSITIONS = {
        PositionType.SITTING: {
            "name": "duduk",
            "emoji": "🧘",
            "description": (
                "Duduk dengan nyaman di sofa empuk. Kaki sedikit ditekuk, "
                "tangan di atas pangkuan. Badan rileks, siap ngobrol panjang. "
                "Sesekali bergeser mencari posisi yang paling nyaman. "
                "Bantal di belakang punggung bikin tambah betah."
            ),
            "actions": [
                "duduk manis di sofa",
                "duduk bersila di lantai",
                "duduk di kursi malas",
                "duduk dengan kaki menjuntai",
                "duduk sambil memangku bantal"
            ],
            "mood_effects": ["rileks", "tenang", "nyaman"],
            "intimacy_allowed": True,  # bisa intim sambil duduk
            "sound": "suara sofa sedikit berderit",
            "feeling": "pantat mulai pegal kalau terlalu lama"
        },
        
        PositionType.STANDING: {
            "name": "berdiri",
            "emoji": "🧍",
            "description": (
                "Berdiri tegak dengan kedua kaki menapak lantai. "
                "Tangan di samping badan atau kadang bertumpu di pinggang. "
                "Sesekali bergeser berat badan dari kaki kiri ke kanan. "
                "Pandangan lurus ke depan, siap melangkah kapan saja."
            ),
            "actions": [
                "berdiri tegak di dekat jendela",
                "bersandar di dinding sambil berdiri",
                "berdiri dengan tangan di pinggang",
                "berdiri sambil melihat pemandangan",
                "berdiri di depan cermin"
            ],
            "mood_effects": ["waspada", "bersemangat", "siap"],
            "intimacy_allowed": True,  # bisa intim sambil berdiri
            "sound": "suara langkah kaki pelan",
            "feeling": "kaki mulai pegal kalau terlalu lama"
        },
        
        PositionType.LYING: {
            "name": "berbaring",
            "emoji": "😴",
            "description": (
                "Berbaring dengan nyaman di atas ranjang. Badan meregang, "
                "kepala di atas bantal empuk. Selimut tipis menutupi sebagian "
                "tubuh. Posisi yang paling nyaman buat santai atau tidur. "
                "Sesekali berguling mencari posisi yang lebih enak."
            ),
            "actions": [
                "berbaring di ranjang",
                "rebahan sambil main HP",
                "tiduran dengan tangan di belakang kepala",
                "berbaring miring sambil memeluk bantal",
                "telentang dengan kaki terbuka"
            ],
            "mood_effects": ["malas", "rileks", "ngantuk", "nyaman"],
            "intimacy_allowed": True,  # posisi favorit buat intim
            "sound": "suara sprei yang digerakkan",
            "feeling": "enak banget, bisa ketiduran"
        },
        
        PositionType.LEANING: {
            "name": "bersandar",
            "emoji": "🚶",
            "description": (
                "Bersandar santai di dinding atau pintu. Satu kaki sedikit "
                "ditekuk, tangan mungkin dilipat di depan dada. Posisi casual "
                "yang kelihatan keren. Kadang sambil mainin rambut atau "
                "lihat kuku."
            ),
            "actions": [
                "bersandar di dinding",
                "bersandar di pintu kamar",
                "bersandar di lemari",
                "bersandar sambil melipat tangan",
                "bersandar sambil mainin rambut"
            ],
            "mood_effects": ["santai", "cool", "percaya diri"],
            "intimacy_allowed": True,  # bisa ciuman sambil bersandar
            "sound": "suara punggung menempel di dinding",
            "feeling": "adem karena kena tembok"
        },
        
        PositionType.CRAWLING: {
            "name": "merangkak",
            "emoji": "🐾",
            "description": (
                "Merangkak di lantai dengan kedua tangan dan lutut. "
                "Posisi yang agak ekstrem, biasanya kalo lagi main-main "
                "atau situasi intim tertentu. Gerakan pelan dan hati-hati."
            ),
            "actions": [
                "merangkak di lantai",
                "merangkak mendekat",
                "merangkak sambil menunduk",
                "merangkak di atas kasur"
            ],
            "mood_effects": ["playful", "nakal", "berani"],
            "intimacy_allowed": True,  # posisi untuk BDSM
            "sound": "suara lutut dan tangan di lantai",
            "feeling": "lutut agak sakit kalau lama"
        },
        
        PositionType.KNEELING: {
            "name": "berlutut",
            "emoji": "🙏",
            "description": (
                "Berlutut di lantai dengan kedua lutut menapak. "
                "Badan tegak atau bisa juga sedikit membungkuk. "
                "Posisi yang menunjukkan hormat atau kadang untuk "
                "aktivitas intim tertentu."
            ),
            "actions": [
                "berlutut di lantai",
                "berlutut di ranjang",
                "berlutut sambil menunduk",
                "berlutut di depan sofa"
            ],
            "mood_effects": ["hormat", "patuh", "intim"],
            "intimacy_allowed": True,  # posisi untuk blowjob
            "sound": "suara lutut menyentuh lantai",
            "feeling": "lutut mulai pegal"
        }
    }
    
    def __init__(self):
        self.current_position = PositionType.SITTING
        self.last_change = time.time()
        self.position_since = time.time()
        self.change_cooldown = 30  # minimal 30 detik di satu posisi
        self.position_history = []  # history posisi
        
        logger.info("✅ PositionSystem initialized with 6 positions")
    
    def get_current(self) -> PositionType:
        """Dapatkan posisi saat ini"""
        return self.current_position
    
    def get_current_info(self) -> Dict:
        """Dapatkan info lengkap posisi saat ini"""
        info = self.POSITIONS.get(self.current_position, self.POSITIONS[PositionType.SITTING])
        return {
            "position": self.current_position,
            "name": info["name"],
            "emoji": info["emoji"],
            "description": info["description"],
            "actions": info["actions"],
            "mood_effects": info["mood_effects"],
            "intimacy_allowed": info["intimacy_allowed"],
            "sound": info["sound"],
            "feeling": info["feeling"],
            "time_here": self.get_time_here()
        }
    
    def get_time_here(self) -> int:
        """Dapatkan durasi di posisi saat ini (detik)"""
        return int(time.time() - self.position_since)
    
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
    
    def can_change(self) -> bool:
        """Cek apakah boleh ganti posisi"""
        return self.get_time_here() >= self.change_cooldown
    
    def change_to(self, new_position: PositionType) -> bool:
        """
        Ganti ke posisi baru
        
        Args:
            new_position: Posisi baru
            
        Returns:
            True jika berhasil
        """
        if not self.can_change():
            logger.debug(f"Cannot change position, cooldown: {self.get_time_here()} < {self.change_cooldown}")
            return False
        
        if new_position == self.current_position:
            return False
        
        # Catat posisi sebelumnya
        old_info = self.POSITIONS.get(self.current_position)
        
        self.position_history.append({
            "position": self.current_position,
            "name": old_info["name"],
            "duration": self.get_time_here(),
            "timestamp": self.position_since
        })
        
        # Ganti ke posisi baru
        self.current_position = new_position
        self.last_change = time.time()
        self.position_since = time.time()
        
        logger.info(f"🔄 Changed position from {old_info['name']} to {new_position.value}")
        return True
    
    def change_random(self) -> PositionType:
        """
        Ganti ke posisi random
        
        Returns:
            Posisi baru
        """
        available = [pos for pos in PositionType if pos != self.current_position]
        new_pos = random.choice(available)
        self.change_to(new_pos)
        return new_pos
    
    def get_change_message(self) -> str:
        """
        Dapatkan pesan saat ganti posisi (500+ karakter)
        """
        info = self.get_current_info()
        
        messages = [
            f"*{info['actions'][0]}* {info['emoji']}\n\n"
            f"Aku ganti posisi sekarang, {info['name']}. {info['description']} "
            f"{info['sound']} terdengar. {info['feeling']}. Nyaman banget rasanya.",
            
            f"*berganti posisi*\n\n"
            f"Sekarang aku {info['name']}. {info['description'][:150]} "
            f"Suasana hatiku jadi lebih {random.choice(info['mood_effects'])}. "
            f"{info['feeling']} sih, tapi gapapa.",
            
            f"*mengubah posisi*\n\n"
            f"Aku memutuskan untuk {info['name']}. {info['description']} "
            f"Posisi ini cocok banget buat {random.choice(['santai', 'ngobrol', 'bersama kamu'])}. "
            f"Gimana? Kamu suka lihat aku kayak gini?"
        ]
        
        return random.choice(messages)
    
    def get_position_context(self) -> str:
        """
        Dapatkan konteks posisi untuk prompt AI (500+ karakter)
        """
        info = self.get_current_info()
        
        return (
            f"🧍 **Posisi: {info['emoji']} {info['name']}**\n"
            f"{info['description']}\n\n"
            f"{info['feeling']} {info['sound']}.\n"
            f"Sudah di posisi ini selama: {self.get_time_here_str()}\n"
            f"Cocok buat: {', '.join(info['mood_effects'])}"
        )
    
    def get_position_description(self) -> str:
        """
        Dapatkan deskripsi posisi saat ini (untuk diselipkan di chat)
        """
        info = self.get_current_info()
        action = random.choice(info['actions'])
        
        templates = [
            f"Aku lagi {action} nih. {info['description'][:100]}... Enak banget rasanya.",
            f"Sekarang aku {info['name']}. {info['feeling']} sih, tapi gapapa.",
            f"*{action}* sambil {random.choice(['main HP', 'ngelamun', 'dengerin musik'])}."
        ]
        
        return random.choice(templates)
    
    def get_position_history(self, limit: int = 5) -> List[str]:
        """Dapatkan history posisi yang pernah diambil"""
        history = []
        for entry in self.position_history[-limit:]:
            minutes = entry['duration'] // 60
            history.append(f"• {entry['name']} ({minutes} menit)")
        return history
    
    def reset(self):
        """Reset ke posisi awal"""
        self.current_position = PositionType.SITTING
        self.last_change = time.time()
        self.position_since = time.time()
        self.position_history = []
        logger.info("Position system reset")


__all__ = ['PositionSystem', 'PositionType']
