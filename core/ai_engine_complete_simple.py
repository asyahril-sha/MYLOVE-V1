#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Engine Simple - Untuk testing
"""

import logging
import random
import asyncio
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class AIEngineComplete:
    """AI Engine Simple Version untuk testing"""
    
    def __init__(self, api_key: str, user_id: int, session_id: str):
        self.api_key = api_key
        self.user_id = user_id
        self.session_id = session_id
        self.total_responses = 0
        logger.info(f"✅ AIEngineSimple initialized for user {user_id}")
        
    async def start_session(self, role: str, bot_name: str, rel_type: str = "non_pdkt", instance_id: str = None):
        """Mulai session baru"""
        self.role = role
        self.bot_name = bot_name
        logger.info(f"✅ Session started: {role} - {bot_name}")
        return True
        
    async def process_message(self, user_message: str, context: Dict[str, Any] = None) -> str:
        """Proses pesan dan generate response"""
        self.total_responses += 1
        
        bot_name = context.get('bot_name', 'Aku') if context else 'Aku'
        user_name = context.get('user_name', 'kamu') if context else 'kamu'
        
        # Response bervariasi
        responses = [
            f"{bot_name} denger {user_name}. Ceritanya menarik, lanjutkan dong...",
            f"Hmm... {bot_name} mikir. {user_name} tahu nggak, aku suka cara kamu cerita.",
            f"{bot_name} di sini, {user_name}. Aku selalu dengerin kok. Ada lagi?",
            f"Wah, {user_name} bikin {bot_name} penasaran. Cerita lagi yuk!",
            f"{bot_name} senang ngobrol sama {user_name}. Kamu lagi mikirin apa?",
            f"Aku dengerin, {user_name}. Kadang aku juga suka kepikiran hal yang sama.",
            f"{bot_name} selalu ada buat {user_name}. Cerita apa lagi?"
        ]
        
        return random.choice(responses)
    
    async def end_session(self):
        """Akhiri session"""
        logger.info(f"Session ended for {self.user_id}")
