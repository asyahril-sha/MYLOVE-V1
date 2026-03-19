#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - CONTEXT ANALYZER (FIX FULL)
=============================================================================
Menganalisis semua konteks percakapan untuk AI prompt
- Menggabungkan data dari semua sistem (memory, leveling, dynamics, dll)
- Menyediakan konteks lengkap untuk generate respons
- Fix: Semua import path benar, error handling lengkap
=============================================================================
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class ContextAnalyzer:
    """
    Menganalisis dan menggabungkan semua konteks percakapan
    Menyediakan data lengkap untuk prompt AI
    """
    
    def __init__(self):
        # Cache untuk hasil analisis
        self.cache = {}
        self.cache_ttl = 300  # 5 menit
        
        logger.info("✅ ContextAnalyzer initialized")
    
    async def analyze(self,
                     user_id: int,
                     session_id: str,
                     user_message: str,
                     role: str,
                     bot_name: str,
                     user_name: str,
                     
                     # ===== DATA DARI SISTEM LAIN =====
                     intimacy_data: Optional[Dict] = None,
                     mood_data: Optional[Dict] = None,
                     chemistry_data: Optional[Dict] = None,
                     direction_data: Optional[Dict] = None,
                     location_data: Optional[Dict] = None,
                     clothing_data: Optional[Dict] = None,
                     physical_attrs: Optional[Dict] = None,
                     user_preferences: Optional[Dict] = None,
                     memories: Optional[List[Dict]] = None,
                     story_data: Optional[Dict] = None,
                     intent_data: Optional[Dict] = None,
                     dominance_mode: str = "normal",
                     conversation_history: Optional[List[Dict]] = None,
                     
                     # ===== METADATA =====
                     metadata: Optional[Dict] = None) -> Dict:
        """
        Analisis lengkap semua konteks
        
        Args:
            user_id: ID user
            session_id: ID sesi
            user_message: Pesan user saat ini
            role: Role bot
            bot_name: Nama bot
            user_name: Nama user
            
            intimacy_data: Data dari intimacy system
            mood_data: Data dari mood system
            chemistry_data: Data dari chemistry system
            direction_data: Data dari direction system
            location_data: Data lokasi
            clothing_data: Data pakaian
            physical_attrs: Atribut fisik bot
            user_preferences: Preferensi user
            memories: Memori relevan
            story_data: Data story arc
            intent_data: Data intent user
            dominance_mode: Mode dominasi (normal/dominant/submissive/switch)
            conversation_history: History percakapan
            
            metadata: Metadata tambahan
            
        Returns:
            Dict berisi semua konteks untuk prompt
        """
        
        # Cek cache (hanya untuk pesan yang sama persis)
        cache_key = f"{session_id}:{user_message[:50]}"
        if cache_key in self.cache:
            cache_age = time.time() - self.cache[cache_key]['timestamp']
            if cache_age < self.cache_ttl:
                logger.debug(f"Context cache hit for: {user_message[:30]}...")
                return self.cache[cache_key]['data']
        
        # ===== 1. KONTEKS DASAR =====
        context = {
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'time_of_day': self._get_time_of_day(),
            'day_of_week': datetime.now().strftime('%A'),
            
            'user': {
                'id': user_id,
                'name': user_name,
                'message': user_message,
                'message_length': len(user_message)
            },
            
            'bot': {
                'name': bot_name,
                'role': role,
                'dominance_mode': dominance_mode
            },
            
            'session': {
                'id': session_id,
                'duration': await self._get_session_duration(session_id)
            }
        }
        
        # ===== 2. INTIMACY DATA =====
        if intimacy_data:
            context['intimacy'] = {
                'level': intimacy_data.get('level', 1),
                'level_name': intimacy_data.get('level_name', 'Malu-malu'),
                'can_intim': intimacy_data.get('can_intim', False),
                'progress': intimacy_data.get('progress', 0),
                'next_level_in': intimacy_data.get('next_level_in', 0)
            }
        else:
            context['intimacy'] = {
                'level': 1,
                'level_name': 'Malu-malu',
                'can_intim': False,
                'progress': 0,
                'next_level_in': 0
            }
        
        # ===== 3. MOOD DATA =====
        if mood_data:
            context['mood'] = {
                'current': mood_data.get('current', 'calm'),
                'emoji': mood_data.get('emoji', '😐'),
                'description': mood_data.get('description', 'netral'),
                'intensity': mood_data.get('intensity', 0.5),
                'factor': mood_data.get('factor', 1.0)
            }
        else:
            context['mood'] = {
                'current': 'calm',
                'emoji': '😐',
                'description': 'netral',
                'intensity': 0.5,
                'factor': 1.0
            }
        
        # ===== 4. CHEMISTRY DATA =====
        if chemistry_data:
            context['chemistry'] = {
                'level': chemistry_data.get('level', 'biasa'),
                'score': chemistry_data.get('score', 50),
                'vibe': chemistry_data.get('vibe', '😐'),
                'description': chemistry_data.get('description', ''),
                'trend': chemistry_data.get('trend', 'stabil')
            }
        else:
            context['chemistry'] = {
                'level': 'biasa',
                'score': 50,
                'vibe': '😐',
                'description': 'Chemistry biasa',
                'trend': 'stabil'
            }
        
        # ===== 5. DIRECTION DATA (untuk PDKT) =====
        if direction_data:
            context['direction'] = {
                'who': direction_data.get('who', 'user_ke_bot'),
                'text': direction_data.get('text', ''),
                'hint': direction_data.get('hint', ''),
                'intensity': direction_data.get('intensity', 5)
            }
        
        # ===== 6. LOKASI & PAKAIAN =====
        if location_data:
            context['location'] = {
                'name': location_data.get('name', 'Tempat tidak diketahui'),
                'description': location_data.get('description', ''),
                'category': location_data.get('category', 'urban'),
                'base_risk': location_data.get('base_risk', 50),
                'base_thrill': location_data.get('base_thrill', 50)
            }
        else:
            context['location'] = {
                'name': 'Tempat tidak diketahui',
                'description': '',
                'category': 'unknown',
                'base_risk': 50,
                'base_thrill': 50
            }
        
        if clothing_data:
            context['clothing'] = {
                'description': clothing_data.get('description', 'Pakaian biasa'),
                'type': clothing_data.get('type', 'casual'),
                'color': clothing_data.get('color', '')
            }
        else:
            context['clothing'] = {
                'description': 'Pakaian biasa',
                'type': 'casual'
            }
        
        # ===== 7. ATRIBUT FISIK BOT =====
        if physical_attrs:
            context['physical'] = {
                'age': physical_attrs.get('age', 22),
                'height': physical_attrs.get('height', 165),
                'weight': physical_attrs.get('weight', 52),
                'chest': physical_attrs.get('chest', '34B'),
                'hair': physical_attrs.get('hair', 'hitam panjang'),
                'eyes': physical_attrs.get('eyes', 'coklat')
            }
        
        # ===== 8. PREFERENSI USER =====
        if user_preferences:
            context['preferences'] = {
                'positions': user_preferences.get('positions', [])[:3],
                'areas': user_preferences.get('areas', [])[:3],
                'activities': user_preferences.get('activities', [])[:3],
                'locations': user_preferences.get('locations', [])[:3]
            }
        
        # ===== 9. MEMORI RELEVAN =====
        if memories:
            context['memories'] = []
            for mem in memories[:5]:  # Max 5 memories
                context['memories'].append({
                    'content': mem.get('content', '')[:100],
                    'emotion': mem.get('emotional_tag', 'netral'),
                    'time_ago': self._format_time_ago(mem.get('timestamp', time.time()))
                })
        
        # ===== 10. STORY ARC =====
        if story_data:
            context['story'] = {
                'current_arc': story_data.get('current_arc', 'get_to_know'),
                'description': story_data.get('description', ''),
                'recommended_scene': story_data.get('recommended_scene', ''),
                'progression': story_data.get('progression', [])
            }
        
        # ===== 11. INTENT USER =====
        if intent_data:
            context['intent'] = {
                'primary': intent_data.get('primary_intent', 'chit_chat'),
                'all': [i.value for i in intent_data.get('all_intents', [])],
                'sentiment': intent_data.get('sentiment', 'neutral'),
                'is_question': intent_data.get('is_question', False),
                'needs': intent_data.get('needs', [])
            }
        
        # ===== 12. HISTORY PERCAKAPAN =====
        if conversation_history:
            context['history'] = []
            for msg in conversation_history[-5:]:  # Last 5 messages
                context['history'].append({
                    'role': msg.get('role', 'user'),
                    'content': msg.get('content', '')[:100],
                    'time_ago': self._format_time_ago(msg.get('timestamp', time.time()))
                })
        
        # ===== 13. METADATA TAMBAHAN =====
        if metadata:
            context['metadata'] = metadata
        
        # ===== 14. HITUNGAN TAMBAHAN =====
        context['calculations'] = {
            'should_be_proactive': await self._should_be_proactive(context),
            'idle_minutes': await self._get_idle_minutes(session_id),
            'conversation_tone': self._analyze_tone(user_message)
        }
        
        # Simpan ke cache
        self.cache[cache_key] = {
            'timestamp': time.time(),
            'data': context
        }
        
        # Bersihkan cache lama
        self._cleanup_cache()
        
        logger.debug(f"Context analyzed for session {session_id}")
        
        return context
    
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
    
    async def _get_session_duration(self, session_id: str) -> int:
        """Dapatkan durasi sesi dalam menit"""
        # Akan diambil dari session storage
        return 0
    
    async def _get_idle_minutes(self, session_id: str) -> float:
        """Dapatkan berapa menit user diam"""
        # Akan diambil dari session storage
        return 0
    
    async def _should_be_proactive(self, context: Dict) -> bool:
        """
        Cek apakah bot perlu memulai pesan proaktif
        """
        idle_minutes = context.get('calculations', {}).get('idle_minutes', 0)
        
        # Jika user diam > 5 menit
        if idle_minutes > 5:
            return True
        
        return False
    
    def _analyze_tone(self, message: str) -> str:
        """
        Analisis nada percakapan secara sederhana
        """
        message_lower = message.lower()
        
        positive_words = ['senang', 'bahagia', 'suka', 'cinta', 'sayang', '❤️', '😊', '🥰']
        negative_words = ['sedih', 'marah', 'kecewa', 'benci', '😢', '😠', '💔']
        intimate_words = ['intim', 'ml', 'sex', 'tidur', '🔥', '💦', '😏']
        
        pos_count = sum(1 for w in positive_words if w in message_lower)
        neg_count = sum(1 for w in negative_words if w in message_lower)
        int_count = sum(1 for w in intimate_words if w in message_lower)
        
        if int_count > 0:
            return "intimate"
        elif pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        else:
            return "neutral"
    
    def _format_time_ago(self, timestamp: float) -> str:
        """Format waktu yang lalu"""
        diff = time.time() - timestamp
        
        if diff < 60:
            return "baru saja"
        elif diff < 3600:
            return f"{int(diff / 60)} menit lalu"
        elif diff < 86400:
            return f"{int(diff / 3600)} jam lalu"
        else:
            return f"{int(diff / 86400)} hari lalu"
    
    def _cleanup_cache(self):
        """Bersihkan cache yang sudah expired"""
        now = time.time()
        expired = []
        
        for key, data in self.cache.items():
            if now - data['timestamp'] > self.cache_ttl:
                expired.append(key)
        
        for key in expired:
            del self.cache[key]
    
    def get_summary(self, context: Dict) -> str:
        """
        Dapatkan ringkasan konteks untuk log
        
        Args:
            context: Hasil dari analyze()
            
        Returns:
            String ringkasan
        """
        lines = [
            f"📊 Context Summary:",
            f"• User: {context['user']['name']}",
            f"• Bot: {context['bot']['name']} ({context['bot']['role']})",
            f"• Level: {context['intimacy']['level']} | Mood: {context['mood']['emoji']}",
            f"• Chemistry: {context['chemistry']['level']} ({context['chemistry']['score']}%)",
            f"• Location: {context['location']['name']}",
            f"• Intent: {context.get('intent', {}).get('primary', 'unknown')}"
        ]
        
        return "\n".join(lines)


__all__ = ['ContextAnalyzer']
