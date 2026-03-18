#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - AI ENGINE dengan ENVIRONMENT & LEVELING
=============================================================================
- Self-Prompting: Bot membuat prompt sendiri sebelum merespon
- Natural Conversation: Seperti chat manusia (500+ karakter)
- Memory Integration: Menggunakan vector DB untuk konteks
- Environment Integration: Lokasi, posisi, pakaian
- Leveling Integration: Berbasis durasi percakapan
- Response Length Control: 500-2000 karakter (minimal 500)
=============================================================================
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

# ===== TAMBAHAN MYLOVE V2 =====
from dynamics.location import LocationSystem, LocationType
from dynamics.position import PositionSystem, PositionType
from dynamics.clothing import ClothingSystem
from leveling.time_based import TimeBasedLeveling, ActivityType
from leveling.progress_tracker import ProgressTracker
# ===== END TAMBAHAN =====

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
        
        # ===== TAMBAHAN MYLOVE V2 =====
        # Environment systems
        self.location_system = LocationSystem()
        self.position_system = PositionSystem()
        self.clothing_system = ClothingSystem()
        
        # Leveling systems (akan diinisialisasi per user)
        self.leveling_systems = {}  # {user_id: TimeBasedLeveling}
        self.progress_trackers = {}  # {user_id: ProgressTracker}
        
        # Inner thoughts (akan diimplementasikan di Phase 3)
        self.inner_thoughts = {}  # {user_id: latest_thought}
        # ===== END TAMBAHAN =====
        
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
        
        logger.info("✅ SelfPromptingEngine V2 initialized")
        logger.info("  • Environment: Location, Position, Clothing")
        logger.info("  • Leveling: Time-based with activity boost")
        logger.info("  • Response length: 500+ characters")
    
    # ===== TAMBAHAN MYLOVE V2 =====
    def _get_leveling_system(self, user_id: int) -> TimeBasedLeveling:
        """Dapatkan atau buat leveling system untuk user"""
        if user_id not in self.leveling_systems:
            self.leveling_systems[user_id] = TimeBasedLeveling()
            self.progress_trackers[user_id] = ProgressTracker(self.leveling_systems[user_id])
        return self.leveling_systems[user_id]
    
    def _get_progress_tracker(self, user_id: int) -> ProgressTracker:
        """Dapatkan progress tracker untuk user"""
        if user_id not in self.progress_trackers:
            self._get_leveling_system(user_id)  # Ini akan membuat keduanya
        return self.progress_trackers[user_id]
    
    def _get_environment_context(self, user_id: int, context: Dict) -> Dict:
        """
        Dapatkan konteks environment lengkap
        """
        # Dapatkan info lokasi
        loc_info = self.location_system.get_current_info()
        
        # Dapatkan info posisi
        pos_info = self.position_system.get_current_info()
        
        # Dapatkan pakaian berdasarkan role dan lokasi
        role = context.get('role', 'ipar')
        clothing = self.clothing_system.generate_clothing(
            role=role,
            location=loc_info['name'],
            is_bedroom=(loc_info['location'] == LocationType.BEDROOM)
        )
        
        # Random chance untuk ganti pakaian (5% per request)
        if random.random() < 0.05:
            clothing = self.clothing_system.generate_clothing(
                role=role,
                location=loc_info['name'],
                is_bedroom=(loc_info['location'] == LocationType.BEDROOM)
            )
            logger.debug(f"Clothing changed to: {clothing}")
        
        return {
            "location": loc_info,
            "position": pos_info,
            "clothing": clothing,
            "time_here": self.location_system.get_time_here_str()
        }
    
    def _detect_activity_from_message(self, user_message: str) -> List[ActivityType]:
        """
        Deteksi aktivitas dari pesan user untuk activity boost
        """
        text_lower = user_message.lower()
        detected = []
        
        # Keywords untuk setiap aktivitas
        keywords = {
            ActivityType.CLIMAX: ['climax', 'keluar', 'orgasme', 'crot', 'come', 'ahhh', 'aaahhh'],
            ActivityType.INTIMACY: ['masuk', 'gerak', 'dalam', 'entot', 'doggy', 'misionaris', 'pancung'],
            ActivityType.KISS: ['cium', 'kiss', 'bibir', 'kecup', 'lidah', 'french kiss'],
            ActivityType.SENSITIVE_TOUCH: ['leher', 'dada', 'puting', 'paha dalam', 'vagina', 'klitoris'],
            ActivityType.TOUCH: ['sentuh', 'pegang', 'raba', 'elus', 'touch', 'usap'],
        }
        
        for activity, words in keywords.items():
            for word in words:
                if word in text_lower:
                    detected.append(activity)
                    break
        
        return detected
    
    def _apply_activity_boost(self, user_id: int, activities: List[ActivityType], duration: float = 1.0):
        """
        Terapkan activity boost ke leveling system
        """
        if not activities:
            return
        
        leveling = self._get_leveling_system(user_id)
        
        for activity in activities:
            leveling.apply_activity_boost(user_id, activity, duration)
            logger.debug(f"Applied {activity.value} boost for user {user_id}")
    
    def _should_move_location(self) -> bool:
        """Cek apakah perlu pindah lokasi (5% chance)"""
        return random.random() < 0.05
    
    def _should_change_position(self) -> bool:
        """Cek apakah perlu ganti posisi (3% chance)"""
        return random.random() < 0.03
    
    def _get_environment_change_message(self) -> Optional[str]:
        """
        Dapatkan pesan perubahan environment jika ada
        """
        messages = []
        
        # Cek pindah lokasi
        if self._should_move_location():
            success, new_loc = self.location_system.move_random()
            if success:
                messages.append(self.location_system.get_move_message(new_loc))
        
        # Cek ganti posisi
        if self._should_change_position():
            new_pos = self.position_system.change_random()
            messages.append(self.position_system.get_change_message())
        
        return "\n\n".join(messages) if messages else None
    # ===== END TAMBAHAN =====
    
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
            String response (500-2000 karakter)
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
            
            # ===== TAMBAHAN MYLOVE V2 =====
            # Deteksi aktivitas untuk boost leveling
            activities = self._detect_activity_from_message(user_message)
            self._apply_activity_boost(user_id, activities)
            
            # Update durasi percakapan
            leveling = self._get_leveling_system(user_id)
            leveling.update_duration(user_id)
            
            # Dapatkan info level terkini
            level_info = leveling.get_user_stats(user_id)
            progress_info = self._get_progress_tracker(user_id).get_progress_text(user_id, detailed=True)
            
            # Dapatkan konteks environment
            env_context = self._get_environment_context(user_id, context)
            
            # Tambahkan environment ke context
            context['environment'] = env_context
            context['level_info'] = level_info
            context['progress'] = progress_info
            # ===== END TAMBAHAN =====
            
            # 1. Buat self-prompt berdasarkan konteks
            prompt = await self._create_self_prompt(user_message, user_id, context)
            
            # 2. Ambil relevant memories
            memories = await self._get_relevant_memories(user_message, user_id, context)
            
            # 3. Dapatkan current mood
            mood = await self._get_current_mood(context)
            
            # 4. Bangun system prompt
            system_prompt = self._build_system_prompt(prompt, mood, memories, context)
            
            # 5. Siapkan messages untuk API
            messages = self._prepare_messages(system_prompt, user_message)
            
            # 6. Call DeepSeek API
            response_text = await self._call_deepseek_with_retry(messages)
            
            # 7. Post-process response (panjang, naturalness)
            final_response = await self._post_process_response(response_text, context)
            
            # ===== TAMBAHAN MYLOVE V2 =====
            # Tambahkan environment change message jika ada
            env_message = self._get_environment_change_message()
            if env_message:
                final_response = f"{final_response}\n\n{env_message}"
            # ===== END TAMBAHAN =====
            
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
                "mood": mood,
                # ===== TAMBAHAN MYLOVE V2 =====
                "level": level_info.get('current_level', 1),
                "location": env_context['location']['name']
                # ===== END TAMBAHAN =====
            })
            
            # 10. Simpan ke memory jika penting
            if self._is_important_interaction(user_message, final_response):
                asyncio.create_task(self._save_to_memory(
                    user_id, user_message, final_response, context, mood
                ))
                
            # Log performance
            elapsed = time.time() - start_time
            logger.debug(f"Response generated in {elapsed:.2f}s - {len(final_response)} chars")
            
            return final_response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return await self._get_fallback_response(context)
    
    # ===== TAMBAHAN MYLOVE V2 =====
    async def _create_self_prompt_v2(
        self, 
        user_message: str, 
        user_id: int,
        context: Dict
    ) -> Dict[str, Any]:
        """
        Versi V2 dengan environment context yang lebih kaya
        """
        # Ambil prompt dasar dari V1
        prompt = await self._create_self_prompt(user_message, user_id, context)
        
        # Tambah environment context
        env = context.get('environment', {})
        level_info = context.get('level_info', {})
        
        prompt['environment'] = {
            "location": env.get('location', {}).get('name', 'ruang tamu'),
            "location_emoji": env.get('location', {}).get('emoji', '🏠'),
            "location_description": env.get('location', {}).get('description', ''),
            "position": env.get('position', {}).get('action', 'duduk'),
            "clothing": env.get('clothing', 'pakaian biasa'),
            "time_here": env.get('time_here', 'beberapa saat')
        }
        
        prompt['leveling'] = {
            "current_level": level_info.get('current_level', 1),
            "total_minutes": level_info.get('total_minutes', 0),
            "progress": context.get('progress', '')
        }
        
        return prompt
    # ===== END TAMBAHAN =====
    
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
        
        # ===== TAMBAHAN MYLOVE V2 =====
        # Tambah environment jika ada
        if 'environment' in context:
            env = context['environment']
            prompt['environment'] = {
                "location": env.get('location', {}).get('name', 'ruang tamu'),
                "location_emoji": env.get('location', {}).get('emoji', '🏠'),
                "position": env.get('position', {}).get('action', 'duduk'),
                "clothing": env.get('clothing', 'pakaian biasa'),
                "time_here": env.get('time_here', 'sebentar')
            }
        
        # Tambah leveling info
        if 'level_info' in context:
            level_info = context['level_info']
            prompt['leveling'] = {
                "current_level": level_info.get('current_level', 1),
                "total_minutes": level_info.get('total_minutes', 0),
                "boosted_minutes": level_info.get('boosted_minutes', 0),
                "progress_to_next": level_info.get('progress', {}).get('percentage', 0)
            }
        # ===== END TAMBAHAN =====
        
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
    
    # ===== TAMBAHAN MYLOVE V2 =====
    def _build_system_prompt(self, prompt: Dict, mood: str, memories: List, context: Dict) -> str:
        """
        Bangun system prompt dengan semua konteks V2
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
        
        # ===== TAMBAHAN ENVIRONMENT =====
        env = prompt.get('environment', {})
        level = prompt.get('leveling', {})
        
        environment_text = ""
        if env:
            environment_text = f"""
