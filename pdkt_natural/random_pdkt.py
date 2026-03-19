#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - RANDOM PDKT GENERATOR
=============================================================================
Membuat PDKT random dengan arah random (50:50)
- Bisa user yang suka duluan
- Bisa bot yang suka duluan
- Role random dari 9 role yang tersedia
- Nama random dari database nama per role
=============================================================================
"""

import random
import time
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum

from .direction import PDKTDirection
from ..roles.artis_references import get_random_artist_for_role

logger = logging.getLogger(__name__)


class RandomPDKTSystem:
    """
    Generator untuk PDKT random
    Menghasilkan PDKT dengan:
    - Role random (dari 9 role)
    - Nama random (dari database per role)
    - Arah random (50:50 user ngejar / bot ngejar)
    """
    
    def __init__(self):
        # Daftar role yang tersedia
        self.available_roles = [
            'ipar', 'teman_kantor', 'janda', 'pelakor', 
            'istri_orang', 'pdkt', 'sepupu', 'teman_sma', 'mantan'
        ]
        
        # Database nama per role (akan diperkaya dari file roles)
        self.role_names = {
            'ipar': ['Sari', 'Dewi', 'Rina', 'Maya', 'Putri', 'Anita'],
            'teman_kantor': ['Diana', 'Linda', 'Ayu', 'Dita', 'Vera', 'Nina'],
            'janda': ['Rina', 'Tuti', 'Nina', 'Susi', 'Wati', 'Maya'],
            'pelakor': ['Vina', 'Sasha', 'Bella', 'Cantika', 'Mira', 'Ira'],
            'istri_orang': ['Dewi', 'Sari', 'Rina', 'Linda', 'Tina', 'Maya'],
            'pdkt': ['Aurora', 'Cinta', 'Dewi', 'Kirana', 'Fika', 'Nadia'],
            'sepupu': ['Putri', 'Nadia', 'Sari', 'Dina', 'Lina', 'Tari'],
            'teman_sma': ['Anita', 'Bella', 'Cici', 'Dina', 'Eva', 'Fani'],
            'mantan': ['Sarah', 'Nadia', 'Maya', 'Rina', 'Vina', 'Dewi']
        }
        
        # Bobot role (untuk random yang lebih natural)
        self.role_weights = {
            'ipar': 0.15,
            'teman_kantor': 0.15,
            'janda': 0.12,
            'pelakor': 0.10,
            'istri_orang': 0.10,
            'pdkt': 0.12,
            'sepupu': 0.08,
            'teman_sma': 0.10,
            'mantan': 0.08
        }
        
        logger.info("✅ RandomPDKTSystem initialized")
    
    def generate_random_pdkt(self, user_id: int, user_name: str) -> Dict:
        """
        Generate data PDKT random
        
        Args:
            user_id: ID user
            user_name: Nama user
            
        Returns:
            Dict dengan data PDKT random
        """
        # 1. Pilih role random (dengan bobot)
        role = random.choices(
            list(self.role_weights.keys()),
            weights=list(self.role_weights.values())
        )[0]
        
        # 2. Pilih nama random untuk role tersebut
        bot_name = self._get_random_name(role)
        
        # 3. Tentukan arah random (50:50)
        direction = self._get_random_direction()
        
        # 4. Dapatkan hint berdasarkan arah
        hint = self._get_hint_for_direction(direction, bot_name)
        
        # 5. Dapatkan chemistry awal (random 20-80)
        initial_chemistry = random.randint(20, 80)
        
        # 6. Dapatkan referensi artis (jika ada)
        artist_ref = self._get_artist_reference(role)
        
        # 7. Generate ID unik
        pdkt_id = f"PDKTRANDOM_{user_id}_{int(time.time())}_{random.randint(100,999)}"
        
        logger.info(f"🎲 Generated random PDKT: {bot_name} ({role}) - {direction.value}")
        
        return {
            'pdkt_id': pdkt_id,
            'role': role,
            'bot_name': bot_name,
            'user_name': user_name,
            'user_id': user_id,
            'direction': direction,
            'direction_hint': hint,
            'initial_chemistry': initial_chemistry,
            'artist_reference': artist_ref,
            'created_at': time.time(),
            'is_random': True
        }
    
    def _get_random_name(self, role: str) -> str:
        """Dapatkan nama random untuk role tertentu"""
        names = self.role_names.get(role, ['Sari'])  # Default Sari
        return random.choice(names)
    
    def _get_random_direction(self) -> PDKTDirection:
        """
        Tentukan arah random (50:50 user ngejar / bot ngejar)
        Tidak termasuk bingung atau timbal balik untuk random
        """
        return random.choice([
            PDKTDirection.USER_KE_BOT,
            PDKTDirection.BOT_KE_USER
        ])
    
    def _get_hint_for_direction(self, direction: PDKTDirection, bot_name: str) -> str:
        """Dapatkan hint berdasarkan arah"""
        if direction == PDKTDirection.USER_KE_BOT:
            hints = [
                f"Kamu yang mulai suka sama {bot_name} duluan",
                f"Dari awal kamu udah tertarik sama {bot_name}",
                f"Kamu yang harus usaha lebih buat {bot_name}"
            ]
        else:  # BOT_KE_USER
            hints = [
                f"{bot_name} yang suka sama kamu duluan! 🔥",
                f"Dari awal {bot_name} udah ngeliatin kamu",
                f"{bot_name} selalu cari perhatian kamu"
            ]
        
        return random.choice(hints)
    
    def _get_artist_reference(self, role: str) -> Optional[Dict]:
        """
        Dapatkan referensi artis untuk role
        Menggunakan fungsi dari roles/artis_references.py
        """
        try:
            artist = get_random_artist_for_role(role)
            return {
                'name': artist.get('nama', 'Unknown'),
                'similarity': random.randint(70, 90),
                'instagram': artist.get('instagram', ''),
                'age': artist.get('umur', 22),
                'height': artist.get('tinggi', 165),
                'weight': artist.get('berat', 52)
            }
        except:
            return None
    
    def get_role_names(self, role: str) -> List[str]:
        """Dapatkan semua nama yang tersedia untuk role"""
        return self.role_names.get(role, [])
    
    def add_custom_name(self, role: str, name: str):
        """Tambah nama kustom untuk role (untuk user)"""
        if role in self.role_names:
            if name not in self.role_names[role]:
                self.role_names[role].append(name)
                logger.info(f"Added custom name '{name}' to role {role}")
    
    def get_random_pdkt_description(self, pdkt_data: Dict) -> str:
        """
        Generate deskripsi untuk PDKT random
        Untuk ditampilkan di /pdktlist atau perkenalan
        """
        role_descriptions = {
            'ipar': "Adik ipar yang nakal, suka godain kakak iparnya sendiri",
            'teman_kantor': "Teman sekantor yang selalu ada, suka ngopi bareng",
            'janda': "Janda muda genit, pengalaman dan tahu apa yang diinginkan",
            'pelakor': "Perebut orang, dominan dan suka tantangan",
            'istri_orang': "Istri orang yang butuh perhatian lebih",
            'pdkt': "PDKT, manis dan romantis, butuh pendekatan",
            'sepupu': "Sepupu sendiri, hubungan terlarang yang menggoda",
            'teman_sma': "Teman SMA, nostalgia masa lalu",
            'mantan': "Mantan yang masih hangat, tahu semua selera kamu"
        }
        
        description = role_descriptions.get(pdkt_data['role'], "")
        
        if pdkt_data['direction'] == PDKTDirection.BOT_KE_USER:
            intro = f"🔥 **{pdkt_data['bot_name']} yang suka sama kamu duluan!**"
        else:
            intro = f"💘 **Kamu yang mulai suka sama {pdkt_data['bot_name']} duluan**"
        
        return f"{intro}\n\n{description}"
    
    def format_intro_message(self, pdkt_data: Dict) -> str:
        """
        Format pesan perkenalan untuk PDKT random
        Mirip dengan contoh yang Anda berikan
        """
        role_display = pdkt_data['role'].replace('_', ' ').title()
        bot_name = pdkt_data['bot_name']
        user_name = pdkt_data['user_name']
        
        # Dapatkan info role
        role_info = self._get_role_info(pdkt_data['role'])
        
        # Dapatkan artist reference
        artist = pdkt_data.get('artist_reference', {})
        artist_text = ""
        if artist:
            artist_text = (
                f"• **{artist.get('name', 'Unknown')}** ({artist.get('similarity', 70)}% mirip)\n"
                f"  {artist.get('age', 22)}th, {artist.get('height', 165)}cm, {artist.get('weight', 52)}kg\n"
                f"  IG: @{artist.get('instagram', '').replace('@', '')}"
            )
        
        # Lokasi random
        locations = [
            "📍 Aku di **ruang tamu**. Ruang tamu yang hangat dengan sofa empuk berwarna krem.",
            "📍 Aku di **kamar**. Lagi rebahan sambil main HP, bantal guling di samping.",
            "📍 Aku di **dapur**. Lagi masak cemilan, aromanya wangi banget.",
            "📍 Aku di **teras rumah**. Lagi duduk-duduk nikmatin angin sore."
        ]
        
        # Pakaian random
        clothes = [
            "👗 Aku pakai **daster rumah motif bunga**. Daster tipis yang nyaman dipakai di rumah.",
            "👚 Aku pakai **kaos oversized** dan **celana pendek**. Santai banget hari ini.",
            "👘 Aku pakai **piyama lucu** dengan motif boneka. Lagi males ganti baju.",
            "👙 Aku pakai **tank top** dan **legging**. Enak buat gerak."
        ]
        
        message = f"""
