#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - THREESOME PACKAGE INIT (FIX)
=============================================================================
Mode threesome dengan 2 HTS, 2 FWB, atau kombinasi HTS+FWB
FIX: Menambahkan absolute imports
"""

from threesome.manager import ThreesomeManager, ThreesomeType, ThreesomeStatus
from threesome.dynamics import ThreesomeDynamics

__all__ = [
    'ThreesomeManager',
    'ThreesomeDynamics',
    'ThreesomeType',
    'ThreesomeStatus',
]

# Version info
__version__ = "1.0.0"