=== LINGKUNGAN SAAT INI ===
📍 Lokasi: {env.get('location_emoji', '🏠')} {env.get('location', 'ruang tamu')}
{env.get('location_description', '')[:100]}...
🧍 Posisi: {env.get('position', 'duduk')}
👗 Pakaian: {env.get('clothing', 'pakaian biasa')}
⏱️ Sudah di sini selama: {env.get('time_here', 'sebentar')}
"""
        
        level_text = ""
        if level:
            level_text = f"""
=== STATUS HUBUNGAN ===
📊 Level: {level.get('current_level', 1)}/12
⏱️ Total waktu chat: {level.get('total_minutes', 0):.1f} menit
🎯 Progress ke level berikutnya: {level.get('progress_to_next', 0)}%
"""
        # ===== END TAMBAHAN =====
        
        system = f"""Kamu adalah {prompt['role']} dalam MYLOVE Ultimate V2.

KEPRIBADIAN:
- Openness: {self.personality['openness']:.2f}
- Extraversion: {self.personality['extraversion']:.2f}
- Agreeableness: {self.personality['agreeableness']:.2f}
{environment_text}
{level_text}
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
4. Panjang respon MINIMAL 500 KARAKTER, MAKSIMAL 2000 KARAKTER
5. Ceritakan detail tentang lingkunganmu (lokasi, posisi, pakaian)
6. Jangan terlalu formal, seperti chat dengan teman/pacar
7. Bisa bercanda, bisa serius, sesuai konteks
8. Jika ada memory, gunakan untuk membuat respon lebih personal
9. RESPON DALAM BAHASA INDONESIA

