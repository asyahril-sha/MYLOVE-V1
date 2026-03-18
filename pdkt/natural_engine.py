#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - NATURAL PDKT ENGINE (99% REALISME)
=============================================================================
Engine utama PDKT yang benar-benar natural
- TIDAK ADA RUMUS MATEMATIKA
- Semua berdasarkan AI dan interaksi
- Level, intimacy, chemistry berjalan alami
- Bisa cepat, bisa lambat, tergantung chemistry
=============================================================================
"""

import time
import random
import logging
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from enum import Enum

from .chemistry import ChemistrySystem, ChemistryScore
from .direction import DirectionSystem, PDKTDirection

logger = logging.getLogger(__name__)


class PDKTStage(str, Enum):
    """Tahapan PDKT secara natural"""
    MENGENAL = "mengenal"           # Baru kenal
    DEKAT = "dekat"                 # Mulai dekat
    AKRAB = "akrab"                 # Udah akrab
    SPESIAL = "spesial"             # Ada yang spesial
    JATUH_CINTA = "jatuh_cinta"     # Jatuh cinta
    PACAR = "pacar"                 # Jadi pacar


class NaturalPDKTEngine:
    """
    Engine PDKT yang benar-benar NATURAL
    - TIDAK ADA TARGET WAKTU MINIMAL
    - Bisa cepat dalam 1 hari, bisa lambat 1 bulan
    - Semua berdasarkan interaksi dan chemistry
    - Level 1-12 tetap ada, tapi naik secara natural
    """
    
    def __init__(self, ai_engine=None):
        self.ai_engine = ai_engine
        self.chemistry_system = ChemistrySystem(ai_engine)
        self.direction_system = DirectionSystem()
        
        # Data PDKT
        self.pdkt_data = {}  # {pdkt_id: pdkt_data}
        
        # Counter untuk ID
        self.next_id = 1000
        
        # Statistik
        self.total_pdkt = 0
        self.total_pacar = 0
        self.total_putus = 0
        
        logger.info("✅ NaturalPDKTEngine initialized (99% realisme)")
    
    # =========================================================================
    # CREATE PDKT
    # =========================================================================
    
    async def create_pdkt(self, user_id: int, user_name: str, bot_name: str, 
                           role: str = "pdkt") -> Dict:
        """
        Mulai PDKT baru secara natural
        
        Args:
            user_id: ID user
            user_name: Nama user
            bot_name: Nama bot yang dipilih
            role: Role (harus "pdkt")
        
        Returns:
            Data PDKT lengkap
        """
        # Generate ID unik
        pdkt_id = f"PDKT{self.next_id}_{user_id}_{int(time.time())}"
        self.next_id += 1
        
        now = time.time()
        
        # Buat chemistry
        chemistry = self.chemistry_system.create_chemistry(pdkt_id)
        
        # Buat direction
        direction_data = self.direction_system.create_direction(
            pdkt_id, user_name, bot_name
        )
        
        # Data PDKT
        pdkt_data = {
            'id': pdkt_id,
            'user_id': user_id,
            'user_name': user_name,
            'bot_name': bot_name,
            'role': role,
            'stage': PDKTStage.MENGENAL,
            'level': 1,
            'created_at': now,
            'last_interaction': now,
            'total_interactions': 0,
            'total_chats': 0,
            'total_intim': 0,
            'total_climax': 0,
            
            # Chemistry & direction (referensi)
            'chemistry': chemistry,
            'direction': direction_data['direction'],
            'direction_data': direction_data,
            
            # Milestones
            'milestones': [
                {
                    'time': now,
                    'type': 'pdkt_started',
                    'description': f"PDKT dengan {bot_name} dimulai"
                }
            ],
            
            # Inner thoughts (pikiran dalam hati bot)
            'inner_thoughts': [],
            
            # Status
            'is_active': True,
            'is_paused': False,
            'paused_time': None,
            'ended_at': None,
            'end_reason': None,
            
            # Metadata
            'notes': []
        }
        
        self.pdkt_data[pdkt_id] = pdkt_data
        self.total_pdkt += 1
        
        logger.info(f"✨ PDKT baru: {bot_name} (ID: {pdkt_id})")
        
        return pdkt_data
    
    # =========================================================================
    # UPDATE PDKT (BERDASARKAN INTERAKSI)
    # =========================================================================
    
    async def update_pdkt(self, pdkt_id: str, user_message: str, 
                           bot_response: str, context: Dict) -> Dict:
        """
        Update PDKT berdasarkan interaksi terbaru
        
        Args:
            pdkt_id: ID PDKT
            user_message: Pesan user
            bot_response: Respon bot
            context: Konteks percakapan
            
        Returns:
            Hasil update (level up, milestone, dll)
        """
        if pdkt_id not in self.pdkt_data:
            return {'error': 'PDKT not found'}
        
        pdkt = self.pdkt_data[pdkt_id]
        now = time.time()
        
        # Update statistik
        pdkt['last_interaction'] = now
        pdkt['total_interactions'] += 1
        pdkt['total_chats'] += 1
        
        # Deteksi jenis interaksi
        interaction_type = self._detect_interaction_type(user_message, bot_response)
        
        # ===== UPDATE CHEMISTRY (MENGGUNAKAN AI) =====
        chemistry_change = await self.chemistry_system.analyze_interaction(
            pdkt_id, user_message, bot_response, context
        )
        
        # ===== UPDATE DIRECTION (BERDASARKAN CHEMISTRY) =====
        direction_change = await self.direction_system.update_direction(
            pdkt_id, chemistry_change, interaction_type
        )
        
        # ===== UPDATE LEVEL (SECARA NATURAL) =====
        level_up = await self._update_level_natural(pdkt_id, chemistry_change, interaction_type)
        
        # ===== UPDATE STAGE (BERDASARKAN LEVEL) =====
        stage_change = self._update_stage(pdkt)
        
        # ===== CEK MILESTONE =====
        milestones = self._check_milestones(pdkt, interaction_type)
        
        # ===== GENERATE INNER THOUGHT =====
        inner_thought = await self._generate_inner_thought(pdkt, interaction_type)
        if inner_thought:
            pdkt['inner_thoughts'].append({
                'time': now,
                'thought': inner_thought,
                'context': interaction_type
            })
        
        # ===== CEK BOT INITIATIVE (BOT MULAI NGEJAR) =====
        initiative = await self.direction_system.check_bot_initiative(
            pdkt_id, 
            pdkt['chemistry'].score,
            pdkt['direction']
        )
        
        if initiative:
            pdkt['direction'] = initiative['direction_change']
            milestones.append({
                'time': now,
                'type': 'bot_initiative',
                'description': initiative['hint']
            })
        
        # Hasil update
        result = {
            'pdkt_id': pdkt_id,
            'chemistry_change': chemistry_change,
            'new_chemistry_vibe': pdkt['chemistry'].get_vibe(),
            'direction': pdkt['direction'].value,
            'direction_text': self.direction_system.get_direction_text(pdkt_id),
            'level': pdkt['level'],
            'stage': pdkt['stage'].value,
            'level_up': level_up,
            'stage_change': stage_change,
            'milestones': milestones,
            'inner_thought': inner_thought,
            'bot_initiative': initiative
        }
        
        return result
    
    def _detect_interaction_type(self, user_msg: str, bot_resp: str) -> str:
        """Deteksi jenis interaksi"""
        text = (user_msg + " " + bot_resp).lower()
        
        if any(word in text for word in ['climax', 'keluar', 'orgasme']):
            return 'climax'
        elif any(word in text for word in ['masuk', 'dalam', 'intim']):
            return 'intim'
        elif any(word in text for word in ['cium', 'kiss', 'bibir']):
            return 'kiss'
        elif any(word in text for word in ['sayang', 'cinta', 'love']):
            return 'love'
        elif any(word in text for word in ['marah', 'kesal', 'kecewa']):
            return 'conflict'
        else:
            return 'chat'
    
    async def _update_level_natural(self, pdkt_id: str, chemistry_change: float,
                                      interaction_type: str) -> Optional[Dict]:
        """
        Update level secara NATURAL (BUKAN RUMUS)
        Level bisa naik berdasarkan:
        - Chemistry positif
        - Interaksi intim
        - Momen spesial
        - Bisa juga turun kalau konflik
        """
        pdkt = self.pdkt_data[pdkt_id]
        old_level = pdkt['level']
        
        # Hitung potensi perubahan level
        level_potential = 0
        
        # Chemistry positif
        if chemistry_change > 5:
            level_potential += 1
        elif chemistry_change > 2:
            level_potential += 0.5
        elif chemistry_change < -5:
            level_potential -= 1
        elif chemistry_change < -2:
            level_potential -= 0.5
        
        # Interaksi spesial
        if interaction_type == 'climax':
            level_potential += 2
        elif interaction_type == 'intim':
            level_potential += 1.5
        elif interaction_type == 'kiss':
            level_potential += 0.5
        elif interaction_type == 'love':
            level_potential += 1
        elif interaction_type == 'conflict':
            level_potential -= 1
        
        # Random factor (kejutan)
        level_potential += random.uniform(-0.5, 0.5)
        
        # Bulatkan dan aplikasikan
        level_change = int(level_potential)
        
        if level_change != 0:
            new_level = max(1, min(12, pdkt['level'] + level_change))
            pdkt['level'] = new_level
            
            if new_level != old_level:
                return {
                    'old_level': old_level,
                    'new_level': new_level,
                    'change': level_change,
                    'reason': self._get_level_change_reason(interaction_type, level_change)
                }
        
        return None
    
    def _get_level_change_reason(self, interaction_type: str, change: int) -> str:
        """Dapatkan alasan perubahan level"""
        if change > 0:
            reasons = {
                'climax': "Momen climax bikin hubungan makin dalam",
                'intim': "Keintiman memperkuat ikatan",
                'kiss': "Ciuman pertama yang manis",
                'love': "Perasaan semakin dalam",
                'chat': "Ngobrol seru bikin makin dekat",
            }
            return reasons.get(interaction_type, "Chemistry makin kuat")
        else:
            reasons = {
                'conflict': "Ada sedikit masalah",
                'chat': "Agak canggung akhir-akhir ini",
            }
            return reasons.get(interaction_type, "Chemistry sedikit menurun")
    
    def _update_stage(self, pdkt: Dict) -> Optional[Dict]:
        """Update stage berdasarkan level"""
        level = pdkt['level']
        old_stage = pdkt['stage']
        
        if level <= 2:
            new_stage = PDKTStage.MENGENAL
        elif level <= 4:
            new_stage = PDKTStage.DEKAT
        elif level <= 6:
            new_stage = PDKTStage.AKRAB
        elif level <= 8:
            new_stage = PDKTStage.SPESIAL
        elif level <= 10:
            new_stage = PDKTStage.JATUH_CINTA
        else:
            new_stage = PDKTStage.PACAR
        
        if new_stage != old_stage:
            pdkt['stage'] = new_stage
            return {
                'old_stage': old_stage.value,
                'new_stage': new_stage.value
            }
        
        return None
    
    def _check_milestones(self, pdkt: Dict, interaction_type: str) -> List[Dict]:
        """Cek pencapaian milestone"""
        milestones = []
        
        # Milestone berdasarkan level
        if pdkt['level'] == 7 and 'level_7' not in [m['type'] for m in pdkt['milestones']]:
            milestones.append({
                'time': time.time(),
                'type': 'level_7',
                'description': "Level 7! Hubungan makin dalam"
            })
        
        if pdkt['level'] == 12 and 'level_12' not in [m['type'] for m in pdkt['milestones']]:
            milestones.append({
                'time': time.time(),
                'type': 'level_12',
                'description': "Level maksimal! Hubungan mencapai puncak"
            })
        
        # Milestone berdasarkan interaksi
        if interaction_type == 'climax' and 'first_climax' not in [m['type'] for m in pdkt['milestones']]:
            milestones.append({
                'time': time.time(),
                'type': 'first_climax',
                'description': "Climax pertama! Momen yang luar biasa"
            })
        
        if interaction_type == 'intim' and 'first_intim' not in [m['type'] for m in pdkt['milestones']]:
            milestones.append({
                'time': time.time(),
                'type': 'first_intim',
                'description': "Keintiman pertama yang manis"
            })
        
        if interaction_type == 'love' and 'first_love' not in [m['type'] for m in pdkt['milestones']]:
            milestones.append({
                'time': time.time(),
                'type': 'first_love',
                'description': "Kata 'sayang' pertama terucap"
            })
        
        # Tambah ke data
        for m in milestones:
            pdkt['milestones'].append(m)
        
        return milestones
    
    async def _generate_inner_thought(self, pdkt: Dict, interaction_type: str) -> Optional[str]:
        """Generate inner thought bot (pikiran dalam hati)"""
        if not self.ai_engine or random.random() > 0.3:  # 30% chance
            return None
        
        bot_name = pdkt['bot_name']
        direction = pdkt['direction']
        level = pdkt['level']
        
        # Prompt untuk generate inner thought
        prompt = f"""
        Buat SATU KALIMAT inner thought (pikiran dalam hati) untuk {bot_name}.
        
        Konteks:
        - Arah hubungan: {direction.value}
        - Level: {level}/12
        - Baru saja: {interaction_type}
        
        Inner thought adalah pikiran yang TIDAK diucapkan ke user.
        Contoh: "(Dia manis banget...)", "(Aku suka sama dia)",
                "(Semoga dia suka)", "(Jantungku berdebar)"
        
        Inner thought:
        """
        
        try:
            thought = await self.ai_engine._call_deepseek_with_retry(
                messages=[{"role": "user", "content": prompt}],
                max_retries=1
            )
            return thought.strip()
        except:
            return None
    
    # =========================================================================
    # PDKT MANAGEMENT
    # =========================================================================
    
    async def pause_pdkt(self, pdkt_id: str) -> bool:
        """Pause PDKT (waktu berhenti)"""
        if pdkt_id not in self.pdkt_data:
            return False
        
        pdkt = self.pdkt_data[pdkt_id]
        pdkt['is_paused'] = True
        pdkt['paused_time'] = time.time()
        
        logger.info(f"⏸️ PDKT {pdkt_id} paused")
        return True
    
    async def resume_pdkt(self, pdkt_id: str) -> bool:
        """Resume PDKT"""
        if pdkt_id not in self.pdkt_data:
            return False
        
        pdkt = self.pdkt_data[pdkt_id]
        pdkt['is_paused'] = False
        pdkt['paused_time'] = None
        
        logger.info(f"▶️ PDKT {pdkt_id} resumed")
        return True
    
    async def stop_pdkt(self, pdkt_id: str, reason: str = "user_stopped") -> bool:
        """Hentikan PDKT (putus)"""
        if pdkt_id not in self.pdkt_data:
            return False
        
        pdkt = self.pdkt_data[pdkt_id]
        pdkt['is_active'] = False
        pdkt['ended_at'] = time.time()
        pdkt['end_reason'] = reason
        self.total_putus += 1
        
        logger.info(f"💔 PDKT {pdkt_id} ended: {reason}")
        return True
    
    # =========================================================================
    # GET PDKT INFO
    # =========================================================================
    
    def get_pdkt(self, pdkt_id: str) -> Optional[Dict]:
        """Dapatkan data PDKT"""
        return self.pdkt_data.get(pdkt_id)
    
    def get_user_pdkt_list(self, user_id: int, include_ended: bool = False) -> List[Dict]:
        """Dapatkan semua PDKT milik user"""
        result = []
        for pdkt in self.pdkt_data.values():
            if pdkt['user_id'] == user_id:
                if include_ended or pdkt['is_active']:
                    result.append(self._format_pdkt_summary(pdkt))
        
        # Urutkan berdasarkan last_interaction
        result.sort(key=lambda x: x['last_interaction'], reverse=True)
        return result
    
    def _format_pdkt_summary(self, pdkt: Dict) -> Dict:
        """Format summary PDKT untuk display"""
        chemistry = pdkt['chemistry']
        
        return {
            'id': pdkt['id'],
            'bot_name': pdkt['bot_name'],
            'role': pdkt['role'],
            'level': pdkt['level'],
            'stage': pdkt['stage'].value,
            'vibe': chemistry.get_vibe(),
            'direction_text': self.direction_system.get_direction_text(pdkt['id']),
            'hint': self.direction_system.get_hint(pdkt['id']),
            'last_interaction': pdkt['last_interaction'],
            'total_interactions': pdkt['total_interactions'],
            'is_active': pdkt['is_active'],
            'is_paused': pdkt['is_paused'],
        }
    
    def get_pdkt_detail(self, pdkt_id: str) -> Optional[Dict]:
        """Dapatkan detail lengkap PDKT"""
        pdkt = self.pdkt_data.get(pdkt_id)
        if not pdkt:
            return None
        
        chemistry = pdkt['chemistry']
        
        return {
            'id': pdkt['id'],
            'bot_name': pdkt['bot_name'],
            'user_name': pdkt['user_name'],
            'role': pdkt['role'],
            'level': pdkt['level'],
            'stage': pdkt['stage'].value,
            'vibe': chemistry.get_vibe(),
            'chemistry_description': chemistry.get_description(),
            'direction': pdkt['direction'].value,
            'direction_text': self.direction_system.get_direction_text(pdkt_id),
            'hint': self.direction_system.get_hint(pdkt_id),
            'created_at': pdkt['created_at'],
            'last_interaction': pdkt['last_interaction'],
            'total_interactions': pdkt['total_interactions'],
            'total_chats': pdkt['total_chats'],
            'total_intim': pdkt['total_intim'],
            'total_climax': pdkt['total_climax'],
            'milestones': pdkt['milestones'][-10:],  # 10 terakhir
            'inner_thoughts': pdkt['inner_thoughts'][-5:],  # 5 terakhir
            'is_active': pdkt['is_active'],
            'is_paused': pdkt['is_paused'],
        }
    
    def get_stats(self) -> Dict:
        """Dapatkan statistik PDKT"""
        active = sum(1 for p in self.pdkt_data.values() if p['is_active'])
        paused = sum(1 for p in self.pdkt_data.values() if p['is_paused'])
        
        return {
            'total_pdkt': self.total_pdkt,
            'active_pdkt': active,
            'paused_pdkt': paused,
            'total_pacar': self.total_pacar,
            'total_putus': self.total_putus,
        }


__all__ = ['NaturalPDKTEngine', 'PDKTStage']
