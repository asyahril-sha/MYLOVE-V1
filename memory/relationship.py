#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - RELATIONSHIP MEMORY
=============================================================================
Tracking hubungan spesifik per role
- Timeline hubungan
- Status (HTS/FWB/Pacar)
- Intimacy level tracking
- Milestones
"""

import time
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import logging
import random

logger = logging.getLogger(__name__)


class RelationshipMemory:
    """
    Menyimpan data hubungan per role
    Terintegrasi dengan intimacy system
    """
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.relationships = {}  # {user_id: {role: relationship_data}}
        self.timelines = {}  # {user_id: {role: [events]}}
        self.loaded = False
        
    async def initialize(self):
        """Load relationship data"""
        try:
            rel_path = self.db_path.parent / "relationships.json"
            time_path = self.db_path.parent / "timelines.json"
            
            if rel_path.exists():
                with open(rel_path, 'r') as f:
                    self.relationships = json.load(f)
                    
            if time_path.exists():
                with open(time_path, 'r') as f:
                    self.timelines = json.load(f)
                    
            logger.info(f"📚 Loaded relationships: {len(self.relationships)} users")
            self.loaded = True
            
        except Exception as e:
            logger.error(f"Error loading relationships: {e}")
            self.relationships = {}
            self.timelines = {}
            self.loaded = True
            
    async def save(self):
        """Save relationship data"""
        if not self.loaded:
            return
            
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.db_path.parent / "relationships.json", 'w') as f:
                json.dump(self.relationships, f, indent=2)
                
            with open(self.db_path.parent / "timelines.json", 'w') as f:
                json.dump(self.timelines, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving relationships: {e}")
            
    # =========================================================================
    # RELATIONSHIP MANAGEMENT
    # =========================================================================
    
    async def create_relationship(self, user_id: int, role: str, 
                                    initial_status: str = 'hts'):
        """Create new relationship"""
        user_key = str(user_id)
        
        if user_key not in self.relationships:
            self.relationships[user_key] = {}
            
        self.relationships[user_key][role] = {
            'status': initial_status,
            'created_at': time.time(),
            'last_interaction': time.time(),
            'total_interactions': 0,
            'intimacy_level': 1,
            'intimacy_history': [
                {'level': 1, 'timestamp': time.time(), 'event': 'start'}
            ],
            'favorite_positions': [],
            'favorite_areas': [],
            'milestones': [],
            'total_climax': 0,
            'total_intim_sessions': 0,
            'aftercare_count': 0,
            'reset_count': 0
        }
        
        # Create timeline
        if user_key not in self.timelines:
            self.timelines[user_key] = {}
            
        self.timelines[user_key][role] = []
        
        # Add first event
        await self.add_timeline_event(user_id, role, 'relationship_started', {
            'status': initial_status,
            'intimacy_level': 1
        })
        
        await self.save()
        logger.info(f"Created {initial_status} relationship for user {user_id} role {role}")
        
        return self.relationships[user_key][role]
        
    async def get_relationship(self, user_id: int, role: str) -> Optional[Dict]:
        """Get relationship data"""
        user_key = str(user_id)
        
        if user_key in self.relationships and role in self.relationships[user_key]:
            return self.relationships[user_key][role]
            
        return None
        
    async def update_relationship(self, user_id: int, role: str, updates: Dict):
        """Update relationship data"""
        user_key = str(user_id)
        
        if user_key not in self.relationships:
            self.relationships[user_key] = {}
            
        if role not in self.relationships[user_key]:
            await self.create_relationship(user_id, role)
            
        for key, value in updates.items():
            self.relationships[user_key][role][key] = value
            
        self.relationships[user_key][role]['last_interaction'] = time.time()
        
        if 'intimacy_level' in updates:
            # Add to history
            if 'intimacy_history' not in self.relationships[user_key][role]:
                self.relationships[user_key][role]['intimacy_history'] = []
                
            self.relationships[user_key][role]['intimacy_history'].append({
                'level': updates['intimacy_level'],
                'timestamp': time.time(),
                'event': 'level_change'
            })
            
        await self.save()
        
    async def increment_interaction(self, user_id: int, role: str):
        """Increment interaction count"""
        rel = await self.get_relationship(user_id, role)
        if rel:
            rel['total_interactions'] += 1
            rel['last_interaction'] = time.time()
            await self.save()
            
    # =========================================================================
    # INTIMACY LEVEL MANAGEMENT
    # =========================================================================
    
    async def set_intimacy_level(self, user_id: int, role: str, level: int):
        """Set intimacy level"""
        await self.update_relationship(user_id, role, {'intimacy_level': level})
        
        # Add timeline event
        await self.add_timeline_event(user_id, role, 'intimacy_level_changed', {
            'new_level': level
        })
        
    async def get_intimacy_level(self, user_id: int, role: str) -> int:
        """Get current intimacy level"""
        rel = await self.get_relationship(user_id, role)
        return rel.get('intimacy_level', 1) if rel else 1
        
    async def increase_intimacy(self, user_id: int, role: str, amount: int = 1) -> int:
        """Increase intimacy level"""
        current = await self.get_intimacy_level(user_id, role)
        new_level = min(12, current + amount)
        
        await self.set_intimacy_level(user_id, role, new_level)
        
        # Check for milestone
        if new_level == 6 and role == 'pdkt':
            await self.add_milestone(user_id, role, 'became_pacar')
        elif new_level == 7:
            await self.add_milestone(user_id, role, 'can_intim')
        elif new_level == 12:
            await self.add_milestone(user_id, role, 'reached_aftercare')
            
        return new_level
        
    async def reset_intimacy(self, user_id: int, role: str, reset_to: int = 7):
        """Reset intimacy level (after aftercare)"""
        current = await self.get_intimacy_level(user_id, role)
        
        await self.set_intimacy_level(user_id, role, reset_to)
        
        # Update reset count
        rel = await self.get_relationship(user_id, role)
        if rel:
            rel['reset_count'] = rel.get('reset_count', 0) + 1
            await self.save()
            
        # Add timeline event
        await self.add_timeline_event(user_id, role, 'intimacy_reset', {
            'from_level': current,
            'to_level': reset_to,
            'reset_count': rel.get('reset_count', 0)
        })
        
        logger.info(f"Intimacy reset for user {user_id} role {role}: {current} -> {reset_to}")
        
        return reset_to
        
    # =========================================================================
    # STATUS MANAGEMENT (HTS/FWB/PACAR)
    # =========================================================================
    
    async def set_status(self, user_id: int, role: str, status: str):
        """Set relationship status"""
        valid_statuses = ['hts', 'fwb', 'pacar']
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
            
        rel = await self.get_relationship(user_id, role)
        old_status = rel.get('status') if rel else None
        
        await self.update_relationship(user_id, role, {'status': status})
        
        # Add timeline event
        await self.add_timeline_event(user_id, role, 'status_changed', {
            'old_status': old_status,
            'new_status': status
        })
        
        # Add milestone
        await self.add_milestone(user_id, role, f'became_{status}')
        
        logger.info(f"Status changed for user {user_id} role {role}: {old_status} -> {status}")
        
    async def get_status(self, user_id: int, role: str) -> str:
        """Get relationship status"""
        rel = await self.get_relationship(user_id, role)
        return rel.get('status', 'hts') if rel else 'hts'
        
    # =========================================================================
    # TIMELINE MANAGEMENT
    # =========================================================================
    
    async def add_timeline_event(self, user_id: int, role: str, 
                                   event_type: str, data: Dict = None):
        """Add event to timeline"""
        user_key = str(user_id)
        
        if user_key not in self.timelines:
            self.timelines[user_key] = {}
            
        if role not in self.timelines[user_key]:
            self.timelines[user_key][role] = []
            
        event = {
            'type': event_type,
            'timestamp': time.time(),
            'datetime': datetime.now().isoformat(),
            'data': data or {}
        }
        
        self.timelines[user_key][role].append(event)
        
        # Keep last 100 events
        if len(self.timelines[user_key][role]) > 100:
            self.timelines[user_key][role] = self.timelines[user_key][role][-100:]
            
        await self.save()
        
    async def get_timeline(self, user_id: int, role: str, 
                            limit: int = 50) -> List[Dict]:
        """Get timeline for role"""
        user_key = str(user_id)
        
        if (user_key in self.timelines and 
            role in self.timelines[user_key]):
            return self.timelines[user_key][role][-limit:]
            
        return []
        
    async def add_milestone(self, user_id: int, role: str, milestone: str):
        """Add milestone to relationship"""
        rel = await self.get_relationship(user_id, role)
        if rel:
            if 'milestones' not in rel:
                rel['milestones'] = []
                
            milestone_data = {
                'type': milestone,
                'timestamp': time.time(),
                'intimacy_level': rel.get('intimacy_level', 1)
            }
            
            rel['milestones'].append(milestone_data)
            
            # Also add to timeline
            await self.add_timeline_event(user_id, role, 'milestone', milestone_data)
            
            await self.save()
            
    async def get_milestones(self, user_id: int, role: str) -> List[Dict]:
        """Get all milestones for role"""
        rel = await self.get_relationship(user_id, role)
        return rel.get('milestones', []) if rel else []
        
    # =========================================================================
    # PREFERENCES TRACKING
    # =========================================================================
    
    async def add_favorite_position(self, user_id: int, role: str, position: str):
        """Add to favorite positions"""
        rel = await self.get_relationship(user_id, role)
        if rel:
            if 'favorite_positions' not in rel:
                rel['favorite_positions'] = []
                
            if position not in rel['favorite_positions']:
                rel['favorite_positions'].append(position)
                
            # Keep top 5
            rel['favorite_positions'] = rel['favorite_positions'][:5]
            
            await self.save()
            
    async def add_favorite_area(self, user_id: int, role: str, area: str):
        """Add to favorite areas"""
        rel = await self.get_relationship(user_id, role)
        if rel:
            if 'favorite_areas' not in rel:
                rel['favorite_areas'] = []
                
            if area not in rel['favorite_areas']:
                rel['favorite_areas'].append(area)
                
            rel['favorite_areas'] = rel['favorite_areas'][:5]
            
            await self.save()
            
    # =========================================================================
    # INTIMACY SESSIONS TRACKING
    # =========================================================================
    
    async def record_intim_session(self, user_id: int, role: str, 
                                     climax: bool = False):
        """Record intimacy session"""
        rel = await self.get_relationship(user_id, role)
        if rel:
            rel['total_intim_sessions'] = rel.get('total_intim_sessions', 0) + 1
            
            if climax:
                rel['total_climax'] = rel.get('total_climax', 0) + 1
                
            await self.save()
            
    async def record_aftercare(self, user_id: int, role: str, aftercare_type: str):
        """Record aftercare session"""
        rel = await self.get_relationship(user_id, role)
        if rel:
            rel['aftercare_count'] = rel.get('aftercare_count', 0) + 1
            
            await self.add_timeline_event(user_id, role, 'aftercare', {
                'type': aftercare_type,
                'count': rel['aftercare_count']
            })
            
            await self.save()
            
    # =========================================================================
    # QUERY & UTILITY
    # =========================================================================
    
    async def get_all_roles(self, user_id: int) -> List[str]:
        """Get all roles for user"""
        user_key = str(user_id)
        
        if user_key in self.relationships:
            return list(self.relationships[user_key].keys())
            
        return []
        
    async def get_relationship_summary(self, user_id: int, role: str) -> str:
        """Get human-readable relationship summary"""
        rel = await self.get_relationship(user_id, role)
        if not rel:
            return f"Belum ada hubungan dengan role {role}"
            
        status_map = {
            'hts': 'Hubungan Tanpa Status',
            'fwb': 'Friends With Benefits',
            'pacar': 'Pacar'
        }
        
        status = status_map.get(rel.get('status', 'hts'), 'HTS')
        intimacy = rel.get('intimacy_level', 1)
        
        # Durasi hubungan
        duration = time.time() - rel.get('created_at', time.time())
        days = int(duration / 86400)
        
        summary = [
            f"📊 **Hubungan dengan role {role}**",
            f"Status: {status}",
            f"Intimacy Level: {intimacy}/12",
            f"Durasi: {days} hari",
            f"Total Interaksi: {rel.get('total_interactions', 0)}",
            f"Total Intim: {rel.get('total_intim_sessions', 0)}",
            f"Total Climax: {rel.get('total_climax', 0)}"
        ]
        
        if rel.get('favorite_positions'):
            summary.append(f"Posisi Favorit: {', '.join(rel['favorite_positions'])}")
            
        if rel.get('milestones'):
            recent = rel['milestones'][-3:]
            milestone_names = [m['type'] for m in recent]
            summary.append(f"Milestone: {', '.join(milestone_names)}")
            
        return "\n".join(summary)
        
    async def get_ranking_data(self, user_id: int) -> List[Dict]:
        """Get data for ranking system"""
        user_key = str(user_id)
        
        if user_key not in self.relationships:
            return []
            
        rankings = []
        for role, data in self.relationships[user_key].items():
            # Calculate score
            score = (
                data.get('total_interactions', 0) * 0.3 +
                data.get('intimacy_level', 1) * 0.4 +
                min(100, (time.time() - data.get('created_at', time.time())) / 86400) * 0.2 +
                data.get('total_climax', 0) * 0.1
            )
            
            rankings.append({
                'role': role,
                'status': data.get('status', 'hts'),
                'intimacy_level': data.get('intimacy_level', 1),
                'total_interactions': data.get('total_interactions', 0),
                'total_climax': data.get('total_climax', 0),
                'score': score,
                'last_interaction': data.get('last_interaction', 0)
            })
            
        # Sort by score
        rankings.sort(key=lambda x: x['score'], reverse=True)
        
        return rankings
        
    async def delete_user_data(self, user_id: int):
        """Delete all data for user"""
        user_key = str(user_id)
        
        if user_key in self.relationships:
            del self.relationships[user_key]
        if user_key in self.timelines:
            del self.timelines[user_key]
            
        await self.save()
        logger.info(f"Deleted all relationship data for user {user_id}")


__all__ = ['RelationshipMemory']
