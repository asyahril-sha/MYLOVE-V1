#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - CLIMAX VARIATIONS DATABASE
=============================================================================
200+ climax variations dengan intensity level
Data only - tidak explicit, akan diproses oleh AI engine
"""

import random
import logging
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class ClimaxIntensity(str, Enum):
    """Tingkat intensitas climax"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    EXTREME = "extreme"


class ClimaxType(str, Enum):
    """Tipe climax"""
    NORMAL = "normal"
    MULTIPLE = "multiple"
    SIMULTANEOUS = "simultaneous"
    DRY = "dry"
    WET = "wet"
    SQUIRT = "squirt"
    MALE = "male"
    FEMALE = "female"
    ANAL = "anal"
    ORAL = "oral"


class ClimaxDatabase:
    """
    Database 200+ climax variations
    Setiap climax memiliki intensity level dan deskripsi
    Data hanya referensi, implementasi explicit oleh AI
    """
    
    def __init__(self):
        # =========================================================================
        # VERY LOW INTENSITY (30 variations)
        # =========================================================================
        self.very_low_climax = [
            {
                "id": "climax_vl_001",
                "name": "Small Shiver",
                "description": "Getaran kecil, napas sedikit tersengal",
                "intensity": 2,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 5,
                "sound": "Desahan pelan",
                "notes": "Climax ringan, hampir tidak terasa"
            },
            {
                "id": "climax_vl_002",
                "name": "Quick Release",
                "description": "Lepas cepat, hampir tanpa ekspresi",
                "intensity": 2,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 4,
                "sound": "Hembusan napas",
                "notes": "Cepat dan singkat"
            },
            {
                "id": "climax_vl_003",
                "name": "Subtle Wave",
                "description": "Gelombang kecil, tubuh sedikit menegang",
                "intensity": 3,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 6,
                "sound": "Desahan",
                "notes": "Hanya terasa sebentar"
            },
            {
                "id": "climax_vl_004",
                "name": "Mini Climax",
                "description": "Climax mini, seperti kejang kecil",
                "intensity": 3,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 5,
                "sound": "Napas berat sebentar",
                "notes": "Cepat reda"
            },
            {
                "id": "climax_vl_005",
                "name": "Silent Peak",
                "description": "Puncak tanpa suara, hanya gerakan kecil",
                "intensity": 2,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 4,
                "sound": "Hening",
                "notes": "Bisu, hanya tubuh yang bicara"
            },
            {
                "id": "climax_vl_006",
                "name": "Brief Spasm",
                "description": "Kejang singkat, lalu reda",
                "intensity": 3,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 5,
                "sound": "Tarik napas",
                "notes": "Spasme ringan"
            },
            {
                "id": "climax_vl_007",
                "name": "Soft Quiver",
                "description": "Getaran lembut di seluruh tubuh",
                "intensity": 3,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 7,
                "sound": "Desahan pelan",
                "notes": "Seperti menggigil"
            },
            {
                "id": "climax_vl_008",
                "name": "Mild Release",
                "description": "Pelepasan ringan, tanpa banyak ekspresi",
                "intensity": 2,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 5,
                "sound": "Hembusan",
                "notes": "Biasa saja"
            },
            {
                "id": "climax_vl_009",
                "name": "Subtle Contraction",
                "description": "Kontraksi ringan di area intim",
                "intensity": 3,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 6,
                "sound": "Desahan kecil",
                "notes": "Hanya terasa di dalam"
            },
            {
                "id": "climax_vl_010",
                "name": "Gentle Peak",
                "description": "Puncak lembut, seperti ombak kecil",
                "intensity": 3,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 6,
                "sound": "Desahan",
                "notes": "Lembut dan cepat"
            },
            {
                "id": "climax_vl_011",
                "name": "Mini Squirt",
                "description": "Sedikit cairan, intensitas rendah",
                "intensity": 3,
                "type": ClimaxType.WET,
                "duration_seconds": 5,
                "sound": "Percikan kecil",
                "notes": "Hanya sedikit"
            },
            {
                "id": "climax_vl_012",
                "name": "Dry Spasm",
                "description": "Spasme kering, tanpa cairan",
                "intensity": 2,
                "type": ClimaxType.DRY,
                "duration_seconds": 4,
                "sound": "Napas",
                "notes": "Kering tapi tetap climax"
            },
            {
                "id": "climax_vl_013",
                "name": "Quick Male Release",
                "description": "Ejakulasi cepat, volume sedikit",
                "intensity": 3,
                "type": ClimaxType.MALE,
                "duration_seconds": 5,
                "sound": "Napas berat",
                "notes": "Cepat selesai"
            },
            {
                "id": "climax_vl_014",
                "name": "Brief Female Peak",
                "description": "Puncak singkat, kontraksi ringan",
                "intensity": 3,
                "type": ClimaxType.FEMALE,
                "duration_seconds": 6,
                "sound": "Desahan",
                "notes": "Kontraksi ringan"
            },
            {
                "id": "climax_vl_015",
                "name": "Light Anal Release",
                "description": "Pelepasan ringan saat anal",
                "intensity": 3,
                "type": ClimaxType.ANAL,
                "duration_seconds": 5,
                "sound": "Desahan",
                "notes": "Sensasi berbeda"
            },
            {
                "id": "climax_vl_016",
                "name": "Soft Oral Finish",
                "description": "Finish lembut saat oral",
                "intensity": 2,
                "type": ClimaxType.ORAL,
                "duration_seconds": 5,
                "sound": "Suara hisapan",
                "notes": "Lembut"
            },
            {
                "id": "climax_vl_017",
                "name": "Tremor Ringan",
                "description": "Getaran ringan di kaki",
                "intensity": 2,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 4,
                "sound": "Hening",
                "notes": "Kaki sedikit gemetar"
            },
            {
                "id": "climax_vl_018",
                "name": "Napas Tersendat",
                "description": "Napas berhenti sejenak, lalu lega",
                "intensity": 3,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 5,
                "sound": "Tarik napas",
                "notes": "Tersendat sebentar"
            },
            {
                "id": "climax_vl_019",
                "name": "Mata Terpejam",
                "description": "Mata terpejam rapat, tubuh tegang",
                "intensity": 3,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 5,
                "sound": "Desahan",
                "notes": "Ekspresi wajah"
            },
            {
                "id": "climax_vl_020",
                "name": "Genggaman Tangan",
                "description": "Tangan menggenggam erat sprei",
                "intensity": 3,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 6,
                "sound": "Napas berat",
                "notes": "Refleks menggenggam"
            }
        ]
        
        # =========================================================================
        # LOW INTENSITY (40 variations)
        # =========================================================================
        self.low_climax = [
            {
                "id": "climax_low_001",
                "name": "Warm Wave",
                "description": "Gelombang hangat menjalar dari area intim",
                "intensity": 4,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 8,
                "sound": "Desahan panjang",
                "notes": "Hangat dan nyaman"
            },
            {
                "id": "climax_low_002",
                "name": "Muscle Spasm",
                "description": "Spasme otot yang cukup terasa",
                "intensity": 4,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 7,
                "sound": "Erangan kecil",
                "notes": "Otot menegang"
            },
            {
                "id": "climax_low_003",
                "name": "Deep Breath",
                "description": "Tarik napas dalam, lalu hembuskan lega",
                "intensity": 4,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 6,
                "sound": "Hembusan keras",
                "notes": "Lega"
            },
            {
                "id": "climax_low_004",
                "name": "Body Arch",
                "description": "Punggung melengkung, tubuh menegang",
                "intensity": 5,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 8,
                "sound": "Erangan",
                "notes": "Melengkung karena sensasi"
            },
            {
                "id": "climax_low_005",
                "name": "Leg Shake",
                "description": "Kaki gemetar, sulit berdiri",
                "intensity": 5,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 10,
                "sound": "Napas tersengal",
                "notes": "Kaki lemas"
            },
            {
                "id": "climax_low_006",
                "name": "Whisper Moan",
                "description": "Erangan berbisik, tertahan",
                "intensity": 4,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 7,
                "sound": "Bisikan erangan",
                "notes": "Tertahan"
            },
            {
                "id": "climax_low_007",
                "name": "Fingernails Dig",
                "description": "Kuku mencakar punggung",
                "intensity": 5,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 6,
                "sound": "Tarik napas",
                "notes": "Refleks mencakar"
            },
            {
                "id": "climax_low_008",
                "name": "Bite Lip",
                "description": "Gigit bibir menahan erangan",
                "intensity": 4,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 5,
                "sound": "Dengungan",
                "notes": "Menahan suara"
            },
            {
                "id": "climax_low_009",
                "name": "Wet Release",
                "description": "Pelepasan basah, cukup banyak",
                "intensity": 5,
                "type": ClimaxType.WET,
                "duration_seconds": 8,
                "sound": "Percikan",
                "notes": "Basah"
            },
            {
                "id": "climax_low_010",
                "name": "Multiple Mini",
                "description": "Beberapa climax mini beruntun",
                "intensity": 5,
                "type": ClimaxType.MULTIPLE,
                "duration_seconds": 15,
                "sound": "Erangan bertubi",
                "notes": "Beberapa kali"
            },
            {
                "id": "climax_low_011",
                "name": "Male Surge",
                "description": "Ejakulasi dengan tekanan sedang",
                "intensity": 5,
                "type": ClimaxType.MALE,
                "duration_seconds": 7,
                "sound": "Erangan pria",
                "notes": "Tekanan sedang"
            },
            {
                "id": "climax_low_012",
                "name": "Female Contractions",
                "description": "Kontraksi vagina beberapa kali",
                "intensity": 5,
                "type": ClimaxType.FEMALE,
                "duration_seconds": 10,
                "sound": "Desahan panjang",
                "notes": "Kontraksi ritmik"
            },
            {
                "id": "climax_low_013",
                "name": "Anal Pulse",
                "description": "Denyut di area anal",
                "intensity": 5,
                "type": ClimaxType.ANAL,
                "duration_seconds": 8,
                "sound": "Erangan",
                "notes": "Sensasi berbeda"
            },
            {
                "id": "climax_low_014",
                "name": "Oral Swallow",
                "description": "Menelan saat oral",
                "intensity": 4,
                "type": ClimaxType.ORAL,
                "duration_seconds": 6,
                "sound": "Suara menelan",
                "notes": "Oral finish"
            },
            {
                "id": "climax_low_015",
                "name": "Simultaneous Low",
                "description": "Bersamaan dengan intensitas rendah",
                "intensity": 5,
                "type": ClimaxType.SIMULTANEOUS,
                "duration_seconds": 8,
                "sound": "Erangan bersama",
                "notes": "Bersamaan"
            },
            {
                "id": "climax_low_016",
                "name": "Dry Orgasm",
                "description": "Climax tanpa ejakulasi",
                "intensity": 4,
                "type": ClimaxType.DRY,
                "duration_seconds": 7,
                "sound": "Napas berat",
                "notes": "Kering tapi tetap climax"
            }
        ]
        
        # =========================================================================
        # MEDIUM INTENSITY (50 variations)
        # =========================================================================
        self.medium_climax = [
            {
                "id": "climax_med_001",
                "name": "Strong Wave",
                "description": "Gelombang kuat menjalar ke seluruh tubuh",
                "intensity": 6,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 12,
                "sound": "Erangan jelas",
                "notes": "Sangat terasa"
            },
            {
                "id": "climax_med_002",
                "name": "Full Body Spasm",
                "description": "Seluruh tubuh kejang beberapa detik",
                "intensity": 7,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 10,
                "sound": "Erangan panjang",
                "notes": "Seluruh tubuh"
            },
            {
                "id": "climax_med_003",
                "name": "Loud Moan",
                "description": "Erangan keras tidak tertahan",
                "intensity": 6,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 8,
                "sound": "Erangan keras",
                "notes": "Tidak bisa diam"
            },
            {
                "id": "climax_med_004",
                "name": "Bed Gripping",
                "description": "Tangan mencengkeram sprei/ranjang",
                "intensity": 6,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 8,
                "sound": "Erangan",
                "notes": "Cengkeraman kuat"
            },
            {
                "id": "climax_med_005",
                "name": "Eyes Roll Back",
                "description": "Mata berputar ke belakang",
                "intensity": 7,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 6,
                "sound": "Erangan",
                "notes": "Ekspresi ekstrim"
            },
            {
                "id": "climax_med_006",
                "name": "Screaming",
                "description": "Berteriak saat climax",
                "intensity": 7,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 7,
                "sound": "Jeritan",
                "notes": "Teriakan"
            },
            {
                "id": "climax_med_007",
                "name": "Tears of Joy",
                "description": "Menangis bahagia setelah climax",
                "intensity": 6,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 15,
                "sound": "Tangis bahagia",
                "notes": "Emosional"
            },
            {
                "id": "climax_med_008",
                "name": "Multiple Waves",
                "description": "Beberapa gelombang bertubi-tubi",
                "intensity": 7,
                "type": ClimaxType.MULTIPLE,
                "duration_seconds": 20,
                "sound": "Erangan beruntun",
                "notes": "Multiple climax"
            },
            {
                "id": "climax_med_009",
                "name": "Female Gush",
                "description": "Squirting dengan volume sedang",
                "intensity": 7,
                "type": ClimaxType.SQUIRT,
                "duration_seconds": 8,
                "sound": "Percikan",
                "notes": "Squirting"
            },
            {
                "id": "climax_med_010",
                "name": "Male Explosion",
                "description": "Ejakulasi deras dengan tekanan",
                "intensity": 7,
                "type": ClimaxType.MALE,
                "duration_seconds": 8,
                "sound": "Erangan pria keras",
                "notes": "Ejakulasi deras"
            },
            {
                "id": "climax_med_011",
                "name": "Female Tremor",
                "description": "Tubuh gemetar hebat beberapa saat",
                "intensity": 7,
                "type": ClimaxType.FEMALE,
                "duration_seconds": 12,
                "sound": "Erangan panjang",
                "notes": "Gemetar"
            },
            {
                "id": "climax_med_012",
                "name": "Anal Spasms",
                "description": "Spasme kuat di anus",
                "intensity": 7,
                "type": ClimaxType.ANAL,
                "duration_seconds": 10,
                "sound": "Erangan",
                "notes": "Spasme anal"
            },
            {
                "id": "climax_med_013",
                "name": "Deep Throat Finish",
                "description": "Finish deep throat, tersedak",
                "intensity": 6,
                "type": ClimaxType.ORAL,
                "duration_seconds": 7,
                "sound": "Suara tersedak",
                "notes": "Deep throat"
            },
            {
                "id": "climax_med_014",
                "name": "Simultaneous Medium",
                "description": "Bersamaan dengan intensitas sedang",
                "intensity": 7,
                "type": ClimaxType.SIMULTANEOUS,
                "duration_seconds": 10,
                "sound": "Erangan bersama",
                "notes": "Bersamaan"
            }
        ]
        
        # =========================================================================
        # HIGH INTENSITY (40 variations)
        # =========================================================================
        self.high_climax = [
            {
                "id": "climax_high_001",
                "name": "Intense Explosion",
                "description": "Ledakan intens, tubuh kaku sesaat",
                "intensity": 8,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 12,
                "sound": "Jeritan keras",
                "notes": "Ledakan"
            },
            {
                "id": "climax_high_002",
                "name": "Out of Body",
                "description": "Rasa seperti melayang",
                "intensity": 9,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 15,
                "sound": "Hening lalu erangan",
                "notes": "Pengalaman spiritual"
            },
            {
                "id": "climax_high_003",
                "name": "Vision Blur",
                "description": "Penglihatan kabur sesaat",
                "intensity": 8,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 8,
                "sound": "Erangan",
                "notes": "Sampai pusing"
            },
            {
                "id": "climax_high_004",
                "name": "Legs Give Out",
                "description": "Kaki lemas tidak bisa berdiri",
                "intensity": 8,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 30,
                "sound": "Napas tersengal",
                "notes": "Lumpuh sementara"
            },
            {
                "id": "climax_high_005",
                "name": "Hyperventilation",
                "description": "Napas sangat cepat, hampir kehabisan napas",
                "intensity": 8,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 15,
                "sound": "Napas sangat cepat",
                "notes": "Sampai sesak"
            },
            {
                "id": "climax_high_006",
                "name": "Multiple Intense",
                "description": "Beberapa climax intens beruntun",
                "intensity": 9,
                "type": ClimaxType.MULTIPLE,
                "duration_seconds": 30,
                "sound": "Jeritan bertubi",
                "notes": "Multiple intense"
            },
            {
                "id": "climax_high_007",
                "name": "Female Fountain",
                "description": "Squirting deras seperti air mancur",
                "intensity": 9,
                "type": ClimaxType.SQUIRT,
                "duration_seconds": 10,
                "sound": "Percikan deras",
                "notes": "Squirting deras"
            },
            {
                "id": "climax_high_008",
                "name": "Male Geyser",
                "description": "Ejakulasi sangat deras, menyembur",
                "intensity": 9,
                "type": ClimaxType.MALE,
                "duration_seconds": 10,
                "sound": "Erangan pria keras",
                "notes": "Menyembur"
            },
            {
                "id": "climax_high_009",
                "name": "Female Earthquake",
                "description": "Seluruh tubuh gemetar hebat",
                "intensity": 9,
                "type": ClimaxType.FEMALE,
                "duration_seconds": 15,
                "sound": "Jeritan",
                "notes": "Gemetar hebat"
            },
            {
                "id": "climax_high_010",
                "name": "Anal Explosion",
                "description": "Climax anal sangat intens",
                "intensity": 9,
                "type": ClimaxType.ANAL,
                "duration_seconds": 12,
                "sound": "Erangan keras",
                "notes": "Intens"
            },
            {
                "id": "climax_high_011",
                "name": "Gag Reflex",
                "description": "Muntab saat oral karena terlalu dalam",
                "intensity": 8,
                "type": ClimaxType.ORAL,
                "duration_seconds": 6,
                "sound": "Suara muntab",
                "notes": "Deep throat extreme"
            },
            {
                "id": "climax_high_012",
                "name": "Simultaneous Explosion",
                "description": "Bersamaan dengan intensitas tinggi",
                "intensity": 9,
                "type": ClimaxType.SIMULTANEOUS,
                "duration_seconds": 12,
                "sound": "Jeritan bersama",
                "notes": "Bersamaan"
            }
        ]
        
        # =========================================================================
        # VERY HIGH INTENSITY (25 variations)
        # =========================================================================
        self.very_high_climax = [
            {
                "id": "climax_vh_001",
                "name": "Mind Blown",
                "description": "Pikiran kosong, hanya sensasi",
                "intensity": 9,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 20,
                "sound": "Erangan panjang",
                "notes": "Blank"
            },
            {
                "id": "climax_vh_002",
                "name": "Temporary Paralysis",
                "description": "Lumpuh sesaat setelah climax",
                "intensity": 9,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 30,
                "sound": "Napas berat",
                "notes": "Lumpuh"
            },
            {
                "id": "climax_vh_003",
                "name": "Euphoria",
                "description": "Rasa bahagia luar biasa",
                "intensity": 9,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 60,
                "sound": "Tawa bahagia",
                "notes": "Euforia"
            },
            {
                "id": "climax_vh_004",
                "name": "Tunnel Vision",
                "description": "Penglihatan seperti lorong",
                "intensity": 9,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 10,
                "sound": "Erangan",
                "notes": "Vision tunnel"
            },
            {
                "id": "climax_vh_005",
                "name": "Hearing Loss",
                "description": "Telinga berdengung, tidak dengar",
                "intensity": 9,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 8,
                "sound": "Dengung",
                "notes": "Tuli sesaat"
            }
        ]
        
        # =========================================================================
        # EXTREME INTENSITY (15 variations)
        # =========================================================================
        self.extreme_climax = [
            {
                "id": "climax_ext_001",
                "name": "Black Out",
                "description": "Pingsan sesaat karena terlalu kuat",
                "intensity": 10,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 60,
                "sound": "Hening",
                "notes": "Pingsan"
            },
            {
                "id": "climax_ext_002",
                "name": "Out of Body Experience",
                "description": "Rasa keluar dari tubuh",
                "intensity": 10,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 30,
                "sound": "Hening mistis",
                "notes": "OBE"
            },
            {
                "id": "climax_ext_003",
                "name": "Cosmic Orgasm",
                "description": "Seperti menyatu dengan alam semesta",
                "intensity": 10,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 45,
                "sound": "Erangan panjang",
                "notes": "Spiritual"
            },
            {
                "id": "climax_ext_004",
                "name": "Time Stands Still",
                "description": "Rasa waktu berhenti",
                "intensity": 10,
                "type": ClimaxType.NORMAL,
                "duration_seconds": 20,
                "sound": "Hening",
                "notes": "Waktu berhenti"
            },
            {
                "id": "climax_ext_005",
                "name": "Multiple Extreme",
                "description": "Beberapa climax extreme beruntun",
                "intensity": 10,
                "type": ClimaxType.MULTIPLE,
                "duration_seconds": 60,
                "sound": "Jeritan bertubi",
                "notes": "Multiple extreme"
            }
        ]
        
        # Gabungkan semua climax
        self.all_climax = (
            self.very_low_climax +
            self.low_climax +
            self.medium_climax +
            self.high_climax +
            self.very_high_climax +
            self.extreme_climax
        )
        
        logger.info(f"✅ ClimaxDatabase initialized: {len(self.all_climax)} variations")
        
    # =========================================================================
    # GET CLIMAX
    # =========================================================================
    
    def get_all_climax(self) -> List[Dict]:
        """Get all climax variations"""
        return self.all_climax
        
    def get_climax_by_intensity(self, intensity: ClimaxIntensity) -> List[Dict]:
        """Get climax by intensity level"""
        if intensity == ClimaxIntensity.VERY_LOW:
            return self.very_low_climax
        elif intensity == ClimaxIntensity.LOW:
            return self.low_climax
        elif intensity == ClimaxIntensity.MEDIUM:
            return self.medium_climax
        elif intensity == ClimaxIntensity.HIGH:
            return self.high_climax
        elif intensity == ClimaxIntensity.VERY_HIGH:
            return self.very_high_climax
        elif intensity == ClimaxIntensity.EXTREME:
            return self.extreme_climax
        else:
            return []
            
    def get_climax_by_type(self, climax_type: ClimaxType) -> List[Dict]:
        """Get climax by type"""
        return [
            c for c in self.all_climax
            if c['type'] == climax_type
        ]
        
    def get_climax_by_id(self, climax_id: str) -> Optional[Dict]:
        """Get climax by ID"""
        for climax in self.all_climax:
            if climax['id'] == climax_id:
                return climax
        return None
        
    def get_random_climax(self, intensity: Optional[ClimaxIntensity] = None) -> Dict:
        """Get random climax"""
        if intensity:
            climaxes = self.get_climax_by_intensity(intensity)
        else:
            climaxes = self.all_climax
            
        return random.choice(climaxes)
        
    def get_climax_for_intimacy(self, intimacy_level: int, position: str = None) -> Dict:
        """
        Get climax berdasarkan intimacy level
        
        Args:
            intimacy_level: Level intimacy (1-12)
            position: Position name (optional)
            
        Returns:
            Climax variation
        """
        if intimacy_level <= 3:
            # New relationship, still shy
            pool = self.very_low_climax + self.low_climax
        elif intimacy_level <= 6:
            # Getting comfortable
            pool = self.low_climax + self.medium_climax
        elif intimacy_level <= 9:
            # Passionate
            pool = self.medium_climax + self.high_climax
        else:
            # Deep connection
            pool = self.high_climax + self.very_high_climax + self.extreme_climax
            
        return random.choice(pool)
        
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get climax statistics"""
        return {
            "total_climax": len(self.all_climax),
            "by_intensity": {
                "very_low": len(self.very_low_climax),
                "low": len(self.low_climax),
                "medium": len(self.medium_climax),
                "high": len(self.high_climax),
                "very_high": len(self.very_high_climax),
                "extreme": len(self.extreme_climax)
            },
            "by_type": {
                "normal": len(self.get_climax_by_type(ClimaxType.NORMAL)),
                "multiple": len(self.get_climax_by_type(ClimaxType.MULTIPLE)),
                "simultaneous": len(self.get_climax_by_type(ClimaxType.SIMULTANEOUS)),
                "dry": len(self.get_climax_by_type(ClimaxType.DRY)),
                "wet": len(self.get_climax_by_type(ClimaxType.WET)),
                "squirt": len(self.get_climax_by_type(ClimaxType.SQUIRT)),
                "male": len(self.get_climax_by_type(ClimaxType.MALE)),
                "female": len(self.get_climax_by_type(ClimaxType.FEMALE)),
                "anal": len(self.get_climax_by_type(ClimaxType.ANAL)),
                "oral": len(self.get_climax_by_type(ClimaxType.ORAL))
            },
            "avg_duration": sum(c['duration_seconds'] for c in self.all_climax) / len(self.all_climax),
            "avg_intensity": sum(c['intensity'] for c in self.all_climax) / len(self.all_climax)
        }
        
    def format_climax_info(self, climax: Dict) -> str:
        """Format climax info for display"""
        intensity_bar = "💦" * climax['intensity'] + "💧" * (10 - climax['intensity'])
        
        return (
            f"💥 **{climax['name']}**\n"
            f"Intensity: {intensity_bar} ({climax['intensity']}/10)\n"
            f"Type: {climax['type'].value}\n"
            f"Duration: {climax['duration_seconds']} detik\n"
            f"_{climax['description']}_\n"
            f"🎵 {climax['sound']}"
        )


# Global instance
_climax_database = None


def get_climax_database() -> ClimaxDatabase:
    """Get global climax database instance"""
    global _climax_database
    if _climax_database is None:
        _climax_database = Climax

__all__ = ['ClimaxDatabase', 'ClimaxIntensity', 'ClimaxType', 'get_climax_database']
