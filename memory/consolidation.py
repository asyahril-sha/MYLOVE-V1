#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - MEMORY CONSOLIDATION
=============================================================================
- "Tidur" memori berdasarkan jumlah interaksi
- Forgetting otomatis untuk memori tidak penting
- Kompresi memori berdasarkan importance score
- BUKAN real time, tapi berdasarkan jumlah chat
"""

import time
import json
import asyncio
import logging
import random
import math
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class MemoryConsolidation:
    """
    Memory consolidation berdasarkan jumlah interaksi
    BUKAN real time - menggunakan hitungan chat
    """
    
    def __init__(self, db_path: Path, vector_memory, episodic_memory, semantic_memory):
        self.db_path = db_path
        self.vector_memory = vector_memory
        self.episodic_memory = episodic_memory
        self.semantic_memory = semantic_memory
        
        # Threshold untuk importance (0-1)
        self.importance_thresholds = {
            'high': 0.8,      # Tetap disimpan
            'medium': 0.5,    # Mungkin di-forget
            'low': 0.3        # Kemungkinan besar di-forget
        }
        
        # Stats
        self.total_consolidations = 0
        self.total_memories_forgotten = 0
        
        # Target chat per level (BUKAN waktu)
        self.chat_targets = {
            1: 5,      # Level 1: 0-5 chat
            2: 15,     # Level 2: 6-15 chat
            3: 30,     # Level 3: 16-30 chat
            4: 50,     # Level 4: 31-50 chat
            5: 75,     # Level 5: 51-75 chat
            6: 100,    # Level 6: 76-100 chat
            7: 130,    # Level 7: 101-130 chat
            8: 165,    # Level 8: 131-165 chat
            9: 205,    # Level 9: 166-205 chat
            10: 250,   # Level 10: 206-250 chat
            11: 300,   # Level 11: 251-300 chat
            12: 350,   # Level 12: 301-350 chat (aftercare)
        }
        
        logger.info("✅ MemoryConsolidation initialized (CHAT-BASED)")
        
    # =========================================================================
    # INTIMACY LEVEL BERDASARKAN JUMLAH CHAT
    # =========================================================================
    
    def get_intimacy_level_from_chats(self, total_chats: int) -> int:
        """
        Hitung intimacy level berdasarkan jumlah chat
        BUKAN berdasarkan waktu real
        """
        for level, target in sorted(self.chat_targets.items()):
            if total_chats <= target:
                return level
        return 12  # Maximum level
        
    def get_chats_needed_for_next_level(self, total_chats: int) -> int:
        """Hitung berapa chat lagi untuk naik level"""
        current_level = self.get_intimacy_level_from_chats(total_chats)
        
        if current_level >= 12:
            return 0  # Already max
            
        next_target = self.chat_targets[current_level + 1]
        return max(0, next_target - total_chats)
        
    def get_chat_range_for_level(self, level: int) -> tuple:
        """Dapatkan range chat untuk level tertentu"""
        if level == 1:
            return (0, self.chat_targets[1])
        elif level == 12:
            return (self.chat_targets[11], self.chat_targets[12])
        else:
            return (self.chat_targets[level-1] + 1, self.chat_targets[level])
            
    def calculate_importance_from_chats(self, chat_count: int, memory_age_in_chats: int) -> float:
        """
        Hitung importance score berdasarkan jumlah chat
        
        Args:
            chat_count: Total chat yang sudah terjadi
            memory_age_in_chats: Berapa chat yang lalu memory ini dibuat
            
        Returns:
            importance score (0-1)
        """
        # Base importance
        importance = 0.7
        
        # Memory lebih penting jika masih baru (dalam hitungan chat)
        if memory_age_in_chats < 10:
            importance += 0.2
        elif memory_age_in_chats < 50:
            importance += 0.1
        elif memory_age_in_chats > 200:
            importance -= 0.2
            
        # Memory lebih penting jika total chat masih sedikit
        if chat_count < 100:
            importance += 0.1
            
        return max(0.1, min(1.0, importance))
        
    # =========================================================================
    # MEMORY CONSOLIDATION (BERDASARKAN JUMLAH CHAT)
    # =========================================================================
    
    async def consolidate(self, user_id: int, total_chats: int):
        """
        Lakukan konsolidasi memori berdasarkan jumlah chat
        Dipanggil setiap N chat, bukan berdasarkan waktu
        """
        logger.info(f"🧠 Consolidating memories for user {user_id} (total chats: {total_chats})")
        
        try:
            # 1. Hitung importance untuk semua memori
            memories = await self._get_all_memories(user_id)
            
            # 2. Tentukan mana yang di-forget
            to_forget = []
            to_keep = []
            
            for memory in memories:
                # Hitung age in chats
                memory_chat_count = memory.get('metadata', {}).get('chat_count', total_chats)
                age_in_chats = total_chats - memory_chat_count
                
                # Hitung importance
                importance = self.calculate_importance_from_chats(
                    total_chats, age_in_chats
                )
                
                # Adjust berdasarkan metadata
                if memory.get('metadata', {}).get('emotional_tag') in ['senang', 'rindu']:
                    importance += 0.1
                    
                if memory.get('metadata', {}).get('has_sexual') == 'True':
                    importance += 0.1
                    
                # Decision
                if importance < self.importance_thresholds['low']:
                    to_forget.append(memory)
                else:
                    to_keep.append(memory)
                    
            # 3. Lupakan memori yang tidak penting
            for memory in to_forget:
                await self._forget_memory(user_id, memory)
                self.total_memories_forgotten += 1
                
            # 4. Update stats
            self.total_consolidations += 1
            
            logger.info(f"✅ Consolidation complete: kept {len(to_keep)}, forgot {len(to_forget)}")
            
            return {
                'kept': len(to_keep),
                'forgotten': len(to_forget),
                'total_chats': total_chats
            }
            
        except Exception as e:
            logger.error(f"Error during consolidation: {e}")
            return None
            
    async def _get_all_memories(self, user_id: int) -> List[Dict]:
        """Get all memories for user from all systems"""
        memories = []
        
        # Get from vector memory
        if self.vector_memory:
            try:
                # Get recent memories
                recent = await self.vector_memory.get_recent(user_id, limit=100)
                memories.extend(recent)
            except:
                pass
                
        # Get from episodic memory
        if self.episodic_memory:
            try:
                episodes = await self.episodic_memory.get_episodes(user_id, limit=100)
                for ep in episodes:
                    memories.append({
                        'content': ep.get('description', ''),
                        'metadata': {
                            'importance': ep.get('emotional_impact', 0.5),
                            'type': 'episodic',
                            'timestamp': ep.get('timestamp', 0)
                        }
                    })
            except:
                pass
                
        return memories
        
    async def _forget_memory(self, user_id: int, memory: Dict):
        """Lupakan memori tertentu"""
        try:
            # Delete from vector DB
            if self.vector_memory and memory.get('id'):
                await self.vector_memory.delete_memory(memory['id'])
                
            logger.debug(f"Forgot memory: {memory.get('content', '')[:50]}...")
            
        except Exception as e:
            logger.error(f"Error forgetting memory: {e}")
            
    # =========================================================================
    # MEMORY COMPRESSION
    # =========================================================================
    
    async def compress_memories(self, user_id: int, total_chats: int):
        """
        Kompres memori serupa menjadi satu
        Dipanggil setiap 100 chat
        """
        if total_chats % 100 != 0:
            return
            
        logger.info(f"🗜️ Compressing memories for user {user_id} at {total_chats} chats")
        
        try:
            # Get all memories
            memories = await self._get_all_memories(user_id)
            
            # Group similar memories (sederhana)
            groups = {}
            for memory in memories:
                content = memory.get('content', '')[:50]  # Prefix
                if content not in groups:
                    groups[content] = []
                groups[content].append(memory)
                
            # Compress groups with >3 similar memories
            compressed_count = 0
            for content, group in groups.items():
                if len(group) > 3:
                    # Keep only the most important one
                    best = max(group, key=lambda x: x.get('metadata', {}).get('importance', 0))
                    
                    # Forget others
                    for memory in group:
                        if memory != best:
                            await self._forget_memory(user_id, memory)
                            compressed_count += 1
                            
            logger.info(f"✅ Compressed {compressed_count} memories")
            
        except Exception as e:
            logger.error(f"Error compressing memories: {e}")
            
    # =========================================================================
    # MEMORY CONSOLIDATION TRIGGER
    # =========================================================================
    
    async def check_and_consolidate(self, user_id: int, total_chats: int):
        """
        Cek apakah perlu konsolidasi berdasarkan jumlah chat
        Dipanggil setiap kali user chat
        """
        # Consolidate every 50 chats
        if total_chats % 50 == 0:
            return await self.consolidate(user_id, total_chats)
            
        # Compress every 100 chats
        if total_chats % 100 == 0:
            return await self.compress_memories(user_id, total_chats)
            
        return None
        
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    async def get_stats(self) -> Dict:
        """Get consolidation statistics"""
        return {
            "total_consolidations": self.total_consolidations,
            "total_memories_forgotten": self.total_memories_forgotten,
            "chat_targets": self.chat_targets
        }
        
    async def get_intimacy_progress(self, total_chats: int) -> Dict:
        """Get intimacy progress based on chats"""
        current_level = self.get_intimacy_level_from_chats(total_chats)
        next_level_chats = self.get_chats_needed_for_next_level(total_chats)
        
        # Calculate percentage to next level
        if current_level >= 12:
            percentage = 100
        else:
            current_range = self.get_chat_range_for_level(current_level)
            progress = total_chats - current_range[0]
            total_needed = current_range[1] - current_range[0]
            percentage = min(100, int((progress / total_needed) * 100))
            
        return {
            "current_level": current_level,
            "total_chats": total_chats,
            "next_level_in": next_level_chats,
            "progress_percentage": percentage,
            "chat_range": self.get_chat_range_for_level(current_level)
        }


__all__ = ['MemoryConsolidation']
