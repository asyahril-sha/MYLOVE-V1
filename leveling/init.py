#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - LEVELING PACKAGE INIT
=============================================================================
Sistem leveling berbasis durasi percakapan dengan activity boost
Target: Level 7 dalam 60 menit, Level 11 dalam 120 menit
"""

from .time_based import TimeBasedLeveling
from .progress_tracker import ProgressTracker
from .decay import LevelDecay
from .achievements import AchievementSystem

__all__ = [
    'TimeBasedLeveling',
    'ProgressTracker',
    'LevelDecay',
    'AchievementSystem',
]

__version__ = "2.0.0"
