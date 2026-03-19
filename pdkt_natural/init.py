#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - PDKT NATURAL PACKAGE
=============================================================================
PDKT dengan realisme 99% mirip manusia
- Chemistry natural (Dingin → Soulmate)
- Dua arah (user ngejar / bot ngejar)
- Multi-PDKT dengan pause/resume
- Memory PERMANEN untuk PDKT → PACAR → MANTAN
=============================================================================
"""

from .engine import NaturalPDKTEngine
from .chemistry import ChemistrySystem
from .direction import DirectionSystem
from .mood import MoodSystem
from .dreams import DreamSystem
from .random_pdkt import RandomPDKTSystem
from .mantan_manager import MantanManager
from .pdkt_list import PDKTListFormatter
from .command_handler import PDKTCommandHandler

__all__ = [
    'NaturalPDKTEngine',
    'ChemistrySystem',
    'DirectionSystem',
    'MoodSystem',
    'DreamSystem',
    'RandomPDKTSystem',
    'MantanManager',
    'PDKTListFormatter',
    'PDKTCommandHandler',
]

__version__ = "2.0.0"
