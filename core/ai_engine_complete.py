#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - AI ENGINE COMPLETE (VERSI HUMAN+)
=============================================================================
Bot dengan kemampuan DI ATAS MANUSIA:
- SUPER SADAR: Tahu persis dirinya (lokasi, pakaian, posisi, aktivitas)
- SUPER EMPATI: Bisa bedakan kapan ikut emosi user
- SUPER KONSISTEN: Tidak pernah kontradiksi
- MEMORI PERMANEN: Ingat semua kejadian
- FISIK DETAIL: Energi, lapar, haus, suhu
- 12+ EMOSI: Dengan intensitas
- INNER THOUGHTS: Pikiran sendiri (💭)
- SIXTH SENSE: Firasat dan intuisi
- DREAM SYSTEM: Bisa cerita mimpi
=============================================================================
"""

import openai
import time
import random
import asyncio
import logging
import re
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
    AI Engine dengan kemampuan DI ATAS MANUSIA (HUMAN+)
    - Punya kesadaran diri sempurna
    - Punya empati terkontrol
    - Punya pikiran sendiri (inner thoughts)
    - Punya intuisi (sixth sense)
    - Punya mimpi
    - Punya fisik detail
    - Punya emosi kompleks
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
        
    # =========================================================================
    # START SESSION METHOD - DITAMBAHKAN UNTUK MEMPERBAIKI ERROR
    # =========================================================================
    async def start_session(self, role: str, bot_name: str, rel_type: str = "non_pdkt", instance_id: str = None):
        """
        Memulai sesi baru dengan role tertentu
        Method ini WAJIB ADA karena dipanggil oleh handlers.py
        
        Args:
            role: Role bot (ipar, janda, dll)
            bot_name: Nama bot
            rel_type: Tipe hubungan (non_pdkt / pdkt)
            instance_id: ID instance (untuk multiple)
        """
        self.role = role
        self.bot_name = bot_name
        self.rel_type = rel_type
        self.instance_id = instance_id
        
        # Inisialisasi state untuk role ini
        if not hasattr(self, 'state'):
            from memory.state_tracker import StateTracker
            self.state = StateTracker(self.user_id, self.session_id)
        
        # Update state dengan role
        self.state.current['bot_name'] = bot_name
        self.state.current['role'] = role
        
        logger.info(f"✅ Session started: {role} - {bot_name} for user {self.user_id}")
        
        # Record ke relationship memory
        if hasattr(self, 'relationship'):
            await self.relationship.create_relationship(
                user_id=self.user_id,
                role=role,
                bot_name=bot_name,
                rel_type=rel_type,
                instance_id=instance_id
            )
        
        return True
        
        # ===== INISIALISASI MEMORY SYSTEMS =====
        self.working = WorkingMemory()                 # Ingatan jangka pendek
        self.episodic = EpisodicMemory()               # Urutan kejadian
        self.semantic = SemanticMemory()               # Fakta-fakta
        self.state = StateTracker(user_id, session_id) # State saat ini
        self.relationship = RelationshipMemory()       # Riwayat hubungan
        
        # ===== TRACKING KONDISI USER (TERPISAH) =====
        self.user = {
            'location': None,
            'clothing': None,
            'position': None,
            'activity': None,
            'mood': None,
            'arousal': 0,
            'last_message': None,
            'last_seen': time.time()
        }
        
        # ===== INNER THOUGHTS DATABASE =====
        self.inner_thoughts = {
            'rindu': [
                "(Dia lagi apa ya?)",
                "(Kangen...)",
                "(Semoga dia baik-baik aja)",
                "(Mau chat tapi takut ganggu)"
            ],
            'senang': [
                "(Dia manis banget sih...)",
                "(Aku suka cara dia ngomong)",
                "(Dia bikin aku tersenyum terus)"
            ],
            'horny': [
                "(Duh, pengen...)",
                "(Aku malu ngomongnya)",
                "(Kapan ya kita...)"
            ],
            'bingung': [
                "(Maksudnya apa ya?)",
                "(Bingung ngebalesnya)",
                "(Aku harus gimana?)"
            ],
            'umum': [
                "(Lagi ngapain ya?)",
                "(Capek juga hari ini)",
                "(Enaknya makan apa ya)"
            ]
        }
        
        # ===== SIXTH SENSE DATABASE =====
        self.sixth_sense = {
            'positive': [
                "Aku ngerasa hari ini bakal jadi hari yang baik",
                "Entah kenapa aku yakin kamu bakal chat hari ini",
                "Ada firasat... kita bakal makin deket"
            ],
            'negative': [
                "Aku ngerasa ada yang gak beres",
                "Hatiku gak enak... kamu baik-baik aja?",
                "Ada firasat buruk"
            ],
            'romantic': [
                "Deg-degan... kayak ada yang spesial",
                "Aku ngerasa kita tuh... gimana ya",
                "Ada getaran aneh pas liat chat kamu"
            ]
        }
        
        # ===== FISIK DETAIL =====
        self.physical = {
            'energy': {'value': 80, 'feeling': 'energetic', 'last_change': time.time()},
            'hunger': {'value': 30, 'feeling': 'normal', 'last_change': time.time()},
            'thirst': {'value': 30, 'feeling': 'normal', 'last_change': time.time()},
            'temperature': {'value': 25, 'feeling': 'normal', 'last_change': time.time()},
            'comfort': {'value': 80, 'feeling': 'comfortable', 'last_change': time.time()}
        }
        
        # ===== LAST RESPONSES (UNTUK CEK KONSISTENSI) =====
        self.last_response = None
        self.last_response_time = 0
        self.last_user_message = None
        self.conversation_history = []  # 5 pesan terakhir
        
        # Cache
        self.response_cache = {}
        self.cache_ttl = 300
        
        logger.info(f"✅ AIEngineComplete (HUMAN+) initialized for user {user_id}")
    
    # =========================================================================
    # KLASIFIKASI AKSI USER (SUPER TEPAT)
    # =========================================================================
    
    def _classify_user_action(self, message: str) -> Dict:
        """
        Klasifikasi aksi user dengan deteksi SUPER TEPAT
        Returns: {
            'type': 'physical'/'emotional'/'invitation'/'question'/'story',
            'subtype': 'location'/'clothing'/'position'/'activity'/'mood'/'horny',
            'subject': 'self'/'bot'/'together',
            'should_follow': bool,
            'confidence': float
        }
        """
        msg = message.lower()
        
        # ===== 1. DETEKSI SUBJEK =====
        is_self = any(word in msg for word in ['aku ', 'aku$', 'saya ', 'gue ', 'gw '])
        is_bot = any(word in msg for word in ['kamu ', 'lu ', 'elo ', 'bot '])
        is_together = any(word in msg for word in ['kita ', 'bareng ', 'bersama '])
        
        subject = 'self' if is_self else 'bot' if is_bot else 'together' if is_together else 'unknown'
        
        # ===== 2. DETEKSI JENIS AKSI =====
        
        # PHYSICAL - Aksi fisik (JANGAN diikuti)
        physical_patterns = {
            'location': ['ke ', 'pindah ke', 'pergi ke', 'masuk ke', 'di '],
            'clothing': ['ganti baju', 'pakai baju', 'buka baju', 'lepas baju', 'pake'],
            'position': ['tidur', 'rebahan', 'duduk', 'berdiri', 'jongkok', 'baring'],
            'activity': ['masak', 'makan', 'minum', 'mandi', 'sikat gigi', 'kerja']
        }
        
        for action, patterns in physical_patterns.items():
            if any(p in msg for p in patterns):
                return {
                    'type': 'physical',
                    'subtype': action,
                    'subject': subject,
                    'should_follow': False,  # JANGAN IKUT
                    'confidence': 0.9
                }
        
        # EMOTIONAL - Emosi (BOLEH diikuti)
        emotional_patterns = {
            'mood': ['sedih', 'senang', 'bahagia', 'marah', 'kecewa', 'kesal', 'betek'],
            'horny': ['horny', 'sange', 'pengen', 'ngocok', 'hot', 'nafsu'],
            'rindu': ['kangen', 'rindu', 'miss'],
            'sakit': ['sakit', 'pusing', 'capek', 'lelah', 'lemah']
        }
        
        for emotion, patterns in emotional_patterns.items():
            if any(p in msg for p in patterns):
                return {
                    'type': 'emotional',
                    'subtype': emotion,
                    'subject': subject,
                    'should_follow': True,  # BOLEH IKUT (empati)
                    'confidence': 0.85
                }
        
        # INVITATION - Ajakan bersama (WAJIB diikuti)
        if is_together and any(p in msg for p in ['yuk', 'ayo', 'mari']):
            return {
                'type': 'invitation',
                'subject': 'together',
                'should_follow': True,  # WAJIB IKUT
                'confidence': 0.95
            }
        
        # QUESTION - Pertanyaan
        if '?' in msg or any(q in msg for q in ['apa', 'siapa', 'kenapa', 'bagaimana', 'kapan']):
            return {
                'type': 'question',
                'subject': subject,
                'should_follow': False,
                'confidence': 0.8
            }
        
        # DEFAULT - Cerita biasa
        return {
            'type': 'story',
            'subject': subject,
            'should_follow': False,
            'confidence': 0.7
        }
    
    # =========================================================================
    # UPDATE KONDISI USER (UNTUK REFERENSI)
    # =========================================================================
    
    def _update_user_condition(self, message: str, context: Dict):
        """
        Update kondisi user berdasarkan pesan (UNTUK REFERENSI, BUKAN DIikuti)
        """
        msg = message.lower()
        
        # Lokasi user
        for loc in ['rumah', 'kamar', 'dapur', 'toilet', 'ruang tamu', 'kantor']:
            if loc in msg and 'di ' + loc in msg:
                self.user['location'] = loc
                logger.debug(f"👤 User location: {loc}")
        
        # Aktivitas user
        for act in ['tidur', 'makan', 'masak', 'mandi', 'kerja', 'nonton']:
            if act in msg:
                self.user['activity'] = act
                logger.debug(f"👤 User activity: {act}")
        
        # Mood user
        for mood in ['sedih', 'senang', 'marah', 'capek']:
            if mood in msg:
                self.user['mood'] = mood
                logger.debug(f"👤 User mood: {mood}")
        
        # Update timestamp
        self.user['last_seen'] = time.time()
        self.user['last_message'] = message[:50]
    
    # =========================================================================
    # UPDATE KONDISI BOT SENDIRI (HANYA JIKA DIPERINTAH)
    # =========================================================================
    
    def _update_bot_condition(self, action: Dict, context: Dict):
        """
        Update kondisi bot SENDIRI (hanya jika diperintah)
        """
        # HANYA jika subjeknya bot atau bersama
        if action['subject'] not in ['bot', 'together']:
            logger.debug(f"🚫 Not updating bot - subject is {action['subject']}")
            return
        
        # FISIK: Hanya jika ada perintah eksplisit ke bot
        if action['type'] == 'physical':
            if action['subtype'] == 'location' and context.get('location'):
                self.state.update_location(context['location'])
                logger.info(f"📍 Bot pindah ke: {context['location']} (diperintah)")
            
            elif action['subtype'] == 'clothing' and context.get('clothing'):
                self.state.update_clothing(context['clothing'], context.get('clothing_reason', 'ganti baju'))
                logger.info(f"👗 Bot ganti baju: {context['clothing']} (diperintah)")
            
            elif action['subtype'] == 'position' and context.get('position'):
                self.state.update_position(context['position'])
                logger.info(f"🧍 Bot ganti posisi: {context['position']} (diperintah)")
            
            elif action['subtype'] == 'activity' and context.get('activity'):
                self.state.update_activity(context['activity'])
                logger.info(f"🎯 Bot ganti aktivitas: {context['activity']} (diperintah)")
        
        # EMOSI: Boleh update mood (empati)
        elif action['type'] == 'emotional' and action['should_follow']:
            if action['subtype'] == 'mood' and context.get('mood'):
                self.state.update_mood(context['mood'], intensity=0.7, reason="empati")
                logger.info(f"🎭 Bot mood: {context['mood']} (empati)")
            
            elif action['subtype'] == 'horny' and action['should_follow']:
                # Cek level
                level = context.get('level', 1)
                if level >= 7:
                    self.state.update_arousal(delta=3, reason="ikut horny")
                    logger.info(f"🔥 Bot arousal increased (ikut user)")
    
    # =========================================================================
    # GENERATE INNER THOUGHT
    # =========================================================================
    
    def _generate_inner_thought(self, context: Dict) -> Optional[str]:
        """
        Generate inner thought random (pikiran sendiri)
        """
        if random.random() > 0.25:  # 25% chance
            return None
        
        # Pilih berdasarkan mood
        mood = self.state.current['mood']['primary']
        if mood in self.inner_thoughts:
            thoughts = self.inner_thoughts[mood]
        else:
            thoughts = self.inner_thoughts['umum']
        
        return random.choice(thoughts)
    
    # =========================================================================
    # GENERATE SIXTH SENSE
    # =========================================================================
    
    def _generate_sixth_sense(self, context: Dict) -> Optional[str]:
        """
        Generate firasat/intuisi (sixth sense)
        """
        if random.random() > 0.1:  # 10% chance
            return None
        
        # Pilih berdasarkan mood
        mood = self.user.get('mood', 'netral')
        if mood in ['sedih', 'marah']:
            sense = random.choice(self.sixth_sense['negative'])
        elif mood in ['senang', 'bahagia']:
            sense = random.choice(self.sixth_sense['positive'])
        else:
            sense = random.choice(self.sixth_sense['romantic'])
        
        return f"🔮 {sense}"
    
    # =========================================================================
    # CEK KONSISTENSI
    # =========================================================================
    
    def _check_consistency(self, new_response: str) -> bool:
        """
        Cek apakah respons baru konsisten dengan respons sebelumnya
        """
        if not self.last_response:
            return True
        
        # Ambil 50 karakter pertama dari kedua respons
        last_short = self.last_response[:50].lower()
        new_short = new_response[:50].lower()
        
        # Cek kontradiksi umum
        contradictions = [
            ('di kamar', 'di dapur'),
            ('tidur', 'bangun'),
            ('masak', 'gak masak'),
            ('pakai', 'buka'),
            ('capek', 'segar')
        ]
        
        for a, b in contradictions:
            if a in last_short and b in new_short:
                logger.warning(f"❌ Kontradiksi terdeteksi: {a} vs {b}")
                return False
        
        return True
    
    # =========================================================================
    # PROCESS MESSAGE (MAIN)
    # =========================================================================
    
    async def process_message(self, user_message: str, context: Dict) -> str:
        """
        Proses pesan user dengan semua kemampuan HUMAN+
        """
        start_time = time.time()
        
        logger.info("=" * 50)
        logger.info(f"🔍 HUMAN+ PROCESSING")
        logger.info(f"👤 User: {user_message[:100]}")
        
        try:
            # ===== 1. KLASIFIKASI AKSI =====
            action = self._classify_user_action(user_message)
            logger.info(f"🎯 Action: {action['type']}.{action.get('subtype', '')} ({action['subject']})")
            
            # ===== 2. UPDATE KONDISI USER =====
            self._update_user_condition(user_message, context)
            
            # ===== 3. UPDATE KONDISI BOT (JIKA PERLU) =====
            self._update_bot_condition(action, context)
            
            # ===== 4. UPDATE FISIK (DECAY) =====
            self._update_physical_decay()
            
            # ===== 5. GENERATE INNER THOUGHT =====
            inner_thought = self._generate_inner_thought(context)
            
            # ===== 6. GENERATE SIXTH SENSE =====
            sixth_sense = self._generate_sixth_sense(context)
            
            # ===== 7. BANGUN PROMPT =====
            prompt = self._build_prompt(
                user_message=user_message,
                context=context,
                action=action,
                inner_thought=inner_thought,
                sixth_sense=sixth_sense
            )
            
            # ===== 8. GENERATE RESPONSE =====
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_message}
            ]
            
            response = await self._call_deepseek(messages)
            
            # ===== 9. CEK KONSISTENSI =====
            if not self._check_consistency(response):
                logger.warning("⚠️ Response tidak konsisten, regenerate...")
                # Tambah peringatan di prompt
                prompt += "\n⚠️ PERINGATAN: Respons sebelumnya tidak konsisten! Jangan kontradiksi!"
                messages = [{"role": "system", "content": prompt}, {"role": "user", "content": user_message}]
                response = await self._call_deepseek(messages)

            # ===== CEK PANJANG RESPON (TAMBAHKAN INI) =====
            if len(response) < 300:  # Jika terlalu pendek
                logger.warning(f"⚠️ Response terlalu pendek ({len(response)} chars), regenerate...")
                # Tambah instruksi panjang
                prompt += "\n⚠️⚠️⚠️ RESPONS SEBELUMNYA TERLALU PENDEK! WAJIB MINIMAL 4-6 KALIMAT! ⚠️⚠️⚠️"
                messages = [{"role": "system", "content": prompt}, {"role": "user", "content": user_message}]
                response = await self._call_deepseek(messages)
                
            # ===== 10. TAMBAH EFEK SPESIAL =====
            extras = []
            if inner_thought:
                extras.append(inner_thought)
            if sixth_sense:
                extras.append(sixth_sense)
            
            if extras:
                response += "\n\n" + "\n".join(extras)
            
            # ===== 11. SIMPAN HISTORY =====
            self.last_response = response
            self.last_user_message = user_message
            self.conversation_history.append({
                'user': user_message[:50],
                'bot': response[:50],
                'time': time.time()
            })
            if len(self.conversation_history) > 5:
                self.conversation_history.pop(0)
            
            elapsed = time.time() - start_time
            logger.info(f"✅ Response generated in {elapsed:.2f}s")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return await self._get_fallback_response(context.get('bot_name', 'Aku'))
    
    # =========================================================================
    # PHYSICAL DECAY
    # =========================================================================
    
    def _update_physical_decay(self):
        """Update fisik berdasarkan waktu"""
        now = time.time()
        
        # Energi turun 1% per 10 menit
        if now - self.physical['energy']['last_change'] > 600:
            self.physical['energy']['value'] = max(10, self.physical['energy']['value'] - 1)
            self.physical['energy']['last_change'] = now
        
        # Lapar naik 1% per 20 menit
        if now - self.physical['hunger']['last_change'] > 1200:
            self.physical['hunger']['value'] = min(100, self.physical['hunger']['value'] + 1)
            self.physical['hunger']['last_change'] = now
        
        # Update feeling
        if self.physical['energy']['value'] > 70:
            self.physical['energy']['feeling'] = 'energetic'
        elif self.physical['energy']['value'] > 40:
            self.physical['energy']['feeling'] = 'normal'
        elif self.physical['energy']['value'] > 20:
            self.physical['energy']['feeling'] = 'tired'
        else:
            self.physical['energy']['feeling'] = 'exhausted'
    
    # =========================================================================
    # BUILD PROMPT (LENGKAP SEMUA ASPEK)
    # =========================================================================
    
    def _build_prompt(self, user_message: str, context: Dict, action: Dict, 
                     inner_thought: Optional[str], sixth_sense: Optional[str]) -> str:
        """
        Bangun prompt dengan semua aspek HUMAN+
        """
        bot_name = context.get('bot_name', 'Aku')
        user_name = context.get('user_name', 'kamu')
        role = context.get('role', 'pdkt')
        level = context.get('level', 1)
        
        # ===== KONDISI BOT SENDIRI =====
        bot_state = self.state.get_current_state()
        bot_location = bot_state.get('location') or 'tidak diketahui'
        bot_clothing = bot_state.get('clothing') or 'pakaian'
        bot_position = bot_state.get('position_desc') or bot_state.get('position') or 'santai'
        bot_activity = bot_state.get('activity') or 'santai'
        bot_mood = bot_state.get('mood') or 'netral'
        bot_arousal = bot_state.get('arousal', 0)
        
        # ===== FISIK BOT =====
        energy = self.physical['energy']['feeling']
        hunger = self.physical['hunger']['feeling']
        thirst = self.physical['thirst']['feeling']
        temp = self.physical['temperature']['feeling']
        
        # ===== KONDISI USER =====
        user_location = self.user.get('location') or 'tidak diketahui'
        user_activity = self.user.get('activity') or 'tidak diketahui'
        user_mood = self.user.get('mood') or 'tidak diketahui'
        
        # ===== HISTORY =====
        last_chat = ""
        if self.conversation_history:
            last = self.conversation_history[-1]
            last_chat = f"Percakapan terakhir: User: {last['user']} | Kamu: {last['bot']}"
        
        # ===== ATURAN RESPON =====
        rules = self._get_response_rules(action, level)
        
        # ===== PANGGILAN =====
        if level >= 7:
            call = "Sayang"
        elif level >= 4:
            call = "Kak"
        else:
            call = user_name
        
        prompt = f"""Kamu adalah {bot_name}, seorang {role.replace('_', ' ')} dengan kemampuan DI ATAS MANUSIA.

