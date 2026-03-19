#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - NAME GENERATOR
=============================================================================
Membangkitkan nama permanent untuk bot
- Setiap role punya database nama sendiri
- Nama dipilih random saat pertama memulai
- Nama masuk ke UniqueID dan dipakai selamanya
=============================================================================
"""

import random
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class NameOrigin(str, Enum):
    """Asal-usul nama"""
    INDONESIAN = "indonesian"      # Nama Indonesia
    JAPANESE = "japanese"           # Nama Jepang
    KOREAN = "korean"                # Nama Korea
    WESTERN = "western"               # Nama Barat
    UNIQUE = "unique"                  # Nama unik/karakter


class NameGenerator:
    """
    Generator nama permanent untuk bot
    - Database nama per role
    - Bisa tambah nama kustom
    - Nama dipilih random dan disimpan selamanya
    """
    
    def __init__(self):
        # Database nama lengkap per role
        self.role_names = {
            # ===== ROLE IPAR =====
            'ipar': [
                # Nama Indonesia
                {'name': 'Sari', 'origin': NameOrigin.INDONESIAN, 'meaning': 'esensi/intisari'},
                {'name': 'Dewi', 'origin': NameOrigin.INDONESIAN, 'meaning': 'dewi'},
                {'name': 'Rina', 'origin': NameOrigin.INDONESIAN, 'meaning': 'cahaya'},
                {'name': 'Maya', 'origin': NameOrigin.INDONESIAN, 'meaning': 'ilusi/maya'},
                {'name': 'Putri', 'origin': NameOrigin.INDONESIAN, 'meaning': 'putri'},
                {'name': 'Anita', 'origin': NameOrigin.INDONESIAN, 'meaning': 'anugerah'},
                {'name': 'Lestari', 'origin': NameOrigin.INDONESIAN, 'meaning': 'abadi'},
                # Nama Jepang
                {'name': 'Yuki', 'origin': NameOrigin.JAPANESE, 'meaning': 'salju'},
                {'name': 'Hana', 'origin': NameOrigin.JAPANESE, 'meaning': 'bunga'},
                {'name': 'Sakura', 'origin': NameOrigin.JAPANESE, 'meaning': 'bunga sakura'},
                # Nama Korea
                {'name': 'Hana', 'origin': NameOrigin.KOREAN, 'meaning': 'satu'},
                {'name': 'Nara', 'origin': NameOrigin.KOREAN, 'meaning': 'negara'},
                {'name': 'Sora', 'origin': NameOrigin.KOREAN, 'meaning': 'langit'}
            ],
            
            # ===== ROLE TEMAN KANTOR =====
            'teman_kantor': [
                {'name': 'Diana', 'origin': NameOrigin.WESTERN, 'meaning': 'dewi bulan'},
                {'name': 'Linda', 'origin': NameOrigin.WESTERN, 'meaning': 'cantik'},
                {'name': 'Ayu', 'origin': NameOrigin.INDONESIAN, 'meaning': 'cantik'},
                {'name': 'Dita', 'origin': NameOrigin.INDONESIAN, 'meaning': 'anugerah'},
                {'name': 'Vera', 'origin': NameOrigin.WESTERN, 'meaning': 'kebenaran'},
                {'name': 'Nina', 'origin': NameOrigin.WESTERN, 'meaning': 'cahaya'},
                {'name': 'Tina', 'origin': NameOrigin.INDONESIAN, 'meaning': 'murni'},
                {'name': 'Rani', 'origin': NameOrigin.INDONESIAN, 'meaning': 'ratu'},
                {'name': 'Sarah', 'origin': NameOrigin.WESTERN, 'meaning': 'putri'},
                {'name': 'Michelle', 'origin': NameOrigin.WESTERN, 'meaning': 'siapa yang seperti Tuhan'}
            ],
            
            # ===== ROLE JANDA =====
            'janda': [
                {'name': 'Rina', 'origin': NameOrigin.INDONESIAN, 'meaning': 'cahaya'},
                {'name': 'Tuti', 'origin': NameOrigin.INDONESIAN, 'meaning': 'tulus'},
                {'name': 'Nina', 'origin': NameOrigin.WESTERN, 'meaning': 'cahaya'},
                {'name': 'Susi', 'origin': NameOrigin.INDONESIAN, 'meaning': 'bunga lili'},
                {'name': 'Wati', 'origin': NameOrigin.INDONESIAN, 'meaning': 'perempuan'},
                {'name': 'Maya', 'origin': NameOrigin.INDONESIAN, 'meaning': 'ilusi'},
                {'name': 'Ira', 'origin': NameOrigin.INDONESIAN, 'meaning': 'pengajar'},
                {'name': 'Vina', 'origin': NameOrigin.INDONESIAN, 'meaning': 'cinta'},
                {'name': 'Lina', 'origin': NameOrigin.INDONESIAN, 'meaning': 'cahaya'},
                {'name': 'Santi', 'origin': NameOrigin.INDONESIAN, 'meaning': 'damai'}
            ],
            
            # ===== ROLE PELAKOR =====
            'pelakor': [
                {'name': 'Vina', 'origin': NameOrigin.INDONESIAN, 'meaning': 'cinta'},
                {'name': 'Sasha', 'origin': NameOrigin.WESTERN, 'meaning': 'pembela'},
                {'name': 'Bella', 'origin': NameOrigin.WESTERN, 'meaning': 'cantik'},
                {'name': 'Cantika', 'origin': NameOrigin.INDONESIAN, 'meaning': 'cantik'},
                {'name': 'Mira', 'origin': NameOrigin.INDONESIAN, 'meaning': 'laut'},
                {'name': 'Ira', 'origin': NameOrigin.INDONESIAN, 'meaning': 'pengajar'},
                {'name': 'Gita', 'origin': NameOrigin.INDONESIAN, 'meaning': 'lagu'},
                {'name': 'Kiki', 'origin': NameOrigin.UNIQUE, 'meaning': 'kebahagiaan'},
                {'name': 'Lala', 'origin': NameOrigin.UNIQUE, 'meaning': 'bunga'},
                {'name': 'Sasa', 'origin': NameOrigin.UNIQUE, 'meaning': 'lili'}
            ],
            
            # ===== ROLE ISTRI ORANG =====
            'istri_orang': [
                {'name': 'Dewi', 'origin': NameOrigin.INDONESIAN, 'meaning': 'dewi'},
                {'name': 'Sari', 'origin': NameOrigin.INDONESIAN, 'meaning': 'esensi'},
                {'name': 'Rina', 'origin': NameOrigin.INDONESIAN, 'meaning': 'cahaya'},
                {'name': 'Linda', 'origin': NameOrigin.WESTERN, 'meaning': 'cantik'},
                {'name': 'Tina', 'origin': NameOrigin.INDONESIAN, 'meaning': 'murni'},
                {'name': 'Maya', 'origin': NameOrigin.INDONESIAN, 'meaning': 'ilusi'},
                {'name': 'Ani', 'origin': NameOrigin.INDONESIAN, 'meaning': 'anugerah'},
                {'name': 'Nita', 'origin': NameOrigin.INDONESIAN, 'meaning': 'berkat'},
                {'name': 'Rita', 'origin': NameOrigin.INDONESIAN, 'meaning': 'mutiara'},
                {'name': 'Susan', 'origin': NameOrigin.WESTERN, 'meaning': 'bunga lili'}
            ],
            
            # ===== ROLE PDKT =====
            'pdkt': [
                {'name': 'Aurora', 'origin': NameOrigin.WESTERN, 'meaning': 'fajar'},
                {'name': 'Cinta', 'origin': NameOrigin.INDONESIAN, 'meaning': 'cinta'},
                {'name': 'Dewi', 'origin': NameOrigin.INDONESIAN, 'meaning': 'dewi'},
                {'name': 'Kirana', 'origin': NameOrigin.INDONESIAN, 'meaning': 'cahaya'},
                {'name': 'Fika', 'origin': NameOrigin.INDONESIAN, 'meaning': 'cerdas'},
                {'name': 'Nadia', 'origin': NameOrigin.WESTERN, 'meaning': 'harapan'},
                {'name': 'Amara', 'origin': NameOrigin.UNIQUE, 'meaning': 'abadi'},
                {'name': 'Kayla', 'origin': NameOrigin.WESTERN, 'meaning': 'murni'},
                {'name': 'Zahra', 'origin': NameOrigin.WESTERN, 'meaning': 'bunga'},
                {'name': 'Alya', 'origin': NameOrigin.INDONESIAN, 'meaning': 'langit'}
            ],
            
            # ===== ROLE SEPUPU =====
            'sepupu': [
                {'name': 'Putri', 'origin': NameOrigin.INDONESIAN, 'meaning': 'putri'},
                {'name': 'Nadia', 'origin': NameOrigin.WESTERN, 'meaning': 'harapan'},
                {'name': 'Sari', 'origin': NameOrigin.INDONESIAN, 'meaning': 'esensi'},
                {'name': 'Dina', 'origin': NameOrigin.INDONESIAN, 'meaning': 'adil'},
                {'name': 'Lina', 'origin': NameOrigin.INDONESIAN, 'meaning': 'cahaya'},
                {'name': 'Tari', 'origin': NameOrigin.INDONESIAN, 'meaning': 'penari'},
                {'name': 'Nuri', 'origin': NameOrigin.INDONESIAN, 'meaning': 'burung'},
                {'name': 'Mila', 'origin': NameOrigin.INDONESIAN, 'meaning': 'cinta'},
                {'name': 'Dara', 'origin': NameOrigin.INDONESIAN, 'meaning': 'gadis'},
                {'name': 'Wulan', 'origin': NameOrigin.INDONESIAN, 'meaning': 'bulan'}
            ],
            
            # ===== ROLE TEMAN SMA =====
            'teman_sma': [
                {'name': 'Anita', 'origin': NameOrigin.INDONESIAN, 'meaning': 'anugerah'},
                {'name': 'Bella', 'origin': NameOrigin.WESTERN, 'meaning': 'cantik'},
                {'name': 'Cici', 'origin': NameOrigin.UNIQUE, 'meaning': 'kakak'},
                {'name': 'Dina', 'origin': NameOrigin.INDONESIAN, 'meaning': 'adil'},
                {'name': 'Eva', 'origin': NameOrigin.WESTERN, 'meaning': 'hidup'},
                {'name': 'Fani', 'origin': NameOrigin.INDONESIAN, 'meaning': 'bersinar'},
                {'name': 'Gita', 'origin': NameOrigin.INDONESIAN, 'meaning': 'lagu'},
                {'name': 'Hani', 'origin': NameOrigin.INDONESIAN, 'meaning': 'bahagia'},
                {'name': 'Indah', 'origin': NameOrigin.INDONESIAN, 'meaning': 'cantik'},
                {'name': 'Julia', 'origin': NameOrigin.WESTERN, 'meaning': 'muda'}
            ],
            
            # ===== ROLE MANTAN =====
            'mantan': [
                {'name': 'Sarah', 'origin': NameOrigin.WESTERN, 'meaning': 'putri'},
                {'name': 'Nadia', 'origin': NameOrigin.WESTERN, 'meaning': 'harapan'},
                {'name': 'Maya', 'origin': NameOrigin.INDONESIAN, 'meaning': 'ilusi'},
                {'name': 'Rina', 'origin': NameOrigin.INDONESIAN, 'meaning': 'cahaya'},
                {'name': 'Vina', 'origin': NameOrigin.INDONESIAN, 'meaning': 'cinta'},
                {'name': 'Dewi', 'origin': NameOrigin.INDONESIAN, 'meaning': 'dewi'},
                {'name': 'Linda', 'origin': NameOrigin.WESTERN, 'meaning': 'cantik'},
                {'name': 'Ayu', 'origin': NameOrigin.INDONESIAN, 'meaning': 'cantik'},
                {'name': 'Tina', 'origin': NameOrigin.INDONESIAN, 'meaning': 'murni'},
                {'name': 'Rani', 'origin': NameOrigin.INDONESIAN, 'meaning': 'ratu'}
            ]
        }
        
        # Nama-nama yang sudah dipakai (untuk menghindari duplikat dalam satu role)
        self.used_names = {}  # {user_id: {role: [names]}}
        
        logger.info("✅ NameGenerator initialized")
    
    def get_random_name(self, role: str, user_id: int = None) -> Dict:
        """
        Dapatkan nama random untuk role tertentu
        
        Args:
            role: Nama role
            user_id: ID user (untuk tracking nama yang sudah dipakai)
            
        Returns:
            Dict dengan data nama
        """
        if role not in self.role_names:
            role = 'pdkt'  # Default
        
        names = self.role_names[role]
        
        # Filter nama yang sudah dipakai user ini (jika ada user_id)
        if user_id:
            used = self.used_names.get(user_id, {}).get(role, [])
            available = [n for n in names if n['name'] not in used]
            
            if not available:
                # Semua nama sudah dipakai, reset (tapi kasih warning)
                logger.warning(f"All names for role {role} have been used. Recycling...")
                available = names
                # Hapus tracking untuk role ini
                if user_id in self.used_names and role in self.used_names[user_id]:
                    self.used_names[user_id][role] = []
        else:
            available = names
        
        selected = random.choice(available)
        
        # Tandai sebagai terpakai
        if user_id:
            if user_id not in self.used_names:
                self.used_names[user_id] = {}
            if role not in self.used_names[user_id]:
                self.used_names[user_id][role] = []
            
            self.used_names[user_id][role].append(selected['name'])
        
        return selected
    
    def get_name_by_index(self, role: str, index: int, user_id: int = None) -> Optional[Dict]:
        """
        Dapatkan nama berdasarkan index (untuk testing)
        
        Args:
            role: Nama role
            index: Index dalam list (0-based)
            user_id: ID user
            
        Returns:
            Data nama atau None
        """
        if role not in self.role_names:
            return None
        
        names = self.role_names[role]
        if 0 <= index < len(names):
            return names[index]
        
        return None
    
    def add_custom_name(self, role: str, name: str, meaning: str = "", 
                        origin: NameOrigin = NameOrigin.UNIQUE):
        """
        Tambah nama kustom untuk role
        
        Args:
            role: Nama role
            name: Nama yang ditambahkan
            meaning: Arti nama
            origin: Asal nama
        """
        if role not in self.role_names:
            self.role_names[role] = []
        
        # Cek duplikat
        for n in self.role_names[role]:
            if n['name'].lower() == name.lower():
                logger.warning(f"Name {name} already exists for role {role}")
                return
        
        self.role_names[role].append({
            'name': name,
            'origin': origin,
            'meaning': meaning
        })
        
        logger.info(f"Added custom name '{name}' to role {role}")
    
    def get_name_description(self, name_data: Dict) -> str:
        """
        Dapatkan deskripsi nama untuk perkenalan
        
        Args:
            name_data: Data nama dari get_random_name
            
        Returns:
            String deskripsi
        """
        name = name_data['name']
        meaning = name_data.get('meaning', '')
        origin = name_data.get('origin', NameOrigin.INDONESIAN)
        
        origin_text = {
            NameOrigin.INDONESIAN: "nama Indonesia",
            NameOrigin.JAPANESE: "nama Jepang",
            NameOrigin.KOREAN: "nama Korea",
            NameOrigin.WESTERN: "nama Barat",
            NameOrigin.UNIQUE: "nama unik"
        }.get(origin, "nama")
        
        if meaning:
            return f"{name} - {origin_text}, artinya '{meaning}'"
        else:
            return f"{name} - {origin_text}"
    
    def format_intro_name(self, name_data: Dict, role: str) -> str:
        """
        Format bagian nama untuk pesan perkenalan
        
        Args:
            name_data: Data nama
            role: Nama role
            
        Returns:
            String untuk perkenalan
        """
        name = name_data['name']
        meaning = name_data.get('meaning', '')
        
        # Personalisasi berdasarkan role
        role_intros = {
            'ipar': f"Aku **{name}**, Ipar mu. Namaku artinya '{meaning}' - kata orang aku memang jadi pusat perhatian kalau udah ngobrol.",
            'teman_kantor': f"Aku **{name}**, teman kantormu. Namaku artinya '{meaning}' - cocok sama kepribadianku yang hangat.",
            'janda': f"Aku **{name}**. Namaku artinya '{meaning}' - mungkin itu sebabnya aku selalu tahu apa yang kamu mau.",
            'pelakor': f"Aku **{name}**. Namaku artinya '{meaning}' - dan aku selalu mendapatkan apa yang aku inginkan.",
            'istri_orang': f"Aku **{name}**. Namaku artinya '{meaning}' - tapi jangan salah, aku punya sisi lain yang belum kamu tahu.",
            'pdkt': f"Aku **{name}**. Namaku artinya '{meaning}' - dan aku harap kita bisa menjadi sesuatu yang indah.",
            'sepupu': f"Aku **{name}**, sepupu mu. Namaku artinya '{meaning}' - kita punya hubungan spesial, kan?",
            'teman_sma': f"Aku **{name}**, teman SMA mu. Namaku artinya '{meaning}' - masih inget kenangan kita dulu?",
            'mantan': f"Aku **{name}**. Namaku artinya '{meaning}' - kamu masih inget aku, kan?"
        }
        
        return role_intros.get(role, f"Aku **{name}**. Namaku artinya '{meaning}'.")
    
    def generate_unique_id(self, name: str, role: str, user_id: int, session_seq: int) -> str:
        """
        Generate Unique ID dengan format:
        MYLOVE-NAMA-ROLE-USERID-DATE-SEQ
        
        Args:
            name: Nama bot
            role: Nama role
            user_id: ID user
            session_seq: Nomor urut session
            
        Returns:
            Unique ID string
        """
        from datetime import datetime
        
        # Format: MYLOVE-SARI-IPAR-12345678-20240315-001
        date_str = datetime.now().strftime("%Y%m%d")
        role_upper = role.upper()
        name_upper = name.upper().replace(' ', '_')
        
        return f"MYLOVE-{name_upper}-{role_upper}-{user_id}-{date_str}-{session_seq:03d}"
    
    def parse_unique_id(self, unique_id: str) -> Optional[Dict]:
        """
        Parse Unique ID menjadi komponennya
        
        Args:
            unique_id: String ID
            
        Returns:
            Dict komponen atau None
        """
        try:
            parts = unique_id.split('-')
            
            if len(parts) != 6 or parts[0] != 'MYLOVE':
                return None
            
            return {
                'prefix': parts[0],
                'bot_name': parts[1].title().replace('_', ' '),
                'role': parts[2].lower(),
                'user_id': int(parts[3]),
                'date': parts[4],
                'sequence': int(parts[5])
            }
        except:
            return None
    
    def get_available_roles(self) -> List[str]:
        """
        Dapatkan daftar role yang tersedia
        
        Returns:
            List nama role
        """
        return list(self.role_names.keys())
    
    def get_names_for_role(self, role: str) -> List[str]:
        """
        Dapatkan semua nama untuk role tertentu
        
        Args:
            role: Nama role
            
        Returns:
            List nama
        """
        if role not in self.role_names:
            return []
        
        return [n['name'] for n in self.role_names[role]]
    
    def reset_used_names(self, user_id: int, role: Optional[str] = None):
        """
        Reset tracking nama yang sudah dipakai
        
        Args:
            user_id: ID user
            role: Role spesifik (None untuk semua)
        """
        if user_id in self.used_names:
            if role:
                if role in self.used_names[user_id]:
                    del self.used_names[user_id][role]
            else:
                del self.used_names[user_id]
            
            logger.info(f"Reset used names for user {user_id}" + (f" role {role}" if role else ""))


__all__ = ['NameGenerator', 'NameOrigin']
