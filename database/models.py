#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - DATABASE MODELS
=============================================================================
- Data models untuk semua entitas
- Pydantic models untuk validasi
- JSON serialization/deserialization
"""

import time
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class RelationshipStatus(str, Enum):
    """Status hubungan"""
    HTS = "hts"
    FWB = "fwb"
    PACAR = "pacar"
    PUTUS = "putus"
    BREAK = "break"


class MemoryType(str, Enum):
    """Tipe memori"""
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    RELATIONSHIP = "relationship"


class MilestoneType(str, Enum):
    """Tipe milestone"""
    FIRST_KISS = "first_kiss"
    FIRST_INTIM = "first_intim"
    FIRST_DATE = "first_date"
    FIRST_FWB = "first_fwb"
    FIRST_HTS = "first_hts"
    BECAME_PACAR = "became_pacar"
    BECAME_FWB = "became_fwb"
    LEVEL_UP = "level_up"
    AFTERCARE = "aftercare"
    RESET = "reset"
    BREAK_UP = "break_up"


class BackupType(str, Enum):
    """Tipe backup"""
    AUTO = "auto"
    MANUAL = "manual"


class BackupStatus(str, Enum):
    """Status backup"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


# =============================================================================
# USER MODELS
# =============================================================================

class User(BaseModel):
    """Model untuk user Telegram"""
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: float = Field(default_factory=time.time)
    last_active: float = Field(default_factory=time.time)
    total_interactions: int = 0
    preferences: Dict[str, Any] = Field(default_factory=dict)
    settings: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('telegram_id')
    def validate_telegram_id(cls, v):
        if v <= 0:
            raise ValueError('telegram_id must be positive')
        return v
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for DB"""
        return {
            'telegram_id': self.telegram_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at,
            'last_active': self.last_active,
            'total_interactions': self.total_interactions,
            'preferences': json.dumps(self.preferences),
            'settings': json.dumps(self.settings)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """Create from dictionary"""
        return cls(
            telegram_id=data['telegram_id'],
            username=data.get('username'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            created_at=data.get('created_at', time.time()),
            last_active=data.get('last_active', time.time()),
            total_interactions=data.get('total_interactions', 0),
            preferences=json.loads(data.get('preferences', '{}')),
            settings=json.loads(data.get('settings', '{}'))
        )


# =============================================================================
# SESSION MODELS
# =============================================================================

class Session(BaseModel):
    """Model untuk session chat"""
    id: str  # MYLOVE-ROLE-USER-DATE-SEQ
    user_id: int
    role: str
    status: str = "active"
    start_time: float = Field(default_factory=time.time)
    end_time: Optional[float] = None
    last_message_time: float = Field(default_factory=time.time)
    total_messages: int = 0
    intimacy_level: int = 1
    location: Optional[str] = None
    summary: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('role')
    def validate_role(cls, v):
        valid_roles = ['ipar', 'janda', 'pelakor', 'istri_orang', 
                      'pdkt', 'sepupu', 'teman_kantor', 'teman_sma', 'mantan']
        if v not in valid_roles:
            raise ValueError(f'role must be one of {valid_roles}')
        return v
    
    @validator('intimacy_level')
    def validate_intimacy(cls, v):
        if v < 1 or v > 12:
            raise ValueError('intimacy_level must be between 1 and 12')
        return v
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for DB"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'role': self.role,
            'status': self.status,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'last_message_time': self.last_message_time,
            'total_messages': self.total_messages,
            'intimacy_level': self.intimacy_level,
            'location': self.location,
            'summary': self.summary,
            'metadata': json.dumps(self.metadata)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Session':
        """Create from dictionary"""
        return cls(
            id=data['id'],
            user_id=data['user_id'],
            role=data['role'],
            status=data.get('status', 'active'),
            start_time=data.get('start_time', time.time()),
            end_time=data.get('end_time'),
            last_message_time=data.get('last_message_time', time.time()),
            total_messages=data.get('total_messages', 0),
            intimacy_level=data.get('intimacy_level', 1),
            location=data.get('location'),
            summary=data.get('summary'),
            metadata=json.loads(data.get('metadata', '{}'))
        )
    
    @property
    def duration_minutes(self) -> float:
        """Get session duration in minutes"""
        end = self.end_time or time.time()
        return (end - self.start_time) / 60
    
    @property
    def is_active(self) -> bool:
        """Check if session is active"""
        return self.status == "active"


# =============================================================================
# CONVERSATION MODELS
# =============================================================================

class Conversation(BaseModel):
    """Model untuk pesan dalam session"""
    id: Optional[int] = None
    session_id: str
    timestamp: float = Field(default_factory=time.time)
    user_message: str
    bot_response: str
    intent: Optional[str] = None
    mood: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for DB"""
        return {
            'session_id': self.session_id,
            'timestamp': self.timestamp,
            'user_message': self.user_message,
            'bot_response': self.bot_response,
            'intent': self.intent,
            'mood': self.mood
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Conversation':
        """Create from dictionary"""
        return cls(
            id=data.get('id'),
            session_id=data['session_id'],
            timestamp=data.get('timestamp', time.time()),
            user_message=data['user_message'],
            bot_response=data['bot_response'],
            intent=data.get('intent'),
            mood=data.get('mood')
        )


# =============================================================================
# MEMORY MODELS
# =============================================================================

class Memory(BaseModel):
    """Model untuk memori (episodic/semantic)"""
    id: Optional[int] = None
    user_id: int
    role: Optional[str] = None
    memory_type: MemoryType
    content: str
    importance: float = 0.5
    emotional_tag: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('importance')
    def validate_importance(cls, v):
        if v < 0 or v > 1:
            raise ValueError('importance must be between 0 and 1')
        return v
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for DB"""
        return {
            'user_id': self.user_id,
            'role': self.role,
            'memory_type': self.memory_type.value,
            'content': self.content,
            'importance': self.importance,
            'emotional_tag': self.emotional_tag,
            'timestamp': self.timestamp,
            'metadata': json.dumps(self.metadata)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Memory':
        """Create from dictionary"""
        return cls(
            id=data.get('id'),
            user_id=data['user_id'],
            role=data.get('role'),
            memory_type=MemoryType(data['memory_type']),
            content=data['content'],
            importance=data.get('importance', 0.5),
            emotional_tag=data.get('emotional_tag'),
            timestamp=data.get('timestamp', time.time()),
            metadata=json.loads(data.get('metadata', '{}'))
        )


# =============================================================================
# RELATIONSHIP MODELS
# =============================================================================

class Relationship(BaseModel):
    """Model untuk hubungan (HTS/FWB/Pacar)"""
    id: Optional[int] = None
    user_id: int
    role: str
    instance_id: Optional[str] = None  # Untuk multiple FWB
    status: RelationshipStatus = RelationshipStatus.HTS
    intimacy_level: int = 1
    total_interactions: int = 0
    total_intim_sessions: int = 0
    total_climax: int = 0
    created_at: float = Field(default_factory=time.time)
    last_interaction: float = Field(default_factory=time.time)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    milestones: List[Dict[str, Any]] = Field(default_factory=list)
    history: List[Dict[str, Any]] = Field(default_factory=list)
    
    @validator('intimacy_level')
    def validate_intimacy(cls, v):
        if v < 1 or v > 12:
            raise ValueError('intimacy_level must be between 1 and 12')
        return v
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for DB"""
        return {
            'user_id': self.user_id,
            'role': self.role,
            'instance_id': self.instance_id,
            'status': self.status.value,
            'intimacy_level': self.intimacy_level,
            'total_interactions': self.total_interactions,
            'total_intim_sessions': self.total_intim_sessions,
            'total_climax': self.total_climax,
            'created_at': self.created_at,
            'last_interaction': self.last_interaction,
            'preferences': json.dumps(self.preferences),
            'milestones': json.dumps(self.milestones),
            'history': json.dumps(self.history)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Relationship':
        """Create from dictionary"""
        return cls(
            id=data.get('id'),
            user_id=data['user_id'],
            role=data['role'],
            instance_id=data.get('instance_id'),
            status=RelationshipStatus(data.get('status', 'hts')),
            intimacy_level=data.get('intimacy_level', 1),
            total_interactions=data.get('total_interactions', 0),
            total_intim_sessions=data.get('total_intim_sessions', 0),
            total_climax=data.get('total_climax', 0),
            created_at=data.get('created_at', time.time()),
            last_interaction=data.get('last_interaction', time.time()),
            preferences=json.loads(data.get('preferences', '{}')),
            milestones=json.loads(data.get('milestones', '[]')),
            history=json.loads(data.get('history', '[]'))
        )
    
    @property
    def display_name(self) -> str:
        """Get display name for relationship"""
        if self.instance_id:
            return f"{self.role} #{self.instance_id[-4:]}"
        return self.role


# =============================================================================
# PREFERENCE MODELS
# =============================================================================

class Preference(BaseModel):
    """Model untuk preferensi user"""
    id: Optional[int] = None
    user_id: int
    role: Optional[str] = None
    pref_type: str  # position, area, activity, location
    item: str
    score: float = 0.5
    count: int = 1
    last_updated: float = Field(default_factory=time.time)
    
    @validator('score')
    def validate_score(cls, v):
        if v < 0 or v > 1:
            raise ValueError('score must be between 0 and 1')
        return v
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for DB"""
        return {
            'user_id': self.user_id,
            'role': self.role,
            'pref_type': self.pref_type,
            'item': self.item,
            'score': self.score,
            'count': self.count,
            'last_updated': self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Preference':
        """Create from dictionary"""
        return cls(
            id=data.get('id'),
            user_id=data['user_id'],
            role=data.get('role'),
            pref_type=data['pref_type'],
            item=data['item'],
            score=data.get('score', 0.5),
            count=data.get('count', 1),
            last_updated=data.get('last_updated', time.time())
        )


# =============================================================================
# MILESTONE MODELS
# =============================================================================

class Milestone(BaseModel):
    """Model untuk milestone dalam hubungan"""
    id: Optional[int] = None
    user_id: int
    role: Optional[str] = None
    milestone_type: MilestoneType
    description: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)
    intimacy_level: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for DB"""
        return {
            'user_id': self.user_id,
            'role': self.role,
            'milestone_type': self.milestone_type.value,
            'description': self.description,
            'timestamp': self.timestamp,
            'intimacy_level': self.intimacy_level,
            'metadata': json.dumps(self.metadata)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Milestone':
        """Create from dictionary"""
        return cls(
            id=data.get('id'),
            user_id=data['user_id'],
            role=data.get('role'),
            milestone_type=MilestoneType(data['milestone_type']),
            description=data.get('description'),
            timestamp=data.get('timestamp', time.time()),
            intimacy_level=data.get('intimacy_level'),
            metadata=json.loads(data.get('metadata', '{}'))
        )


# =============================================================================
# BACKUP MODELS
# =============================================================================

class Backup(BaseModel):
    """Model untuk history backup"""
    id: Optional[int] = None
    filename: str
    size: Optional[int] = None
    created_at: float = Field(default_factory=time.time)
    type: BackupType = BackupType.AUTO
    status: BackupStatus = BackupStatus.COMPLETED
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for DB"""
        return {
            'filename': self.filename,
            'size': self.size,
            'created_at': self.created_at,
            'type': self.type.value,
            'status': self.status.value,
            'metadata': json.dumps(self.metadata)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Backup':
        """Create from dictionary"""
        return cls(
            id=data.get('id'),
            filename=data['filename'],
            size=data.get('size'),
            created_at=data.get('created_at', time.time()),
            type=BackupType(data.get('type', 'auto')),
            status=BackupStatus(data.get('status', 'completed')),
            metadata=json.loads(data.get('metadata', '{}'))
        )


__all__ = [
    'RelationshipStatus',
    'MemoryType',
    'MilestoneType',
    'BackupType',
    'BackupStatus',
    'User',
    'Session',
    'Conversation',
    'Memory',
    'Relationship',
    'Preference',
    'Milestone',
    'Backup',
]
