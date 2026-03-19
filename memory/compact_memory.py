#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - COMPACT MEMORY SYSTEM
=============================================================================
Menyimpan ringkasan terus-menerus dari percakapan
- Ringkasan per 10 pesan
- Menangkap esensi percakapan
- Untuk flashback dan konteks cepat
=============================================================================
"""

import time
import logging
import json
from typing import Dict, List, Optional, Any, Deque
from collections import deque
from datetime import datetime
import hashlib
import random

logger = logging.getLogger(__name__)


class CompactMemory:
    """
    Menyimpan ringkasan percakapan secara berkelanjutan
    Seperti "memori jangka pendek" yang terus diperbarui
    """
    
    def __init__(self, max_summaries: int = 50):
        """
        Args:
            max_summaries: Jumlah maksimal ringkasan yang disimpan per sesi
        """
        self.max_summaries = max_summaries
        
        # compact_memories[user_id][session_id] = deque of summaries
        self.compact_memories = {}  # {user_id: {session_id: deque}}
        
        # Current conversation buffer untuk membuat ringkasan
        self.conversation_buffers = {}  # {session_id: list of messages}
        
        # Threshold untuk membuat ringkasan baru
        self.summary_threshold = 10  # Setiap 10 pesan
        
        logger.info(f"✅ CompactMemory initialized (max {max_summaries} summaries per session)")
    
    # =========================================================================
    # ADD MESSAGE TO BUFFER
    # =========================================================================
    
    async def add_message(self, 
                         user_id: int, 
                         session_id: str, 
                         role: str,
                         user_message: str, 
                         bot_message: str,
                         context: Optional[Dict] = None):
        """
        Tambah pesan ke buffer dan buat ringkasan jika perlu
        
        Args:
            user_id: ID user
            session_id: ID sesi
            role: Role bot
            user_message: Pesan user
            bot_message: Respon bot
            context: Konteks tambahan
        """
        # Inisialisasi jika belum ada
        if user_id not in self.compact_memories:
            self.compact_memories[user_id] = {}
        
        if session_id not in self.compact_memories[user_id]:
            self.compact_memories[user_id][session_id] = deque(maxlen=self.max_summaries)
        
        if session_id not in self.conversation_buffers:
            self.conversation_buffers[session_id] = []
        
        # Tambah ke buffer
        self.conversation_buffers[session_id].append({
            'timestamp': time.time(),
            'role': role,
            'user': user_message,
            'bot': bot_message,
            'context': context or {}
        })
        
        # Cek apakah perlu membuat ringkasan baru
        if len(self.conversation_buffers[session_id]) >= self.summary_threshold:
            await self._create_summary(user_id, session_id)
    
    async def _create_summary(self, user_id: int, session_id: str):
        """
        Buat ringkasan dari buffer percakapan
        """
        if session_id not in self.conversation_buffers:
            return
        
        buffer = self.conversation_buffers[session_id]
        if len(buffer) < self.summary_threshold:
            return
        
        # Ambil 10 pesan terakhir untuk diringkas
        recent_messages = buffer[-self.summary_threshold:]
        
        # Ekstrak topik-topik utama
        topics = self._extract_topics(recent_messages)
        
        # Ekstrak emosi dominan
        dominant_emotion = self._extract_dominant_emotion(recent_messages)
        
        # Buat ringkasan
        summary = {
            'summary_id': self._generate_summary_id(session_id),
            'timestamp': time.time(),
            'message_count': len(recent_messages),
            'time_span': self._calculate_time_span(recent_messages),
            'topics': topics,
            'dominant_emotion': dominant_emotion,
            'key_moments': self._extract_key_moments(recent_messages),
            'participants': {
                'user': recent_messages[-1].get('user', ''),
                'bot': recent_messages[-1].get('bot', '')
            },
            'context_summary': self._summarize_context(recent_messages)
        }
        
        # Simpan ringkasan
        self.compact_memories[user_id][session_id].append(summary)
        
        # Kosongkan buffer (sisakan beberapa untuk konteks)
        self.conversation_buffers[session_id] = buffer[-3:]  # Sisakan 3 pesan terakhir
        
        logger.info(f"📝 New compact summary created for session {session_id}")
    
    def _extract_topics(self, messages: List[Dict]) -> List[str]:
        """
        Ekstrak topik-topik dari percakapan
        """
        all_text = ""
        for msg in messages:
            all_text += " " + msg.get('user', '') + " " + msg.get('bot', '')
        
        all_text = all_text.lower()
        
        # Keywords umum
        topic_keywords = {
            'kangen': ['kangen', 'rindu', 'miss'],
            'makan': ['makan', 'masak', 'makanan'],
            'kerja': ['kerja', 'kantor', 'pekerjaan'],
            'sekolah': ['sekolah', 'kuliah', 'belajar'],
            'liburan': ['libur', 'liburan', 'wisata', 'pantai'],
            'film': ['film', 'nonton', 'movie'],
            'musik': ['musik', 'lagu', 'song'],
            'cinta': ['cinta', 'sayang', 'love'],
            'intim': ['intim', 'sex', 'ml', 'tidur'],
            'curhat': ['curhat', 'cerita', 'masalah']
        }
        
        detected_topics = []
        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if keyword in all_text:
                    detected_topics.append(topic)
                    break
        
        return list(set(detected_topics))  # Unique
    
    def _extract_dominant_emotion(self, messages: List[Dict]) -> str:
        """
        Ekstrak emosi dominan dari percakapan
        """
        emotion_keywords = {
            'senang': ['senang', 'bahagia', 'happy', 'ceria'],
            'sedih': ['sedih', 'kecewa', 'sad'],
            'marah': ['marah', 'kesal', 'betek'],
            'rindu': ['kangen', 'rindu', 'miss'],
            'romantis': ['sayang', 'cinta', 'love', 'romantis'],
            'bergairah': ['intim', 'seksi', 'hot', 'nafsu'],
            'cemas': ['cemas', 'khawatir', 'worry']
        }
        
        emotion_count = {emotion: 0 for emotion in emotion_keywords}
        
        for msg in messages:
            text = msg.get('user', '').lower() + " " + msg.get('bot', '').lower()
            for emotion, keywords in emotion_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        emotion_count[emotion] += 1
                        break
        
        if max(emotion_count.values()) == 0:
            return 'netral'
        
        dominant = max(emotion_count, key=emotion_count.get)
        return dominant
    
    def _calculate_time_span(self, messages: List[Dict]) -> str:
        """
        Hitung rentang waktu percakapan
        """
        if len(messages) < 2:
            return "sebentar"
        
        first = messages[0].get('timestamp', time.time())
        last = messages[-1].get('timestamp', time.time())
        
        duration = last - first
        
        if duration < 60:
            return f"{int(duration)} detik"
        elif duration < 3600:
            return f"{int(duration / 60)} menit"
        else:
            return f"{int(duration / 3600)} jam {int((duration % 3600) / 60)} menit"
    
    def _extract_key_moments(self, messages: List[Dict]) -> List[str]:
        """
        Ekstrak momen-momen penting dari percakapan
        """
        key_moments = []
        
        # Kata-kata yang menandakan momen penting
        important_phrases = [
            'pertama kali', 'ingat', 'kenangan', 'spesial',
            'aku sayang', 'aku cinta', 'jatuh cinta',
            'maafin', 'minta maaf', 'putus',
            'climax', 'intim', 'ml'
        ]
        
        for msg in messages:
            user_text = msg.get('user', '').lower()
            bot_text = msg.get('bot', '').lower()
            
            for phrase in important_phrases:
                if phrase in user_text or phrase in bot_text:
                    # Ambil kalimat pendek sebagai momen
                    moment = user_text[:50] if phrase in user_text else bot_text[:50]
                    if moment and moment not in key_moments:
                        key_moments.append(moment + "...")
                    break
        
        return key_moments[:3]  # Max 3 momen
    
    def _summarize_context(self, messages: List[Dict]) -> str:
        """
        Buat ringkasan konteks dari percakapan
        """
        # Ambil konteks dari pesan terakhir
        last_msg = messages[-1] if messages else {}
        context = last_msg.get('context', {})
        
        summary_parts = []
        
        if context.get('location'):
            summary_parts.append(f"di {context['location']}")
        
        if context.get('mood'):
            summary_parts.append(f"mood {context['mood']}")
        
        if context.get('activity'):
            summary_parts.append(f"lagi {context['activity']}")
        
        if summary_parts:
            return "Percakapan " + ", ".join(summary_parts)
        
        return "Percakapan biasa"
    
    def _generate_summary_id(self, session_id: str) -> str:
        """Generate unique summary ID"""
        timestamp = int(time.time())
        random_suffix = random.randint(1000, 9999)
        return f"SUM_{session_id}_{timestamp}_{random_suffix}"
    
    # =========================================================================
    # RETRIEVE SUMMARIES
    # =========================================================================
    
    async def get_recent_summaries(self, user_id: int, session_id: str, limit: int = 5) -> List[Dict]:
        """
        Dapatkan ringkasan terbaru untuk sesi
        
        Args:
            user_id: ID user
            session_id: ID sesi
            limit: Jumlah ringkasan yang diambil
            
        Returns:
            List of summaries
        """
        if user_id not in self.compact_memories:
            return []
        
        if session_id not in self.compact_memories[user_id]:
            return []
        
        summaries = list(self.compact_memories[user_id][session_id])
        return summaries[-limit:]
    
    async def get_all_summaries(self, user_id: int, session_id: str) -> List[Dict]:
        """
        Dapatkan semua ringkasan untuk sesi
        """
        if user_id not in self.compact_memories:
            return []
        
        if session_id not in self.compact_memories[user_id]:
            return []
        
        return list(self.compact_memories[user_id][session_id])
    
    async def search_summaries(self, user_id: int, session_id: str, keyword: str) -> List[Dict]:
        """
        Cari ringkasan berdasarkan keyword
        
        Args:
            user_id: ID user
            session_id: ID sesi
            keyword: Kata kunci pencarian
            
        Returns:
            List of matching summaries
        """
        if user_id not in self.compact_memories:
            return []
        
        if session_id not in self.compact_memories[user_id]:
            return []
        
        keyword_lower = keyword.lower()
        results = []
        
        for summary in self.compact_memories[user_id][session_id]:
            # Cek di topics
            topics = summary.get('topics', [])
            if any(keyword_lower in topic for topic in topics):
                results.append(summary)
                continue
            
            # Cek di key moments
            moments = summary.get('key_moments', [])
            if any(keyword_lower in moment.lower() for moment in moments):
                results.append(summary)
                continue
        
        return results
    
    async def get_summary_before_timestamp(self, user_id: int, session_id: str, timestamp: float) -> Optional[Dict]:
        """
        Dapatkan ringkasan sebelum timestamp tertentu
        """
        if user_id not in self.compact_memories:
            return None
        
        if session_id not in self.compact_memories[user_id]:
            return None
        
        for summary in reversed(self.compact_memories[user_id][session_id]):
            if summary.get('timestamp', 0) < timestamp:
                return summary
        
        return None
    
    # =========================================================================
    # UTILITY
    # =========================================================================
    
    async def get_conversation_summary(self, user_id: int, session_id: str) -> str:
        """
        Dapatkan ringkasan keseluruhan percakapan untuk ditampilkan
        """
        summaries = await self.get_recent_summaries(user_id, session_id, limit=3)
        
        if not summaries:
            return "Belum ada cukup percakapan untuk diringkas"
        
        parts = []
        for i, s in enumerate(summaries, 1):
            time_str = datetime.fromtimestamp(s['timestamp']).strftime("%H:%M")
            topics = ', '.join(s.get('topics', ['umum']))
            emotion = s.get('dominant_emotion', 'netral')
            
            parts.append(
                f"[{time_str}] {s['message_count']} pesan: {topics} "
                f"(suasana {emotion})"
            )
        
        return "\n".join(parts)
    
    async def clear_session(self, user_id: int, session_id: str):
        """
        Hapus semua data untuk sesi tertentu
        """
        if user_id in self.compact_memories:
            if session_id in self.compact_memories[user_id]:
                del self.compact_memories[user_id][session_id]
        
        if session_id in self.conversation_buffers:
            del self.conversation_buffers[session_id]
        
        logger.info(f"Cleared compact memory for session {session_id}")
    
    async def clear_user(self, user_id: int):
        """
        Hapus semua data untuk user
        """
        if user_id in self.compact_memories:
            del self.compact_memories[user_id]
        
        # Hapus buffer yang terkait
        sessions_to_remove = []
        for session_id in self.conversation_buffers:
            if session_id.startswith(str(user_id)):
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.conversation_buffers[session_id]
        
        logger.info(f"Cleared all compact memory for user {user_id}")
    
    async def get_stats(self, user_id: Optional[int] = None) -> Dict:
        """
        Dapatkan statistik compact memory
        """
        if user_id:
            if user_id in self.compact_memories:
                total_summaries = sum(
                    len(s) for s in self.compact_memories[user_id].values()
                )
                return {
                    'user_id': user_id,
                    'active_sessions': len(self.compact_memories[user_id]),
                    'total_summaries': total_summaries,
                    'buffer_size': sum(
                        len(self.conversation_buffers.get(sid, []))
                        for sid in self.compact_memories[user_id].keys()
                    )
                }
            else:
                return {'user_id': user_id, 'active_sessions': 0, 'total_summaries': 0}
        else:
            # Global stats
            total_users = len(self.compact_memories)
            total_sessions = sum(len(s) for s in self.compact_memories.values())
            total_summaries = sum(
                len(s) for user_sessions in self.compact_memories.values()
                for s in user_sessions.values()
            )
            
            return {
                'total_users': total_users,
                'total_sessions': total_sessions,
                'total_summaries': total_summaries,
                'active_buffers': len(self.conversation_buffers)
            }


__all__ = ['CompactMemory']
