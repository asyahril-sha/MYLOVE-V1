#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - DATABASE REPOSITORY V2
=============================================================================
Berdasarkan V1 dengan penambahan method untuk:
- PDKT Natural (create, get, update, pause, resume, stop)
- Mantan (add, get, list, fwb request)
- FWB (create, pause, resume, end, get top)
- HTS (create, get, list, check expiry)
- Memory V2 (save, recall, search)
=============================================================================
"""

import time
import json
import logging
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta

from .connection import get_db
from .models_v2 import (
    # V1 Models
    User, Session, Conversation, Memory, Relationship,
    Preference, Milestone, Backup,
    # V2 Models
    PDKTSession, PDKTInnerThought, Mantan, FWBRequest,
    FWBRelation, HTSRelation, MemoryV2,
    # Enums
    PDKTStatus, PDKTDirection, ChemistryLevel, MoodType,
    MantanStatus, FWBStatus, HTSStatus
)

logger = logging.getLogger(__name__)


class RepositoryV2:
    """
    Repository untuk semua operasi database V2
    Menggabungkan method V1 dan menambah method V2
    """
    
    def __init__(self):
        self.db = None
        
    async def _get_db(self):
        """Get database connection"""
        if not self.db:
            self.db = await get_db()
        return self.db
    
    # =========================================================================
    # USER REPOSITORY (V1 - TETAP)
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
    # SESSION REPOSITORY (V1 - TETAP)
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
    # CONVERSATION REPOSITORY (V1 - TETAP)
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
    # MEMORY REPOSITORY (V1 - TETAP)
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
        
    async def get_user_memories(self, user_id: int, memory_type: Optional[str] = None, 
                                limit: int = 50) -> List[Memory]:
        """Get memories for user"""
        db = await self._get_db()
        if memory_type:
            results = await db.fetch_all(
                "SELECT * FROM memories WHERE user_id = ? AND memory_type = ? ORDER BY importance DESC LIMIT ?",
                (user_id, memory_type, limit)
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
    
    # =========================================================================
    # RELATIONSHIP REPOSITORY (V1 - TETAP)
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
        
    async def get_all_relationships(self, user_id: int, status: Optional[str] = None) -> List[Relationship]:
        """Get all relationships for user"""
        db = await self._get_db()
        if status:
            results = await db.fetch_all(
                "SELECT * FROM relationships WHERE user_id = ? AND status = ? ORDER BY last_interaction DESC",
                (user_id, status)
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
    
    # =========================================================================
    # PREFERENCE REPOSITORY (V1 - TETAP)
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
    # MILESTONE REPOSITORY (V1 - TETAP)
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
    # BACKUP REPOSITORY (V1 - TETAP)
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
    
    # =========================================================================
    # PDKT REPOSITORY (BARU V2)
    # =========================================================================
    
    async def create_pdkt(self, pdkt: PDKTSession) -> str:
        """Create new PDKT session"""
        db = await self._get_db()
        await db.execute(
            """
            INSERT INTO pdkt_sessions 
            (id, user_id, role, bot_name, status, direction, chemistry_score,
             chemistry_level, mood, level, total_duration, total_chats,
             total_intim, total_climax, created_at, last_interaction,
             paused_at, ended_at, end_reason, inner_thoughts, milestones, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                pdkt.id, pdkt.user_id, pdkt.role, pdkt.bot_name,
                pdkt.status.value, pdkt.direction.value, pdkt.chemistry_score,
                pdkt.chemistry_level.value, pdkt.mood.value, pdkt.level,
                pdkt.total_duration, pdkt.total_chats, pdkt.total_intim,
                pdkt.total_climax, pdkt.created_at, pdkt.last_interaction,
                pdkt.paused_at, pdkt.ended_at, pdkt.end_reason,
                json.dumps(pdkt.inner_thoughts), json.dumps(pdkt.milestones),
                json.dumps(pdkt.metadata)
            )
        )
        logger.info(f"✅ Created PDKT session: {pdkt.id}")
        return pdkt.id
    
    async def get_pdkt(self, pdkt_id: str) -> Optional[PDKTSession]:
        """Get PDKT session by ID"""
        db = await self._get_db()
        result = await db.fetch_one(
            "SELECT * FROM pdkt_sessions WHERE id = ?",
            (pdkt_id,)
        )
        return PDKTSession.from_dict(result) if result else None
    
    async def get_user_pdkt_list(self, user_id: int, include_ended: bool = False) -> List[PDKTSession]:
        """Get all PDKT sessions for user"""
        db = await self._get_db()
        if include_ended:
            query = "SELECT * FROM pdkt_sessions WHERE user_id = ? ORDER BY last_interaction DESC"
        else:
            query = "SELECT * FROM pdkt_sessions WHERE user_id = ? AND status IN ('active', 'paused') ORDER BY last_interaction DESC"
        
        results = await db.fetch_all(query, (user_id,))
        return [PDKTSession.from_dict(r) for r in results]
    
    async def get_active_pdkt_by_role(self, user_id: int, role: str) -> Optional[PDKTSession]:
        """Get active PDKT for specific role"""
        db = await self._get_db()
        result = await db.fetch_one(
            "SELECT * FROM pdkt_sessions WHERE user_id = ? AND role = ? AND status = 'active' LIMIT 1",
            (user_id, role)
        )
        return PDKTSession.from_dict(result) if result else None
    
    async def update_pdkt(self, pdkt: PDKTSession):
        """Update PDKT session"""
        db = await self._get_db()
        await db.execute(
            """
            UPDATE pdkt_sessions SET
                status = ?, direction = ?, chemistry_score = ?,
                chemistry_level = ?, mood = ?, level = ?,
                total_duration = ?, total_chats = ?, total_intim = ?,
                total_climax = ?, last_interaction = ?, paused_at = ?,
                ended_at = ?, end_reason = ?, inner_thoughts = ?,
                milestones = ?, metadata = ?
            WHERE id = ?
            """,
            (
                pdkt.status.value, pdkt.direction.value, pdkt.chemistry_score,
                pdkt.chemistry_level.value, pdkt.mood.value, pdkt.level,
                pdkt.total_duration, pdkt.total_chats, pdkt.total_intim,
                pdkt.total_climax, pdkt.last_interaction, pdkt.paused_at,
                pdkt.ended_at, pdkt.end_reason,
                json.dumps(pdkt.inner_thoughts), json.dumps(pdkt.milestones),
                json.dumps(pdkt.metadata), pdkt.id
            )
        )
    
    async def pause_pdkt(self, pdkt_id: str):
        """Pause PDKT session"""
        db = await self._get_db()
        await db.execute(
            "UPDATE pdkt_sessions SET status = ?, paused_at = ? WHERE id = ?",
            (PDKTStatus.PAUSED.value, time.time(), pdkt_id)
        )
        logger.info(f"⏸️ Paused PDKT: {pdkt_id}")
    
    async def resume_pdkt(self, pdkt_id: str):
        """Resume PDKT session"""
        db = await self._get_db()
        await db.execute(
            "UPDATE pdkt_sessions SET status = ?, paused_at = NULL WHERE id = ?",
            (PDKTStatus.ACTIVE.value, pdkt_id)
        )
        logger.info(f"▶️ Resumed PDKT: {pdkt_id}")
    
    async def stop_pdkt(self, pdkt_id: str, reason: str):
        """Stop/end PDKT session"""
        db = await self._get_db()
        await db.execute(
            "UPDATE pdkt_sessions SET status = ?, ended_at = ?, end_reason = ? WHERE id = ?",
            (PDKTStatus.ENDED.value, time.time(), reason, pdkt_id)
        )
        logger.info(f"💔 Stopped PDKT: {pdkt_id}")
    
    async def add_inner_thought(self, thought: PDKTInnerThought) -> int:
        """Add inner thought to PDKT"""
        db = await self._get_db()
        cursor = await db.execute(
            """
            INSERT INTO pdkt_inner_thoughts 
            (pdkt_id, thought, context, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (thought.pdkt_id, thought.thought, thought.context, thought.timestamp)
        )
        return cursor.lastrowid
    
    async def get_inner_thoughts(self, pdkt_id: str, limit: int = 10) -> List[PDKTInnerThought]:
        """Get inner thoughts for PDKT"""
        db = await self._get_db()
        results = await db.fetch_all(
            "SELECT * FROM pdkt_inner_thoughts WHERE pdkt_id = ? ORDER BY timestamp DESC LIMIT ?",
            (pdkt_id, limit)
        )
        return [PDKTInnerThought.from_dict(r) for r in results]
    
    # =========================================================================
    # MANTAN REPOSITORY (BARU V2)
    # =========================================================================
    
    async def add_mantan(self, mantan: Mantan) -> str:
        """Add new mantan"""
        db = await self._get_db()
        await db.execute(
            """
            INSERT INTO mantan 
            (id, user_id, pdkt_id, bot_name, role, status, putus_time,
             putus_reason, chemistry_history, milestones, total_chats,
             total_intim, total_climax, first_kiss_time, first_intim_time,
             become_pacar_time, last_chat_time, fwb_requests,
             fwb_start_time, fwb_end_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                mantan.id, mantan.user_id, mantan.pdkt_id, mantan.bot_name,
                mantan.role, mantan.status.value, mantan.putus_time,
                mantan.putus_reason, json.dumps(mantan.chemistry_history),
                json.dumps(mantan.milestones), mantan.total_chats,
                mantan.total_intim, mantan.total_climax, mantan.first_kiss_time,
                mantan.first_intim_time, mantan.become_pacar_time,
                mantan.last_chat_time, json.dumps(mantan.fwb_requests),
                mantan.fwb_start_time, mantan.fwb_end_time
            )
        )
        logger.info(f"✅ Added mantan: {mantan.id}")
        return mantan.id
    
    async def get_mantan(self, mantan_id: str) -> Optional[Mantan]:
        """Get mantan by ID"""
        db = await self._get_db()
        result = await db.fetch_one(
            "SELECT * FROM mantan WHERE id = ?",
            (mantan_id,)
        )
        return Mantan.from_dict(result) if result else None
    
    async def get_user_mantan(self, user_id: int) -> List[Mantan]:
        """Get all mantan for user"""
        db = await self._get_db()
        results = await db.fetch_all(
            "SELECT * FROM mantan WHERE user_id = ? ORDER BY putus_time DESC",
            (user_id,)
        )
        return [Mantan.from_dict(r) for r in results]
    
    async def update_mantan_status(self, mantan_id: str, status: MantanStatus):
        """Update mantan status"""
        db = await self._get_db()
        await db.execute(
            "UPDATE mantan SET status = ? WHERE id = ?",
            (status.value, mantan_id)
        )
    
    async def update_mantan_fwb(self, mantan_id: str, fwb_start: float = None, fwb_end: float = None):
        """Update FWB related fields in mantan"""
        db = await self._get_db()
        if fwb_start:
            await db.execute(
                "UPDATE mantan SET fwb_start_time = ?, status = ? WHERE id = ?",
                (fwb_start, MantanStatus.FWB_ACCEPTED.value, mantan_id)
            )
        elif fwb_end:
            await db.execute(
                "UPDATE mantan SET fwb_end_time = ?, status = ? WHERE id = ?",
                (fwb_end, MantanStatus.FWB_ENDED.value, mantan_id)
            )
    
    # =========================================================================
    # FWB REQUEST REPOSITORY (BARU V2)
    # =========================================================================
    
    async def create_fwb_request(self, request: FWBRequest) -> str:
        """Create new FWB request"""
        db = await self._get_db()
        await db.execute(
            """
            INSERT INTO fwb_requests 
            (id, user_id, mantan_id, bot_name, user_message, timestamp, status, bot_decision, expiry_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request.id, request.user_id, request.mantan_id, request.bot_name,
                request.user_message, request.timestamp, request.status,
                json.dumps(request.bot_decision), request.expiry_time
            )
        )
        return request.id
    
    async def get_fwb_request(self, request_id: str) -> Optional[FWBRequest]:
        """Get FWB request by ID"""
        db = await self._get_db()
        result = await db.fetch_one(
            "SELECT * FROM fwb_requests WHERE id = ?",
            (request_id,)
        )
        return FWBRequest.from_dict(result) if result else None
    
    async def get_pending_fwb_requests(self, user_id: int) -> List[FWBRequest]:
        """Get all pending FWB requests for user"""
        db = await self._get_db()
        results = await db.fetch_all(
            "SELECT * FROM fwb_requests WHERE user_id = ? AND status = 'pending' ORDER BY timestamp DESC",
            (user_id,)
        )
        return [FWBRequest.from_dict(r) for r in results]
    
    async def update_fwb_request_status(self, request_id: str, status: str, bot_decision: Dict = None):
        """Update FWB request status"""
        db = await self._get_db()
        if bot_decision:
            await db.execute(
                "UPDATE fwb_requests SET status = ?, bot_decision = ? WHERE id = ?",
                (status, json.dumps(bot_decision), request_id)
            )
        else:
            await db.execute(
                "UPDATE fwb_requests SET status = ? WHERE id = ?",
                (status, request_id)
            )
    
    # =========================================================================
    # FWB REPOSITORY (BARU V2)
    # =========================================================================
    
    async def create_fwb(self, fwb: FWBRelation) -> str:
        """Create new FWB relationship"""
        db = await self._get_db()
        await db.execute(
            """
            INSERT INTO fwb_relations 
            (id, user_id, mantan_id, bot_name, role, status, created_at,
             last_interaction, chemistry_score, climax_count, intim_count,
             total_chats, pause_history, ended_at, end_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                fwb.id, fwb.user_id, fwb.mantan_id, fwb.bot_name, fwb.role,
                fwb.status.value, fwb.created_at, fwb.last_interaction,
                fwb.chemistry_score, fwb.climax_count, fwb.intim_count,
                fwb.total_chats, json.dumps(fwb.pause_history),
                fwb.ended_at, fwb.end_reason
            )
        )
        logger.info(f"✅ Created FWB: {fwb.id}")
        return fwb.id
    
    async def get_fwb(self, fwb_id: str) -> Optional[FWBRelation]:
        """Get FWB by ID"""
        db = await self._get_db()
        result = await db.fetch_one(
            "SELECT * FROM fwb_relations WHERE id = ?",
            (fwb_id,)
        )
        return FWBRelation.from_dict(result) if result else None
    
    async def get_user_fwb(self, user_id: int, include_ended: bool = False) -> List[FWBRelation]:
        """Get all FWB for user"""
        db = await self._get_db()
        if include_ended:
            query = "SELECT * FROM fwb_relations WHERE user_id = ? ORDER BY last_interaction DESC"
        else:
            query = "SELECT * FROM fwb_relations WHERE user_id = ? AND status IN ('active', 'paused') ORDER BY last_interaction DESC"
        
        results = await db.fetch_all(query, (user_id,))
        return [FWBRelation.from_dict(r) for r in results]
    
    async def get_top_fwb(self, user_id: int, limit: int = 10) -> List[FWBRelation]:
        """Get top FWB by score (chemistry * 0.6 + climax * 0.4)"""
        db = await self._get_db()
        results = await db.fetch_all(
            """
            SELECT *, (chemistry_score * 0.6 + climax_count * 0.4) as score 
            FROM fwb_relations 
            WHERE user_id = ? AND status = 'active' 
            ORDER BY score DESC LIMIT ?
            """,
            (user_id, limit)
        )
        return [FWBRelation.from_dict(r) for r in results]
    
    async def update_fwb(self, fwb: FWBRelation):
        """Update FWB relationship"""
        db = await self._get_db()
        await db.execute(
            """
            UPDATE fwb_relations SET
                status = ?, last_interaction = ?, chemistry_score = ?,
                climax_count = ?, intim_count = ?, total_chats = ?,
                pause_history = ?, ended_at = ?, end_reason = ?
            WHERE id = ?
            """,
            (
                fwb.status.value, fwb.last_interaction, fwb.chemistry_score,
                fwb.climax_count, fwb.intim_count, fwb.total_chats,
                json.dumps(fwb.pause_history), fwb.ended_at, fwb.end_reason,
                fwb.id
            )
        )
    
    async def pause_fwb(self, fwb_id: str, reason: str):
        """Pause FWB relationship"""
        db = await self._get_db()
        # Get current pause history
        fwb = await self.get_fwb(fwb_id)
        if fwb:
            pause_history = fwb.pause_history
            pause_history.append({
                'timestamp': time.time(),
                'action': 'pause',
                'reason': reason
            })
            
            await db.execute(
                """
                UPDATE fwb_relations SET
                    status = ?, pause_history = ?
                WHERE id = ?
                """,
                (FWBStatus.PAUSED.value, json.dumps(pause_history), fwb_id)
            )
            logger.info(f"⏸️ Paused FWB: {fwb_id}")
    
    async def resume_fwb(self, fwb_id: str):
        """Resume FWB relationship"""
        db = await self._get_db()
        # Get current pause history
        fwb = await self.get_fwb(fwb_id)
        if fwb:
            pause_history = fwb.pause_history
            pause_history.append({
                'timestamp': time.time(),
                'action': 'resume'
            })
            
            await db.execute(
                """
                UPDATE fwb_relations SET
                    status = ?, pause_history = ?, last_interaction = ?
                WHERE id = ?
                """,
                (FWBStatus.ACTIVE.value, json.dumps(pause_history), time.time(), fwb_id)
            )
            logger.info(f"▶️ Resumed FWB: {fwb_id}")
    
    async def end_fwb(self, fwb_id: str, reason: str):
        """End FWB relationship"""
        db = await self._get_db()
        await db.execute(
            """
            UPDATE fwb_relations SET
                status = ?, ended_at = ?, end_reason = ?
            WHERE id = ?
            """,
            (FWBStatus.ENDED.value, time.time(), reason, fwb_id)
        )
        logger.info(f"💔 Ended FWB: {fwb_id}")
    
    # =========================================================================
    # HTS REPOSITORY (BARU V2)
    # =========================================================================
    
    async def create_hts(self, hts: HTSRelation) -> str:
        """Create new HTS relationship"""
        db = await self._get_db()
        await db.execute(
            """
            INSERT INTO hts_relations 
            (id, user_id, role, bot_name, status, created_at, expiry_time,
             last_interaction, chemistry_score, climax_count, intimacy_level,
             total_chats, total_intim, history)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                hts.id, hts.user_id, hts.role, hts.bot_name,
                hts.status.value, hts.created_at, hts.expiry_time,
                hts.last_interaction, hts.chemistry_score, hts.climax_count,
                hts.intimacy_level, hts.total_chats, hts.total_intim,
                json.dumps(hts.history)
            )
        )
        logger.info(f"✅ Created HTS: {hts.id}")
        return hts.id
    
    async def get_hts(self, hts_id: str) -> Optional[HTSRelation]:
        """Get HTS by ID"""
        db = await self._get_db()
        result = await db.fetch_one(
            "SELECT * FROM hts_relations WHERE id = ?",
            (hts_id,)
        )
        return HTSRelation.from_dict(result) if result else None
    
    async def get_user_hts(self, user_id: int, include_expired: bool = False) -> List[HTSRelation]:
        """Get all HTS for user"""
        db = await self._get_db()
        now = time.time()
        
        if include_expired:
            query = "SELECT * FROM hts_relations WHERE user_id = ? ORDER BY last_interaction DESC"
            results = await db.fetch_all(query, (user_id,))
        else:
            query = "SELECT * FROM hts_relations WHERE user_id = ? AND status = 'active' AND expiry_time > ? ORDER BY last_interaction DESC"
            results = await db.fetch_all(query, (user_id, now))
        
        return [HTSRelation.from_dict(r) for r in results]
    
    async def get_top_hts(self, user_id: int, limit: int = 10) -> List[HTSRelation]:
        """Get top HTS by score (chemistry * 0.5 + climax * 0.3 + intimacy_level * 0.2)"""
        db = await self._get_db()
        now = time.time()
        results = await db.fetch_all(
            """
            SELECT *, (chemistry_score * 0.5 + climax_count * 0.3 + intimacy_level * 0.2) as score 
            FROM hts_relations 
            WHERE user_id = ? AND status = 'active' AND expiry_time > ?
            ORDER BY score DESC LIMIT ?
            """,
            (user_id, now, limit)
        )
        return [HTSRelation.from_dict(r) for r in results]
    
    async def update_hts(self, hts: HTSRelation):
        """Update HTS relationship"""
        db = await self._get_db()
        await db.execute(
            """
            UPDATE hts_relations SET
                status = ?, last_interaction = ?, chemistry_score = ?,
                climax_count = ?, intimacy_level = ?, total_chats = ?,
                total_intim = ?, history = ?
            WHERE id = ?
            """,
            (
                hts.status.value, hts.last_interaction, hts.chemistry_score,
                hts.climax_count, hts.intimacy_level, hts.total_chats,
                hts.total_intim, json.dumps(hts.history), hts.id
            )
        )
    
    async def check_expired_hts(self, user_id: Optional[int] = None) -> int:
        """Check and mark expired HTS"""
        db = await self._get_db()
        now = time.time()
        
        if user_id:
            result = await db.execute(
                "UPDATE hts_relations SET status = ? WHERE user_id = ? AND status = 'active' AND expiry_time < ?",
                (HTSStatus.EXPIRED.value, user_id, now)
            )
        else:
            result = await db.execute(
                "UPDATE hts_relations SET status = ? WHERE status = 'active' AND expiry_time < ?",
                (HTSStatus.EXPIRED.value, now)
            )
        
        # Get number of affected rows
        count = result.rowcount
        if count > 0:
            logger.info(f"⏰ Marked {count} HTS as expired")
        
        return count
    
    # =========================================================================
    # MEMORY V2 REPOSITORY (BARU)
    # =========================================================================
    
    async def save_memory_v2(self, memory: MemoryV2) -> str:
        """Save memory to V2 memory table"""
        db = await self._get_db()
        await db.execute(
            """
            INSERT INTO memories_v2 
            (id, user_id, session_id, content, memory_type, importance,
             emotional_tag, timestamp, access_count, last_access, context, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                memory.id, memory.user_id, memory.session_id, memory.content,
                memory.memory_type, memory.importance, memory.emotional_tag,
                memory.timestamp, memory.access_count, memory.last_access,
                json.dumps(memory.context), json.dumps(memory.metadata)
            )
        )
        return memory.id
    
    async def get_memory_v2(self, memory_id: str) -> Optional[MemoryV2]:
        """Get memory by ID"""
        db = await self._get_db()
        result = await db.fetch_one(
            "SELECT * FROM memories_v2 WHERE id = ?",
            (memory_id,)
        )
        return MemoryV2.from_dict(result) if result else None
    
    async def search_memories(self, user_id: int, query: str, limit: int = 10) -> List[MemoryV2]:
        """Search memories by content (simple LIKE search)"""
        db = await self._get_db()
        search_term = f"%{query}%"
        results = await db.fetch_all(
            """
            SELECT * FROM memories_v2 
            WHERE user_id = ? AND content LIKE ? 
            ORDER BY importance DESC, timestamp DESC LIMIT ?
            """,
            (user_id, search_term, limit)
        )
        return [MemoryV2.from_dict(r) for r in results]
    
    async def get_recent_memories(self, user_id: int, session_id: Optional[str] = None, limit: int = 20) -> List[MemoryV2]:
        """Get recent memories"""
        db = await self._get_db()
        if session_id:
            results = await db.fetch_all(
                "SELECT * FROM memories_v2 WHERE user_id = ? AND session_id = ? ORDER BY timestamp DESC LIMIT ?",
                (user_id, session_id, limit)
            )
        else:
            results = await db.fetch_all(
                "SELECT * FROM memories_v2 WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                (user_id, limit)
            )
        return [MemoryV2.from_dict(r) for r in results]
    
    async def update_memory_access(self, memory_id: str):
        """Update memory access count and last access time"""
        db = await self._get_db()
        await db.execute(
            """
            UPDATE memories_v2 SET
                access_count = access_count + 1,
                last_access = ?
            WHERE id = ?
            """,
            (time.time(), memory_id)
        )
    
    async def delete_memory_v2(self, memory_id: str):
        """Delete memory"""
        db = await self._get_db()
        await db.execute(
            "DELETE FROM memories_v2 WHERE id = ?",
            (memory_id,)
        )
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    async def get_user_stats_v2(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user statistics including V2 data"""
        db = await self._get_db()
        
        # Basic stats from V1
        sessions = await db.fetch_one(
            "SELECT COUNT(*) as count FROM sessions WHERE user_id = ?",
            (user_id,)
        )
        
        messages = await db.fetch_one(
            """
            SELECT COUNT(*) as count FROM conversations c
            JOIN sessions s ON c.session_id = s.id
            WHERE s.user_id = ?
            """,
            (user_id,)
        )
        
        # PDKT stats
        pdkt_active = await db.fetch_one(
            "SELECT COUNT(*) as count FROM pdkt_sessions WHERE user_id = ? AND status IN ('active', 'paused')",
            (user_id,)
        )
        
        pdkt_ended = await db.fetch_one(
            "SELECT COUNT(*) as count FROM pdkt_sessions WHERE user_id = ? AND status = 'ended'",
            (user_id,)
        )
        
        # Mantan stats
        mantan = await db.fetch_one(
            "SELECT COUNT(*) as count FROM mantan WHERE user_id = ?",
            (user_id,)
        )
        
        # FWB stats
        fwb_active = await db.fetch_one(
            "SELECT COUNT(*) as count FROM fwb_relations WHERE user_id = ? AND status = 'active'",
            (user_id,)
        )
        
        fwb_paused = await db.fetch_one(
            "SELECT COUNT(*) as count FROM fwb_relations WHERE user_id = ? AND status = 'paused'",
            (user_id,)
        )
        
        # HTS stats
        hts_active = await db.fetch_one(
            "SELECT COUNT(*) as count FROM hts_relations WHERE user_id = ? AND status = 'active'",
            (user_id,)
        )
        
        # Memory stats
        memories = await db.fetch_one(
            "SELECT COUNT(*) as count FROM memories_v2 WHERE user_id = ?",
            (user_id,)
        )
        
        return {
            # V1 stats
            'total_sessions': sessions['count'] if sessions else 0,
            'total_messages': messages['count'] if messages else 0,
            
            # V2 stats
            'pdkt_active': pdkt_active['count'] if pdkt_active else 0,
            'pdkt_ended': pdkt_ended['count'] if pdkt_ended else 0,
            'total_pdkt': (pdkt_active['count'] if pdkt_active else 0) + (pdkt_ended['count'] if pdkt_ended else 0),
            'total_mantan': mantan['count'] if mantan else 0,
            'fwb_active': fwb_active['count'] if fwb_active else 0,
            'fwb_paused': fwb_paused['count'] if fwb_paused else 0,
            'total_fwb': (fwb_active['count'] if fwb_active else 0) + (fwb_paused['count'] if fwb_paused else 0),
            'hts_active': hts_active['count'] if hts_active else 0,
            'total_memories_v2': memories['count'] if memories else 0
        }
    
    async def cleanup_expired_hts(self) -> int:
        """Clean up expired HTS (mark as expired)"""
        return await self.check_expired_hts()
    
    async def cleanup_old_fwb_requests(self, days: int = 30):
        """Delete old FWB requests"""
        db = await self._get_db()
        cutoff = time.time() - (days * 86400)
        await db.execute(
            "DELETE FROM fwb_requests WHERE timestamp < ? AND status IN ('accepted', 'declined')",
            (cutoff,)
        )
        logger.info(f"🧹 Cleaned up old FWB requests older than {days} days")


__all__ = ['RepositoryV2']
