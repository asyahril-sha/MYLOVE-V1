#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - EPISODIC MEMORY
=============================================================================
Ingatan seperti diary - menyimpan urutan kejadian dari awal sampai sekarang
- Setiap kejadian punya konteks (lokasi, waktu, emosi)
- Bisa flashback ke momen tertentu
- Urutan kejadian tidak boleh lompat-lompat
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
    AFTERCARE = "aftercare"
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
        self.episode_index = {}  # {episode_id: location}
        
        # Timeline per session (ringkasan)
        self.timelines = {}  # {session_id: list of (time, type, summary)}
        
        # Momen penting yang ditandai
        self.important_moments = {}  # {session_id: list of episode_ids}
        
        logger.info(f"✅ EpisodicMemory initialized (max {max_episodes} episodes)")
        
    async def add_location_episode(self, session_id: str, from_loc: str, to_loc: str):
        """Catat perpindahan lokasi sebagai episode"""
        
        await self.add_episode(
            session_id=session_id,
            episode_type="location_change",
            data={
                'from': from_loc,
                'to': to_loc,
                'timestamp': time.time()
            },
            importance=0.6
        )
        logger.debug(f"📍 Location episode recorded: {from_loc} → {to_loc}")
        
    # =========================================================================
    # ADD EPISODE
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
        
        # Validasi urutan
        if not await self._validate_sequence(session_id, episode_type, data):
            logger.warning(f"Episode sequence validation failed for {episode_type}")
            # Tetap simpan tapi kasih warning
        
        # Buat episode ID
        episode_id = self._generate_episode_id(session_id, episode_type)
        
        # Dapatkan episode terakhir untuk konteks
        last_episode = self.episodes[session_id][-1] if self.episodes[session_id] else None
        
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
            'context': {
                'last_episode': last_episode['episode_id'] if last_episode else None,
                'time_since_last': time.time() - (last_episode['timestamp'] if last_episode else 0)
            } if last_episode else None
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
    
    async def _validate_sequence(self, session_id: str, 
                                  new_type: str, new_data: Dict) -> bool:
        """
        Validasi apakah urutan episode masuk akal
        Mencegah lompatan logika
        """
        if session_id not in self.episodes or not self.episodes[session_id]:
            return True
        
        last = self.episodes[session_id][-1]
        last_type = last['type']
        last_data = last['data']
        
        # ===== VALIDASI LOKASI =====
        if new_type == EpisodeType.LOCATION_CHANGE:
            last_loc = last_data.get('to') if last_type == EpisodeType.LOCATION_CHANGE else None
            
            if last_loc:
                new_loc = new_data.get('to')
                # Cek transisi masuk akal
                if not self._is_plausible_location_transition(last_loc, new_loc):
                    logger.warning(f"Invalid location transition: {last_loc} → {new_loc}")
                    return False
        
        # ===== VALIDASI PAKAIAN =====
        if new_type == EpisodeType.CLOTHING_CHANGE:
            last_cloth = last_data.get('to') if last_type == EpisodeType.CLOTHING_CHANGE else None
            
            if last_cloth:
                new_cloth = new_data.get('to')
                reason = new_data.get('reason', '')
                
                # Ganti baju harus ada alasan
                if not reason or len(reason) < 3:
                    logger.warning(f"Clothing change without reason: {last_cloth} → {new_cloth}")
                    return False
        
        # ===== VALIDASI INTIM =====
        if new_type == EpisodeType.INTIMACY_START:
            # Harus di lokasi intim
            loc = new_data.get('location', '')
            intimate_places = ['kamar', 'kamar mandi', 'toilet']
            if not any(p in loc.lower() for p in intimate_places):
                logger.warning(f"Intimacy start in non-intimate location: {loc}")
                return False
        
        return True
    
    def _is_plausible_location_transition(self, from_loc: str, to_loc: str) -> bool:
        """Cek apakah transisi lokasi masuk akal"""
        from_lower = from_loc.lower()
        to_lower = to_loc.lower()
        
        # Transisi yang masuk akal
        plausible = {
            'ruang tamu': ['kamar', 'dapur', 'teras', 'kamar mandi'],
            'kamar': ['kamar mandi', 'ruang tamu'],
            'kamar mandi': ['kamar', 'ruang tamu'],
            'dapur': ['ruang tamu'],
            'teras': ['ruang tamu'],
            'pantai': ['mobil', 'kafe'],
            'mall': ['parkiran', 'mobil'],
            'mobil': ['pantai', 'mall', 'rumah'],
        }
        
        for key, values in plausible.items():
            if key in from_lower:
                return any(v in to_lower for v in values)
        
        return True
    
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
    
    async def get_random_flashback(self, session_id: str, 
                                     min_importance: float = 0.5) -> Optional[Dict]:
        """
        Dapatkan episode random untuk flashback
        
        Args:
            session_id: ID session
            min_importance: Minimal importance
            
        Returns:
            Episode or None
        """
        if session_id not in self.episodes:
            return None
        
        # Filter berdasarkan importance
        episodes = [e for e in self.episodes[session_id] 
                   if e['importance'] >= min_importance]
        
        if not episodes:
            return None
        
        return random.choice(episodes)
    
    async def get_flashback_by_type(self, session_id: str, 
                                      episode_type: str) -> Optional[Dict]:
        """Dapatkan flashback berdasarkan tipe"""
        episodes = await self.get_episodes(session_id, episode_type, limit=10)
        
        if episodes:
            return random.choice(episodes)
        
        return None
    
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
        if trigger:
            # Cari episode yang relevan dengan trigger
            episodes = await self.get_episodes(session_id, limit=50)
            relevant = []
            
            for ep in episodes:
                desc = str(ep.get('data', {})).lower()
                if trigger.lower() in desc:
                    relevant.append(ep)
            
            if relevant:
                episode = random.choice(relevant)
            else:
                episode = await self.get_random_flashback(session_id, 0.7)
        else:
            episode = await self.get_random_flashback(session_id, 0.7)
        
        if not episode:
            return None
        
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
            EpisodeType.CONFESSION: [
                f"Waktu kamu pertama bilang sayang... {time_ago}.",
                f"Aku masih inget waktu kamu confess... {time_ago}.",
            ],
            EpisodeType.LOCATION_CHANGE: [
                f"Inget gak waktu kita di {episode['data'].get('to', 'sana')}? {time_ago}.",
            ],
        }
        
        default_templates = [
            f"Jadi inget... {episode.get('data', {}).get('summary', 'momen itu')} {time_ago}.",
            f"Kangen masa-masa {self._format_time_ago(episode['timestamp'])}...",
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
    # SEARCH
    # =========================================================================
    
    async def search_episodes(self, session_id: str, query: str) -> List[Dict]:
        """Cari episode berdasarkan query"""
        if session_id not in self.episodes:
            return []
        
        query_lower = query.lower()
        results = []
        
        for ep in self.episodes[session_id]:
            # Cari di data
            data_str = json.dumps(ep.get('data', {})).lower()
            if query_lower in data_str:
                results.append(ep)
        
        return results
    
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
                'first_episode': episodes[0] if episodes else None,
                'last_episode': episodes[-1] if episodes else None,
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
    
    # =========================================================================
    # UTILITY
    # =========================================================================
    
    async def clear_session(self, session_id: str):
        """Hapus semua data untuk session"""
        if session_id in self.episodes:
            del self.episodes[session_id]
        if session_id in self.timelines:
            del self.timelines[session_id]
        if session_id in self.important_moments:
            del self.important_moments[session_id]
        
        # Hapus dari index
        to_delete = []
        for ep_id, loc in self.episode_index.items():
            if loc['session_id'] == session_id:
                to_delete.append(ep_id)
        
        for ep_id in to_delete:
            del self.episode_index[ep_id]
        
        logger.info(f"Cleared episodic memory for session {session_id}")
    
    async def format_timeline(self, session_id: str, limit: int = 10) -> str:
        """Format timeline untuk ditampilkan"""
        timeline = await self.get_timeline(session_id, limit)
        
        if not timeline:
            return "Belum ada kejadian"
        
        lines = ["📜 **TIMELINE KEJADIAN:**"]
        
        for t in timeline:
            time_str = datetime.fromtimestamp(t['time']).strftime("%H:%M")
            lines.append(f"• [{time_str}] {t['summary']}")
        
        return "\n".join(lines)


__all__ = ['EpisodicMemory', 'EpisodeType']
