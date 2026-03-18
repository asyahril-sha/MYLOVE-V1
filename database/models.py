#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - DATABASE MODELS (FIX FULL + PDKT)
=============================================================================
- Data models untuk semua entitas
- Pydantic models untuk validasi
- SQLAlchemy Base class untuk import
- PLUS Constants class untuk PTB ConversationHandler
- **TAMBAHAN: Tabel untuk PDKT dengan dual leveling system**
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
# CONSTANTS UNTUK PTB CONVERSATION HANDLER
# =============================================================================
class Constants:
    """
    Constants untuk PTB ConversationHandler
    Class ini yang di-import oleh bot.application.py
    """
    
    # Conversation States
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
    
    # Roles
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
    
    # Callback data patterns
    AGREE_18 = "agree_18"
    UNPAUSE = "unpause"
    NEW = "new"
    
    # Relationship stages
    STAGE_STRANGER = "stranger"
    STAGE_FRIEND = "friend"
    STAGE_CLOSE_FRIEND = "close_friend"
    STAGE_LOVER = "lover"
    STAGE_PARTNER = "partner"
    STAGE_MARRIED = "married"
    
    # Relationship statuses
    STATUS_PDKT = "pdkt"
    STATUS_SINGLE = "single"
    STATUS_COMPLICATED = "complicated"
    STATUS_EXCLUSIVE = "exclusive"
    
    # Dominance types
    DOM_NORMAL = "normal"
    DOM_DOMINANT = "dominant"
    DOM_SUBMISSIVE = "submissive"
    DOM_SWITCH = "switch"
    
    # Relationship types
    TYPE_HTS = "hts"
    TYPE_FWB = "fwb"
    TYPE_ONS = "ons"
    
    # Moods
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
# ENUMS
# =============================================================================

class RelationshipStatus(str, Enum):
    """Status hubungan"""
    HTS = "hts"
    FWB = "fwb"
    PACAR = "pacar"
    PUTUS = "putus"
    BREAK = "break"
    ENDED = "ended"


class PDKTStatus(str, Enum):
    """Status PDKT"""
    ACTIVE = "active"      # Sedang berjalan
    PAUSED = "paused"      # Di-pause
    STOPPED = "stopped"    # Dihentikan (putus)
    COMPLETED = "completed" # Jadi pacar


class PDKTDirection(str, Enum):
    """Arah PDKT"""
    USER_TO_BOT = "user_to_bot"   # User yang ngejar
    BOT_TO_USER = "bot_to_user"   # Bot yang ngejar
    MUTUAL = "mutual"              # Saling suka
    CONFUSED = "confused"          # Bingung


class PDKTStage(str, Enum):
    """Tahapan PDKT"""
    MENGENAL = "mengenal"
    DEKAT = "dekat"
    AKRAB = "akrab"
    SPESIAL = "spesial"
    JATUH_CINTA = "jatuh_cinta"
    PACAR = "pacar"


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
# USER MODEL
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
# SESSION MODEL
# =============================================================================

class Session(BaseModel):
    """Model untuk session chat"""
    id: str  # MYLOVE-NAMA_BOT-ROLE-USER-DATE-SEQ
    user_id: int
    bot_name: str  # Nama bot yang dipilih
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
            'bot_name': self.bot_name,
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
            bot_name=data.get('bot_name', 'Aurora'),
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
# CONVERSATION MODEL
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
# MEMORY MODEL
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
# RELATIONSHIP MODEL (HTS/FWB)
# =============================================================================

class Relationship(BaseModel):
    """Model untuk hubungan (HTS/FWB/Pacar)"""
    id: Optional[int] = None
    user_id: int
    bot_name: str
    role: str
    instance_id: Optional[str] = None
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
            'bot_name': self.bot_name,
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
            bot_name=data.get('bot_name', 'Aurora'),
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
        """Get display name for relationship with nama bot"""
        if self.instance_id:
            return f"{self.bot_name} ({self.role}) #{self.instance_id[-4:]}"
        return f"{self.bot_name} ({self.role})"
    
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
# PDKT MODEL (BARU)
# =============================================================================

