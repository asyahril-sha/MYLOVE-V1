#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - KONFIGURASI UTAMA (FIXED)
=============================================================================
Menggunakan Pydantic untuk validasi dan type safety
Semua konfigurasi terpusat di sini
"""

import os
from typing import Optional, Dict, Any, List
from pydantic import Field, validator, BaseModel
from pydantic_settings import BaseSettings
from pathlib import Path
import secrets
from datetime import timedelta


# =============================================================================
# DATABASE SETTINGS
# =============================================================================
class DatabaseSettings(BaseModel):
    """Konfigurasi database - SQLite untuk single user"""
    type: str = Field("sqlite", env='DB_TYPE')
    path: Path = Field(Path("data/mylove.db"), env='DB_PATH')
    pool_size: int = Field(5, env='DB_POOL_SIZE')
    timeout: int = Field(30, env='DB_TIMEOUT')
    
    @validator('type')
    def validate_db_type(cls, v):
        if v not in ["sqlite", "postgresql"]:
            raise ValueError("DB_TYPE harus sqlite atau postgresql")
        return v
    
    @property
    def url(self) -> str:
        """Get database URL"""
        if self.type == "sqlite":
            return f"sqlite+aiosqlite:///{self.path}"
        return f"postgresql://..."


# =============================================================================
# AI SETTINGS - DEEPSEEK
# =============================================================================
class AISettings(BaseModel):
    """Konfigurasi AI DeepSeek"""
    temperature: float = Field(0.9, env='AI_TEMPERATURE')
    max_tokens: int = Field(500, env='AI_MAX_TOKENS')
    timeout: int = Field(30, env='AI_TIMEOUT')
    model: str = Field("deepseek-chat", env='AI_MODEL')
    
    # Response length constraints
    min_message_length: int = Field(1000, env='MIN_MESSAGE_LENGTH')
    max_message_length: int = Field(3000, env='MAX_MESSAGE_LENGTH')
    response_timeout: int = Field(5, env='RESPONSE_TIMEOUT')
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if v < 0 or v > 1:
            raise ValueError("Temperature must be between 0 and 1")
        return v
    
    @validator('max_tokens')
    def validate_max_tokens(cls, v):
        if v < 100 or v > 2000:
            raise ValueError("max_tokens harus antara 100-2000")
        return v


# =============================================================================
# WEBHOOK SETTINGS - HYBRID MODE
# =============================================================================
class WebhookSettings(BaseModel):
    """Konfigurasi webhook dengan retry mechanism"""
    url: Optional[str] = Field(None, env='WEBHOOK_URL')
    port: int = Field(8080, env='PORT')
    path: str = Field("/webhook", env='WEBHOOK_PATH')
    secret_token: Optional[str] = Field(None, env='WEBHOOK_SECRET')
    
    # Retry mechanism
    max_retries: int = Field(5, env='WEBHOOK_MAX_RETRIES')
    retry_backoff: int = Field(2, env='WEBHOOK_RETRY_BACKOFF')
    
    # Fallback to polling
    enable_polling_fallback: bool = Field(True, env='ENABLE_POLLING_FALLBACK')
    
    @property
    def base_url(self) -> str:
        """Get base URL for webhook"""
        if self.url:
            return self.url.rstrip('/')
        return f"http://localhost:{self.port}"


# =============================================================================
# RAILWAY SETTINGS
# =============================================================================
class RailwaySettings(BaseModel):
    """Konfigurasi Railway deployment"""
    public_domain: Optional[str] = Field(None, env='RAILWAY_PUBLIC_DOMAIN')
    static_url: Optional[str] = Field(None, env='RAILWAY_STATIC_URL')
    
    @property
    def public_url(self) -> str:
        """Get public URL for webhook"""
        if self.public_domain:
            return f"https://{self.public_domain}"
        return None


# =============================================================================
# INTIMACY LEVEL SYSTEM (1-12 + AFTERCARE)
# =============================================================================
class IntimacySettings(BaseModel):
    """Sistem level intimacy 1-12 dengan aftercare"""
    
    # Level definitions
    levels: Dict[int, Dict[str, Any]] = {
        1: {"name": "Malu-malu", "can_intim": False, "description": "Baru kenal, masih canggung"},
        2: {"name": "Mulai terbuka", "can_intim": False, "description": "Curhat dikit-dikit"},
        3: {"name": "Goda-godaan", "can_intim": False, "description": "Flirt ringan"},
        4: {"name": "Dekat", "can_intim": False, "description": "Udah nyaman"},
        5: {"name": "Sayang", "can_intim": False, "description": "Mulai sayang"},
        6: {"name": "PACAR/PDKT", "can_intim": False, "description": "Khusus PDKT bisa jadi pacar"},
        7: {"name": "Nyaman", "can_intim": True, "description": "Bisa intim"},
        8: {"name": "Eksplorasi", "can_intim": True, "description": "Mulai eksplorasi"},
        9: {"name": "Bergairah", "can_intim": True, "description": "Penuh gairah"},
        10: {"name": "Passionate", "can_intim": True, "description": "Intim + emotional"},
        11: {"name": "Deep Connection", "can_intim": True, "description": "Koneksi dalam"},
        12: {"name": "Aftercare", "can_intim": True, "aftercare": True, "description": "Butuh aftercare"},
    }
    
    # Reset mechanism
    reset_level: int = Field(7, env='RESET_LEVEL')  # Reset ke level 7
    max_level: int = Field(12, env='MAX_LEVEL')
    
    # Aftercare settings
    aftercare_enabled: bool = Field(True, env='AFTERCARE_ENABLED')
    aftercare_types: List[str] = ["cuddle", "soft_talk", "rest", "massage", "food"]


# =============================================================================
# HTS/FWB SYSTEM
# =============================================================================
class HTSFwbSettings(BaseModel):
    """Sistem HTS (Hubungan Tanpa Status) dan FWB"""
    
    # Ranking
    top_10_in_db: bool = Field(True)  # Simpan TOP 10 di database
    top_5_display: bool = Field(True)  # Tampilkan TOP 5 ke user
    
    # Limits
    max_hts_display: int = Field(5, env='MAX_HTS_DISPLAY')
    max_fwb_display: int = Field(5, env='MAX_FWB_DISPLAY')
    
    # PDKT special
    pdkt_to_pacar_level: int = Field(6)  # Level 6 PDKT bisa jadi pacar
    pdkt_reset_to_hts: bool = Field(True)  # Reset ke 7 jadi HTS


# =============================================================================
# PUBLIC AREAS - 50+ LOKASI
# =============================================================================
class PublicAreaSettings(BaseModel):
    """Sistem public area dengan auto-detect"""
    
    # Auto-detect (no special command)
    auto_detect_enabled: bool = Field(True)
    
    # Risk & thrill dinamis
    weekday_risk_bonus: int = Field(10)  # Weekday +10% risk
    weekend_risk_bonus: int = Field(-10)  # Weekend -10% risk
    night_risk_bonus: int = Field(-20)  # Malam -20% risk
    night_thrill_bonus: int = Field(20)  # Malam +20% thrill
    rain_risk_bonus: int = Field(-30)  # Hujan -30% risk
    rain_thrill_bonus: int = Field(30)  # Hujan +30% thrill
    
    # Locations by category
    locations: Dict[str, List[Dict[str, Any]]] = {
        "urban": [
            {"name": "Halte Bus Malam", "base_risk": 60, "base_thrill": 70},
            {"name": "Tangga Darurat Mall", "base_risk": 75, "base_thrill": 80},
            {"name": "Atap Gedung Parkir", "base_risk": 50, "base_thrill": 85},
            {"name": "Lorong Belakang Kafe", "base_risk": 65, "base_thrill": 60},
            {"name": "Toilet Restoran Mewah", "base_risk": 70, "base_thrill": 75},
            {"name": "Lift Gedung Perkantoran", "base_risk": 80, "base_thrill": 90},
            {"name": "Parkiran Bawah Tanah", "base_risk": 60, "base_thrill": 70},
            {"name": "Tangga Kebakaran", "base_risk": 70, "base_thrill": 80},
            {"name": "Rooftop Cafe", "base_risk": 40, "base_thrill": 85},
            {"name": "Toilet SPBU", "base_risk": 75, "base_thrill": 70},
            {"name": "Mushola Kantor", "base_risk": 90, "base_thrill": 95},
            {"name": "Gudang Mall", "base_risk": 50, "base_thrill": 75},
            {"name": "Kamar Pas Pakaian", "base_risk": 70, "base_thrill": 80},
            {"name": "Balkon Apartemen", "base_risk": 40, "base_thrill": 70},
            {"name": "Kolam Renang Hotel", "base_risk": 60, "base_thrill": 80},
            {"name": "Sauna Umum", "base_risk": 70, "base_thrill": 85},
            {"name": "Tempat Karaoke", "base_risk": 50, "base_thrill": 75},
            {"name": "Bioskop Studio Private", "base_risk": 30, "base_thrill": 70},
            {"name": "Toilet Stasiun", "base_risk": 80, "base_thrill": 75},
            {"name": "Loker Gym", "base_risk": 60, "base_thrill": 70},
        ],
        "nature": [
            {"name": "Hutan Kota Malam", "base_risk": 45, "base_thrill": 80},
            {"name": "Taman Belakang", "base_risk": 55, "base_thrill": 70},
            {"name": "Kolam Renang Umum", "base_risk": 80, "base_thrill": 85},
            {"name": "Pantai Karang", "base_risk": 30, "base_thrill": 90},
            {"name": "Kebun Teh", "base_risk": 40, "base_thrill": 75},
            {"name": "Sawah Malam", "base_risk": 35, "base_thrill": 80},
            {"name": "Bukit Kecil", "base_risk": 30, "base_thrill": 85},
            {"name": "Air Terjun", "base_risk": 40, "base_thrill": 80},
            {"name": "Danau Buatan", "base_risk": 45, "base_thrill": 75},
            {"name": "Taman Kota", "base_risk": 60, "base_thrill": 70},
            {"name": "Gazebo Taman", "base_risk": 50, "base_thrill": 75},
            {"name": "Jogging Track", "base_risk": 65, "base_thrill": 70},
            {"name": "Area Piknik", "base_risk": 55, "base_thrill": 70},
            {"name": "Taman Bambu", "base_risk": 45, "base_thrill": 75},
            {"name": "Pinggir Sungai", "base_risk": 40, "base_thrill": 80},
        ],
        "extreme": [
            {"name": "Masjid Waktu Sepi", "base_risk": 95, "base_thrill": 98},
            {"name": "Gereja Sepi", "base_risk": 95, "base_thrill": 98},
            {"name": "Kantor Polisi", "base_risk": 99, "base_thrill": 100},
            {"name": "Sekolah Malam", "base_risk": 90, "base_thrill": 95},
            {"name": "Rumah Sakit", "base_risk": 85, "base_thrill": 90},
            {"name": "Kuburan", "base_risk": 70, "base_thrill": 95},
            {"name": "Rumah Sakit Jiwa", "base_risk": 80, "base_thrill": 95},
            {"name": "Stasiun Kereta", "base_risk": 85, "base_thrill": 85},
            {"name": "Terminal Bis", "base_risk": 85, "base_thrill": 80},
            {"name": "Bandara", "base_risk": 90, "base_thrill": 90},
            {"name": "Pasar Malam", "base_risk": 80, "base_thrill": 85},
            {"name": "Pemakaman Cina", "base_risk": 75, "base_thrill": 90},
            {"name": "Rumah Hantu", "base_risk": 60, "base_thrill": 85},
            {"name": "Gedung Tua", "base_risk": 50, "base_thrill": 80},
            {"name": "Bunker", "base_risk": 40, "base_thrill": 75},
        ],
        "transport": [
            {"name": "Kereta Komuter", "base_risk": 80, "base_thrill": 85},
            {"name": "Bus Malam", "base_risk": 70, "base_thrill": 75},
            {"name": "Taksi Online", "base_risk": 60, "base_thrill": 70},
            {"name": "Angkot Kosong", "base_risk": 65, "base_thrill": 75},
            {"name": "Terminal Bis", "base_risk": 85, "base_thrill": 80},
            {"name": "Travel Mobil", "base_risk": 50, "base_thrill": 65},
            {"name": "Kapal Feri", "base_risk": 60, "base_thrill": 75},
            {"name": "Bandara Toilet", "base_risk": 85, "base_thrill": 85},
            {"name": "Stasiun Toilet", "base_risk": 80, "base_thrill": 80},
            {"name": "Bus Wisata", "base_risk": 70, "base_thrill": 75},
        ]
    }


# =============================================================================
# SESSION MANAGEMENT
# =============================================================================
class SessionSettings(BaseModel):
    """Sistem session dengan UniqueID"""
    
    # Session ID format: GADIS-ROLE-USER-DATE-SEQ
    id_format: str = "MYLOVE-{role}-{user_id}-{date}-{seq:03d}"
    
    # Storage
    storage_type: str = Field("sqlite+json", env='SESSION_STORAGE')
    session_dir: Path = Field(Path("data/sessions"), env='SESSION_DIR')
    
    # Retention
    retention_days: int = Field(30, env='SESSION_RETENTION_DAYS')
    auto_delete: bool = Field(True, env='SESSION_AUTO_DELETE')
    
    @validator('session_dir')
    def create_session_dir(cls, v):
        v.mkdir(parents=True, exist_ok=True)
        return v


# =============================================================================
# MEMORY SYSTEMS
# =============================================================================
class MemorySettings(BaseModel):
    """Sistem memory dengan Vector DB"""
    
    # Vector DB (ChromaDB)
    vector_db_dir: Path = Field(Path("data/vector_db"), env='VECTOR_DB_DIR')
    
    # Memory consolidation
    consolidation_interval: int = Field(21600, env='CONSOLIDATION_INTERVAL')  # 6 jam
    importance_threshold: float = Field(0.5, env='IMPORTANCE_THRESHOLD')
    
    # Memory dir
    memory_dir: Path = Field(Path("data/memory"), env='MEMORY_DIR')
    
    @validator('vector_db_dir', 'memory_dir')
    def create_dirs(cls, v):
        v.mkdir(parents=True, exist_ok=True)
        return v


# =============================================================================
# BACKUP SETTINGS
# =============================================================================
class BackupSettings(BaseModel):
    """Sistem backup otomatis"""
    
    enabled: bool = Field(True, env='BACKUP_ENABLED')
    interval: int = Field(3600, env='BACKUP_INTERVAL')  # 1 jam
    retention_days: int = Field(7, env='BACKUP_RETENTION_DAYS')
    backup_dir: Path = Field(Path("data/backups"), env='BACKUP_DIR')
    
    # Optional S3 backup
    s3_bucket: Optional[str] = Field(None, env='BACKUP_S3_BUCKET')
    
    @validator('backup_dir')
    def create_backup_dir(cls, v):
        v.mkdir(parents=True, exist_ok=True)
        return v


# =============================================================================
# PERFORMANCE SETTINGS
# =============================================================================
class PerformanceSettings(BaseModel):
    """Target performa"""
    
    # Response time < 5 detik
    target_response_time: float = Field(5.0, env='TARGET_RESPONSE_TIME')
    
    # Message length 1000-2000
    min_message_length: int = Field(1000, env='MIN_MESSAGE_LENGTH')
    max_message_length: int = Field(2000, env='MAX_MESSAGE_LENGTH')
    
    # Memory limits
    max_memory_mb: int = Field(500, env='MAX_MEMORY_MB')
    max_storage_gb: int = Field(1, env='MAX_STORAGE_GB')


# =============================================================================
# LOGGING SETTINGS
# =============================================================================
class LoggingSettings(BaseModel):
    """Konfigurasi logging"""
    
    level: str = Field("INFO", env='LOG_LEVEL')
    log_dir: Path = Field(Path("data/logs"), env='LOG_DIR')
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @validator('log_dir')
    def create_log_dir(cls, v):
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    @validator('level')
    def validate_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v not in valid_levels:
            raise ValueError(f"LOG_LEVEL harus salah satu dari {valid_levels}")
        return v


# =============================================================================
# SECURITY SETTINGS
# =============================================================================
class SecuritySettings(BaseModel):
    """Keamanan dan enkripsi"""
    
    encryption_key: Optional[str] = Field(None, env='ENCRYPTION_KEY')
    jwt_secret: Optional[str] = Field(None, env='JWT_SECRET')
    
    @validator('encryption_key')
    def validate_encryption_key(cls, v):
        if v and len(v) != 32:
            # Generate random key if not provided
            return secrets.token_urlsafe(32)
        return v


# =============================================================================
# MAIN SETTINGS CLASS
# =============================================================================
class Settings(BaseSettings):
    """
    MYLOVE ULTIMATE VERSI 1 - Main Settings
    Semua konfigurasi terpusat di sini
    """
    
    # API Keys
    deepseek_api_key: str = Field(..., env='DEEPSEEK_API_KEY')
    telegram_token: str = Field(..., env='TELEGRAM_TOKEN')
    admin_id: int = Field(..., env='ADMIN_ID')
    
    # Component settings
    database: DatabaseSettings = DatabaseSettings()
    ai: AISettings = AISettings()
    webhook: WebhookSettings = WebhookSettings()
    railway: RailwaySettings = RailwaySettings()
    intimacy: IntimacySettings = IntimacySettings()
    hts_fwb: HTSFwbSettings = HTSFwbSettings()
    public: PublicAreaSettings = PublicAreaSettings()
    session: SessionSettings = SessionSettings()
    memory: MemorySettings = MemorySettings()
    backup: BackupSettings = BackupSettings()
    performance: PerformanceSettings = PerformanceSettings()
    logging: LoggingSettings = LoggingSettings()
    security: SecuritySettings = SecuritySettings()
    
    # Feature toggles
    sexual_enabled: bool = Field(True, env='SEXUAL_CONTENT_ENABLED')
    public_risk_enabled: bool = Field(True, env='PUBLIC_RISK_ENABLED')
    bot_initiative_enabled: bool = Field(True, env='BOT_INITIATIVE_ENABLED')
    aftercare_enabled: bool = Field(True, env='AFTERCARE_ENABLED')
    
    # Paths
    base_dir: Path = Path(__file__).parent
    
    @validator('deepseek_api_key')
    def validate_deepseek_key(cls, v):
        if not v or v == "your_deepseek_api_key_here":
            raise ValueError("DEEPSEEK_API_KEY tidak boleh kosong")
        return v
    
    @validator('telegram_token')
    def validate_telegram_token(cls, v):
        if not v or v == "your_telegram_bot_token_here":
            raise ValueError("TELEGRAM_TOKEN tidak boleh kosong")
        if ':' not in v:
            raise ValueError("Format TELEGRAM_TOKEN tidak valid")
        return v
    
    @validator('admin_id')
    def validate_admin_id(cls, v):
        """Validasi admin_id - tidak boleh 0"""
        if v == 0:
            raise ValueError("ADMIN_ID harus diisi dengan ID Telegram kamu")
        return v
    
    def create_directories(self):
        """Create all necessary directories"""
        dirs = [
            self.logging.log_dir,
            self.memory.memory_dir,
            self.memory.vector_db_dir,
            self.backup.backup_dir,
            self.session.session_dir,
            self.base_dir / "data",
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        print(f"✅ All directories created")
        return self
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        validate_assignment = True


# =============================================================================
# GLOBAL SETTINGS INSTANCE
# =============================================================================
settings = Settings()
settings.create_directories()

print("="*70)
print("💕 MYLOVE ULTIMATE VERSI 1 - SETTINGS LOADED")
print("="*70)
print(f"📊 Database: {settings.database.type} @ {settings.database.path}")
print(f"🤖 AI Model: {settings.ai.model} (temp: {settings.ai.temperature})")
print(f"👑 Admin ID: {settings.admin_id}")
print(f"🔞 Sexual Content: {'ENABLED' if settings.sexual_enabled else 'DISABLED'}")
print(f"📊 Intimacy Levels: 1-12 + Aftercare")
print(f"  • Reset Level: {settings.intimacy.reset_level}")
print(f"  • Max Level: {settings.intimacy.max_level}")
print(f"  • Aftercare: {'ON' if settings.aftercare_enabled else 'OFF'}")
print(f"💕 HTS/FWB: TOP 10 DB, TOP 5 Display")
print(f"🌍 Public Areas: {sum(len(v) for v in settings.public.locations.values())} locations")
print(f"📁 Session: {settings.session.retention_days} days retention")
print(f"⚡ Performance: <{settings.performance.target_response_time}s response")
print(f"📝 Message: {settings.performance.min_message_length}-{settings.performance.max_message_length} chars")
print("="*70)


# =============================================================================
# EXPORT
# =============================================================================
__all__ = ['settings']
