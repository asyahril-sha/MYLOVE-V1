#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - DATABASE REPOSITORY (FIX FULL + PDKT)
=============================================================================
- CRUD operations untuk semua models
- Query methods untuk akses data
- Transaction management
- **PDKT Repository methods**
=============================================================================
"""

import time
import json
import logging
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta

from .connection import get_db
from .models import (
    User, Session, Conversation, Memory, Relationship,
    Preference, Milestone, Backup, RelationshipStatus,
    MemoryType, MilestoneType, BackupType, BackupStatus,
    PDKT, PDKTStatus, PDKTDirection, PDKTStage
)

logger = logging.getLogger(__name__)


class Repository:
    """
    Repository untuk semua operasi database
    Menyediakan method CRUD untuk setiap model
    """
    
    def __init__(self):
        self.db = None
        
    async def _get_db(self):
        """Get database connection"""
        if not self.db:
            self.db = await get_db()
        return self.db
        
    # =========================================================================
    # USER REPOSITORY
    # =========================================================================
    
    async def get_user(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        db = await self._get_db()
        result = await db.fetch_one(
            "SELECT * FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        return User.from_dict(result) if result else None
        
    async def create_user(self, user: User) -> int:
        """Create new user"""
        db = await self._get_db()
        await db.execute(
            """
            INSERT INTO users 
            (telegram_id, username, first_name, last_name, created_at, last_active, 
             total_interactions, preferences, settings)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user.telegram_id, user.username, user.first_name, user.last_name,
                user.created_at, user.last_active, user.total_interactions,
                json.dumps(user.preferences), json.dumps(user.settings)
            )
        )
        logger.info(f"✅ Created user: {user.telegram_id}")
        return user.telegram_id
        
    async def update_user(self, user: User):
        """Update existing user"""
        db = await self._get_db()
        await db.execute(
            """
            UPDATE users SET
                username = ?, first_name = ?, last_name = ?,
                last_active = ?, total_interactions = ?,
                preferences = ?, settings = ?
            WHERE telegram_id = ?
            """,
            (
                user.username, user.first_name, user.last_name,
                user.last_active, user.total_interactions,
                json.dumps(user.preferences), json.dumps(user.settings),
                user.telegram_id
            )
        )
        logger.debug(f"Updated user: {user.telegram_id}")
        
    async def update_user_last_active(self, telegram_id: int):
        """Update user last active timestamp"""
        db = await self._get_db()
        await db.execute(
            "UPDATE users SET last_active = ? WHERE telegram_id = ?",
            (time.time(), telegram_id)
        )
        
    async def increment_user_interactions(self, telegram_id: int):
        """Increment user total interactions"""
        db = await self._get_db()
        await db.execute(
            """
            UPDATE users 
            SET total_interactions = total_interactions + 1,
                last_active = ?
            WHERE telegram_id = ?
            """,
            (time.time(), telegram_id)
        )
        
    # =========================================================================
    # SESSION REPOSITORY
    # =========================================================================
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        db = await self._get_db()
        result = await db.fetch_one(
            "SELECT * FROM sessions WHERE id = ?",
            (session_id,)
        )
        return Session.from_dict(result) if result else None
        
    async def get_active_session(self, user_id: int, role: Optional[str] = None) -> Optional[Session]:
        """Get active session for user"""
        db = await self._get_db()
        query = "SELECT * FROM sessions WHERE user_id = ? AND status = 'active'"
        params = [user_id]
        
        if role:
            query += " AND role = ?"
            params.append(role)
            
        query += " ORDER BY last_message_time DESC LIMIT 1"
        
        result = await db.fetch_one(query, params)
        return Session.from_dict(result) if result else None
        
    async def get_user_sessions(self, user_id: int, limit: int = 10, include_closed: bool = True) -> List[Session]:
        """Get all sessions for user"""
        db = await self._get_db()
        if include_closed:
            query = "SELECT * FROM sessions WHERE user_id = ? ORDER BY last_message_time DESC LIMIT ?"
        else:
            query = "SELECT * FROM sessions WHERE user_id = ? AND status = 'active' ORDER BY last_message_time DESC LIMIT ?"
            
        results = await db.fetch_all(query, (user_id, limit))
        return [Session.from_dict(r) for r in results]
        
    async def create_session(self, session: Session) -> str:
        """Create new session"""
        db = await self._get_db()
        await db.execute(
            """
            INSERT INTO sessions 
            (id, user_id, bot_name, role, status, start_time, last_message_time, 
             total_messages, intimacy_level, location, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session.id, session.user_id, session.bot_name, session.role, session.status.value,
                session.start_time, session.last_message_time,
                session.total_messages, session.intimacy_level,
                session.location, json.dumps(session.metadata)
            )
        )
        logger.info(f"✅ Created session: {session.id}")
        return session.id
        
    async def update_session(self, session: Session):
        """Update existing session"""
        db = await self._get_db()
        await db.execute(
            """
            UPDATE sessions SET
                status = ?, last_message_time = ?, total_messages = ?,
                intimacy_level = ?, location = ?, summary = ?, metadata = ?
            WHERE id = ?
            """,
            (
                session.status.value, session.last_message_time, session.total_messages,
                session.intimacy_level, session.location, session.summary,
                json.dumps(session.metadata), session.id
            )
        )
        
    async def close_session(self, session_id: str, summary: Optional[str] = None):
        """Close session"""
        db = await self._get_db()
        await db.execute(
            """
            UPDATE sessions 
            SET status = 'closed', end_time = ?, summary = ?
            WHERE id = ?
            """,
            (time.time(), summary, session_id)
        )
        logger.info(f"📁 Closed session: {session_id}")
        
    async def delete_session(self, session_id: str):
        """Delete session (cascade will delete conversations)"""
        db = await self._get_db()
        await db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        logger.info(f"🗑️ Deleted session: {session_id}")
        
    # =========================================================================
    # CONVERSATION REPOSITORY
    # =========================================================================
    
    async def add_message(self, conversation: Conversation) -> int:
        """Add message to conversation"""
        db = await self._get_db()
        cursor = await db.execute(
            """
            INSERT INTO conversations 
            (session_id, timestamp, user_message, bot_response, intent, mood)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                conversation.session_id, conversation.timestamp,
                conversation.user_message, conversation.bot_response,
                conversation.intent, conversation.mood
            )
        )
        return cursor.lastrowid
        
    async def get_session_conversations(self, session_id: str, limit: int = 50) -> List[Conversation]:
        """Get conversations for session"""
        db = await self._get_db()
        results = await db.fetch_all(
            "SELECT * FROM conversations WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
            (session_id, limit)
        )
        return [Conversation.from_dict(r) for r in results]
        
    async def get_recent_conversations(self, user_id: int, limit: int = 10) -> List[Conversation]:
        """Get recent conversations for user"""
        db = await self._get_db()
        results = await db.fetch_all(
            """
            SELECT c.* FROM conversations c
            JOIN sessions s ON c.session_id = s.id
            WHERE s.user_id = ?
            ORDER BY c.timestamp DESC LIMIT ?
            """,
            (user_id, limit)
        )
        return [Conversation.from_dict(r) for r in results]
        
    # =========================================================================
    # MEMORY REPOSITORY
    # =========================================================================
    
    async def add_memory(self, memory: Memory) -> int:
        """Add memory"""
        db = await self._get_db()
        cursor = await db.execute(
            """
            INSERT INTO memories 
            (user_id, role, memory_type, content, importance, emotional_tag, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                memory.user_id, memory.role, memory.memory_type.value,
                memory.content, memory.importance, memory.emotional_tag,
                memory.timestamp, json.dumps(memory.metadata)
            )
        )
        return cursor.lastrowid
        
    async def get_user_memories(self, user_id: int, memory_type: Optional[MemoryType] = None, 
                                limit: int = 50) -> List[Memory]:
        """Get memories for user"""
        db = await self._get_db()
        if memory_type:
            results = await db.fetch_all(
                "SELECT * FROM memories WHERE user_id = ? AND memory_type = ? ORDER BY importance DESC LIMIT ?",
                (user_id, memory_type.value, limit)
            )
        else:
            results = await db.fetch_all(
                "SELECT * FROM memories WHERE user_id = ? ORDER BY importance DESC LIMIT ?",
                (user_id, limit)
            )
        return [Memory.from_dict(r) for r in results]
        
    async def get_role_memories(self, user_id: int, role: str, limit: int = 20) -> List[Memory]:
        """Get memories for specific role"""
        db = await self._get_db()
        results = await db.fetch_all(
            "SELECT * FROM memories WHERE user_id = ? AND role = ? ORDER BY importance DESC LIMIT ?",
            (user_id, role, limit)
        )
        return [Memory.from_dict(r) for r in results]
        
    async def delete_old_memories(self, user_id: int, threshold: float = 0.3, days: int = 30):
        """Delete memories with low importance and older than days"""
        db = await self._get_db()
        cutoff = time.time() - (days * 86400)
        await db.execute(
            "DELETE FROM memories WHERE user_id = ? AND importance < ? AND timestamp < ?",
            (user_id, threshold, cutoff)
        )
        
    # =========================================================================
    # RELATIONSHIP REPOSITORY (HTS/FWB)
    # =========================================================================
    
    async def get_relationship(self, user_id: int, role: str, instance_id: Optional[str] = None) -> Optional[Relationship]:
        """Get relationship"""
        db = await self._get_db()
        if instance_id:
            result = await db.fetch_one(
                "SELECT * FROM relationships WHERE user_id = ? AND role = ? AND instance_id = ?",
                (user_id, role, instance_id)
            )
        else:
            result = await db.fetch_one(
                "SELECT * FROM relationships WHERE user_id = ? AND role = ? AND instance_id IS NULL",
                (user_id, role)
            )
        return Relationship.from_dict(result) if result else None
        
    async def get_all_relationships(self, user_id: int, status: Optional[RelationshipStatus] = None) -> List[Relationship]:
        """Get all relationships for user"""
        db = await self._get_db()
        if status:
            results = await db.fetch_all(
                "SELECT * FROM relationships WHERE user_id = ? AND status = ? ORDER BY last_interaction DESC",
                (user_id, status.value)
            )
        else:
            results = await db.fetch_all(
                "SELECT * FROM relationships WHERE user_id = ? ORDER BY last_interaction DESC",
                (user_id,)
            )
        return [Relationship.from_dict(r) for r in results]
        
    async def create_relationship(self, relationship: Relationship) -> int:
        """Create new relationship"""
        db = await self._get_db()
        cursor = await db.execute(
            """
            INSERT INTO relationships 
            (user_id, bot_name, role, instance_id, status, intimacy_level, total_interactions,
             total_intim_sessions, total_climax, created_at, last_interaction,
             preferences, milestones, history)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                relationship.user_id, relationship.bot_name, relationship.role, relationship.instance_id,
                relationship.status.value, relationship.intimacy_level,
                relationship.total_interactions, relationship.total_intim_sessions,
                relationship.total_climax, relationship.created_at,
                relationship.last_interaction, json.dumps(relationship.preferences),
                json.dumps(relationship.milestones), json.dumps(relationship.history)
            )
        )
        return cursor.lastrowid
        
    async def update_relationship(self, relationship: Relationship):
        """Update relationship"""
        db = await self._get_db()
        await db.execute(
            """
            UPDATE relationships SET
                status = ?, intimacy_level = ?, total_interactions = ?,
                total_intim_sessions = ?, total_climax = ?, last_interaction = ?,
                preferences = ?, milestones = ?, history = ?
            WHERE id = ?
            """,
            (
                relationship.status.value, relationship.intimacy_level,
                relationship.total_interactions, relationship.total_intim_sessions,
                relationship.total_climax, relationship.last_interaction,
                json.dumps(relationship.preferences), json.dumps(relationship.milestones),
                json.dumps(relationship.history), relationship.id
            )
        )
        
    async def delete_relationship(self, relationship_id: int):
        """Delete relationship"""
        db = await self._get_db()
        await db.execute(
            "DELETE FROM relationships WHERE id = ?",
            (relationship_id,)
        )
        
    # =========================================================================
    # PDKT REPOSITORY (BARU)
    # =========================================================================
    
    async def create_pdkt(self, pdkt: PDKT) -> str:
        """Create new PDKT"""
        db = await self._get_db()
        await db.execute(
            """
            INSERT INTO pdkt 
            (id, user_id, bot_name, role, status, is_paused, paused_at, direction, stage,
             level, chemistry_score, chemistry_history, created_at, last_interaction,
             total_minutes, paused_total, total_chats, total_intim, total_climax,
             milestones, inner_thoughts, ended_at, end_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                pdkt.id, pdkt.user_id, pdkt.bot_name, pdkt.role,
                pdkt.status.value, 1 if pdkt.is_paused else 0, pdkt.paused_at,
                pdkt.direction.value, pdkt.stage.value, pdkt.level,
                pdkt.chemistry_score, json.dumps(pdkt.chemistry_history),
                pdkt.created_at, pdkt.last_interaction,
                pdkt.total_minutes, pdkt.paused_total,
                pdkt.total_chats, pdkt.total_intim, pdkt.total_climax,
                json.dumps(pdkt.milestones), json.dumps(pdkt.inner_thoughts),
                pdkt.ended_at, pdkt.end_reason
            )
        )
        logger.info(f"✅ Created PDKT: {pdkt.id} for user {pdkt.user_id}")
        return pdkt.id
        
    async def get_pdkt(self, pdkt_id: str) -> Optional[PDKT]:
        """Get PDKT by ID"""
        db = await self._get_db()
        result = await db.fetch_one(
            "SELECT * FROM pdkt WHERE id = ?",
            (pdkt_id,)
        )
        return PDKT.from_dict(result) if result else None
        
    async def get_user_pdkt(self, user_id: int, include_ended: bool = False) -> List[PDKT]:
        """Get all PDKT for user"""
        db = await self._get_db()
        if include_ended:
            results = await db.fetch_all(
                "SELECT * FROM pdkt WHERE user_id = ? ORDER BY last_interaction DESC",
                (user_id,)
            )
        else:
            results = await db.fetch_all(
                "SELECT * FROM pdkt WHERE user_id = ? AND status != 'stopped' ORDER BY last_interaction DESC",
                (user_id,)
            )
        return [PDKT.from_dict(r) for r in results]
        
    async def get_active_pdkt(self, user_id: int) -> List[PDKT]:
        """Get active PDKT for user (not paused and not ended)"""
        db = await self._get_db()
        results = await db.fetch_all(
            "SELECT * FROM pdkt WHERE user_id = ? AND status = 'active' AND is_paused = 0 ORDER BY last_interaction DESC",
            (user_id,)
        )
        return [PDKT.from_dict(r) for r in results]
        
    async def get_paused_pdkt(self, user_id: int) -> List[PDKT]:
        """Get paused PDKT for user"""
        db = await self._get_db()
        results = await db.fetch_all(
            "SELECT * FROM pdkt WHERE user_id = ? AND is_paused = 1 ORDER BY last_interaction DESC",
            (user_id,)
        )
        return [PDKT.from_dict(r) for r in results]
        
    async def update_pdkt(self, pdkt: PDKT):
        """Update PDKT data"""
        db = await self._get_db()
        await db.execute(
            """
            UPDATE pdkt SET
                status = ?, is_paused = ?, paused_at = ?, direction = ?, stage = ?,
                level = ?, chemistry_score = ?, chemistry_history = ?,
                last_interaction = ?, total_minutes = ?, paused_total = ?,
                total_chats = ?, total_intim = ?, total_climax = ?,
                milestones = ?, inner_thoughts = ?, ended_at = ?, end_reason = ?
            WHERE id = ?
            """,
            (
                pdkt.status.value, 1 if pdkt.is_paused else 0, pdkt.paused_at,
                pdkt.direction.value, pdkt.stage.value, pdkt.level,
                pdkt.chemistry_score, json.dumps(pdkt.chemistry_history),
                pdkt.last_interaction, pdkt.total_minutes, pdkt.paused_total,
                pdkt.total_chats, pdkt.total_intim, pdkt.total_climax,
                json.dumps(pdkt.milestones), json.dumps(pdkt.inner_thoughts),
                pdkt.ended_at, pdkt.end_reason, pdkt.id
            )
        )
        logger.debug(f"Updated PDKT: {pdkt.id}")
        
    async def pause_pdkt(self, pdkt_id: str):
        """Pause PDKT"""
        db = await self._get_db()
        await db.execute(
            "UPDATE pdkt SET is_paused = 1, paused_at = ? WHERE id = ?",
            (time.time(), pdkt_id)
        )
        logger.info(f"⏸️ PDKT paused: {pdkt_id}")
        
    async def resume_pdkt(self, pdkt_id: str):
        """Resume PDKT"""
        db = await self._get_db()
        await db.execute(
            "UPDATE pdkt SET is_paused = 0, paused_at = NULL WHERE id = ?",
            (pdkt_id,)
        )
        logger.info(f"▶️ PDKT resumed: {pdkt_id}")
        
    async def stop_pdkt(self, pdkt_id: str, reason: str = "user_stopped"):
        """Stop PDKT (end)"""
        db = await self._get_db()
        await db.execute(
            "UPDATE pdkt SET status = 'stopped', ended_at = ?, end_reason = ? WHERE id = ?",
            (time.time(), reason, pdkt_id)
        )
        logger.info(f"💔 PDKT stopped: {pdkt_id}")
        
    async def add_pdkt_milestone(self, pdkt_id: str, milestone: Dict):
        """Add milestone to PDKT"""
        pdkt = await self.get_pdkt(pdkt_id)
        if pdkt:
            pdkt.milestones.append(milestone)
            await self.update_pdkt(pdkt)
            
    async def add_pdkt_inner_thought(self, pdkt_id: str, thought: Dict):
        """Add inner thought to PDKT"""
        pdkt = await self.get_pdkt(pdkt_id)
        if pdkt:
            pdkt.inner_thoughts.append(thought)
            # Keep last 20 thoughts
            if len(pdkt.inner_thoughts) > 20:
                pdkt.inner_thoughts = pdkt.inner_thoughts[-20:]
            await self.update_pdkt(pdkt)
            
    async def get_pdkt_stats(self, user_id: int) -> Dict:
        """Get PDKT statistics for user"""
        db = await self._get_db()
        
        # Total PDKT
        total = await db.fetch_one(
            "SELECT COUNT(*) as count FROM pdkt WHERE user_id = ?",
            (user_id,)
        )
        
        # Active PDKT
        active = await db.fetch_one(
            "SELECT COUNT(*) as count FROM pdkt WHERE user_id = ? AND status = 'active' AND is_paused = 0",
            (user_id,)
        )
        
        # Paused PDKT
        paused = await db.fetch_one(
            "SELECT COUNT(*) as count FROM pdkt WHERE user_id = ? AND is_paused = 1",
            (user_id,)
        )
        
        # Ended PDKT
        ended = await db.fetch_one(
            "SELECT COUNT(*) as count FROM pdkt WHERE user_id = ? AND status = 'stopped'",
            (user_id,)
        )
        
        # Average level
        avg_level = await db.fetch_one(
            "SELECT AVG(level) as avg FROM pdkt WHERE user_id = ? AND status = 'active'",
            (user_id,)
        )
        
        return {
            'total_pdkt': total['count'] if total else 0,
            'active_pdkt': active['count'] if active else 0,
            'paused_pdkt': paused['count'] if paused else 0,
            'ended_pdkt': ended['count'] if ended else 0,
            'avg_level': round(avg_level['avg'], 1) if avg_level and avg_level['avg'] else 0
        }
        
    # =========================================================================
    # PREFERENCE REPOSITORY
    # =========================================================================
    
    async def add_preference(self, preference: Preference) -> int:
        """Add or update preference"""
        db = await self._get_db()
        
        # Check if exists
        existing = await db.fetch_one(
            """
            SELECT * FROM preferences 
            WHERE user_id = ? AND pref_type = ? AND item = ?
            """,
            (preference.user_id, preference.pref_type.value, preference.item)
        )
        
        if existing:
            # Update
            await db.execute(
                """
                UPDATE preferences SET
                    score = ?, count = count + 1, last_updated = ?
                WHERE id = ?
                """,
                (preference.score, preference.last_updated, existing['id'])
            )
            return existing['id']
        else:
            # Insert
            cursor = await db.execute(
                """
                INSERT INTO preferences 
                (user_id, role, pref_type, item, score, count, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    preference.user_id, preference.role, preference.pref_type.value,
                    preference.item, preference.score, preference.count,
                    preference.last_updated
                )
            )
            return cursor.lastrowid
            
    async def get_top_preferences(self, user_id: int, pref_type: str, 
                                   role: Optional[str] = None, limit: int = 5) -> List[Preference]:
        """Get top preferences by score"""
        db = await self._get_db()
        if role:
            results = await db.fetch_all(
                """
                SELECT * FROM preferences 
                WHERE user_id = ? AND pref_type = ? AND role = ?
                ORDER BY score DESC LIMIT ?
                """,
                (user_id, pref_type, role, limit)
            )
        else:
            results = await db.fetch_all(
                """
                SELECT * FROM preferences 
                WHERE user_id = ? AND pref_type = ?
                ORDER BY score DESC LIMIT ?
                """,
                (user_id, pref_type, limit)
            )
        return [Preference.from_dict(r) for r in results]
        
    # =========================================================================
    # MILESTONE REPOSITORY
    # =========================================================================
    
    async def add_milestone(self, milestone: Milestone) -> int:
        """Add milestone"""
        db = await self._get_db()
        cursor = await db.execute(
            """
            INSERT INTO milestones 
            (user_id, role, milestone_type, description, timestamp, intimacy_level, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                milestone.user_id, milestone.role, milestone.milestone_type.value,
                milestone.description, milestone.timestamp, milestone.intimacy_level,
                json.dumps(milestone.metadata)
            )
        )
        return cursor.lastrowid
        
    async def get_user_milestones(self, user_id: int, limit: int = 20) -> List[Milestone]:
        """Get user milestones"""
        db = await self._get_db()
        results = await db.fetch_all(
            "SELECT * FROM milestones WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
            (user_id, limit)
        )
        return [Milestone.from_dict(r) for r in results]
        
    async def get_role_milestones(self, user_id: int, role: str, limit: int = 10) -> List[Milestone]:
        """Get milestones for specific role"""
        db = await self._get_db()
        results = await db.fetch_all(
            "SELECT * FROM milestones WHERE user_id = ? AND role = ? ORDER BY timestamp DESC LIMIT ?",
            (user_id, role, limit)
        )
        return [Milestone.from_dict(r) for r in results]
        
    # =========================================================================
    # BACKUP REPOSITORY
    # =========================================================================
    
    async def add_backup(self, backup: Backup) -> int:
        """Add backup record"""
        db = await self._get_db()
        cursor = await db.execute(
            """
            INSERT INTO backups 
            (filename, size, created_at, type, status, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                backup.filename, backup.size, backup.created_at,
                backup.type.value, backup.status.value,
                json.dumps(backup.metadata)
            )
        )
        return cursor.lastrowid
        
    async def get_backups(self, limit: int = 10) -> List[Backup]:
        """Get recent backups"""
        db = await self._get_db()
        results = await db.fetch_all(
            "SELECT * FROM backups ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        return [Backup.from_dict(r) for r in results]
        
    async def update_backup_status(self, backup_id: int, status: BackupStatus):
        """Update backup status"""
        db = await self._get_db()
        await db.execute(
            "UPDATE backups SET status = ? WHERE id = ?",
            (status.value, backup_id)
        )
        
    async def delete_old_backups(self, keep_days: int = 7):
        """Delete backups older than keep_days"""
        db = await self._get_db()
        cutoff = time.time() - (keep_days * 86400)
        await db.execute(
            "DELETE FROM backups WHERE created_at < ?",
            (cutoff,)
        )
        
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        db = await self._get_db()
        
        # Total sessions
        sessions = await db.fetch_one(
            "SELECT COUNT(*) as count FROM sessions WHERE user_id = ?",
            (user_id,)
        )
        
        # Total messages
        messages = await db.fetch_one(
            """
            SELECT COUNT(*) as count FROM conversations c
            JOIN sessions s ON c.session_id = s.id
            WHERE s.user_id = ?
            """,
            (user_id,)
        )
        
        # Total memories
        memories = await db.fetch_one(
            "SELECT COUNT(*) as count FROM memories WHERE user_id = ?",
            (user_id,)
        )
        
        # Total climax
        climax = await db.fetch_one(
            "SELECT SUM(total_climax) as total FROM relationships WHERE user_id = ?",
            (user_id,)
        )
        
        # Active relationships
        active = await db.fetch_one(
            "SELECT COUNT(*) as count FROM relationships WHERE user_id = ? AND status IN ('hts', 'fwb', 'pacar')",
            (user_id,)
        )
        
        # PDKT stats
        pdkt_stats = await self.get_pdkt_stats(user_id)
        
        return {
            'total_sessions': sessions['count'] if sessions else 0,
            'total_messages': messages['count'] if messages else 0,
            'total_memories': memories['count'] if memories else 0,
            'total_climax': climax['total'] if climax and climax['total'] else 0,
            'active_relationships': active['count'] if active else 0,
            'pdkt': pdkt_stats
        }
        
    async def cleanup_old_data(self, days: int = 30):
        """Clean up old data"""
        cutoff = time.time() - (days * 86400)
        db = await self._get_db()
        
        # Delete old conversations (through closed sessions)
        await db.execute(
            """
            DELETE FROM conversations 
            WHERE session_id IN (
                SELECT id FROM sessions 
                WHERE status = 'closed' AND last_message_time < ?
            )
            """,
            (cutoff,)
        )
        
        # Delete old closed sessions
        await db.execute(
            "DELETE FROM sessions WHERE status = 'closed' AND last_message_time < ?",
            (cutoff,)
        )
        
        # Delete old memories (low importance)
        await db.execute(
            "DELETE FROM memories WHERE importance < 0.3 AND timestamp < ?",
            (cutoff,)
        )
        
        # Delete old PDKT (stopped more than 30 days)
        await db.execute(
            "DELETE FROM pdkt WHERE status = 'stopped' AND ended_at < ?",
            (cutoff,)
        )
        
        logger.info(f"🧹 Cleaned up data older than {days} days")


__all__ = ['Repository']
