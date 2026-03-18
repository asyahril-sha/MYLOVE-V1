#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - BACKUP PACKAGE INIT
=============================================================================
Inisialisasi package backup dan export semua komponen
"""

from .automated import AutoBackup, get_backup_manager
from .recovery import RecoveryManager
from .verify import BackupVerifier

__all__ = [
    'AutoBackup',
    'get_backup_manager',
    'RecoveryManager',
    'BackupVerifier',
]

# Version info
__version__ = "1.0.0"
