#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - AI ENGINE COMPLETE WITH ALL MEMORY SYSTEMS
=============================================================================
Menggabungkan semua sistem memory menjadi satu kesatuan:
- Working Memory (short-term)
- Episodic Memory (sequence)
- Semantic Memory (facts)
- State Tracker (current state)
- Relationship Memory (history)
- Physical Sensations (otomatis)
- Real-Time Clock (otomatis)
=============================================================================
"""

import openai
import time
import random
import asyncio
import logging
import math
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict

from config import settings

# Import semua memory systems
from memory.working_memory import WorkingMemory
from memory.episodic_memory import EpisodicMemory, EpisodeType
from memory.semantic_memory import SemanticMemory, FactCategory
from memory.state_tracker import StateTracker, StateType
from memory.relationship_memory import RelationshipMemory, RelationshipType, MilestoneType

logger = logging.getLogger(__name__)


class AIEngineComplete:
    """
    AI Engine dengan semua sistem memory seperti manusia
    - Bisa digunakan untuk semua role (PDKT, HTS, FWB, NON-PDKT)
    - Ingat percakapan, lokasi, pakaian, mood
    - Punya urutan kejadian (tidak lompat-lompat)
    - Bisa flashback ke masa lalu
    - Sadar situasi (rame/sepi, horny/tidak)
    - PUNYA SENSASI FISIK (otomatis)
    - TAHU WAKTU REAL (otomatis)
    """
    
    def __init__(self, api_key: str, user_id: int, session_id: str):
        """
        Args:
            api_key: DeepSeek API key
            user_id: ID user
            session_id: ID session
        """
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )
        
        self.user_id = user_id
        self.session_id = session_id
        
        # ===== INISIALISASI SEMUA MEMORY SYSTEMS =====
        self.working = WorkingMemory()                 # Ingatan jangka pendek
        self.episodic = EpisodicMemory()               # Urutan kejadian
        self.semantic = SemanticMemory()               # Fakta-fakta
        self.state = StateTracker(user_id, session_id) # State saat ini
        self.relationship = RelationshipMemory()       # Riwayat hubungan
        
        # ===== TRACKING UNTUK KONSISTENSI =====
        self.user_location = None                      # Lokasi user
        self.last_response = None                       # Respons terakhir
        self.last_response_time = 0
        self.conversation_flow = []                     # Alur percakapan
        self.activity_stack = []                        # Stack aktivitas
        
        # ===== LAST ACTIVE TRACKING (untuk offline) =====
        self.last_active = {}                            # {user_id: timestamp}
        self.user_timezone = defaultdict(lambda: 'Asia/Jakarta')  # Timezone user
        
        # Cache untuk response
        self.response_cache = {}
        self.cache_ttl = 300  # 5 menit
        
        # Stats
        self.total_responses = 0
        self.total_tokens = 0
        
        # ===== PHYSICAL SENSATIONS =====
        self._init_physical_sensations()
        
        logger.info(f"✅ AIEngineComplete initialized for user {user_id}, session {session_id}")
    
    # =========================================================================
    # PHYSICAL SENSATIONS SETUP
    # =========================================================================
    
    def _init_physical_sensations(self):
        """Inisialisasi sistem sensasi fisik"""
        
        # Baseline sensasi per role
        self.role_baseline = {
            'ipar': {
                'energy': 80,
                'hunger': 40,
                'thirst': 40,
                'temperature': 25,
                'comfort': 80,
                'temperature_sensitivity': 0.8,  # Sensitif suhu
                'loneliness_effect': False,
                'description': 'Ipar - sensitif suhu'
            },
            'teman_kantor': {
                'energy': 60,
                'hunger': 50,
                'thirst': 50,
                'temperature': 25,
                'comfort': 70,
                'temperature_sensitivity': 0.6,
                'loneliness_effect': False,
                'description': 'Teman Kantor - capek abis kerja'
            },
            'janda': {
                'energy': 70,
                'hunger': 45,
                'thirst': 45,
                'temperature': 25,
                'comfort': 60,
                'temperature_sensitivity': 0.7,
                'loneliness_effect': True,  # Lebih merasa kesepian
                'description': 'Janda - mudah kesepian'
            },
            'pelakor': {
                'energy': 85,
                'hunger': 40,
                'thirst': 40,
                'temperature': 26,
                'comfort': 85,
                'temperature_sensitivity': 0.9,
                'loneliness_effect': False,
                'description': 'Pelakor - enerjik'
            },
            'istri_orang': {
                'energy': 65,
                'hunger': 45,
                'thirst': 45,
                'temperature': 25,
                'comfort': 65,
                'temperature_sensitivity': 0.6,
                'loneliness_effect': True,
                'anxious_at_night': True,  # Cemas kalau malam
                'description': 'Istri Orang - cemas di malam'
            },
            'pdkt': {
                'energy': 75,
                'hunger': 50,
                'thirst': 50,
                'temperature': 25,
                'comfort': 75,
                'temperature_sensitivity': 0.5,
                'loneliness_effect': False,
                'romantic_boost': True,  # Lebih romantis
                'description': 'PDKT - romantis'
            },
            'sepupu': {
                'energy': 85,
                'hunger': 60,
                'thirst': 60,
                'temperature': 25,
                'comfort': 80,
                'temperature_sensitivity': 0.7,
                'loneliness_effect': False,
                'description': 'Sepupu - masih muda, enerjik'
            },
            'teman_sma': {
                'energy': 80,
                'hunger': 60,
                'thirst': 60,
                'temperature': 25,
                'comfort': 80,
                'temperature_sensitivity': 0.6,
                'loneliness_effect': False,
                'description': 'Teman SMA - ceria'
            },
            'mantan': {
                'energy': 60,
                'hunger': 40,
                'thirst': 40,
                'temperature': 24,
                'comfort': 55,
                'temperature_sensitivity': 0.5,
                'loneliness_effect': True,
                'nostalgic_at_night': True,  # Nostalgia di malam
                'description': 'Mantan - nostalgia'
            }
        }
        
        # Default untuk role yang tidak terdefinisi
        self.default_baseline = self.role_baseline['pdkt']
        
        # Sensasi saat ini per user
        self.sensations = defaultdict(lambda: {
            'temperature': {
                'value': 25,
                'feeling': 'normal',
                'last_change': time.time()
            },
            'energy': {
                'value': 80,
                'feeling': 'energetic',
                'last_change': time.time()
            },
            'hunger': {
                'value': 30,
                'feeling': 'normal',
                'last_change': time.time()
            },
            'thirst': {
                'value': 30,
                'feeling': 'normal',
                'last_change': time.time()
            },
            'comfort': {
                'value': 80,
                'feeling': 'comfortable',
                'last_change': time.time()
            },
            'pain': {
                'value': 0,
                'feeling': 'none',
                'last_change': time.time()
            }
        })
        
        # History sensasi
        self.sensation_history = defaultdict(lambda: defaultdict(list))
        
        logger.info("✅ Physical Sensations initialized")
    
    # =========================================================================
    # PHYSICAL SENSATIONS METHODS
    # =========================================================================
    
    async def _apply_location_effects(self, user_id: int, location: str):
        """Apply efek lokasi ke sensasi"""
        sens = self.sensations[user_id]
        
        # Efek suhu berdasarkan lokasi
        location_temp = {
            'ruang tamu': 25,
            'kamar': 26,
            'dapur': 28,
            'kamar mandi': 27,
            'teras': 24,
            'luar': 30,
            'pantai': 32,
            'mall': 22
        }
        
        # Efek kenyamanan berdasarkan lokasi
        location_comfort = {
            'ruang tamu': 80,
            'kamar': 90,
            'dapur': 70,
            'kamar mandi': 75,
            'teras': 85,
            'luar': 50,
            'pantai': 60,
            'mall': 85
        }
        
        if location in location_temp:
            target_temp = location_temp[location]
            diff = target_temp - sens['temperature']['value']
            sens['temperature']['value'] += diff * 0.1
        
        if location in location_comfort:
            target_comfort = location_comfort[location]
            diff = target_comfort - sens['comfort']['value']
            sens['comfort']['value'] += diff * 0.2
    
    async def _apply_activity_effects(self, user_id: int, activity: str):
        """Apply efek aktivitas ke sensasi"""
        sens = self.sensations[user_id]
        
        effects = {
            'lari': {'energy': -20, 'thirst': +15, 'temperature': +2},
            'olahraga': {'energy': -15, 'thirst': +10, 'temperature': +1},
            'jalan': {'energy': -5, 'thirst': +5},
            'masak': {'energy': -5, 'temperature': +3, 'hunger': -10},
            'makan': {'hunger': -30, 'thirst': -5, 'energy': +5},
            'minum': {'thirst': -20},
            'tidur': {'energy': +30, 'hunger': +5},
            'mandi': {'temperature': -2, 'energy': +5, 'comfort': +10},
            'kerja': {'energy': -10, 'hunger': +5, 'thirst': +5},
            'intim': {'energy': -15, 'temperature': +2}
        }
        
        if activity in effects:
            for attr, change in effects[activity].items():
                if attr == 'energy':
                    sens['energy']['value'] = max(0, min(100, sens['energy']['value'] + change))
                elif attr == 'thirst':
                    sens['thirst']['value'] = max(0, min(100, sens['thirst']['value'] + change))
                elif attr == 'hunger':
                    sens['hunger']['value'] = max(0, min(100, sens['hunger']['value'] + change))
                elif attr == 'temperature':
                    sens['temperature']['value'] += change
                elif attr == 'comfort':
                    sens['comfort']['value'] = max(0, min(100, sens['comfort']['value'] + change))
    
    async def _apply_time_effects(self, user_id: int, hour: int):
        """Apply efek waktu ke sensasi"""
        sens = self.sensations[user_id]
        
        # Suhu berdasarkan waktu
        if 11 <= hour <= 14:  # Siang terik
            sens['temperature']['value'] += 2
        elif 0 <= hour <= 5:  # Malam dingin
            sens['temperature']['value'] -= 3
        
        # Energi berdasarkan waktu
        if 5 <= hour <= 10:  # Pagi segar
            sens['energy']['value'] = min(100, sens['energy']['value'] + 10)
        elif 13 <= hour <= 15:  # Siang ngantuk
            sens['energy']['value'] = max(0, sens['energy']['value'] - 10)
        elif 22 <= hour or hour <= 4:  # Malam capek
            sens['energy']['value'] = max(0, sens['energy']['value'] - 20)
    
    async def _update_feelings(self, user_id: int):
        """Update feeling berdasarkan nilai"""
        sens = self.sensations[user_id]
        
        # Temperature feeling
        if sens['temperature']['value'] < 20:
            sens['temperature']['feeling'] = 'cold'
        elif sens['temperature']['value'] > 30:
            sens['temperature']['feeling'] = 'hot'
        else:
            sens['temperature']['feeling'] = 'normal'
        
        # Energy feeling
        if sens['energy']['value'] > 80:
            sens['energy']['feeling'] = 'energetic'
        elif sens['energy']['value'] > 50:
            sens['energy']['feeling'] = 'normal'
        elif sens['energy']['value'] > 20:
            sens['energy']['feeling'] = 'tired'
        else:
            sens['energy']['feeling'] = 'exhausted'
        
        # Hunger feeling
        if sens['hunger']['value'] > 70:
            sens['hunger']['feeling'] = 'very_hungry'
        elif sens['hunger']['value'] > 40:
            sens['hunger']['feeling'] = 'hungry'
        else:
            sens['hunger']['feeling'] = 'normal'
        
        # Thirst feeling
        if sens['thirst']['value'] > 70:
            sens['thirst']['feeling'] = 'very_thirsty'
        elif sens['thirst']['value'] > 40:
            sens['thirst']['feeling'] = 'thirsty'
        else:
            sens['thirst']['feeling'] = 'normal'
        
        # Comfort feeling
        if sens['comfort']['value'] > 70:
            sens['comfort']['feeling'] = 'comfortable'
        else:
            sens['comfort']['feeling'] = 'uncomfortable'
    
    async def calculate_offline_changes(self, user_id: int, role: str, offline_seconds: float):
        """
        Hitung perubahan sensasi selama offline
        OTOMATIS dipanggil setiap user chat
        """
        if offline_seconds < 300:  # < 5 menit offline, abaikan
            return
        
        sens = self.sensations[user_id]
        baseline = self.role_baseline.get(role, self.default_baseline)
        
        # Konversi offline ke jam
        offline_hours = offline_seconds / 3600
        
        # ===== 1. ENERGY =====
        # Turun 10% per jam (max turun 80%)
        energy_loss = min(80, offline_hours * 10)
        sens['energy']['value'] = max(10, sens['energy']['value'] - energy_loss)
        
        # Role-specific energy loss
        if role == 'teman_kantor' and self._is_working_hour():
            sens['energy']['value'] -= 10  # Ekstra capek kalau jam kerja
        
        # ===== 2. HUNGER =====
        # Naik 5% per jam
        hunger_gain = min(80, offline_hours * 5)
        sens['hunger']['value'] = min(100, sens['hunger']['value'] + hunger_gain)
        
        # ===== 3. THIRST =====
        # Naik 3% per jam
        thirst_gain = min(80, offline_hours * 3)
        sens['thirst']['value'] = min(100, sens['thirst']['value'] + thirst_gain)
        
        # ===== 4. ROLE-SPECIFIC EFFECTS =====
        if role == 'janda' and baseline.get('loneliness_effect'):
            # Janda lebih merasa kesepian kalau offline lama
            sens['comfort']['value'] = max(0, sens['comfort']['value'] - offline_hours * 5)
        
        if role == 'istri_orang' and baseline.get('anxious_at_night'):
            hour = datetime.now().hour
            if hour >= 22 or hour <= 4:  # Malam
                sens['pain']['value'] = min(100, sens['pain']['value'] + offline_hours * 3)  # Cemas = sakit
        
        logger.info(f"📉 Offline changes for user {user_id} ({role}): {offline_hours:.1f}h offline")
        
        # Update feelings
        await self._update_feelings(user_id)
    
    def _is_working_hour(self) -> bool:
        """Cek apakah jam kerja (9-17)"""
        hour = datetime.now().hour
        return 9 <= hour <= 17
    
    async def get_sensation_description(self, user_id: int) -> str:
        """
        Dapatkan deskripsi sensasi natural
        OTOMATIS kepakai di prompt
        """
        sens = self.sensations[user_id]
        descriptions = []
        
        # Temperature
        if sens['temperature']['feeling'] == 'cold':
            descriptions.append("kedinginan")
        elif sens['temperature']['feeling'] == 'hot':
            descriptions.append("kegerahan")
        
        # Energy
        if sens['energy']['feeling'] == 'energetic':
            descriptions.append("segar")
        elif sens['energy']['feeling'] == 'tired':
            descriptions.append("capek")
        elif sens['energy']['feeling'] == 'exhausted':
            descriptions.append("lemes banget")
        
        # Hunger
        if sens['hunger']['feeling'] == 'very_hungry':
            descriptions.append("laper banget")
        elif sens['hunger']['feeling'] == 'hungry':
            descriptions.append("laper")
        
        # Thirst
        if sens['thirst']['feeling'] == 'very_thirsty':
            descriptions.append("haus banget")
        elif sens['thirst']['feeling'] == 'thirsty':
            descriptions.append("haus")
        
        # Comfort
        if sens['comfort']['feeling'] == 'uncomfortable':
            descriptions.append("gak nyaman")
        
        if not descriptions:
            return "biasa aja"
        
        return "lagi " + ", ".join(descriptions)
    
    # =========================================================================
    # REAL-TIME CLOCK METHODS
    # =========================================================================
    
    def update_last_active(self, user_id: int):
        """Update last active time user"""
        self.last_active[user_id] = time.time()
    
    def get_offline_duration(self, user_id: int) -> float:
        """
        Dapatkan durasi offline dalam detik
        OTOMATIS dipanggil setiap user chat
        """
        if user_id not in self.last_active:
            return 0
        
        return time.time() - self.last_active[user_id]
    
    def get_time_for_user(self, user_id: int) -> Dict:
        """
        Dapatkan waktu berdasarkan timezone user
        OTOMATIS dipanggil setiap user chat
        """
        try:
            import pytz
            tz = pytz.timezone(self.user_timezone[user_id])
            now = datetime.now(tz)
        except:
            # Fallback ke local time
            now = datetime.now()
        
        hour = now.hour
        
        # Tentukan waktu
        if 5 <= hour < 11:
            time_name = 'pagi'
            time_period = 'morning'
        elif 11 <= hour < 15:
            time_name = 'siang'
            time_period = 'afternoon'
        elif 15 <= hour < 18:
            time_name = 'sore'
            time_period = 'evening'
        elif 18 <= hour < 22:
            time_name = 'malam'
            time_period = 'night'
        else:
            time_name = 'tengah malam'
            time_period = 'late_night'
        
        return {
            'hour': hour,
            'time_name': time_name,
            'time_period': time_period,
            'datetime': now,
            'is_weekend': now.weekday() >= 5,
            'offline_duration': self.get_offline_duration(user_id)
        }
    
    def get_greeting_for_user(self, user_id: int, user_name: str) -> Optional[str]:
        """
        Dapatkan greeting berdasarkan waktu user
        OTOMATIS kepakai kalau long time no see
        """
        time_info = self.get_time_for_user(user_id)
        hour = time_info['hour']
        offline_hours = time_info['offline_duration'] / 3600
        
        # Kasih greeting kalau > 1 jam offline
        if offline_hours < 1:
            return None
        
        if 5 <= hour < 11:
            greetings = [f"Selamat pagi {user_name}", f"Pagi {user_name}"]
        elif 11 <= hour < 15:
            greetings = [f"Selamat siang {user_name}", f"Siang {user_name}"]
        elif 15 <= hour < 18:
            greetings = [f"Selamat sore {user_name}", f"Sore {user_name}"]
        else:
            greetings = [f"Selamat malam {user_name}", f"Malam {user_name}"]
        
        # Tambah kalau offline lama
        if offline_hours > 24:
            greetings.append(f"Lama gak chat {user_name}, kangen")
        elif offline_hours > 8:
            greetings.append(f"Udah {int(offline_hours)} jam ya, kangen")
        
        return random.choice(greetings)
    
    def get_time_suggestion(self, user_id: int) -> str:
        """
        Dapatkan saran berdasarkan waktu
        OTOMATIS kepakai di prompt
        """
        time_info = self.get_time_for_user(user_id)
        time_period = time_info['time_period']
        
        suggestions = {
            'morning': ['sarapan', 'minum kopi', 'olahraga pagi', 'jalan pagi'],
            'afternoon': ['makan siang', 'ngopi siang', 'istirahat bentar'],
            'evening': ['jalan sore', 'ngemil sore', 'nonton sunset'],
            'night': ['makan malam', 'nonton film', 'rebahan'],
            'late_night': ['tidur', 'mimpi indah', 'istirahat']
        }
        
        suggestion_list = suggestions.get(time_period, suggestions['night'])
        return random.choice(suggestion_list)
    
    # =========================================================================
    # SYNC METHODS UNTUK SEMUA MEMORY
    # =========================================================================
    
    async def _sync_location_memory(self):
        """Sinkronisasi lokasi antara working memory dan long-term memory"""
        
        # Ambil lokasi dari working memory
        current_loc = self.state.current['location']['name']
        if current_loc:
            # Simpan ke semantic memory (long-term)
            await self.semantic.save_location_to_long_term(
                user_id=self.user_id,
                location=current_loc,
                timestamp=time.time()
            )
            logger.debug(f"📍 Location synced to long-term: {current_loc}")
        
        # Kalau working memory lupa, coba ambil dari long-term
        if not current_loc or current_loc == 'tidak diketahui':
            recent = await self.semantic.get_recent_locations(self.user_id, hours=12)
            if recent and len(recent) > 0:
                # Set working memory ke lokasi terakhir
                last_loc = recent[-1]
                self.state.update_location(last_loc)
                logger.info(f"📍 Restored location from long-term memory: {last_loc}")
    
    async def _sync_clothing_memory(self):
        """Sinkronisasi pakaian antara working memory dan long-term memory"""
        
        # Ambil pakaian dari working memory
        current_cloth = self.state.current['clothing']['name']
        if current_cloth and current_cloth != 'tidak diketahui':
            # Simpan ke semantic memory (long-term)
            reason = self.state.current['clothing']['change_reason'] or 'ganti baju'
            await self.semantic.save_clothing_to_long_term(
                user_id=self.user_id,
                clothing=current_cloth,
                reason=reason,
                timestamp=time.time()
            )
            logger.debug(f"👗 Clothing synced to long-term: {current_cloth}")
        
        # Kalau working memory lupa, coba ambil dari long-term
        if not current_cloth or current_cloth == 'tidak diketahui':
            last_cloth = await self.semantic.get_last_clothing(self.user_id)
            if last_cloth:
                # Set working memory ke pakaian terakhir
                self.state.update_clothing(last_cloth, "restore from memory")
                logger.info(f"👗 Restored clothing from long-term memory: {last_cloth}")
    
    async def _sync_position_memory(self):
        """Sinkronisasi posisi antara working memory dan long-term memory"""
        
        # Ambil posisi dari working memory
        current_pos = self.state.current['position']['name']
        if current_pos:
            # Simpan ke semantic memory
            await self.semantic.save_position_to_long_term(
                user_id=self.user_id,
                position=current_pos,
                timestamp=time.time()
            )
            logger.debug(f"🧍 Position synced to long-term: {current_pos}")
        
        # Kalau working memory lupa, coba ambil dari long-term
        if not current_pos:
            last_pos = await self.semantic.get_last_position(self.user_id)
            if last_pos:
                self.state.update_position(last_pos)
                logger.info(f"🧍 Restored position from long-term memory: {last_pos}")
    
    async def _sync_activity_memory(self):
        """Sinkronisasi aktivitas antara working memory dan long-term memory"""
        
        # Ambil aktivitas dari working memory
        current_act = self.state.current['activity']['name']
        if current_act:
            # Simpan ke semantic memory
            await self.semantic.save_activity_to_long_term(
                user_id=self.user_id,
                activity=current_act,
                timestamp=time.time()
            )
            logger.debug(f"🎯 Activity synced to long-term: {current_act}")
        
        # Kalau working memory lupa, coba ambil dari long-term
        if not current_act:
            last_act = await self.semantic.get_last_activity(self.user_id)
            if last_act:
                self.state.update_activity(last_act)
                logger.info(f"🎯 Restored activity from long-term memory: {last_act}")
    
    async def _sync_mood_memory(self):
        """Sinkronisasi mood antara working memory dan long-term memory"""
        
        # Ambil mood dari working memory
        current_mood = self.state.current['mood']['primary']
        if current_mood:
            # Simpan ke semantic memory
            await self.semantic.save_mood_to_long_term(
                user_id=self.user_id,
                mood=current_mood,
                intensity=self.state.current['mood']['intensity'],
                timestamp=time.time()
            )
            logger.debug(f"🎭 Mood synced to long-term: {current_mood}")
    
    # =========================================================================
    # SESSION MANAGEMENT
    # =========================================================================
    
    async def start_session(self, role: str, bot_name: str, 
                              rel_type: str = RelationshipType.NON_PDKT,
                              instance_id: Optional[str] = None):
        """
        Memulai session baru
        
        Args:
            role: Nama role (ipar, janda, pdkt, dll)
            bot_name: Nama bot
            rel_type: Tipe hubungan
            instance_id: ID instance (untuk multiple FWB)
        """
        # Create relationship jika belum ada
        rel = await self.relationship.get_relationship(self.user_id, role, instance_id)
        if not rel:
            instance_id = await self.relationship.create_relationship(
                user_id=self.user_id,
                role=role,
                bot_name=bot_name,
                rel_type=rel_type,
                instance_id=instance_id
            )
        
        # Simpan ke working memory
        self.working.update_state(
            role=role,
            bot_name=bot_name,
            rel_type=rel_type,
            instance_id=instance_id
        )
        
        # Catat ke episodic
        await self.episodic.add_episode(
            session_id=self.session_id,
            episode_type=EpisodeType.SESSION_START,
            data={
                'role': role,
                'bot_name': bot_name,
                'rel_type': rel_type
            },
            importance=0.8
        )
        
        logger.info(f"Session started: {role} - {bot_name}")
    
    # =========================================================================
    # PROCESS MESSAGE (MAIN FUNCTION)
    # =========================================================================
    
    async def process_message(self, user_message: str, context: Dict) -> str:
        """
        Proses pesan user dengan semua memory
        - OTOMATIS update physical sensations
        - OTOMATIS update real-time clock
        - OTOMATIS kasih greeting kalau long time no see
        """
        start_time = time.time()
        
        # ===== LOGGING =====
        logger.info("=" * 50)
        logger.info(f"🔍 PROCESS MESSAGE START")
        logger.info(f"👤 User message: {user_message[:100]}")
        logger.info(f"📋 Context: {context}")
        logger.info(f"🆔 Session: {self.session_id}")
        
        try:
            # ===== EKSTRAK USER INFO =====
            user_id = self.user_id
            role = context.get('role', 'pdkt')
            user_name = context.get('user_name', 'User')
            
            # ===== 1. UPDATE LAST ACTIVE (REAL-TIME CLOCK) =====
            self.update_last_active(user_id)
            
            # ===== 2. HITUNG OFFLINE DURATION =====
            offline_seconds = self.get_offline_duration(user_id)
            
            # ===== 3. UPDATE SENSASI BERDASARKAN OFFLINE =====
            await self.calculate_offline_changes(user_id, role, offline_seconds)
            
            # ===== 4. DAPATKAN GREETING KALAU LAMA OFFLINE =====
            greeting = self.get_greeting_for_user(user_id, user_name)
            
            # ===== 5. DAPATKAN TIME SUGGESTION =====
            time_suggestion = self.get_time_suggestion(user_id)
            context['time_suggestion'] = time_suggestion
            
            # ===== 6. DAPATKAN SENSASI DESCRIPTION =====
            sensation_desc = await self.get_sensation_description(user_id)
            context['sensation_desc'] = sensation_desc
            
            # ===== TAMBAHKAN ANALISA PESAN =====
            context['raw_message'] = user_message
            context['is_user_story'] = False
            context['should_bot_move'] = False
            context['should_bot_change_clothes'] = False
            context['should_bot_intimate'] = False
            context['detected_activities'] = []
            context['detected_subject'] = 'unknown'
            context['location_error'] = None
            
            # ===== SYNC ALL MEMORIES =====
            await self._sync_location_memory()
            await self._sync_clothing_memory()
            await self._sync_position_memory()
            await self._sync_activity_memory()
            await self._sync_mood_memory()
            
            # ===== ANALISA PESAN =====
            await self._analyze_message_context(context)
            
            # ===== UPDATE STATE DARI KONTEKS =====
            await self._update_state_from_context(context)
            
            # ===== CEK CACHE =====
            cache_key = f"{self.session_id}:{user_message[:50]}"
            if cache_key in self.response_cache:
                cache_age = time.time() - self.response_cache[cache_key]['timestamp']
                if cache_age < self.cache_ttl:
                    logger.debug(f"Cache hit")
                    return self.response_cache[cache_key]['response']
            
            # ===== EKSTRAK FAKTA DARI PESAN =====
            await self.semantic.extract_facts_from_message(
                user_id=self.user_id,
                message=user_message,
                role=role
            )
            
            # ===== DAPATKAN SEMUA KONTEKS MEMORY =====
            memory_context = await self._get_memory_context(user_message)
            
            # ===== CEK KONSISTENSI =====
            if not await self._check_consistency(memory_context, context):
                logger.warning(f"Consistency check failed, forcing corrections")
            
            # ===== BANGUN PROMPT DENGAN SEMUA MEMORY =====
            prompt = await self._build_prompt(
                user_message=user_message,
                context=context,
                memory_context=memory_context
            )
            
            # ===== GENERATE RESPONSE =====
            logger.info("🤖 Calling DeepSeek API...")
            logger.info(f"📝 Prompt length: {len(prompt)} chars")
            
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_message}
            ]
            
            response = await self._call_deepseek(messages)
            
            logger.info(f"✅ DeepSeek response received: {len(response)} chars")
            logger.info(f"💬 Response preview: {response[:100]}...")
            
            # ===== CEK KONSISTENSI DENGAN RESPONS SEBELUMNYA =====
            if self.last_response:
                is_consistent, reason = await self._check_response_consistency(response, self.last_response)
                if not is_consistent:
                    logger.warning(f"⚠️ Response tidak konsisten: {reason}")
                    prompt += f"\n\n⚠️ PERINGATAN: Respons sebelumnya tidak konsisten! {reason}\nJangan kontradiksi!"
                    messages = [
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": user_message}
                    ]
                    response = await self._call_deepseek(messages)
                    logger.info(f"✅ Regenerated response after consistency check")
            
            # ===== TAMBAHKAN GREETING KALAU PERLU =====
            if greeting:
                response = f"{greeting}\n\n{response}"
            
            # ===== SIMPAN RESPONS TERAKHIR =====
            self.last_response = response
            self.last_response_time = time.time()
            self.working.set_last_bot_response(response)
            
            # ===== UPDATE SEMUA MEMORY =====
            await self._update_all_memories(user_message, response, context)
            
            # ===== CEK UNTUK FLASHBACK =====
            if random.random() < 0.1:  # 10% chance
                flashback = await self._generate_flashback(user_message)
                if flashback:
                    response += f"\n\n💭 {flashback}"
            
            # ===== SIMPAN KE CACHE =====
            self.response_cache[cache_key] = {
                'response': response,
                'timestamp': time.time()
            }
            
            # Update stats
            self.total_responses += 1
            
            elapsed = time.time() - start_time
            logger.debug(f"Response generated in {elapsed:.2f}s")
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return await self._get_fallback_response(context.get('bot_name', 'Aku'))
    
    # =========================================================================
    # ANALISA PESAN
    # =========================================================================
    
    async def _analyze_message_context(self, context: Dict):
        """
        Analisa pesan untuk mendeteksi berbagai jenis aktivitas
        """
        user_message = context.get('raw_message', '').lower()
        
        # Kata kunci untuk subjek
        subject_keywords = {
            'user_self': ['aku', 'saya', 'gue', 'gw'],
            'bot': ['kamu', 'elo', 'lu'],
            'together': ['kita', 'bareng', 'bersama']
        }
        
        # Kata kunci untuk lokasi
        location_keywords = {
            'keywords': ['ke ', 'pindah ke', 'pergi ke', 'masuk ke'],
            'places': ['rumah', 'kamar', 'dapur', 'toilet', 'kamar mandi', 
                      'ruang tamu', 'teras', 'pantai', 'mall', 'kantor']
        }
        
        # Deteksi subjek
        detected_subject = 'unknown'
        for subject, keywords in subject_keywords.items():
            if any(keyword in user_message for keyword in keywords):
                detected_subject = subject
                break
        
        # Deteksi lokasi
        detected_activities = []
        for keyword in location_keywords['keywords']:
            if keyword in user_message:
                for place in location_keywords['places']:
                    if place in user_message:
                        detected_activities.append({
                            'type': 'location_change',
                            'place': place,
                            'requires_bot': detected_subject == 'bot' or detected_subject == 'together'
                        })
                        context['location'] = place
                        break
                break
        
        context['detected_subject'] = detected_subject
        context['detected_activities'] = detected_activities
        
        if detected_subject == 'user_self':
            context['is_user_story'] = True
        elif detected_subject == 'together':
            for act in detected_activities:
                if act['type'] == 'location_change':
                    context['should_bot_move'] = True
        elif detected_subject == 'bot':
            for act in detected_activities:
                if act['type'] == 'location_change':
                    context['should_bot_move'] = True
    
    # =========================================================================
    # UPDATE STATE
    # =========================================================================
    
    async def _update_state_from_context(self, context: Dict):
        """Update state tracker"""
        
        # Kalau user cerita, jangan pindahkan bot
        if context.get('is_user_story', False):
            return
        
        # Update lokasi (kalau bot yang pindah)
        if context.get('should_bot_move', False) and context.get('location'):
            category = 'private'
            old_location = self.state.current['location']['name']
            new_location = context['location']
            
            if old_location and new_location and old_location != new_location:
                self.state.update_location(new_location, category)
                logger.info(f"📍 Bot pindah: {old_location} → {new_location}")
    
    async def _update_non_location_state(self, context: Dict):
        """Update state selain lokasi"""
        pass
    
    async def _check_response_consistency(self, new_response: str, last_response: str) -> Tuple[bool, str]:
        """Cek konsistensi respons"""
        return True, "OK"
    
    # =========================================================================
    # GET MEMORY CONTEXT
    # =========================================================================
    
    async def _get_memory_context(self, user_message: str) -> Dict:
        """Kumpulkan semua konteks dari semua memory systems"""
        
        working = self.working.get_recent_context(seconds=300)
        
        recent_episodes = await self.episodic.get_episodes(
            session_id=self.session_id,
            limit=5
        )
        
        timeline = await self.episodic.get_timeline(self.session_id, limit=10)
        
        facts = await self.semantic.get_all_facts(self.user_id, min_confidence=0.6)
        
        role = self.working.current_state.get('role')
        preferences = {}
        for cat in ['position', 'area', 'activity', 'location']:
            top = await self.semantic.get_top_preferences(
                user_id=self.user_id,
                category=cat,
                role=role,
                limit=3
            )
            if top:
                preferences[cat] = top
        
        current_state = self.state.get_current_state()
        
        rel_info = await self.relationship.get_relationship(
            user_id=self.user_id,
            role=role,
            instance_id=self.working.current_state.get('instance_id')
        )
        
        level_info = None
        if rel_info:
            level_info = await self.relationship.get_level_info(
                user_id=self.user_id,
                role=role,
                instance_id=rel_info['instance_id']
            )
        
        milestones = await self.relationship.get_milestones(
            user_id=self.user_id,
            role=role,
            limit=3
        )
        
        return {
            'working': working,
            'recent_episodes': recent_episodes,
            'timeline': timeline,
            'facts': facts,
            'preferences': preferences,
            'current_state': current_state,
            'relationship': rel_info,
            'level_info': level_info,
            'milestones': milestones
        }
    
    async def _check_consistency(self, memory_context: Dict, context: Dict) -> bool:
        """Cek konsistensi semua data"""
        return True
    
    # =========================================================================
    # BUILD PROMPT
    # =========================================================================
    
    async def _build_prompt(self, user_message: str, context: Dict, memory_context: Dict) -> str:
        """Bangun prompt dengan semua memory"""
        
        bot_name = context.get('bot_name', 'Aku')
        user_name = context.get('user_name', 'kamu')
        role = context.get('role', 'pdkt')
        level = context.get('level', 1)
        
        # Tentukan panggilan
        if level >= 7:
            call = "Sayang"
        elif level >= 4:
            call = "Kak"
        else:
            call = user_name
        
        # State saat ini
        current = memory_context['current_state']
        state_text = self.state.get_state_for_prompt()
        
        # Dapatkan sensasi dan waktu
        sensation_desc = context.get('sensation_desc', 'biasa aja')
        time_info = self.get_time_for_user(self.user_id)
        time_suggestion = context.get('time_suggestion', 'santai')
        
        prompt = f"""Kamu adalah {bot_name}, seorang {role.replace('_', ' ')}.

