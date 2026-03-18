#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - LEVELING PACKAGE INIT
=============================================================================
Sistem leveling berbasis durasi percakapan dengan activity boost
Target: Level 7 dalam 60 menit, Level 11 dalam 120 menit
"""

from .time_based import TimeBasedLeveling, ActivityType
from .progress_tracker import ProgressTracker

__all__ = [
    'TimeBasedLeveling',
    'ActivityType',
    'ProgressTracker',
]

__version__ = "2.0.0"
