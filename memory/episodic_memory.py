#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - EPISODIC MEMORY
=============================================================================
Ingatan seperti diary - menyimpan urutan kejadian dari awal sampai sekarang
=============================================================================
"""

import time
import logging
import json
import random
from typing import Dict, List, Optional, Any, Tuple
from collections import deque
from datetime import datetime

logger = logging.getLogger(__name__)


class EpisodeType:
    """Tipe-tipe episode/kejadian"""
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    LOCATION_CHANGE = "location_change"
    CLOTHING_CHANGE = "clothing_change"
    POSITION_CHANGE = "position_change"
    MOOD_CHANGE = "mood_change"
    AROUSAL_CHANGE = "arousal_change"
    INTIMACY_START = "intimacy_start"
    INTIMACY_END = "intimacy_end"
    CLIMAX = "climax"
    FIRST_KISS = "first_kiss"
    FIRST_INTIM = "first_intim"
    FIRST_CLIMAX = "first_climax"
    CONFESSION = "confession"
    FIGHT = "fight"
    RECONCILIATION = "reconciliation"
    MILESTONE = "milestone"
    USER_MESSAGE = "user_message"
    BOT_MESSAGE = "bot_message"
    IMPORTANT_TOPIC = "important_topic"
    ACTIVITY_CHANGE = "activity_change"


class EpisodicMemory:
    """
    Menyimpan urutan kejadian seperti diary manusia
    - Kronologis dari awal sampai sekarang
    - Bisa di-flashback
    - Validasi urutan (gak boleh lompat)
    """
    
    def __init__(self, max_episodes: int = 1000):
        """
        Args:
            max_episodes: Maksimal episode yang disimpan (default 1000)
        """
        self.max_episodes = max_episodes
        
        # episodes per session {session_id: deque of episodes}
        self.episodes = {}
        
        # Index untuk pencarian cepat
        self.episode_index = {}
        
        # Timeline per session (ringkasan)
        self.timelines = {}
        
        # Momen penting yang ditandai
        self.important_moments = {}
        
        logger.info(f"✅ EpisodicMemory initialized (max {max_episodes} episodes)")
    
    # =========================================================================
    # EPISODE METHODS UNTUK SEMUA STATE
    # =========================================================================
    
    async def add_location_episode(self, session_id: str, from_loc: str, to_loc: str):
        """Catat perpindahan lokasi sebagai episode"""
        return await self.add_episode(
            session_id=session_id,
            episode_type=EpisodeType.LOCATION_CHANGE,
            data={'from': from_loc, 'to': to_loc},
            importance=0.6
        )
    
    async def add_clothing_episode(self, session_id: str, from_cloth: str, to_cloth: str, reason: str):
        """Catat pergantian pakaian sebagai episode"""
        return await self.add_episode(
            session_id=session_id,
            episode_type=EpisodeType.CLOTHING_CHANGE,
            data={'from': from_cloth, 'to': to_cloth, 'reason': reason},
            importance=0.5
        )
    
    async def add_position_episode(self, session_id: str, from_pos: str, to_pos: str):
        """Catat perubahan posisi sebagai episode"""
        return await self.add_episode(
            session_id=session_id,
            episode_type=EpisodeType.POSITION_CHANGE,
            data={'from': from_pos, 'to': to_pos},
            importance=0.4
        )
    
    async def add_activity_episode(self, session_id: str, from_act: str, to_act: str):
        """Catat perubahan aktivitas sebagai episode"""
        return await self.add_episode(
            session_id=session_id,
            episode_type=EpisodeType.ACTIVITY_CHANGE,
            data={'from': from_act, 'to': to_act},
            importance=0.5
        )
    
    async def add_mood_episode(self, session_id: str, from_mood: str, to_mood: str, reason: str = ""):
        """Catat perubahan mood sebagai episode"""
        return await self.add_episode(
            session_id=session_id,
            episode_type=EpisodeType.MOOD_CHANGE,
            data={'from': from_mood, 'to': to_mood, 'reason': reason},
            importance=0.6
        )
    
    async def add_arousal_episode(self, session_id: str, from_level: int, to_level: int, reason: str = ""):
        """Catat perubahan gairah sebagai episode"""
        return await self.add_episode(
            session_id=session_id,
            episode_type=EpisodeType.AROUSAL_CHANGE,
            data={'from': from_level, 'to': to_level, 'reason': reason},
            importance=0.7
        )
    
    async def add_intimacy_start_episode(self, session_id: str, location: str):
        """Catat mulai intim sebagai episode"""
        return await self.add_episode(
            session_id=session_id,
            episode_type=EpisodeType.INTIMACY_START,
            data={'location': location},
            importance=0.9
        )
    
    async def add_intimacy_end_episode(self, session_id: str, duration: float):
        """Catat selesai intim sebagai episode"""
        return await self.add_episode(
            session_id=session_id,
            episode_type=EpisodeType.INTIMACY_END,
            data={'duration': duration},
            importance=0.8
        )
    
    async def add_climax_episode(self, session_id: str, intensity: int, position: str = ""):
        """Catat climax sebagai episode"""
        return await self.add_episode(
            session_id=session_id,
            episode_type=EpisodeType.CLIMAX,
            data={'intensity': intensity, 'position': position},
            importance=1.0
        )
    
    async def add_first_kiss_episode(self, session_id: str, location: str):
        """Catat first kiss sebagai episode"""
        return await self.add_episode(
            session_id=session_id,
            episode_type=EpisodeType.FIRST_KISS,
            data={'location': location},
            importance=1.0
        )
    
    async def add_first_intim_episode(self, session_id: str, location: str):
        """Catat first intim sebagai episode"""
        return await self.add_episode(
            session_id=session_id,
            episode_type=EpisodeType.FIRST_INTIM,
            data={'location': location},
            importance=1.0
        )
    
    # =========================================================================
    # ADD EPISODE (METHOD UTAMA)
    # =========================================================================
    
    async def add_episode(self,
                         session_id: str,
                         episode_type: str,
                         data: Dict[str, Any],
                         importance: float = 0.5,
                         emotional_tag: Optional[str] = None) -> str:
        """
        Tambah episode baru
        
        Args:
            session_id: ID session
            episode_type: Tipe episode (dari EpisodeType)
            data: Data episode
            importance: Tingkat kepentingan (0-1)
            emotional_tag: Tag emosi (senang, sedih, dll)
            
        Returns:
            episode_id
        """
        
        # Inisialisasi jika belum ada
        if session_id not in self.episodes:
            self.episodes[session_id] = deque(maxlen=self.max_episodes)
        
        if session_id not in self.timelines:
            self.timelines[session_id] = []
        
        # Buat episode ID
        episode_id = self._generate_episode_id(session_id, episode_type)
        
        # Buat episode
        episode = {
            'episode_id': episode_id,
            'session_id': session_id,
            'type': episode_type,
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'data': data,
            'importance': importance,
            'emotional_tag': emotional_tag,
        }
        
        # Simpan episode
        self.episodes[session_id].append(episode)
        
        # Update index
        self.episode_index[episode_id] = {
            'session_id': session_id,
            'index': len(self.episodes[session_id]) - 1
        }
        
        # Buat ringkasan untuk timeline
        summary = self._create_summary(episode)
        self.timelines[session_id].append({
            'time': episode['timestamp'],
            'type': episode_type,
            'summary': summary,
            'episode_id': episode_id
        })
        
        # Jika penting, simpan di important_moments
        if importance >= 0.7:
            if session_id not in self.important_moments:
                self.important_moments[session_id] = []
            self.important_moments[session_id].append(episode_id)
        
        logger.debug(f"Episode added: {episode_type} - {summary}")
        
        return episode_id
    
    def _generate_episode_id(self, session_id: str, episode_type: str) -> str:
        """Generate unique episode ID"""
        timestamp = int(time.time())
        random_suffix = random.randint(1000, 9999)
        return f"EP_{session_id}_{episode_type}_{timestamp}_{random_suffix}"
    
    def _create_summary(self, episode: Dict) -> str:
        """Buat ringkasan singkat untuk timeline"""
        ep_type = episode['type']
        data = episode['data']
        
        summaries = {
            EpisodeType.SESSION_START: "Memulai sesi",
            EpisodeType.SESSION_END: "Mengakhiri sesi",
            EpisodeType.LOCATION_CHANGE: f"Pindah ke {data.get('to', '?')}",
            EpisodeType.CLOTHING_CHANGE: f"Ganti {data.get('to', '?')} ({data.get('reason', 'ganti baju')})",
            EpisodeType.POSITION_CHANGE: f"Ganti posisi ke {data.get('to', '?')}",
            EpisodeType.ACTIVITY_CHANGE: f"Ganti aktivitas ke {data.get('to', '?')}",
            EpisodeType.MOOD_CHANGE: f"Mood berubah: {data.get('from', '?')} → {data.get('to', '?')}",
            EpisodeType.AROUSAL_CHANGE: f"Gairah: {data.get('from', '?')} → {data.get('to', '?')}",
            EpisodeType.INTIMACY_START: "Mulai intim",
            EpisodeType.INTIMACY_END: "Selesai intim",
            EpisodeType.CLIMAX: "Climax! 🔥",
            EpisodeType.FIRST_KISS: "First kiss! 💋",
            EpisodeType.FIRST_INTIM: "First intim! 🔥",
            EpisodeType.CONFESSION: f"{data.get('text', 'Confession')}",
        }
        
        return summaries.get(ep_type, ep_type)
    
    # =========================================================================
    # GET EPISODES
    # =========================================================================
    
    async def get_episodes(self, session_id: str, 
                            episode_type: Optional[str] = None,
                            limit: int = 20,
                            offset: int = 0) -> List[Dict]:
        """
        Dapatkan episode untuk session
        
        Args:
            session_id: ID session
            episode_type: Filter by type
            limit: Jumlah episode
            offset: Mulai dari index ke-
            
        Returns:
            List of episodes
        """
        if session_id not in self.episodes:
            return []
        
        episodes = list(self.episodes[session_id])
        
        # Balik urutan (terbaru dulu)
        episodes.reverse()
        
        if episode_type:
            episodes = [e for e in episodes if e['type'] == episode_type]
        
        return episodes[offset:offset+limit]
    
    async def get_episode(self, episode_id: str) -> Optional[Dict]:
        """Dapatkan episode spesifik"""
        if episode_id not in self.episode_index:
            return None
        
        loc = self.episode_index[episode_id]
        session_id = loc['session_id']
        idx = loc['index']
        
        if session_id in self.episodes and idx < len(self.episodes[session_id]):
            return self.episodes[session_id][idx]
        
        return None
    
    async def get_timeline(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Dapatkan timeline (ringkasan)"""
        if session_id not in self.timelines:
            return []
        
        timeline = self.timelines[session_id]
        timeline.reverse()  # terbaru dulu
        return timeline[:limit]
    
    async def get_important_moments(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Dapatkan momen-momen penting"""
        if session_id not in self.important_moments:
            return []
        
        important_ids = self.important_moments[session_id][-limit:]
        moments = []
        
        for ep_id in important_ids:
            ep = await self.get_episode(ep_id)
            if ep:
                moments.append(ep)
        
        return moments
    
    # =========================================================================
    # FLASHBACK
    # =========================================================================
    
    async def generate_flashback_text(self, session_id: str, 
                                        trigger: Optional[str] = None) -> Optional[str]:
        """
        Generate teks flashback untuk ditampilkan ke user
        
        Args:
            session_id: ID session
            trigger: Kata kunci pemicu
            
        Returns:
            Teks flashback
        """
        if session_id not in self.episodes or not self.episodes[session_id]:
            return None
        
        if trigger:
            # Cari episode yang relevan dengan trigger
            episodes = list(self.episodes[session_id])
            relevant = []
            
            for ep in episodes:
                desc = str(ep.get('data', {})).lower()
                if trigger.lower() in desc:
                    relevant.append(ep)
            
            if relevant:
                episode = random.choice(relevant)
            else:
                episode = random.choice(episodes)
        else:
            episode = random.choice(list(self.episodes[session_id]))
        
        # Format flashback
        time_ago = self._format_time_ago(episode['timestamp'])
        
        templates = {
            EpisodeType.FIRST_KISS: [
                f"Inget gak waktu pertama kita ciuman? {time_ago}...",
                f"First kiss kita dulu... {time_ago}.",
            ],
            EpisodeType.FIRST_INTIM: [
                f"Kali pertama kita intim... {time_ago}. Masih inget?",
                f"First time kita... {time_ago}. Hangat banget.",
            ],
            EpisodeType.CLIMAX: [
                f"Waktu kita climax bareng... {time_ago}. Luar biasa.",
                f"Masih inget climax pertama kita? {time_ago}.",
            ],
            EpisodeType.LOCATION_CHANGE: [
                f"Inget gak waktu kita di {episode['data'].get('to', 'sana')}? {time_ago}.",
            ],
            EpisodeType.CLOTHING_CHANGE: [
                f"Inget gak waktu kamu ganti {episode['data'].get('to', 'baju')}? {time_ago}.",
            ],
        }
        
        default_templates = [
            f"Jadi inget... {episode.get('data', {})} {time_ago}.",
            f"Kangen masa-masa {time_ago}...",
        ]
        
        template_list = templates.get(episode['type'], default_templates)
        
        return random.choice(template_list)
    
    def _format_time_ago(self, timestamp: float) -> str:
        """Format waktu yang lalu"""
        diff = time.time() - timestamp
        
        if diff < 60:
            return "baru aja"
        elif diff < 3600:
            return f"{int(diff/60)} menit lalu"
        elif diff < 86400:
            return f"{int(diff/3600)} jam lalu"
        elif diff < 604800:
            return f"{int(diff/86400)} hari lalu"
        else:
            return f"{int(diff/604800)} minggu lalu"
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    async def get_stats(self, session_id: Optional[str] = None) -> Dict:
        """Dapatkan statistik"""
        if session_id:
            if session_id not in self.episodes:
                return {'total_episodes': 0}
            
            episodes = self.episodes[session_id]
            
            # Hitung per tipe
            type_count = {}
            for ep in episodes:
                ep_type = ep['type']
                type_count[ep_type] = type_count.get(ep_type, 0) + 1
            
            return {
                'session_id': session_id,
                'total_episodes': len(episodes),
                'by_type': type_count,
                'important_moments': len(self.important_moments.get(session_id, [])),
            }
        else:
            # Global stats
            total_sessions = len(self.episodes)
            total_episodes = sum(len(eps) for eps in self.episodes.values())
            
            return {
                'total_sessions': total_sessions,
                'total_episodes': total_episodes,
                'avg_per_session': total_episodes / total_sessions if total_sessions else 0
            }


__all__ = ['EpisodicMemory', 'EpisodeType']
