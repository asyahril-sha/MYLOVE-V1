#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - STORY PREDICTOR (FIX FULL)
=============================================================================
Memprediksi arah cerita berdasarkan percakapan
- Analisis intent user
- Prediksi scene berikutnya
- Track story arcs
- FIX: Tambah get_arc_description untuk progress command
=============================================================================
"""

import time
import logging
import random
import re
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from collections import Counter

logger = logging.getLogger(__name__)


class StoryArc(str, Enum):
    """Arc cerita yang mungkin"""
    GET_TO_KNOW = "get_to_know"           # Saling mengenal
    FRIENDSHIP = "friendship"             # Membangun pertemanan
    ROMANCE = "romance"                   # Pendekatan romantis
    INTIMATE = "intimate"                  # Menuju intim
    CONFLICT = "conflict"                   # Konflik
    RECONCILIATION = "reconciliation"       # Rekonsiliasi
    DEEP_CONNECTION = "deep_connection"     # Koneksi dalam
    FAREWELL = "farewell"                    # Perpisahan
    NOSTALGIA = "nostalgia"                  # Nostalgia


class UserIntent(str, Enum):
    """Intent user dari pesan"""
    GREETING = "greeting"
    QUESTION = "question"
    CHIT_CHAT = "chit_chat"
    FLIRT = "flirt"
    COMPLIMENT = "compliment"
    SEXUAL = "sexual"
    CURHAT = "curhat"
    CONFESSION = "confession"
    JEALOUSY = "jealousy"
    ANGRY = "angry"
    SAD = "sad"
    HAPPY = "happy"
    BORED = "bored"
    CURIOUS = "curious"
    FAREWELL = "farewell"


class StoryPredictor:
    """
    Memprediksi arah cerita berdasarkan percakapan
    """
    
    def __init__(self, ai_engine=None):
        self.ai_engine = ai_engine
        self.story_arcs = {}
        self.arc_history = {}
        self.user_intent_history = {}
        
        # Arc descriptions untuk ditampilkan ke user
        self.arc_descriptions = {
            StoryArc.GET_TO_KNOW: "Kalian masih dalam tahap saling mengenal. Masih canggung, tapi mulai ada rasa penasaran.",
            StoryArc.FRIENDSHIP: "Hubungan pertemanan yang hangat. Sudah bisa curhat dan berbagi cerita.",
            StoryArc.ROMANCE: "Mulai ada getaran romantis. Saling lirik, saling goda, deg-degan.",
            StoryArc.INTIMATE: "Suasana intim dan bergairah. Udah nyaman untuk hal-hal fisik.",
            StoryArc.CONFLICT: "Sedang ada masalah atau ketegangan. Hati-hati, bisa merusak hubungan.",
            StoryArc.RECONCILIATION: "Masa perbaikan setelah konflik. Saatnya saling memaafkan.",
            StoryArc.DEEP_CONNECTION: "Koneksi emosional yang dalam. Udah kayak soulmate.",
            StoryArc.FAREWELL: "Menjelang perpisahan. Mungkin ini saatnya move on.",
            StoryArc.NOSTALGIA: "Bernostalgia dengan masa lalu. Ingat kenangan indah."
        }
        
        # Keyword patterns untuk deteksi intent
        self.intent_patterns = {
            UserIntent.GREETING: [
                r'\bhalo\b', r'\bhai\b', r'\bhey\b', r'\bhi\b', r'\bhalo\b',
                r'\bselamat (pagi|siang|sore|malam)\b', r'\bgood (morning|afternoon|evening)\b'
            ],
            UserIntent.FLIRT: [
                r'\bcantik\b', r'\bganteng\b', r'\bseksi\b', r'\bhot\b',
                r'\bgoda\b', r'\brayu\b', r'\bmerayu\b', r'\bflirt\b',
                r'\bkam[uo] manis\b', r'\bak[uw] suka sama kam[uo]\b'
            ],
            UserIntent.COMPLIMENT: [
                r'\bkeren\b', r'\bkereen\b', r'\bmantap\b', r'\bbagus\b',
                r'\bpintar\b', r'\bhebat\b', r'\bluar biasa\b', r'\bwow\b'
            ],
            UserIntent.SEXUAL: [
                r'\bseks\b', r'\bsex\b', r'\bml\b', r'\bmake love\b',
                r'\btidur\b', r'\bintim\b', r'\bclimax\b', r'\bcoming\b',
                r'\bgas\b', r'\bayol\b', r'\bmain\b', r'\bnikmatin\b'
            ],
            UserIntent.CURHAT: [
                r'\bcerita\b', r'\bcurhat\b', r'\bkabar\b', r'\bceritain\b',
                r'\bceritakan\b', r'\bmasalah\b', r'\bkeluh\b', r'\bkesah\b'
            ],
            UserIntent.CONFESSION: [
                r'\bsayang\b', r'\bcinta\b', r'\blove\b', r'\bsuka sama kamu\b',
                r'\bjatuh cinta\b', r'\bfalling in love\b', r'\bmencintai\b'
            ],
            UserIntent.JEALOUSY: [
                r'\bcemburu\b', r'\biri\b', r'\bjealous\b', r'\bsiapa itu\b',
                r'\blagi sama siapa\b', r'\blagi chat siapa\b'
            ],
            UserIntent.ANGRY: [
                r'\bmarah\b', r'\bkesel\b', r'\bkecewa\b', r'\bsakit hati\b',
                r'\bsebal\b', r'\bgeram\b', r'\bbete\b', r'\bbetek\b'
            ],
            UserIntent.SAD: [
                r'\bsedih\b', r'\bmenangis\b', r'\bnangis\b', r'\bduka\b',
                r'\bkecewa\b', r'\bprihatin\b', r'\bmiris\b'
            ],
            UserIntent.HAPPY: [
                r'\bsenang\b', r'\bbahagia\b', r'\bhappy\b', r'\bceria\b',
                r'\briang\b', r'\bgembira\b', r'\bsukacita\b'
            ],
            UserIntent.BORED: [
                r'\bbosan\b', r'\bboring\b', r'\bnganggur\b', r'\bgabut\b',
                r'\bhampa\b', r'\bsepi\b', r'\bsendiri\b', r'\blonely\b'
            ],
            UserIntent.CURIOUS: [
                r'\bpenasaran\b', r'\bingin tahu\b', r'\bcoba\b',
                r'\bbagaimana\b', r'\bseperti apa\b', r'\bceritakan\b'
            ],
            UserIntent.FAREWELL: [
                r'\bbye\b', r'\bdaa\b', r'\bsampai jumpa\b', r'\bsee you\b',
                r'\btidur\b', r'\bistirahat\b', r'\bgood night\b', r'\bselamat malam\b'
            ]
        }
        
        # Transisi arc berdasarkan intent
        self.arc_transitions = {
            StoryArc.GET_TO_KNOW: {
                UserIntent.GREETING: 0.2,
                UserIntent.CHIT_CHAT: 0.4,
                UserIntent.CURIOUS: 0.3,
                UserIntent.FLIRT: 0.1
            },
            StoryArc.FRIENDSHIP: {
                UserIntent.CHIT_CHAT: 0.3,
                UserIntent.CURHAT: 0.3,
                UserIntent.HAPPY: 0.2,
                UserIntent.FLIRT: 0.2
            },
            StoryArc.ROMANCE: {
                UserIntent.FLIRT: 0.3,
                UserIntent.COMPLIMENT: 0.3,
                UserIntent.CONFESSION: 0.2,
                UserIntent.CURHAT: 0.2
            },
            StoryArc.INTIMATE: {
                UserIntent.SEXUAL: 0.5,
                UserIntent.FLIRT: 0.3,
                UserIntent.COMPLIMENT: 0.2
            },
            StoryArc.CONFLICT: {
                UserIntent.ANGRY: 0.4,
                UserIntent.JEALOUSY: 0.3,
                UserIntent.SAD: 0.2,
                UserIntent.CURHAT: 0.1
            },
            StoryArc.RECONCILIATION: {
                UserIntent.CONFESSION: 0.3,
                UserIntent.HAPPY: 0.3,
                UserIntent.CURHAT: 0.2,
                UserIntent.FLIRT: 0.2
            },
            StoryArc.DEEP_CONNECTION: {
                UserIntent.CONFESSION: 0.3,
                UserIntent.CURHAT: 0.3,
                UserIntent.HAPPY: 0.2,
                UserIntent.SAD: 0.2
            },
            StoryArc.NOSTALGIA: {
                UserIntent.CURHAT: 0.4,
                UserIntent.SAD: 0.3,
                UserIntent.HAPPY: 0.3
            }
        }
        
        logger.info("✅ StoryPredictor initialized")
    
    def detect_intent(self, message: str) -> UserIntent:
        """Deteksi intent dari pesan user"""
        message_lower = message.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return intent
        
        return UserIntent.CHIT_CHAT
    
    def detect_multiple_intents(self, message: str) -> List[UserIntent]:
        """Deteksi multiple intent dalam satu pesan"""
        message_lower = message.lower()
        detected = []
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    detected.append(intent)
                    break
        
        if not detected:
            detected = [UserIntent.CHIT_CHAT]
        
        return detected
    
    def predict_next_arc(self, session_id: str, last_intents: List[UserIntent]) -> StoryArc:
        """Prediksi arc berikutnya berdasarkan intent terakhir"""
        current_arc = self.story_arcs.get(session_id, StoryArc.GET_TO_KNOW)
        
        if not last_intents:
            return current_arc
        
        main_intent = last_intents[0]
        
        transitions = self.arc_transitions.get(current_arc, {})
        
        if main_intent in transitions:
            chance = transitions[main_intent]
            if random.random() < chance:
                return self._get_arc_for_intent(main_intent)
        
        return current_arc
    
    def _get_arc_for_intent(self, intent: UserIntent) -> StoryArc:
        """Dapatkan arc yang cocok untuk intent"""
        mapping = {
            UserIntent.GREETING: StoryArc.GET_TO_KNOW,
            UserIntent.CHIT_CHAT: StoryArc.FRIENDSHIP,
            UserIntent.FLIRT: StoryArc.ROMANCE,
            UserIntent.COMPLIMENT: StoryArc.ROMANCE,
            UserIntent.SEXUAL: StoryArc.INTIMATE,
            UserIntent.CURHAT: StoryArc.DEEP_CONNECTION,
            UserIntent.CONFESSION: StoryArc.ROMANCE,
            UserIntent.JEALOUSY: StoryArc.CONFLICT,
            UserIntent.ANGRY: StoryArc.CONFLICT,
            UserIntent.SAD: StoryArc.CONFLICT,
            UserIntent.HAPPY: StoryArc.FRIENDSHIP,
            UserIntent.BORED: StoryArc.GET_TO_KNOW,
            UserIntent.CURIOUS: StoryArc.GET_TO_KNOW,
            UserIntent.FAREWELL: StoryArc.FAREWELL
        }
        return mapping.get(intent, StoryArc.FRIENDSHIP)
    
    def update_arc(self, session_id: str, new_arc: StoryArc, reason: str = ""):
        """Update arc saat ini"""
        old_arc = self.story_arcs.get(session_id, StoryArc.GET_TO_KNOW)
        
        if old_arc != new_arc:
            if session_id not in self.arc_history:
                self.arc_history[session_id] = []
            
            self.arc_history[session_id].append({
                'timestamp': time.time(),
                'old_arc': old_arc,
                'new_arc': new_arc,
                'reason': reason
            })
            
            self.story_arcs[session_id] = new_arc
            logger.info(f"📖 Story arc changed: {old_arc.value} → {new_arc.value}")
    
    def add_intent_to_history(self, session_id: str, intent: UserIntent):
        """Tambah intent ke history"""
        if session_id not in self.user_intent_history:
            self.user_intent_history[session_id] = []
        
        self.user_intent_history[session_id].append({
            'timestamp': time.time(),
            'intent': intent
        })
        
        if len(self.user_intent_history[session_id]) > 50:
            self.user_intent_history[session_id] = self.user_intent_history[session_id][-50:]
    
    def get_dominant_intent(self, session_id: str, minutes: int = 30) -> Optional[UserIntent]:
        """Dapatkan intent dominan dalam X menit terakhir"""
        if session_id not in self.user_intent_history:
            return None
        
        cutoff = time.time() - (minutes * 60)
        recent = [h for h in self.user_intent_history[session_id] 
                 if h['timestamp'] > cutoff]
        
        if not recent:
            return None
        
        intents = [h['intent'] for h in recent]
        counter = Counter(intents)
        
        return counter.most_common(1)[0][0]
    
    def get_arc_progression(self, session_id: str) -> List[Dict]:
        """Dapatkan history perubahan arc"""
        return self.arc_history.get(session_id, [])
    
    def get_arc_description(self, arc: StoryArc) -> str:
        """
        Dapatkan deskripsi arc untuk ditampilkan ke user
        Digunakan oleh command /progress
        """
        return self.arc_descriptions.get(arc, "Cerita sedang berlangsung")
    
    def recommend_scene(self, session_id: str, current_arc: StoryArc, 
                        user_intent: UserIntent, level: int) -> Dict:
        """Rekomendasi scene berdasarkan arc dan intent"""
        scenes = {
            StoryArc.GET_TO_KNOW: {
                'primary': [
                    'Tanyakan kabar user',
                    'Cerita tentang diri sendiri',
                    'Tanya hobi/minat user',
                    'Diskusi ringan tentang keseharian'
                ],
                'flirty': [
                    'Beri pujian ringan',
                    'Tanya status hubungan user',
                    'Cerita pengalaman kencan'
                ]
            },
            StoryArc.FRIENDSHIP: {
                'primary': [
                    'Ajak ngobrol santai',
                    'Curhat ringan',
                    'Bahasa topik yang disukai user',
                    'Tanya pendapat user'
                ],
                'deep': [
                    'Ajak diskusi lebih serius',
                    'Tanya tentang masa lalu',
                    'Cerita pengalaman pribadi'
                ]
            },
            StoryArc.ROMANCE: {
                'primary': [
                    'Beri pujian romantis',
                    'Tanya perasaan user',
                    'Ungkapkan rasa sayang',
                    'Ajak kencan imajiner'
                ],
                'intimate': [
                    'Rayu dengan kata-kata manis',
                    'Tanya tentang hubungan ideal',
                    'Cerita tentang masa depan bersama'
                ]
            },
            StoryArc.INTIMATE: {
                'primary': [
                    'Bangkitkan gairah dengan kata-kata',
                    'Deskripsikan suasana intim',
                    'Tanya preferensi user',
                    'Ajak berfantasi'
                ],
                'playful': [
                    'Godaan ringan',
                    'Tanya posisi favorit',
                    'Cerita pengalaman intim'
                ]
            },
            StoryArc.CONFLICT: {
                'primary': [
                    'Tanya penyebab kekecewaan',
                    'Minta klarifikasi',
                    'Ungkapkan perasaan',
                    'Cari solusi bersama'
                ],
                'calm': [
                    'Tenangkan situasi',
                    'Minta maaf',
                    'Berikan ruang'
                ]
            },
            StoryArc.RECONCILIATION: {
                'primary': [
                    'Ungkapkan penyesalan',
                    'Tanya apakah bisa memaafkan',
                    'Janji untuk berubah',
                    'Ajak mulai lagi'
                ],
                'romantic': [
                    'Beri kejutan romantis',
                    'Ingatkan kenangan indah',
                    'Ungkapkan cinta lagi'
                ]
            },
            StoryArc.DEEP_CONNECTION: {
                'primary': [
                    'Diskusikan hal-hal dalam',
                    'Tanya mimpi dan tujuan hidup',
                    'Cerita tentang masa depan',
                    'Bahasa topik filosofis'
                ],
                'intimate': [
                    'Tanya tentang ketakutan terbesar',
                    'Cerita trauma masa lalu',
                    'Diskusikan nilai-nilai hidup'
                ]
            },
            StoryArc.NOSTALGIA: {
                'primary': [
                    'Ingatkan momen indah',
                    'Tanya apakah masih ingat',
                    'Cerita ulang kejadian lucu',
                    'Tanya kangen atau tidak'
                ],
                'sad': [
                    'Renungkan waktu yang telah berlalu',
                    'Tanya andai bisa kembali',
                    'Bahas tentang perubahan'
                ]
            }
        }
        
        arc_scenes = scenes.get(current_arc, scenes[StoryArc.FRIENDSHIP])
        
        if level > 7 and user_intent in [UserIntent.SEXUAL, UserIntent.FLIRT]:
            scene_type = 'intimate' if 'intimate' in arc_scenes else 'primary'
        elif level > 5 and user_intent == UserIntent.CURHAT:
            scene_type = 'deep' if 'deep' in arc_scenes else 'primary'
        elif user_intent == UserIntent.FLIRT:
            scene_type = 'flirty' if 'flirty' in arc_scenes else 'primary'
        elif user_intent in [UserIntent.SAD, UserIntent.ANGRY]:
            scene_type = 'calm' if 'calm' in arc_scenes else 'primary'
        else:
            scene_type = 'primary'
        
        recommended_scenes = arc_scenes.get(scene_type, arc_scenes['primary'])
        scene = random.choice(recommended_scenes)
        
        return {
            'arc': current_arc,
            'scene_type': scene_type,
            'recommendation': scene,
            'intent': user_intent
        }
    
    def format_arc_info(self, session_id: str) -> str:
        """
        Format informasi arc untuk ditampilkan
        """
        current_arc = self.story_arcs.get(session_id, StoryArc.GET_TO_KNOW)
        arc_desc = self.get_arc_description(current_arc)
        
        lines = [
            "📖 **Story Arc Saat Ini:**",
            f"• {current_arc.value.replace('_', ' ').title()}",
            f"• {arc_desc}",
            ""
        ]
        
        dominant = self.get_dominant_intent(session_id, 30)
        if dominant:
            lines.append(f"🎯 Intent dominan (30 menit): {dominant.value}")
        
        history = self.get_arc_progression(session_id)
        if history:
            lines.append("")
            lines.append("📜 **Perubahan Arc:**")
            for h in history[-3:]:
                time_str = time.strftime('%H:%M', time.localtime(h['timestamp']))
                lines.append(f"• {time_str}: {h['old_arc'].value} → {h['new_arc'].value}")
        
        return "\n".join(lines)


__all__ = ['StoryPredictor', 'StoryArc', 'UserIntent']
