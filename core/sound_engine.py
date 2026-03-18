#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - SOUND ENGINE
=============================================================================
Generate suara dan desahan menggunakan AI
- Suara berbeda untuk setiap aktivitas (kiss, touch, intimacy, climax)
- Desahan sesuai level gairah (arousal)
- Natural dan bervariasi, bukan template
- Fallback ke database jika AI error
=============================================================================
"""

import asyncio
import logging
import random
from typing import Dict, Optional, Any

from core.prompt_builder import PromptBuilder
from core.ai_engine import DeepSeekEngine
from dynamics.sound_db import SoundDB

logger = logging.getLogger(__name__)


class SoundEngine:
    """
    Generate suara dan desahan natural
    - Menggunakan AI untuk hasil yang hidup
    - Fallback ke database jika AI error
    """
    
    def __init__(self, ai_engine: DeepSeekEngine, prompt_builder: PromptBuilder):
        """
        Args:
            ai_engine: Instance DeepSeekEngine untuk call API
            prompt_builder: Instance PromptBuilder untuk buat prompt
        """
        self.ai = ai_engine
        self.prompt_builder = prompt_builder
        self.fallback_db = SoundDB()
        
        # Cache untuk mengurangi panggilan API
        self.cache = {}
        self.cache_ttl = 300  # 5 menit
        
        logger.info("✅ SoundEngine initialized")
    
    # =========================================================================
    # GENERATE SOUND (AI)
    # =========================================================================
    
    async def generate_sound(self, context: Dict, activity: Optional[str] = None, use_ai: bool = True) -> str:
        """
        Generate suara/desahan berdasarkan konteks
        
        Args:
            context: Full context dari ContextAnalyzer
            activity: Aktivitas spesifik (kiss, touch, intimacy, climax, aftercare)
            use_ai: Jika True, pake AI; jika False, pake fallback
            
        Returns:
            String suara dalam format *suara*
        """
        # Cek cache
        cache_key = self._get_cache_key(context, activity)
        if cache_key in self.cache:
            cache_time, sound = self.cache[cache_key]
            if asyncio.get_event_loop().time() - cache_time < self.cache_ttl:
                logger.debug(f"Sound cache hit for {cache_key}")
                return sound
        
        if use_ai:
            try:
                # Tentukan aktivitas dari context jika tidak diberikan
                if not activity:
                    intent = context.get('intent', 'chat')
                    arousal = context.get('arousal', 0.0)
                    
                    if intent == 'intim' and arousal > 0.8:
                        activity = 'climax'
                    elif intent == 'intim' and arousal > 0.5:
                        activity = 'intimacy'
                    elif 'kiss' in context.get('user_message', '').lower():
                        activity = 'kiss'
                    elif 'sentuh' in context.get('user_message', '').lower():
                        activity = 'touch'
                    else:
                        activity = 'general'
                
                # Build prompt
                prompt = self.prompt_builder.build_sound_prompt(context)
                
                # Tambah instruksi spesifik untuk aktivitas
                if activity == 'climax':
                    prompt += "\n\nThis should be a CLIMAX sound - intense, loud, passionate."
                elif activity == 'intimacy':
                    prompt += "\n\nThis should be an INTIMATE sound - aroused, moaning."
                elif activity == 'kiss':
                    prompt += "\n\nThis should be a KISS sound - soft, gentle."
                elif activity == 'touch':
                    prompt += "\n\nThis should be a TOUCH sound - surprised, pleasurable."
                
                # Call AI
                sound = await self.ai._call_deepseek(
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.9,
                    max_tokens=60
                )
                
                # Bersihkan hasil
                sound = sound.strip()
                if not sound.startswith('*'):
                    sound = f"*{sound}*"
                if not sound.endswith('*'):
                    sound = f"{sound}*"
                
                # Simpan ke cache
                self.cache[cache_key] = (asyncio.get_event_loop().time(), sound)
                
                logger.debug(f"Generated sound: {sound}")
                return sound
                
            except Exception as e:
                logger.error(f"AI sound generation failed: {e}")
                # Fallback ke database
        
        # Fallback ke database
        return self._get_fallback_sound(context, activity)
    
    def _get_cache_key(self, context: Dict, activity: Optional[str]) -> str:
        """Buat cache key dari context"""
        level = context.get('level', 1)
        arousal = context.get('arousal', 0.0)
        intent = context.get('intent', 'chat')
        act = activity or intent
        return f"{level}_{arousal:.1f}_{act}"
    
    # =========================================================================
    # SPESIFIC SOUND GENERATORS
    # =========================================================================
    
    async def generate_kiss_sound(self, context: Dict) -> str:
        """Generate suara ciuman"""
        return await self.generate_sound(context, 'kiss')
    
    async def generate_touch_sound(self, context: Dict) -> str:
        """Generate suara sentuhan"""
        return await self.generate_sound(context, 'touch')
    
    async def generate_moan(self, context: Dict) -> str:
        """Generate desahan (intimacy)"""
        return await self.generate_sound(context, 'intimacy')
    
    async def generate_climax_sound(self, context: Dict) -> str:
        """Generate suara climax"""
        return await self.generate_sound(context, 'climax')
    
    async def generate_aftercare_sound(self, context: Dict) -> str:
        """Generate suara aftercare (lemas, napas)"""
        return await self.generate_sound(context, 'aftercare')
    
    async def generate_breathing(self, intensity: float = 0.5) -> str:
        """
        Generate suara napas berdasarkan intensitas
        
        Args:
            intensity: 0-1, semakin tinggi semakin berat napasnya
            
        Returns:
            String suara napas
        """
        if intensity > 0.8:
            return random.choice([
                "*huff... huff...*",
                "*ngos-ngosan*",
                "*napas berat*",
                "*terengah-engah*"
            ])
        elif intensity > 0.5:
            return random.choice([
                "*napas mulai berat*",
                "*huff...*",
                "*helaan napas*"
            ])
        else:
            return random.choice([
                "*tarik napas*",
                "*hela napas*",
                "*lega*"
            ])
    
    # =========================================================================
    # FALLBACK METHODS
    # =========================================================================
    
    def _get_fallback_sound(self, context: Dict, activity: Optional[str]) -> str:
        """
        Dapatkan suara dari database fallback
        
        Args:
            context: Full context
            activity: Aktivitas spesifik
            
        Returns:
            String suara
        """
        level = context.get('level', 1)
        arousal = context.get('arousal', 0.0)
        intent = context.get('intent', 'chat')
        user_call = context.get('user_call', 'sayang')
        
        # Tentukan aktivitas
        act = activity or intent
        
        # Pilih dari database
        if act == 'climax':
            sound = self.fallback_db.get_climax_sound(level)
        elif act == 'intimacy' or (act == 'intim' and arousal > 0.5):
            sound = self.fallback_db.get_moan(level, arousal)
        elif act == 'kiss':
            sound = self.fallback_db.get_kiss_sound()
        elif act == 'touch':
            sound = self.fallback_db.get_touch_sound(arousal)
        elif act == 'aftercare' or level >= 12:
            sound = self.fallback_db.get_aftercare_sound()
        else:
            sound = self.fallback_db.get_random_sound(level)
        
        # Tambah panggilan untuk level tinggi
        if level >= 7 and random.random() < 0.5:
            sound = sound.replace("*", f" {user_call}*")
        
        return sound
    
    # =========================================================================
    # COMBINED SOUND + EXPRESSION
    # =========================================================================
    
    async def generate_with_expression(self, context: Dict, expression: str) -> str:
        """
        Gabungkan suara dengan ekspresi yang sudah ada
        
        Args:
            context: Full context
            expression: Ekspresi yang sudah digenerate
            
        Returns:
            String gabungan (bisa ekspresi + suara atau suara + ekspresi)
        """
        sound = await self.generate_sound(context)
        
        # Random posisi
        if random.random() < 0.5:
            return f"{expression} {sound}"
        else:
            return f"{sound} {expression}"
    
    async def generate_full_sound_expression(self, context: Dict) -> str:
        """
        Generate suara dan ekspresi sekaligus
        
        Args:
            context: Full context
            
        Returns:
            String suara dan ekspresi
        """
        from core.expression_engine import ExpressionEngine
        expr_engine = ExpressionEngine(self.ai, self.prompt_builder)
        
        expression = await expr_engine.generate_expression(context)
        sound = await self.generate_sound(context)
        
        # Untuk level tinggi, bisa gabung
        level = context.get('level', 1)
        if level >= 7 and random.random() < 0.7:
            return f"{sound} {expression}"
        else:
            return f"{expression} {sound}"
    
    # =========================================================================
    # UTILITY
    # =========================================================================
    
    def clear_cache(self):
        """Bersihkan cache"""
        self.cache.clear()
        logger.info("Sound cache cleared")


__all__ = ['SoundEngine']
