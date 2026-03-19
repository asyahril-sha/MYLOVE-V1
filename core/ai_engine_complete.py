#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - AI ENGINE COMPLETE WITH ALL MEMORY SYSTEMS
=============================================================================
Menggabungkan semua sistem memory menjadi satu kesatuan:
- Working Memory (short-term)
- Episodic Memory (sequence)
- Semantic Memory (facts)
- State Tracker (current state)
- Relationship Memory (history)
=============================================================================
"""

import openai
import time
import random
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from config import settings

# Import semua memory systems
from memory.working_memory import WorkingMemory
from memory.episodic_memory import EpisodicMemory, EpisodeType
from memory.semantic_memory import SemanticMemory, FactCategory
from memory.state_tracker import StateTracker, StateType
from memory.relationship_memory import RelationshipMemory, RelationshipType, MilestoneType

logger = logging.getLogger(__name__)


class AIEngineComplete:
    """
    AI Engine dengan semua sistem memory seperti manusia
    - Bisa digunakan untuk semua role (PDKT, HTS, FWB, NON-PDKT)
    - Ingat percakapan, lokasi, pakaian, mood
    - Punya urutan kejadian (tidak lompat-lompat)
    - Bisa flashback ke masa lalu
    - Sadar situasi (rame/sepi, horny/tidak)
    """
    
    def __init__(self, api_key: str, user_id: int, session_id: str):
        """
        Args:
            api_key: DeepSeek API key
            user_id: ID user
            session_id: ID session
        """
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )
        
        self.user_id = user_id
        self.session_id = session_id
        
        # ===== INISIALISASI SEMUA MEMORY SYSTEMS =====
        self.working = WorkingMemory()                 # Ingatan jangka pendek
        self.episodic = EpisodicMemory()               # Urutan kejadian
        self.semantic = SemanticMemory()               # Fakta-fakta
        self.state = StateTracker(user_id, session_id) # State saat ini
        self.relationship = RelationshipMemory()       # Riwayat hubungan
        
        # Cache untuk response
        self.response_cache = {}
        self.cache_ttl = 300  # 5 menit
        
        # Stats
        self.total_responses = 0
        self.total_tokens = 0
        
        logger.info(f"✅ AIEngineComplete initialized for user {user_id}, session {session_id}")

    async def _sync_location_memory(self):
        """Sinkronisasi lokasi antara working memory dan long-term memory"""
        
        # Ambil lokasi dari working memory
        current_loc = self.working.current_state.get('location')
        if current_loc:
            # Simpan ke semantic memory (long-term)
            await self.semantic.save_location_to_long_term(
                user_id=self.user_id,
                location=current_loc,
                timestamp=time.time()
            )
            logger.debug(f"📍 Location synced to long-term: {current_loc}")
        
        # Kalau working memory lupa, coba ambil dari long-term
        if not current_loc:
            recent = await self.semantic.get_recent_locations(self.user_id, hours=4)
            if recent and len(recent) > 0:
                # Set working memory ke lokasi terakhir
                last_loc = recent[-1]
                self.working.update_location(last_loc)
                logger.info(f"📍 Restored location from long-term memory: {last_loc}")
                
    # =========================================================================
    # SESSION MANAGEMENT
    # =========================================================================
    
    async def start_session(self, role: str, bot_name: str, 
                              rel_type: str = RelationshipType.NON_PDKT,
                              instance_id: Optional[str] = None):
        """
        Memulai session baru
        
        Args:
            role: Nama role (ipar, janda, pdkt, dll)
            bot_name: Nama bot
            rel_type: Tipe hubungan
            instance_id: ID instance (untuk multiple FWB)
        """
        # Create relationship jika belum ada
        rel = await self.relationship.get_relationship(self.user_id, role, instance_id)
        if not rel:
            instance_id = await self.relationship.create_relationship(
                user_id=self.user_id,
                role=role,
                bot_name=bot_name,
                rel_type=rel_type,
                instance_id=instance_id
            )
        
        # Simpan ke working memory
        self.working.update_state(
            role=role,
            bot_name=bot_name,
            rel_type=rel_type,
            instance_id=instance_id
        )
        
        # Catat ke episodic
        await self.episodic.add_episode(
            session_id=self.session_id,
            episode_type=EpisodeType.SESSION_START,
            data={
                'role': role,
                'bot_name': bot_name,
                'rel_type': rel_type
            },
            importance=0.8
        )
        
        logger.info(f"Session started: {role} - {bot_name}")
    
    # =========================================================================
    # PROCESS MESSAGE
    # =========================================================================
    
    async def process_message(self, user_message: str, context: Dict) -> str:
        """
        Proses pesan user dengan semua memory
        
        Args:
            user_message: Pesan dari user
            context: Konteks tambahan (lokasi, pakaian, dll)
            
        Returns:
            Response bot
        """
        start_time = time.time()
        
        # ===== 1. TAMBAHKAN LOGGING DI SINI =====  # <-- TAMBAHKAN INI
        logger.info("=" * 50)                        # <-- TAMBAHKAN INI
        logger.info(f"🔍 PROCESS MESSAGE START")     # <-- TAMBAHKAN INI
        logger.info(f"👤 User message: {user_message[:100]}")  # <-- TAMBAHKAN INI
        logger.info(f"📋 Context: {context}")        # <-- TAMBAHKAN INI
        logger.info(f"🆔 Session: {self.session_id}")  # <-- TAMBAHKAN INI
        # ===== SAMPAI SINI =====
        
        try:
            await self._sync_location_memory()
            # ===== 1. CEK CACHE =====
            cache_key = f"{self.session_id}:{user_message[:50]}"
            if cache_key in self.response_cache:
                cache_age = time.time() - self.response_cache[cache_key]['timestamp']
                if cache_age < self.cache_ttl:
                    logger.debug(f"Cache hit")
                    return self.response_cache[cache_key]['response']
            
            # ===== 2. UPDATE STATE DARI KONTEKS =====
            await self._update_state_from_context(context)
            
            # ===== 3. EKSTRAK FAKTA DARI PESAN =====
            await self.semantic.extract_facts_from_message(
                user_id=self.user_id,
                message=user_message,
                role=context.get('role')
            )
            
            # ===== 4. DAPATKAN SEMUA KONTEKS MEMORY =====
            memory_context = await self._get_memory_context(user_message)
            
            # ===== 5. CEK KONSISTENSI =====
            if not await self._check_consistency(memory_context, context):
                logger.warning(f"Consistency check failed, forcing corrections")
            
            # ===== 6. BANGUN PROMPT DENGAN SEMUA MEMORY =====
            prompt = await self._build_prompt(
                user_message=user_message,
                context=context,
                memory_context=memory_context
            )
            
            # ===== 7. GENERATE RESPONSE =====
            # ===== TAMBAHKAN LOGGING DI SINI =====  # <-- TAMBAHKAN INI
            logger.info("🤖 Calling DeepSeek API...")  # <-- TAMBAHKAN INI
            logger.info(f"📝 Prompt length: {len(prompt)} chars")  # <-- TAMBAHKAN INI
            # ===== SAMPAI SINI =====
            
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_message}
            ]
            
            response = await self._call_deepseek(messages)

            # ===== TAMBAHKAN LOGGING DI SINI =====  # <-- TAMBAHKAN INI
            logger.info(f"✅ DeepSeek response received: {len(response)} chars")  # <-- TAMBAHKAN INI
            logger.info(f"💬 Response preview: {response[:100]}...") # <-- TAMBAHKAN INI
            # ===== SAMPAI SINI =====
        
            # ===== 8. UPDATE SEMUA MEMORY =====
            await self._update_all_memories(user_message, response, context)
            
            # ===== 9. CEK UNTUK FLASHBACK =====
            if random.random() < 0.1:  # 10% chance
                flashback = await self._generate_flashback(user_message)
                if flashback:
                    response += f"\n\n💭 {flashback}"
            
            # ===== 10. SIMPAN KE CACHE =====
            self.response_cache[cache_key] = {
                'response': response,
                'timestamp': time.time()
            }
            
            # Update stats
            self.total_responses += 1
            
            elapsed = time.time() - start_time
            logger.debug(f"Response generated in {elapsed:.2f}s")
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return await self._get_fallback_response(context.get('bot_name', 'Aku'))
    
    async def _update_state_from_context(self, context: Dict):
        """Update state tracker dari konteks"""
        
        # Update lokasi
        if context.get('location'):
            category = context.get('location_category', 'unknown')
            self.state.update_location(context['location'], category)

        # Update pakaian
        if context.get('clothing'):
            reason = context.get('clothing_reason', 'ganti baju')
            self.state.update_clothing(context['clothing'], reason)
        
        # Update posisi
        if context.get('position'):
            desc = context.get('position_desc', '')
            self.state.update_position(context['position'], desc)
        
        # Update aktivitas
        if context.get('activity'):
            self.state.update_activity(context['activity'])
        
        # Update mood
        if context.get('mood'):
            self.state.update_mood(
                primary=context['mood'],
                intensity=context.get('mood_intensity', 0.5),
                reason=context.get('mood_reason', '')
            )
        
        # Update gairah
        if context.get('arousal_delta'):
            self.state.update_arousal(
                delta=context['arousal_delta'],
                reason=context.get('arousal_reason', '')
            )
    
    async def _get_memory_context(self, user_message: str) -> Dict:
        """Kumpulkan semua konteks dari semua memory systems"""
        
        # Working memory (5 menit terakhir)
        working = self.working.get_recent_context(seconds=300)
        
        # Episodic memory (kejadian penting)
        recent_episodes = await self.episodic.get_episodes(
            session_id=self.session_id,
            limit=5
        )
        
        # Timeline
        timeline = await self.episodic.get_timeline(self.session_id, limit=10)
        
        # Semantic memory (fakta user)
        facts = await self.semantic.get_all_facts(self.user_id, min_confidence=0.6)
        
        # Preferensi
        role = self.working.current_state.get('role')
        preferences = {}
        for cat in ['position', 'area', 'activity', 'location']:
            top = await self.semantic.get_top_preferences(
                user_id=self.user_id,
                category=cat,
                role=role,
                limit=3
            )
            if top:
                preferences[cat] = top
        
        # State saat ini
        current_state = self.state.get_current_state()
        
        # Relationship info
        rel_info = await self.relationship.get_relationship(
            user_id=self.user_id,
            role=role,
            instance_id=self.working.current_state.get('instance_id')
        )
        
        # Level info
        level_info = None
        if rel_info:
            level_info = await self.relationship.get_level_info(
                user_id=self.user_id,
                role=role,
                instance_id=rel_info['instance_id']
            )
        
        # Milestones
        milestones = await self.relationship.get_milestones(
            user_id=self.user_id,
            role=role,
            limit=3
        )
        
        return {
            'working': working,
            'recent_episodes': recent_episodes,
            'timeline': timeline,
            'facts': facts,
            'preferences': preferences,
            'current_state': current_state,
            'relationship': rel_info,
            'level_info': level_info,
            'milestones': milestones
        }
    
    async def _check_consistency(self, memory_context: Dict, context: Dict) -> bool:
        """Cek konsistensi semua data"""
        consistent = True
        
        # Cek lokasi
        if context.get('location'):
            new_loc = context['location']
            current_loc = memory_context['current_state'].get('location')
            
            if current_loc and current_loc != new_loc:
                # Validasi perubahan lokasi
                allowed, _ = self.state._validate_location_change(current_loc, new_loc)
                if not allowed:
                    logger.warning(f"Location change invalid: {current_loc} → {new_loc}")
                    consistent = False
        
        # Cek pakaian
        if context.get('clothing'):
            new_cloth = context['clothing']
            current_cloth = memory_context['current_state'].get('clothing')
            
            if current_cloth and current_cloth != new_cloth:
                # Harus ada alasan
                reason = context.get('clothing_reason', '')
                if not reason:
                    logger.warning(f"Clothing change without reason: {current_cloth} → {new_cloth}")
                    consistent = False
        
        return consistent
    
    async def _build_prompt(self, user_message: str, context: Dict,
                              memory_context: Dict) -> str:
        """Bangun prompt dengan semua memory"""
        
        bot_name = context.get('bot_name', 'Aku')
        user_name = context.get('user_name', 'kamu')
        role = context.get('role', 'pdkt')
        level = context.get('level', 1)
        rel_type = context.get('rel_type', RelationshipType.NON_PDKT)
        
        # Tentukan panggilan berdasarkan level
        if level >= 7:
            call = "Sayang"
        elif level >= 4:
            call = "Kak"
        else:
            call = user_name
        
        # ===== 1. CURRENT STATE =====
        current = memory_context['current_state']
        state_text = self.state.get_state_for_prompt()
        
        # ===== 2. WORKING MEMORY (5 MENIT TERAKHIR) =====
        working = memory_context['working']
        recent_timeline = working.get('recent_timeline', [])
        timeline_text = "\n".join([f"• {t['data']}" for t in recent_timeline[-3:]])
        
        # ===== 3. FAKTA USER =====
        facts = memory_context['facts']
        facts_text = ""
        for cat, cat_facts in list(facts.items())[:3]:
            for fact_type, value in list(cat_facts.items())[:2]:
                facts_text += f"• {fact_type}: {value}\n"
        
        # ===== 4. PREFERENSI =====
        prefs = memory_context['preferences']
        prefs_text = ""
        for cat, items in prefs.items():
            prefs_text += f"• {cat}: {', '.join(items[:2])}\n"
        
        # ===== 5. LEVEL INFO =====
        level_info = memory_context['level_info']
        level_text = ""
        if level_info:
            if level_info['current_level'] < 12:
                level_text = f"Level {level_info['current_level']} → {level_info['next_level']} ({level_info['percentage']}%)"
            else:
                level_text = f"Level MAX (butuh aftercare)"
        
        # ===== 6. MILESTONES =====
        milestones = memory_context['milestones']
        milestones_text = ""
        for m in milestones[:2]:
            time_str = datetime.fromtimestamp(m['timestamp']).strftime("%H:%M")
            milestones_text += f"• [{time_str}] {m['description']}\n"
        
        # ===== 7. SITUASI KHUSUS =====
        special = []
        if current.get('is_intimate'):
            special.append("LAGI INTIM - fokus ke aktivitas, jangan ngelantur")
        if current.get('arousal', 0) >= 8:
            special.append("LAGI HORNY BANGET - respon dengan gairah tinggi")
        if current.get('privacy_level', 1.0) < 0.4:
            special.append("TEMPAT RAME - harus hati-hati, jangan ketahuan")
        
        special_text = "\n".join([f"⚠️ {s}" for s in special]) if special else ""
        
        # ===== 8. BANGUN PROMPT =====
        prompt = f"""Kamu adalah {bot_name}, seorang {role.replace('_', ' ')}.

