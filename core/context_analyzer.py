#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - CONTEXT ANALYZER
=============================================================================
Menganalisis konteks SUPER LENGKAP untuk AI prompt
- Deteksi bahasa user (Indonesia/Inggris)
- Analisis intent dan mood dari pesan
- Mengumpulkan semua data: level, lokasi, posisi, pakaian
- Menentukan panggilan yang tepat berdasarkan level
=============================================================================
"""

import re
import random
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class ContextAnalyzer:
    """
    Menganalisis semua konteks yang relevan untuk generate respons AI
    """
    
    def __init__(self):
        # Kamus kata untuk deteksi bahasa
        self.indo_words = {
            'aku', 'kamu', 'dia', 'kita', 'mereka', 'ini', 'itu', 'sini', 'situ',
            'apa', 'siapa', 'kenapa', 'bagaimana', 'kapan', 'dimana',
            'ya', 'tidak', 'boleh', 'mau', 'bisa', 'harus',
            'dan', 'atau', 'tapi', 'karena', 'jika', 'maka',
            'sudah', 'belum', 'sedang', 'akan', 'lagi',
            'saya', 'anda', 'kami', 'mereka', 'dia',
            'ngapain', 'gimana', 'kenapa', 'kok', 'sih', 'deh', 'dong',
            'sayang', 'cinta', 'kangen', 'rindu', 'suka',
            'makasih', 'terima kasih', 'maaf', 'permisi',
            'iya', 'enggak', 'gak', 'nggak', 'bukan',
            'pagi', 'siang', 'sore', 'malam',
            'rumah', 'kantor', 'sekolah', 'kampus', 'mall',
            'makan', 'minum', 'tidur', 'mandi', 'kerja'
        }
        
        self.eng_words = {
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'this', 'that', 'these', 'those', 'here', 'there',
            'what', 'who', 'why', 'how', 'when', 'where',
            'yes', 'no', 'can', 'could', 'will', 'would', 'shall', 'should', 'may', 'might', 'must',
            'and', 'or', 'but', 'because', 'if', 'then',
            'already', 'yet', 'still', 'again', 'soon',
            'the', 'a', 'an', 'of', 'in', 'on', 'at', 'to', 'for', 'with', 'by',
            'love', 'like', 'miss', 'want', 'need',
            'thanks', 'thank', 'sorry', 'excuse',
            'yes', 'no', 'not', 'is', 'are', 'am',
            'morning', 'afternoon', 'evening', 'night',
            'home', 'office', 'school', 'college', 'mall',
            'eat', 'drink', 'sleep', 'shower', 'work'
        }
        
        # Kata kunci untuk deteksi intent
        self.intent_keywords = {
            'rindu': ['rindu', 'kangen', 'miss', 'kangeeeen'],
            'sayang': ['sayang', 'cinta', 'love', 'lope'],
            'intim': ['sex', 'ml', 'tidur', 'intim', 'ayol', 'gas', 'horny', 'nafsu'],
            'curhat': ['cerita', 'curhat', 'kabar', 'gimana', 'how', 'story'],
            'kegiatan': ['ngapain', 'lagi apa', 'kamu lagi', 'what are you'],
            'marah': ['marah', 'kesal', 'bet', 'angry', 'kesel'],
            'sedih': ['sedih', 'sad', 'down', 'galau'],
            'bahagia': ['senang', 'happy', 'bahagia', 'joy'],
            'lelah': ['capek', 'lelah', 'tired', 'exhausted'],
            'bingung': ['bingung', 'confused', 'buntu'],
            'takut': ['takut', 'scared', 'afraid', 'khawatir'],
            'kaget': ['kaget', 'shock', 'surprised', 'wow'],
            'kesepian': ['sepi', 'sendiri', 'alone', 'lonely']
        }
        
        logger.info("✅ ContextAnalyzer initialized")
    
    # =========================================================================
    # DETEKSI BAHASA
    # =========================================================================
    
    def detect_language(self, text: str) -> str:
        """
        Deteksi apakah teks menggunakan bahasa Indonesia atau Inggris
        
        Args:
            text: Pesan dari user
            
        Returns:
            'id' untuk Indonesia, 'en' untuk Inggris
        """
        if not text:
            return 'id'
        
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        if not words:
            return 'id'
        
        indo_count = sum(1 for word in words if word in self.indo_words)
        eng_count = sum(1 for word in words if word in self.eng_words)
        
        if indo_count == 0 and eng_count == 0:
            if 'the' in text_lower or 'and' in text_lower or 'is' in text_lower:
                return 'en'
            return 'id'
        
        return 'id' if indo_count >= eng_count else 'en'
    
    def get_language_instruction(self, language: str) -> str:
        """Dapatkan instruksi untuk AI berdasarkan bahasa"""
        if language == 'en':
            return (
                "RESPOND IN ENGLISH with natural, casual conversation style. "
                "Use everyday English like a native speaker would text."
            )
        else:
            return (
                "RESPON DALAM BAHASA INDONESIA dengan gaya percakapan sehari-hari. "
                "Gunakan bahasa gaul yang natural, seperti orang ngobrol di chat. "
                "Boleh pake kata 'sih', 'deh', 'dong', 'kok' yang bikin natural."
            )
    
    # =========================================================================
    # DETEKSI INTENT
    # =========================================================================
    
    def detect_intent(self, message: str) -> str:
        """Deteksi intent dari pesan user"""
        message_lower = message.lower()
        
        for intent, keywords in self.intent_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return intent
        
        return 'chat'
    
    def detect_mood_from_intent(self, intent: str) -> str:
        """Deteksi mood berdasarkan intent"""
        mood_map = {
            'rindu': 'rindu',
            'sayang': 'sayang',
            'intim': 'horny',
            'curhat': 'terbuka',
            'kegiatan': 'biasa',
            'marah': 'marah',
            'sedih': 'sedih',
            'bahagia': 'senang',
            'lelah': 'capek',
            'bingung': 'bingung',
            'takut': 'takut',
            'kaget': 'kaget',
            'kesepian': 'sepi'
        }
        return mood_map.get(intent, 'netral')
    
    # =========================================================================
    # SISTEM PANGGILAN
    # =========================================================================
    
    def get_calling(self, level: int, role: str, bot_name: str, user_name: str, 
                    language: str = 'id') -> Dict[str, str]:
        """Tentukan panggilan yang tepat berdasarkan level"""
        
        # Panggilan untuk bot menyebut dirinya sendiri
        if level >= 7:
            bot_call = random.choice([bot_name, "aku"])
        else:
            bot_call = bot_name
        
        # Panggilan untuk user
        if language == 'en':
            if level >= 9:
                user_call = random.choice(["baby", "sweetheart", "love", "honey"])
            elif level >= 7:
                user_call = random.choice(["darling", "dear", "sweetie"])
            elif level >= 4:
                user_call = user_name
            else:
                user_call = user_name
        else:
            if level >= 9:
                user_call = random.choice(["sayang", "cinta", "baby"])
            elif level >= 7:
                user_call = random.choice(["sayang", "cinta"])
            elif level >= 4:
                if user_name.lower() in ['mas', 'bro', 'bang']:
                    user_call = "mas"
                elif user_name.lower() in ['mbak', 'sis']:
                    user_call = "mbak"
                else:
                    user_call = "kak"
            else:
                user_call = user_name
        
        return {'bot_call': bot_call, 'user_call': user_call}
    
    # =========================================================================
    # LEVEL DESCRIPTIONS
    # =========================================================================
    
    def get_level_description(self, level: int) -> str:
        """Dapatkan deskripsi karakteristik level"""
        descriptions = {
            1: "masih canggung, malu-malu, sopan",
            2: "mulai terbuka, sedikit curhat",
            3: "mulai nyaman, bisa bercanda ringan",
            4: "sudah dekat, mulai menggoda",
            5: "akrab, bisa goda-godaan",
            6: "percaya diri, genit",
            7: "intim, mulai berani secara seksual",
            8: "vulgar, terbuka secara seksual",
            9: "bergairah, penuh nafsu",
            10: "sangat bergairah, liar",
            11: "deep connection, emosional",
            12: "aftercare, lembut, hangat"
        }
        return descriptions.get(level, "normal")
    
    def get_intimacy_status(self, level: int) -> str:
        """Dapatkan status intim berdasarkan level"""
        if level >= 12:
            return "aftercare - butuh perhatian setelah climax"
        elif level >= 7:
            return "bisa intim - level hubungan memungkinkan aktivitas seksual"
        else:
            return "belum bisa intim - masih dalam tahap pendekatan"
    
    # =========================================================================
    # BUILD FULL CONTEXT
    # =========================================================================
    
    async def build_full_context(self, user_id: int, user_message: str, 
                                   user_data: Dict, env_data: Dict = None) -> Dict:
        """Bangun konteks SUPER LENGKAP untuk AI prompt"""
        
        role = user_data.get('current_role', 'ipar')
        bot_name = user_data.get('bot_name', 'Aurora')
        user_name = user_data.get('user_name', 'Sayang')
        level = user_data.get('intimacy_level', 1)
        
        language = self.detect_language(user_message)
        intent = self.detect_intent(user_message)
        mood = self.detect_mood_from_intent(intent)
        calls = self.get_calling(level, role, bot_name, user_name, language)
        
        leveling = user_data.get('leveling', {})
        total_minutes = leveling.get('total_minutes', 0)
        boosted_minutes = leveling.get('boosted_minutes', 0)
        
        if env_data is None:
            env_data = {}
        
        location = env_data.get('location', user_data.get('current_location', 'ruang tamu'))
        position = env_data.get('position', user_data.get('current_position', 'duduk'))
        clothing = env_data.get('clothing', user_data.get('current_clothing', 'pakaian biasa'))
        
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
        
        milestones = user_data.get('milestones', [])
        recent_milestones = milestones[-3:] if milestones else []
        
        full_context = {
            'user_id': user_id,
            'user_name': user_name,
            'user_message': user_message,
            'bot_name': bot_name,
            'role': role,
            'bot_call': calls['bot_call'],
            'user_call': calls['user_call'],
            'language': language,
            'language_instruction': self.get_language_instruction(language),
            'intent': intent,
            'mood': mood,
            'level': level,
            'level_description': self.get_level_description(level),
            'intimacy_status': self.get_intimacy_status(level),
            'location': location,
            'position': position,
            'clothing': clothing,
            'time_of_day': time_of_day,
            'hour': hour,
            'day': now.strftime("%A"),
            'date': now.strftime("%d %B %Y"),
            'total_minutes': round(total_minutes, 1),
            'boosted_minutes': round(boosted_minutes, 1),
            'minutes_to_level_7': max(0, 60 - total_minutes),
            'minutes_to_level_11': max(0, 120 - total_minutes),
            'recent_milestones': recent_milestones,
            'total_chats': user_data.get('total_chats', 0),
            'relationship_status': user_data.get('relationship_status', 'hts'),
            'threesome_mode': user_data.get('threesome_mode', False),
        }
        
        if 'arousal' in user_data:
            full_context['arousal'] = user_data['arousal']
            full_context['arousal_percent'] = f"{user_data['arousal']*100:.0f}%"
        
        logger.debug(f"Full context built for user {user_id}")
        return full_context


__all__ = ['ContextAnalyzer']