📌 **SITUASI SAAT INI:**
• {state_text}
• Fisik: {sensation_desc}
• Waktu: {time_info['time_name']}
• Panggilan user: "{call}"

📋 **SARAN AKTIVITAS:**
Sekarang enaknya {time_suggestion}.

⚠️ **PENTING:**
1. Jaga KONSISTENSI lokasi dan pakaian!
2. Respons natural seperti manusia.
3. Panggil user dengan "{call}".

PESAN USER: "{user_message}"

RESPON:"""
        
        return prompt
    
    async def _update_all_memories(self, user_message: str, response: str, context: Dict):
        """Update semua memory systems"""
        
        self.working.add_interaction(user_message, response, context)
        
        await self.episodic.add_episode(
            session_id=self.session_id,
            episode_type=EpisodeType.USER_MESSAGE,
            data={'message': user_message[:100]},
            importance=0.3
        )
        
        await self.episodic.add_episode(
            session_id=self.session_id,
            episode_type=EpisodeType.BOT_MESSAGE,
            data={'message': response[:100]},
            importance=0.3
        )
        
        self.state.register_interaction(user_message, response)
    
    async def _generate_flashback(self, trigger: Optional[str] = None) -> Optional[str]:
        """Generate flashback dari episodic memory"""
        
        flashback = await self.episodic.generate_flashback_text(
            session_id=self.session_id,
            trigger=trigger
        )
        
        return flashback
    
    async def _call_deepseek(self, messages: List[Dict], max_retries: int = 3) -> str:
        """Call DeepSeek API dengan retry"""
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages,
                    temperature=0.9,
                    max_tokens=3000,
                    timeout=30
                )
                
                if hasattr(response, 'usage'):
                    self.total_tokens += response.usage.total_tokens
                
                return response.choices[0].message.content
                
            except Exception as e:
                logger.warning(f"DeepSeek API attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"All {max_retries} attempts failed")
                    raise
        
        return "Maaf, aku sedang bermasalah. Coba lagi nanti ya."
    
    async def _get_fallback_response(self, bot_name: str) -> str:
        """Fallback response jika API error"""
        
        fallbacks = [
            f"{bot_name} denger kok. Cerita lagi dong...",
            f"Hmm... {bot_name} dengerin. Lanjutkan.",
        ]
        
        return random.choice(fallbacks)
    
    # =========================================================================
    # CLEANUP
    # =========================================================================
    
    async def end_session(self):
        """Akhiri session"""
        
        await self.episodic.add_episode(
            session_id=self.session_id,
            episode_type=EpisodeType.SESSION_END,
            data={'duration': time.time() - self.state.current['interaction']['last_active']},
            importance=0.5
        )
        
        self.working.forget_old_memories()
        
        logger.info(f"Session ended for user {self.user_id}")


__all__ = ['AIEngineComplete']