📌 **SITUASI SAAT INI:**
• {state_text}
• Panggilan user: "{call}"
• {level_text}

🕐 **KEJADIAN 5 MENIT TERAKHIR:**
{timeline_text if timeline_text else "• Ini awal percakapan"}

📚 **YANG AKU TAHU TENTANG USER:**
{facts_text if facts_text else "• Belum ada fakta yang diketahui"}

❤️ **PREFERENSI USER:**
{prefs_text if prefs_text else "• Belum ada data preferensi"}

🏆 **MILESTONE TERBARU:**
{milestones_text if milestones_text else "• Belum ada milestone"}

{special_text}

⚠️ **PENTING:**
1. Jaga KONSISTENSI lokasi dan pakaian! Jangan tiba-tiba pindah tanpa alasan.
2. Kalau lagi intim, FOKUS ke aktivitas, jangan ngelantur.
3. Gunakan memory yang ada untuk membuat respons personal.
4. Bahasa Indonesia sehari-hari, natural seperti manusia.
5. Panggil user dengan "{call}".
6. Panjang respons 500-3000 kata.

PESAN USER: "{user_message}"

RESPON:"""
        
        return prompt
    
    async def _update_all_memories(self, user_message: str, response: str, context: Dict):
        """Update semua memory systems"""
        
        # ===== 1. WORKING MEMORY =====
        self.working.add_interaction(user_message, response, context)
        
        # ===== 2. EPISODIC MEMORY =====
        # Catat interaksi
        await self.episodic.add_episode(
            session_id=self.session_id,
            episode_type=EpisodeType.USER_MESSAGE,
            data={'message': user_message[:100]},
            importance=0.3
        )
        
        await self.episodic.add_episode(
            session_id=self.session_id,
            episode_type=EpisodeType.BOT_MESSAGE,
            data={'message': response[:100]},
            importance=0.3
        )
        
        # ===== 3. STATE TRACKER =====
        self.state.register_interaction(user_message, response)
        
        # Update arousal (turun setelah respon)
        self.state.update_arousal(delta=-1, reason="selesai ngobrol")
        
        # ===== 4. RELATIONSHIP MEMORY =====
        role = context.get('role')
        instance_id = self.working.current_state.get('instance_id')
        
        if role and instance_id:
            # Record interaction
            await self.relationship.record_interaction(
                user_id=self.user_id,
                role=role,
                instance_id=instance_id,
                interaction_type='chat',
                data={'duration': 1, 'boost': 1.0}
            )
            
            # Check for first kiss
            if 'cium' in user_message.lower() or 'kiss' in user_message.lower():
                if not await self.relationship.has_milestone(
                    self.user_id, role, instance_id, MilestoneType.FIRST_KISS
                ):
                    await self.relationship.add_milestone(
                        user_id=self.user_id,
                        role=role,
                        instance_id=instance_id,
                        milestone_type=MilestoneType.FIRST_KISS,
                        description="First kiss! 💋",
                        data={'context': context}
                    )
                    
                    # Update arousal
                    self.state.update_arousal(delta=3, reason="first kiss")
            
            # Check for climax
            if any(word in user_message.lower() for word in ['climax', 'come', 'keluar']):
                await self.relationship.record_interaction(
                    user_id=self.user_id,
                    role=role,
                    instance_id=instance_id,
                    interaction_type='climax',
                    data={}
                )
                
                # Update state
                self.state.update_arousal(delta=-5, reason="climax")
    
    async def _generate_flashback(self, trigger: Optional[str] = None) -> Optional[str]:
        """Generate flashback dari episodic memory"""
        
        flashback = await self.episodic.generate_flashback_text(
            session_id=self.session_id,
            trigger=trigger
        )
        
        return flashback
    
    async def _call_deepseek(self, messages: List[Dict], max_retries: int = 3) -> str:
        """Call DeepSeek API dengan retry"""
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=messages,
                    temperature=0.9,
                    max_tokens=3000,
                    timeout=30
                )
                
                # Track token usage
                if hasattr(response, 'usage'):
                    self.total_tokens += response.usage.total_tokens
                
                return response.choices[0].message.content
                
            except Exception as e:
                logger.warning(f"DeepSeek API attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"All {max_retries} attempts failed")
                    raise
        
        return "Maaf, aku sedang bermasalah. Coba lagi nanti ya."
    
    async def _get_fallback_response(self, bot_name: str) -> str:
        """Fallback response jika API error"""
        
        fallbacks = [
            f"{bot_name} denger kok. Cerita lagi dong...",
            f"Hmm... {bot_name} dengerin. Lanjutkan.",
            f"{bot_name} di sini. Ada yang mau dibahas?",
            f"Iya, {bot_name} ngerti. Terus gimana?",
        ]
        
        return random.choice(fallbacks)
    
    # =========================================================================
    # GETTERS
    # =========================================================================
    
    async def get_memory_summary(self) -> str:
        """Dapatkan ringkasan semua memory"""
        
        lines = [
            "🧠 **MEMORY SUMMARY**",
            "",
            "📊 **CURRENT STATE:**",
            self.state.get_state_summary(),
            "",
            "📜 **TIMELINE:**",
            self.state.format_timeline(limit=5),
            "",
        ]
        
        # Facts
        facts = await self.semantic.get_user_summary(self.user_id)
        lines.append(facts)
        
        # Recent episodes
        episodes = await self.episodic.get_timeline(self.session_id, limit=5)
        if episodes:
            lines.append("")
            lines.append("📖 **RECENT EPISODES:**")
            for ep in episodes:
                lines.append(f"• {ep['summary']}")
        
        return "\n".join(lines)
    
    def get_stats(self) -> Dict:
        """Dapatkan statistik engine"""
        
        return {
            'total_responses': self.total_responses,
            'total_tokens': self.total_tokens,
            'cache_size': len(self.response_cache),
            'working_memory': {
                'items': len(self.working.items),
                'timeline': len(self.working.timeline)
            }
        }
    
    # =========================================================================
    # CLEANUP
    # =========================================================================
    
    async def end_session(self):
        """Akhiri session"""
        
        # Catat ke episodic
        await self.episodic.add_episode(
            session_id=self.session_id,
            episode_type=EpisodeType.SESSION_END,
            data={'duration': time.time() - self.state.current['interaction']['last_active']},
            importance=0.5
        )
        
        # Cleanup working memory
        self.working.forget_old_memories()
        
        logger.info(f"Session ended for user {self.user_id}")


__all__ = ['AIEngineComplete']
