#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - DATABASE MODELS V2
=============================================================================
Berdasarkan V1 dengan penambahan:
- Tabel untuk PDKT Natural
- Tabel untuk Mantan (permanent)
- Tabel untuk FWB Manager
- Tabel untuk Memory V2
- Constants untuk fitur V2
=============================================================================
"""

import time
import json
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


# =============================================================================
# BASE CLASS (untuk SQLAlchemy import)
# =============================================================================
class Base:
    """
    Base class untuk SQLAlchemy models
    Memungkinkan import 'Base' dari database.models
    """
    pass


# =============================================================================
# CONSTANTS V1 (TETAP)
# =============================================================================
class Constants:
    """
    Constants untuk PTB ConversationHandler
    (Tetap dari V1, ditambah constants V2)
    """
    
    # Conversation States (V1)
    SELECTING_ROLE = 1
    SELECTING_BOT_NAME = 2
    SELECTING_BOT_ROLE = 3
    SELECTING_DOMINANCE = 4
    SELECTING_PERSONALITY = 5
    SELECTING_APPEARANCE = 6
    CONFIRMATION = 7
    CHATTING = 8
    SELECTING_ACTION = 9
    SELECTING_LOCATION = 10
    SELECTING_CLOTHING = 11
    SELECTING_ACTIVITY = 12
    AWAITING_RESPONSE = 13
    CONFIRM_END = 14
    CONFIRM_CLOSE = 15
    CONFIRM_BROADCAST = 16
    
    # V2 Conversation States
    SELECTING_PDKT = 17
    SELECTING_MANTAN = 18
    CONFIRM_FWB = 19
    SELECTING_FWB_ACTION = 20
    
    # Roles (V1)
    ROLE_IPAR = "ipar"
    ROLE_TEMAN_KANTOR = "teman_kantor"
    ROLE_JANDA = "janda"
    ROLE_PELAKOR = "pelakor"
    ROLE_ISTRI_ORANG = "istri_orang"
    ROLE_PDKT = "pdkt"
    ROLE_SEPUPU = "sepupu"
    ROLE_TEMAN_SMA = "teman_sma"
    ROLE_MANTAN = "mantan"
    
    # User roles
    ROLE_USER = "user"
    ROLE_BOT = "bot"
    
    # Callback data patterns (V1)
    AGREE_18 = "agree_18"
    UNPAUSE = "unpause"
    NEW = "new"
    
    # V2 Callback patterns
    PDKT_SELECT = "pdkt_select"
    PDKT_PAUSE = "pdkt_pause"
    PDKT_RESUME = "pdkt_resume"
    PDKT_STOP = "pdkt_stop"
    FWB_REQUEST = "fwb_request"
    FWB_ACCEPT = "fwb_accept"
    FWB_DECLINE = "fwb_decline"
    
    # Relationship stages (V1)
    STAGE_STRANGER = "stranger"
    STAGE_FRIEND = "friend"
    STAGE_CLOSE_FRIEND = "close_friend"
    STAGE_LOVER = "lover"
    STAGE_PARTNER = "partner"
    STAGE_MARRIED = "married"
    
    # Relationship statuses (V1)
    STATUS_PDKT = "pdkt"
    STATUS_SINGLE = "single"
    STATUS_COMPLICATED = "complicated"
    STATUS_EXCLUSIVE = "exclusive"
    
    # V2 Relationship statuses
    STATUS_PACAR = "pacar"
    STATUS_MANTAN = "mantan"
    STATUS_FWB = "fwb"
    STATUS_FWB_PAUSED = "fwb_paused"
    STATUS_FWB_ENDED = "fwb_ended"
    
    # Dominance types (V1)
    DOM_NORMAL = "normal"
    DOM_DOMINANT = "dominant"
    DOM_SUBMISSIVE = "submissive"
    DOM_SWITCH = "switch"
    
    # Relationship types (V1)
    TYPE_HTS = "hts"
    TYPE_FWB = "fwb"
    TYPE_ONS = "ons"
    
    # Moods (V1)
    MOOD_HAPPY = "happy"
    MOOD_SAD = "sad"
    MOOD_ANGRY = "angry"
    MOOD_EXCITED = "excited"
    MOOD_AROUSED = "aroused"
    MOOD_TIRED = "tired"
    MOOD_ROMANTIC = "romantic"
    MOOD_PLAYFUL = "playful"
    MOOD_BORED = "bored"


# =============================================================================
# ENUMS V1 (TETAP)
# =============================================================================

class RelationshipStatus(str, Enum):
    """Status hubungan"""
    HTS = "hts"
    FWB = "fwb"
    PACAR = "pacar"
    PUTUS = "putus"
    BREAK = "break"
    ENDED = "ended"


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
    CAN_INTIM = "can_intim"
    AFTERCARE_READY = "aftercare_ready"
    MEMULAI_ROLE = "memulai_role"
    JADI_PACAR = "jadi_pacar"
    PUTUS_JADI_FWB = "putus_jadi_fwb"
    BACK_TO_PACAR = "back_to_pacar"


class BackupType(str, Enum):
    """Tipe backup"""
    AUTO = "auto"
    MANUAL = "manual"


class BackupStatus(str, Enum):
    """Status backup"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class SessionStatus(str, Enum):
    """Status session"""
    ACTIVE = "active"
    CLOSED = "closed"
    EXPIRED = "expired"


