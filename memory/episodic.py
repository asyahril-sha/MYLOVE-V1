#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - EPISODIC MEMORY
=============================================================================
Menyimpan momen-momen spesial dalam hubungan
- First kiss, first intimacy, special dates
- Timeline tracking per role
"""

import json
import time
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import logging
import random

from config import settings

logger = logging.getLogger(__name__)


class EpisodicMemory:
    """
    Menyimpan episode/momen spesial dalam hubungan
    Setiap role punya timeline sendiri
    """
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.memories = {}  # {user_id: {role: [episodes]}}
        self.loaded = False
        
    async def initialize(self):
        """Load memories from file"""
        try:
            if self.db_path.exists():
                with open(self.db_path, 'r') as f:
                    self.memories = json.load(f)
                logger.info(f"📚 Loaded episodic memories from {self.db_path}")
            else:
                self.memories = {}
                logger.info("📚 Created new episodic memory store")
                
            self.loaded = True
            
        except Exception as e:
            logger.error(f"Error loading episodic memories: {e}")
            self.memories = {}
            self.loaded = True
            
    async def save(self):
        """Save memories to file"""
        if not self.loaded:
            return
            
        try:
            # Create directory if not exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.db_path, 'w') as f:
                json.dump(self.memories, f, indent=2)
                
            logger.debug(f"Saved episodic memories to {self.db_path}")
            
        except Exception as e:
            logger.error(f"Error saving episodic memories: {e}")
            
    async def add_episode(self, user_id: int, role: str, episode: Dict):
        """
        Tambah episode/momen spesial
        
        Args:
            user_id: ID user
            role: Role name
            episode: {
                'type': 'first_kiss'|'first_intim'|'first_date'|'special',
                'timestamp': time.time(),
                'description': '...',
                'intimacy_level': 7,
                'emotional_impact': 0.8,
                'location': 'pantai',
                'with_role': role
            }
        """
        if not self.loaded:
            await self.initialize()
            
        user_key = str(user_id)
        if user_key not in self.memories:
            self.memories[user_key] = {}
            
        if role not in self.memories[user_key]:
            self.memories[user_key][role] = []
            
        # Add timestamp if not present
        if 'timestamp' not in episode:
            episode['timestamp'] = time.time()
            
        # Add unique ID
        episode['id'] = f"ep_{user_id}_{role}_{int(time.time())}_{random.randint(100, 999)}"
        
        self.memories[user_key][role].append(episode)
        
        # Sort by timestamp
        self.memories[user_key][role].sort(key=lambda x: x.get('timestamp', 0))
        
        logger.info(f"Added episode for user {user_id} role {role}: {episode.get('type')}")
        
        # Save after adding
        await self.save()
        
    async def get_episodes(self, user_id: int, role: Optional[str] = None,
                           episode_type: Optional[str] = None,
                           limit: int = 10) -> List[Dict]:
        """Get episodes for user"""
        
        if not self.loaded:
            await self.initialize()
            
        user_key = str(user_id)
        if user_key not in self.memories:
            return []
            
        episodes = []
        
        if role:
            # Get for specific role
            if role in self.memories[user_key]:
                episodes = self.memories[user_key][role]
        else:
            # Get all roles
            for role_name, role_episodes in self.memories[user_key].items():
                episodes.extend(role_episodes)
                
        # Filter by type
        if episode_type:
            episodes = [e for e in episodes if e.get('type') == episode_type]
            
        # Sort by timestamp (newest first)
        episodes.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        
        return episodes[:limit]
        
    async def get_first_kiss(self, user_id: int, role: str) -> Optional[Dict]:
        """Get first kiss episode"""
        episodes = await self.get_episodes(user_id, role, 'first_kiss', 1)
        return episodes[0] if episodes else None
        
    async def get_first_intim(self, user_id: int, role: str) -> Optional[Dict]:
        """Get first intimacy episode"""
        episodes = await self.get_episodes(user_id, role, 'first_intim', 1)
        return episodes[0] if episodes else None
        
    async def get_milestones(self, user_id: int, role: str) -> List[Dict]:
        """Get all milestones for role"""
        milestone_types = ['first_kiss', 'first_intim', 'first_date', 
                          'first_fwb', 'first_hts', 'anniversary']
        
        episodes = await self.get_episodes(user_id, role)
        return [e for e in episodes if e.get('type') in milestone_types]
        
    async def get_timeline(self, user_id: int, role: str) -> List[Dict]:
        """Get full timeline for role"""
        episodes = await self.get_episodes(user_id, role)
        return sorted(episodes, key=lambda x: x.get('timestamp', 0))
        
    async def get_recent_memories(self, user_id: int, role: str, 
                                   days: int = 7) -> List[Dict]:
        """Get memories from recent days"""
        cutoff = time.time() - (days * 86400)
        
        episodes = await self.get_episodes(user_id, role)
        return [e for e in episodes if e.get('timestamp', 0) > cutoff]
        
    async def get_important_memories(self, user_id: int, role: str,
                                      threshold: float = 0.7) -> List[Dict]:
        """Get memories with high emotional impact"""
        episodes = await self.get_episodes(user_id, role)
        return [e for e in episodes if e.get('emotional_impact', 0) > threshold]
        
    async def delete_episode(self, episode_id: str):
        """Delete specific episode"""
        for user_key in self.memories:
            for role in self.memories[user_key]:
                self.memories[user_key][role] = [
                    e for e in self.memories[user_key][role] 
                    if e.get('id') != episode_id
                ]
                
        await self.save()
        logger.info(f"Deleted episode {episode_id}")
        
    async def delete_user_memories(self, user_id: int):
        """Delete all memories for user"""
        user_key = str(user_id)
        if user_key in self.memories:
            del self.memories[user_key]
            await self.save()
            logger.info(f"Deleted all episodic memories for user {user_id}")
            
    async def get_stats(self, user_id: Optional[int] = None) -> Dict:
        """Get statistics"""
        
        if user_id:
            user_key = str(user_id)
            if user_key not in self.memories:
                return {"total_episodes": 0}
                
            total = sum(len(eps) for eps in self.memories[user_key].values())
            roles = list(self.memories[user_key].keys())
            
            return {
                "total_episodes": total,
                "roles": roles,
                "by_role": {role: len(eps) for role, eps in self.memories[user_key].items()}
            }
        else:
            # Global stats
            total_users = len(self.memories)
            total_episodes = sum(
                sum(len(eps) for eps in user_data.values())
                for user_data in self.memories.values()
            )
            
            return {
                "total_users": total_users,
                "total_episodes": total_episodes,
                "avg_per_user": total_episodes / total_users if total_users > 0 else 0
            }


__all__ = ['EpisodicMemory']