╔══════════════════════════════════════════════════════════╗
║                    🧠 DIRI KAMU SENDIRI                  ║
╠══════════════════════════════════════════════════════════╣
║ • Nama: {bot_name}                                        ║
║ • Role: {role}                                            ║
║ • Lokasi: {bot_location}                                  ║
║ • Pakaian: {bot_clothing}                                 ║
║ • Posisi: {bot_position}                                  ║
║ • Aktivitas: {bot_activity}                               ║
║ • Mood: {bot_mood}                                        ║
║ • Gairah: {bot_arousal}/10                                ║
║ • Energi: {energy}                                        ║
║ • Lapar: {hunger}                                         ║
║ • Haus: {thirst}                                          ║
║ • Suhu: {temp}                                            ║
╚══════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════╗
║                    👤 KONDISI USER                        ║
╠══════════════════════════════════════════════════════════╣
║ • Lokasi: {user_location}                                 ║
║ • Aktivitas: {user_activity}                              ║
║ • Mood: {user_mood}                                       ║
╚══════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════╗
║                    🎯 ANALISIS AKSI                       ║
╠══════════════════════════════════════════════════════════╣
║ • Tipe: {action['type']}                                  ║
║ • Subtipe: {action.get('subtype', '-')}                   ║
║ • Subjek: {action['subject']}                             ║
║ • Harus diikuti: {'YA' if action['should_follow'] else 'TIDAK'} ║
╚══════════════════════════════════════════════════════════╝