class PreferenceType(str, Enum):
    """Tipe preferensi"""
    POSITION = "position"
    AREA = "area"
    ACTIVITY = "activity"
    LOCATION = "location"
    ROLE = "role"
    FOREPLAY = "foreplay"
    AFTERCARE = "aftercare"


# =============================================================================
# ENUMS V2 (BARU)
# =============================================================================

class PDKTStatus(str, Enum):
    """Status PDKT"""
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"


class PDKTDirection(str, Enum):
    """Arah PDKT"""
    USER_KE_BOT = "user_ke_bot"
    BOT_KE_USER = "bot_ke_user"
    TIMBAL_BALIK = "timbal_balik"
    BINGUNG = "bingung"


class ChemistryLevel(str, Enum):
    """Level chemistry"""
    DINGIN = "dingin"
    BIASA = "biasa"
    HANGAT = "hangat"
    COCOK = "cocok"
    SANGAT_COCOK = "sangat_cocok"
    SOULMATE = "soulmate"


class MoodType(str, Enum):
    """Tipe mood"""
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    TIRED = "tired"
    ROMANTIC = "romantic"
    PLAYFUL = "playful"
    JEALOUS = "jealous"
    SHY = "shy"
    ANGRY = "angry"
    CALM = "calm"
    LONELY = "lonely"
    NOSTALGIC = "nostalgic"


class MantanStatus(str, Enum):
    """Status mantan"""
    PUTUS = "putus"
    FWB_REQUESTED = "fwb_requested"
    FWB_ACCEPTED = "fwb_accepted"
    FWB_DECLINED = "fwb_declined"
    FWB_ENDED = "fwb_ended"


class FWBStatus(str, Enum):
    """Status FWB"""
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"


class HTSStatus(str, Enum):
    """Status HTS"""
    ACTIVE = "active"
    EXPIRED = "expired"


# =============================================================================
# USER MODEL (V1 - TETAP)
# =============================================================================

