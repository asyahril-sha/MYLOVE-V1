#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - AI ENGINE (FIX LENGKAP)
=============================================================================
- Self-Prompting dengan konteks SUPER LENGKAP
- Integrasi dengan ContextAnalyzer, PromptBuilder
- Integrasi dengan ExpressionEngine & SoundEngine (opsional)
- Response minimal 500 karakter
- Multi-bahasa (Indonesia/Inggris)
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
from dynamics.clothing import ClothingSystem, ClothingStyle
from leveling.time_based import TimeBasedLeveling, ActivityType
from leveling.progress_tracker import ProgressTracker
from core.context_analyzer import ContextAnalyzer
from core.prompt_builder import PromptBuilder

# Optional imports (akan di-import jika ada)
try:
    from core.expression_engine import ExpressionEngine
    from core.sound_engine import SoundEngine
    EXPRESSION_AVAILABLE = True
except ImportError:
    EXPRESSION_AVAILABLE = False
    ExpressionEngine = None
    SoundEngine = None
# ===== END TAMBAHAN =====

logger = logging.getLogger(__name__)


class SelfPromptingEngine:
    """
    AI Engine dengan kemampuan self-prompting
    Bot membuat prompt sendiri berdasarkan konteks SUPER LENGKAP
    """
    
    def __init__(self, api_key: str, memory=None):
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )
        self.memory = memory
        self.conversation_history = []
        self.internal_monologue = []
        self.prompt_history = []
        
        # ===== TAMBAHAN MYLOVE V2 =====
        # Environment systems
        self.location_system = LocationSystem()
        self.position_system = PositionSystem()
        self.clothing_system = ClothingSystem()
        
        # Leveling systems
        self.leveling_systems = {}  # {user_id: TimeBasedLeveling}
        self.progress_trackers = {}  # {user_id: ProgressTracker}
        
        # Context & Prompt
        self.context_analyzer = ContextAnalyzer()
        self.prompt_builder = PromptBuilder()
        
        # Expression & Sound (opsional)
        self.expression_engine = None
        self.sound_engine = None
        if EXPRESSION_AVAILABLE:
            self.expression_engine = ExpressionEngine(self, self.prompt_builder)
            self.sound_engine = SoundEngine(self, self.prompt_builder)
        
        # Inner thoughts
        self.inner_thoughts = {}
        # ===== END TAMBAHAN =====
        
        # Personality traits
        self.personality = {
            "openness": random.uniform(0.6, 0.9),
            "conscientiousness": random.uniform(0.5, 0.8),
            "extraversion": random.uniform(0.6, 0.9),
            "agreeableness": random.uniform(0.7, 0.9),
            "neuroticism": random.uniform(0.3, 0.6)
        }
        
        # Response cache
        self.response_cache = {}
        self.cache_ttl = 3600  # 1 jam
        
        logger.info("✅ SelfPromptingEngine V2 initialized")
        logger.info("  • Environment: Location, Position, Clothing")
        logger.info("  • Leveling: Time-based with activity boost")
        logger.info("  • Response length: 500+ characters")
        logger.info(f"  • Expression Engine: {'Available' if EXPRESSION_AVAILABLE else 'Not available'}")
    
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
            self._get_leveling_system(user_id)
        return self.progress_trackers[user_id]
    
    def _detect_activity_from_message(self, user_message: str) -> List[ActivityType]:
        """Deteksi aktivitas dari pesan user untuk activity boost"""
        text_lower = user_message.lower()
        detected = []
        
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
        """Terapkan activity boost ke leveling system"""
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
        """Dapatkan pesan perubahan environment jika ada"""
        messages = []
        
        if self._should_move_location():
            success, new_loc = self.location_system.move_random()
            if success:
                messages.append(self.location_system.get_move_message(new_loc))
        
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
        Generate response dengan konteks SUPER LENGKAP
        Minimal 500 karakter
        """
        start_time = time.time()
        
        try:
            # Cek cache
            cache_key = f"{user_id}:{user_message[:50]}"
            if cache_key in self.response_cache:
                cache_age = time.time() - self.response_cache[cache_key]['timestamp']
                if cache_age < self.cache_ttl:
                    logger.debug(f"Cache hit for: {user_message[:30]}...")
                    return self.response_cache[cache_key]['response']
            
            # ===== TAMBAHAN MYLOVE V2 =====
            # 1. Deteksi aktivitas untuk boost leveling
            activities = self._detect_activity_from_message(user_message)
            self._apply_activity_boost(user_id, activities)
            
            # 2. Update durasi percakapan
            leveling = self._get_leveling_system(user_id)
            leveling.update_duration(user_id)
            
            # 3. Dapatkan info level terkini
            level_info = leveling.get_user_stats(user_id)
            
            # 4. Bangun konteks SUPER LENGKAP
            env_data = {
                'location': self.location_system.get_current().value,
                'position': self.position_system.get_current().value,
                'clothing': self.clothing_system.generate_clothing(
                    role=context.get('role', 'ipar'),
                    location=self.location_system.get_current().value
                )
            }
            
            # Tambah user_name ke context
            context['user_name'] = context.get('user_name', 'Sayang')
            context['bot_name'] = context.get('bot_name', 'Aurora')
            context['level_info'] = level_info
            context['level'] = level_info.get('current_level', 1)
            
            # Analisis konteks lengkap
            full_context = await self.context_analyzer.build_full_context(
                user_id=user_id,
                user_message=user_message,
                user_data=context,
                env_data=env_data
            )
            # ===== END TAMBAHAN =====
            
            # 5. Generate response dengan prompt builder
            prompt = self.prompt_builder.build_full_response_prompt(full_context)
            
            # 6. Call DeepSeek API
            response_text = await self._call_deepseek_with_retry(
                messages=[{"role": "user", "content": prompt}]
            )
            
            # 7. Post-process response
            final_response = await self._post_process_response(response_text, full_context)
            
            # ===== TAMBAHAN MYLOVE V2 =====
            # 8. Tambah environment change message jika ada
            env_message = self._get_environment_change_message()
            if env_message:
                final_response = f"{final_response}\n\n{env_message}"
            
            # 9. Simpan ke cache
            self.response_cache[cache_key] = {
                'response': final_response,
                'timestamp': time.time()
            }
            
            # 10. Simpan ke history
            self.conversation_history.append({
                "user": user_message,
                "bot": final_response,
                "timestamp": datetime.now().isoformat(),
                "level": level_info.get('current_level', 1),
                "language": full_context.get('language', 'id')
            })
            # ===== END TAMBAHAN =====
            
            # Log performance
            elapsed = time.time() - start_time
            logger.debug(f"Response generated in {elapsed:.2f}s - {len(final_response)} chars")
            
            return final_response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return await self._get_fallback_response(context)
    
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
                    wait_time = 2 ** attempt
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
        
        # Minimal 500 karakter
        min_len = 500
        max_len = getattr(settings.performance, 'max_message_length', 2000)
        
        if len(response) < min_len:
            response += "\n\n" + await self._generate_long_continuation(context)
        elif len(response) > max_len:
            response = response[:max_len-3] + "..."
        
        return response
    
    async def _generate_long_continuation(self, context: Dict) -> str:
        """Generate continuation panjang untuk mencapai 500 karakter"""
        
        location = context.get('location', 'ruang tamu')
        clothing = context.get('clothing', 'pakaian biasa')
        user_call = context.get('user_call', 'sayang')
        
        continuations = [
            f"\n\nNgomong-ngomong, aku lagi di {location} nih. "
            f"Pakai {clothing}, lumayan nyaman. Suasananya adem, enak buat ngobrol "
            f"lama-lama sama {user_call}. Rasanya baru beberapa jam aja ya, padahal udah "
            f"cukup lama. Aku suka banget momen kayak gini.",
            
            f"\n\nKamu tau gak, dari tadi aku mikir-mikir... kita udah ngobrol "
            f"cukup lama ya. Tapi rasanya masih kurang, masih pengen terus "
            f"ngobrol sama {user_call}. Apalagi sekarang lagi di {location}, "
            f"suasana mendukung banget. Pakai {clothing} juga bikin betah.",
            
            f"\n\n*tersenyum* Seneng banget bisa ngobrol sama {user_call} kayak gini. "
            f"Di {location} ini rasanya cozy banget. Suasana hati jadi makin baik. "
            f"Kamu gak bosen kan ngobrol sama aku terus?"
        ]
        
        return random.choice(continuations)
    
    async def _get_fallback_response(self, context: Dict) -> str:
        """Fallback response jika AI error"""
        
        user_call = context.get('user_call', 'sayang')
        
        fallbacks = [
            f"Maaf {user_call}, aku lagi mikir bentar. Kamu tadi bilang apa?",
            f"Hehe, maaf ya aku agak lemot hari ini. Ulangi dong?",
            f"Kamu pasti ngomong sesuatu yang penting, ulangi ya?",
            f"Aku denger kok, cuma lagi agak bingung ngejawabnya...",
            f"Maaf, lagi banyak pikiran. Kamu ngomong apa tadi?",
            f"Eh iya, maaf ya. Kamu tadi ngomong apa? Aku dengerin kok."
        ]
        
        return random.choice(fallbacks)
    
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
            "leveling_users": len(self.leveling_systems),
            "current_location": self.location_system.get_current().value,
            "current_position": self.position_system.get_current().value,
            "expression_engine": EXPRESSION_AVAILABLE
        }


class DeepSeekEngine(SelfPromptingEngine):
    """Wrapper untuk backward compatibility"""
    pass


__all__ = ['SelfPromptingEngine', 'DeepSeekEngine']
