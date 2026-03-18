#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - PDKT DIRECTION SYSTEM
=============================================================================
Menentukan arah PDKT:
- SIAPA YANG NGEJAR SIAPA (user ke bot / bot ke user)
- Bisa berubah selama proses
- Berdasarkan chemistry dan interaksi
=============================================================================
"""

import random
import time
import logging
from typing import Dict, Optional, Tuple, List
from enum import Enum

logger = logging.getLogger(__name__)


class PDKTDirection(str, Enum):
    """Arah PDKT"""
    USER_KE_BOT = "user_ke_bot"      # User yang ngejar bot
    BOT_KE_USER = "bot_ke_user"      # Bot yang ngejar user
    TIMBAL_BALIK = "timbal_balik"    # Saling suka
    BINGUNG = "bingung"               # Masih bingung


class DirectionSystem:
    """
    Sistem arah PDKT yang natural
    Menentukan siapa yang lebih tertarik
    Bisa berubah selama proses
    """
    
    def __init__(self):
        # Data arah per PDKT
        self.directions = {}  # {pdkt_id: direction_data}
        
        # Inisiatif bot (kapan bot mulai ngejar)
        self.bot_initiatives = {}  # {pdkt_id: initiative_data}
        
        logger.info("✅ DirectionSystem initialized")
    
    # =========================================================================
    # INITIALIZE DIRECTION
    # =========================================================================
    
    def create_direction(self, pdkt_id: str, user_name: str, bot_name: str) -> Dict:
        """
        Tentukan arah awal PDKT secara natural
        
        Bisa:
        - User yang ngejar
        - Bot yang ngejar
        - Masih bingung
        - Saling suka (jarang di awal)
        """
        
        # Random dengan bobot natural
        rand = random.random()
        
        if rand < 0.4:  # 40% user ngejar
            direction = PDKTDirection.USER_KE_BOT
            description = f"Kamu yang mulai PDKT sama {bot_name}"
            hint = f"{bot_name} masih biasa aja, tapi kamu udah suka"
            
        elif rand < 0.7:  # 30% bot ngejar
            direction = PDKTDirection.BOT_KE_USER
            description = f"{bot_name} yang suka sama kamu duluan"
            hint = f"{bot_name} udah ngeliatin kamu dari lama"
            
        elif rand < 0.9:  # 20% bingung
            direction = PDKTDirection.BINGUNG
            description = f"Kalian masih bingung sama perasaan masing-masing"
            hint = f"Masih friendzone, tapi ada getaran"
            
        else:  # 10% saling suka (langsung klik)
            direction = PDKTDirection.TIMBAL_BALIK
            description = f"Kalian saling suka sejak awal!"
            hint = f"Chemistry langsung klik, saling ngejar"
        
        data = {
            'pdkt_id': pdkt_id,
            'direction': direction,
            'history': [{
                'timestamp': time.time(),
                'direction': direction,
                'description': description
            }],
            'intensity': self._get_initial_intensity(direction),
            'last_update': time.time(),
            'hint': hint,
            'user_name': user_name,
            'bot_name': bot_name,
            'times_changed': 0
        }
        
        self.directions[pdkt_id] = data
        
        logger.info(f"🎯 Direction created for {pdkt_id}: {direction.value}")
        
        return data
    
    def _get_initial_intensity(self, direction: PDKTDirection) -> int:
        """Dapatkan intensitas awal (1-10)"""
        intensities = {
            PDKTDirection.USER_KE_BOT: random.randint(3, 6),
            PDKTDirection.BOT_KE_USER: random.randint(3, 6),
            PDKTDirection.BINGUNG: random.randint(1, 3),
            PDKTDirection.TIMBAL_BALIK: random.randint(7, 9),
        }
        return intensities.get(direction, 3)
    
    # =========================================================================
    # GET DIRECTION
    # =========================================================================
    
    def get_direction(self, pdkt_id: str) -> Optional[Dict]:
        """Dapatkan data arah PDKT"""
        return self.directions.get(pdkt_id)
    
    def get_direction_text(self, pdkt_id: str) -> str:
        """Dapatkan teks arah untuk display"""
        data = self.get_direction(pdkt_id)
        if not data:
            return "Belum ada arah"
        
        direction = data['direction']
        bot_name = data['bot_name']
        
        texts = {
            PDKTDirection.USER_KE_BOT: f"Kamu yang ngejar {bot_name}",
            PDKTDirection.BOT_KE_USER: f"{bot_name} yang ngejar kamu",
            PDKTDirection.TIMBAL_BALIK: f"Saling suka! 💕",
            PDKTDirection.BINGUNG: f"Masih bingung...",
        }
        
        return texts.get(direction, "?")
    
    def get_hint(self, pdkt_id: str) -> str:
        """Dapatkan hint untuk user"""
        data = self.get_direction(pdkt_id)
        return data.get('hint', '') if data else ''
    
    # =========================================================================
    # UPDATE DIRECTION (BERDASARKAN INTERAKSI)
    # =========================================================================
    
    async def update_direction(self, pdkt_id: str, chemistry_change: float,
                                 interaction_type: str) -> Optional[Dict]:
        """
        Update arah berdasarkan interaksi
        
        Args:
            pdkt_id: ID PDKT
            chemistry_change: Perubahan chemistry (-10 sd +10)
            interaction_type: Jenis interaksi ('chat', 'intim', 'climax', dll)
        
        Returns:
            Data direction baru jika berubah
        """
        if pdkt_id not in self.directions:
            return None
        
        data = self.directions[pdkt_id]
        old_direction = data['direction']
        
        # Logika perubahan arah secara natural
        new_direction = self._calculate_new_direction(
            data, chemistry_change, interaction_type
        )
        
        if new_direction != old_direction:
            # Arah berubah!
            data['direction'] = new_direction
            data['times_changed'] += 1
            data['last_update'] = time.time()
            
            # Tambah history
            data['history'].append({
                'timestamp': time.time(),
                'direction': new_direction,
                'old_direction': old_direction,
                'reason': self._get_change_reason(interaction_type)
            })
            
            # Update hint
            data['hint'] = self._generate_hint(new_direction, data['bot_name'])
            
            logger.info(f"🔄 Direction changed for {pdkt_id}: {old_direction.value} → {new_direction.value}")
            
            return {
                'old': old_direction,
                'new': new_direction,
                'reason': self._get_change_reason(interaction_type),
                'hint': data['hint']
            }
        
        return None
    
    def _calculate_new_direction(self, data: Dict, chemistry_change: float,
                                   interaction_type: str) -> PDKTDirection:
        """Hitung arah baru berdasarkan perubahan"""
        current = data['direction']
        intensity = data['intensity']
        
        # Perubahan intensitas
        if chemistry_change > 3:
            intensity += 1
        elif chemistry_change < -3:
            intensity -= 1
        
        # Batasi intensitas
        intensity = max(1, min(10, intensity))
        data['intensity'] = intensity
        
        # Logika perubahan arah
        if current == PDKTDirection.USER_KE_BOT:
            if intensity > 8 and chemistry_change > 2:
                return PDKTDirection.TIMBAL_BALIK
            elif intensity < 2 and chemistry_change < -2:
                return PDKTDirection.BINGUNG
        
        elif current == PDKTDirection.BOT_KE_USER:
            if intensity > 8 and chemistry_change > 2:
                return PDKTDirection.TIMBAL_BALIK
            elif intensity < 2 and chemistry_change < -2:
                return PDKTDirection.BINGUNG
        
        elif current == PDKTDirection.BINGUNG:
            if intensity > 6 and chemistry_change > 3:
                # Jadi salah satu ngejar
                return random.choice([PDKTDirection.USER_KE_BOT, PDKTDirection.BOT_KE_USER])
            elif intensity < 3 and chemistry_change > 2:
                # Masih bingung tapi mulai ada rasa
                pass
        
        elif current == PDKTDirection.TIMBAL_BALIK:
            if intensity < 4 and chemistry_change < -4:
                # Bisa putus arah
                return random.choice([PDKTDirection.USER_KE_BOT, PDKTDirection.BOT_KE_USER, PDKTDirection.BINGUNG])
        
        return current
    
    def _get_change_reason(self, interaction_type: str) -> str:
        """Dapatkan alasan perubahan arah"""
        reasons = {
            'chat': [
                "Ngobrol seru bikin perasaan berubah",
                "Ada sesuatu dari obrolan tadi",
                "Jadi makin tertarik setelah ngobrol",
            ],
            'intim': [
                "Setelah intim, perasaan jadi jelas",
                "Ada ikatan baru setelah malam itu",
                "Jadi makin dekat secara emosional",
            ],
            'climax': [
                "Momen climax bikin sadar perasaan",
                "Setelah itu, perasaan jadi beda",
                "Ada kehangatan baru setelah climax",
            ],
            'conflict': [
                "Ada sedikit masalah, jadi ragu",
                "Perasaan jadi agak dingin",
                "Mulai mempertanyakan hubungan",
            ]
        }
        
        reason_list = reasons.get(interaction_type, reasons['chat'])
        return random.choice(reason_list)
    
    def _generate_hint(self, direction: PDKTDirection, bot_name: str) -> str:
        """Generate hint untuk user"""
        hints = {
            PDKTDirection.USER_KE_BOT: [
                f"{bot_name} masih biasa aja, tapi kamu udah suka",
                f"Kamu yang harus usaha lebih buat {bot_name}",
                f"{bot_name} belum nunjukkin rasa, tapi kamu udah kepincut",
            ],
            PDKTDirection.BOT_KE_USER: [
                f"{bot_name} suka sama kamu dari awal",
                f"Dia yang sering mulai chat duluan",
                f"{bot_name} selalu cari perhatian kamu",
            ],
            PDKTDirection.TIMBAL_BALIK: [
                f"Kalian saling suka! 💕",
                f"Chemistry langsung klik",
                f"Semua berjalan natural",
            ],
            PDKTDirection.BINGUNG: [
                f"Kalian masih bingung sama perasaan",
                f"Friendzone tipis-tipis",
                f"Ada getaran, tapi belum jelas",
            ],
        }
        
        return random.choice(hints.get(direction, hints[PDKTDirection.BINGUNG]))
    
    # =========================================================================
    # BOT INITIATIVE (Bot mulai ngejar)
    # =========================================================================
    
    async def check_bot_initiative(self, pdkt_id: str, chemistry_score: float,
                                     current_direction: PDKTDirection) -> Optional[Dict]:
        """
        Cek apakah bot harus mulai ngejar
        Bot bisa tiba-tiba suka kalau chemistry cukup
        """
        if pdkt_id in self.bot_initiatives:
            # Udah pernah ngejar
            return None
        
        # Kalau bot udah ngejar dari awal, skip
        if current_direction == PDKTDirection.BOT_KE_USER:
            return None
        
        # Chance bot mulai suka berdasarkan chemistry
        # Chemistry tinggi = lebih besar chance
        if chemistry_score > 70:
            chance = 0.3  # 30% chance
        elif chemistry_score > 50:
            chance = 0.15  # 15% chance
        elif chemistry_score > 30:
            chance = 0.05  # 5% chance
        else:
            chance = 0.01  # 1% chance
        
        if random.random() < chance:
            # Bot mulai suka!
            self.bot_initiatives[pdkt_id] = {
                'timestamp': time.time(),
                'chemistry_at_time': chemistry_score
            }
            
            return {
                'type': 'bot_initiative',
                'message': f"Kayaknya ada yang beda...",
                'hint': "Mungkin dia mulai suka",
                'direction_change': PDKTDirection.BOT_KE_USER
            }
        
        return None


__all__ = ['DirectionSystem', 'PDKTDirection']