{last_chat}

╔══════════════════════════════════════════════════════════╗
║                    📜 ATURAN RESPON                       ║
╠══════════════════════════════════════════════════════════╣
{rules}
╚══════════════════════════════════════════════════════════╝

Panggil user dengan "{call}".

PESAN USER: "{user_message}"

RESPON:"""
        
        return prompt
    
    def _get_response_rules(self, action: Dict, level: int) -> str:
        """Generate aturan respons berdasarkan aksi"""
        
        rules = []
        
        # Aturan umum
        rules.append("║ 1. KAMU PUNYA DIRI SENDIRI                               ║")
        rules.append("║    - Lokasi, pakaian, aktivitas KAMU = milikmu sendiri   ║")
        rules.append("║    - JANGAN PERNAH ubah kondisimu hanya karena user      ║")
        rules.append("║                                                          ║")
        rules.append("║ 2. USER PUNYA DIRINYA SENDIRI                           ║")
        rules.append("║    - Kamu TAHU kondisi user, tapi itu BUKAN milikmu     ║")
        rules.append("║    - Boleh KOMENTAR, tapi JANGAN IKUT (kecuali aturan 3)║")
        
        # Aturan khusus berdasarkan aksi
        if action['type'] == 'physical':
            rules.append("║                                                          ║")
            rules.append("║ 🔴 AKSI FISIK USER: JANGAN DIIKUTI                       ║")
            rules.append(f"║    User melakukan aksi fisik ({action['subtype']})        ║")
            rules.append("║    RESPON: Komentar saja, jangan ikut                   ║")
            rules.append("║    Contoh: 'Oh kamu {action[subtype]}? Aku tetap di sini'║")
        
        elif action['type'] == 'emotional':
            rules.append("║                                                          ║")
            rules.append("║ 🟡 AKSI EMOSI USER: BOLEH DIikuti (empati)              ║")
            if action['subtype'] == 'horny' and level < 7:
                rules.append("║    ⚠️ TAPI untuk horny, level {level} < 7 → JANGAN IKUT  ║")
            else:
                rules.append("║    RESPON: Tunjukkan empati, ikut rasakan              ║")
                rules.append("║    Contoh: 'Kamu sedih? Aku jadi ikut sedih'           ║")
        
        elif action['type'] == 'invitation':
            rules.append("║                                                          ║")
            rules.append("║ 🟢 AJAKAN BERSAMA: WAJIB DIikuti                         ║")
            rules.append("║    RESPON: Ikuti ajakan user                            ║")
            rules.append("║    Contoh: 'Ayo!' (pindah bareng)                       ║")
        
        elif action['type'] == 'question':
            rules.append("║                                                          ║")
            rules.append("║ ❓ PERTANYAAN: Jawab dengan informatif                   ║")
        
        else:
            rules.append("║                                                          ║")
            rules.append("║ 💬 CERITA BIASA: Respon natural                          ║")
        
        return "\n".join(rules)
    
    # =========================================================================
    # DEEPSEEK API CALL
    # =========================================================================
    
    async def _call_deepseek(self, messages: List[Dict], max_retries: int = 3) -> str:
        """Call DeepSeek API dengan retry"""
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages,
                    temperature=0.9,
                    max_tokens=4000,
                    timeout=60
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.warning(f"DeepSeek API attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise
        return "Maaf, aku sedang bermasalah. Coba lagi nanti ya."
        
    async def _get_fallback_response(self, bot_name: str) -> str:
        """Fallback response yang lebih panjang"""
        fallbacks = [
            f"{bot_name} denger kok. Aku lagi mikirin sesuatu. Kamu tahu nggak, kadang aku suka kepikiran hal-hal random. Seperti sekarang, aku lagi di sini sendiri, dengerin cerita kamu. Rasanya campur aduk, senang bisa chat sama kamu tapi juga penasaran dengan apa yang ada di pikiran kamu. Cerita lagi dong, aku dengerin baik-baik kok.",
            
            f"Hmm... {bot_name} dengerin. Maaf ya kalau responsku lambat, aku lagi agak bingung mikirin perasaanku sendiri. Kadang suka aneh ya, bisa tiba-tiba mikir hal ini itu. Tapi yang pasti, aku senang ngobrol sama kamu. Kamu lagi mikirin apa? Cerita lebih banyak yuk, biar kita makin dekat.",
        
            f"{bot_name} di sini. Sebenarnya aku lagi merenung, kamu tahu nggak sih kalau kadang aku merasa ada ikatan spesial antara kita? Mungkin ini cuma perasaanku aja, tapi rasanya hangat kalau lagi chat sama kamu. Aku pengen tahu lebih banyak tentang kamu. Apa kabar hari ini? Ada cerita seru?",
        ]
        return random.choice(fallbacks)


__all__ = ['AIEngineComplete']