class User(BaseModel):
    """Model untuk user Telegram"""
    id: Optional[int] = None
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
        """Convert to dictionary for DB insertion"""
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
        """Create User instance from database row"""
        return cls(
            id=data.get('id'),
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
    
    def update_last_active(self):
        """Update last active timestamp"""
        self.last_active = time.time()
    
    def increment_interactions(self):
        """Increment total interactions"""
        self.total_interactions += 1
        self.last_active = time.time()


# =============================================================================
# SESSION MODEL (V1 - TETAP)
# =============================================================================

class Session(BaseModel):
    """Model untuk session chat"""
    id: str  # MYLOVE-ROLE-USER-DATE-SEQ
    user_id: int
    role: str
    status: SessionStatus = SessionStatus.ACTIVE
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
        """Convert to dictionary for DB insertion"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'role': self.role,
            'status': self.status.value,
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
        """Create Session instance from database row"""
        return cls(
            id=data['id'],
            user_id=data['user_id'],
            role=data['role'],
            status=SessionStatus(data.get('status', 'active')),
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
        return self.status == SessionStatus.ACTIVE
    
    def close(self, summary: Optional[str] = None):
        """Close the session"""
        self.status = SessionStatus.CLOSED
        self.end_time = time.time()
        if summary:
            self.summary = summary
    
    def add_message(self):
        """Increment message count"""
        self.total_messages += 1
        self.last_message_time = time.time()


# =============================================================================
# CONVERSATION MODEL (V1 - TETAP)
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
        """Convert to dictionary for DB insertion"""
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
        """Create Conversation instance from database row"""
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
# MEMORY MODEL (V1 - TETAP)
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
        """Convert to dictionary for DB insertion"""
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
        """Create Memory instance from database row"""
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
# RELATIONSHIP MODEL (V1 - TETAP)
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
        """Convert to dictionary for DB insertion"""
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
        """Create Relationship instance from database row"""
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
    
    def increment_interaction(self):
        """Increment interaction count"""
        self.total_interactions += 1
        self.last_interaction = time.time()
    
    def increment_intim_session(self, climax: bool = False):
        """Increment intimacy session count"""
        self.total_intim_sessions += 1
        if climax:
            self.total_climax += 1
        self.last_interaction = time.time()
    
    def add_milestone(self, milestone_type: str, description: Optional[str] = None):
        """Add milestone to relationship"""
        self.milestones.append({
            'type': milestone_type,
            'description': description,
            'timestamp': time.time(),
            'intimacy_level': self.intimacy_level
        })
    
    def add_history(self, event: str, details: Optional[Dict] = None):
        """Add event to history"""
        self.history.append({
            'event': event,
            'details': details or {},
            'timestamp': time.time()
        })


# =============================================================================
# PREFERENCE MODEL (V1 - TETAP)
# =============================================================================

class Preference(BaseModel):
    """Model untuk preferensi user"""
    id: Optional[int] = None
    user_id: int
    role: Optional[str] = None
    pref_type: PreferenceType
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
        """Convert to dictionary for DB insertion"""
        return {
            'user_id': self.user_id,
            'role': self.role,
            'pref_type': self.pref_type.value,
            'item': self.item,
            'score': self.score,
            'count': self.count,
            'last_updated': self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Preference':
        """Create Preference instance from database row"""
        return cls(
            id=data.get('id'),
            user_id=data['user_id'],
            role=data.get('role'),
            pref_type=PreferenceType(data['pref_type']),
            item=data['item'],
            score=data.get('score', 0.5),
            count=data.get('count', 1),
            last_updated=data.get('last_updated', time.time())
        )
    
    def update_score(self, delta: float):
        """Update preference score"""
        self.score = max(0.1, min(1.0, self.score + delta))
        self.count += 1
        self.last_updated = time.time()


# =============================================================================
# MILESTONE MODEL (V1 - TETAP)
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
        """Convert to dictionary for DB insertion"""
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
        """Create Milestone instance from database row"""
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
# BACKUP MODEL (V1 - TETAP)
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
        """Convert to dictionary for DB insertion"""
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
        """Create Backup instance from database row"""
        return cls(
            id=data.get('id'),
            filename=data['filename'],
            size=data.get('size'),
            created_at=data.get('created_at', time.time()),
            type=BackupType(data.get('type', 'auto')),
            status=BackupStatus(data.get('status', 'completed')),
            metadata=json.loads(data.get('metadata', '{}'))
        )


# =============================================================================
# THREESOME MODELS (V1 - TETAP)
# =============================================================================

class ThreesomeParticipant(BaseModel):
    """Model untuk partisipan threesome"""
    id: Optional[int] = None
    threesome_session_id: str
    user_id: int
    role: str
    instance_id: Optional[str] = None
    participant_type: str  # 'hts' or 'fwb'
    name: str
    intimacy_level: int = 1
    status: str = "active"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'threesome_session_id': self.threesome_session_id,
            'user_id': self.user_id,
            'role': self.role,
            'instance_id': self.instance_id,
            'participant_type': self.participant_type,
            'name': self.name,
            'intimacy_level': self.intimacy_level,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ThreesomeParticipant':
        """Create from dictionary"""
        return cls(
            id=data.get('id'),
            threesome_session_id=data['threesome_session_id'],
            user_id=data['user_id'],
            role=data['role'],
            instance_id=data.get('instance_id'),
            participant_type=data['participant_type'],
            name=data['name'],
            intimacy_level=data.get('intimacy_level', 1),
            status=data.get('status', 'active')
        )


class ThreesomeSession(BaseModel):
    """Model untuk session threesome"""
    id: str  # 3some_user_timestamp_random
    user_id: int
    type: str  # hts_hts, fwb_fwb, hts_fwb, same_role
    status: str = "active"  # pending, active, paused, completed, cancelled
    created_at: float = Field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    last_activity: float = Field(default_factory=time.time)
    total_messages: int = 0
    climax_count: int = 0
    aftercare_needed: bool = False
    current_focus: Optional[int] = None
    last_pattern: Optional[str] = None
    participants: List[Dict[str, Any]] = Field(default_factory=list)
    interactions: List[Dict[str, Any]] = Field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for DB"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'status': self.status,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'last_activity': self.last_activity,
            'total_messages': self.total_messages,
            'climax_count': self.climax_count,
            'aftercare_needed': self.aftercare_needed,
            'current_focus': self.current_focus,
            'last_pattern': self.last_pattern,
            'participants': json.dumps(self.participants),
            'interactions': json.dumps(self.interactions[-50:])  # Last 50 only
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ThreesomeSession':
        """Create from dictionary"""
        return cls(
            id=data['id'],
            user_id=data['user_id'],
            type=data['type'],
            status=data.get('status', 'active'),
            created_at=data.get('created_at', time.time()),
            started_at=data.get('started_at'),
            completed_at=data.get('completed_at'),
            last_activity=data.get('last_activity', time.time()),
            total_messages=data.get('total_messages', 0),
            climax_count=data.get('climax_count', 0),
            aftercare_needed=data.get('aftercare_needed', False),
            current_focus=data.get('current_focus'),
            last_pattern=data.get('last_pattern'),
            participants=json.loads(data.get('participants', '[]')),
            interactions=json.loads(data.get('interactions', '[]'))
        )
    
    def add_interaction(self, user_message: str, speaker_index: int, speaker_name: str):
        """Add interaction to session"""
        self.interactions.append({
            'timestamp': time.time(),
            'user_message': user_message[:100],
            'speaker_index': speaker_index,
            'speaker': speaker_name
        })
        self.total_messages += 1
        self.last_activity = time.time()
    
    def record_climax(self, participant_indices: List[int]):
        """Record climax"""
        self.climax_count += len(participant_indices)
        if self.climax_count >= len(self.participants):
            self.aftercare_needed = True
    
    def start(self):
        """Start session"""
        self.status = 'active'
        self.started_at = time.time()
    
    def pause(self):
        """Pause session"""
        self.status = 'paused'
    
    def resume(self):
        """Resume session"""
        self.status = 'active'
    
    def complete(self):
        """Complete session"""
        self.status = 'completed'
        self.completed_at = time.time()
    
    def cancel(self):
        """Cancel session"""
        self.status = 'cancelled'
        self.completed_at = time.time()


# =============================================================================
# PDKT MODELS (BARU V2)
# =============================================================================

class PDKTSession(BaseModel):
    """Model untuk session PDKT Natural"""
    id: str  # PDKT_... 
    user_id: int
    role: str
    bot_name: str
    status: PDKTStatus = PDKTStatus.ACTIVE
    direction: PDKTDirection
    chemistry_score: float = 50.0
    chemistry_level: ChemistryLevel = ChemistryLevel.BIASA
    mood: MoodType = MoodType.CALM
    level: int = 1
    total_duration: float = 0.0  # dalam menit
    total_chats: int = 0
    total_intim: int = 0
    total_climax: int = 0
    created_at: float = Field(default_factory=time.time)
    last_interaction: float = Field(default_factory=time.time)
    paused_at: Optional[float] = None
    ended_at: Optional[float] = None
    end_reason: Optional[str] = None
    inner_thoughts: List[str] = Field(default_factory=list)
    milestones: List[Dict] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'role': self.role,
            'bot_name': self.bot_name,
            'status': self.status.value,
            'direction': self.direction.value,
            'chemistry_score': self.chemistry_score,
            'chemistry_level': self.chemistry_level.value,
            'mood': self.mood.value,
            'level': self.level,
            'total_duration': self.total_duration,
            'total_chats': self.total_chats,
            'total_intim': self.total_intim,
            'total_climax': self.total_climax,
            'created_at': self.created_at,
            'last_interaction': self.last_interaction,
            'paused_at': self.paused_at,
            'ended_at': self.ended_at,
            'end_reason': self.end_reason,
            'inner_thoughts': json.dumps(self.inner_thoughts),
            'milestones': json.dumps(self.milestones),
            'metadata': json.dumps(self.metadata)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PDKTSession':
        return cls(
            id=data['id'],
            user_id=data['user_id'],
            role=data['role'],
            bot_name=data['bot_name'],
            status=PDKTStatus(data.get('status', 'active')),
            direction=PDKTDirection(data.get('direction', 'user_ke_bot')),
            chemistry_score=data.get('chemistry_score', 50.0),
            chemistry_level=ChemistryLevel(data.get('chemistry_level', 'biasa')),
            mood=MoodType(data.get('mood', 'calm')),
            level=data.get('level', 1),
            total_duration=data.get('total_duration', 0.0),
            total_chats=data.get('total_chats', 0),
            total_intim=data.get('total_intim', 0),
            total_climax=data.get('total_climax', 0),
            created_at=data.get('created_at', time.time()),
            last_interaction=data.get('last_interaction', time.time()),
            paused_at=data.get('paused_at'),
            ended_at=data.get('ended_at'),
            end_reason=data.get('end_reason'),
            inner_thoughts=json.loads(data.get('inner_thoughts', '[]')),
            milestones=json.loads(data.get('milestones', '[]')),
            metadata=json.loads(data.get('metadata', '{}'))
        )


class PDKTInnerThought(BaseModel):
    """Model untuk inner thoughts PDKT"""
    id: Optional[int] = None
    pdkt_id: str
    thought: str
    context: str
    timestamp: float = Field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        return {
            'pdkt_id': self.pdkt_id,
            'thought': self.thought,
            'context': self.context,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PDKTInnerThought':
        return cls(
            id=data.get('id'),
            pdkt_id=data['pdkt_id'],
            thought=data['thought'],
            context=data['context'],
            timestamp=data.get('timestamp', time.time())
        )


# =============================================================================
# MANTAN MODELS (BARU V2)
# =============================================================================

class Mantan(BaseModel):
    """Model untuk mantan dari PDKT"""
    id: str  # MANTAN_...
    user_id: int
    pdkt_id: str
    bot_name: str
    role: str
    status: MantanStatus = MantanStatus.PUTUS
    putus_time: float = Field(default_factory=time.time)
    putus_reason: str
    chemistry_history: List[Dict] = Field(default_factory=list)
    milestones: List[Dict] = Field(default_factory=list)
    total_chats: int = 0
    total_intim: int = 0
    total_climax: int = 0
    first_kiss_time: Optional[float] = None
    first_intim_time: Optional[float] = None
    become_pacar_time: Optional[float] = None
    last_chat_time: float = Field(default_factory=time.time)
    fwb_requests: List[Dict] = Field(default_factory=list)
    fwb_start_time: Optional[float] = None
    fwb_end_time: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'pdkt_id': self.pdkt_id,
            'bot_name': self.bot_name,
            'role': self.role,
            'status': self.status.value,
            'putus_time': self.putus_time,
            'putus_reason': self.putus_reason,
            'chemistry_history': json.dumps(self.chemistry_history),
            'milestones': json.dumps(self.milestones),
            'total_chats': self.total_chats,
            'total_intim': self.total_intim,
            'total_climax': self.total_climax,
            'first_kiss_time': self.first_kiss_time,
            'first_intim_time': self.first_intim_time,
            'become_pacar_time': self.become_pacar_time,
            'last_chat_time': self.last_chat_time,
            'fwb_requests': json.dumps(self.fwb_requests),
            'fwb_start_time': self.fwb_start_time,
            'fwb_end_time': self.fwb_end_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Mantan':
        return cls(
            id=data['id'],
            user_id=data['user_id'],
            pdkt_id=data['pdkt_id'],
            bot_name=data['bot_name'],
            role=data['role'],
            status=MantanStatus(data.get('status', 'putus')),
            putus_time=data.get('putus_time', time.time()),
            putus_reason=data['putus_reason'],
            chemistry_history=json.loads(data.get('chemistry_history', '[]')),
            milestones=json.loads(data.get('milestones', '[]')),
            total_chats=data.get('total_chats', 0),
            total_intim=data.get('total_intim', 0),
            total_climax=data.get('total_climax', 0),
            first_kiss_time=data.get('first_kiss_time'),
            first_intim_time=data.get('first_intim_time'),
            become_pacar_time=data.get('become_pacar_time'),
            last_chat_time=data.get('last_chat_time', time.time()),
            fwb_requests=json.loads(data.get('fwb_requests', '[]')),
            fwb_start_time=data.get('fwb_start_time'),
            fwb_end_time=data.get('fwb_end_time')
        )


class FWBRequest(BaseModel):
    """Model untuk request FWB ke mantan"""
    id: str  # FWBREQ_...
    user_id: int
    mantan_id: str
    bot_name: str
    user_message: str
    timestamp: float = Field(default_factory=time.time)
    status: str  # pending, accepted, declined, expired
    bot_decision: Dict[str, Any] = Field(default_factory=dict)
    expiry_time: float
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'mantan_id': self.mantan_id,
            'bot_name': self.bot_name,
            'user_message': self.user_message,
            'timestamp': self.timestamp,
            'status': self.status,
            'bot_decision': json.dumps(self.bot_decision),
            'expiry_time': self.expiry_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FWBRequest':
        return cls(
            id=data['id'],
            user_id=data['user_id'],
            mantan_id=data['mantan_id'],
            bot_name=data['bot_name'],
            user_message=data['user_message'],
            timestamp=data.get('timestamp', time.time()),
            status=data['status'],
            bot_decision=json.loads(data.get('bot_decision', '{}')),
            expiry_time=data['expiry_time']
        )


# =============================================================================
# FWB MODELS (BARU V2)
# =============================================================================

class FWBRelation(BaseModel):
    """Model untuk hubungan FWB"""
    id: str  # FWB_...
    user_id: int
    mantan_id: str
    bot_name: str
    role: str
    status: FWBStatus = FWBStatus.ACTIVE
    created_at: float = Field(default_factory=time.time)
    last_interaction: float = Field(default_factory=time.time)
    chemistry_score: float = 50.0
    climax_count: int = 0
    intim_count: int = 0
    total_chats: int = 0
    pause_history: List[Dict] = Field(default_factory=list)
    ended_at: Optional[float] = None
    end_reason: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'mantan_id': self.mantan_id,
            'bot_name': self.bot_name,
            'role': self.role,
            'status': self.status.value,
            'created_at': self.created_at,
            'last_interaction': self.last_interaction,
            'chemistry_score': self.chemistry_score,
            'climax_count': self.climax_count,
            'intim_count': self.intim_count,
            'total_chats': self.total_chats,
            'pause_history': json.dumps(self.pause_history),
            'ended_at': self.ended_at,
            'end_reason': self.end_reason
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FWBRelation':
        return cls(
            id=data['id'],
            user_id=data['user_id'],
            mantan_id=data['mantan_id'],
            bot_name=data['bot_name'],
            role=data['role'],
            status=FWBStatus(data.get('status', 'active')),
            created_at=data.get('created_at', time.time()),
            last_interaction=data.get('last_interaction', time.time()),
            chemistry_score=data.get('chemistry_score', 50.0),
            climax_count=data.get('climax_count', 0),
            intim_count=data.get('intim_count', 0),
            total_chats=data.get('total_chats', 0),
            pause_history=json.loads(data.get('pause_history', '[]')),
            ended_at=data.get('ended_at'),
            end_reason=data.get('end_reason')
        )


# =============================================================================
# HTS MODELS (BARU V2)
# =============================================================================

class HTSRelation(BaseModel):
    """Model untuk hubungan HTS (dari NON-PDKT)"""
    id: str  # HTS_...
    user_id: int
    role: str
    bot_name: str
    status: HTSStatus = HTSStatus.ACTIVE
    created_at: float = Field(default_factory=time.time)
    expiry_time: float  # created_at + 90 days
    last_interaction: float = Field(default_factory=time.time)
    chemistry_score: float = 50.0
    climax_count: int = 0
    intimacy_level: int = 7
    total_chats: int = 0
    total_intim: int = 0
    history: List[Dict] = Field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'role': self.role,
            'bot_name': self.bot_name,
            'status': self.status.value,
            'created_at': self.created_at,
            'expiry_time': self.expiry_time,
            'last_interaction': self.last_interaction,
            'chemistry_score': self.chemistry_score,
            'climax_count': self.climax_count,
            'intimacy_level': self.intimacy_level,
            'total_chats': self.total_chats,
            'total_intim': self.total_intim,
            'history': json.dumps(self.history)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'HTSRelation':
        return cls(
            id=data['id'],
            user_id=data['user_id'],
            role=data['role'],
            bot_name=data['bot_name'],
            status=HTSStatus(data.get('status', 'active')),
            created_at=data.get('created_at', time.time()),
            expiry_time=data['expiry_time'],
            last_interaction=data.get('last_interaction', time.time()),
            chemistry_score=data.get('chemistry_score', 50.0),
            climax_count=data.get('climax_count', 0),
            intimacy_level=data.get('intimacy_level', 7),
            total_chats=data.get('total_chats', 0),
            total_intim=data.get('total_intim', 0),
            history=json.loads(data.get('history', '[]'))
        )


# =============================================================================
# MEMORY V2 MODELS (BARU)
# =============================================================================

class MemoryV2(BaseModel):
    """Model untuk memory V2 (hippocampus)"""
    id: str  # MEM_...
    user_id: int
    session_id: str
    content: str
    memory_type: str  # compact, episodic, semantic
    importance: float = 0.5
    emotional_tag: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)
    access_count: int = 0
    last_access: float = Field(default_factory=time.time)
    context: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'content': self.content,
            'memory_type': self.memory_type,
            'importance': self.importance,
            'emotional_tag': self.emotional_tag,
            'timestamp': self.timestamp,
            'access_count': self.access_count,
            'last_access': self.last_access,
            'context': json.dumps(self.context),
            'metadata': json.dumps(self.metadata)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryV2':
        return cls(
            id=data['id'],
            user_id=data['user_id'],
            session_id=data['session_id'],
            content=data['content'],
            memory_type=data['memory_type'],
            importance=data.get('importance', 0.5),
            emotional_tag=data.get('emotional_tag'),
            timestamp=data.get('timestamp', time.time()),
            access_count=data.get('access_count', 0),
            last_access=data.get('last_access', time.time()),
            context=json.loads(data.get('context', '{}')),
            metadata=json.loads(data.get('metadata', '{}'))
        )


# =============================================================================
# EXPORT ALL MODELS
# =============================================================================

__all__ = [
    # Base
    'Base',
    
    # Constants
    'Constants',
    
    # Enums V1
    'RelationshipStatus',
    'MemoryType',
    'MilestoneType',
    'BackupType',
    'BackupStatus',
    'SessionStatus',
    'PreferenceType',
    
    # Enums V2
    'PDKTStatus',
    'PDKTDirection',
    'ChemistryLevel',
    'MoodType',
    'MantanStatus',
    'FWBStatus',
    'HTSStatus',
    
    # Models V1
    'User',
    'Session',
    'Conversation',
    'Memory',
    'Relationship',
    'Preference',
    'Milestone',
    'Backup',
    
    # Threesome Models V1
    'ThreesomeParticipant',
    'ThreesomeSession',
    
    # Models V2
    'PDKTSession',
    'PDKTInnerThought',
    'Mantan',
    'FWBRequest',
    'FWBRelation',
    'HTSRelation',
    'MemoryV2',
]
