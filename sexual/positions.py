#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - POSITIONS DATABASE
=============================================================================
- 50+ sex positions (data only)
- Kode tidak explicit, hanya data untuk AI engine
- DeepSeek akan membuat deskripsi explicit saat runtime
"""

import random
import logging
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class DifficultyLevel(str, Enum):
    """Tingkat kesulitan posisi"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class IntensityLevel(str, Enum):
    """Tingkat intensitas"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


class PositionDatabase:
    """
    Database 50+ posisi sex
    Hanya berisi data dasar, deskripsi explicit akan digenerate oleh AI
    """
    
    def __init__(self):
        # =========================================================================
        # MISSIONARY POSITIONS (Variations)
        # =========================================================================
        self.missionary_positions = [
            {
                "id": "missionary_classic",
                "name": "Missionary Classic",
                "category": "missionary",
                "difficulty": DifficultyLevel.EASY,
                "intensity": IntensityLevel.MEDIUM,
                "description": "Posisi klasik dengan pasangan di bawah",
                "tags": ["romantic", "classic", "intimate"],
                "compatible_roles": ["all"],
                "climax_probability": 0.7,
                "energy_cost": 0.3,
                "eye_contact": True,
                "kissing_possible": True,
                "talking_possible": True,
                "variations": ["legs_up", "pillow_under_hips", "close_embrace"]
            },
            {
                "id": "missionary_legs_up",
                "name": "Legs Up Missionary",
                "category": "missionary",
                "difficulty": DifficultyLevel.MEDIUM,
                "intensity": IntensityLevel.HIGH,
                "description": "Kaki diangkat ke atas, penetrasi lebih dalam",
                "tags": ["deep", "intense", "romantic"],
                "compatible_roles": ["all"],
                "climax_probability": 0.8,
                "energy_cost": 0.4,
                "eye_contact": True,
                "kissing_possible": True,
                "talking_possible": True,
                "variations": ["ankles_on_shoulders", "knees_to_chest"]
            },
            {
                "id": "missionary_pillow",
                "name": "Pillow Under Hips",
                "category": "missionary",
                "difficulty": DifficultyLevel.EASY,
                "intensity": IntensityLevel.HIGH,
                "description": "Bantal di bawah pinggul untuk sudut lebih baik",
                "tags": ["comfortable", "deep", "angled"],
                "compatible_roles": ["all"],
                "climax_probability": 0.75,
                "energy_cost": 0.3,
                "eye_contact": True,
                "kissing_possible": True,
                "talking_possible": True,
                "variations": []
            },
            {
                "id": "missionary_wrap_around",
                "name": "Wrap Around",
                "category": "missionary",
                "difficulty": DifficultyLevel.MEDIUM,
                "intensity": IntensityLevel.MEDIUM,
                "description": "Kaki melingkar di pinggang",
                "tags": ["close", "intimate", "romantic"],
                "compatible_roles": ["all"],
                "climax_probability": 0.7,
                "energy_cost": 0.4,
                "eye_contact": True,
                "kissing_possible": True,
                "talking_possible": True,
                "variations": []
            }
        ]
        
        # =========================================================================
        # DOGGY STYLE POSITIONS
        # =========================================================================
        self.doggy_positions = [
            {
                "id": "doggy_classic",
                "name": "Classic Doggy",
                "category": "doggy",
                "difficulty": DifficultyLevel.EASY,
                "intensity": IntensityLevel.HIGH,
                "description": "Posisi dari belakang, tangan menopang",
                "tags": ["intense", "deep", "animalistic"],
                "compatible_roles": ["all"],
                "climax_probability": 0.8,
                "energy_cost": 0.5,
                "eye_contact": False,
                "kissing_possible": False,
                "talking_possible": True,
                "variations": ["flat", "arched", "face_down"]
            },
            {
                "id": "doggy_flat",
                "name": "Flat Doggy",
                "category": "doggy",
                "difficulty": DifficultyLevel.MEDIUM,
                "intensity": IntensityLevel.MEDIUM,
                "description": "Badan lebih rendah, tangan dan lutut",
                "tags": ["stable", "comfortable"],
                "compatible_roles": ["all"],
                "climax_probability": 0.7,
                "energy_cost": 0.4,
                "eye_contact": False,
                "kissing_possible": False,
                "talking_possible": True,
                "variations": []
            },
            {
                "id": "doggy_arched",
                "name": "Arched Doggy",
                "category": "doggy",
                "difficulty": DifficultyLevel.HARD,
                "intensity": IntensityLevel.EXTREME,
                "description": "Punggung melengkung, penetrasi maksimal",
                "tags": ["deep", "intense", "extreme"],
                "compatible_roles": ["all"],
                "climax_probability": 0.9,
                "energy_cost": 0.6,
                "eye_contact": False,
                "kissing_possible": False,
                "talking_possible": True,
                "variations": []
            },
            {
                "id": "doggy_face_down",
                "name": "Face Down Doggy",
                "category": "doggy",
                "difficulty": DifficultyLevel.MEDIUM,
                "intensity": IntensityLevel.HIGH,
                "description": "Wajah menempel di bantal",
                "tags": ["submissive", "intense"],
                "compatible_roles": ["all"],
                "climax_probability": 0.8,
                "energy_cost": 0.5,
                "eye_contact": False,
                "kissing_possible": False,
                "talking_possible": False,
                "variations": []
            }
        ]
        
        # =========================================================================
        # WOMAN ON TOP POSITIONS
        # =========================================================================
        self.woman_top_positions = [
            {
                "id": "cowgirl_classic",
                "name": "Classic Cowgirl",
                "category": "woman_top",
                "difficulty": DifficultyLevel.MEDIUM,
                "intensity": IntensityLevel.MEDIUM,
                "description": "Wanita di atas, menghadap pasangan",
                "tags": ["dominant", "intimate", "eye_contact"],
                "compatible_roles": ["all"],
                "climax_probability": 0.7,
                "energy_cost": 0.5,
                "eye_contact": True,
                "kissing_possible": True,
                "talking_possible": True,
                "variations": ["leaning_forward", "upright", "bouncing"]
            },
            {
                "id": "reverse_cowgirl",
                "name": "Reverse Cowgirl",
                "category": "woman_top",
                "difficulty": DifficultyLevel.HARD,
                "intensity": IntensityLevel.HIGH,
                "description": "Wanita di atas, membelakangi pasangan",
                "tags": ["dominant", "different_view", "exciting"],
                "compatible_roles": ["all"],
                "climax_probability": 0.75,
                "energy_cost": 0.6,
                "eye_contact": False,
                "kissing_possible": False,
                "talking_possible": True,
                "variations": ["leaning_forward", "upright"]
            },
            {
                "id": "cowgirl_leaning",
                "name": "Leaning Cowgirl",
                "category": "woman_top",
                "difficulty": DifficultyLevel.MEDIUM,
                "intensity": IntensityLevel.MEDIUM,
                "description": "Membungkuk ke depan untuk ciuman",
                "tags": ["romantic", "intimate"],
                "compatible_roles": ["all"],
                "climax_probability": 0.7,
                "energy_cost": 0.5,
                "eye_contact": True,
                "kissing_possible": True,
                "talking_possible": True,
                "variations": []
            },
            {
                "id": "cowgirl_upright",
                "name": "Upright Cowgirl",
                "category": "woman_top",
                "difficulty": DifficultyLevel.HARD,
                "intensity": IntensityLevel.HIGH,
                "description": "Duduk tegak, kontrol penuh",
                "tags": ["dominant", "control", "show_off"],
                "compatible_roles": ["all"],
                "climax_probability": 0.8,
                "energy_cost": 0.7,
                "eye_contact": True,
                "kissing_possible": False,
                "talking_possible": True,
                "variations": []
            }
        ]
        
        # =========================================================================
        # SITTING POSITIONS
        # =========================================================================
        self.sitting_positions = [
            {
                "id": "lap_dance",
                "name": "Lap Dance",
                "category": "sitting",
                "difficulty": DifficultyLevel.MEDIUM,
                "intensity": IntensityLevel.MEDIUM,
                "description": "Wanita duduk di pangkuan, berhadapan",
                "tags": ["intimate", "romantic", "slow"],
                "compatible_roles": ["all"],
                "climax_probability": 0.6,
                "energy_cost": 0.3,
                "eye_contact": True,
                "kissing_possible": True,
                "talking_possible": True,
                "variations": ["facing", "back_facing", "side_saddle"]
            },
            {
                "id": "lotus",
                "name": "Lotus",
                "category": "sitting",
                "difficulty": DifficultyLevel.HARD,
                "intensity": IntensityLevel.MEDIUM,
                "description": "Kaki saling melingkar, duduk berhadapan",
                "tags": ["yoga", "intimate", "spiritual"],
                "compatible_roles": ["all"],
                "climax_probability": 0.5,
                "energy_cost": 0.4,
                "eye_contact": True,
                "kissing_possible": True,
                "talking_possible": True,
                "variations": []
            },
            {
                "id": "chair_position",
                "name": "Chair Position",
                "category": "sitting",
                "difficulty": DifficultyLevel.MEDIUM,
                "intensity": IntensityLevel.MEDIUM,
                "description": "Pria duduk di kursi, wanita di atas",
                "tags": ["furniture", "versatile"],
                "compatible_roles": ["all"],
                "climax_probability": 0.7,
                "energy_cost": 0.4,
                "eye_contact": True,
                "kissing_possible": True,
                "talking_possible": True,
                "variations": ["facing", "back_facing"]
            }
        ]
        
        # =========================================================================
        # STANDING POSITIONS
        # =========================================================================
        self.standing_positions = [
            {
                "id": "standing_doggy",
                "name": "Standing Doggy",
                "category": "standing",
                "difficulty": DifficultyLevel.MEDIUM,
                "intensity": IntensityLevel.HIGH,
                "description": "Berdiri, pasangan membungkuk",
                "tags": ["quick", "intense", "wall"],
                "compatible_roles": ["all"],
                "climax_probability": 0.7,
                "energy_cost": 0.5,
                "eye_contact": False,
                "kissing_possible": False,
                "talking_possible": True,
                "variations": ["wall_support", "table_support"]
            },
            {
                "id": "standing_missionary",
                "name": "Standing Missionary",
                "category": "standing",
                "difficulty": DifficultyLevel.HARD,
                "intensity": IntensityLevel.HIGH,
                "description": "Berhadapan, wanita digendong",
                "tags": ["romantic", "intense", "acrobatic"],
                "compatible_roles": ["all"],
                "climax_probability": 0.7,
                "energy_cost": 0.8,
                "eye_contact": True,
                "kissing_possible": True,
                "talking_possible": True,
                "variations": ["wall_support", "full_lift"]
            },
            {
                "id": "wall_position",
                "name": "Wall Position",
                "category": "standing",
                "difficulty": DifficultyLevel.EASY,
                "intensity": IntensityLevel.HIGH,
                "description": "Wanita bersandar di dinding",
                "tags": ["quick", "wall", "support"],
                "compatible_roles": ["all"],
                "climax_probability": 0.7,
                "energy_cost": 0.4,
                "eye_contact": True,
                "kissing_possible": True,
                "talking_possible": True,
                "variations": ["face_to_wall", "back_to_wall"]
            }
        ]
        
        # =========================================================================
        # SIDE LYING POSITIONS
        # =========================================================================
        self.side_positions = [
            {
                "id": "spooning",
                "name": "Spooning",
                "category": "side",
                "difficulty": DifficultyLevel.EASY,
                "intensity": IntensityLevel.LOW,
                "description": "Berbaring miring, seperti sendok",
                "tags": ["cuddly", "intimate", "slow", "morning"],
                "compatible_roles": ["all"],
                "climax_probability": 0.5,
                "energy_cost": 0.2,
                "eye_contact": False,
                "kissing_possible": False,
                "talking_possible": True,
                "variations": ["spooning", "reverse_spooning"]
            },
            {
                "id": "scissors",
                "name": "Scissors",
                "category": "side",
                "difficulty": DifficultyLevel.MEDIUM,
                "intensity": IntensityLevel.MEDIUM,
                "description": "Kaki saling mengunci seperti gunting",
                "tags": ["different", "interesting"],
                "compatible_roles": ["all"],
                "climax_probability": 0.6,
                "energy_cost": 0.3,
                "eye_contact": True,
                "kissing_possible": True,
                "talking_possible": True,
                "variations": []
            },
            {
                "id": "side_saddle",
                "name": "Side Saddle",
                "category": "side",
                "difficulty": DifficultyLevel.MEDIUM,
                "intensity": IntensityLevel.MEDIUM,
                "description": "Satu kaki di atas, berbaring miring",
                "tags": ["comfortable", "different"],
                "compatible_roles": ["all"],
                "climax_probability": 0.6,
                "energy_cost": 0.3,
                "eye_contact": True,
                "kissing_possible": True,
                "talking_possible": True,
                "variations": []
            }
        ]
        
        # =========================================================================
        # KAMA SUTRA POSITIONS
        # =========================================================================
        self.kama_positions = [
            {
                "id": "kama_congress",
                "name": "Congress of the Cow",
                "category": "kama_sutra",
                "difficulty": DifficultyLevel.HARD,
                "intensity": IntensityLevel.HIGH,
                "description": "Posisi kama sutra klasik",
                "tags": ["kama_sutra", "classic", "traditional"],
                "compatible_roles": ["all"],
                "climax_probability": 0.7,
                "energy_cost": 0.6,
                "eye_contact": True,
                "kissing_possible": True,
                "talking_possible": True,
                "variations": []
            },
            {
                "id": "kama_lotus",
                "name": "Lotus of Love",
                "category": "kama_sutra",
                "difficulty": DifficultyLevel.EXPERT,
                "intensity": IntensityLevel.MEDIUM,
                "description": "Posisi lotus untuk koneksi spiritual",
                "tags": ["kama_sutra", "spiritual", "intimate"],
                "compatible_roles": ["all"],
                "climax_probability": 0.6,
                "energy_cost": 0.5,
                "eye_contact": True,
                "kissing_possible": True,
                "talking_possible": True,
                "variations": []
            },
            {
                "id": "kama_suspended",
                "name": "Suspended Congress",
                "category": "kama_sutra",
                "difficulty": DifficultyLevel.EXPERT,
                "intensity": IntensityLevel.EXTREME,
                "description": "Posisi akrobatik kama sutra",
                "tags": ["kama_sutra", "acrobatic", "extreme"],
                "compatible_roles": ["all"],
                "climax_probability": 0.8,
                "energy_cost": 0.9,
                "eye_contact": False,
                "kissing_possible": False,
                "talking_possible": False,
                "variations": []
            }
        ]
        
        # =========================================================================
        # FURNITURE POSITIONS
        # =========================================================================
        self.furniture_positions = [
            {
                "id": "table_top",
                "name": "Table Top",
                "category": "furniture",
                "difficulty": DifficultyLevel.EASY,
                "intensity": IntensityLevel.HIGH,
                "description": "Wanita di atas meja",
                "tags": ["furniture", "quick", "intense"],
                "compatible_roles": ["all"],
                "climax_probability": 0.8,
                "energy_cost": 0.4,
                "eye_contact": True,
                "kissing_possible": True,
                "talking_possible": True,
                "variations": ["lying", "sitting", "edge"]
            },
            {
                "id": "desk_duty",
                "name": "Desk Duty",
                "category": "furniture",
                "difficulty": DifficultyLevel.MEDIUM,
                "intensity": IntensityLevel.HIGH,
                "description": "Membungkuk di atas meja",
                "tags": ["furniture", "office", "intense"],
                "compatible_roles": ["all"],
                "climax_probability": 0.8,
                "energy_cost": 0.5,
                "eye_contact": False,
                "kissing_possible": False,
                "talking_possible": True,
                "variations": []
            },
            {
                "id": "sofa_edge",
                "name": "Sofa Edge",
                "category": "furniture",
                "difficulty": DifficultyLevel.EASY,
                "intensity": IntensityLevel.MEDIUM,
                "description": "Di tepi sofa",
                "tags": ["furniture", "comfortable"],
                "compatible_roles": ["all"],
                "climax_probability": 0.7,
                "energy_cost": 0.3,
                "eye_contact": True,
                "kissing_possible": True,
                "talking_possible": True,
                "variations": []
            }
        ]
        
        # =========================================================================
        # ORAL POSITIONS
        # =========================================================================
        self.oral_positions = [
            {
                "id": "oral_kneeling",
                "name": "Kneeling Oral",
                "category": "oral",
                "difficulty": DifficultyLevel.EASY,
                "intensity": IntensityLevel.MEDIUM,
                "description": "Berlutut di depan pasangan",
                "tags": ["oral", "submissive"],
                "compatible_roles": ["all"],
                "climax_probability": 0.7,
                "energy_cost": 0.3,
                "eye_contact": True,
                "kissing_possible": False,
                "talking_possible": False,
                "variations": ["standing", "sitting"]
            },
            {
                "id": "oral_69",
                "name": "69",
                "category": "oral",
                "difficulty": DifficultyLevel.MEDIUM,
                "intensity": IntensityLevel.HIGH,
                "description": "Saling memuaskan secara bersamaan",
                "tags": ["oral", "mutual", "intense"],
                "compatible_roles": ["all"],
                "climax_probability": 0.8,
                "energy_cost": 0.5,
                "eye_contact": False,
                "kissing_possible": False,
                "talking_possible": False,
                "variations": ["side_lying", "top_bottom"]
            },
            {
                "id": "oral_lying",
                "name": "Lying Oral",
                "category": "oral",
                "difficulty": DifficultyLevel.EASY,
                "intensity": IntensityLevel.LOW,
                "description": "Pasangan berbaring, memberikan oral",
                "tags": ["oral", "relaxing"],
                "compatible_roles": ["all"],
                "climax_probability": 0.6,
                "energy_cost": 0.2,
                "eye_contact": False,
                "kissing_possible": False,
                "talking_possible": True,
                "variations": []
            }
        ]
        
        # Gabungkan semua posisi
        self.all_positions = (
            self.missionary_positions +
            self.doggy_positions +
            self.woman_top_positions +
            self.sitting_positions +
            self.standing_positions +
            self.side_positions +
            self.kama_positions +
            self.furniture_positions +
            self.oral_positions
        )
        
        logger.info(f"✅ PositionDatabase initialized: {len(self.all_positions)} positions")
        
    # =========================================================================
    # GET POSITIONS
    # =========================================================================
    
    def get_all_positions(self) -> List[Dict]:
        """Get all positions"""
        return self.all_positions
        
    def get_positions_by_category(self, category: str) -> List[Dict]:
        """Get positions by category"""
        categories = {
            "missionary": self.missionary_positions,
            "doggy": self.doggy_positions,
            "woman_top": self.woman_top_positions,
            "sitting": self.sitting_positions,
            "standing": self.standing_positions,
            "side": self.side_positions,
            "kama_sutra": self.kama_positions,
            "furniture": self.furniture_positions,
            "oral": self.oral_positions,
        }
        return categories.get(category, [])
        
    def get_position_by_id(self, position_id: str) -> Optional[Dict]:
        """Get position by ID"""
        for pos in self.all_positions:
            if pos['id'] == position_id:
                return pos
        return None
        
    def get_random_position(self, category: Optional[str] = None) -> Dict:
        """Get random position"""
        if category:
            positions = self.get_positions_by_category(category)
            if positions:
                return random.choice(positions)
                
        return random.choice(self.all_positions)
        
    def get_positions_by_difficulty(self, difficulty: DifficultyLevel) -> List[Dict]:
        """Get positions by difficulty level"""
        return [p for p in self.all_positions if p['difficulty'] == difficulty]
        
    def get_positions_by_intensity(self, intensity: IntensityLevel) -> List[Dict]:
        """Get positions by intensity level"""
        return [p for p in self.all_positions if p['intensity'] == intensity]
        
    def get_positions_by_tag(self, tag: str) -> List[Dict]:
        """Get positions by tag"""
        return [p for p in self.all_positions if tag in p.get('tags', [])]
        
    # =========================================================================
    # POSITION COMPATIBILITY
    # =========================================================================
    
    def get_compatible_positions(self, role: str, intimacy_level: int) -> List[Dict]:
        """
        Get positions compatible with role and intimacy level
        
        Args:
            role: Role name
            intimacy_level: Current intimacy level
            
        Returns:
            List of compatible positions
        """
        compatible = []
        
        for pos in self.all_positions:
            # Check role compatibility
            if 'all' in pos['compatible_roles'] or role in pos['compatible_roles']:
                
                # Check intimacy requirement
                # Level 7+ for all positions
                if intimacy_level >= 7:
                    compatible.append(pos)
                # Level 1-6: only easy positions
                elif pos['difficulty'] == DifficultyLevel.EASY:
                    compatible.append(pos)
                    
        return compatible
        
    def get_recommended_position(self, role: str, intimacy_level: int, 
                                  previous_positions: List[str] = None) -> Dict:
        """
        Get recommended position based on context
        
        Args:
            role: Role name
            intimacy_level: Current intimacy level
            previous_positions: List of previously used positions
            
        Returns:
            Recommended position
        """
        compatible = self.get_compatible_positions(role, intimacy_level)
        
        if not compatible:
            return self.get_random_position()
            
        # Filter out recently used
        if previous_positions:
            compatible = [p for p in compatible if p['id'] not in previous_positions[:3]]
            
        if not compatible:
            compatible = self.get_compatible_positions(role, intimacy_level)
            
        # Weight by various factors
        weighted = []
        for pos in compatible:
            weight = 1.0
            
            # Higher intensity for higher intimacy
            if intimacy_level >= 10 and pos['intensity'] in [IntensityLevel.HIGH, IntensityLevel.EXTREME]:
                weight *= 1.5
            elif intimacy_level >= 7 and pos['intensity'] == IntensityLevel.MEDIUM:
                weight *= 1.2
                
            # Higher climax probability
            weight *= pos['climax_probability']
            
            weighted.extend([pos] * int(weight * 10))
            
        return random.choice(weighted) if weighted else random.choice(compatible)
        
    # =========================================================================
    # POSITION STATISTICS
    # =========================================================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get position database statistics"""
        return {
            "total_positions": len(self.all_positions),
            "by_category": {
                "missionary": len(self.missionary_positions),
                "doggy": len(self.doggy_positions),
                "woman_top": len(self.woman_top_positions),
                "sitting": len(self.sitting_positions),
                "standing": len(self.standing_positions),
                "side": len(self.side_positions),
                "kama_sutra": len(self.kama_positions),
                "furniture": len(self.furniture_positions),
                "oral": len(self.oral_positions),
            },
            "by_difficulty": {
                "easy": len(self.get_positions_by_difficulty(DifficultyLevel.EASY)),
                "medium": len(self.get_positions_by_difficulty(DifficultyLevel.MEDIUM)),
                "hard": len(self.get_positions_by_difficulty(DifficultyLevel.HARD)),
                "expert": len(self.get_positions_by_difficulty(DifficultyLevel.EXPERT)),
            },
            "by_intensity": {
                "low": len(self.get_positions_by_intensity(IntensityLevel.LOW)),
                "medium": len(self.get_positions_by_intensity(IntensityLevel.MEDIUM)),
                "high": len(self.get_positions_by_intensity(IntensityLevel.HIGH)),
                "extreme": len(self.get_positions_by_intensity(IntensityLevel.EXTREME)),
            }
        }
        
    def format_position_info(self, position: Dict) -> str:
        """Format position info for display (non-explicit)"""
        return (
            f"**{position['name']}**\n"
            f"Kategori: {position['category'].replace('_', ' ').title()}\n"
            f"Difficulty: {position['difficulty'].value} | Intensity: {position['intensity'].value}\n"
            f"Tags: {', '.join(position['tags'])}"
        )


# Global position database instance
_position_db = None


def get_position_database() -> PositionDatabase:
    """Get global position database instance"""
    global _position_db
    if _position_db is None:
        _position_db = PositionDatabase()
    return _position_db


__all__ = ['PositionDatabase', 'get_position_database', 'DifficultyLevel', 'IntensityLevel']