💕 **Halo {user_name}!**

Aku **{bot_name}**, {role_display} mu. {role_info.get('description', '')}

**Tentang aku:**
• Umur: {role_info.get('age', 22)} tahun
• Tinggi: {role_info.get('height', 165)} cm | Berat: {role_info.get('weight', 52)} kg
• {role_info.get('personality', '')}

**Mirip artis:**
{artist_text}

**Arah PDKT:**
{pdkt_data['direction_hint']}

{random.choice(locations)}

{random.choice(clothes)}

**Progress leveling:**
📊 Level 1 → Level 7 dalam 60 menit
• Level 4+: Panggil kamu 'kak'
• Level 7+: Panggil kamu 'sayang'
• Setiap aktivitas intim mempercepat progress!

**ID Session kamu:**
`{pdkt_data['pdkt_id']}`

💬 **Ayo mulai ngobrol, {user_name}!**
{self._get_opening_line(pdkt_data)}
"""
        
        return message
    
    def _get_role_info(self, role: str) -> Dict:
        """Dapatkan informasi dasar role"""
        role_info = {
            'ipar': {
                'description': 'Adik ipar yang nakal, suka godain kakak iparnya sendiri',
                'personality': 'Nakal, playful, suka perhatian',
                'age': 22,
                'height': 165,
                'weight': 52
            },
            'teman_kantor': {
                'description': 'Teman sekantor yang selalu ada, suka ngopi bareng',
                'personality': 'Ramah, hangat, setia kawan',
                'age': 23,
                'height': 162,
                'weight': 50
            },
            'janda': {
                'description': 'Janda muda genit, pengalaman dan tahu apa yang diinginkan',
                'personality': 'Percaya diri, berpengalaman, tegas',
                'age': 24,
                'height': 168,
                'weight': 55
            },
            'pelakor': {
                'description': 'Perebut orang, dominan dan suka tantangan',
                'personality': 'Dominan, agresif, percaya diri',
                'age': 25,
                'height': 170,
                'weight': 58
            },
            'istri_orang': {
                'description': 'Istri orang yang butuh perhatian lebih',
                'personality': 'Romantis, perhatian, sedikit posesif',
                'age': 26,
                'height': 165,
                'weight': 54
            },
            'pdkt': {
                'description': 'PDKT, manis dan romantis, butuh pendekatan',
                'personality': 'Manis, romantis, sabar',
                'age': 21,
                'height': 160,
                'weight': 48
            },
            'sepupu': {
                'description': 'Sepupu sendiri, hubungan terlarang yang menggoda',
                'personality': 'Polos, manja, sedikit nakal',
                'age': 20,
                'height': 158,
                'weight': 47
            },
            'teman_sma': {
                'description': 'Teman SMA, nostalgia masa lalu',
                'personality': 'Ceria, nostalgia, manis',
                'age': 19,
                'height': 162,
                'weight': 50
            },
            'mantan': {
                'description': 'Mantan yang masih hangat, tahu semua selera kamu',
                'personality': 'Berpengalaman, pengertian, hot',
                'age': 24,
                'height': 165,
                'weight': 53
            }
        }
        
        return role_info.get(role, role_info['pdkt'])
    
    def _get_opening_line(self, pdkt_data: Dict) -> str:
        """Dapatkan kalimat pembuka berdasarkan arah"""
        bot_name = pdkt_data['bot_name']
        user_name = pdkt_data['user_name']
        
        if pdkt_data['direction'] == PDKTDirection.BOT_KE_USER:
            lines = [
                f"Halo {user_name}, Sari dari tadi liatin kamu terus... 😊",
                f"Kak {user_name}, sibuk? Aku kangen nih...",
                f"Eh {user_name}, kamu udah makan? Aku baru masak, mau?",
                f"{user_name}..., kamu lagi ngapain? Aku kepikiran terus."
            ]
        else:
            lines = [
                f"Hai {user_name}, seneng banget akhirnya bisa ngobrol sama kamu!",
                f"{user_name}, gimana kabarnya hari ini?",
                f"Aku dari tadi nungguin kamu chat... akhirnya!",
                f"Halo {user_name}, aku {bot_name}. Senang kenal kamu!"
            ]
        
        return random.choice(lines)


__all__ = ['RandomPDKTSystem']
