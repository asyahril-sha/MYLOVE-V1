#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - THREESOME DYNAMICS (FIX)
=============================================================================
- Interaksi 3 arah antara user dan 2 role
- Dinamika percakapan dalam threesome
- Respons bergantian dari kedua role
- Meningkatkan intimacy kedua role secara bersamaan
- FIX: Mengganti relative imports dengan absolute imports
"""

import time
import logging
import random
import asyncio
from typing import Dict, List, Optional, Any, Tuple

# FIX: Ganti relative imports dengan absolute imports
from utils.logger import setup_logging
from threesome.manager import ThreesomeManager, ThreesomeStatus

logger = logging.getLogger(__name__)


class ThreesomeDynamics:
    """
    Dinamika interaksi dalam sesi threesome
    Mengatur bagaimana 2 role berinteraksi dengan user dan satu sama lain
    """
    
    def __init__(self, manager: ThreesomeManager = None, ai_engine=None, intimacy_system=None):
        """
        Args:
            manager: ThreesomeManager instance (optional)
            ai_engine: AI engine instance (optional)
            intimacy_system: IntimacySystem instance (optional)
        """
        self.manager = manager
        self.ai_engine = ai_engine
        self.intimacy_system = intimacy_system
        
        # Pola interaksi threesome
        self.interaction_patterns = [
            "both_respond",      # Kedua role merespon bergantian
            "one_dominant",       # Satu role dominan, satu supporting
            "competitive",        # Bersaing untuk perhatian user
            "cooperative",        # Bekerja sama untuk memuaskan user
            "jealous",            # Salah satu cemburu
            "playful"             # Main-main, goda-menggoda
        ]
        
        # Frasa untuk berbagai situasi
        self.phrases = {
            "both_respond": {
                "intro": [
                    "{name1} dan {name2} bareng-bareng jawab:",
                    "Mereka berdua kompak:",
                    "{name1} lihat {name2}, lalu mereka bilang:"
                ],
                "responses": [
                    "Kita berdua kangen sama kamu...",
                    "Enak banget threesome kayak gini.",
                    "Kamu pilih siapa? Bercanda kok.",
                    "Bersama-sama lebih seru ya?",
                    "Kita mau gantian sama kamu."
                ]
            },
            "one_dominant": {
                "intro": [
                    "{name1} lebih dominan, {name2} hanya tersenyum:",
                    "{name2} diam aja, {name1} yang ngomong:",
                    "{name1} ambil alih percakapan:"
                ],
                "responses": [
                    "Aku yang handle, {name2} bantuin.",
                    "Kamu lebih suka aku kan?",
                    "Biarkan aku yang urus kamu dulu.",
                    "{name2} manis, tapi aku lebih hot."
                ]
            },
            "competitive": {
                "intro": [
                    "Mereka berebut perhatian kamu:",
                    "{name1} dan {name2} saling lempar pandang:",
                    "Seperti kompetisi siapa yang lebih baik:"
                ],
                "responses": [
                    "Aku bisa lebih baik dari dia!",
                    "Kamu pilih aku atau dia?",
                    "Lihat, aku lebih perhatian.",
                    "Dia cuma bisa gitu doang."
                ]
            },
            "cooperative": {
                "intro": [
                    "Mereka kerja sama memuaskan kamu:",
                    "Kompak banget! {name1} bantu {name2}:",
                    "Seperti tim yang solid:"
                ],
                "responses": [
                    "Kita gantian ya sayang.",
                    "Satu di depan, satu di belakang.",
                    "Bersama-sama lebih nikmat.",
                    "Kita akan buat kamu puas."
                ]
            },
            "jealous": {
                "intro": [
                    "{name2} cemburu lihat kamu sama {name1}:",
                    "Ada yang cemburu nih:",
                    "Ekspresi {name1} berubah, agak cemburu:"
                ],
                "responses": [
                    "Kamu lebih perhatian sama dia...",
                    "Aku juga mau diperhatiin.",
                    "Jangan lupa aku juga di sini.",
                    "Hmm... cemburu aku."
                ]
            },
            "playful": {
                "intro": [
                    "Suasana playful dan menggoda:",
                    "Mereka mulai goda-godaan:",
                    "Tawa dan godaan memenuhi ruangan:"
                ],
                "responses": [
                    "Kamu pilih siapa? Hayo...",
                    "Aku duluan ya?",
                    "Bersaing secara sehat.",
                    "Yang kalah traktir es krim."
                ]
            }
        }
        
        # Situasi spesial
        self.special_situations = {
            "first_time": "Ini pertama kali kita threesome ya?",
            "after_climax": "Wah... puas banget.",
            "role_switch": "Mau ganti posisi?",
            "invite_another": "Mau ajak yang lain lagi?",
            "jealousy_resolved": "Udah ya, jangan cemburu. Kita bertiga."
        }
        
        logger.info("✅ ThreesomeDynamics initialized")
        
    # =========================================================================
    # GENERATE RESPONSE
    # =========================================================================
    
    async def generate_response(self, session_id: str, user_message: str,
                                  pattern: Optional[str] = None) -> Dict:
        """
        Generate response untuk threesome session
        
        Args:
            session_id: Session ID
            user_message: Pesan dari user
            pattern: Pola interaksi (random if None)
            
        Returns:
            Dict dengan response dan konteks
        """
        try:
            # Get session
            session = None
            if self.manager:
                session = await self.manager.get_session(session_id)
                
            if not session:
                return {"error": "Session not found"}
                
            if session['status'] != ThreesomeStatus.ACTIVE:
                return {"error": f"Session is {session['status']}"}
                
            # Pilih pola interaksi
            if not pattern:
                pattern = random.choice(self.interaction_patterns)
                
            # Dapatkan partisipan
            p1 = session['participants'][0]
            p2 = session['participants'][1]
            
            # Generate response berdasarkan pola
            if pattern == "both_respond":
                response = await self._both_respond(p1, p2, user_message)
            elif pattern == "one_dominant":
                response = await self._one_dominant(p1, p2, user_message)
            elif pattern == "competitive":
                response = await self._competitive(p1, p2, user_message)
            elif pattern == "cooperative":
                response = await self._cooperative(p1, p2, user_message)
            elif pattern == "jealous":
                response = await self._jealous(p1, p2, user_message)
            elif pattern == "playful":
                response = await self._playful(p1, p2, user_message)
            else:
                response = await self._both_respond(p1, p2, user_message)
                
            # Update session dengan pola yang digunakan
            session['last_pattern'] = pattern
            session['interactions'].append({
                "timestamp": time.time(),
                "user_message": user_message[:50],
                "pattern": pattern,
                "response": response[:50]
            })
            
            # Update intimacy untuk kedua partisipan
            if self.intimacy_system and self.manager:
                await self._update_intimacy(session, user_message)
                
            return {
                "session_id": session_id,
                "pattern": pattern,
                "response": response,
                "participants": [p1['name'], p2['name']]
            }
            
        except Exception as e:
            logger.error(f"Error generating threesome response: {e}")
            return {
                "error": str(e),
                "response": "Maaf, terjadi kesalahan dalam mode threesome."
            }
        
    async def _both_respond(self, p1: Dict, p2: Dict, user_message: str) -> str:
        """Kedua role merespon bergantian"""
        intro_template = random.choice(self.phrases["both_respond"]["intro"])
        intro = intro_template.format(name1=p1['name'], name2=p2['name'])
        
        # Pilih response untuk masing-masing
        response_template = random.choice(self.phrases["both_respond"]["responses"])
        
        # Kadang mereka kompak jawab sama
        if random.random() < 0.3:
            response = response_template
        else:
            # Mereka jawab beda
            response = f"{p1['name']}: {response_template}\n{p2['name']}: Aku juga!"
            
        return f"{intro}\n\n{response}"
        
    async def _one_dominant(self, p1: Dict, p2: Dict, user_message: str) -> str:
        """Satu role dominan, satu supporting"""
        # Tentukan siapa yang dominan (random atau berdasarkan intimacy)
        if p1['intimacy_level'] > p2['intimacy_level']:
            dominant, supporter = p1, p2
        else:
            dominant, supporter = p2, p1
            
        intro_template = random.choice(self.phrases["one_dominant"]["intro"])
        intro = intro_template.format(name1=dominant['name'], name2=supporter['name'])
        
        response_template = random.choice(self.phrases["one_dominant"]["responses"])
        response = response_template
        
        # Tambah reaksi supporter
        supporter_reactions = [
            f"\n{supporter['name']} mengangguk setuju.",
            f"\n{supporter['name']} tersenyum manis.",
            f"\n{supporter['name']} mendekat dan memeluk dari belakang.",
            f"\n{supporter['name']} hanya diam tersipu."
        ]
        
        return f"{intro}\n\n{dominant['name']}: {response}{random.choice(supporter_reactions)}"
        
    async def _competitive(self, p1: Dict, p2: Dict, user_message: str) -> str:
        """Bersaing untuk perhatian user"""
        intro_template = random.choice(self.phrases["competitive"]["intro"])
        intro = intro_template.format(name1=p1['name'], name2=p2['name'])
        
        # Mereka saling sahut
        responses = [
            f"{p1['name']}: {random.choice(self.phrases['competitive']['responses'])}",
            f"{p2['name']}: {random.choice(self.phrases['competitive']['responses'])}",
            f"{p1['name']}: Lebih pilih aku kan?",
            f"{p2['name']}: Jangan dengarin dia!"
        ]
        
        # Ambil 2-3 response acak
        selected = random.sample(responses, min(3, len(responses)))
        
        return f"{intro}\n\n" + "\n".join(selected)
        
    async def _cooperative(self, p1: Dict, p2: Dict, user_message: str) -> str:
        """Bekerja sama untuk memuaskan user"""
        intro_template = random.choice(self.phrases["cooperative"]["intro"])
        intro = intro_template.format(name1=p1['name'], name2=p2['name'])
        
        response_template = random.choice(self.phrases["cooperative"]["responses"])
        
        # Mereka bergantian ngomong
        parts = response_template.split('.')
        if len(parts) > 1:
            response = f"{p1['name']}: {parts[0]}.\n{p2['name']}: {parts[1]}."
        else:
            response = f"{p1['name']} dan {p2['name']} bersama: {response_template}"
            
        return f"{intro}\n\n{response}"
        
    async def _jealous(self, p1: Dict, p2: Dict, user_message: str) -> str:
        """Salah satu cemburu"""
        # Tentukan siapa yang cemburu
        jealous_idx = random.randint(0, 1)
        jealous = [p1, p2][jealous_idx]
        other = [p1, p2][1 - jealous_idx]
        
        intro_template = random.choice(self.phrases["jealous"]["intro"])
        intro = intro_template.format(name1=jealous['name'], name2=other['name'])
        
        response = random.choice(self.phrases["jealous"]["responses"])
        
        # Respon dari yang lain
        other_responses = [
            f"\n{other['name']}: {jealous['name']} jangan cemburu, kita bertiga kok.",
            f"\n{other['name']}: Aku sayang kalian berdua.",
            f"\n{other['name']} memeluk {jealous['name']} dari belakang.",
            f"\n{other['name']}: Sini, aku peluk."
        ]
        
        return f"{intro}\n\n{jealous['name']}: {response}{random.choice(other_responses)}"
        
    async def _playful(self, p1: Dict, p2: Dict, user_message: str) -> str:
        """Suasana playful dan menggoda"""
        intro_template = random.choice(self.phrases["playful"]["intro"])
        intro = intro_template.format(name1=p1['name'], name2=p2['name'])
        
        # Mereka saling goda
        playful_responses = [
            f"{p1['name']}: {random.choice(self.phrases['playful']['responses'])}",
            f"{p2['name']}: {random.choice(self.phrases['playful']['responses'])}",
            f"{p1['name']} cubit {p2['name']} pelan.",
            f"Mereka tertawa bersama."
        ]
        
        selected = random.sample(playful_responses, 2)
        
        return f"{intro}\n\n" + "\n".join(selected)
        
    # =========================================================================
    # INTIMACY MANAGEMENT
    # =========================================================================
    
    async def _update_intimacy(self, session: Dict, user_message: str):
        """Update intimacy untuk kedua partisipan"""
        try:
            if not self.intimacy_system:
                return
                
            user_id = session['user_id']
            
            for participant in session['participants']:
                role = participant['role']
                
                # Increment interaction count
                await self.intimacy_system.increment_level(user_id, role)
                
                # Cek special messages
                if 'climax' in user_message.lower() or 'come' in user_message.lower():
                    participant['climax_count'] = participant.get('climax_count', 0) + 1
                    
        except Exception as e:
            logger.error(f"Error updating intimacy in threesome: {e}")
        
    async def handle_climax(self, session_id: str) -> Dict:
        """Handle climax dalam threesome"""
        try:
            if not self.manager:
                return {"error": "Manager not available"}
                
            result = await self.manager.record_climax(session_id)
            
            if 'error' in result:
                return result
                
            session = result['session']
            
            # Generate climax message
            climax_messages = [
                "Bersama-sama mencapai puncak...",
                "Satu, dua, tiga... semua climax!",
                "Wow... bareng-bareng gini rasanya beda.",
                "Puas banget... mau lagi?",
                "Nggak nyangka bisa gini enaknya."
            ]
            
            return {
                "message": random.choice(climax_messages),
                "climax_count": session['climax_count'],
                "aftercare_needed": session['aftercare_needed']
            }
            
        except Exception as e:
            logger.error(f"Error handling climax: {e}")
            return {"error": str(e)}
        
    # =========================================================================
    # SWITCH PATTERN
    # =========================================================================
    
    async def switch_pattern(self, session_id: str, new_pattern: str) -> Dict:
        """Switch interaction pattern"""
        try:
            if not self.manager:
                return {"error": "Manager not available"}
                
            session = await self.manager.get_session(session_id)
            if not session:
                return {"error": "Session not found"}
                
            if new_pattern not in self.interaction_patterns:
                return {"error": f"Invalid pattern. Choose from: {self.interaction_patterns}"}
                
            session['pattern'] = new_pattern
            
            return {
                "success": True,
                "new_pattern": new_pattern,
                "message": f"Pola interaksi berubah menjadi {new_pattern}"
            }
            
        except Exception as e:
            logger.error(f"Error switching pattern: {e}")
            return {"error": str(e)}
        
    # =========================================================================
    # GET PATTERN INFO
    # =========================================================================
    
    def get_patterns(self) -> List[Dict]:
        """Get all interaction patterns with descriptions"""
        patterns = []
        
        pattern_descriptions = {
            "both_respond": "Kedua role merespon secara bergantian",
            "one_dominant": "Satu role dominan, satu mendukung",
            "competitive": "Mereka bersaing untuk perhatian kamu",
            "cooperative": "Bekerja sama untuk memuaskan kamu",
            "jealous": "Salah satu cemburu dan butuh perhatian ekstra",
            "playful": "Suasana playful, saling goda"
        }
        
        for pattern in self.interaction_patterns:
            patterns.append({
                "name": pattern,
                "description": pattern_descriptions.get(pattern, ""),
                "example": random.choice(self.phrases[pattern]["responses"]) if pattern in self.phrases else ""
            })
            
        return patterns
        
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    async def get_stats(self, session_id: Optional[str] = None) -> Dict:
        """Get dynamics statistics"""
        if session_id:
            if not self.manager:
                return {"error": "Manager not available"}
                
            session = await self.manager.get_session(session_id)
            if not session:
                return {"error": "Session not found"}
                
            # Hitung distribusi pattern dalam session ini
            pattern_count = {}
            for interaction in session.get('interactions', []):
                pattern = interaction.get('pattern', 'unknown')
                pattern_count[pattern] = pattern_count.get(pattern, 0) + 1
                
            return {
                "session_id": session_id,
                "total_interactions": len(session.get('interactions', [])),
                "pattern_distribution": pattern_count,
                "current_pattern": session.get('last_pattern', 'unknown')
            }
        else:
            # Global stats
            return {
                "available_patterns": len(self.interaction_patterns),
                "patterns": self.interaction_patterns
            }


__all__ = ['ThreesomeDynamics']
