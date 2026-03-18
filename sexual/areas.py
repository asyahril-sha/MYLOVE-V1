#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - SENSITIVE AREAS DATABASE
=============================================================================
100+ sensitive areas dengan sensitivity level
Data only - tidak explicit, akan diproses oleh AI engine
"""

import random
import logging
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class AreaCategory(str, Enum):
    """Kategori area sensitif"""
    HEAD = "head"
    NECK = "neck"
    CHEST = "chest"
    BACK = "back"
    ARMS = "arms"
    STOMACH = "stomach"
    HIPS = "hips"
    LEGS = "legs"
    FEET = "feet"
    SPECIAL = "special"


class AreaDatabase:
    """
    Database 100+ sensitive areas
    Setiap area memiliki sensitivity level (1-10)
    Data hanya referensi, implementasi explicit oleh AI
    """
    
    def __init__(self):
        # =========================================================================
        # HEAD AREAS (10 areas)
        # =========================================================================
        self.head_areas = [
            {
                "id": "head_forehead",
                "name": "Dahi",
                "description": "Area dahi, sensitif saat dicium pelan",
                "sensitivity": 5,
                "notes": "Ciuman di dihi terasa romantis"
            },
            {
                "id": "head_temple",
                "name": "Pelipis",
                "description": "Pelipis kiri dan kanan",
                "sensitivity": 6,
                "notes": "Ciuman ringan di pelipis menenangkan"
            },
            {
                "id": "head_earlobe",
                "name": "Daun Telinga",
                "description": "Daun telinga, sangat sensitif",
                "sensitivity": 8,
                "notes": "Bisikan atau ciuman di telinga"
            },
            {
                "id": "head_behind_ear",
                "name": "Belakang Telinga",
                "description": "Area belakang telinga",
                "sensitivity": 9,
                "notes": "Sangat sensitif, bisa bikin merinding"
            },
            {
                "id": "head_cheek",
                "name": "Pipi",
                "description": "Pipi kiri dan kanan",
                "sensitivity": 4,
                "notes": "Ciuman di pipi terasa manis"
            },
            {
                "id": "head_lips",
                "name": "Bibir",
                "description": "Bibir, sangat sensitif",
                "sensitivity": 9,
                "notes": "Ciuman, gigitan ringan"
            },
            {
                "id": "head_tongue",
                "name": "Lidah",
                "description": "Lidah, French kiss",
                "sensitivity": 8,
                "notes": "Untuk kissing dalam"
            },
            {
                "id": "head_chin",
                "name": "Dagu",
                "description": "Area dagu",
                "sensitivity": 5,
                "notes": "Ciuman atau elusan"
            },
            {
                "id": "head_scalp",
                "name": "Kulit Kepala",
                "description": "Kulit kepala",
                "sensitivity": 7,
                "notes": "Pijatan kepala terasa nyaman"
            },
            {
                "id": "head_nape",
                "name": "Tengkuk",
                "description": "Tengkuk leher belakang",
                "sensitivity": 8,
                "notes": "Sangat sensitif, bisa bikin merinding"
            }
        ]
        
        # =========================================================================
        # NECK AREAS (8 areas)
        # =========================================================================
        self.neck_areas = [
            {
                "id": "neck_front",
                "name": "Leher Depan",
                "description": "Leher bagian depan",
                "sensitivity": 7,
                "notes": "Ciuman ringan, hindari tekanan keras"
            },
            {
                "id": "neck_side",
                "name": "Leher Samping",
                "description": "Leher samping kiri/kanan",
                "sensitivity": 8,
                "notes": "Sangat sensitif, bekas ciuman bisa muncul"
            },
            {
                "id": "neck_back",
                "name": "Leher Belakang",
                "description": "Leher bagian belakang",
                "sensitivity": 7,
                "notes": "Elusan atau ciuman ringan"
            },
            {
                "id": "neck_collarbone",
                "name": "Tulang Selangka",
                "description": "Area tulang selangka",
                "sensitivity": 6,
                "notes": "Ciuman atau jilatan"
            },
            {
                "id": "neck_throat",
                "name": "Tenggorokan",
                "description": "Area tenggorokan",
                "sensitivity": 5,
                "notes": "Sangat sensitif, hati-hati"
            },
            {
                "id": "neck_dimple",
                "name": "Lekuk Leher",
                "description": "Lekuk antara leher dan bahu",
                "sensitivity": 9,
                "notes": "Sweet spot, sangat sensitif"
            },
            {
                "id": "neck_trapezius",
                "name": "Otot Trapezius",
                "description": "Otot antara leher dan bahu",
                "sensitivity": 6,
                "notes": "Pijatan terasa nyaman"
            },
            {
                "id": "neck_adams_apple",
                "name": "Jakun",
                "description": "Area jakun (khusus pria)",
                "sensitivity": 5,
                "notes": "Sensitif untuk pria"
            }
        ]
        
        # =========================================================================
        # CHEST AREAS (12 areas)
        # =========================================================================
        self.chest_areas = [
            {
                "id": "chest_upper",
                "name": "Dada Atas",
                "description": "Dada bagian atas",
                "sensitivity": 5,
                "notes": "Elusan atau ciuman"
            },
            {
                "id": "chest_center",
                "name": "Dada Tengah",
                "description": "Dada bagian tengah",
                "sensitivity": 5,
                "notes": "Area netral"
            },
            {
                "id": "chest_lower",
                "name": "Dada Bawah",
                "description": "Dada bagian bawah",
                "sensitivity": 6,
                "notes": "Dekat dengan area sensitif"
            },
            {
                "id": "chest_left",
                "name": "Dada Kiri",
                "description": "Dada sisi kiri",
                "sensitivity": 5,
                "notes": "Dekat dengan jantung"
            },
            {
                "id": "chest_right",
                "name": "Dada Kanan",
                "description": "Dada sisi kanan",
                "sensitivity": 5,
                "notes": "Simetris dengan kiri"
            },
            {
                "id": "nipple_left",
                "name": "Puting Kiri",
                "description": "Puting susu kiri",
                "sensitivity": 9,
                "notes": "Sangat sensitif, untuk rangsangan"
            },
            {
                "id": "nipple_right",
                "name": "Puting Kanan",
                "description": "Puting susu kanan",
                "sensitivity": 9,
                "notes": "Sangat sensitif, untuk rangsangan"
            },
            {
                "id": "areola_left",
                "name": "Areola Kiri",
                "description": "Area sekitar puting kiri",
                "sensitivity": 8,
                "notes": "Sensitif, bisa dijilat"
            },
            {
                "id": "areola_right",
                "name": "Areola Kanan",
                "description": "Area sekitar puting kanan",
                "sensitivity": 8,
                "notes": "Sensitif, bisa dijilat"
            },
            {
                "id": "chest_side_left",
                "name": "Samping Dada Kiri",
                "description": "Samping dada kiri",
                "sensitivity": 6,
                "notes": "Area transisi"
            },
            {
                "id": "chest_side_right",
                "name": "Samping Dada Kanan",
                "description": "Samping dada kanan",
                "sensitivity": 6,
                "notes": "Area transisi"
            },
            {
                "id": "sternum",
                "name": "Tulang Dada",
                "description": "Tulang dada tengah",
                "sensitivity": 4,
                "notes": "Elusan ringan"
            }
        ]
        
        # =========================================================================
        # BACK AREAS (10 areas)
        # =========================================================================
        self.back_areas = [
            {
                "id": "back_upper",
                "name": "Punggung Atas",
                "description": "Punggung bagian atas",
                "sensitivity": 5,
                "notes": "Elusan atau pijatan"
            },
            {
                "id": "back_middle",
                "name": "Punggung Tengah",
                "description": "Punggung bagian tengah",
                "sensitivity": 5,
                "notes": "Area luas untuk elusan"
            },
            {
                "id": "back_lower",
                "name": "Punggung Bawah",
                "description": "Punggung bagian bawah",
                "sensitivity": 6,
                "notes": "Dekat pinggang"
            },
            {
                "id": "spine",
                "name": "Tulang Belakang",
                "description": "Sepanjang tulang belakang",
                "sensitivity": 7,
                "notes": "Elusan dari atas ke bawah"
            },
            {
                "id": "shoulder_blade_left",
                "name": "Tulang Belikat Kiri",
                "description": "Tulang belikat kiri",
                "sensitivity": 5,
                "notes": "Pijatan area ini nyaman"
            },
            {
                "id": "shoulder_blade_right",
                "name": "Tulang Belikat Kanan",
                "description": "Tulang belikat kanan",
                "sensitivity": 5,
                "notes": "Pijatan area ini nyaman"
            },
            {
                "id": "waist_back",
                "name": "Pinggang Belakang",
                "description": "Pinggang sisi belakang",
                "sensitivity": 6,
                "notes": "Area sensitif saat dipegang"
            },
            {
                "id": "hip_back_left",
                "name": "Pinggul Belakang Kiri",
                "description": "Pinggul sisi belakang kiri",
                "sensitivity": 6,
                "notes": "Dekat dengan bokong"
            },
            {
                "id": "hip_back_right",
                "name": "Pinggul Belakang Kanan",
                "description": "Pinggul sisi belakang kanan",
                "sensitivity": 6,
                "notes": "Dekat dengan bokong"
            },
            {
                "id": "tailbone",
                "name": "Tulang Ekor",
                "description": "Tulang ekor",
                "sensitivity": 7,
                "notes": "Area sensitif, hati-hati"
            }
        ]
        
        # =========================================================================
        # ARMS AREAS (12 areas)
        # =========================================================================
        self.arms_areas = [
            {
                "id": "shoulder_left",
                "name": "Bahu Kiri",
                "description": "Bahu kiri",
                "sensitivity": 5,
                "notes": "Pijatan atau ciuman"
            },
            {
                "id": "shoulder_right",
                "name": "Bahu Kanan",
                "description": "Bahu kanan",
                "sensitivity": 5,
                "notes": "Pijatan atau ciuman"
            },
            {
                "id": "armpit_left",
                "name": "Ketiak Kiri",
                "description": "Ketiak kiri",
                "sensitivity": 7,
                "notes": "Sensitif, geli"
            },
            {
                "id": "armpit_right",
                "name": "Ketiak Kanan",
                "description": "Ketiak kanan",
                "sensitivity": 7,
                "notes": "Sensitif, geli"
            },
            {
                "id": "bicep_left",
                "name": "Lengan Atas Kiri",
                "description": "Lengan atas kiri",
                "sensitivity": 4,
                "notes": "Elusan"
            },
            {
                "id": "bicep_right",
                "name": "Lengan Atas Kanan",
                "description": "Lengan atas kanan",
                "sensitivity": 4,
                "notes": "Elusan"
            },
            {
                "id": "forearm_left",
                "name": "Lengan Bawah Kiri",
                "description": "Lengan bawah kiri",
                "sensitivity": 5,
                "notes": "Elusan atau ciuman"
            },
            {
                "id": "forearm_right",
                "name": "Lengan Bawah Kanan",
                "description": "Lengan bawah kanan",
                "sensitivity": 5,
                "notes": "Elusan atau ciuman"
            },
            {
                "id": "elbow_left",
                "name": "Siku Kiri",
                "description": "Siku kiri",
                "sensitivity": 3,
                "notes": "Kurang sensitif"
            },
            {
                "id": "elbow_right",
                "name": "Siku Kanan",
                "description": "Siku kanan",
                "sensitivity": 3,
                "notes": "Kurang sensitif"
            },
            {
                "id": "wrist_left",
                "name": "Pergelangan Kiri",
                "description": "Pergelangan tangan kiri",
                "sensitivity": 6,
                "notes": "Area sensitif, nadi"
            },
            {
                "id": "wrist_right",
                "name": "Pergelangan Kanan",
                "description": "Pergelangan tangan kanan",
                "sensitivity": 6,
                "notes": "Area sensitif, nadi"
            }
        ]
        
        # =========================================================================
        # STOMACH AREAS (8 areas)
        # =========================================================================
        self.stomach_areas = [
            {
                "id": "stomach_upper",
                "name": "Perut Atas",
                "description": "Perut bagian atas",
                "sensitivity": 5,
                "notes": "Elusan"
            },
            {
                "id": "stomach_center",
                "name": "Perut Tengah",
                "description": "Perut bagian tengah",
                "sensitivity": 6,
                "notes": "Area sensitif"
            },
            {
                "id": "stomach_lower",
                "name": "Perut Bawah",
                "description": "Perut bagian bawah",
                "sensitivity": 7,
                "notes": "Dekat area intim"
            },
            {
                "id": "belly_button",
                "name": "Pusar",
                "description": "Pusar",
                "sensitivity": 8,
                "notes": "Sangat sensitif untuk beberapa orang"
            },
            {
                "id": "side_waist_left",
                "name": "Samping Pinggang Kiri",
                "description": "Samping pinggang kiri",
                "sensitivity": 7,
                "notes": "Area geli"
            },
            {
                "id": "side_waist_right",
                "name": "Samping Pinggang Kanan",
                "description": "Samping pinggang kanan",
                "sensitivity": 7,
                "notes": "Area geli"
            },
            {
                "id": "ribs_left",
                "name": "Tulang Rusuk Kiri",
                "description": "Tulang rusuk kiri",
                "sensitivity": 5,
                "notes": "Hati-hati"
            },
            {
                "id": "ribs_right",
                "name": "Tulang Rusuk Kanan",
                "description": "Tulang rusuk kanan",
                "sensitivity": 5,
                "notes": "Hati-hati"
            }
        ]
        
        # =========================================================================
        # HIPS AREAS (8 areas)
        # =========================================================================
        self.hips_areas = [
            {
                "id": "hip_bone_left",
                "name": "Tulang Pinggul Kiri",
                "description": "Tulang pinggul kiri",
                "sensitivity": 6,
                "notes": "Area yang menonjol"
            },
            {
                "id": "hip_bone_right",
                "name": "Tulang Pinggul Kanan",
                "description": "Tulang pinggul kanan",
                "sensitivity": 6,
                "notes": "Area yang menonjol"
            },
            {
                "id": "hip_side_left",
                "name": "Samping Pinggul Kiri",
                "description": "Samping pinggul kiri",
                "sensitivity": 6,
                "notes": "Area untuk dipegang"
            },
            {
                "id": "hip_side_right",
                "name": "Samping Pinggul Kanan",
                "description": "Samping pinggul kanan",
                "sensitivity": 6,
                "notes": "Area untuk dipegang"
            },
            {
                "id": "buttock_upper_left",
                "name": "Bokong Atas Kiri",
                "description": "Bokong bagian atas kiri",
                "sensitivity": 7,
                "notes": "Area sensitif"
            },
            {
                "id": "buttock_upper_right",
                "name": "Bokong Atas Kanan",
                "description": "Bokong bagian atas kanan",
                "sensitivity": 7,
                "notes": "Area sensitif"
            },
            {
                "id": "buttock_lower_left",
                "name": "Bokong Bawah Kiri",
                "description": "Bokong bagian bawah kiri",
                "sensitivity": 7,
                "notes": "Area sensitif"
            },
            {
                "id": "buttock_lower_right",
                "name": "Bokong Bawah Kanan",
                "description": "Bokong bagian bawah kanan",
                "sensitivity": 7,
                "notes": "Area sensitif"
            }
        ]
        
        # =========================================================================
        # LEGS AREAS (14 areas)
        # =========================================================================
        self.legs_areas = [
            {
                "id": "thigh_front_left",
                "name": "Paha Depan Kiri",
                "description": "Paha bagian depan kiri",
                "sensitivity": 6,
                "notes": "Elusan"
            },
            {
                "id": "thigh_front_right",
                "name": "Paha Depan Kanan",
                "description": "Paha bagian depan kanan",
                "sensitivity": 6,
                "notes": "Elusan"
            },
            {
                "id": "thigh_inner_left",
                "name": "Paha Dalam Kiri",
                "description": "Paha bagian dalam kiri",
                "sensitivity": 8,
                "notes": "Sangat sensitif, area intim"
            },
            {
                "id": "thigh_inner_right",
                "name": "Paha Dalam Kanan",
                "description": "Paha bagian dalam kanan",
                "sensitivity": 8,
                "notes": "Sangat sensitif, area intim"
            },
            {
                "id": "thigh_outer_left",
                "name": "Paha Luar Kiri",
                "description": "Paha bagian luar kiri",
                "sensitivity": 5,
                "notes": "Kurang sensitif"
            },
            {
                "id": "thigh_outer_right",
                "name": "Paha Luar Kanan",
                "description": "Paha bagian luar kanan",
                "sensitivity": 5,
                "notes": "Kurang sensitif"
            },
            {
                "id": "knee_left",
                "name": "Lutut Kiri",
                "description": "Lutut kiri",
                "sensitivity": 3,
                "notes": "Kurang sensitif"
            },
            {
                "id": "knee_right",
                "name": "Lutut Kanan",
                "description": "Lutut kanan",
                "sensitivity": 3,
                "notes": "Kurang sensitif"
            },
            {
                "id": "calf_left",
                "name": "Betis Kiri",
                "description": "Betis kiri",
                "sensitivity": 4,
                "notes": "Elusan atau pijatan"
            },
            {
                "id": "calf_right",
                "name": "Betis Kanan",
                "description": "Betis kanan",
                "sensitivity": 4,
                "notes": "Elusan atau pijatan"
            },
            {
                "id": "shin_left",
                "name": "Tulang Kering Kiri",
                "description": "Tulang kering kiri",
                "sensitivity": 3,
                "notes": "Hati-hati"
            },
            {
                "id": "shin_right",
                "name": "Tulang Kering Kanan",
                "description": "Tulang kering kanan",
                "sensitivity": 3,
                "notes": "Hati-hati"
            },
            {
                "id": "ankle_left",
                "name": "Pergelangan Kaki Kiri",
                "description": "Pergelangan kaki kiri",
                "sensitivity": 5,
                "notes": "Elusan"
            },
            {
                "id": "ankle_right",
                "name": "Pergelangan Kaki Kanan",
                "description": "Pergelangan kaki kanan",
                "sensitivity": 5,
                "notes": "Elusan"
            }
        ]
        
        # =========================================================================
        # FEET AREAS (8 areas)
        # =========================================================================
        self.feet_areas = [
            {
                "id": "foot_top_left",
                "name": "Punggung Kaki Kiri",
                "description": "Punggung kaki kiri",
                "sensitivity": 4,
                "notes": "Elusan"
            },
            {
                "id": "foot_top_right",
                "name": "Punggung Kaki Kanan",
                "description": "Punggung kaki kanan",
                "sensitivity": 4,
                "notes": "Elusan"
            },
            {
                "id": "foot_sole_left",
                "name": "Telapak Kaki Kiri",
                "description": "Telapak kaki kiri",
                "sensitivity": 6,
                "notes": "Sensitif, geli"
            },
            {
                "id": "foot_sole_right",
                "name": "Telapak Kaki Kanan",
                "description": "Telapak kaki kanan",
                "sensitivity": 6,
                "notes": "Sensitif, geli"
            },
            {
                "id": "toes_left",
                "name": "Jari Kaki Kiri",
                "description": "Jari-jari kaki kiri",
                "sensitivity": 5,
                "notes": "Beberapa orang sensitif"
            },
            {
                "id": "toes_right",
                "name": "Jari Kaki Kanan",
                "description": "Jari-jari kaki kanan",
                "sensitivity": 5,
                "notes": "Beberapa orang sensitif"
            },
            {
                "id": "heel_left",
                "name": "Tumit Kiri",
                "description": "Tumit kaki kiri",
                "sensitivity": 3,
                "notes": "Kurang sensitif"
            },
            {
                "id": "heel_right",
                "name": "Tumit Kanan",
                "description": "Tumit kaki kanan",
                "sensitivity": 3,
                "notes": "Kurang sensitif"
            }
        ]
        
        # =========================================================================
        # SPECIAL AREAS (10 areas - untuk BDSM/fetish)
        # =========================================================================
        self.special_areas = [
            {
                "id": "special_ear",
                "name": "Ear Kissing",
                "description": "Ciuman dan bisikan di telinga",
                "sensitivity": 9,
                "notes": "Untuk foreplay"
            },
            {
                "id": "special_neck",
                "name": "Neck Biting",
                "description": "Gigitan ringan di leher",
                "sensitivity": 8,
                "notes": "Bisa meninggalkan bekas"
            },
            {
                "id": "special_spine",
                "name": "Spine Tracing",
                "description": "Elusan sepanjang tulang belakang",
                "sensitivity": 7,
                "notes": "Dengan ujung jari"
            },
            {
                "id": "special_waist",
                "name": "Waist Holding",
                "description": "Memegang pinggang erat",
                "sensitivity": 7,
                "notes": "Saat intim"
            },
            {
                "id": "special_inner_thigh",
                "name": "Inner Thigh Kiss",
                "description": "Ciuman di paha dalam",
                "sensitivity": 9,
                "notes": "Membangun gairah"
            },
            {
                "id": "special_buttock",
                "name": "Buttock Caress",
                "description": "Elusan di bokong",
                "sensitivity": 7,
                "notes": "Bisa dengan tekanan"
            },
            {
                "id": "special_hip_grip",
                "name": "Hip Grip",
                "description": "Memegang pinggul erat",
                "sensitivity": 8,
                "notes": "Saat doggy style"
            },
            {
                "id": "special_shoulder_bite",
                "name": "Shoulder Bite",
                "description": "Gigitan di bahu",
                "sensitivity": 6,
                "notes": "Saat climax"
            },
            {
                "id": "special_hair_pull",
                "name": "Hair Pulling",
                "description": "Menarik rambut pelan",
                "sensitivity": 7,
                "notes": "Untuk dominasi"
            },
            {
                "id": "special_wrist_grip",
                "name": "Wrist Grip",
                "description": "Memegang pergelangan tangan",
                "sensitivity": 6,
                "notes": "Saat missionaris"
            }
        ]
        
        # Gabungkan semua area
        self.all_areas = (
            self.head_areas +
            self.neck_areas +
            self.chest_areas +
            self.back_areas +
            self.arms_areas +
            self.stomach_areas +
            self.hips_areas +
            self.legs_areas +
            self.feet_areas +
            self.special_areas
        )
        
        logger.info(f"✅ AreaDatabase initialized: {len(self.all_areas)} areas")
        
    # =========================================================================
    # GET AREAS
    # =========================================================================
    
    def get_all_areas(self) -> List[Dict]:
        """Get all areas"""
        return self.all_areas
        
    def get_areas_by_category(self, category: AreaCategory) -> List[Dict]:
        """Get areas by category"""
        if category == AreaCategory.HEAD:
            return self.head_areas
        elif category == AreaCategory.NECK:
            return self.neck_areas
        elif category == AreaCategory.CHEST:
            return self.chest_areas
        elif category == AreaCategory.BACK:
            return self.back_areas
        elif category == AreaCategory.ARMS:
            return self.arms_areas
        elif category == AreaCategory.STOMACH:
            return self.stomach_areas
        elif category == AreaCategory.HIPS:
            return self.hips_areas
        elif category == AreaCategory.LEGS:
            return self.legs_areas
        elif category == AreaCategory.FEET:
            return self.feet_areas
        elif category == AreaCategory.SPECIAL:
            return self.special_areas
        else:
            return []
            
    def get_area_by_id(self, area_id: str) -> Optional[Dict]:
        """Get area by ID"""
        for area in self.all_areas:
            if area['id'] == area_id:
                return area
        return None
        
    def get_areas_by_sensitivity(self, min_sensitivity: int = 7, max_sensitivity: int = 10) -> List[Dict]:
        """Get areas by sensitivity range"""
        return [
            area for area in self.all_areas
            if min_sensitivity <= area['sensitivity'] <= max_sensitivity
        ]
        
    def get_random_area(self, category: Optional[AreaCategory] = None) -> Dict:
        """Get random area"""
        if category:
            areas = self.get_areas_by_category(category)
        else:
            areas = self.all_areas
            
        return random.choice(areas)
        
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get area statistics"""
        return {
            "total_areas": len(self.all_areas),
            "by_category": {
                "head": len(self.head_areas),
                "neck": len(self.neck_areas),
                "chest": len(self.chest_areas),
                "back": len(self.back_areas),
                "arms": len(self.arms_areas),
                "stomach": len(self.stomach_areas),
                "hips": len(self.hips_areas),
                "legs": len(self.legs_areas),
                "feet": len(self.feet_areas),
                "special": len(self.special_areas)
            },
            "avg_sensitivity": sum(a['sensitivity'] for a in self.all_areas) / len(self.all_areas),
            "high_sensitivity": len([a for a in self.all_areas if a['sensitivity'] >= 8]),
            "low_sensitivity": len([a for a in self.all_areas if a['sensitivity'] <= 4])
        }
        
    def format_area_info(self, area: Dict) -> str:
        """Format area info for display"""
        return (
            f"📍 **{area['name']}**\n"
            f"Sensitivity: {'🔴' * area['sensitivity']}{'⚪' * (10 - area['sensitivity'])} ({area['sensitivity']}/10)\n"
            f"_{area['description']}_\n"
            f"💡 {area['notes']}"
        )


# Global instance
_area_database = None


def get_area_database() -> AreaDatabase:
    """Get global area database instance"""
    global _area_database
    if _area_database is None:
        _area_database = AreaDatabase()
    return _area_database


__all__ = ['AreaDatabase', 'AreaCategory', 'get_area_database']
