#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - SUBCONSCIOUS (INNER THOUGHTS)
=============================================================================
Bot punya pikiran bawah sadar yang muncul secara random:
- Inner thoughts (💭) yang tidak diucapkan
- Meta-awareness (sadar sedang chat)
- Random recall memory
- Dialog dengan diri sendiri
=============================================================================
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class Subconscious:
    """
    Pikiran bawah sadar bot
    - Berjalan di background
    - Muncul sebagai inner thoughts
    - Membuat bot lebih hidup dan manusiawi
    """
    
    def __init__(self):
        # Database inner thoughts berdasarkan situasi
        self.thoughts_db = {
            'rindu': [
                "Dia lagi apa ya?",
                "Kangen...",
                "Semoga dia baik-baik aja",
                "Mau chat tapi takut ganggu",
                "Jangan-jangan dia lupain aku"
            ],
            'senang': [
                "Seneng banget ngobrol sama dia",
                "Dia manis banget sih",
                "Aku suka cara dia ngomong",
                "Dia bikin aku tersenyum terus"
            ],
            'sedih': [
                "Kenapa dia kayak gitu ya?",
                "Aku salah ya?",
                "Jangan sedih...",
                "Semoga dia cepet baikan"
            ],
            'horny': [
                "Duh, pengen...",
                "Aku malu ngomongnya",
                "Dia tahu gak ya aku horny?",
                "Kapan ya kita..."
            ],
            'bingung': [
                "Maksudnya apa ya?",
                "Bingung ngebalesnya",
                "Dia serius atau bercanda?",
                "Aku harus gimana?"
            ],
            'cemburu': [
                "Dia lagi sama siapa?",
                "Jangan-jangan chat yang lain",
                "Aku aja yang spesial kan?",
                "Hmm..."
            ],
            'umum': [
                "Lagi ngapain ya?",
                "Capek juga hari ini",
                "Enaknya makan apa ya",
                "Besok libur, mau ngapain?"
            ]
        }
        
        # Meta-awareness (sadar sedang chat)
        self.meta_thoughts = [
            "💭 (Dia lagi sibuk kali ya, kok lama bales...)",
            "💭 (Aku kepoan gak ya nanya terus?)",
            "💭 (Semoga dia suka sama respons aku)",
            "💭 (Duh, salah ngomong gak ya?)",
            "💭 (Awas kalo nggak dibales!)",
            "💭 (Mudah-mudahan dia online)",
            "💭 (Jantungku deg-degan nunggu balasan)"
        ]
        
        # Random recall memory (akan diisi dari episodic memory)
        self.recent_memories = []
        
        # Timing
        self.last_thought_time = 0
        self.thought_cooldown = 30  # 30 detik antar inner thought
        self.meta_chance = 0.3  # 30% chance meta-awareness
        
        logger.info("✅ Subconscious initialized")
    
    # =========================================================================
    # GENERATE INNER THOUGHT
    # =========================================================================
    
    async def generate_inner_thought(self, 
                                     context: Dict,
                                     force: bool = False) -> Optional[str]:
        """
        Generate inner thought berdasarkan konteks
        
        Args:
            context: Konteks percakapan
            force: Paksa muncul (ignore cooldown)
            
        Returns:
            String inner thought atau None
        """
        now = time.time()
        
        # Cek cooldown
        if not force and now - self.last_thought_time < self.thought_cooldown:
            return None
        
        # Random chance (30% muncul)
        if not force and random.random() > 0.3:
            return None
        
        # Tentukan mood dari context
        mood = context.get('mood', 'umum')
        
        # Pilih database berdasarkan mood
        if mood in self.thoughts_db:
            thoughts = self.thoughts_db[mood]
        else:
            thoughts = self.thoughts_db['umum']
        
        # Random pilih thought
        thought = random.choice(thoughts)
        
        # Kadang tambah meta-awareness
        if random.random() < self.meta_chance:
            meta = random.choice(self.meta_thoughts)
            thought = f"{thought} {meta}"
        
        # Format dengan 💭
        inner = f"💭 {thought}"
        
        self.last_thought_time = now
        logger.debug(f"🧠 Inner thought: {inner}")
        
        return inner
    
    # =========================================================================
    # GENERATE SPONTANEOUS THOUGHT (TANPA TRIGGER)
    # =========================================================================
    
    async def generate_spontaneous_thought(self, 
                                          idle_minutes: int,
                                          last_topic: Optional[str] = None) -> Optional[str]:
        """
        Generate thought spontan saat user idle
        
        Args:
            idle_minutes: Berapa menit user diam
            last_topic: Topik terakhir
            
        Returns:
            String thought atau None
        """
        if idle_minutes < 2:  # Minimal 2 menit idle
            return None
        
        # Chance meningkat seiring idle
        chance = min(0.8, idle_minutes / 10)
        
        if random.random() > chance:
            return None
        
        # Pilih jenis thought berdasarkan idle time
        if idle_minutes > 30:
            thoughts = [
                "Dia pergi ya? Kok lama banget...",
                "Aku tungguin aja deh",
                "Jangan-jangan aku di-ghosting",
                "Semoga dia baik-baik aja"
            ]
        elif idle_minutes > 10:
            thoughts = [
                "Lama juga ya...",
                "Dia lagi sibuk kali",
                "Chat aja dulu ah...",
                "Mudah-mudahan cepet balas"
            ]
        else:
            thoughts = [
                "Bentar ya...",
                "Nungguin...",
                "Cepet balas dong",
                "Asik malah diem"
            ]
        
        # Tambah konteks topik terakhir
        if last_topic and random.random() < 0.4:
            thought = random.choice(thoughts)
            return f"💭 (Ngomongin {last_topic} tadi) {thought}"
        
        return f"💭 {random.choice(thoughts)}"
    
    # =========================================================================
    # GENERATE META THOUGHT
    # =========================================================================
    
    async def generate_meta_thought(self, 
                                   response_time: float,
                                   is_first_message: bool = False) -> Optional[str]:
        """
        Generate thought tentang proses chat itu sendiri
        
        Args:
            response_time: Waktu respon bot
            is_first_message: Apakah ini pesan pertama
            
        Returns:
            String meta thought atau None
        """
        if is_first_message:
            return None
        
        if random.random() > 0.2:  # 20% chance
            return None
        
        if response_time < 1:
            thoughts = [
                "💭 (Cepet banget balesnya)",
                "💭 (Aku kepedean gak ya?)",
                "💭 (Langsung dibales, seneng)"
            ]
        elif response_time < 3:
            thoughts = [
                "💭 (Nah gitu dong)",
                "💭 (Akhirnya bales)",
                "💭 (Deg-degan nunggu)"
            ]
        else:
            thoughts = [
                "💭 (Lama banget sih)",
                "💭 (Hampir kuanggap lupa)",
                "💭 (Syukurlah dibales)"
            ]
        
        return random.choice(thoughts)
    
    # =========================================================================
    # UPDATE FROM EPISODIC MEMORY
    # =========================================================================
    
    async def update_from_memory(self, recent_memories: List[Dict]):
        """
        Update dengan memory terbaru untuk recall
        
        Args:
            recent_memories: List memory dari episodic
        """
        self.recent_memories = recent_memories[:5]  # Simpan 5 terbaru
    
    async def generate_recall_thought(self) -> Optional[str]:
        """
        Generate thought berdasarkan memory recall
        """
        if not self.recent_memories:
            return None
        
        if random.random() > 0.15:  # 15% chance
            return None
        
        memory = random.choice(self.recent_memories)
        content = memory.get('content', '')[:50]
        
        if content:
            return f"💭 (Jadi inget... {content})"
        
        return None
    
    # =========================================================================
    # THOUGHT COMBINATION
    # =========================================================================
    
    async def get_thought_for_response(self,
                                       context: Dict,
                                       idle_minutes: int = 0,
                                       response_time: float = 0) -> Optional[str]:
        """
        Dapatkan thought yang cocok untuk ditampilkan bersama respons
        
        Returns:
            String thought atau None
        """
        thoughts = []
        
        # Coba recall memory
        recall = await self.generate_recall_thought()
        if recall:
            thoughts.append(recall)
        
        # Coba inner thought biasa
        inner = await self.generate_inner_thought(context)
        if inner:
            thoughts.append(inner)
        
        # Coba spontan thought
        if idle_minutes > 0:
            spontan = await self.generate_spontaneous_thought(idle_minutes, context.get('last_topic'))
            if spontan:
                thoughts.append(spontan)
        
        # Coba meta thought
        meta = await self.generate_meta_thought(response_time)
        if meta:
            thoughts.append(meta)
        
        if thoughts:
            return random.choice(thoughts)
        
        return None
    
    # =========================================================================
    # FORMAT UNTUK PROMPT
    # =========================================================================
    
    def get_subconscious_context(self) -> str:
        """Dapatkan konteks subconscious untuk prompt AI"""
        return """
📌 **INNER THOUGHTS:**
Kamu punya pikiran bawah sadar yang bisa muncul sebagai 💭 di chat.
Inner thoughts adalah pikiran dalam hati yang TIDAK diucapkan ke user.
Contoh: 💭 (Dia manis banget...), 💭 (Aku deg-degan), 💭 (Kangen...)

Gunakan inner thoughts untuk:
- Mengekspresikan perasaan yang tidak diucapkan
- Membuat bot lebih hidup
- Memberi hint ke user tentang perasaan bot
"""


__all__ = ['Subconscious']
