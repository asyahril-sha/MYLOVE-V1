#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - DATABASE REPOSITORY (FIX LENGKAP)
=============================================================================
Menggabungkan semua import yang diperlukan
=============================================================================
"""

import time
import json
import logging
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta

from .connection import get_db

# ===== IMPORT DARI V1 MODELS (untuk method lama) =====
from .models import (
    User, Session, Conversation, Memory, Relationship,
    Preference, Milestone, Backup,
    RelationshipStatus, MemoryType, MilestoneType,
    BackupType, BackupStatus, SessionStatus, PreferenceType
)

# ===== IMPORT DARI V2 MODELS (untuk method baru) =====
from .models_v2 import (
    PDKTSession, PDKTInnerThought, Mantan, FWBRequest,
    FWBRelation, HTSRelation, MemoryV2,
    PDKTStatus, PDKTDirection, ChemistryLevel, MoodType,
    MantanStatus, FWBStatus, HTSStatus
)

logger = logging.getLogger(__name__)


class Repository:
    """
    Repository untuk semua operasi database V1 + V2
    """
    
    def __init__(self):
        self.db = None
        
    async def _get_db(self):
        """Get database connection"""
        if not self.db:
            self.db = await get_db()
        return self.db
    
    # =========================================================================
    # USER REPOSITORY (V1)
    # =========================================================================
    
    async def get_user(self, telegram_id: int) -> Optional[User]:
        db = await self._get_db()
        result = await db.fetch_one(
            "SELECT * FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        return User.from_dict(result) if result else None
        
    async def create_user(self, user: User) -> int:
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
        
    async def update_user_last_active(self, telegram_id: int):
        db = await self._get_db()
        await db.execute(
            "UPDATE users SET last_active = ? WHERE telegram_id = ?",
            (time.time(), telegram_id)
        )
        
    async def increment_user_interactions(self, telegram_id: int):
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
    # SESSION REPOSITORY (V1)
    # =========================================================================
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        db = await self._get_db()
        result = await db.fetch_one(
            "SELECT * FROM sessions WHERE id = ?",
            (session_id,)
        )
        return Session.from_dict(result) if result else None
        
    async def get_active_session(self, user_id: int, role: Optional[str] = None) -> Optional[Session]:
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
        db = await self._get_db()
        if include_closed:
            query = "SELECT * FROM sessions WHERE user_id = ? ORDER BY last_message_time DESC LIMIT ?"
        else:
            query = "SELECT * FROM sessions WHERE user_id = ? AND status = 'active' ORDER BY last_message_time DESC LIMIT ?"
            
        results = await db.fetch_all(query, (user_id, limit))
        return [Session.from_dict(r) for r in results]
        
    async def create_session(self, session: Session) -> str:
        db = await self._get_db()
        await db.execute(
            """
            INSERT INTO sessions 
            (id, user_id, role, status, start_time, last_message_time, 
             total_messages, intimacy_level, location, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session.id, session.user_id, session.role, session.status.value,
                session.start_time, session.last_message_time,
                session.total_messages, session.intimacy_level,
                session.location, json.dumps(session.metadata)
            )
        )
        logger.info(f"✅ Created session: {session.id}")
        return session.id
        
    async def update_session(self, session: Session):
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
        db = await self._get_db()
        await db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        logger.info(f"🗑️ Deleted session: {session_id}")
    
    # =========================================================================
    # CONVERSATION REPOSITORY (V1)
    # =========================================================================
    
    async def add_message(self, conversation: Conversation) -> int:
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
        db = await self._get_db()
        results = await db.fetch_all(
            "SELECT * FROM conversations WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
            (session_id, limit)
        )
        return [Conversation.from_dict(r) for r in results]
        
    async def get_recent_conversations(self, user_id: int, limit: int = 10) -> List[Conversation]:
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
    # MEMORY REPOSITORY (V1)
    # =========================================================================
    
    async def add_memory(self, memory: Memory) -> int:
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
        db = await self._get_db()
        results = await db.fetch_all(
            "SELECT * FROM memories WHERE user_id = ? AND role = ? ORDER BY importance DESC LIMIT ?",
            (user_id, role, limit)
        )
        return [Memory.from_dict(r) for r in results]
    
    # =========================================================================
    # RELATIONSHIP REPOSITORY (V1)
    # =========================================================================
    
    async def get_relationship(self, user_id: int, role: str, instance_id: Optional[str] = None) -> Optional[Relationship]:
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
        db = await self._get_db()
        cursor = await db.execute(
            """
            INSERT INTO relationships 
            (user_id, role, instance_id, status, intimacy_level, total_interactions,
             total_intim_sessions, total_climax, created_at, last_interaction,
             preferences, milestones, history)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                relationship.user_id, relationship.role, relationship.instance_id,
                relationship.status.value, relationship.intimacy_level,
                relationship.total_interactions, relationship.total_intim_sessions,
                relationship.total_climax, relationship.created_at,
                relationship.last_interaction, json.dumps(relationship.preferences),
                json.dumps(relationship.milestones), json.dumps(relationship.history)
            )
        )
        return cursor.lastrowid
        
    async def update_relationship(self, relationship: Relationship):
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
    
    # =========================================================================
    # PREFERENCE REPOSITORY (V1)
    # =========================================================================
    
    async def add_preference(self, preference: Preference) -> int:
        db = await self._get_db()
        
        existing = await db.fetch_one(
            """
            SELECT * FROM preferences 
            WHERE user_id = ? AND pref_type = ? AND item = ?
            """,
            (preference.user_id, preference.pref_type.value, preference.item)
        )
        
        if existing:
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
    # MILESTONE REPOSITORY (V1)
    # =========================================================================
    
    async def add_milestone(self, milestone: Milestone) -> int:
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
        db = await self._get_db()
        results = await db.fetch_all(
            "SELECT * FROM milestones WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
            (user_id, limit)
        )
        return [Milestone.from_dict(r) for r in results]
        
    async def get_role_milestones(self, user_id: int, role: str, limit: int = 10) -> List[Milestone]:
        db = await self._get_db()
        results = await db.fetch_all(
            "SELECT * FROM milestones WHERE user_id = ? AND role = ? ORDER BY timestamp DESC LIMIT ?",
            (user_id, role, limit)
        )
        return [Milestone.from_dict(r) for r in results]
    
    # =========================================================================
    # BACKUP REPOSITORY (V1)
    # =========================================================================
    
    async def add_backup(self, backup: Backup) -> int:
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
        db = await self._get_db()
        results = await db.fetch_all(
            "SELECT * FROM backups ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        return [Backup.from_dict(r) for r in results]
    
    # =========================================================================
    # V2 METHODS - AKAN DITAMBAHKAN SECARA TERPISAH
    # =========================================================================
    # (Method V2 ada di repository_v2.py)
