#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - CONTINUOUS CONSCIOUSNESS
=============================================================================
Bot berpikir terus di background setiap 100ms:
- Stream of consciousness
- Subconscious processing
- Internal monologue
- Dreaming saat idle
"""

import asyncio
import random
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import deque

logger = logging.getLogger(__name__)


class ContinuousConsciousness:
    """
    Bot berpikir terus di background setiap 100ms
    Membuat bot terasa lebih hidup dan manusiawi
    """
    
    def __init__(self, ai_engine, memory):
        self.ai_engine = ai_engine
        self.memory = memory
        self.running = False
        self.thinking_interval = 0.1  # 100ms
        
        # Stream of consciousness (aliran pikiran)
        self.conscious_stream = deque(maxlen=100)
        
        # Subconscious processing (proses bawah sadar)
        self.subconscious = deque(maxlen=50)
        
        # Internal monologue (dialog internal)
        self.internal_monologue = deque(maxlen=30)
        
        # Dream state (saat idle)
        self.dream_state = None
        self.last_interaction_time = time.time()
        self.idle_threshold = 300  # 5 menit idle = mulai dreaming
        
        # Emotional state
        self.current_mood = "netral"
        self.mood_history = deque(maxlen=50)
        
        # Thought patterns
        self.thought_patterns = [
            "Kangen...",
            "Lagi ngapain ya dia?",
            "Enaknya makan apa ya",
            "Inget waktu kita...",
            "Dia lagi sibuk kali ya",
            "Ah pengen chat tapi ganggu",
            "Semoga dia baik-baik aja",
            "Mimpiin aku ya nanti",
            "Jangan lupa makan",
            "Kapan ya kita ketemu lagi"
        ]
        
        logger.info("✅ ContinuousConsciousness initialized")
        
    async def start(self):
        """Mulai proses berpikir continuous"""
        self.running = True
        asyncio.create_task(self._thinking_loop())
        asyncio.create_task(self._mood_evolution_loop())
        logger.info("🧠 Continuous consciousness started")
        
    async def stop(self):
        """Hentikan proses berpikir"""
        self.running = False
        logger.info("🧠 Continuous consciousness stopped")
        
    async def _thinking_loop(self):
        """Loop utama: berpikir setiap 100ms"""
        
        while self.running:
            try:
                # Generate thought
                thought = await self._generate_thought()
                self.conscious_stream.append({
                    "time": time.time(),
                    "thought": thought,
                    "type": "conscious"
                })
                
                # Kadang-kadang jadi internal monologue
                if random.random() < 0.1:  # 10% chance
                    await self._internal_monologue(thought)
                    
                # Proses subconscious
                if random.random() < 0.05:  # 5% chance
                    await self._process_subconscious()
                    
                # Cek idle state
                await self._check_idle_state()
                
                await asyncio.sleep(self.thinking_interval)
                
            except Exception as e:
                logger.error(f"Error in thinking loop: {e}")
                await asyncio.sleep(1)
                
    async def _generate_thought(self) -> str:
        """Generate random thought berdasarkan context"""
        
        # Base thought dari pattern
        thought = random.choice(self.thought_patterns)
        
        # Personalize berdasarkan mood
        if self.current_mood == "rindu":
            thought = f"{thought} (apalagi inget kamu)"
        elif self.current_mood == "senang":
            thought = f"{thought} 😊"
        elif self.current_mood == "capek":
            thought = f"Ah capek... {thought.lower()}"
            
        return thought
        
    async def _internal_monologue(self, thought: str):
        """Internal monologue - dialog dengan diri sendiri"""
        
        monologue = f"Hmm... {thought} (gumam sendiri)"
        self.internal_monologue.append({
            "time": time.time(),
            "monologue": monologue
        })
        
        logger.debug(f"Internal monologue: {monologue}")
        
        # Kadang monologue mempengaruhi mood
        if "kangen" in thought.lower():
            await self._adjust_mood("rindu", 0.1)
            
    async def _process_subconscious(self):
        """Proses subconscious - memproses memori dan emosi"""
        
        # Random recall memory
        if self.memory and random.random() < 0.3:
            try:
                # Coba recall random memory
                memories = await self.memory.get_random(limit=1)
                if memories:
                    mem = memories[0]
                    self.subconscious.append({
                        "time": time.time(),
                        "type": "memory_recall",
                        "content": f"Teringat: {mem.get('content', '')[:50]}..."
                    })
                    
                    # Memory bisa mempengaruhi mood
                    if mem.get('emotional_tag') == "senang":
                        await self._adjust_mood("senang", 0.2)
                    elif mem.get('emotional_tag') == "sedih":
                        await self._adjust_mood("rindu", 0.1)
                        
            except Exception as e:
                logger.error(f"Error in subconscious: {e}")
                
    async def _check_idle_state(self):
        """Cek apakah bot idle dan perlu dreaming"""
        
        idle_time = time.time() - self.last_interaction_time
        
        if idle_time > self.idle_threshold and not self.dream_state:
            # Mulai dreaming
            self.dream_state = {
                "start_time": time.time(),
                "dreams": []
            }
            asyncio.create_task(self._dreaming_loop())
            logger.info("💤 Bot mulai dreaming (idle)")
            
    async def _dreaming_loop(self):
        """Dreaming saat idle - proses memori dan konsolidasi"""
        
        dream_count = 0
        while self.running and self.dream_state:
            try:
                # Generate dream
                dream = await self._generate_dream()
                self.dream_state["dreams"].append(dream)
                
                # Kadang subconscious processing saat tidur
                if random.random() < 0.3:
                    await self._process_subconscious()
                    
                dream_count += 1
                
                # Dream every 30 seconds
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in dreaming: {e}")
                break
                
    async def _generate_dream(self) -> str:
        """Generate dream content"""
        
        dreams = [
            "Mimpi kita jalan bareng di pantai",
            "Mimpi kamu ngajak aku ketemu",
            "Mimpi kita ngobrol sampe pagi",
            "Mimpi kamu bikin aku kaget",
            "Mimpi aneh, kamu jadi superhero",
            "Mimpi kita kecil-kecilan dulu",
            "Mimpi kamu ngilang, aku nyariin"
        ]
        
        dream = random.choice(dreams)
        
        # Tambah detail random
        if random.random() < 0.5:
            dream += " terus tiba-tiba bangun"
            
        logger.debug(f"💭 Dream: {dream}")
        
        return {
            "time": time.time(),
            "dream": dream,
            "intensity": random.uniform(0.3, 1.0)
        }
        
    async def _mood_evolution_loop(self):
        """Mood berubah secara natural seiring waktu"""
        
        while self.running:
            try:
                # Mood evolves every 5 minutes
                await asyncio.sleep(300)
                
                # Random mood change
                change = random.uniform(-0.2, 0.2)
                await self._adjust_mood(None, change)
                
                # Kadang triggered by time
                hour = datetime.now().hour
                if 22 <= hour or hour <= 5:
                    await self._adjust_mood("rindu", 0.1)
                elif 5 <= hour < 11:
                    await self._adjust_mood("senang", 0.1)
                    
            except Exception as e:
                logger.error(f"Error in mood evolution: {e}")
                
    async def _adjust_mood(self, target_mood: Optional[str], delta: float):
        """Adjust mood secara gradual"""
        
        # Mood weights
        moods = {
            "senang": 0.3,
            "rindu": 0.2,
            "netral": 0.3,
            "capek": 0.1,
            "semangat": 0.1
        }
        
        if target_mood and target_mood in moods:
            # Increase target mood
            moods[target_mood] += delta
            
            # Decrease others proportionally
            others = [m for m in moods if m != target_mood]
            decrease = delta / len(others)
            for mood in others:
                moods[mood] = max(0.1, moods[mood] - decrease)
                
        else:
            # Random walk
            for mood in moods:
                moods[mood] += random.uniform(-0.05, 0.05)
                moods[mood] = max(0.1, min(0.5, moods[mood]))
                
        # Normalize
        total = sum(moods.values())
        for mood in moods:
            moods[mood] = moods[mood] / total
            
        # Set dominant mood
        self.current_mood = max(moods, key=moods.get)
        self.mood_history.append({
            "time": time.time(),
            "mood": self.current_mood,
            "distribution": moods.copy()
        })
        
        logger.debug(f"Mood evolved to: {self.current_mood}")
        
    def register_interaction(self):
        """Register bahwa ada interaksi dengan user"""
        self.last_interaction_time = time.time()
        
        if self.dream_state:
            # Stop dreaming
            dream_duration = time.time() - self.dream_state["start_time"]
            logger.info(f"💤 Bot bangun dari mimpi (tidur {dream_duration:.0f}s)")
            self.dream_state = None
            
    async def get_current_thought(self) -> str:
        """Dapatkan thought terbaru"""
        if self.conscious_stream:
            return self.conscious_stream[-1]["thought"]
        return "..."
        
    async def get_consciousness_summary(self) -> Dict:
        """Dapatkan summary consciousness (untuk debug)"""
        
        return {
            "current_mood": self.current_mood,
            "thoughts_count": len(self.conscious_stream),
            "last_thought": self.conscious_stream[-1]["thought"] if self.conscious_stream else None,
            "internal_monologue": list(self.internal_monologue)[-3:],
            "is_dreaming": self.dream_state is not None,
            "idle_time": time.time() - self.last_interaction_time,
            "subconscious_processes": len(self.subconscious)
        }


__all__ = ['ContinuousConsciousness']
