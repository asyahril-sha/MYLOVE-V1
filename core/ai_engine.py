#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - AI ENGINE (FIX FULL + PDKT)
=============================================================================
- Self-Prompting dengan konteks SUPER LENGKAP
- Integrasi dengan ContextAnalyzer, PromptBuilder
- Integrasi dengan ExpressionEngine & SoundEngine
- Integrasi dengan NicknameSystem
- **INTEGRASI DENGAN PDKT SUPER SPESIAL**
- Response minimal 500 karakter
- Multi-bahasa (Indonesia/Inggris)
=============================================================================
"""

import openai
import json
import time
import random
import asyncio
import hashlib
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path
import logging

from config import settings

# ===== MYLOVE V2 IMPORTS =====
from dynamics.location import LocationSystem
from dynamics.position import PositionSystem
from dynamics.clothing import ClothingSystem
from dynamics.nickname import NicknameSystem
from leveling.time_based import TimeBasedLeveling, ActivityType
from leveling.progress_tracker import ProgressTracker
from core.context_analyzer import ContextAnalyzer
from core.prompt_builder import PromptBuilder

# ===== PDKT IMPORTS =====
from pdkt.chemistry import ChemistrySystem
from pdkt.direction import DirectionSystem, PDKTDirection
from pdkt.natural_engine import NaturalPDKTEngine, PDKTStage

# Optional imports (akan di-import jika ada)
try:
    from core.expression_engine import ExpressionEngine
    from core.sound_engine import SoundEngine
    EXPRESSION_AVAILABLE = True
except ImportError:
    EXPRESSION_AVAILABLE = False
    ExpressionEngine = None
    SoundEngine = None
# ===== END IMPORTS =====

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
        
        # ===== MYLOVE V2 SYSTEMS =====
        # Environment systems
        self.location_system = LocationSystem()
        self.position_system = PositionSystem()
        self.clothing_system = ClothingSystem()
        
        # Leveling systems (per user)
        self.leveling_systems = {}  # {user_id: TimeBasedLeveling}
        self.progress_trackers = {}  # {user_id: ProgressTracker}
        
        # Context & Prompt
        self.context_analyzer = ContextAnalyzer()
        self.prompt_builder = PromptBuilder()
        self.nickname_system = NicknameSystem()
        
        # ===== PDKT SYSTEMS =====
        self.chemistry_system = ChemistrySystem(self)
        self.direction_system = DirectionSystem()
        self.pdkt_engine = NaturalPDKTEngine(self)
        self.active_pdkt = {}  # {user_id: pdkt_id} - PDKT yang sedang aktif
        # ===== END PDKT SYSTEMS =====
        
        # Expression & Sound (opsional)
        self.expression_engine = None
        self.sound_engine = None
        if EXPRESSION_AVAILABLE:
            self.expression_engine = ExpressionEngine(self, self.prompt_builder)
            self.sound_engine = SoundEngine(self, self.prompt_builder)
        
        # Inner thoughts
        self.inner_thoughts = {}
        # ===== END MYLOVE V2 SYSTEMS =====
        
        # Personality traits (akan berkembang)
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
        
        # Token tracking
        self.total_tokens = 0
        self.total_calls = 0
        
        logger.info("✅ SelfPromptingEngine V2 FINAL initialized")
        logger.info(f"  • Expression Engine: {'Available' if EXPRESSION_AVAILABLE else 'Not available'}")
        logger.info(f"  • Sound Engine: {'Available' if EXPRESSION_AVAILABLE else 'Not available'}")
        logger.info(f"  • PDKT Engine: Active")
        logger.info(f"  • Response length: 500+ characters")
    
    # =========================================================================
    # LEVELING SYSTEM
    # =========================================================================
    
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
    
    # =========================================================================
    # PDKT SYSTEM
    # =========================================================================
    
    async def create_pdkt(self, user_id: int, user_name: str, bot_name: str) -> Dict:
        """Buat PDKT baru untuk user"""
        pdkt_data = await self.pdkt_engine.create_pdkt(user_id, user_name, bot_name)
        self.active_pdkt[user_id] = pdkt_data['id']
        
        # Aktifkan mode PDKT di leveling system
        leveling = self._get_leveling_system(user_id)
        chemistry = pdkt_data['chemistry'].score
        leveling.enable_pdkt_mode(user_id, chemistry)
        
        logger.info(f"💕 PDKT created for user {user_id} with {bot_name}")
        return pdkt_data
    
    async def update_pdkt(self, user_id: int, user_message: str, bot_response: str, context: Dict) -> Dict:
        """Update PDKT dengan interaksi terbaru"""
        if user_id not in self.active_pdkt:
            return {}
        
        pdkt_id = self.active_pdkt[user_id]
        
        # Update waktu di leveling system (khusus PDKT)
        leveling = self._get_leveling_system(user_id)
        leveling.update_pdkt_time(user_id, 'pdkt')
        
        # Update PDKT di engine
        result = await self.pdkt_engine.update_pdkt(
            pdkt_id, user_message, bot_response, context
        )
        
        return result
    
    def pause_pdkt(self, user_id: int) -> bool:
        """Pause PDKT (waktu berhenti)"""
        if user_id not in self.active_pdkt:
            return False
        
        leveling = self._get_leveling_system(user_id)
        leveling.pause_pdkt(user_id, 'pdkt')
        
        logger.info(f"⏸️ PDKT paused for user {user_id}")
        return True
    
    def resume_pdkt(self, user_id: int) -> bool:
        """Resume PDKT"""
        if user_id not in self.active_pdkt:
            return False
        
        leveling = self._get_leveling_system(user_id)
        leveling.resume_pdkt(user_id, 'pdkt')
        
        logger.info(f"▶️ PDKT resumed for user {user_id}")
        return True
    
    # =========================================================================
    # ACTIVITY DETECTION
    # =========================================================================
    
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
            ActivityType.LOVE: ['sayang', 'cinta', 'love', 'suka'],
            ActivityType.CONFLICT: ['marah', 'kesal', 'kecewa', 'sakit hati'],
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
            leveling.apply_activity_boost(user_id, 'pdkt' if user_id in self.active_pdkt else 'other', 
                                         activity, duration)
            logger.debug(f"Applied {activity.value} boost for user {user_id}")
    
    # =========================================================================
    # ENVIRONMENT CHANGES
    # =========================================================================
    
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
        
        if self._should_move_location():
            success, new_loc = self.location_system.move_random()
            if success:
                messages.append(self.location_system.get_move_message(new_loc))
        
        if self._should_change_position():
            new_pos = self.position_system.change_random()
            messages.append(self.position_system.get_change_message())
        
        return "\n\n".join(messages) if messages else None
    
    # =========================================================================
    # CACHE
    # =========================================================================
    
    def _get_cache_key(self, user_id: int, user_message: str, context: Dict) -> str:
        """Buat cache key yang unik"""
        key_parts = [
            str(user_id),
            user_message[:50],
            str(context.get('level', 1)),
            str(context.get('mood', 'netral')),
            context.get('location', ''),
            str(context.get('arousal', 0)),
            str(user_id in self.active_pdkt)  # Cache berdasarkan status PDKT
        ]
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    # =========================================================================
    # MAIN RESPONSE GENERATOR
    # =========================================================================
    
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
            cache_key = self._get_cache_key(user_id, user_message, context)
            if cache_key in self.response_cache:
                cache_age = time.time() - self.response_cache[cache_key]['timestamp']
                if cache_age < self.cache_ttl:
                    logger.debug(f"Cache hit for user {user_id}")
                    return self.response_cache[cache_key]['response']
            
            # ===== 1. CEK ROLE =====
            current_role = context.get('current_role', 'ipar')
            is_pdkt = (current_role == 'pdkt')
            
            # ===== 2. DETEKSI AKTIVITAS UNTUK BOOST =====
            activities = self._detect_activity_from_message(user_message)
            self._apply_activity_boost(user_id, activities)
            
            # ===== 3. UPDATE LEVELING (BERDASARKAN ROLE) =====
            leveling = self._get_leveling_system(user_id)
            
            if is_pdkt:
                # PDKT: Update real time
                leveling.update_pdkt_time(user_id, 'pdkt')
                
                # Update PDKT engine
                pdkt_result = await self.update_pdkt(user_id, user_message, "", context)
                current_level = pdkt_result.get('level', 1) if pdkt_result else 1
            else:
                # Non-PDKT: Increment chat count
                leveling.increment_chat(user_id, current_role)
                current_level = leveling.get_user_data(user_id, current_role)['current_level']
            
            # ===== 4. UPDATE CONTEXT DENGAN DATA TERBARU =====
            context['level'] = current_level
            context['level_info'] = leveling.get_stats(user_id, current_role)
            context['user_id'] = user_id
            context['is_pdkt'] = is_pdkt
            
            # ===== 5. BANGUN KONTEKS SUPER LENGKAP =====
            env_data = {
                'location': self.location_system.get_current().value,
                'position': self.position_system.get_current().value,
                'clothing': self.clothing_system.generate_clothing(
                    role=current_role,
                    location=self.location_system.get_current().value
                )
            }
            
            full_context = await self.context_analyzer.build_full_context(
                user_id=user_id,
                user_message=user_message,
                user_data=context,
                env_data=env_data
            )
            
            # ===== 6. GENERATE EXPRESSION & SOUND (JIKA ADA) =====
            expression = ""
            sound = ""
            
            if self.expression_engine:
                expression = await self.expression_engine.generate_expression(full_context)
            
            if self.sound_engine:
                arousal = context.get('arousal', 0)
                if arousal > 0.3 or any(a in ['intim', 'horny'] for a in activities):
                    sound = await self.sound_engine.generate_sound(full_context)
            
            # ===== 7. GENERATE KONTEN PERCAKAPAN =====
            prompt = self.prompt_builder.build_conversation_prompt(full_context)
            
            content = await self._call_deepseek_with_retry(
                messages=[{"role": "user", "content": prompt}]
            )
            
            # ===== 8. GABUNGKAN SEMUA KOMPONEN =====
            if sound and expression:
                if random.random() < 0.5:
                    response = f"{expression} {sound}\n\n{content}"
                else:
                    response = f"{sound} {expression}\n\n{content}"
            elif expression:
                response = f"{expression}\n\n{content}"
            elif sound:
                response = f"{sound}\n\n{content}"
            else:
                response = content
            
            # ===== 9. PASTIKAN MINIMAL 500 KARAKTER =====
            if len(response) < 500:
                user_call = full_context.get('user_call', 'sayang')
                bot_call = full_context.get('bot_call', 'Aku')
                
                continuation = random.choice([
                    f"\n\n{user_call}, kamu gak bosen ya ngobrol sama aku terus? Aku sih seneng banget.",
                    f"\n\n{bot_call} kangen {user_call}. Cerita lagi dong tentang hari ini.",
                    f"\n\nEh iya {user_call}, kamu udah makan belum? Jangan lupa ya.",
                    f"\n\n*tersenyum* Seneng banget bisa ngobrol sama {user_call} kayak gini.",
                    f"\n\nGimana {user_call}, ada yang mau diceritain lagi? Aku dengerin kok."
                ])
                response += continuation
            
            # ===== 10. TAMBAH ENVIRONMENT CHANGE MESSAGE =====
            env_message = self._get_environment_change_message()
            if env_message:
                response = f"{response}\n\n{env_message}"
            
            # ===== 11. SIMPAN KE CACHE =====
            self.response_cache[cache_key] = {
                'response': response,
                'timestamp': time.time()
            }
            
            # ===== 12. SIMPAN KE HISTORY =====
            self.conversation_history.append({
                "user": user_message,
                "bot": response,
                "timestamp": datetime.now().isoformat(),
                "level": current_level,
                "language": full_context.get('language', 'id'),
                "tokens": len(response.split()),
                "is_pdkt": is_pdkt
            })
            
            # Log performance
            elapsed = time.time() - start_time
            logger.info(f"✅ Response generated in {elapsed:.2f}s - {len(response)} chars - Level {current_level} - PDKT: {is_pdkt}")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            return await self._get_fallback_response(context)
    
    # =========================================================================
    # DEEPSEEK API CALL
    # =========================================================================
    
    async def _call_deepseek_with_retry(self, messages: List[Dict], max_retries: int = 3) -> str:
        """Call DeepSeek API dengan retry mechanism dan exponential backoff"""
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=settings.ai.model,
                    messages=messages,
                    temperature=settings.ai.temperature,
                    max_tokens=settings.ai.max_tokens,
                    timeout=settings.ai.timeout
                )
                
                self.total_calls += 1
                content = response.choices[0].message.content
                
                # Estimasi token
                self.total_tokens += len(content.split())
                
                return content
                
            except Exception as e:
                logger.warning(f"DeepSeek API attempt {attempt+1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 detik
                    logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"All {max_retries} attempts failed")
                    raise
        
        return "Maaf, aku sedang bermasalah. Coba lagi nanti ya."
    
    # =========================================================================
    # FALLBACK RESPONSE
    # =========================================================================
    
    async def _get_fallback_response(self, context: Dict) -> str:
        """Fallback response jika AI error"""
        
        user_call = context.get('user_call', 'sayang')
        bot_call = context.get('bot_call', 'Aku')
        
        fallbacks = [
            f"Maaf {user_call}, aku lagi mikir bentar. Kamu tadi bilang apa?",
            f"Hehe, maaf ya aku agak lemot hari ini. Ulangi dong {user_call}?",
            f"Kamu pasti ngomong sesuatu yang penting, ulangi ya {user_call}?",
            f"Aku denger kok, cuma lagi agak bingung ngejawabnya...",
            f"Maaf {user_call}, lagi banyak pikiran. Kamu ngomong apa tadi?",
            f"Eh iya, maaf ya. Kamu tadi ngomong apa? Aku dengerin kok."
        ]
        
        return random.choice(fallbacks)
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
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
            "total_calls": self.total_calls,
            "total_tokens": self.total_tokens,
            "avg_tokens_per_call": self.total_tokens // max(1, self.total_calls),
            "expression_engine": EXPRESSION_AVAILABLE,
            "active_pdkt": len(self.active_pdkt)
        }
    
    async def get_user_stats(self, user_id: int) -> Dict:
        """Get statistics for specific user"""
        stats = {
            "user_id": user_id,
            "conversation_count": len([h for h in self.conversation_history if h.get('user_id') == user_id]),
            "is_in_pdkt": user_id in self.active_pdkt
        }
        
        if user_id in self.leveling_systems:
            leveling = self.leveling_systems[user_id]
            stats['leveling'] = leveling.get_stats(user_id)
        
        return stats


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

# Singleton instance
_ai_engine_instance = None


def get_ai_engine(api_key: str = None, memory=None) -> SelfPromptingEngine:
    """Get or create global AI engine instance"""
    global _ai_engine_instance
    if _ai_engine_instance is None:
        if api_key is None:
            api_key = settings.deepseek_api_key
        _ai_engine_instance = SelfPromptingEngine(api_key, memory)
    return _ai_engine_instance


# Untuk backward compatibility
class DeepSeekEngine(SelfPromptingEngine):
    """Wrapper untuk backward compatibility"""
    pass


__all__ = ['SelfPromptingEngine', 'DeepSeekEngine', 'get_ai_engine']
