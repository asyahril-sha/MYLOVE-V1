#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - UTILITIES PACKAGE INIT
=============================================================================
Inisialisasi package utilities dan export semua komponen
"""

from .logger import setup_logging, get_logger
from .exceptions import (
    MyLoveError, DatabaseError, AINotAvailableError,
    SessionNotFoundError, RoleNotFoundError, IntimacyLevelError,
    ConfigurationError, WebhookError, BackupError
)
from .helpers import (
    sanitize_input, format_number, truncate_text,
    time_ago, calculate_age, parse_command_args,
    generate_temp_id, validate_role, validate_intimacy_level,
    format_duration, extract_keywords, similarity_score
)
from .performance import PerformanceMonitor, measure_time, async_measure_time

__all__ = [
    # Logger
    'setup_logging',
    'get_logger',
    
    # Exceptions
    'MyLoveError',
    'DatabaseError',
    'AINotAvailableError',
    'SessionNotFoundError',
    'RoleNotFoundError',
    'IntimacyLevelError',
    'ConfigurationError',
    'WebhookError',
    'BackupError',
    
    # Helpers
    'sanitize_input',
    'format_number',
    'truncate_text',
    'time_ago',
    'calculate_age',
    'parse_command_args',
    'generate_temp_id',
    'validate_role',
    'validate_intimacy_level',
    'format_duration',
    'extract_keywords',
    'similarity_score',
    
    # Performance
    'PerformanceMonitor',
    'measure_time',
    'async_measure_time',
]

# Version info
__version__ = "1.0.0"
