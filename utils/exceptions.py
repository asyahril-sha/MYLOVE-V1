#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - CUSTOM EXCEPTIONS
=============================================================================
- Exception hierarchy untuk error handling
- Kategori error spesifik untuk debugging
"""

from typing import Optional, Any


class MyLoveError(Exception):
    """Base exception untuk semua error MYLOVE"""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Any] = None):
        self.message = message
        self.code = code or "UNKNOWN_ERROR"
        self.details = details
        super().__init__(self.message)
        
    def __str__(self):
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message


# =============================================================================
# CONFIGURATION ERRORS
# =============================================================================

class ConfigurationError(MyLoveError):
    """Error dalam konfigurasi"""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(
            message=f"Configuration error: {message}",
            code="CONFIG_ERROR",
            details={"config_key": config_key}
        )


class MissingAPIKeyError(ConfigurationError):
    """API key tidak ditemukan"""
    
    def __init__(self, key_name: str):
        super().__init__(
            message=f"Missing API key: {key_name}",
            config_key=key_name
        )


class InvalidTokenError(ConfigurationError):
    """Token tidak valid"""
    
    def __init__(self, token_type: str):
        super().__init__(
            message=f"Invalid {token_type} token",
            config_key=token_type
        )


# =============================================================================
# DATABASE ERRORS
# =============================================================================

class DatabaseError(MyLoveError):
    """Error database"""
    
    def __init__(self, message: str, query: Optional[str] = None):
        super().__init__(
            message=f"Database error: {message}",
            code="DB_ERROR",
            details={"query": query}
        )


class ConnectionError(DatabaseError):
    """Error koneksi database"""
    
    def __init__(self, db_path: str):
        super().__init__(
            message=f"Cannot connect to database: {db_path}",
            query=None
        )


class QueryError(DatabaseError):
    """Error eksekusi query"""
    
    def __init__(self, query: str, error: str):
        super().__init__(
            message=f"Query failed: {error}",
            query=query
        )


class IntegrityError(DatabaseError):
    """Integrity constraint violation"""
    
    def __init__(self, table: str, constraint: str):
        super().__init__(
            message=f"Integrity error on {table}: {constraint}",
            query=None
        )


# =============================================================================
# AI ERRORS
# =============================================================================

class AINotAvailableError(MyLoveError):
    """AI service tidak tersedia"""
    
    def __init__(self, model: str, reason: str = "unknown"):
        super().__init__(
            message=f"AI service {model} not available: {reason}",
            code="AI_UNAVAILABLE",
            details={"model": model, "reason": reason}
        )


class AIRateLimitError(AINotAvailableError):
    """Rate limit exceeded"""
    
    def __init__(self, model: str, retry_after: int):
        super().__init__(
            model=model,
            reason=f"rate limit exceeded, retry after {retry_after}s"
        )


class AITimeoutError(AINotAvailableError):
    """Timeout saat call AI"""
    
    def __init__(self, model: str, timeout: int):
        super().__init__(
            model=model,
            reason=f"timeout after {timeout}s"
        )


# =============================================================================
# SESSION ERRORS
# =============================================================================

class SessionNotFoundError(MyLoveError):
    """Session tidak ditemukan"""
    
    def __init__(self, session_id: str):
        super().__init__(
            message=f"Session not found: {session_id}",
            code="SESSION_NOT_FOUND",
            details={"session_id": session_id}
        )


class SessionExpiredError(SessionNotFoundError):
    """Session sudah expired"""
    
    def __init__(self, session_id: str, days: int):
        super().__init__(session_id)
        self.message = f"Session {session_id} expired after {days} days"


class SessionNotActiveError(MyLoveError):
    """Session tidak aktif"""
    
    def __init__(self, session_id: str, status: str):
        super().__init__(
            message=f"Session {session_id} is not active (status: {status})",
            code="SESSION_INACTIVE",
            details={"session_id": session_id, "status": status}
        )


# =============================================================================
# ROLE ERRORS
# =============================================================================

class RoleNotFoundError(MyLoveError):
    """Role tidak ditemukan"""
    
    def __init__(self, role: str):
        super().__init__(
            message=f"Role not found: {role}",
            code="ROLE_NOT_FOUND",
            details={"role": role}
        )


class RoleNotEligibleError(MyLoveError):
    """Role tidak eligible untuk operasi tertentu"""
    
    def __init__(self, role: str, operation: str):
        super().__init__(
            message=f"Role {role} not eligible for {operation}",
            code="ROLE_NOT_ELIGIBLE",
            details={"role": role, "operation": operation}
        )


# =============================================================================
# INTIMACY ERRORS
# =============================================================================

class IntimacyLevelError(MyLoveError):
    """Error terkait intimacy level"""
    
    def __init__(self, message: str, current: int, required: int):
        super().__init__(
            message=message,
            code="INTIMACY_ERROR",
            details={"current": current, "required": required}
        )


class IntimacyTooLowError(IntimacyLevelError):
    """Intimacy level terlalu rendah"""
    
    def __init__(self, current: int, required: int, action: str):
        super().__init__(
            message=f"Intimacy level too low for {action} (current: {current}, required: {required})",
            current=current,
            required=required
        )


class IntimacyTooHighError(IntimacyLevelError):
    """Intimacy level terlalu tinggi"""
    
    def __init__(self, current: int, max_allowed: int, action: str):
        super().__init__(
            message=f"Intimacy level too high for {action} (current: {current}, max: {max_allowed})",
            current=current,
            required=max_allowed
        )


# =============================================================================
# RELATIONSHIP ERRORS
# =============================================================================

class RelationshipNotFoundError(MyLoveError):
    """Relationship tidak ditemukan"""
    
    def __init__(self, user_id: int, role: str, instance_id: Optional[str] = None):
        details = {"user_id": user_id, "role": role}
        if instance_id:
            details["instance_id"] = instance_id
            
        super().__init__(
            message=f"Relationship not found: {role}" + (f" ({instance_id})" if instance_id else ""),
            code="RELATIONSHIP_NOT_FOUND",
            details=details
        )


class RelationshipExistsError(MyLoveError):
    """Relationship sudah ada"""
    
    def __init__(self, user_id: int, role: str):
        super().__init__(
            message=f"Relationship already exists: {role}",
            code="RELATIONSHIP_EXISTS",
            details={"user_id": user_id, "role": role}
        )


# =============================================================================
# WEBHOOK ERRORS
# =============================================================================

class WebhookError(MyLoveError):
    """Error webhook"""
    
    def __init__(self, message: str, url: Optional[str] = None):
        super().__init__(
            message=f"Webhook error: {message}",
            code="WEBHOOK_ERROR",
            details={"url": url}
        )


class WebhookSetupError(WebhookError):
    """Gagal setup webhook"""
    
    def __init__(self, url: str, attempts: int):
        super().__init__(
            message=f"Failed to setup webhook after {attempts} attempts",
            url=url
        )


class WebhookTimeoutError(WebhookError):
    """Timeout webhook"""
    
    def __init__(self, url: str, timeout: int):
        super().__init__(
            message=f"Webhook timeout after {timeout}s",
            url=url
        )


# =============================================================================
# BACKUP ERRORS
# =============================================================================

class BackupError(MyLoveError):
    """Error backup/restore"""
    
    def __init__(self, message: str, filename: Optional[str] = None):
        super().__init__(
            message=f"Backup error: {message}",
            code="BACKUP_ERROR",
            details={"filename": filename}
        )


class BackupNotFoundError(BackupError):
    """File backup tidak ditemukan"""
    
    def __init__(self, filename: str):
        super().__init__(
            message=f"Backup file not found: {filename}",
            filename=filename
        )


class BackupCorruptedError(BackupError):
    """File backup corrupt"""
    
    def __init__(self, filename: str):
        super().__init__(
            message=f"Backup file corrupted: {filename}",
            filename=filename
        )


# =============================================================================
# VALIDATION ERRORS
# =============================================================================

class ValidationError(MyLoveError):
    """Error validasi input"""
    
    def __init__(self, field: str, reason: str, value: Optional[Any] = None):
        super().__init__(
            message=f"Validation error for {field}: {reason}",
            code="VALIDATION_ERROR",
            details={"field": field, "value": value, "reason": reason}
        )


class InvalidCommandError(ValidationError):
    """Command tidak valid"""
    
    def __init__(self, command: str, reason: str = "unknown"):
        super().__init__(
            field="command",
            reason=reason,
            value=command
        )


__all__ = [
    'MyLoveError',
    'ConfigurationError',
    'MissingAPIKeyError',
    'InvalidTokenError',
    'DatabaseError',
    'ConnectionError',
    'QueryError',
    'IntegrityError',
    'AINotAvailableError',
    'AIRateLimitError',
    'AITimeoutError',
    'SessionNotFoundError',
    'SessionExpiredError',
    'SessionNotActiveError',
    'RoleNotFoundError',
    'RoleNotEligibleError',
    'IntimacyLevelError',
    'IntimacyTooLowError',
    'IntimacyTooHighError',
    'RelationshipNotFoundError',
    'RelationshipExistsError',
    'WebhookError',
    'WebhookSetupError',
    'WebhookTimeoutError',
    'BackupError',
    'BackupNotFoundError',
    'BackupCorruptedError',
    'ValidationError',
    'InvalidCommandError',
]
