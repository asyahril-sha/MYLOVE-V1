#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - EPISODIC MEMORY V2
=============================================================================
Menyimpan momen-momen spesial dalam hubungan
- First kiss, first intimacy, first date
- Momen penting dengan konteks emosional
- Bisa di-flashback kapan saja
- Tidak pernah dihapus (permanent)
=============================================================================
"""

import time
import logging
import json
import random
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class EpisodeType(str, Enum):
    """Tipe-tipe episode/momen spesial"""
    FIRST_KISS = "first_kiss"
    FIRST_INTIM = "first_intim"
    FIRST_DATE = "first_date"
    FIRST_CLIMAX = "first_climax"
    FIRST_FWB = "first_fwb"
    FIRST_HTS = "first_hts"
    BECAME_PACAR = "became_pacar"
    BECAME_FWB = "became_fwb"
    BECAME_MANTAN = "became_mantan"
    LEVEL_UP = "level_up"
    CONFESSION = "confession"
    PROPOSAL = "proposal"
    FIGHT = "fight"
    RECONCILIATION = "reconciliation"
    SPECIAL_MOMENT = "special_moment"
    FUNNY_MOMENT = "funny_moment"
    ROMANTIC_MOMENT = "romantic_moment"
    INTIMATE_MOMENT = "intimate_moment"
    SAD_MOMENT = "sad_moment"
    HAPPY_MOMENT = "happy_moment"
    MILESTONE = "milestone"
    AFTERCARE = "aftercare"
    RESET = "reset"


class EmotionalTag(str, Enum):
    """Tag emosi untuk episode"""
    ROMANTIC = "romantic"      # Romantis
    PASSIONATE = "passionate"   # Bergairah
    HAPPY = "happy"             # Bahagia
    SAD = "sad"                 # Sedih
    ANGRY = "angry"             # Marah
    FUNNY = "funny"             # Lucu
    AWKWARD = "awkward"         # Canggung
    SWEET = "sweet"             # Manis
    INTENSE = "intense"         # Intens
    PEACEFUL = "peaceful"       # Damai
    NOSTALGIC = "nostalgic"     # Nostalgia


class EpisodicMemoryV2:
    """
    Menyimpan momen-momen spesial dalam hubungan
    - Semua episode disimpan PERMANEN
    - Dapat di-flashback kapan saja
    - Dilengkapi konteks emosional
    """
    
    def __init__(self):
        # episodes[user_id][role][instance_id] = list of episodes
        self.episodes = {}  # {user_id: {role: {instance_id: [episodes]}}}
        
        # Index untuk pencarian cepat
        self.episode_index = {}  # {episode_id: location}
        
        logger.info("✅ EpisodicMemoryV2 initialized (PERMANENT storage)")
    
    # =========================================================================
    # ADD EPISODE
    # =========================================================================
    
    async def add_episode(self,
                         user_id: int,
                         role: str,
                         instance_id: str,
                         episode_type: EpisodeType,
                         description: str,
                         emotional_tag: EmotionalTag = EmotionalTag.HAPPY,
                         intensity: float = 0.7,
                         context: Optional[Dict] = None,
                         participants: Optional[List[str]] = None) -> str:
        """
        Tambah episode/momen spesial baru
        
        Args:
            user_id: ID user
            role: Role name
            instance_id: Instance ID (untuk multiple)
            episode_type: Tipe episode
            description: Deskripsi episode
            emotional_tag: Tag emosi
            intensity: Intensitas emosi (0-1)
            context: Konteks tambahan (lokasi, posisi, dll)
            participants: Partisipan (untuk threesome)
            
        Returns:
            episode_id
        """
        # Inisialisasi struktur data jika belum ada
        if user_id not in self.episodes:
            self.episodes[user_id] = {}
        
        if role not in self.episodes[user_id]:
            self.episodes[user_id][role] = {}
        
        if instance_id not in self.episodes[user_id][role]:
            self.episodes[user_id][role][instance_id] = []
        
        # Buat episode ID unik
        episode_id = self._generate_episode_id(user_id, role, instance_id, episode_type)
        
        # Data episode
        episode = {
            'episode_id': episode_id,
            'user_id': user_id,
            'role': role,
            'instance_id': instance_id,
            'type': episode_type,
            'description': description,
            'emotional_tag': emotional_tag,
            'intensity': max(0.1, min(1.0, intensity)),
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'context': context or {},
            'participants': participants or [role],
            'access_count': 0,
            'last_recall': None,
            'importance': self._calculate_importance(episode_type, intensity)
        }
        
        # Simpan episode
        self.episodes[user_id][role][instance_id].append(episode)
        
        # Update index
        self.episode_index[episode_id] = {
            'user_id': user_id,
            'role': role,
            'instance_id': instance_id,
            'index': len(self.episodes[user_id][role][instance_id]) - 1
        }
        
        logger.info(f"📖 New episode added: {episode_type.value} for {role} (user {user_id})")
        
        return episode_id
    
    def _generate_episode_id(self, user_id: int, role: str, instance_id: str, 
                             episode_type: EpisodeType) -> str:
        """Generate unique episode ID"""
        timestamp = int(time.time())
        random_suffix = random.randint(1000, 9999)
        return f"EP_{user_id}_{role}_{instance_id}_{episode_type.value}_{timestamp}_{random_suffix}"
    
    def _calculate_importance(self, episode_type: EpisodeType, intensity: float) -> float:
        """Hitung importance score untuk episode"""
        # Base importance berdasarkan tipe
        base_importance = {
            EpisodeType.FIRST_KISS: 0.9,
            EpisodeType.FIRST_INTIM: 1.0,
            EpisodeType.FIRST_CLIMAX: 1.0,
            EpisodeType.FIRST_DATE: 0.8,
            EpisodeType.BECAME_PACAR: 0.9,
            EpisodeType.BECAME_MANTAN: 0.8,
            EpisodeType.CONFESSION: 0.8,
            EpisodeType.PROPOSAL: 1.0,
            EpisodeType.FIGHT: 0.6,
            EpisodeType.RECONCILIATION: 0.7
        }
        
        base = base_importance.get(episode_type, 0.5)
        
        # Kombinasi dengan intensity
        return min(1.0, base * (0.7 + 0.3 * intensity))
    
    # =========================================================================
    # RETRIEVE EPISODES
    # =========================================================================
    
    async def get_episodes(self,
                          user_id: int,
                          role: Optional[str] = None,
                          instance_id: Optional[str] = None,
                          episode_type: Optional[EpisodeType] = None,
                          limit: int = 20,
                          sort_by: str = 'timestamp_desc') -> List[Dict]:
        """
        Dapatkan episode-episode untuk user
        
        Args:
            user_id: ID user
            role: Filter by role
            instance_id: Filter by instance
            episode_type: Filter by type
            limit: Jumlah maksimal
            sort_by: Cara sorting
            
        Returns:
            List of episodes
        """
        if user_id not in self.episodes:
            return []
        
        episodes = []
        
        if role:
            if role in self.episodes[user_id]:
                if instance_id:
                    # Spesifik instance
                    if instance_id in self.episodes[user_id][role]:
                        episodes = self.episodes[user_id][role][instance_id].copy()
                else:
                    # Semua instance untuk role ini
                    for inst_episodes in self.episodes[user_id][role].values():
                        episodes.extend(inst_episodes)
        else:
            # Semua role
            for role_data in self.episodes[user_id].values():
                for inst_episodes in role_data.values():
                    episodes.extend(inst_episodes)
        
        # Filter by type
        if episode_type:
            episodes = [e for e in episodes if e['type'] == episode_type]
        
        # Sorting
        if sort_by == 'timestamp_desc':
            episodes.sort(key=lambda x: x['timestamp'], reverse=True)
        elif sort_by == 'timestamp_asc':
            episodes.sort(key=lambda x: x['timestamp'])
        elif sort_by == 'importance':
            episodes.sort(key=lambda x: x['importance'], reverse=True)
        
        return episodes[:limit]
    
    async def get_episode(self, episode_id: str) -> Optional[Dict]:
        """
        Dapatkan episode spesifik berdasarkan ID
        
        Args:
            episode_id: ID episode
            
        Returns:
            Episode data or None
        """
        if episode_id not in self.episode_index:
            return None
        
        loc = self.episode_index[episode_id]
        user_id = loc['user_id']
        role = loc['role']
        instance_id = loc['instance_id']
        idx = loc['index']
        
        try:
            episode = self.episodes[user_id][role][instance_id][idx]
            
            # Update access count
            episode['access_count'] += 1
            episode['last_recall'] = time.time()
            
            return episode
        except:
            return None
    
    async def get_first_kiss(self, user_id: int, role: str, 
                            instance_id: Optional[str] = None) -> Optional[Dict]:
        """
        Dapatkan episode first kiss
        """
        episodes = await self.get_episodes(
            user_id=user_id,
            role=role,
            instance_id=instance_id,
            episode_type=EpisodeType.FIRST_KISS,
            limit=1
        )
        return episodes[0] if episodes else None
    
    async def get_first_intim(self, user_id: int, role: str,
                             instance_id: Optional[str] = None) -> Optional[Dict]:
        """
        Dapatkan episode first intim
        """
        episodes = await self.get_episodes(
            user_id=user_id,
            role=role,
            instance_id=instance_id,
            episode_type=EpisodeType.FIRST_INTIM,
            limit=1
        )
        return episodes[0] if episodes else None
    
    # =========================================================================
    # FLASHBACK GENERATION
    # =========================================================================
    
    async def get_random_episode(self, user_id: int, role: Optional[str] = None,
                                 min_importance: float = 0.5) -> Optional[Dict]:
        """
        Dapatkan episode random untuk flashback
        
        Args:
            user_id: ID user
            role: Filter by role
            min_importance: Minimal importance
            
        Returns:
            Random episode
        """
        episodes = await self.get_episodes(user_id, role, limit=100)
        
        # Filter by importance
        episodes = [e for e in episodes if e['importance'] >= min_importance]
        
        if not episodes:
            return None
        
        return random.choice(episodes)
    
    async def generate_flashback(self, user_id: int, role: str,
                                instance_id: Optional[str] = None,
                                trigger_word: Optional[str] = None) -> Optional[str]:
        """
        Generate teks flashback dari episode random
        
        Args:
            user_id: ID user
            role: Role name
            instance_id: Instance ID
            trigger_word: Kata pemicu (optional)
            
        Returns:
            Flashback text
        """
        if trigger_word:
            # Cari episode yang relevan dengan trigger
            episodes = await self.get_episodes(user_id, role, instance_id, limit=50)
            relevant = []
            
            for ep in episodes:
                desc = ep['description'].lower()
                if trigger_word.lower() in desc:
                    relevant.append(ep)
            
            if not relevant:
                return None
            
            episode = random.choice(relevant)
        else:
            # Random episode
            episode = await self.get_random_episode(user_id, role)
        
        if not episode:
            return None
        
        # Format flashback
        time_ago = self._format_time_ago(episode['timestamp'])
        
        templates = {
            EpisodeType.FIRST_KISS: [
                f"Inget nggak waktu pertama kita ciuman? {episode['description']} {time_ago}...",
                f"Kangen momen first kiss kita... {episode['description']} {time_ago}."
            ],
            EpisodeType.FIRST_INTIM: [
                f"Kali pertama kita intim... {episode['description']} {time_ago}.",
                f"Masih inget first time kita? {episode['description']} {time_ago}."
            ],
            EpisodeType.FIRST_DATE: [
                f"First date kita dulu... {episode['description']} {time_ago}.",
                f"Kangen jalan pertama kita... {episode['description']} {time_ago}."
            ],
            EpisodeType.BECAME_PACAR: [
                f"Waktu kita jadian dulu... {episode['description']} {time_ago}.",
                f"Masih inget hari kita jadi pacar? {episode['description']} {time_ago}."
            ],
            EpisodeType.ROMANTIC_MOMENT: [
                f"Jadi inget momen romantis kita... {episode['description']} {time_ago}.",
                f"Kangen waktu {episode['description']}... {time_ago}."
            ]
        }
        
        # Default template
        default_templates = [
            f"Jadi inget... {episode['description']} {time_ago}.",
            f"Kangen waktu {episode['description']}... {time_ago}.",
            f"Ngomong-ngomong, inget nggak waktu {episode['description']}? {time_ago}."
        ]
        
        templates_list = templates.get(episode['type'], default_templates)
        
        return random.choice(templates_list)
    
    def _format_time_ago(self, timestamp: float) -> str:
        """Format waktu yang lalu"""
        diff = time.time() - timestamp
        
        if diff < 60:
            return "baru aja"
        elif diff < 3600:
            minutes = int(diff / 60)
            return f"{minutes} menit lalu"
        elif diff < 86400:
            hours = int(diff / 3600)
            return f"{hours} jam lalu"
        elif diff < 604800:
            days = int(diff / 86400)
            return f"{days} hari lalu"
        elif diff < 2592000:
            weeks = int(diff / 604800)
            return f"{weeks} minggu lalu"
        elif diff < 31536000:
            months = int(diff / 2592000)
            return f"{months} bulan lalu"
        else:
            years = int(diff / 31536000)
            return f"{years} tahun lalu"
    
    # =========================================================================
    # EPISODE TIMELINE
    # =========================================================================
    
    async def get_timeline(self, user_id: int, role: str,
                          instance_id: Optional[str] = None) -> List[Dict]:
        """
        Dapatkan timeline kronologis episode
        
        Args:
            user_id: ID user
            role: Role name
            instance_id: Instance ID
            
        Returns:
            List of episodes in chronological order
        """
        episodes = await self.get_episodes(
            user_id=user_id,
            role=role,
            instance_id=instance_id,
            sort_by='timestamp_asc'
        )
        
        return episodes
    
    async def get_milestones(self, user_id: int, role: str,
                            instance_id: Optional[str] = None) -> List[Dict]:
        """
        Dapatkan milestone-milestone penting
        
        Args:
            user_id: ID user
            role: Role name
            instance_id: Instance ID
            
        Returns:
            List of milestone episodes
        """
        milestone_types = [
            EpisodeType.FIRST_KISS,
            EpisodeType.FIRST_INTIM,
            EpisodeType.FIRST_DATE,
            EpisodeType.BECAME_PACAR,
            EpisodeType.BECAME_FWB,
            EpisodeType.CONFESSION,
            EpisodeType.PROPOSAL
        ]
        
        episodes = await self.get_episodes(user_id, role, instance_id, limit=100)
        milestones = [e for e in episodes if e['type'] in milestone_types]
        
        return sorted(milestones, key=lambda x: x['timestamp'])
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    async def get_stats(self, user_id: Optional[int] = None) -> Dict:
        """
        Dapatkan statistik episodic memory
        """
        if user_id:
            if user_id not in self.episodes:
                return {'total_episodes': 0, 'by_role': {}}
            
            total = 0
            by_role = {}
            
            for role, instances in self.episodes[user_id].items():
                role_total = sum(len(eps) for eps in instances.values())
                by_role[role] = role_total
                total += role_total
            
            return {
                'user_id': user_id,
                'total_episodes': total,
                'by_role': by_role
            }
        else:
            # Global stats
            total_users = len(self.episodes)
            total_episodes = sum(
                sum(len(eps) for inst in user_data.values() for eps in inst.values())
                for user_data in self.episodes.values()
            )
            
            return {
                'total_users': total_users,
                'total_episodes': total_episodes,
                'avg_per_user': total_episodes / total_users if total_users > 0 else 0
            }
    
    async def format_timeline(self, user_id: int, role: str,
                             instance_id: Optional[str] = None) -> str:
        """
        Format timeline untuk ditampilkan ke user
        """
        timeline = await self.get_timeline(user_id, role, instance_id)
        
        if not timeline:
            return f"Belum ada momen spesial dengan {role}"
        
        lines = [f"📜 **Timeline dengan {role}:**\n"]
        
        for ep in timeline[-10:]:  # 10 terakhir
            time_str = datetime.fromtimestamp(ep['timestamp']).strftime("%d %b %Y")
            emoji = self._get_episode_emoji(ep['type'])
            
            lines.append(
                f"{emoji} **{ep['type'].value.replace('_', ' ').title()}**"
            )
            lines.append(f"   {ep['description']}")
            lines.append(f"   🕒 {time_str}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _get_episode_emoji(self, episode_type: EpisodeType) -> str:
        """Dapatkan emoji untuk tipe episode"""
        emojis = {
            EpisodeType.FIRST_KISS: "💋",
            EpisodeType.FIRST_INTIM: "🔥",
            EpisodeType.FIRST_DATE: "📅",
            EpisodeType.FIRST_CLIMAX: "💦",
            EpisodeType.BECAME_PACAR: "💕",
            EpisodeType.BECAME_FWB: "💞",
            EpisodeType.BECAME_MANTAN: "💔",
            EpisodeType.CONFESSION: "💘",
            EpisodeType.PROPOSAL: "💍",
            EpisodeType.FIGHT: "⚔️",
            EpisodeType.RECONCILIATION: "🕊️",
            EpisodeType.ROMANTIC_MOMENT: "🥰",
            EpisodeType.HAPPY_MOMENT: "😊",
            EpisodeType.SAD_MOMENT: "😢"
        }
        return emojis.get(episode_type, "📌")


__all__ = ['EpisodicMemoryV2', 'EpisodeType', 'EmotionalTag']
