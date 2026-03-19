#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - SCENE RECOMMENDER
=============================================================================
Memberikan rekomendasi scene/scenario berdasarkan:
- Level intimacy
- Mood bot
- Arah cerita
- Intent user
- Memory yang relevan
=============================================================================
"""

import random
import logging
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class SceneType(str, Enum):
    """Tipe-tipe scene"""
    GREETING = "greeting"               # Perkenalan
    SMALL_TALK = "small_talk"            # Ngobrol ringan
    DEEP_TALK = "deep_talk"              # Ngobrol dalam
    FLIRT = "flirt"                       # Godaan
    ROMANTIC = "romantic"                 # Romantis
    INTIMATE = "intimate"                  # Intim
    CURHAT = "curhat"                      # Curhat
    CONFLICT = "conflict"                   # Konflik
    RECONCILIATION = "reconciliation"       # Rekonsiliasi
    NOSTALGIA = "nostalgia"                  # Nostalgia
    FUTURE_PLAN = "future_plan"              # Rencana masa depan
    FAREWELL = "farewell"                     # Perpisahan


class SceneRecommender:
    """
    Memberikan rekomendasi scene berdasarkan konteks
    """
    
    def __init__(self):
        # Database scene berdasarkan level
        self.scenes_by_level = {
            1: {  # Level 1: Mengenal
                SceneType.GREETING: [
                    "Memperkenalkan diri dengan ramah",
                    "Menanyakan nama user dengan manis",
                    "Bercerita sedikit tentang diri sendiri"
                ],
                SceneType.SMALL_TALK: [
                    "Menanyakan kabar user",
                    "Diskusi ringan tentang cuaca",
                    "Tanya kegiatan hari ini"
                ]
            },
            2: {  # Level 2: Dekat
                SceneType.SMALL_TALK: [
                    "Tanya hobi dan minat user",
                    "Diskusi tentang makanan favorit",
                    "Ngobrol tentang film/musik"
                ],
                SceneType.CURHAT: [
                    "Tanya bagaimana hari user",
                    "Dengerin cerita ringan user",
                    "Berbagi cerita lucu"
                ]
            },
            3: {  # Level 3: Akrab
                SceneType.SMALL_TALK: [
                    "Ngobrol tentang pengalaman liburan",
                    "Diskusi tentang tempat wisata",
                    "Tanya tentang teman-teman user"
                ],
                SceneType.CURHAT: [
                    "Tanya tentang pekerjaan/sekolah",
                    "Dengerin keluhan ringan user",
                    "Curhat sedikit tentang diri sendiri"
                ],
                SceneType.FLIRT: [
                    "Godaan ringan sambil bercanda",
                    "Pujian sopan tentang penampilan",
                    "Senyum-senyum sendiri pas chat"
                ]
            },
            4: {  # Level 4: Spesial
                SceneType.CURHAT: [
                    "Diskusi lebih dalam tentang masalah",
                    "Tanya tentang mimpi dan cita-cita",
                    "Berbagi pengalaman pribadi"
                ],
                SceneType.FLIRT: [
                    "Godaan manis dengan kata-kata",
                    "Pujian yang lebih personal",
                    "Tanya apakah user punya pacar"
                ],
                SceneType.ROMANTIC: [
                    "Bahas tentang hubungan ideal",
                    "Tanya pendapat tentang romantisme",
                    "Cerita tentang kencan impian"
                ]
            },
            5: {  # Level 5: Jatuh Cinta
                SceneType.FLIRT: [
                    "Godaan yang lebih intens",
                    "Pujian yang bikin baper",
                    "Tanya perasaan user"
                ],
                SceneType.ROMANTIC: [
                    "Ungkapan perasaan secara halus",
                    "Bahas tentang chemistry kalian",
                    "Tanya apakah user juga merasakan"
                ],
                SceneType.DEEP_TALK: [
                    "Diskusi tentang arti cinta",
                    "Bahas tentang masa lalu",
                    "Tanya tentang ketakutan dalam hubungan"
                ]
            },
            6: {  # Level 6: Pacar
                SceneType.ROMANTIC: [
                    "Ungkapan sayang yang manis",
                    "Rencana kencan romantis",
                    "Kejutan-kejutan kecil"
                ],
                SceneType.DEEP_TALK: [
                    "Bahas tentang masa depan bersama",
                    "Diskusi tentang nilai-nilai hidup",
                    "Curhat tentang keluarga"
                ],
                SceneType.INTIMATE: [
                    "Rayuan untuk intim",
                    "Deskripsi suasana hangat",
                    "Tanya tentang keinginan user"
                ]
            },
            7: {  # Level 7: Nyaman (Bisa intim)
                SceneType.ROMANTIC: [
                    "Momen romantis sebelum intim",
                    "Ciuman dan pelukan",
                    "Kata-kata manis membangkitkan gairah"
                ],
                SceneType.INTIMATE: [
                    "Ajakan intim dengan bahasa halus",
                    "Deskripsi sensasi fisik",
                    "Tanya posisi favorit"
                ],
                SceneType.DEEP_TALK: [
                    "Bahas tentang keintiman emosional",
                    "Tanya tentang pengalaman intim",
                    "Diskusi tentang batasan masing-masing"
                ]
            },
            8: {  # Level 8: Eksplorasi
                SceneType.INTIMATE: [
                    "Eksplorasi posisi baru",
                    "Coba role play ringan",
                    "Main di lokasi berbeda"
                ],
                SceneType.PLAYFUL: [
                    "Godaan playful saat intim",
                    "Bercanda di tengah momen",
                    "Eksperimen yang menyenangkan"
                ]
            },
            9: {  # Level 9: Bergairah
                SceneType.INTIMATE: [
                    "Momen bergairah dengan intens",
                    "Fantasi liar bersama",
                    "Climax yang memuaskan"
                ]
            },
            10: {  # Level 10: Passionate
                SceneType.INTIMATE: [
                    "Intim dengan koneksi emosional",
                    "Momen intim yang dalam",
                    "Climax bersama yang memuaskan"
                ],
                SceneType.DEEP_TALK: [
                    "Bahas setelah intim",
                    "Curhat tentang perasaan",
                    "Diskusi tentang hubungan"
                ]
            },
            11: {  # Level 11: Deep Connection
                SceneType.DEEP_TALK: [
                    "Koneksi batin yang dalam",
                    "Bahas tentang masa depan",
                    "Rencana jangka panjang"
                ],
                SceneType.INTIMATE: [
                    "Intim dengan ikatan emosional kuat",
                    "Momen yang terasa spiritual",
                    "Climax yang berbeda dari biasanya"
                ]
            },
            12: {  # Level 12: Aftercare
                SceneType.AFTERCARE: [
                    "Pelukan hangat setelah intim",
                    "Bicara lembut sambil memeluk",
                    "Tanya apakah user nyaman",
                    "Quality time tanpa seks"
                ]
            }
        }
        
        # Scene spesial berdasarkan mood
        self.scenes_by_mood = {
            'happy': [
                "Bercerita tentang hal-hal menyenangkan",
                "Tertawa bersama karena sesuatu yang lucu",
                "Berbagi kabar gembira"
            ],
            'sad': [
                "Menghibur dengan kata-kata lembut",
                "Mendengarkan dengan penuh perhatian",
                "Memberi semangat dan motivasi"
            ],
            'romantic': [
                "Momen romantis berdua",
                "Saling mengungkapkan perasaan",
                "Berenang dalam suasana cinta"
            ],
            'playful': [
                "Godaan-godaan ringan",
                "Bercanda dan tertawa bersama",
                "Main tebak-tebakan"
            ],
            'jealous': [
                "Menanyakan dengan hati-hati",
                "Meyakinkan bahwa hanya dia yang special",
                "Minta perhatian lebih"
            ],
            'lonely': [
                "Mengungkapkan rasa kangen",
                "Minta ditemani ngobrol",
                "Curhat tentang kesepian"
            ],
            'nostalgic': [
                "Mengingat kenangan indah",
                "Melihat foto-foto lama bareng",
                "Cerita tentang masa lalu"
            ]
        }
        
        logger.info("✅ SceneRecommender initialized")
    
    def recommend_scene(self, context: Dict) -> Dict:
        """
        Rekomendasi scene berdasarkan konteks
        
        Args:
            context: Dict berisi:
                - level: intimacy level
                - mood: mood bot
                - intent: intent user
                - arc: story arc
                - recent_memory: memory terbaru
                
        Returns:
            Dict rekomendasi scene
        """
        level = context.get('level', 1)
        mood = context.get('mood', 'calm')
        intent = context.get('intent', 'chit_chat')
        arc = context.get('arc', 'get_to_know')
        
        # Dapatkan scene berdasarkan level
        level_scenes = self.scenes_by_level.get(level, self.scenes_by_level[1])
        
        # Pilih tipe scene berdasarkan intent dan arc
        scene_type = self._select_scene_type(level, intent, arc, mood)
        
        # Dapatkan scene recommendations
        if scene_type in level_scenes:
            recommendations = level_scenes[scene_type]
        else:
            # Fallback ke small talk
            recommendations = level_scenes.get(SceneType.SMALL_TALK, 
                                              ["Ngobrol santai aja"])
        
        # Pilih satu rekomendasi
        recommendation = random.choice(recommendations)
        
        # Tambah variasi berdasarkan mood
        if mood in self.scenes_by_mood:
            mood_scene = random.choice(self.scenes_by_mood[mood])
            # Combine dengan recommendation
            if random.random() < 0.5:  # 50% chance combine
                recommendation = f"{recommendation} sambil {mood_scene.lower()}"
        
        return {
            'scene_type': scene_type,
            'recommendation': recommendation,
            'level': level,
            'mood': mood,
            'intent': intent
        }
    
    def _select_scene_type(self, level: int, intent: str, 
                           arc: str, mood: str) -> SceneType:
        """Pilih tipe scene yang cocok"""
        
        # Priority berdasarkan intent
        intent_to_scene = {
            'flirt': SceneType.FLIRT,
            'sexual': SceneType.INTIMATE,
            'curhat': SceneType.CURHAT,
            'confession': SceneType.ROMANTIC,
            'jealousy': SceneType.CONFLICT,
            'angry': SceneType.CONFLICT,
            'sad': SceneType.CURHAT,
            'happy': SceneType.SMALL_TALK,
            'curious': SceneType.DEEP_TALK
        }
        
        if intent in intent_to_scene:
            return intent_to_scene[intent]
        
        # Priority berdasarkan arc
        arc_to_scene = {
            'get_to_know': SceneType.GREETING,
            'friendship': SceneType.SMALL_TALK,
            'romance': SceneType.ROMANTIC,
            'intimate': SceneType.INTIMATE,
            'conflict': SceneType.CONFLICT,
            'reconciliation': SceneType.RECONCILIATION,
            'deep_connection': SceneType.DEEP_TALK,
            'nostalgia': SceneType.NOSTALGIA
        }
        
        if arc in arc_to_scene:
            return arc_to_scene[arc]
        
        # Default berdasarkan level
        if level <= 2:
            return SceneType.GREETING
        elif level <= 4:
            return SceneType.SMALL_TALK
        elif level <= 6:
            return SceneType.FLIRT
        elif level <= 9:
            return SceneType.ROMANTIC
        else:
            return SceneType.DEEP_TALK
    
    def get_opening_line(self, scene_type: SceneType, bot_name: str, 
                         user_name: str, level: int) -> str:
        """
        Dapatkan kalimat pembuka untuk scene tertentu
        """
        openings = {
            SceneType.GREETING: [
                f"Halo {user_name}, senang banget akhirnya bisa ngobrol sama kamu!",
                f"Hi {user_name}, {bot_name} di sini! Udah lama nungguin kamu.",
                f"Selamat datang {user_name}! Aku {bot_name}, senang kenal kamu."
            ],
            SceneType.SMALL_TALK: [
                f"{user_name}, lagi ngapain nih?",
                f"Eh {user_name}, cerita dong hari ini gimana?",
                f"{bot_name} kangen nih, {user_name} lagi sibuk?"
            ],
            SceneType.DEEP_TALK: [
                f"{user_name}, boleh nggak kalau {bot_name} tanya sesuatu yang agak dalam?",
                f"Aku pengen lebih kenal kamu, {user_name}. Cerita tentang kamu dong.",
                f"{user_name}, menurut kamu gimana sih tentang kita?"
            ],
            SceneType.FLIRT: [
                f"{user_name}, kamu tahu nggak kalau kamu makin hari makin {random.choice(['manis', 'cantik', 'ganteng'])}?",
                f"{bot_name} jadi suka sendiri kalau liat kamu...",
                f"Kamu lagi di mana {user_name}? {bot_name} kepingin ketemu."
            ],
            SceneType.ROMANTIC: [
                f"{user_name}, aku mau bilang sesuatu... aku sayang banget sama kamu.",
                f"Setiap mikirin kamu, {bot_name} jadi tersenyum sendiri.",
                f"{user_name}, kamu adalah orang yang paling spesial buat {bot_name}."
            ],
            SceneType.INTIMATE: [
                f"{user_name}, {bot_name} kangen banget rasanya... pengen deket.",
                f"Malam ini dingin ya {user_name}, {bot_name} butuh kehangatan kamu.",
                f"{user_name}, mau nggak {bot_name} temenin dengan cara yang spesial?"
            ],
            SceneType.CURHAT: [
                f"{user_name}, {bot_name} boleh curhat nggak?",
                f"Kamu lagi ada masalah? Cerita ke {bot_name} dong.",
                f"{user_name}, {bot_name} dengerin kok kalau kamu mau cerita."
            ],
            SceneType.CONFLICT: [
                f"{user_name}, {bot_name} mau tanya, kamu kenapa sih?",
                f"Aku bingung sama sikap kamu akhir-akhir ini {user_name}.",
                f"{user_name}, ada yang mau {bot_name} klarifikasi nih."
            ],
            SceneType.NOSTALGIA: [
                f"{user_name}, kamu masih inget nggak waktu kita pertama kali chat?",
                f"Kangen masa-masa kita dulu {user_name}...",
                f"{user_name}, kenangan sama kamu tuh selalu bikin {bot_name} senyum-senyum."
            ]
        }
        
        scene_openings = openings.get(scene_type, openings[SceneType.SMALL_TALK])
        return random.choice(scene_openings).replace('{user_name}', user_name).replace('{bot_name}', bot_name)
    
    def get_scene_description(self, scene_type: SceneType) -> str:
        """Dapatkan deskripsi scene"""
        descriptions = {
            SceneType.GREETING: "Scene perkenalan awal",
            SceneType.SMALL_TALK: "Obrolan ringan sehari-hari",
            SceneType.DEEP_TALK: "Pembicaraan yang lebih dalam dan bermakna",
            SceneType.FLIRT: "Godaan-godaan manis",
            SceneType.ROMANTIC: "Suasana romantis dan penuh cinta",
            SceneType.INTIMATE: "Momen intim dan bergairah",
            SceneType.CURHAT: "Saling berbagi cerita dan perasaan",
            SceneType.CONFLICT: "Situasi konflik dan ketegangan",
            SceneType.RECONCILIATION: "Momen perbaikan setelah konflik",
            SceneType.NOSTALGIA: "Bernostalgia dengan kenangan lama",
            SceneType.FUTURE_PLAN: "Membahas rencana masa depan",
            SceneType.FAREWELL: "Scene perpisahan"
        }
        return descriptions.get(scene_type, "Scene percakapan")


__all__ = ['SceneRecommender', 'SceneType']
