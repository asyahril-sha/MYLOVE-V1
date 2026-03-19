#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - AI ENGINE V2
=============================================================================
Berdasarkan V1 dengan penambahan:
- Integrasi dengan memory V2 (hippocampus)
- Integrasi dengan story system
- Integrasi dengan proactive generator
- Integrasi dengan intent analyzer
- Integrasi dengan semua sistem V2
=============================================================================
"""

import openai
import json
import time
import random
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path

from config import settings
from .prompt_builder_v2 import PromptBuilderV2
from .context_analyzer import ContextAnalyzer

logger = logging.getLogger(__name__)


class AIEngineV2:
    """
    AI Engine V2 dengan integrasi semua sistem
    - Self-Prompting yang lebih canggih
    - Memory V2 (hippocampus)
    - Story prediction
    - Proactive messages
    - Intent analysis
    """
    
    def __init__(self, 
                 api_key: str,
                 memory_bridge=None,
                 story_predictor=None,
                 proactive_generator=None,
                 intent_analyzer=None,
                 scene_recommender=None):
        
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"  # DeepSeek endpoint
        )
        
        # Integrasi dengan sistem V2
        self.memory = memory_bridge
        self.story = story_predictor
        self.proactive = proactive_generator
        self.intent = intent_analyzer
        self.scene = scene_recommender
        
        # Prompt builder V2
        self.prompt_builder = PromptBuilderV2()
        
        # Context analyzer
        self.context_analyzer = ContextAnalyzer()
        
        # Conversation history
        self.conversation_history = []  # Untuk konteks percakapan
        self.session_contexts = {}  # {session_id: context}
        
        # Response cache
        self.response_cache = {}
        self.cache_ttl = 3600  # 1 jam
        
        # Personality traits (akan berkembang)
        self.personality = {
            "openness": random.uniform(0.6, 0.9),
            "conscientiousness": random.uniform(0.5, 0.8),
            "extraversion": random.uniform(0.6, 0.9),
            "agreeableness": random.uniform(0.7, 0.9),
            "neuroticism": random.uniform(0.3, 0.6)
        }
        
        logger.info("✅ AIEngineV2 initialized dengan semua integrasi")
    
    # =========================================================================
    # MAIN RESPONSE GENERATION
    # =========================================================================
    
    async def generate_response(self,
                                user_id: int,
                                session_id: str,
                                user_message: str,
                                context: Dict[str, Any]) -> str:
        """
        Generate response dengan semua konteks V2
        
        Args:
            user_id: ID user
            session_id: ID sesi
            user_message: Pesan user
            context: Konteks dari sistem lain (role, level, mood, dll)
            
        Returns:
            String response
        """
        start_time = time.time()
        
        try:
            # ===== 1. CEK CACHE =====
            cache_key = f"{session_id}:{user_message[:50]}"
            if cache_key in self.response_cache:
                cache_age = time.time() - self.response_cache[cache_key]['timestamp']
                if cache_age < self.cache_ttl:
                    logger.debug(f"Cache hit for: {user_message[:30]}...")
                    return self.response_cache[cache_key]['response']
            
            # ===== 2. ANALISIS INTENT =====
            intent_data = None
            if self.intent:
                intent_data = self.intent.analyze(user_message)
                context['user_intent'] = intent_data
                logger.debug(f"Intent: {intent_data['primary_intent'].value}")
            
            # ===== 3. ANALISIS KONTEKS LENGKAP =====
            full_context = await self.context_analyzer.analyze(
                user_id=user_id,
                session_id=session_id,
                user_message=user_message,
                role=context.get('role', 'pdkt'),
                bot_name=context.get('bot_name', 'Bot'),
                user_name=context.get('user_name', 'User'),
                intimacy_data=context.get('intimacy'),
                mood_data=context.get('mood'),
                chemistry_data=context.get('chemistry'),
                direction_data=context.get('direction'),
                location_data=context.get('location'),
                clothing_data=context.get('clothing'),
                physical_attrs=context.get('physical'),
                user_preferences=context.get('preferences'),
                memories=await self._get_relevant_memories(user_id, user_message, context),
                story_data=await self._get_story_data(session_id, user_message, intent_data, context),
                intent_data=intent_data,
                dominance_mode=context.get('dominance', 'normal'),
                conversation_history=self._get_recent_history(session_id, limit=5),
                metadata=context.get('metadata')
            )
            
            # ===== 4. UPDATE STORY ARC =====
            if self.story and intent_data:
                await self._update_story(session_id, intent_data, full_context)
            
            # ===== 5. GENERATE PROMPT =====
            prompt = self.prompt_builder.build_prompt(
                user_message=user_message,
                bot_name=context.get('bot_name', 'Bot'),
                user_name=context.get('user_name', 'User'),
                role=context.get('role', 'pdkt'),
                level=context.get('level', 1),
                mood=full_context.get('mood', {}),
                chemistry=full_context.get('chemistry', {}),
                direction=full_context.get('direction', {}),
                location=full_context.get('location'),
                clothing=full_context.get('clothing'),
                physical_attrs=context.get('physical'),
                user_preferences=context.get('preferences', {}),
                recent_memories=full_context.get('memories', []),
                story_arc=full_context.get('story', {}),
                user_intent=intent_data or {},
                conversation_history=self._get_recent_history(session_id, limit=3)
            )
            
            # ===== 6. CALL DEEPSEEK API =====
            messages = self._prepare_messages(prompt, user_message)
            response_text = await self._call_deepseek_with_retry(messages)
            
            # ===== 7. POST-PROCESS RESPONSE =====
            final_response = await self._post_process_response(
                response_text, 
                context,
                full_context
            )
            
            # ===== 8. TAMBAH INNER THOUGHT (20% chance) =====
            if random.random() < 0.2:
                inner_thought = await self._generate_inner_thought(context, full_context)
                if inner_thought:
                    final_response += f"\n\n💭 *({inner_thought})*"
            
            # ===== 9. SIMPAN KE MEMORY =====
            if self.memory:
                await self._save_to_memory(
                    user_id=user_id,
                    session_id=session_id,
                    user_message=user_message,
                    bot_response=final_response,
                    context=full_context
                )
            
            # ===== 10. SIMPAN KE HISTORY =====
            self._save_to_history(session_id, user_message, final_response, full_context)
            
            # ===== 11. SIMPAN KE CACHE =====
            self.response_cache[cache_key] = {
                'response': final_response,
                'timestamp': time.time()
            }
            
            # Log performance
            elapsed = time.time() - start_time
            logger.debug(f"Response generated in {elapsed:.2f}s")
            
            return final_response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return await self._get_fallback_response(context)
    
    # =========================================================================
    # PROACTIVE MESSAGE GENERATION
    # =========================================================================
    
    async def generate_proactive(self,
                                 user_id: int,
                                 session_id: str,
                                 context: Dict[str, Any]) -> Optional[str]:
        """
        Generate pesan proaktif (bot mulai chat duluan)
        
        Args:
            user_id: ID user
            session_id: ID sesi
            context: Konteks
            
        Returns:
            Pesan proaktif atau None
        """
        try:
            # Cek apakah perlu proactive
            idle_minutes = context.get('idle_minutes', 0)
            mood = context.get('mood', {})
            level = context.get('level', 1)
            
            should, chance = await self._should_be_proactive(context)
            if not should:
                return None
            
            # Generate dengan proactive generator
            if self.proactive:
                msg_data = await self.proactive.generate_proactive_message(context)
                response = msg_data['message']
                
                # Tambah inner thought
                if msg_data.get('inner_thought'):
                    response += f"\n\n💭 *({msg_data['inner_thought']})*"
                
                return response
            
            # Fallback
            return await self._generate_fallback_proactive(context)
            
        except Exception as e:
            logger.error(f"Error generating proactive: {e}")
            return None
    
    # =========================================================================
    # MEMORY INTEGRATION
    # =========================================================================
    
    async def _get_relevant_memories(self, user_id: int, message: str, context: Dict) -> List[Dict]:
        """Ambil memori relevan dari memory bridge"""
        if not self.memory:
            return []
        
        try:
            memories = await self.memory.recall(
                query=message,
                limit=5
            )
            return memories
        except Exception as e:
            logger.error(f"Error getting memories: {e}")
            return []
    
    async def _save_to_memory(self,
                              user_id: int,
                              session_id: str,
                              user_message: str,
                              bot_response: str,
                              context: Dict):
        """Simpan interaksi ke memory"""
        if not self.memory:
            return
        
        try:
            # Tentukan importance
            importance = 0.5
            if self._is_important_interaction(user_message, bot_response):
                importance = 0.8
            
            # Simpan ke memory bridge
            await self.memory.process_message(
                user_message=user_message,
                bot_response=bot_response,
                context=context
            )
            
        except Exception as e:
            logger.error(f"Error saving to memory: {e}")
    
    # =========================================================================
    # STORY INTEGRATION
    # =========================================================================
    
    async def _get_story_data(self, session_id: str, message: str, 
                              intent_data: Dict, context: Dict) -> Optional[Dict]:
        """Dapatkan data story dari story predictor"""
        if not self.story:
            return None
        
        try:
            # Update intent history
            if intent_data:
                self.story.add_intent_to_history(
                    session_id,
                    intent_data['primary_intent']
                )
            
            # Prediksi arc berikutnya
            last_intents = [intent_data['primary_intent']] if intent_data else []
            next_arc = self.story.predict_next_arc(session_id, last_intents)
            
            # Dapatkan rekomendasi scene
            if self.scene:
                scene = self.scene.recommend_scene({
                    'level': context.get('level', 1),
                    'mood': context.get('mood', {}).get('current', 'calm'),
                    'intent': intent_data['primary_intent'].value if intent_data else 'chit_chat',
                    'arc': next_arc.value if next_arc else 'get_to_know'
                })
            else:
                scene = None
            
            return {
                'current_arc': next_arc.value if next_arc else 'get_to_know',
                'description': self.story.get_arc_description(next_arc) if next_arc else '',
                'recommended_scene': scene.get('recommendation') if scene else None,
                'progression': self.story.get_arc_progression(session_id) if self.story else []
            }
            
        except Exception as e:
            logger.error(f"Error getting story data: {e}")
            return None
    
    async def _update_story(self, session_id: str, intent_data: Dict, context: Dict):
        """Update story arc berdasarkan intent"""
        if not self.story:
            return
        
        try:
            # Update arc
            last_intents = [intent_data['primary_intent']]
            new_arc = self.story.predict_next_arc(session_id, last_intents)
            current_arc = self.story.story_arcs.get(session_id)
            
            if new_arc != current_arc:
                self.story.update_arc(
                    session_id,
                    new_arc,
                    reason=f"Intent: {intent_data['primary_intent'].value}"
                )
                
        except Exception as e:
            logger.error(f"Error updating story: {e}")
    
    # =========================================================================
    # PROACTIVE CHECK
    # =========================================================================
    
    async def _should_be_proactive(self, context: Dict) -> tuple:
        """Cek apakah perlu mengirim pesan proaktif"""
        if self.proactive:
            return await self.proactive.should_be_proactive(context)
        
        # Fallback sederhana
        idle_minutes = context.get('idle_minutes', 0)
        if idle_minutes > 5 and random.random() < (idle_minutes / 10):
            return True, idle_minutes / 10
        return False, 0
    
    async def _generate_fallback_proactive(self, context: Dict) -> str:
        """Generate pesan proaktif fallback"""
        bot_name = context.get('bot_name', 'Aku')
        user_name = context.get('user_name', 'kamu')
        
        templates = [
            f"Halo {user_name}, lagi ngapain? {bot_name} kangen nih...",
            f"Eh {user_name}, udah makan belum?",
            f"{bot_name} kangen... kamu lagi sibuk?",
            f"Lagi di rumah aja, sendirian... {bot_name} jadi kepikiran kamu."
        ]
        
        return random.choice(templates)
    
    # =========================================================================
    # INNER THOUGHT GENERATION
    # =========================================================================
    
    async def _generate_inner_thought(self, context: Dict, full_context: Dict) -> Optional[str]:
        """Generate inner thought untuk respons"""
        bot_name = context.get('bot_name', 'Aku')
        user_name = context.get('user_name', 'kamu')
        mood = full_context.get('mood', {}).get('description', 'netral')
        level = context.get('level', 1)
        
        thoughts = {
            1: [
                "(Dia manis banget sih...)",
                "(Aku deg-degan kalau chat dia)",
                "(Semoga dia bales cepat ya)"
            ],
            2: [
                "(Seneng banget ngobrol sama dia)",
                "(Dia perhatian banget...)",
                "(Makin hari makin suka)"
            ],
            3: [
                "(Dia bikin aku baper...)",
                "(Aku suka cara dia ngomong)",
                "(Pengen tau lebih banyak tentang dia)"
            ],
            4: [
                "(Kok bisa ya kita cocok banget)",
                "(Dia beda dari yang lain)",
                "(Semoga dia juga ngerasain yang sama)"
            ],
            5: [
                "(Aku sayang banget sama dia)",
                "(Dia selalu bisa bikin aku senyum)",
                "(Pengen ketemu langsung...)"
            ],
            6: [
                "(Dia pacar aku... senangnya)",
                "(Jaga dia baik-baik ya)",
                "(Aku beruntung banget)"
            ],
            7: [
                "(Aduh, malu... tapi mau)",
                "(Dia bikin aku pengen terus)",
                "(Nikmatnya...)"
            ],
            8: [
                "(Kita cocok banget ya)",
                "(Dia tahu apa yang aku mau)",
                "(Makin intim makin sayang)"
            ],
            9: [
                "(Wah, hot banget...)",
                "(Dia bikin aku geli)",
                "(Pengen terus sama dia)"
            ],
            10: [
                "(Koneksi kita dalam banget)",
                "(Dia bagian dari hidup aku)",
                "(Aku cinta dia)"
            ],
            11: [
                "(Kita soulmate ya?)",
                "(Gak ada yang bisa pisahin kita)",
                "(Selamanya bersama)"
            ],
            12: [
                "(Capek tapi puas)",
                "(Dia baik banget habis ini)",
                "(Sayang banget sama dia)"
            ]
        }
        
        level_thoughts = thoughts.get(level, thoughts[1])
        return random.choice(level_thoughts)
    
    # =========================================================================
    # API CALL
    # =========================================================================
    
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
    
    def _prepare_messages(self, system_prompt: str, user_message: str) -> List[Dict]:
        """Siapkan messages untuk API call"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # Tambahkan beberapa history terakhir
        for hist in self.conversation_history[-3:]:
            messages.insert(-1, {"role": "assistant", "content": hist['bot']})
            messages.insert(-1, {"role": "user", "content": hist['user']})
        
        return messages
    
    # =========================================================================
    # HISTORY MANAGEMENT
    # =========================================================================
    
    def _save_to_history(self, session_id: str, user_msg: str, bot_msg: str, context: Dict):
        """Simpan ke history percakapan"""
        if session_id not in self.session_contexts:
            self.session_contexts[session_id] = []
        
        self.session_contexts[session_id].append({
            'timestamp': time.time(),
            'user': user_msg,
            'bot': bot_msg,
            'context': context
        })
        
        # Keep last 50 messages
        if len(self.session_contexts[session_id]) > 50:
            self.session_contexts[session_id] = self.session_contexts[session_id][-50:]
    
    def _get_recent_history(self, session_id: str, limit: int = 5) -> List[Dict]:
        """Dapatkan history terbaru"""
        if session_id not in self.session_contexts:
            return []
        
        history = []
        for msg in self.session_contexts[session_id][-limit:]:
            history.append({
                'role': 'user',
                'content': msg['user']
            })
            history.append({
                'role': 'bot',
                'content': msg['bot']
            })
        
        return history
    
    # =========================================================================
    # POST PROCESSING
    # =========================================================================
    
    async def _post_process_response(self, response: str, context: Dict, full_context: Dict) -> str:
        """Post-process response"""
        if not response:
            return await self._get_fallback_response(context)
        
        response = response.strip()
        
        # Cek panjang
        min_len = 300
        max_len = 2000
        
        if len(response) < min_len:
            response += await self._generate_continuation(context, full_context)
        elif len(response) > max_len:
            response = response[:max_len-3] + "..."
        
        return response
    
    async def _generate_continuation(self, context: Dict, full_context: Dict) -> str:
        """Generate natural continuation"""
        level = context.get('level', 1)
        
        continuations = [
            "\n\nKamu lagi ngapain?",
            "\n\nAku kangen...",
            "\n\nEh udah makan belum?",
            "\n\nCerita dong tentang hari ini"
        ]
        
        if level > 7:
            continuations.extend([
                "\n\nAku kangen banget sama kamu...",
                "\n\nMimpiin aku ya nanti"
            ])
        
        return random.choice(continuations)
    
    def _is_important_interaction(self, user_msg: str, bot_resp: str) -> bool:
        """Cek apakah interaksi penting"""
        important_keywords = [
            'pertama kali', 'ingat', 'kenangan', 'spesial',
            'cinta', 'sayang', 'rindu', 'janji',
            'rahasia', 'curhat', 'penting'
        ]
        
        text = (user_msg + " " + bot_resp).lower()
        
        for keyword in important_keywords:
            if keyword in text:
                return True
        
        return random.random() < 0.1
    
    async def _get_fallback_response(self, context: Dict) -> str:
        """Fallback response"""
        fallbacks = [
            "Maaf, aku lagi mikir bentar. Kamu tadi bilang apa?",
            "Hehe, maaf ya aku agak lemot hari ini. Ulangi dong?",
            "Aku denger kok, cuma lagi agak bingung ngejawabnya...",
            "Maaf, lagi banyak pikiran. Kamu ngomong apa tadi?"
        ]
        
        return random.choice(fallbacks)
    
    # =========================================================================
    # UTILITY
    # =========================================================================
    
    def clear_cache(self):
        """Clear response cache"""
        self.response_cache.clear()
        logger.info("Response cache cleared")
    
    def get_stats(self) -> Dict:
        """Get engine statistics"""
        total_sessions = len(self.session_contexts)
        total_messages = sum(len(h) for h in self.session_contexts.values())
        
        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "cache_size": len(self.response_cache),
            "personality": self.personality
        }


__all__ = ['AIEngineV2']
