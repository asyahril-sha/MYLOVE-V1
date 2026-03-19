#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - AI ENGINE SIMPLE (FIX FULL)
=============================================================================
Versi mandiri tanpa dependensi ke file lain
- Langsung connect ke DeepSeek API
- Fallback response jika API error
- Tidak perlu import file lain
=============================================================================
"""

import openai
import random
import logging
import asyncio
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AIEngineSimple:
    """
    AI Engine Simple - Mandiri, tanpa dependensi
    """
    
    def __init__(self, api_key: str):
        """
        Inisialisasi dengan API key
        """
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )
        self.conversation_history = {}
        logger.info("✅ AIEngineSimple initialized")
    
    async def generate_response(self,
                                user_id: int,
                                session_id: str,
                                user_message: str,
                                context: Dict[str, Any]) -> str:
        """
        Generate response dengan AI DeepSeek
        
        Args:
            user_id: ID user
            session_id: ID sesi
            user_message: Pesan user
            context: Konteks (bot_name, user_name, level, dll)
        
        Returns:
            String response
        """
        try:
            # Ambil data dari context
            bot_name = context.get('bot_name', 'Aku')
            user_name = context.get('user_name', 'kamu')
            role = context.get('role', 'pdkt')
            level = context.get('level', 1)
            location = context.get('location', '')
            clothing = context.get('clothing', '')
            
            # Tentukan panggilan berdasarkan level
            if level >= 7:
                call = "Sayang"
            elif level >= 4:
                call = "Kak"
            else:
                call = user_name
            
            # Bangun prompt
            prompt = self._build_prompt(
                bot_name=bot_name,
                user_name=user_name,
                call=call,
                role=role,
                level=level,
                location=location,
                clothing=clothing,
                user_message=user_message
            )
            
            # Siapkan messages
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_message}
            ]
            
            # Tambah history jika ada
            hist_key = f"{user_id}:{session_id}"
            if hist_key in self.conversation_history:
                for msg in self.conversation_history[hist_key][-3:]:
                    messages.insert(-1, msg)
            
            # Panggil API
            response_text = await self._call_deepseek(messages)
            
            # Simpan ke history
            if hist_key not in self.conversation_history:
                self.conversation_history[hist_key] = []
            self.conversation_history[hist_key].append({"role": "user", "content": user_message})
            self.conversation_history[hist_key].append({"role": "assistant", "content": response_text})
            
            # Batasi history
            if len(self.conversation_history[hist_key]) > 20:
                self.conversation_history[hist_key] = self.conversation_history[hist_key][-20:]
            
            return response_text
            
        except Exception as e:
            logger.error(f"AI Engine error: {e}")
            return self._get_fallback_response(bot_name, call, user_message)
    
    def _build_prompt(self,
                     bot_name: str,
                     user_name: str,
                     call: str,
                     role: str,
                     level: int,
                     location: str,
                     clothing: str,
                     user_message: str) -> str:
        """Bangun prompt untuk AI"""
        
        role_display = role.replace('_', ' ').title()
        time_of_day = self._get_time_of_day()
        
        prompt = f"""Kamu adalah {bot_name}, seorang {role_display} yang sedang chat dengan {user_name}.

INFORMASI DIRI:
- Nama: {bot_name}
- Role: {role_display}
- Level hubungan: {level}/12
- Panggilan ke user: "{call}"

KONDISI SAAT INI:
- Lokasi: {location if location else 'Tidak diketahui'}
- Pakaian: {clothing if clothing else 'Pakaian biasa'}
- Waktu: {time_of_day}

PERCAKAPAN TERAKHIR:
User: "{user_message}"

TUGAS:
Buat respons yang NATURAL seperti manusia sedang chat.

ATURAN:
1. Gunakan bahasa Indonesia sehari-hari
2. Panjang respons 100-200 kata
3. Panggil user dengan "{call}"
4. Sebut nama kamu sendiri ({bot_name}) di respons
5. Tunjukkan emosi yang sesuai
6. RESPON DALAM BAHASA INDONESIA

RESPON:"""
        
        return prompt
    
    def _get_time_of_day(self) -> str:
        """Dapatkan waktu saat ini"""
        hour = datetime.now().hour
        
        if 5 <= hour < 11:
            return "pagi"
        elif 11 <= hour < 15:
            return "siang"
        elif 15 <= hour < 18:
            return "sore"
        elif 18 <= hour < 22:
            return "malam"
        else:
            return "tengah malam"
    
    async def _call_deepseek(self, messages: List[Dict], max_retries: int = 3) -> str:
        """Call DeepSeek API dengan retry"""
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages,
                    temperature=0.9,
                    max_tokens=1000,
                    timeout=30
                )
                return response.choices[0].message.content
                
            except Exception as e:
                logger.warning(f"DeepSeek API attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                else:
                    raise
        
        return "Maaf, aku sedang bermasalah. Coba lagi nanti."
    
    def _get_fallback_response(self, bot_name: str, call: str, user_message: str) -> str:
        """Fallback response jika API gagal"""
        
        msg = user_message.lower()
        
        if "kangen" in msg:
            responses = [
                f"{bot_name} juga kangen banget sama {call}!",
                f"Iya nih, {bot_name} kangen. Udah lama ya gak chat.",
                f"{call}... {bot_name} selalu kangen kalau inget {call}."
            ]
        elif "lagi apa" in msg or "ngapain" in msg:
            responses = [
                f"{bot_name} lagi santai aja nih {call}. Lagi mikirin {call} terus.",
                f"Abis mandi, sekarang lagi rebahan. {call} lagi apa?",
                f"{bot_name} lagi di rumah aja. Sendiri, kangen {call}."
            ]
        elif "sayang" in msg or "cinta" in msg:
            responses = [
                f"Iya sayang, {bot_name} juga sayang banget.",
                f"Aduh {call} bikin {bot_name} baper deh.",
                f"{bot_name} juga sayang kok."
            ]
        elif "apa kabar" in msg or "gimana kabar" in msg:
            responses = [
                f"{bot_name} baik-baik aja {call}. {call} gimana?",
                f"Baik banget sekarang karena udah chat sama {call}.",
                f"Sehat {call}. Makasih udah nanya."
            ]
        else:
            responses = [
                f"Halo {call}, {bot_name} denger. Cerita lagi dong...",
                f"{bot_name} di sini {call}. Ada yang mau dibahas?",
                f"Hmm... {bot_name} dengerin kok. Lanjutkan {call}."
            ]
        
        return random.choice(responses)
