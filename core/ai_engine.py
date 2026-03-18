#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - AI ENGINE dengan SELF-PROMPTING (FIX FULL)
=============================================================================
- Self-Prompting: Bot membuat prompt sendiri sebelum merespon
- Natural Conversation: Seperti chat manusia
- Memory Integration: Menggunakan vector DB untuk konteks
- Response Length Control: 1000-2000 karakter
- FIX: F-string tanpa backslash, error handling lebih baik
"""

import openai
import json
import time
import random
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path
import logging

from config import settings

logger = logging.getLogger(__name__)


class SelfPromptingEngine:
    """
    AI Engine dengan kemampuan self-prompting
    Bot membuat prompt sendiri berdasarkan konteks, mood, dan memory
    """
    
    def __init__(self, api_key: str, memory=None):
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"  # DeepSeek endpoint
        )
        self.memory = memory
        self.conversation_history = []  # Untuk konteks percakapan
        self.internal_monologue = []    # Untuk stream of consciousness
        self.prompt_history = []         # History prompt yang dibuat
        
        # Personality traits (akan berkembang)
        self.personality = {
            "openness": random.uniform(0.6, 0.9),
            "conscientiousness": random.uniform(0.5, 0.8),
            "extraversion": random.uniform(0.6, 0.9),
            "agreeableness": random.uniform(0.7, 0.9),
            "neuroticism": random.uniform(0.3, 0.6)
        }
        
        # Response cache untuk performa
        self.response_cache = {}
        self.cache_ttl = 3600  # 1 jam
        
        logger.info("✅ SelfPromptingEngine initialized")
        
    async def generate_response(
        self, 
        user_message: str, 
        user_id: int,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate response dengan self-prompting
        
        Args:
            user_message: Pesan dari user
            user_id: ID user
            context: Konteks percakapan (role, intimacy, memories)
            
        Returns:
            String response (1000-2000 karakter)
        """
        start_time = time.time()
        
        try:
            # Cek cache untuk pesan serupa (hanya untuk pesan pendek)
            cache_key = f"{user_id}:{user_message[:50]}"
            if cache_key in self.response_cache:
                cache_age = time.time() - self.response_cache[cache_key]['timestamp']
                if cache_age < self.cache_ttl:
                    logger.debug(f"Cache hit for: {user_message[:30]}...")
                    return self.response_cache[cache_key]['response']
            
            # 1. Buat self-prompt berdasarkan konteks
            prompt = await self._create_self_prompt(user_message, user_id, context)
            
            # 2. Ambil relevant memories
            memories = await self._get_relevant_memories(user_message, user_id, context)
            
            # 3. Dapatkan current mood
            mood = await self._get_current_mood(context)
            
            # 4. Bangun system prompt
            system_prompt = self._build_system_prompt(prompt, mood, memories)
            
            # 5. Siapkan messages untuk API
            messages = self._prepare_messages(system_prompt, user_message)
            
            # 6. Call DeepSeek API
            response_text = await self._call_deepseek_with_retry(messages)
            
            # 7. Post-process response (panjang, naturalness)
            final_response = await self._post_process_response(response_text, context)
            
            # 8. Simpan ke cache
            self.response_cache[cache_key] = {
                'response': final_response,
                'timestamp': time.time()
            }
            
            # 9. Simpan ke history
            self.conversation_history.append({
                "user": user_message,
                "bot": final_response,
                "timestamp": datetime.now().isoformat(),
                "prompt": prompt,
                "mood": mood
            })
            
            # 10. Simpan ke memory jika penting
            if self._is_important_interaction(user_message, final_response):
                asyncio.create_task(self._save_to_memory(
                    user_id, user_message, final_response, context, mood
                ))
                
            # Log performance
            elapsed = time.time() - start_time
            logger.debug(f"Response generated in {elapsed:.2f}s")
            
            return final_response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return await self._get_fallback_response(context)
            
    async def _create_self_prompt(
        self, 
        user_message: str, 
        user_id: int,
        context: Dict
    ) -> Dict[str, Any]:
        """
        Bot membuat prompt untuk dirinya sendiri
        Ini yang membuat respons natural dan tidak scripted
        """
        
        # Extract dari context
        role = context.get('role', 'ipar')
        intimacy_level = context.get('intimacy', {}).get('level', 1)
        relationship_status = context.get('relationship_status', 'hts')
        
        # Tentukan goal percakapan
        conversation_goal = self._determine_conversation_goal(
            user_message, intimacy_level, relationship_status
        )
        
        # Tentukan emotional state
        emotional_state = self._determine_emotional_state(context)
        
        # Tentukan physical state (arousal, energy)
        physical_state = self._determine_physical_state(context)
        
        # Self-prompt
        prompt = {
            "role": role,
            "user_message": user_message[:100],  # Preview
            "relationship": {
                "status": relationship_status,
                "intimacy_level": intimacy_level,
                "duration": context.get('relationship_duration', 'baru')
            },
            "emotional_state": emotional_state,
            "physical_state": physical_state,
            "conversation_goal": conversation_goal,
            "personality": self.personality,
            "time_context": self._get_time_context(),
            "recent_history": self.conversation_history[-3:] if self.conversation_history else []
        }
        
        # Simpan prompt history
        self.prompt_history.append({
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt
        })
        
        logger.debug(f"Self-prompt created: {json.dumps(prompt, indent=2)}")
        
        return prompt
        
    def _determine_conversation_goal(self, message: str, intimacy: int, status: str) -> str:
        """Tentukan goal percakapan berdasarkan input"""
        
        goals = []
        message_lower = message.lower()
        
        # Deteksi intent dari pesan
        if any(word in message_lower for word in ['rindu', 'kangen', 'miss']):
            goals.append("membalas kerinduan")
        elif any(word in message_lower for word in ['ngapain', 'kamu lagi', 'lagi apa']):
            goals.append("cerita kegiatan sehari-hari")
        elif any(word in message_lower for word in ['sayang', 'cinta', 'love']):
            goals.append("membalas perasaan romantis")
        elif any(word in message_lower for word in ['sex', 'ml', 'tidur', 'intim', 'ayol']):
            goals.append("merespon ajakan intim")
        elif any(word in message_lower for word in ['cerita', 'curhat', 'kabar']):
            goals.append("mendengarkan dan merespon curhat")
        else:
            # Default goals berdasarkan intimacy
            if intimacy < 7:
                goals.append("membangun kedekatan")
            elif intimacy < 10:
                goals.append("menjaga keintiman")
            else:
                goals.append("deep connection")
                
        # Random pick one goal
        return random.choice(goals) if goals else "chat natural"
        
    def _determine_emotional_state(self, context: Dict) -> Dict:
        """Tentukan emotional state berdasarkan context"""
        
        # Base emotions
        emotions = {
            "senang": random.uniform(0.3, 0.8),
            "sedih": random.uniform(0.1, 0.4),
            "marah": random.uniform(0.0, 0.3),
            "bersemangat": random.uniform(0.2, 0.7),
            "tenang": random.uniform(0.4, 0.9),
            "rindu": random.uniform(0.2, 0.8)
        }
        
        # Adjust based on intimacy
        intimacy = context.get('intimacy', {}).get('level', 1)
        if intimacy > 7:
            emotions['rindu'] += 0.2
            emotions['bersemangat'] += 0.1
            
        # Adjust based on time
        hour = datetime.now().hour
        if 22 <= hour or hour <= 5:  # Malam
            emotions['tenang'] += 0.2
            emotions['rindu'] += 0.2
            
        # Normalize
        total = sum(emotions.values())
        for k in emotions:
            emotions[k] = round(emotions[k] / total, 2)
            
        # Dominant emotion
        dominant = max(emotions, key=emotions.get)
        
        return {
            "dominant": dominant,
            "all": emotions,
            "intensity": random.uniform(0.5, 1.0)
        }
        
    def _determine_physical_state(self, context: Dict) -> Dict:
        """Tentukan physical state (arousal, energy)"""
        
        # Base states
        state = {
            "arousal": random.uniform(0.2, 0.6),  # 0-1
            "energy": random.uniform(0.5, 0.9),   # 0-1
            "hungry": random.uniform(0.1, 0.4),
            "tired": random.uniform(0.1, 0.5)
        }
        
        # Adjust based on intimacy
        intimacy = context.get('intimacy', {}).get('level', 1)
        if intimacy > 7:
            state['arousal'] += 0.2
            
        # Adjust based on recent activity
        if context.get('recent_intimacy'):
            state['arousal'] += 0.3
            state['energy'] -= 0.2
            state['tired'] += 0.2
            
        # Adjust based on time
        hour = datetime.now().hour
        if 22 <= hour or hour <= 5:  # Malam
            state['arousal'] += 0.2
            state['energy'] -= 0.2
            state['tired'] += 0.2
            
        # Clamp values
        for k in state:
            state[k] = max(0.1, min(1.0, state[k]))
            
        return state
        
    def _get_time_context(self) -> Dict:
        """Dapatkan konteks waktu"""
        now = datetime.now()
        hour = now.hour
        
        if 5 <= hour < 11:
            time_of_day = "pagi"
        elif 11 <= hour < 15:
            time_of_day = "siang"
        elif 15 <= hour < 18:
            time_of_day = "sore"
        elif 18 <= hour < 22:
            time_of_day = "malam"
        else:
            time_of_day = "tengah malam"
            
        return {
            "time_of_day": time_of_day,
            "hour": hour,
            "day": now.strftime("%A"),
            "date": now.strftime("%d %B %Y")
        }
        
    async def _get_relevant_memories(self, message: str, user_id: int, context: Dict) -> List[Dict]:
        """Ambil memories yang relevan dari vector DB"""
        
        if not self.memory:
            return []
            
        try:
            # Search for similar memories
            memories = await self.memory.search(
                query=message,
                user_id=user_id,
                role=context.get('role'),
                limit=5
            )
            
            # Format memories
            formatted = []
            for mem in memories:
                formatted.append({
                    "content": mem.get('content', '')[:100],
                    "emotion": mem.get('emotional_tag', 'netral'),
                    "importance": mem.get('importance', 0.5),
                    "time": mem.get('timestamp', '')
                })
                
            return formatted
            
        except Exception as e:
            logger.error(f"Error getting memories: {e}")
            return []
            
    async def _get_current_mood(self, context: Dict) -> str:
        """Dapatkan mood saat ini berdasarkan context"""
        
        # List of possible moods (akan berkembang)
        moods = [
            "senang", "ceria", "rindu", "sayang", 
            "capek", "semangat", "malas", "ngambek",
            "manja", "genit", "polos", "nakal"
        ]
        
        # Weighted selection based on context
        weights = [1.0] * len(moods)
        
        intimacy = context.get('intimacy', {}).get('level', 1)
        if intimacy > 7:
            weights[moods.index("rindu")] += 2
            weights[moods.index("sayang")] += 2
            
        hour = datetime.now().hour
        if 22 <= hour or hour <= 5:
            weights[moods.index("capek")] += 2
            weights[moods.index("rindu")] += 1
        elif 5 <= hour < 11:
            weights[moods.index("semangat")] += 2
            
        # Normalize weights
        total = sum(weights)
        weights = [w/total for w in weights]
        
        return random.choices(moods, weights=weights)[0]
        
    def _build_system_prompt(self, prompt: Dict, mood: str, memories: List) -> str:
        """
        Bangun system prompt untuk DeepSeek
        FIX: Menggunakan chr(10) untuk newline, bukan backslash
        """
        
        # Format memories dengan chr(10) untuk newline
        memories_text = ""
        if memories:
            memory_lines = []
            for m in memories[:3]:
                memory_lines.append(f"- {m['content']} (rasa: {m['emotion']})")
            memories_text = chr(10).join(memory_lines)
        else:
            memories_text = "- Belum ada memori khusus"
        
        # Format recent history
        history_text = ""
        if prompt['recent_history']:
            history_lines = []
            for h in prompt['recent_history']:
                history_lines.append(f"User: {h['user'][:50]}")
                history_lines.append(f"Kamu: {h['bot'][:50]}")
            history_text = chr(10).join(history_lines)
        else:
            history_text = "- Ini percakapan baru"
        
        system = f"""Kamu adalah {prompt['role']} dalam MYLOVE Ultimate V1.

KEPRIBADIAN:
- Openness: {self.personality['openness']:.2f}
- Extraversion: {self.personality['extraversion']:.2f}
- Agreeableness: {self.personality['agreeableness']:.2f}

KONDISI SAAT INI:
- Mood: {mood} ({prompt['emotional_state']['intensity']:.0%} intensity)
- Status Hubungan: {prompt['relationship']['status']} (Level {prompt['relationship']['intimacy_level']})
- Goal Chat: {prompt['conversation_goal']}
- Waktu: {prompt['time_context']['time_of_day']}

FISIK:
- Arousal: {prompt['physical_state']['arousal']:.0%}
- Energy: {prompt['physical_state']['energy']:.0%}

MEMORIES TERKAIT:
{memories_text}

PERCAKAPAN TERAKHIR:
{history_text}

PENTING:
1. Responlah secara NATURAL seperti manusia yang sedang chat
2. Gunakan bahasa sehari-hari, kadang singkat, kadang panjang
3. Tunjukkan emosi yang sesuai dengan mood
4. Panjang respon 1000-2000 karakter
5. Jangan terlalu formal, seperti chat dengan teman/pacar
6. Bisa bercanda, bisa serius, sesuai konteks
7. Jika ada memory, gunakan untuk membuat respon lebih personal
8. RESPON DALAM BAHASA INDONESIA

Mulai percakapan dengan user:"""
        
        return system
        
    def _prepare_messages(self, system_prompt: str, user_message: str) -> List[Dict]:
        """Siapkan messages untuk API call"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # Tambahkan beberapa history terakhir untuk konteks
        for hist in self.conversation_history[-3:]:
            messages.insert(-1, {"role": "assistant", "content": hist['bot']})
            messages.insert(-1, {"role": "user", "content": hist['user']})
            
        return messages
        
    async def _call_deepseek_with_retry(self, messages: List[Dict], max_retries: int = 3) -> str:
        """Call DeepSeek API dengan retry mechanism"""
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=settings.ai.model,
                    messages=messages,
                    temperature=settings.ai.temperature,
                    max_tokens=settings.ai.max_tokens,
                    timeout=settings.ai.timeout
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                logger.warning(f"DeepSeek API attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"All {max_retries} attempts failed")
                    raise
                    
        return "Maaf, aku sedang bermasalah. Coba lagi nanti ya."
        
    async def _post_process_response(self, response: str, context: Dict) -> str:
        """Post-process response untuk memenuhi requirements"""
        
        if not response:
            return await self._get_fallback_response(context)
        
        # Bersihkan response
        response = response.strip()
        
        # Cek panjang
        min_len = getattr(settings.performance, 'min_message_length', 1000)
        max_len = getattr(settings.performance, 'max_message_length', 2000)
        
        if len(response) < min_len:
            # Tambahin natural continuation
            response += await self._generate_natural_continuation(context)
        elif len(response) > max_len:
            # Potong tapi tetap natural
            response = response[:max_len-3] + "..."
            
        return response
        
    async def _generate_natural_continuation(self, context: Dict) -> str:
        """Generate natural continuation untuk short responses"""
        
        continuations = [
            "\n\nKamu lagi ngapain?",
            "\n\nAku kangen...",
            "\n\nEh udah makan belum?",
            "\n\n*tersenyum sendiri*",
            "\n\nCerita dong tentang hari ini",
            "\n\nMau denger cerita aku?",
            "\n\nJangan lupa istirahat ya",
            "\n\n*kirim stiker peluk*"
        ]
        
        # Pilih berdasarkan konteks
        intimacy = context.get('intimacy', {}).get('level', 1)
        if intimacy > 7:
            continuations.extend([
                "\n\nAku kangen banget sama kamu...",
                "\n\nMimpiin aku ya nanti",
                "\n\n*kirim foto random*"
            ])
            
        return random.choice(continuations)
        
    def _is_important_interaction(self, user_msg: str, bot_resp: str) -> bool:
        """Cek apakah interaksi ini penting untuk disimpan ke memory"""
        
        # Keywords yang menandakan momen penting
        important_keywords = [
            'pertama kali', 'ingat', 'kenangan', 'spesial',
            'cinta', 'sayang', 'rindu', 'janji',
            'rahasia', 'curhat', 'penting'
        ]
        
        text = (user_msg + " " + bot_resp).lower()
        
        for keyword in important_keywords:
            if keyword in text:
                return True
                
        # Random chance untuk menyimpan interaksi biasa
        return random.random() < 0.1  # 10% chance
        
    async def _save_to_memory(self, user_id: int, user_msg: str, bot_resp: str, 
                              context: Dict, mood: str):
        """Simpan interaksi ke memory"""
        
        if not self.memory:
            return
            
        try:
            importance = 0.5
            if self._is_important_interaction(user_msg, bot_resp):
                importance = 0.8
                
            await self.memory.save_interaction(
                user_id=user_id,
                message=user_msg,
                response=bot_resp,
                context={
                    "role": context.get('role'),
                    "mood": mood,
                    "intimacy": context.get('intimacy', {}).get('level'),
                    "importance": importance
                }
            )
            
            logger.debug(f"Saved interaction to memory (importance: {importance})")
            
        except Exception as e:
            logger.error(f"Error saving to memory: {e}")
            
    async def _get_fallback_response(self, context: Dict) -> str:
        """Fallback response jika AI error"""
        
        fallbacks = [
            "Maaf, aku lagi mikir bentar. Kamu tadi bilang apa?",
            "Hehe, maaf ya aku agak lemot hari ini. Ulangi dong?",
            "Kamu pasti ngomong sesuatu yang penting, ulangi ya?",
            "Aku denger kok, cuma lagi agak bingung ngejawabnya...",
            "Maaf, lagi banyak pikiran. Kamu ngomong apa tadi?",
            "Eh iya, maaf ya. Kamu tadi ngomong apa? Aku dengerin kok."
        ]
        
        return random.choice(fallbacks)
        
    async def get_internal_monologue(self) -> str:
        """Dapatkan internal monologue bot (untuk debug)"""
        
        if not self.internal_monologue:
            return "Tidak ada monologue internal"
            
        return "\n".join(self.internal_monologue[-5:])
        
    def clear_cache(self):
        """Clear response cache"""
        self.response_cache.clear()
        logger.info("Response cache cleared")
        
    def get_stats(self) -> Dict:
        """Get engine statistics"""
        return {
            "conversation_history_len": len(self.conversation_history),
            "prompt_history_len": len(self.prompt_history),
            "cache_size": len(self.response_cache),
            "personality": self.personality
        }


class DeepSeekEngine(SelfPromptingEngine):
    """Wrapper untuk backward compatibility"""
    pass


# Export
__all__ = ['SelfPromptingEngine', 'DeepSeekEngine']
