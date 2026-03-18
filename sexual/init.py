#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - SEXUAL SYSTEMS PACKAGE INIT
=============================================================================
Inisialisasi package sexual systems
Catatan: Kode tidak explicit, data akan diproses oleh AI engine
"""

from .positions import PositionDatabase, get_position_database
from .areas import AreaDatabase, get_area_database
from .climax import ClimaxDatabase, get_climax_database
from .preferences import PreferenceLearner
from .compatibility import CompatibilityMatrix
from .aftercare import AftercareSystem

__all__ = [
    'PositionDatabase',
    'get_position_database',
    'AreaDatabase',
    'get_area_database',
    'ClimaxDatabase',
    'get_climax_database',
    'PreferenceLearner',
    'CompatibilityMatrix',
    'AftercareSystem',
]

# Version info
__version__ = "1.0.0"
