#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - SESSION STORAGE
=============================================================================
- Menyimpan session di SQLite (metadata) + JSON (full conversation)
- Auto-load session berdasarkan unique ID
- Support untuk melanjutkan session yang sudah di-close
"""

import json
import time
import aiosqlite
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from .unique_id import id_generator

logger = logging.getLogger(__name__)


class SessionStorage:
    """
    Menyimpan session dengan SQLite untuk metadata + JSON untuk full conversation
    """
    
    def __init__(self, db_path: Path, session_dir: Path):
        self.db_path = db_path
        self.session_dir = session_dir
        self.conn = None
        self.initialized = False
        
        # Buat directory session
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
    async def initialize(self):
        """Initialize database tables"""
        try:
            self.conn = await aiosqlite.connect(self.db_path)
            
            # Create sessions table
            await self.conn.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    role TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL,
                    last_message_time REAL NOT NULL,
                    total_messages INTEGER DEFAULT 0,
                    intimacy_level INTEGER DEFAULT 1,
                    status TEXT DEFAULT 'active',
                    location TEXT,
                    summary TEXT,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            ''')
            
            # Create index for faster queries
            await self.conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_user_status 
                ON sessions(user_id, status)
            ''')
            
            await self.conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_date 
                ON sessions(date)
            ''')
            
            await self.conn.commit()
            
            self.initialized = True
            logger.info(f"✅ SessionStorage initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize SessionStorage: {e}")
            raise
            
    # =========================================================================
    # CREATE SESSION
    # =========================================================================
    
    async def create_session(self, user_id: int, role: str) -> Dict:
        """
        Create new session
        
        Args:
            user_id: ID user
            role: Role name
            
        Returns:
            Session data
        """
        if not self.initialized:
            await self.initialize()
            
        # Generate unique ID
        session_id = id_generator.generate(role, user_id)
        parsed = id_generator.parse(session_id)
        
        now = time.time()
        
        # Insert into database
        await self.conn.execute('''
            INSERT INTO sessions 
            (id, role, user_id, date, sequence, start_time, last_message_time, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            role,
            user_id,
            parsed['date'],
            parsed['sequence'],
            now,
            now,
            'active'
        ))
        
        await self.conn.commit()
        
        # Create empty JSON file for conversation
        json_path = self.session_dir / f"{session_id}.json"
        with open(json_path, 'w') as f:
            json.dump({
                "session_id": session_id,
                "created_at": now,
                "conversation": [],
                "memories": [],
                "milestones": []
            }, f, indent=2)
            
        logger.info(f"📁 Created new session: {session_id}")
        
        return await self.get_session(session_id)
        
    # =========================================================================
    # GET SESSION
    # =========================================================================
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Get session by ID (metadata only)
        
        Args:
            session_id: Unique session ID
            
        Returns:
            Session metadata or None
        """
        if not self.initialized:
            await self.initialize()
            
        async with self.conn.execute(
            "SELECT * FROM sessions WHERE id = ?",
            (session_id,)
        ) as cursor:
            row = await cursor.fetchone()
            
        if not row:
            return None
            
        # Get column names
        columns = [description[0] for description in cursor.description]
        session = dict(zip(columns, row))
        
        return session
        
    async def get_full_session(self, session_id: str) -> Optional[Dict]:
        """
        Get full session termasuk conversation dari JSON
        
        Args:
            session_id: Unique session ID
            
        Returns:
            Full session data with conversation
        """
        # Get metadata
        session = await self.get_session(session_id)
        if not session:
            return None
            
        # Get conversation from JSON
        json_path = self.session_dir / f"{session_id}.json"
        if json_path.exists():
            with open(json_path, 'r') as f:
                conversation_data = json.load(f)
                session.update(conversation_data)
                
        return session
        
    async def get_active_session(self, user_id: int, role: Optional[str] = None) -> Optional[Dict]:
        """
        Get active session for user
        
        Args:
            user_id: ID user
            role: Optional role filter
            
        Returns:
            Active session or None
        """
        if not self.initialized:
            await self.initialize()
            
        query = "SELECT * FROM sessions WHERE user_id = ? AND status = 'active'"
        params = [user_id]
        
        if role:
            query += " AND role = ?"
            params.append(role)
            
        query += " ORDER BY last_message_time DESC LIMIT 1"
        
        async with self.conn.execute(query, params) as cursor:
            row = await cursor.fetchone()
            
        if not row:
            return None
            
        columns = [description[0] for description in cursor.description]
        session = dict(zip(columns, row))
        
        return session
        
    async def get_user_sessions(self, user_id: int, limit: int = 10) -> List[Dict]:
        """
        Get all sessions for user (recent first)
        
        Args:
            user_id: ID user
            limit: Max number of sessions
            
        Returns:
            List of sessions
        """
        if not self.initialized:
            await self.initialize()
            
        async with self.conn.execute(
            "SELECT * FROM sessions WHERE user_id = ? ORDER BY last_message_time DESC LIMIT ?",
            (user_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            
        if not rows:
            return []
            
        columns = [description[0] for description in cursor.description]
        sessions = [dict(zip(columns, row)) for row in rows]
        
        return sessions
        
    # =========================================================================
    # UPDATE SESSION
    # =========================================================================
    
    async def add_message(self, session_id: str, user_message: str, bot_response: str):
        """
        Add message to session
        
        Args:
            session_id: Session ID
            user_message: Pesan dari user
            bot_response: Respon dari bot
        """
        # Update database
        now = time.time()
        
        await self.conn.execute('''
            UPDATE sessions 
            SET total_messages = total_messages + 1,
                last_message_time = ?
            WHERE id = ?
        ''', (now, session_id))
        
        await self.conn.commit()
        
        # Update JSON
        json_path = self.session_dir / f"{session_id}.json"
        if json_path.exists():
            with open(json_path, 'r') as f:
                data = json.load(f)
                
            data['conversation'].append({
                "timestamp": now,
                "user": user_message,
                "bot": bot_response
            })
            
            # Keep last 100 messages
            if len(data['conversation']) > 100:
                data['conversation'] = data['conversation'][-100:]
                
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=2)
                
    async def update_intimacy(self, session_id: str, level: int):
        """Update intimacy level dalam session"""
        await self.conn.execute('''
            UPDATE sessions SET intimacy_level = ? WHERE id = ?
        ''', (level, session_id))
        await self.conn.commit()
        
    async def update_location(self, session_id: str, location: str):
        """Update lokasi dalam session"""
        await self.conn.execute('''
            UPDATE sessions SET location = ? WHERE id = ?
        ''', (location, session_id))
        await self.conn.commit()
        
    async def add_memory(self, session_id: str, memory: Dict):
        """Add memory ke session"""
        json_path = self.session_dir / f"{session_id}.json"
        if json_path.exists():
            with open(json_path, 'r') as f:
                data = json.load(f)
                
            if 'memories' not in data:
                data['memories'] = []
                
            data['memories'].append({
                **memory,
                "timestamp": time.time()
            })
            
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=2)
                
    async def add_milestone(self, session_id: str, milestone: str):
        """Add milestone ke session"""
        json_path = self.session_dir / f"{session_id}.json"
        if json_path.exists():
            with open(json_path, 'r') as f:
                data = json.load(f)
                
            if 'milestones' not in data:
                data['milestones'] = []
                
            data['milestones'].append({
                "type": milestone,
                "timestamp": time.time()
            })
            
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=2)
                
    # =========================================================================
    # CLOSE SESSION
    # =========================================================================
    
    async def close_session(self, session_id: str, summary: Optional[str] = None):
        """
        Close session
        
        Args:
            session_id: Session ID
            summary: Ringkasan session (optional)
        """
        now = time.time()
        
        await self.conn.execute('''
            UPDATE sessions 
            SET status = 'closed',
                end_time = ?,
                summary = ?
            WHERE id = ?
        ''', (now, summary, session_id))
        
        await self.conn.commit()
        
        # Generate session summary jika tidak ada
        if not summary:
            await self._generate_session_summary(session_id)
            
        logger.info(f"📁 Closed session: {session_id}")
        
    async def _generate_session_summary(self, session_id: str):
        """Generate summary dari session"""
        session = await self.get_full_session(session_id)
        if not session:
            return
            
        total_msgs = session.get('total_messages', 0)
        duration = (session.get('end_time', time.time()) - session.get('start_time', time.time())) / 60
        
        summary = f"Session {session_id}: {total_msgs} pesan, {duration:.0f} menit"
        
        if session.get('milestones'):
            summary += f", Milestone: {', '.join(session['milestones'][-3:])}"
            
        await self.conn.execute('''
            UPDATE sessions SET summary = ? WHERE id = ?
        ''', (summary, session_id))
        await self.conn.commit()
        
    # =========================================================================
    # CONTINUE SESSION
    # =========================================================================
    
    async def continue_session(self, session_id: str) -> Optional[Dict]:
        """
        Continue closed session
        
        Args:
            session_id: Session ID
            
        Returns:
            Full session data or None
        """
        session = await self.get_session(session_id)
        if not session:
            return None
            
        if session['status'] == 'active':
            # Already active
            return await self.get_full_session(session_id)
            
        # Reactivate
        await self.conn.execute('''
            UPDATE sessions 
            SET status = 'active',
                last_message_time = ?
            WHERE id = ?
        ''', (time.time(), session_id))
        
        await self.conn.commit()
        
        logger.info(f"📁 Continued session: {session_id}")
        
        return await self.get_full_session(session_id)
        
    # =========================================================================
    # DELETE SESSION
    # =========================================================================
    
    async def delete_session(self, session_id: str):
        """Delete session (admin only)"""
        # Delete from database
        await self.conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        await self.conn.commit()
        
        # Delete JSON file
        json_path = self.session_dir / f"{session_id}.json"
        if json_path.exists():
            json_path.unlink()
            
        logger.info(f"🗑️ Deleted session: {session_id}")
        
    async def delete_user_sessions(self, user_id: int):
        """Delete all sessions for user"""
        # Get all sessions
        sessions = await self.get_user_sessions(user_id, limit=1000)
        
        for session in sessions:
            await self.delete_session(session['id'])
            
        logger.info(f"🗑️ Deleted all sessions for user {user_id}")
        
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    async def get_stats(self, user_id: Optional[int] = None) -> Dict:
        """Get session statistics"""
        if not self.initialized:
            await self.initialize()
            
        if user_id:
            # Stats for specific user
            async with self.conn.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
                    SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END) as closed,
                    AVG(total_messages) as avg_messages,
                    SUM(total_messages) as total_messages
                FROM sessions 
                WHERE user_id = ?
            ''', (user_id,)) as cursor:
                row = await cursor.fetchone()
                
            if not row:
                return {}
                
            return {
                "total_sessions": row[0],
                "active_sessions": row[1] or 0,
                "closed_sessions": row[2] or 0,
                "avg_messages_per_session": round(row[3] or 0, 1),
                "total_messages": row[4] or 0
            }
        else:
            # Global stats
            async with self.conn.execute('''
                SELECT 
                    COUNT(*) as total,
                    COUNT(DISTINCT user_id) as unique_users,
                    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
                    AVG(total_messages) as avg_messages
                FROM sessions
            ''') as cursor:
                row = await cursor.fetchone()
                
            if not row:
                return {}
                
            return {
                "total_sessions": row[0],
                "unique_users": row[1],
                "active_sessions": row[2] or 0,
                "avg_messages_per_session": round(row[3] or 0, 1)
            }
            
    async def get_old_sessions(self, days: int = 30) -> List[str]:
        """
        Get sessions older than specified days
        
        Args:
            days: Age in days
            
        Returns:
            List of session IDs
        """
        cutoff = time.time() - (days * 86400)
        
        async with self.conn.execute(
            "SELECT id FROM sessions WHERE last_message_time < ?",
            (cutoff,)
        ) as cursor:
            rows = await cursor.fetchall()
            
        return [row[0] for row in rows]
        
    async def close(self):
        """Close database connection"""
        if self.conn:
            await self.conn.close()
            logger.info("SessionStorage closed")


__all__ = ['SessionStorage']
