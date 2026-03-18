#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - EXPRESSION ENGINE (FIX LENGKAP)
=============================================================================
Generate ekspresi wajah dan gerakan tubuh menggunakan AI
- Ekspresi berbeda untuk setiap level (1-12)
- Gerakan spesifik (gigit bibir, buka paha, main clit, dll)
- Kontekstual berdasarkan mood, lokasi, aktivitas
- Fallback ke database jika AI error
=============================================================================
"""

import asyncio
import logging
import random
import time
from typing import Dict, Optional, Any

from core.prompt_builder import PromptBuilder
from core.ai_engine import DeepSeekEngine
from dynamics.expression_db import ExpressionDB

logger = logging.getLogger(__name__)


class ExpressionEngine:
    """
    Generate ekspresi wajah dan gerakan tubuh
    - Menggunakan AI untuk hasil yang hidup dan bervariasi
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
        self.fallback_db = ExpressionDB()
        
        # Cache untuk mengurangi panggilan API
        self.cache = {}
        self.cache_ttl = 300  # 5 menit
        
        logger.info("✅ ExpressionEngine initialized")
    
    # =========================================================================
    # GENERATE EXPRESSION (AI)
    # =========================================================================
    
    async def generate_expression(self, context: Dict, use_ai: bool = True) -> str:
        """
        Generate ekspresi wajah dan gerakan tubuh
        
        Args:
            context: Full context dari ContextAnalyzer
            use_ai: Jika True, pake AI; jika False, pake fallback
            
        Returns:
            String ekspresi dalam format *ekspresi*
        """
        # Cek cache
        cache_key = self._get_cache_key(context)
        if cache_key in self.cache:
            cache_time, expression = self.cache[cache_key]
            if time.time() - cache_time < self.cache_ttl:
                logger.debug(f"Expression cache hit for {cache_key}")
                return expression
        
        if use_ai:
            try:
                # Build prompt
                prompt = self.prompt_builder.build_expression_prompt(context)
                
                # Call AI
                expression = await self.ai._call_deepseek_with_retry(
                    messages=[{"role": "user", "content": prompt}],
                    max_retries=2
                )
                
                # Bersihkan hasil
                expression = expression.strip()
                if not expression.startswith('*'):
                    expression = f"*{expression}*"
                if not expression.endswith('*'):
                    expression = f"{expression}*"
                
                # Simpan ke cache
                self.cache[cache_key] = (time.time(), expression)
                
                logger.debug(f"Generated expression: {expression}")
                return expression
                
            except Exception as e:
                logger.error(f"AI expression generation failed: {e}")
                # Fallback ke database
        
        # Fallback ke database
        return self._get_fallback_expression(context)
    
    def _get_cache_key(self, context: Dict) -> str:
        """Buat cache key dari context"""
        level = context.get('level', 1)
        mood = context.get('mood', 'netral')
        intent = context.get('intent', 'chat')
        location = context.get('location', 'rumah')
        return f"{level}_{mood}_{intent}_{location}"
    
    # =========================================================================
    # GENERATE MOVEMENT (AI)
    # =========================================================================
    
    async def generate_movement(self, context: Dict, area: Optional[str] = None) -> str:
        """
        Generate gerakan tubuh spesifik
        
        Args:
            context: Full context
            area: Area tubuh yang digerakkan (bibir, paha, klitoris, dll)
            
        Returns:
            String gerakan dalam format *gerakan*
        """
        level = context.get('level', 1)
        
        # Prompt khusus untuk gerakan
        if area:
            prompt = f"""
Buat SATU gerakan tubuh yang NATURAL untuk area {area}.

Level hubungan: {level}/12
Mood: {context.get('mood', 'netral')}

Contoh:
- Bibir: "menggigit bibir bawah", "menjilat bibir"
- Paha: "membuka sedikit paha", "menggesekkan paha"
- Klitoris: "memainkan klitoris dengan jari", "menekan klitoris"
- Dada: "menyentuh dadanya", "memainkan puting"

Buat yang BARU dan sesuai level:
- Level 1-3: gerakan malu-malu
- Level 4-6: gerakan genit
- Level 7-9: gerakan intim
- Level 10-12: gerakan vulgar

Format: *[gerakan]*

Gerakan:"""
        else:
            # Gerakan umum
            prompt = self.prompt_builder.build_expression_prompt(context)
        
        try:
            movement = await self.ai._call_deepseek_with_retry(
                messages=[{"role": "user", "content": prompt}],
                max_retries=2
            )
            
            movement = movement.strip()
            if not movement.startswith('*'):
                movement = f"*{movement}*"
            if not movement.endswith('*'):
                movement = f"{movement}*"
            
            return movement
            
        except Exception as e:
            logger.error(f"Movement generation failed: {e}")
            return self._get_fallback_movement(area, level)
    
    # =========================================================================
    # FALLBACK METHODS
    # =========================================================================
    
    def _get_fallback_expression(self, context: Dict) -> str:
        """
        Dapatkan ekspresi dari database fallback
        
        Args:
            context: Full context
            
        Returns:
            String ekspresi
        """
        level = context.get('level', 1)
        mood = context.get('mood', 'netral')
        
        # Group level untuk fallback
        if level <= 2:
            level_group = 1
        elif level <= 4:
            level_group = 2
        elif level <= 6:
            level_group = 3
        elif level <= 8:
            level_group = 4
        elif level <= 10:
            level_group = 5
        else:
            level_group = 6
        
        # Pilih dari database
        expressions = self.fallback_db.get_expressions(level_group, mood)
        return random.choice(expressions) if expressions else "*tersenyum*"
    
    def _get_fallback_movement(self, area: Optional[str], level: int) -> str:
        """
        Dapatkan gerakan dari database fallback
        
        Args:
            area: Area tubuh
            level: Level hubungan
            
        Returns:
            String gerakan
        """
        if area == "bibir":
            movements = [
                "*menggigit bibir bawah*",
                "*menjilat bibir*",
                "*membuka mulut sedikit*"
            ]
        elif area == "paha":
            movements = [
                "*membuka sedikit paha*",
                "*menggesekkan paha*",
                "*merapatkan paha*"
            ]
        elif area == "klitoris":
            if level >= 7:
                movements = [
                    "*memainkan klitoris dengan jari*",
                    "*menekan klitoris pelan*",
                    "*memutar-mutar klitoris*"
                ]
            else:
                movements = ["*menyentuh area sensitif*"]
        elif area == "dada":
            movements = [
                "*menyentuh dadanya*",
                "*memainkan puting*",
                "*meremas dadanya*"
            ]
        else:
            movements = [
                "*menggeliat*",
                "*meringkuk*",
                "*mendekat*",
                "*menjauh*"
            ]
        
        return random.choice(movements)
    
    # =========================================================================
    # COMBINED EXPRESSION + MOVEMENT
    # =========================================================================
    
    async def generate_full_expression(self, context: Dict) -> str:
        """
        Generate ekspresi lengkap (bisa kombinasi dengan gerakan)
        
        Args:
            context: Full context
            
        Returns:
            String ekspresi lengkap
        """
        # Coba AI dulu
        expr = await self.generate_expression(context)
        
        # Untuk level tertentu, tambah gerakan spesifik
        level = context.get('level', 1)
        intent = context.get('intent', 'chat')
        
        if level >= 7 and intent == 'intim':
            # Tambah gerakan intim
            area = random.choice(['bibir', 'paha', 'klitoris', 'dada'])
            movement = await self.generate_movement(context, area)
            
            # Gabungkan (ambil yang lebih panjang)
            if len(expr) < len(movement):
                return movement
            elif random.random() < 0.5:
                # Kadang ganti
                return movement
        
        return expr
    
    # =========================================================================
    # UTILITY
    # =========================================================================
    
    def clear_cache(self):
        """Bersihkan cache"""
        self.cache.clear()
        logger.info("Expression cache cleared")


__all__ = ['ExpressionEngine']