class PDKT(BaseModel):
    """Model untuk PDKT Super Spesial"""
    id: str  # PDKT001_12345678_1710873600
    user_id: int
    bot_name: str
    role: str = "pdkt"
    
    # Status
    status: PDKTStatus = PDKTStatus.ACTIVE
    is_paused: bool = False
    paused_at: Optional[float] = None
    
    # Arah dan tahap
    direction: PDKTDirection
    stage: PDKTStage = PDKTStage.MENGENAL
    level: int = 1
    
    # Chemistry (disimpan sebagai JSON)
    chemistry_score: float = 50.0
    chemistry_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Waktu
    created_at: float = Field(default_factory=time.time)
    last_interaction: float = Field(default_factory=time.time)
    total_minutes: float = 0.0  # Total waktu aktif (exclude pause)
    paused_total: float = 0.0    # Total waktu di-pause
    
    # Interaksi
    total_chats: int = 0
    total_intim: int = 0
    total_climax: int = 0
    
    # Milestones
    milestones: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Inner thoughts (pikiran dalam hati bot)
    inner_thoughts: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    ended_at: Optional[float] = None
    end_reason: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for DB insertion"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'bot_name': self.bot_name,
            'role': self.role,
            'status': self.status.value,
            'is_paused': 1 if self.is_paused else 0,
            'paused_at': self.paused_at,
            'direction': self.direction.value,
            'stage': self.stage.value,
            'level': self.level,
            'chemistry_score': self.chemistry_score,
            'chemistry_history': json.dumps(self.chemistry_history),
            'created_at': self.created_at,
            'last_interaction': self.last_interaction,
            'total_minutes': self.total_minutes,
            'paused_total': self.paused_total,
            'total_chats': self.total_chats,
            'total_intim': self.total_intim,
            'total_climax': self.total_climax,
            'milestones': json.dumps(self.milestones),
            'inner_thoughts': json.dumps(self.inner_thoughts),
            'ended_at': self.ended_at,
            'end_reason': self.end_reason
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PDKT':
        """Create PDKT instance from database row"""
        return cls(
            id=data['id'],
            user_id=data['user_id'],
            bot_name=data['bot_name'],
            role=data.get('role', 'pdkt'),
            status=PDKTStatus(data.get('status', 'active')),
            is_paused=bool(data.get('is_paused', 0)),
            paused_at=data.get('paused_at'),
            direction=PDKTDirection(data.get('direction', 'user_to_bot')),
            stage=PDKTStage(data.get('stage', 'mengenal')),
            level=data.get('level', 1),
            chemistry_score=data.get('chemistry_score', 50.0),
            chemistry_history=json.loads(data.get('chemistry_history', '[]')),
            created_at=data.get('created_at', time.time()),
            last_interaction=data.get('last_interaction', time.time()),
            total_minutes=data.get('total_minutes', 0.0),
            paused_total=data.get('paused_total', 0.0),
            total_chats=data.get('total_chats', 0),
            total_intim=data.get('total_intim', 0),
            total_climax=data.get('total_climax', 0),
            milestones=json.loads(data.get('milestones', '[]')),
            inner_thoughts=json.loads(data.get('inner_thoughts', '[]')),
            ended_at=data.get('ended_at'),
            end_reason=data.get('end_reason')
        )
    
    def get_chemistry_vibe(self) -> str:
        """Dapatkan vibe chemistry"""
        if self.chemistry_score >= 80:
            return "Soulmate ✨"
        elif self.chemistry_score >= 60:
            return "Sangat Cocok 💞"
        elif self.chemistry_score >= 40:
            return "Cocok 💕"
        elif self.chemistry_score >= 20:
            return "Biasa 😐"
        else:
            return "Dingin ❄️"
    
    def get_direction_text(self) -> str:
        """Dapatkan teks arah hubungan"""
        texts = {
            PDKTDirection.USER_TO_BOT: "Kamu yang ngejar",
            PDKTDirection.BOT_TO_USER: "Dia yang ngejar",
            PDKTDirection.MUTUAL: "Saling suka",
            PDKTDirection.CONFUSED: "Masih bingung",
        }
        return texts.get(self.direction, "?")
    
    def get_stage_text(self) -> str:
        """Dapatkan teks tahapan"""
        texts = {
            PDKTStage.MENGENAL: "Mengenal",
            PDKTStage.DEKAT: "Mulai Dekat",
            PDKTStage.AKRAB: "Akrab",
            PDKTStage.SPESIAL: "Spesial",
            PDKTStage.JATUH_CINTA: "Jatuh Cinta",
            PDKTStage.PACAR: "PACAR!",
        }
        return texts.get(self.stage, self.stage.value)


# =============================================================================
# PREFERENCE MODEL
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
# MILESTONE MODEL
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
# BACKUP MODEL
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
# THREESOME MODELS
# =============================================================================

class ThreesomeParticipant(BaseModel):
    """Model untuk partisipan threesome"""
    id: Optional[int] = None
    threesome_session_id: str
    user_id: int
    bot_name: str
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
            'bot_name': self.bot_name,
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
            bot_name=data.get('bot_name', 'Aurora'),
            role=data['role'],
            instance_id=data.get('instance_id'),
            participant_type=data['participant_type'],
            name=data['name'],
            intimacy_level=data.get('intimacy_level', 1),
            status=data.get('status', 'active')
        )


class ThreesomeSession(BaseModel):
    """Model untuk session threesome"""
    id: str
    user_id: int
    type: str
    status: str = "active"
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
            'aftercare_needed': 1 if self.aftercare_needed else 0,
            'current_focus': self.current_focus,
            'last_pattern': self.last_pattern,
            'participants': json.dumps(self.participants),
            'interactions': json.dumps(self.interactions[-50:])
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
            aftercare_needed=bool(data.get('aftercare_needed', 0)),
            current_focus=data.get('current_focus'),
            last_pattern=data.get('last_pattern'),
            participants=json.loads(data.get('participants', '[]')),
            interactions=json.loads(data.get('interactions', '[]'))
        )


# =============================================================================
# EXPORT ALL MODELS
# =============================================================================

__all__ = [
    # Base
    'Base',
    
    # Constants (PENTING: ini yang di-import oleh bot.application)
    'Constants',
    
    # Enums
    'RelationshipStatus',
    'PDKTStatus',
    'PDKTDirection',
    'PDKTStage',
    'MemoryType',
    'MilestoneType',
    'BackupType',
    'BackupStatus',
    'SessionStatus',
    'PreferenceType',
    
    # Main Models
    'User',
    'Session',
    'Conversation',
    'Memory',
    'Relationship',
    'PDKT',  # BARU
    'Preference',
    'Milestone',
    'Backup',
    
    # Threesome Models
    'ThreesomeParticipant',
    'ThreesomeSession',
]
