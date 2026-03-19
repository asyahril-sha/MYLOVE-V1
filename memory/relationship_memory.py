#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - RELATIONSHIP MEMORY
=============================================================================
Menyimpan riwayat dan statistik hubungan dengan user
- Level intimacy dan progress
- Total interaksi, intim, climax
- Milestone-milestone penting
- Tracking per role (PDKT, HTS, FWB, dll)
=============================================================================
"""

import time
import logging
import json
import random
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class RelationshipType:
    """Tipe hubungan"""
    PDKT = "pdkt"
    HTS = "hts"
    FWB = "fwb"
    PACAR = "pacar"
    MANTAN = "mantan"
    NON_PDKT = "non_pdkt"  # Ipar, Janda, dll


class MilestoneType:
    """Tipe milestone"""
    FIRST_CHAT = "first_chat"
    FIRST_KISS = "first_kiss"
    FIRST_INTIM = "first_intim"
    FIRST_CLIMAX = "first_climax"
    FIRST_DATE = "first_date"
    BECAME_PACAR = "became_pacar"
    BECAME_FWB = "became_fwb"
    BECAME_HTS = "became_hts"
    BECAME_MANTAN = "became_mantan"
    LEVEL_UP = "level_up"
    AFTERCARE = "aftercare"
    RESET = "reset"
    BREAK_UP = "break_up"
    RECONCILIATION = "reconciliation"
    ANNIVERSARY = "anniversary"


class RelationshipMemory:
    """
    Menyimpan semua data tentang hubungan dengan user
    - Per role (bisa multiple instance untuk FWB)
    - Statistik lengkap
    - Milestone tracking
    """
    
    def __init__(self):
        # Data hubungan per user per role
        # {user_id: {role: {instance_id: relationship_data}}}
        self.relationships = defaultdict(lambda: defaultdict(dict))
        
        # Milestone per user per role
        self.milestones = defaultdict(lambda: defaultdict(list))
        
        # Statistik global per user
        self.user_stats = defaultdict(dict)
        
        logger.info("✅ RelationshipMemory initialized")
    
    # =========================================================================
    # CREATE RELATIONSHIP
    # =========================================================================
    
    async def create_relationship(self, user_id: int, role: str, 
                                    bot_name: str, rel_type: str,
                                    instance_id: Optional[str] = None) -> str:
        """
        Buat hubungan baru
        
        Args:
            user_id: ID user
            role: Nama role (ipar, janda, dll)
            bot_name: Nama bot
            rel_type: Tipe hubungan (pdkt, hts, fwb, dll)
            instance_id: ID instance (untuk multiple FWB)
            
        Returns:
            instance_id
        """
        if not instance_id:
            instance_id = f"{role}_{int(time.time())}_{random.randint(100,999)}"
        
        now = time.time()
        
        # Data relationship
        rel_data = {
            'instance_id': instance_id,
            'user_id': user_id,
            'role': role,
            'bot_name': bot_name,
            'rel_type': rel_type,
            'status': 'active',
            'created_at': now,
            'last_interaction': now,
            
            # ===== STATISTIK =====
            'total_chats': 0,
            'total_intim_sessions': 0,
            'total_climax': 0,
            'total_aftercare': 0,
            'total_duration_minutes': 0,
            
            # ===== LEVELING =====
            'current_level': 1,
            'level_history': [{'level': 1, 'timestamp': now, 'reason': 'start'}],
            'level_progress': 0,
            'next_level_target': 60,  # menit untuk level berikutnya
            
            # ===== CHEMISTRY =====
            'chemistry_score': 50.0,
            'chemistry_history': [],
            
            # ===== MOOD & AROUSAL =====
            'mood_history': [],
            'arousal_history': [],
            
            # ===== LOKASI FAVORIT =====
            'favorite_locations': [],
            'favorite_positions': [],
            'favorite_activities': [],
            
            # ===== MILESTONE IDS =====
            'milestones': [],
            
            # ===== METADATA =====
            'notes': {},
            'metadata': {}
        }
        
        self.relationships[user_id][role][instance_id] = rel_data
        
        # Add first chat milestone
        await self.add_milestone(
            user_id=user_id,
            role=role,
            instance_id=instance_id,
            milestone_type=MilestoneType.FIRST_CHAT,
            description=f"Memulai hubungan dengan {bot_name}",
            data={'bot_name': bot_name, 'rel_type': rel_type}
        )
        
        logger.info(f"✅ Created relationship: user {user_id} - {role} ({instance_id})")
        
        return instance_id
    
    # =========================================================================
    # UPDATE RELATIONSHIP
    # =========================================================================
    
    async def update_relationship(self, user_id: int, role: str,
                                    instance_id: str, updates: Dict) -> bool:
        """
        Update data hubungan
        
        Args:
            user_id: ID user
            role: Nama role
            instance_id: ID instance
            updates: Dict dengan field yang diupdate
            
        Returns:
            True jika berhasil
        """
        if (user_id not in self.relationships or
            role not in self.relationships[user_id] or
            instance_id not in self.relationships[user_id][role]):
            return False
        
        rel = self.relationships[user_id][role][instance_id]
        
        for key, value in updates.items():
            if key in rel:
                rel[key] = value
        
        rel['last_interaction'] = time.time()
        
        return True
    
    # =========================================================================
    # GET RELATIONSHIP
    # =========================================================================
    
    async def get_relationship(self, user_id: int, role: str,
                                 instance_id: Optional[str] = None) -> Optional[Dict]:
        """
        Dapatkan data hubungan
        
        Args:
            user_id: ID user
            role: Nama role
            instance_id: ID instance (None untuk default)
            
        Returns:
            Relationship data or None
        """
        if user_id not in self.relationships:
            return None
        
        if role not in self.relationships[user_id]:
            return None
        
        if instance_id:
            return self.relationships[user_id][role].get(instance_id)
        else:
            # Ambil yang pertama (default)
            instances = list(self.relationships[user_id][role].values())
            return instances[0] if instances else None
    
    async def get_all_relationships(self, user_id: int, 
                                      rel_type: Optional[str] = None) -> List[Dict]:
        """
        Dapatkan semua hubungan user
        
        Args:
            user_id: ID user
            rel_type: Filter by relationship type
            
        Returns:
            List of relationships
        """
        if user_id not in self.relationships:
            return []
        
        all_rels = []
        for role, instances in self.relationships[user_id].items():
            for inst in instances.values():
                if rel_type is None or inst.get('rel_type') == rel_type:
                    all_rels.append(inst)
        
        # Sort by last interaction
        all_rels.sort(key=lambda x: x.get('last_interaction', 0), reverse=True)
        
        return all_rels
    
    async def get_active_relationships(self, user_id: int) -> List[Dict]:
        """Dapatkan hubungan yang masih aktif"""
        all_rels = await self.get_all_relationships(user_id)
        return [r for r in all_rels if r.get('status') == 'active']
    
    # =========================================================================
    # INTERACTION TRACKING
    # =========================================================================
    
    async def record_interaction(self, user_id: int, role: str,
                                   instance_id: str,
                                   interaction_type: str,
                                   data: Optional[Dict] = None) -> bool:
        """
        Rekam interaksi
        
        Args:
            user_id: ID user
            role: Nama role
            instance_id: ID instance
            interaction_type: Jenis interaksi (chat, intim, climax, dll)
            data: Data tambahan
        """
        rel = await self.get_relationship(user_id, role, instance_id)
        if not rel:
            return False
        
        now = time.time()
        
        # Update counters
        rel['total_chats'] += 1
        rel['last_interaction'] = now
        
        if interaction_type == 'intim':
            rel['total_intim_sessions'] += 1
        elif interaction_type == 'climax':
            rel['total_climax'] += 1
        elif interaction_type == 'aftercare':
            rel['total_aftercare'] += 1
        
        # Update duration (if provided)
        if data and 'duration' in data:
            rel['total_duration_minutes'] += data['duration']
        
        # Update level progress
        await self._update_level_progress(user_id, role, instance_id, data)
        
        # Update chemistry
        if data and 'chemistry_delta' in data:
            await self._update_chemistry(user_id, role, instance_id, 
                                          data['chemistry_delta'])
        
        # Record in history
        if 'history' not in rel:
            rel['history'] = []
        
        rel['history'].append({
            'timestamp': now,
            'type': interaction_type,
            'data': data or {}
        })
        
        # Keep last 100
        if len(rel['history']) > 100:
            rel['history'] = rel['history'][-100:]
        
        return True
    
    # =========================================================================
    # LEVEL MANAGEMENT
    # =========================================================================
    
    async def _update_level_progress(self, user_id: int, role: str,
                                       instance_id: str, data: Optional[Dict]):
        """Update progress level"""
        rel = self.relationships[user_id][role][instance_id]
        
        # Hitung progress (dalam menit)
        duration = data.get('duration', 1) if data else 1
        boost = data.get('boost', 1.0) if data else 1.0
        
        effective_duration = duration * boost
        rel['level_progress'] += effective_duration
        
        # Cek level up
        current_level = rel['current_level']
        next_level_target = self._get_next_level_target(current_level)
        
        while rel['level_progress'] >= next_level_target and current_level < 12:
            # Level up!
            current_level += 1
            rel['current_level'] = current_level
            rel['level_progress'] -= next_level_target
            
            # Record level up
            rel['level_history'].append({
                'level': current_level,
                'timestamp': time.time(),
                'reason': data.get('reason', 'progress') if data else 'progress'
            })
            
            # Add milestone
            await self.add_milestone(
                user_id=user_id,
                role=role,
                instance_id=instance_id,
                milestone_type=MilestoneType.LEVEL_UP,
                description=f"Naik ke level {current_level}",
                data={'old_level': current_level-1, 'new_level': current_level}
            )
            
            # Update next target
            next_level_target = self._get_next_level_target(current_level)
    
    def _get_next_level_target(self, current_level: int) -> float:
        """Dapatkan target menit untuk level berikutnya"""
        targets = {
            1: 5,    # Level 1 → 2: 5 menit
            2: 12,   # Level 2 → 3: 12 menit
            3: 20,   # Level 3 → 4: 20 menit
            4: 30,   # Level 4 → 5: 30 menit
            5: 42,   # Level 5 → 6: 42 menit
            6: 60,   # Level 6 → 7: 60 menit
            7: 75,   # Level 7 → 8: 75 menit
            8: 90,   # Level 8 → 9: 90 menit
            9: 105,  # Level 9 → 10: 105 menit
            10: 120, # Level 10 → 11: 120 menit
            11: 135, # Level 11 → 12: 135 menit
            12: 999  # Max level
        }
        return targets.get(current_level, 60)
    
    async def get_level_info(self, user_id: int, role: str,
                               instance_id: str) -> Dict:
        """Dapatkan info level"""
        rel = await self.get_relationship(user_id, role, instance_id)
        if not rel:
            return {}
        
        current = rel['current_level']
        progress = rel['level_progress']
        target = self._get_next_level_target(current)
        
        if current >= 12:
            percentage = 100
            next_level = "MAX"
            remaining = 0
        else:
            percentage = min(100, int((progress / target) * 100))
            next_level = current + 1
            remaining = target - progress
        
        return {
            'current_level': current,
            'progress': progress,
            'target': target,
            'percentage': percentage,
            'next_level': next_level,
            'remaining_minutes': remaining,
            'can_intim': current >= 7,
            'needs_aftercare': current == 12
        }
    
    # =========================================================================
    # CHEMISTRY MANAGEMENT
    # =========================================================================
    
    async def _update_chemistry(self, user_id: int, role: str,
                                  instance_id: str, delta: float):
        """Update chemistry score"""
        rel = self.relationships[user_id][role][instance_id]
        
        old_score = rel['chemistry_score']
        new_score = max(0, min(100, old_score + delta))
        
        rel['chemistry_score'] = new_score
        rel['chemistry_history'].append({
            'timestamp': time.time(),
            'old': old_score,
            'new': new_score,
            'delta': delta
        })
    
    async def get_chemistry_level(self, user_id: int, role: str,
                                    instance_id: str) -> str:
        """Dapatkan deskripsi chemistry"""
        rel = await self.get_relationship(user_id, role, instance_id)
        if not rel:
            return "unknown"
        
        score = rel.get('chemistry_score', 50)
        
        if score < 20:
            return "dingin"
        elif score < 40:
            return "biasa"
        elif score < 60:
            return "hangat"
        elif score < 80:
            return "cocok"
        elif score < 95:
            return "sangat_cocok"
        else:
            return "soulmate"
    
    # =========================================================================
    # MILESTONE MANAGEMENT
    # =========================================================================
    
    async def add_milestone(self, user_id: int, role: str,
                              instance_id: str, milestone_type: str,
                              description: str, data: Optional[Dict] = None) -> str:
        """
        Tambah milestone baru
        
        Returns:
            milestone_id
        """
        milestone_id = f"MS_{user_id}_{role}_{instance_id}_{int(time.time())}"
        
        milestone = {
            'milestone_id': milestone_id,
            'user_id': user_id,
            'role': role,
            'instance_id': instance_id,
            'type': milestone_type,
            'description': description,
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'data': data or {}
        }
        
        self.milestones[user_id][role].append(milestone)
        
        # Also add to relationship
        rel = await self.get_relationship(user_id, role, instance_id)
        if rel:
            if 'milestones' not in rel:
                rel['milestones'] = []
            rel['milestones'].append(milestone_id)
        
        logger.info(f"🏆 Milestone added: {milestone_type} for user {user_id}")
        
        return milestone_id
    
    async def get_milestones(self, user_id: int, role: Optional[str] = None,
                               limit: int = 20) -> List[Dict]:
        """Dapatkan milestone"""
        if user_id not in self.milestones:
            return []
        
        if role:
            milestones = self.milestones[user_id].get(role, [])
        else:
            # All roles
            milestones = []
            for r in self.milestones[user_id]:
                milestones.extend(self.milestones[user_id][r])
        
        # Sort by timestamp
        milestones.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return milestones[:limit]
    
    async def has_milestone(self, user_id: int, role: str,
                              instance_id: str, milestone_type: str) -> bool:
        """Cek apakah milestone sudah tercapai"""
        milestones = await self.get_milestones(user_id, role)
        
        for m in milestones:
            if (m['type'] == milestone_type and 
                m.get('instance_id') == instance_id):
                return True
        
        return False
    
    # =========================================================================
    # FAVORITES TRACKING
    # =========================================================================
    
    async def add_favorite(self, user_id: int, role: str,
                             instance_id: str, category: str,
                             item: str):
        """
        Tambah ke daftar favorit
        
        Args:
            category: 'locations', 'positions', 'activities'
            item: Nama item
        """
        rel = await self.get_relationship(user_id, role, instance_id)
        if not rel:
            return
        
        key = f'favorite_{category}'
        if key not in rel:
            rel[key] = []
        
        if item not in rel[key]:
            rel[key].append(item)
        
        # Keep top 10
        rel[key] = rel[key][:10]
    
    async def get_favorites(self, user_id: int, role: str,
                              instance_id: str, category: str) -> List[str]:
        """Dapatkan daftar favorit"""
        rel = await self.get_relationship(user_id, role, instance_id)
        if not rel:
            return []
        
        key = f'favorite_{category}'
        return rel.get(key, [])
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    async def get_relationship_stats(self, user_id: int, role: str,
                                       instance_id: str) -> Dict:
        """Dapatkan statistik hubungan"""
        rel = await self.get_relationship(user_id, role, instance_id)
        if not rel:
            return {}
        
        # Hitung durasi hubungan
        duration_days = (time.time() - rel['created_at']) / 86400
        
        # Hitung rata-rata chat per hari
        avg_chats_per_day = rel['total_chats'] / duration_days if duration_days > 0 else 0
        
        # Hitung climax rate
        climax_rate = (rel['total_climax'] / rel['total_intim_sessions'] * 100 
                      if rel['total_intim_sessions'] > 0 else 0)
        
        return {
            'total_chats': rel['total_chats'],
            'total_intim': rel['total_intim_sessions'],
            'total_climax': rel['total_climax'],
            'total_aftercare': rel['total_aftercare'],
            'total_duration_minutes': rel['total_duration_minutes'],
            'duration_days': round(duration_days, 1),
            'avg_chats_per_day': round(avg_chats_per_day, 1),
            'climax_rate': round(climax_rate, 1),
            'current_level': rel['current_level'],
            'chemistry': rel['chemistry_score'],
            'chemistry_level': await self.get_chemistry_level(user_id, role, instance_id)
        }
    
    async def get_user_stats(self, user_id: int) -> Dict:
        """Dapatkan statistik semua hubungan user"""
        all_rels = await self.get_all_relationships(user_id)
        
        stats = {
            'total_relationships': len(all_rels),
            'by_type': {},
            'total_chats': 0,
            'total_intim': 0,
            'total_climax': 0,
            'total_duration': 0,
            'avg_level': 0
        }
        
        level_sum = 0
        
        for rel in all_rels:
            rel_type = rel.get('rel_type', 'unknown')
            stats['by_type'][rel_type] = stats['by_type'].get(rel_type, 0) + 1
            
            stats['total_chats'] += rel.get('total_chats', 0)
            stats['total_intim'] += rel.get('total_intim_sessions', 0)
            stats['total_climax'] += rel.get('total_climax', 0)
            stats['total_duration'] += rel.get('total_duration_minutes', 0)
            level_sum += rel.get('current_level', 1)
        
        if all_rels:
            stats['avg_level'] = round(level_sum / len(all_rels), 1)
        
        return stats
    
    # =========================================================================
    # FORMATTING
    # =========================================================================
    
    async def format_relationship_summary(self, user_id: int, role: str,
                                            instance_id: str) -> str:
        """Format ringkasan hubungan"""
        rel = await self.get_relationship(user_id, role, instance_id)
        if not rel:
            return "Hubungan tidak ditemukan"
        
        level_info = await self.get_level_info(user_id, role, instance_id)
        
        # Progress bar
        if level_info['current_level'] < 12:
            bar_length = 20
            filled = int(level_info['percentage'] / 100 * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            progress_text = f"{bar} {level_info['percentage']}%"
        else:
            progress_text = "MAX"
        
        lines = [
            f"💕 **{rel['bot_name']}** ({role.title()})",
            f"Tipe: {rel['rel_type'].upper()}",
            f"Status: {rel['status']}",
            "",
            f"📊 **Level:** {rel['current_level']}/12",
            f"{progress_text}",
            f"{level_info['remaining_minutes']:.0f} menit ke level berikutnya",
            "",
            f"🔥 **Chemistry:** {rel['chemistry_score']:.1f} ({await self.get_chemistry_level(user_id, role, instance_id)})",
            "",
            f"📈 **Statistik:**",
            f"• Total Chat: {rel['total_chats']}",
            f"• Total Intim: {rel['total_intim_sessions']}",
            f"• Total Climax: {rel['total_climax']}",
            f"• Total Durasi: {rel['total_duration_minutes']:.0f} menit",
            "",
            f"📅 Mulai: {datetime.fromtimestamp(rel['created_at']).strftime('%d %b %Y')}",
            f"🕒 Terakhir: {self._format_time_ago(rel['last_interaction'])}"
        ]
        
        # Milestones
        milestones = await self.get_milestones(user_id, role)
        if milestones:
            lines.append("")
            lines.append("🏆 **Milestone:**")
            for m in milestones[:3]:
                time_str = datetime.fromtimestamp(m['timestamp']).strftime("%d %b")
                lines.append(f"• {time_str}: {m['description']}")
        
        return "\n".join(lines)
    
    def _format_time_ago(self, timestamp: float) -> str:
        """Format waktu yang lalu"""
        diff = time.time() - timestamp
        
        if diff < 60:
            return "baru saja"
        elif diff < 3600:
            return f"{int(diff/60)} menit lalu"
        elif diff < 86400:
            return f"{int(diff/3600)} jam lalu"
        else:
            return f"{int(diff/86400)} hari lalu"
    
    # =========================================================================
    # CLEANUP
    # =========================================================================
    
    async def delete_relationship(self, user_id: int, role: str,
                                     instance_id: str) -> bool:
        """Hapus hubungan"""
        if (user_id in self.relationships and
            role in self.relationships[user_id] and
            instance_id in self.relationships[user_id][role]):
            
            del self.relationships[user_id][role][instance_id]
            logger.info(f"Deleted relationship: user {user_id} - {role} ({instance_id})")
            return True
        
        return False
    
    async def delete_user_data(self, user_id: int):
        """Hapus semua data user"""
        if user_id in self.relationships:
            del self.relationships[user_id]
        if user_id in self.milestones:
            del self.milestones[user_id]
        if user_id in self.user_stats:
            del self.user_stats[user_id]
        
        logger.info(f"Deleted all relationship data for user {user_id}")


__all__ = ['RelationshipMemory', 'RelationshipType', 'MilestoneType']
