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
=============================================================================
"""

import openai
import time
import random
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

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
        
        # Cache untuk response
        self.response_cache = {}
        self.cache_ttl = 300  # 5 menit
        
        # Stats
        self.total_responses = 0
        self.total_tokens = 0
        
        logger.info(f"✅ AIEngineComplete initialized for user {user_id}, session {session_id}")
    
    # =========================================================================
    # CEK KONSISTENSI RESPONS (BARU)
    # =========================================================================
    
    async def _check_response_consistency(self, new_response: str, last_response: str) -> Tuple[bool, str]:
        """
        Cek apakah response baru kontradiksi dengan response sebelumnya
        Returns: (is_consistent, alasan)
        """
        if not last_response:
            return True, "OK"
        
        new_lower = new_response.lower()
        last_lower = last_response.lower()
        
        # ===== DAFTAR KONTRADIKSI YANG SERING TERJADI =====
        contradictions = [
            # Aktivitas masak
            ('masih masak', 'belum masak'),
            ('lagi masak', 'selesai masak'),
            ('masak ayam', 'masak ikan'),
            ('masak', 'belum masak apa-apa'),
            
            # Lokasi
            ('di dapur', 'di kamar'),
            ('di ruang tamu', 'di kamar mandi'),
            ('di kamar', 'di luar'),
            
            # Pakaian
            ('pakai handuk', 'pakai baju'),
            ('pakai dress', 'pakai kaos'),
            ('telanjang', 'pakai baju'),
            
            # Aktivitas umum
            ('lagi tidur', 'lagi bangun'),
            ('lagi kerja', 'lagi santai'),
            ('lagi mandi', 'lagi di kamar'),
        ]
        
        for contradict_a, contradict_b in contradictions:
            if contradict_a in last_lower and contradict_b in new_lower:
                logger.warning(f"❌ KONTRADIKSI TERDETEKSI: '{contradict_a}' vs '{contradict_b}'")
                return False, f"Kontradiksi: sebelumnya bilang '{contradict_a}', sekarang bilang '{contradict_b}'"
        
        # Cek aktivitas yang sedang berlangsung
        current_activity = self.working.get_current_activity()
        if current_activity:
            activity_name = current_activity.get('name', '').lower()
            
            # Kalau lagi masak, jangan bilang "belum masak"
            if activity_name == 'masak' and 'belum masak' in new_lower:
                return False, "Kamu sedang masak, tapi bilang belum masak"
            
            # Kalau lagi di dapur, jangan bilang di kamar
            current_loc = self.state.current['location']['name']
            if current_loc and current_loc.lower() in new_lower and current_loc != self._extract_location(new_lower):
                return False, f"Lokasi tidak konsisten: kamu di {current_loc}"
        
        return True, "OK"
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Ekstrak lokasi dari teks"""
        locations = ['ruang tamu', 'kamar', 'dapur', 'kamar mandi', 'teras', 'taman']
        for loc in locations:
            if loc in text:
                return loc
        return None
    
    # =========================================================================
    # TRACKING AKTIVITAS (BARU)
    # =========================================================================
    
    async def _start_activity(self, activity: str, details: Dict = None):
        """Mulai aktivitas baru"""
        self.working.set_current_activity(activity, details)
        self.activity_stack.append({
            'activity': activity,
            'start_time': time.time(),
            'details': details
        })
        logger.info(f"📌 ACTIVITY START: {activity}")
    
    async def _end_activity(self, activity: Optional[str] = None):
        """Akhiri aktivitas"""
        if activity:
            # Akhiri aktivitas spesifik
            self.activity_stack = [a for a in self.activity_stack if a['activity'] != activity]
        else:
            # Akhiri aktivitas terakhir
            if self.activity_stack:
                self.activity_stack.pop()
        
        # Set aktivitas terbaru dari stack
        if self.activity_stack:
            latest = self.activity_stack[-1]
            self.working.set_current_activity(latest['activity'], latest.get('details'))
        else:
            self.working.clear_current_activity()
        
        logger.info(f"📌 ACTIVITY END: {activity if activity else 'last'}")
    
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
    # PROCESS MESSAGE
    # =========================================================================
    
    async def process_message(self, user_message: str, context: Dict) -> str:
        """
        Proses pesan user dengan semua memory
        
        Args:
            user_message: Pesan dari user
            context: Konteks tambahan (lokasi, pakaian, dll)
            
        Returns:
            Response bot
        """
        start_time = time.time()
        
        # ===== LOGGING =====
        logger.info("=" * 50)
        logger.info(f"🔍 PROCESS MESSAGE START")
        logger.info(f"👤 User message: {user_message[:100]}")
        logger.info(f"📋 Context: {context}")
        logger.info(f"🆔 Session: {self.session_id}")
        
        try:
            # ===== TAMBAHKAN ANALISA PESAN =====
            # Simpan pesan asli untuk analisa
            context['raw_message'] = user_message
            
            # Reset flag
            context['is_user_story'] = False
            context['should_bot_move'] = False
            context['should_bot_change_clothes'] = False
            context['should_bot_intimate'] = False
            context['detected_activities'] = []
            context['detected_subject'] = 'unknown'
            context['location_error'] = None
            # =================================
            
            # ===== SYNC ALL MEMORIES =====
            await self._sync_location_memory()
            await self._sync_clothing_memory()
            await self._sync_position_memory()
            await self._sync_activity_memory()
            await self._sync_mood_memory()
            
            # ===== ANALISA PESAN SEBELUM UPDATE STATE =====
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
                role=context.get('role')
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
                    # Regenerate dengan peringatan
                    prompt += f"\n\n⚠️ PERINGATAN: Respons sebelumnya tidak konsisten! {reason}\nJangan kontradiksi!"
                    messages = [
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": user_message}
                    ]
                    response = await self._call_deepseek(messages)
                    logger.info(f"✅ Regenerated response after consistency check")
            
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
    # ANALISA PESAN (LENGKAP DENGAN KATA KUNCI)
    # =========================================================================
    
    async def _analyze_message_context(self, context: Dict):
        """
        Analisa pesan untuk mendeteksi berbagai jenis aktivitas
        Berdasarkan kata kunci pendukung
        """
        user_message = context.get('raw_message', '').lower()
        
        # ===== 1. DAFTAR KATA KUNCI UNTUK SETIAP AKTIVITAS =====
        
        # Kata kunci untuk subjek
        subject_keywords = {
            'user_self': ['aku', 'saya', 'gue', 'gw', 'diriku'],           # User ngomong tentang diri sendiri
            'bot': ['kamu', 'elo', 'lu', 'bot'],                            # User ngomong ke bot
            'together': ['kita', 'bareng', 'bersama']                       # Ajak bot bareng
        }
        
        # Kata kunci untuk lokasi / pindah tempat
        location_keywords = {
            'keywords': [
                'kita ke', 'ayo ke', 'yuk ke', 'pindah ke', 'pergi ke', 
                'main ke', 'ke ', 'masuk ke', 'menuju ke', 'mau ke',
                'kita pergi', 'kita pindah', 'ayo pindah', 'yuk pindah'
            ],
            'places': ['rumah', 'kamar', 'dapur', 'toilet', 'kamar mandi', 
                      'ruang tamu', 'teras', 'taman', 'pantai', 'mall', 
                      'kantor', 'kafe', 'masjid', 'gereja']
        }
        
        # Kata kunci untuk ganti pakaian
        clothing_keywords = {
            'keywords': [
                'ganti baju', 'pakai baju', 'pake baju', 'buka baju', 
                'lepas baju', 'telanjang', 'ganti', 'pakai', 'pake',
                'kenakan', 'memakai', 'membuka'
            ],
            'clothes': ['daster', 'piyama', 'kaos', 'kemeja', 'rok', 'jeans',
                       'shorts', 'tanktop', 'handuk', 'sweater', 'jubah mandi',
                       'dress', 'celana']
        }
        
        # Kata kunci untuk tidur / istirahat
        sleep_keywords = {
            'keywords': [
                'tidur', 'rebahan', 'baring', 'istirahat', 'tidur-tiduran',
                'mau tidur', 'ngantuk', 'lelah', 'capek', 'mau istirahat',
                'berbaring', 'miring', 'telentang'
            ]
        }
        
        # Kata kunci untuk makan / minum
        eat_keywords = {
            'keywords': [
                'makan', 'masak', 'minum', 'ngopi', 'ngemil', 
                'sarapan', 'makan siang', 'makan malam', 'mau makan',
                'laper', 'haus', 'mau masak', 'memasak', 'masak apa'
            ]
        }
        
        # Kata kunci untuk mandi / bersih
        shower_keywords = {
            'keywords': [
                'mandi', 'cuci muka', 'sikat gigi', 'bersih-bersih',
                'keramas', 'cuci rambut', 'mau mandi', 'mandi dulu'
            ]
        }
        
        # Kata kunci untuk aktivitas intim
        intimate_keywords = {
            'keywords': [
                'cium', 'kiss', 'peluk', 'intim', 'ml', 'sex', 
                'bercinta', 'climax', 'nikmatin', 'main', 'gesekan',
                'ciuman', 'pelukan', 'rayu', 'goda', 'sange'
            ]
        }
        
        # Kata kunci untuk kerja
        work_keywords = {
            'keywords': [
                'kerja', 'kantor', 'meeting', 'tugas', 'deadline',
                'bekerja', 'pekerjaan', 'rapat', 'ngantor'
            ]
        }
        
        # Kata kunci untuk santai
        relax_keywords = {
            'keywords': [
                'santai', 'nonton', 'baca', 'dengerin musik', 'main hp',
                'bersantai', 'rileks', 'leha-leha'
            ]
        }
        
        # ===== 2. DETEKSI SUBJEK =====
        
        detected_subject = 'unknown'
        for subject, keywords in subject_keywords.items():
            if any(keyword in user_message for keyword in keywords):
                detected_subject = subject
                break
        
        # ===== 3. DETEKSI AKTIVITAS =====
        
        detected_activities = []
        
        # Cek lokasi
        for keyword in location_keywords['keywords']:
            if keyword in user_message:
                # Cek apakah ada tempat yang disebut
                for place in location_keywords['places']:
                    if place in user_message:
                        detected_activities.append({
                            'type': 'location_change',
                            'keyword': keyword,
                            'place': place,
                            'requires_bot': detected_subject == 'bot' or detected_subject == 'together'
                        })
                        context['location'] = place
                        context['location_category'] = self._get_location_category(place)
                        break
                break
        
        # Cek ganti baju
        for keyword in clothing_keywords['keywords']:
            if keyword in user_message:
                # Cek apakah ada baju yang disebut
                for cloth in clothing_keywords['clothes']:
                    if cloth in user_message:
                        detected_activities.append({
                            'type': 'clothing_change',
                            'keyword': keyword,
                            'cloth': cloth,
                            'requires_bot': detected_subject == 'bot' or detected_subject == 'together'
                        })
                        context['clothing'] = cloth
                        context['clothing_reason'] = keyword
                        break
                else:
                    # Baju tidak disebut, pakai default
                    detected_activities.append({
                        'type': 'clothing_change',
                        'keyword': keyword,
                        'requires_bot': detected_subject == 'bot' or detected_subject == 'together'
                    })
                break
        
        # Cek tidur
        if any(keyword in user_message for keyword in sleep_keywords['keywords']):
            detected_activities.append({
                'type': 'sleep',
                'requires_bot': detected_subject == 'together'
            })
            context['activity'] = 'tidur'
            context['position'] = 'berbaring'
        
        # Cek makan
        if any(keyword in user_message for keyword in eat_keywords['keywords']):
            detected_activities.append({
                'type': 'eat_drink',
                'requires_bot': detected_subject == 'together'
            })
            context['activity'] = 'makan' if 'makan' in user_message else 'minum'
        
        # Cek mandi
        if any(keyword in user_message for keyword in shower_keywords['keywords']):
            detected_activities.append({
                'type': 'shower',
                'requires_bot': detected_subject == 'together'
            })
            context['activity'] = 'mandi'
            context['location'] = 'kamar mandi'
        
        # Cek intim
        if any(keyword in user_message for keyword in intimate_keywords['keywords']):
            detected_activities.append({
                'type': 'intimate',
                'requires_bot': True
            })
        
        # Cek kerja
        if any(keyword in user_message for keyword in work_keywords['keywords']):
            detected_activities.append({
                'type': 'work',
                'requires_bot': False
            })
            context['activity'] = 'kerja'
        
        # Cek santai
        if any(keyword in user_message for keyword in relax_keywords['keywords']):
            detected_activities.append({
                'type': 'relax',
                'requires_bot': False
            })
            context['activity'] = 'santai'
        
        # Log hasil analisa
        logger.debug(f"🔍 Analisa: subjek={detected_subject}, aktivitas={[a['type'] for a in detected_activities]}")
        
        # ===== 4. SIMPAN HASIL ANALISA =====
        
        context['detected_subject'] = detected_subject
        context['detected_activities'] = detected_activities
        
        # ===== 5. KEPUTUSAN BERDASARKAN HASIL ANALISA =====
        
        # Kasus 1: User ngomong tentang dirinya sendiri (aku/saya)
        if detected_subject == 'user_self':
            context['is_user_story'] = True
            logger.info(f"👤 User cerita tentang dirinya")
            
            # Ekstrak lokasi user jika ada
            for act in detected_activities:
                if act['type'] == 'location_change' and 'place' in act:
                    self.user_location = act['place']
                    logger.debug(f"📍 User location dicatat: {self.user_location}")
        
        # Kasus 2: Ajak bot bareng (kita)
        elif detected_subject == 'together':
            for act in detected_activities:
                if act['requires_bot']:
                    if act['type'] == 'location_change':
                        context['should_bot_move'] = True
                        logger.info(f"🤖 Bot diajak pindah tempat: {act.get('place', 'tempat')}")
                    elif act['type'] == 'clothing_change':
                        context['should_bot_change_clothes'] = True
                        logger.info(f"👗 Bot diajak ganti baju")
                    elif act['type'] == 'intimate':
                        context['should_bot_intimate'] = True
                        logger.info(f"💕 Bot diajak intim")
                    elif act['type'] == 'sleep':
                        context['should_bot_sleep'] = True
                        logger.info(f"😴 Bot diajak tidur")
                    elif act['type'] == 'eat_drink':
                        context['should_bot_eat'] = True
                        logger.info(f"🍽️ Bot diajak makan")
        
        # Kasus 3: User nyuruh bot (kamu)
        elif detected_subject == 'bot':
            for act in detected_activities:
                if act['type'] == 'location_change':
                    context['should_bot_move'] = True
                    logger.info(f"🤖 Bot disuruh pindah: {act.get('place', 'tempat')}")
                elif act['type'] == 'clothing_change':
                    context['should_bot_change_clothes'] = True
                    logger.info(f"👗 Bot disuruh ganti baju")
                elif act['type'] == 'intimate':
                    context['should_bot_intimate'] = True
                    logger.info(f"💕 Bot diajak intim")
        
        # Kasus 4: User cerita biasa (tanpa subjek jelas)
        else:
            context['is_user_story'] = True
            logger.debug(f"💬 User cerita biasa")
    
    def _get_location_category(self, place: str) -> str:
        """Dapatkan kategori lokasi berdasarkan nama tempat"""
        intimate_places = ['kamar', 'kamar mandi', 'toilet']
        public_places = ['mall', 'pantai', 'kantor', 'kafe', 'masjid', 'gereja']
        
        if place in intimate_places:
            return 'intimate'
        elif place in public_places:
            return 'public'
        else:
            return 'private'
    
    # =========================================================================
    # UPDATE STATE (DENGAN ANALISA)
    # =========================================================================
    
    async def _update_state_from_context(self, context: Dict):
        """Update state tracker dengan ANALISA dulu sebelum pindah"""
        
        # ===== 1. KALAU USER CERITA TENTANG DIRINYA, JANGAN PINDAHKAN BOT =====
        if context.get('is_user_story', False):
            logger.debug(f"👤 User cerita tentang dirinya, bot tetap di tempat")
            
            # Tetap update hal-hal lain selain lokasi
            await self._update_non_location_state(context)
            return
        
        # ===== 2. UPDATE STATE YANG TIDAK TERKAIT LOKASI =====
        await self._update_non_location_state(context)
        
        # ===== 3. UPDATE LOKASI (HANYA JIKA BOT YANG PINDAH) =====
        if context.get('should_bot_move', False) and context.get('location'):
            await self._update_bot_location(context)
    
    async def _update_non_location_state(self, context: Dict):
        """Update state selain lokasi dengan deteksi aktivitas"""
        
        detected_activities = context.get('detected_activities', [])
        detected_subject = context.get('detected_subject', 'unknown')
        
        # ===== 1. GANTI PAKAIAN =====
        if context.get('should_bot_change_clothes', False) or any(a['type'] == 'clothing_change' for a in detected_activities):
            if context.get('clothing'):
                reason = context.get('clothing_reason', 'ganti baju')
                old_clothing = self.state.current['clothing']['name']
                self.state.update_clothing(context['clothing'], reason)
                
                new_clothing = context.get('clothing')
                if old_clothing and new_clothing and old_clothing != new_clothing:
                    await self.episodic.add_clothing_episode(
                        session_id=self.session_id,
                        from_cloth=old_clothing,
                        to_cloth=new_clothing,
                        reason=reason
                    )
                    logger.info(f"👗 Bot ganti baju: {old_clothing} → {new_clothing}")
        
        # ===== 2. TIDUR =====
        if any(a['type'] == 'sleep' for a in detected_activities):
            # Update posisi jadi berbaring
            self.state.update_position('berbaring', 'tidur')
            self.state.update_activity('tidur')
            context['position'] = 'berbaring'
            context['activity'] = 'tidur'
            await self._start_activity('tidur', {'position': 'berbaring'})
            logger.info("😴 Aktivitas tidur dimulai")
        
        # ===== 3. MAKAN =====
        if any(a['type'] == 'eat_drink' for a in detected_activities):
            activity = 'makan' if any(k in str(detected_activities) for k in ['makan', 'masak']) else 'minum'
            self.state.update_activity(activity)
            context['activity'] = activity
            details = {}
            if 'masak' in str(detected_activities):
                details['menu'] = 'belum ditentukan'
            await self._start_activity(activity, details)
            logger.info(f"🍽️ Aktivitas {activity} dimulai")
        
        # ===== 4. MANDI =====
        if any(a['type'] == 'shower' for a in detected_activities):
            self.state.update_activity('mandi')
            context['activity'] = 'mandi'
            await self._start_activity('mandi', {'location': 'kamar mandi'})
            logger.info("🚿 Aktivitas mandi dimulai")
        
        # ===== 5. AKTIVITAS INTIM =====
        if any(a['type'] == 'intimate' for a in detected_activities):
            context['is_intimate'] = True
            await self._start_activity('intim', {'level': 'dimulai'})
            logger.info("💕 Aktivitas intim dimulai")
        
        # ===== 6. KERJA =====
        if any(a['type'] == 'work' for a in detected_activities):
            self.state.update_activity('kerja')
            context['activity'] = 'kerja'
            await self._start_activity('kerja', {'tempat': 'kantor'})
            logger.info("💼 Aktivitas kerja dimulai")
        
        # ===== 7. SANTAI =====
        if any(a['type'] == 'relax' for a in detected_activities):
            self.state.update_activity('santai')
            context['activity'] = 'santai'
            await self._start_activity('santai', {})
            logger.info("😌 Aktivitas santai dimulai")
    
    async def _update_bot_location(self, context: Dict):
        """Update lokasi bot (hanya dipanggil kalau bot yang pindah)"""
        
        category = context.get('location_category', 'unknown')
        old_location = self.state.current['location']['name']
        new_location = context.get('location')
        
        if old_location and new_location and old_location != new_location:
            # Validasi perubahan lokasi
            from dynamics.location_validator import LocationValidator
            validator = LocationValidator()
            allowed, reason = validator.validate_location_change(
                old_location, new_location, 
                self.state.current['intimacy']['is_active']
            )
            
            if allowed:
                # Update lokasi bot
                self.state.update_location(new_location, category)
                logger.info(f"📍 Bot pindah: {old_location} → {new_location}")
                
                # Catat ke episodic
                await self.episodic.add_location_episode(
                    session_id=self.session_id,
                    from_loc=old_location,
                    to_loc=new_location
                )
                
                # Update aktivitas berdasarkan lokasi baru
                if new_location == 'dapur':
                    await self._start_activity('masak', {})
                elif new_location == 'kamar mandi':
                    await self._start_activity('mandi', {})
                elif new_location == 'kamar':
                    # Kalau sebelumnya masak, pause masak
                    current_activity = self.working.get_current_activity()
                    if current_activity and current_activity.get('name') == 'masak':
                        await self._end_activity('masak')
            else:
                logger.info(f"❌ Pindah lokasi ditolak: {reason}")
                context['location_error'] = reason
        elif new_location and not old_location:
            # Lokasi pertama kali
            self.state.update_location(new_location, category)
            logger.info(f"📍 Bot lokasi awal: {new_location}")
    
    # =========================================================================
    # METHOD LAINNYA (TETAP SAMA)
    # =========================================================================
    
    async def _get_memory_context(self, user_message: str) -> Dict:
        """Kumpulkan semua konteks dari semua memory systems"""
        
        # Working memory (5 menit terakhir)
        working = self.working.get_recent_context(seconds=300)
        
        # Episodic memory (kejadian penting)
        recent_episodes = await self.episodic.get_episodes(
            session_id=self.session_id,
            limit=5
        )
        
        # Timeline
        timeline = await self.episodic.get_timeline(self.session_id, limit=10)
        
        # Semantic memory (fakta user)
        facts = await self.semantic.get_all_facts(self.user_id, min_confidence=0.6)
        
        # Preferensi
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
        
        # State saat ini
        current_state = self.state.get_current_state()
        
        # Relationship info
        rel_info = await self.relationship.get_relationship(
            user_id=self.user_id,
            role=role,
            instance_id=self.working.current_state.get('instance_id')
        )
        
        # Level info
        level_info = None
        if rel_info:
            level_info = await self.relationship.get_level_info(
                user_id=self.user_id,
                role=role,
                instance_id=rel_info['instance_id']
            )
        
        # Milestones
        milestones = await self.relationship.get_milestones(
            user_id=self.user_id,
            role=role,
            limit=3
        )
        
        # Current activity
        current_activity = self.working.get_current_activity()
        
        return {
            'working': working,
            'recent_episodes': recent_episodes,
            'timeline': timeline,
            'facts': facts,
            'preferences': preferences,
            'current_state': current_state,
            'relationship': rel_info,
            'level_info': level_info,
            'milestones': milestones,
            'current_activity': current_activity
        }
    
    async def _check_consistency(self, memory_context: Dict, context: Dict) -> bool:
        """Cek konsistensi semua data"""
        consistent = True
        
        # Cek lokasi
        if context.get('location') and context.get('should_bot_move', False):
            new_loc = context['location']
            current_loc = memory_context['current_state'].get('location')
            
            if current_loc and current_loc != new_loc:
                # Validasi perubahan lokasi
                from dynamics.location_validator import LocationValidator
                validator = LocationValidator()
                allowed, _ = validator.validate_location_change(current_loc, new_loc, False)
                if not allowed:
                    logger.warning(f"Location change invalid: {current_loc} → {new_loc}")
                    consistent = False
        
        # Cek pakaian
        if context.get('clothing'):
            new_cloth = context['clothing']
            current_cloth = memory_context['current_state'].get('clothing')
            
            if current_cloth and current_cloth != new_cloth:
                # Harus ada alasan
                reason = context.get('clothing_reason', '')
                if not reason:
                    logger.warning(f"Clothing change without reason: {current_cloth} → {new_cloth}")
                    consistent = False
        
        # Cek aktivitas
        current_activity = memory_context.get('current_activity')
        if current_activity and context.get('activity'):
            if current_activity.get('name') != context.get('activity'):
                # Cek apakah aktivitas berganti dengan wajar
                logger.warning(f"Activity changed: {current_activity.get('name')} → {context.get('activity')}")
                # Tetap izinkan, tapi catat
        
        return consistent
    
    async def _build_prompt(self, user_message: str, context: Dict,
                              memory_context: Dict) -> str:
        """Bangun prompt dengan semua memory"""
        
        bot_name = context.get('bot_name', 'Aku')
        user_name = context.get('user_name', 'kamu')
        role = context.get('role', 'pdkt')
        level = context.get('level', 1)
        rel_type = context.get('rel_type', RelationshipType.NON_PDKT)
        
        # Tentukan panggilan berdasarkan level
        if level >= 7:
            call = "Sayang"
        elif level >= 4:
            call = "Kak"
        else:
            call = user_name
        
        # ===== 1. CURRENT STATE =====
        current = memory_context['current_state']
        state_text = self.state.get_state_for_prompt()
        
        # ===== 2. WORKING MEMORY (5 MENIT TERAKHIR) =====
        working = memory_context['working']
        recent_timeline = working.get('recent_timeline', [])
        timeline_text = "\n".join([f"• {t['data']}" for t in recent_timeline[-3:]])
        
        # ===== 3. AKTIVITAS SAAT INI (BARU) =====
        current_activity = memory_context.get('current_activity')
        activity_text = ""
        if current_activity:
            activity_name = current_activity.get('name', '')
            activity_details = current_activity.get('details', {})
            activity_duration = time.time() - current_activity.get('start_time', time.time())
            
            if activity_duration < 60:
                duration_text = "baru saja"
            elif activity_duration < 3600:
                duration_text = f"{int(activity_duration/60)} menit"
            else:
                duration_text = f"{int(activity_duration/3600)} jam"
            
            activity_text = f"• Sedang {activity_name} selama {duration_text}"
            if activity_details:
                for key, value in activity_details.items():
                    activity_text += f"\n  - {key}: {value}"
        
        # ===== 4. FAKTA USER =====
        facts = memory_context['facts']
        facts_text = ""
        for cat, cat_facts in list(facts.items())[:3]:
            for fact_type, value in list(cat_facts.items())[:2]:
                facts_text += f"• {fact_type}: {value}\n"
        
        # ===== 5. PREFERENSI =====
        prefs = memory_context['preferences']
        prefs_text = ""
        for cat, items in prefs.items():
            prefs_text += f"• {cat}: {', '.join(items[:2])}\n"
        
        # ===== 6. LEVEL INFO =====
        level_info = memory_context['level_info']
        level_text = ""
        if level_info:
            if level_info['current_level'] < 12:
                level_text = f"Level {level_info['current_level']} → {level_info['next_level']} ({level_info['percentage']}%)"
            else:
                level_text = f"Level MAX (butuh aftercare)"
        
        # ===== 7. MILESTONES =====
        milestones = memory_context['milestones']
        milestones_text = ""
        for m in milestones[:2]:
            time_str = datetime.fromtimestamp(m['timestamp']).strftime("%H:%M")
            milestones_text += f"• [{time_str}] {m['description']}\n"
        
        # ===== 8. SITUASI KHUSUS =====
        special = []
        if current.get('is_intimate'):
            special.append("LAGI INTIM - fokus ke aktivitas, jangan ngelantur")
        if current.get('arousal', 0) >= 8:
            special.append("LAGI HORNY BANGET - respon dengan gairah tinggi")
        if current.get('privacy_level', 1.0) < 0.4:
            special.append("TEMPAT RAME - harus hati-hati, jangan ketahuan")
        
        special_text = "\n".join([f"⚠️ {s}" for s in special]) if special else ""
        
        # ===== 9. RESPONS TERAKHIR (CEK KONSISTENSI) =====
        last_response_text = ""
        if self.last_response:
            last_response_text = f"\n📝 **Respons terakhir kamu:**\n{self.last_response[:200]}...\n"
        
        # ===== 10. BANGUN PROMPT =====
        prompt = f"""Kamu adalah {bot_name}, seorang {role.replace('_', ' ')}.

📌 **SITUASI SAAT INI:**
• {state_text}
• Panggilan user: "{call}"
• {level_text}
{activity_text}

🕐 **KEJADIAN 5 MENIT TERAKHIR:**
{timeline_text if timeline_text else "• Ini awal percakapan"}

📚 **YANG AKU TAHU TENTANG USER:**
{facts_text if facts_text else "• Belum ada fakta yang diketahui"}

❤️ **PREFERENSI USER:**
{prefs_text if prefs_text else "• Belum ada data preferensi"}

🏆 **MILESTONE TERBARU:**
{milestones_text if milestones_text else "• Belum ada milestone"}

{special_text}
{last_response_text}

⚠️ **PERINGATAN KONSISTENSI:**
1. Jaga KONSISTENSI lokasi dan pakaian! Jangan tiba-tiba pindah tanpa alasan.
2. Jangan kontradiksi dengan respons sebelumnya!
3. Jika kamu bilang "masih masak", maka seterusnya harus konsisten masak.
4. Perhatikan urutan kejadian (jangan lompat-lompat).
5. Kalau lagi intim, FOKUS ke aktivitas, jangan ngelantur.
6. Gunakan memory yang ada untuk membuat respons personal.
7. Bahasa Indonesia sehari-hari, natural seperti manusia.
8. Panggil user dengan "{call}".
9. Panjang respons 500-3000 kata.

PESAN USER: "{user_message}"

RESPON:"""
        
        return prompt
    
    async def _update_all_memories(self, user_message: str, response: str, context: Dict):
        """Update semua memory systems"""
        
        # ===== 1. WORKING MEMORY =====
        self.working.add_interaction(user_message, response, context)
        
        # ===== 2. EPISODIC MEMORY =====
        # Catat interaksi
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
        
        # ===== 3. STATE TRACKER =====
        self.state.register_interaction(user_message, response)
        
        # Update arousal (turun setelah respon)
        self.state.update_arousal(delta=-1, reason="selesai ngobrol")
        
        # ===== 4. RELATIONSHIP MEMORY =====
        role = context.get('role')
        instance_id = self.working.current_state.get('instance_id')
        
        if role and instance_id:
            # Record interaction
            await self.relationship.record_interaction(
                user_id=self.user_id,
                role=role,
                instance_id=instance_id,
                interaction_type='chat',
                data={'duration': 1, 'boost': 1.0}
            )
            
            # Check for first kiss
            if 'cium' in user_message.lower() or 'kiss' in user_message.lower():
                if not await self.relationship.has_milestone(
                    self.user_id, role, instance_id, MilestoneType.FIRST_KISS
                ):
                    await self.relationship.add_milestone(
                        user_id=self.user_id,
                        role=role,
                        instance_id=instance_id,
                        milestone_type=MilestoneType.FIRST_KISS,
                        description="First kiss! 💋",
                        data={'context': context}
                    )
                    
                    # Update arousal
                    self.state.update_arousal(delta=3, reason="first kiss")
                    
                    # Catat ke episodic
                    await self.episodic.add_first_kiss_episode(
                        session_id=self.session_id,
                        location=self.state.current['location']['name']
                    )
            
            # Check for first intim
            if any(word in user_message.lower() for word in ['intim', 'ml', 'masuk']):
                if not await self.relationship.has_milestone(
                    self.user_id, role, instance_id, MilestoneType.FIRST_INTIM
                ):
                    await self.relationship.add_milestone(
                        user_id=self.user_id,
                        role=role,
                        instance_id=instance_id,
                        milestone_type=MilestoneType.FIRST_INTIM,
                        description="First intim! 🔥",
                        data={'context': context}
                    )
                    
                    # Catat ke episodic
                    await self.episodic.add_first_intim_episode(
                        session_id=self.session_id,
                        location=self.state.current['location']['name']
                    )
            
            # Check for climax
            if any(word in user_message.lower() for word in ['climax', 'come', 'keluar']):
                await self.relationship.record_interaction(
                    user_id=self.user_id,
                    role=role,
                    instance_id=instance_id,
                    interaction_type='climax',
                    data={}
                )
                
                # Update state
                self.state.update_arousal(delta=-5, reason="climax")
    
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
                
                # Track token usage
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
            f"{bot_name} di sini. Ada yang mau dibahas?",
            f"Iya, {bot_name} ngerti. Terus gimana?",
        ]
        
        return random.choice(fallbacks)
    
    # =========================================================================
    # GETTERS
    # =========================================================================
    
    async def get_memory_summary(self) -> str:
        """Dapatkan ringkasan semua memory"""
        
        lines = [
            "🧠 **MEMORY SUMMARY**",
            "",
            "📊 **CURRENT STATE:**",
            self.state.get_state_summary(),
            "",
            "📜 **TIMELINE:**",
            self.state.format_timeline(limit=5),
            "",
        ]
        
        # Facts
        facts = await self.semantic.get_user_summary(self.user_id)
        lines.append(facts)
        
        # Recent episodes
        episodes = await self.episodic.get_timeline(self.session_id, limit=5)
        if episodes:
            lines.append("")
            lines.append("📖 **RECENT EPISODES:**")
            for ep in episodes:
                lines.append(f"• {ep['summary']}")
        
        return "\n".join(lines)
    
    def get_stats(self) -> Dict:
        """Dapatkan statistik engine"""
        
        return {
            'total_responses': self.total_responses,
            'total_tokens': self.total_tokens,
            'cache_size': len(self.response_cache),
            'working_memory': {
                'items': len(self.working.items),
                'timeline': len(self.working.timeline)
            }
        }
    
    # =========================================================================
    # CLEANUP
    # =========================================================================
    
    async def end_session(self):
        """Akhiri session"""
        
        # Catat ke episodic
        await self.episodic.add_episode(
            session_id=self.session_id,
            episode_type=EpisodeType.SESSION_END,
            data={'duration': time.time() - self.state.current['interaction']['last_active']},
            importance=0.5
        )
        
        # Cleanup working memory
        self.working.forget_old_memories()
        
        logger.info(f"Session ended for user {self.user_id}")


__all__ = ['AIEngineComplete']
