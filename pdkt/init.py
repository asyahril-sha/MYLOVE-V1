#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - PDKT SUPER SPESIAL PACKAGE
=============================================================================
PDKT dengan realisme 99% mirip manusia
- Tidak ada rumus matematika
- Berdasarkan chemistry natural
- Bisa cepat atau lambat
- Dua arah (user ngejar / bot ngejar)
=============================================================================
"""

from .chemistry import ChemistrySystem, ChemistryScore
from .direction import DirectionSystem, PDKTDirection
from .natural_engine import NaturalPDKTEngine

__all__ = [
    'ChemistrySystem',
    'ChemistryScore',
    'DirectionSystem',
    'PDKTDirection',
    'NaturalPDKTEngine',
]

__version__ = "2.0.0"