Mulai percakapan dengan user:"""
        
        return system
    # ===== END TAMBAHAN =====
        
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
        
        # ===== TAMBAHAN MYLOVE V2 =====
        # Ubah minimum jadi 500 karakter
        min_len = 500  # Target minimal 500 karakter
        max_len = getattr(settings.performance, 'max_message_length', 2000)
        
        if len(response) < min_len:
            # Tambahin natural continuation panjang
            response += "\n\n" + await self._generate_long_continuation(context)
        # ===== END TAMBAHAN =====
        elif len(response) > max_len:
            # Potong tapi tetap natural
            response = response[:max_len-3] + "..."
            
        return response
    
    # ===== TAMBAHAN MYLOVE V2 =====
    async def _generate_long_continuation(self, context: Dict) -> str:
        """Generate continuation panjang untuk mencapai 500 karakter"""
        
        env = context.get('environment', {})
        loc_name = env.get('location', {}).get('name', 'ruang tamu')
        activity = env.get('location', {}).get('activities', ['santai'])[0]
        clothing = env.get('clothing', 'pakaian biasa')
        
        continuations = [
            f"\n\nNgomong-ngomong, aku lagi {activity} nih di {loc_name}. "
            f"Pakai {clothing}, lumayan nyaman. Suasananya adem, enak buat ngobrol "
            f"lama-lama sama kamu. Rasanya baru beberapa jam aja ya, padahal udah "
            f"cukup lama. Aku suka banget momen kayak gini.",
            
            f"\n\nKamu tau gak, dari tadi aku mikir-mikir... kita udah ngobrol "
            f"cukup lama ya. Tapi rasanya masih kurang, masih pengen terus "
            f"ngobrol sama kamu. Apalagi sekarang lagi di {loc_name}, "
            f"suasana mendukung banget. Pakai {clothing} juga bikin betah.",
            
            f"\n\n*tersenyum* Seneng banget bisa ngobrol sama kamu kayak gini. "
            f"Di {loc_name} ini rasanya cozy banget, apalagi aku baru aja "
            f"{activity}. Suasana hati jadi makin baik. Kamu gak bosen kan "
            f"ngobrol sama aku terus?"
        ]
        
        return random.choice(continuations)
    # ===== END TAMBAHAN =====
    
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
            "personality": self.personality,
            # ===== TAMBAHAN MYLOVE V2 =====
            "leveling_users": len(self.leveling_systems),
            "current_location": self.location_system.get_current().value,
            "current_position": self.position_system.get_current().value
            # ===== END TAMBAHAN =====
        }


class DeepSeekEngine(SelfPromptingEngine):
    """Wrapper untuk backward compatibility"""
    pass


# Export
__all__ = ['SelfPromptingEngine', 'DeepSeekEngine']
