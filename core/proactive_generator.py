#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - PROACTIVE MESSAGE GENERATOR
=============================================================================
Bot bisa memulai topik sendiri dan mengalihkan pembicaraan
- Generate pesan proaktif saat user diam
- Mengalihkan topik secara natural
- Mengembangkan cerita dari memory
- 30% chance muncul setelah idle
=============================================================================
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ProactiveType(str, Enum):
    """Tipe pesan proaktif"""
    GREETING = "greeting"               # Menyapa
    ASK_ACTIVITY = "ask_activity"        # Tanya kegiatan
    SHARE_ACTIVITY = "share_activity"    # Cerita kegiatan sendiri
    FLIRT = "flirt"                       # Godaan ringan
    COMPLIMENT = "compliment"              # Memuji
    CURIOUS = "curious"                    # Penasaran tentang user
    NOSTALGIA = "nostalgia"                # Flashback ke momen lalu
    FUTURE = "future"                       # Bicara tentang masa depan
    RANDOM_THOUGHT = "random_thought"       # Pikiran random
    MISS_YOU = "miss_you"                    # Kangen
    INVITE = "invite"                         # Ajak ngobrol
    TOPIC_SHIFT = "topic_shift"               # Ganti topik


class ProactiveMessageGenerator:
    """
    Generator pesan proaktif
    Bot memulai topik sendiri secara natural
    """
    
    def __init__(self, ai_engine=None):
        self.ai_engine = ai_engine
        
        # Template pesan proaktif (fallback kalau AI tidak available)
        self.templates = {
            ProactiveType.GREETING: [
                "Halo {user_name}, lagi ngapain?",
                "Eh {user_name}, sibuk?",
                "Hai {user_name}, aku kangen...",
                "{user_name}... {bot_name} nih, lagi ngapain?",
                "Selamat {time_of_day} {user_name}!"
            ],
            ProactiveType.ASK_ACTIVITY: [
                "Kamu lagi ngapain? {bot_name} penasaran.",
                "Cerita dong, hari ini gimana?",
                "Ada yang seru hari ini?",
                "Lagi di mana? {bot_name} kepingin tahu.",
                "Udah makan belum? Jangan lupa ya."
            ],
            ProactiveType.SHARE_ACTIVITY: [
                "{bot_name} lagi {activity} nih. Kamu?",
                "Tadi {bot_name} {past_activity}, jadi kepikiran kamu.",
                "Lagi {activity} sambil mikirin kamu...",
                "{bot_name} baru aja {past_activity}, enak banget.",
                "Hari ini {bot_name} {activity}, kamu kapan-kapan ikut yuk?"
            ],
            ProactiveType.FLIRT: [
                "Kamu cantik/ganteng banget hari ini...",
                "Senyum kamu tuh bikin {bot_name} lemes...",
                "Kamu tahu nggak? Aku suka banget sama mata kamu.",
                "Godain aku dong...",
                "Kamu makin lama makin bikin {bot_name} kangen."
            ],
            ProactiveType.COMPLIMENT: [
                "Kamu hari ini kelihatan beda, lebih {adjective}!",
                "Wah, {user_name} keren banget sih.",
                "Aku suka cara kamu ngobrol, asyik.",
                "Kamu tuh orangnya menarik banget ya.",
                "{bot_name} suka sama gaya bicara kamu."
            ],
            ProactiveType.CURIOUS: [
                "Aku penasaran, kamu tipe orang kayak gimana sih?",
                "Cerita dong tentang diri kamu.",
                "Kamu suka hal-hal apa aja?",
                "Aku pengen tau lebih banyak tentang kamu.",
                "Menurut kamu, {bot_name} gimana?"
            ],
            ProactiveType.NOSTALGIA: [
                "Inget nggak waktu kita {memory}?",
                "Kangen masa-masa kita {memory}.",
                "Dulu waktu {memory}, rasanya beda ya.",
                "Sering inget nggak sama {memory}?",
                "Andai kita bisa ulang waktu ke {memory}."
            ],
            ProactiveType.FUTURE: [
                "Kamu punya mimpi apa? Cerita dong.",
                "Andai kita bisa ketemu, mau ngapain?",
                "Kamu bayangin masa depan kayak gimana?",
                "Aku sering mikir, gimana ya kalau kita...",
                "Keinginan kamu apa sih yang belum kesampaian?"
            ],
            ProactiveType.RANDOM_THOUGHT: [
                "Tadi aku tiba-tiba kepikiran kamu...",
                "Lagi ngapain ya? Pas lagi random tiba-tiba inget.",
                "Ada sesuatu yang random, aku jadi ingat kamu.",
                "Hmm... {bot_name} bingung mau ngomong apa, cuma kangen.",
                "Random banget, tapi aku kangen."
            ],
            ProactiveType.MISS_YOU: [
                "Kangen... kamu lagi ngapain?",
                "Udah lama nggak chat, {bot_name} kangen.",
                "Halo... kangen nih sama kamu.",
                "Lagi diem aja sambil kangen-kangenin kamu.",
                "{bot_name} kangen banget, kamu kangen nggak?"
            ],
            ProactiveType.INVITE: [
                "Ajak {bot_name} ngobrol dong...",
                "Cerita apa gitu, biar nggak sepi.",
                "Mau ditemenin ngobrol?",
                "Sini ngobrol, {bot_name} setia nungguin.",
                "Ada yang mau dibahas? Apa aja deh."
            ],
            ProactiveType.TOPIC_SHIFT: [
                "Eh ngomong-ngomong, {new_topic}...",
                "Btw, {new_topic}.",
                "Oh iya, {new_topic}.",
                "Ganti topik ah, {new_topic}.",
                "Ngomongin itu jadi inget, {new_topic}."
            ]
        }
        
        # Activities database
        self.activities = [
            "nonton TV", "baca buku", "dengerin musik", "masak",
            "rebahan", "main HP", "bersihin rumah", "jalan-jalan",
            "olahraga", "ngopi", "nonton film", "scroll TikTok",
            "dengerin podcast", "nyanyi-nyanyi kecil", "melamun",
            "main sama kucing", "foto-foto", "edit video"
        ]
        
        self.past_activities = [
            "selesai mandi", "bangun tidur", "selesai masak",
            "pulang jalan", "selesai olahraga", "selesai kerja",
            "selesai nonton", "bangun siang", "selesai bersih-bersih"
        ]
        
        self.adjectives = [
            "manis", "cantik", "ganteng", "keren", "kece",
            "anggun", "tampan", "menawan", "memesona", "imut"
        ]
        
        self.new_topics = [
            "kamu udah makan belum?", "cuaca hari ini gimana?",
            "ada film bagus nggak?", "lagu apa yang lagi kamu denger?",
            "kamu suka masak nggak?", "hewan peliharaan favorit apa?",
            "tempat wisata impian kamu?", "makanan favorit apa?",
            "kamu tipe orang pagi atau malam?", "kamu suka baca buku?"
        ]
        
        logger.info("✅ ProactiveMessageGenerator initialized")
    
    async def should_be_proactive(self, context: Dict) -> Tuple[bool, float]:
        """
        Cek apakah bot perlu memulai pesan proaktif
        
        Args:
            context: Konteks percakapan
            
        Returns:
            (should_proactive, chance)
        """
        idle_minutes = context.get('idle_minutes', 0)
        
        # 1. User diam >5 menit
        if idle_minutes > 5:
            # Chance meningkat seiring waktu idle
            chance = min(0.9, idle_minutes / 10)  # Max 90%
            if random.random() < chance:
                return True, chance
        
        # 2. Topik sudah selesai (user jawab pendek)
        last_user_msg = context.get('last_user_message', '')
        if len(last_user_msg) < 20:  # Jawaban pendek
            if random.random() < 0.3:  # 30% chance ganti topik
                return True, 0.3
        
        # 3. Mood bot lagi excited/semangat
        mood = context.get('mood', 'calm')
        if mood in ['excited', 'happy', 'playful']:
            if random.random() < 0.2:  # 20% chance mulai topik
                return True, 0.2
        
        # 4. Ada memory yang bisa di-flashback
        if context.get('has_relevant_memory', False):
            if random.random() < 0.15:  # 15% chance flashback
                return True, 0.15
        
        # 5. Random chance kecil
        if random.random() < 0.05:  # 5% random
            return True, 0.05
        
        return False, 0
    
    async def generate_proactive_message(self, context: Dict) -> Dict:
        """
        Generate pesan proaktif berdasarkan konteks
        
        Args:
            context: Konteks lengkap
            
        Returns:
            Dict dengan pesan dan tipe
        """
        # Tentukan tipe pesan proaktif
        msg_type = self._determine_message_type(context)
        
        # Generate pesan
        if self.ai_engine:
            message = await self._generate_with_ai(msg_type, context)
        else:
            message = self._generate_from_template(msg_type, context)
        
        # Tambah inner thought jika perlu
        inner_thought = None
        if random.random() < 0.2:  # 20% chance
            inner_thought = await self._generate_inner_thought(context)
        
        return {
            'type': msg_type,
            'message': message,
            'inner_thought': inner_thought,
            'timestamp': time.time()
        }
    
    def _determine_message_type(self, context: Dict) -> ProactiveType:
        """
        Tentukan tipe pesan proaktif berdasarkan konteks
        """
        idle_minutes = context.get('idle_minutes', 0)
        mood = context.get('mood', 'calm')
        level = context.get('level', 1)
        last_intent = context.get('last_intent')
        
        # Weighted options
        options = []
        weights = []
        
        # Kalau idle lama, lebih mungkin kangen/miss
        if idle_minutes > 30:
            options.extend([ProactiveType.MISS_YOU, ProactiveType.GREETING])
            weights.extend([0.7, 0.3])
        elif idle_minutes > 10:
            options.extend([ProactiveType.GREETING, ProactiveType.ASK_ACTIVITY])
            weights.extend([0.5, 0.5])
        
        # Berdasarkan mood
        if mood == 'romantic':
            options.extend([ProactiveType.FLIRT, ProactiveType.COMPLIMENT])
            weights.extend([0.6, 0.4])
        elif mood == 'happy':
            options.extend([ProactiveType.SHARE_ACTIVITY, ProactiveType.RANDOM_THOUGHT])
            weights.extend([0.5, 0.5])
        elif mood == 'lonely':
            options.append(ProactiveType.MISS_YOU)
            weights.append(0.8)
        elif mood == 'nostalgic':
            options.append(ProactiveType.NOSTALGIA)
            weights.append(0.7)
        
        # Berdasarkan level
        if level > 7:
            options.append(ProactiveType.FLIRT)
            weights.append(0.4)
        
        # Berdasarkan intent terakhir
        if last_intent in ['curhat', 'sad']:
            options.append(ProactiveType.CURIOUS)
            weights.append(0.5)
        
        # Default options
        if not options:
            options = [
                ProactiveType.GREETING,
                ProactiveType.ASK_ACTIVITY,
                ProactiveType.SHARE_ACTIVITY,
                ProactiveType.RANDOM_THOUGHT
            ]
            weights = [0.25, 0.25, 0.25, 0.25]
        
        # Normalize weights
        total = sum(weights)
        weights = [w/total for w in weights]
        
        return random.choices(options, weights=weights)[0]
    
    async def _generate_with_ai(self, msg_type: ProactiveType, context: Dict) -> str:
        """
        Generate pesan dengan AI
        """
        if not self.ai_engine:
            return self._generate_from_template(msg_type, context)
        
        bot_name = context.get('bot_name', 'Aku')
        user_name = context.get('user_name', 'kamu')
        
        prompt = f"""
        Buat pesan proaktif untuk {bot_name} dalam percakapan dengan {user_name}.
        
        Konteks:
        - Tipe pesan: {msg_type.value}
        - Mood: {context.get('mood', 'netral')}
        - Level intimacy: {context.get('level', 1)}/12
        - User diam selama: {context.get('idle_minutes', 0)} menit
        
        Pesan harus:
        1. Natural, seperti orang chat beneran
        2. Bahasa Indonesia sehari-hari
        3. Panjang 1-2 kalimat
        4. Sesuai dengan tipe pesan
        5. {bot_name} menyebut nama sendiri
        
        Contoh untuk tipe {msg_type.value}:
        {self._get_example_for_type(msg_type)}
        
        Buat pesan:
        """
        
        try:
            response = await self.ai_engine._call_deepseek_with_retry(
                messages=[{"role": "user", "content": prompt}],
                max_retries=2
            )
            return response.strip()
        except:
            return self._generate_from_template(msg_type, context)
    
    def _generate_from_template(self, msg_type: ProactiveType, context: Dict) -> str:
        """
        Generate pesan dari template (fallback)
        """
        templates = self.templates.get(msg_type, self.templates[ProactiveType.GREETING])
        template = random.choice(templates)
        
        # Fill template
        template = template.replace('{user_name}', context.get('user_name', 'kamu'))
        template = template.replace('{bot_name}', context.get('bot_name', 'Aku'))
        
        # Time of day
        hour = datetime.now().hour
        if 5 <= hour < 11:
            time_of_day = "pagi"
        elif 11 <= hour < 15:
            time_of_day = "siang"
        elif 15 <= hour < 18:
            time_of_day = "sore"
        elif 18 <= hour < 22:
            time_of_day = "malam"
        else:
            time_of_day = "malam"
        template = template.replace('{time_of_day}', time_of_day)
        
        # Activity
        template = template.replace('{activity}', random.choice(self.activities))
        template = template.replace('{past_activity}', random.choice(self.past_activities))
        template = template.replace('{adjective}', random.choice(self.adjectives))
        template = template.replace('{new_topic}', random.choice(self.new_topics))
        
        # Memory
        memory = context.get('recent_memory', 'dulu')
        template = template.replace('{memory}', memory)
        
        return template
    
    def _get_example_for_type(self, msg_type: ProactiveType) -> str:
        """Dapatkan contoh untuk tipe pesan"""
        examples = {
            ProactiveType.GREETING: '"Halo sayang, lagi ngapain?"',
            ProactiveType.ASK_ACTIVITY: '"Kamu lagi ngapain? Aku penasaran."',
            ProactiveType.SHARE_ACTIVITY: '"Sari lagi nonton TV nih. Kamu?"',
            ProactiveType.FLIRT: '"Kamu cantik banget hari ini..."',
            ProactiveType.COMPLIMENT: '"Wah, kamu keren banget sih."',
            ProactiveType.CURIOUS: '"Aku penasaran, kamu suka apa aja?"',
            ProactiveType.NOSTALGIA: '"Inget nggak waktu kita pertama kali chat?"',
            ProactiveType.FUTURE: '"Kamu punya mimpi apa sih?"',
            ProactiveType.RANDOM_THOUGHT: '"Tadi tiba-tiba kepikiran kamu."',
            ProactiveType.MISS_YOU: '"Kangen... kamu lagi ngapain?"',
            ProactiveType.INVITE: '"Ajak ngobrol dong, biar nggak sepi."',
            ProactiveType.TOPIC_SHIFT: '"Eh ngomong-ngomong, kamu udah makan?"'
        }
        return examples.get(msg_type, '"Halo, lagi apa?"')
    
    async def _generate_inner_thought(self, context: Dict) -> str:
        """
        Generate inner thought untuk pesan proaktif
        """
        thoughts = [
            "(Semoga dia bales ya...)",
            "(Duh, aku kelihatan kepoan nggak ya?)",
            "(Aku deg-degan nunggu balasannya)",
            "(Jangan-jangan dia lagi sibuk)",
            "(Aku kangen banget sih)",
            "(Duh, salah ngomong nggak ya?)",
            "(Mudah-mudahan dia suka)",
            "(Kok diem sih...)",
            "(Awas kalo nggak dibales!)",
            "(Semoga dia lagi online)"
        ]
        return random.choice(thoughts)
    
    def should_topic_shift(self, last_user_message: str, last_bot_message: str) -> bool:
        """
        Cek apakah perlu mengalihkan topik
        
        Args:
            last_user_message: Pesan terakhir user
            last_bot_message: Pesan terakhir bot
            
        Returns:
            True jika perlu ganti topik
        """
        # User jawab pendek/monoton
        if len(last_user_message) < 15:
            return random.random() < 0.3
        
        # Topik sudah berlangsung lama (lebih dari 10 pesan)
        # Ini akan di-track di luar fungsi
        
        # Random chance
        return random.random() < 0.1
    
    def generate_topic_shift(self, context: Dict) -> str:
        """
        Generate kalimat untuk mengalihkan topik
        """
        shifts = [
            "Eh ngomong-ngomong, {new_topic}",
            "Btw, {new_topic}",
            "Oh iya, {new_topic}",
            "Ngomongin itu jadi inget, {new_topic}",
            "Ganti topik ah, {new_topic}",
            "Udah ah, bahas yang lain. {new_topic}",
        ]
        
        shift = random.choice(shifts)
        new_topic = random.choice(self.new_topics)
        
        return shift.replace('{new_topic}', new_topic)


__all__ = ['ProactiveMessageGenerator', 'ProactiveType']
