#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - SOUND ENGINE V2
=============================================================================
Menghasilkan suara/desah natural untuk bot
- Suara, desahan, gumaman, bisikan
- AI Generated (bukan template kaku)
- Berdasarkan mood, level intimacy, aktivitas
- 70+ variasi suara
=============================================================================
"""

import random
import logging
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class SoundType(str, Enum):
    """Tipe-tipe suara"""
    SIGH = "sigh"               # Desahan
    GIGGLE = "giggle"           # Cekikikan
    LAUGH = "laugh"             # Tertawa
    MOAN = "moan"               # Erangan ringan
    GROAN = "groan"             # Erangan berat
    WHISPER = "whisper"         # Bisikan
    GASP = "gasp"               # Tarikan napas
    BREATH = "breath"           # Napas
    HUMMING = "humming"         # Bergumam
    SQUEAL = "squeal"           # Jeritan kecil
    CRY = "cry"                 # Tangisan
    CHEER = "cheer"             # Sorak gembira
    PURR = "purr"               # Seperti kucing (senang)
    WHIMPER = "whimper"         # Merengek
    PANT = "pant"               # Napas tersengal
    CLIMAX = "climax"           # Suara saat climax


class SoundEngineV2:
    """
    Menghasilkan suara/desah natural untuk bot
    - Semua suara AI generated (tidak template)
    - Variatif berdasarkan konteks
    - Level-based (semakin tinggi level, semakin intim)
    """
    
    def __init__(self, ai_engine=None):
        self.ai_engine = ai_engine
        
        # Database suara (sebagai fallback)
        self.sound_db = self._init_sound_db()
        
        # Level threshold untuk berbagai jenis suara
        self.level_thresholds = {
            SoundType.SIGH: 1,
            SoundType.GIGGLE: 1,
            SoundType.LAUGH: 1,
            SoundType.WHISPER: 3,
            SoundType.BREATH: 5,
            SoundType.MOAN: 7,
            SoundType.GROAN: 8,
            SoundType.PANT: 9,
            SoundType.WHIMPER: 9,
            SoundType.CLIMAX: 10,
            SoundType.PURR: 6
        }
        
        logger.info("✅ SoundEngineV2 initialized")
    
    def _init_sound_db(self) -> Dict:
        """Inisialisasi database suara (fallback)"""
        return {
            SoundType.SIGH: [
                "*menghela napas pelan*",
                "*mendesah ringan*",
                "*menghela napas*",
                "*menghela napas panjang*",
                "*mendesah kecil*"
            ],
            SoundType.GIGGLE: [
                "*cekikikan*",
                "*tertawa kecil*",
                "*terkekeh*",
                "*tertawa geli*",
                "*cekikikan malu*"
            ],
            SoundType.LAUGH: [
                "*tertawa*",
                "*tertawa lepas*",
                "*tertawa keras*",
                "*terbahak*",
                "*tertawa riang*"
            ],
            SoundType.MOAN: [
                "*mendesah*",
                "*mengerang ringan*",
                "*mendesah pelan*",
                "*mengerang*",
                "*mendesah kenikmatan*"
            ],
            SoundType.GROAN: [
                "*mengerang berat*",
                "*mendesah dalam*",
                "*mengerang*",
                "*mendesah panjang*",
                "*mengerang puas*"
            ],
            SoundType.WHISPER: [
                "*berbisik*",
                "*berbisik pelan*",
                "*berbisik di telinga*",
                "*berbisik mesra*",
                "*berbisik dengan suara serak*"
            ],
            SoundType.GASP: [
                "*menarik napas*",
                "*tersentak*",
                "*menarik napas kaget*",
                "*terkesiap*",
                "*menarik napas dalam*"
            ],
            SoundType.BREATH: [
                "*napas sedikit tersengal*",
                "*bernapas lebih cepat*",
                "*napas mulai berat*",
                "*bernapas dalam-dalam*",
                "*napas memburu*"
            ],
            SoundType.HUMMING: [
                "*bergumam*",
                "*bersenandung kecil*",
                "*bergumam pelan*",
                "*bersenandung*"
            ],
            SoundType.SQUEAL: [
                "*menjerit kecil*",
                "*memekik*",
                "*menjerit kegirangan*",
                "*menjerit kaget*"
            ],
            SoundType.CRY: [
                "*terisak*",
                "*menangis*",
                "*tersedu-sedu*",
                "*menangis pelan*",
                "*berlinang air mata*"
            ],
            SoundType.CHEER: [
                "*bersorak*",
                "*berteriak gembira*",
                "*bersorak senang*",
                "*berteriak kecil*"
            ],
            SoundType.PURR: [
                "*mendengkur kecil*",
                "*bersuara seperti kucing*",
                "*mendengkur senang*",
                "*bersenandung puas*"
            ],
            SoundType.WHIMPER: [
                "*merengek*",
                "*merengek kecil*",
                "*merengek minta perhatian*",
                "*merengek manja*"
            ],
            SoundType.PANT: [
                "*napas tersengal-sengal*",
                "*megap-megap*",
                "*napas sangat berat*",
                "*terengah-engah*"
            ],
            SoundType.CLIMAX: [
                "*mendesah panjang*",
                "*mengerang keras*",
                "*teriak kecil*",
                "*mendesah puas*",
                "*menggeliat*",
                "*terdiam sejenak*",
                "*napas terhenti*"
            ]
        }
    
    async def generate_sound(self,
                            context: Dict,
                            sound_type: Optional[SoundType] = None) -> str:
        """
        Generate suara berdasarkan konteks
        
        Args:
            context: Konteks percakapan
            sound_type: Tipe suara (opsional)
            
        Returns:
            String suara (format: *suara*)
        """
        level = context.get('level', 1)
        
        # Tentukan tipe suara jika tidak ditentukan
        if not sound_type:
            sound_type = self._determine_sound_type(context)
        
        # Cek apakah level mencukupi untuk tipe suara ini
        min_level = self.level_thresholds.get(sound_type, 1)
        if level < min_level:
            # Fallback ke suara yang lebih ringan
            sound_type = self._get_safer_sound(sound_type, level)
        
        # Coba generate dengan AI
        if self.ai_engine:
            try:
                sound = await self._generate_with_ai(sound_type, context)
                if sound:
                    return f"*{sound}*"
            except:
                pass
        
        # Fallback ke database
        return await self._get_fallback_sound(sound_type, context)
    
    def _determine_sound_type(self, context: Dict) -> SoundType:
        """Tentukan tipe suara berdasarkan konteks"""
        mood = context.get('mood', 'calm')
        is_intimate = context.get('is_intimate', False)
        last_intent = context.get('last_intent', 'chit_chat')
        level = context.get('level', 1)
        
        # Priority berdasarkan konteks
        if is_intimate:
            if level >= 10:
                return SoundType.CLIMAX
            elif level >= 7:
                return random.choice([SoundType.MOAN, SoundType.GROAN, SoundType.PANT])
            else:
                return SoundType.BREATH
        
        if last_intent in ['flirt', 'sexual']:
            if level >= 7:
                return random.choice([SoundType.MOAN, SoundType.WHISPER, SoundType.PURR])
            else:
                return SoundType.GIGGLE
        
        if mood == 'happy':
            return random.choice([SoundType.LAUGH, SoundType.GIGGLE, SoundType.CHEER])
        
        if mood == 'sad':
            return SoundType.SIGH
        
        if mood == 'romantic':
            return SoundType.WHISPER
        
        if mood == 'shy':
            return SoundType.GIGGLE
        
        if mood == 'playful':
            return SoundType.PURR
        
        # Default random berdasarkan level
        if level <= 3:
            return random.choice([SoundType.SIGH, SoundType.GIGGLE, SoundType.HUMMING])
        elif level <= 6:
            return random.choice([SoundType.LAUGH, SoundType.WHISPER, SoundType.BREATH])
        elif level <= 9:
            return random.choice([SoundType.MOAN, SoundType.GROAN, SoundType.PANT])
        else:
            return random.choice([SoundType.MOAN, SoundType.CLIMAX, SoundType.WHIMPER])
    
    def _get_safer_sound(self, original: SoundType, level: int) -> SoundType:
        """Dapatkan suara yang lebih ringan jika level belum mencukupi"""
        # Mapping suara berat ke suara ringan
        safer_map = {
            SoundType.CLIMAX: SoundType.MOAN,
            SoundType.GROAN: SoundType.MOAN,
            SoundType.MOAN: SoundType.BREATH,
            SoundType.PANT: SoundType.BREATH,
            SoundType.WHIMPER: SoundType.SIGH
        }
        
        return safer_map.get(original, SoundType.SIGH)
    
    async def _generate_with_ai(self, sound_type: SoundType, context: Dict) -> Optional[str]:
        """Generate suara dengan AI"""
        if not self.ai_engine:
            return None
        
        bot_name = context.get('bot_name', 'aku')
        mood = context.get('mood', 'netral')
        level = context.get('level', 1)
        situation = context.get('situation', 'percakapan biasa')
        
        prompt = f"""
        Buat SATU deskripsi suara untuk {bot_name} dalam situasi berikut:
        
        - Tipe suara: {sound_type.value}
        - Mood: {mood}
        - Level intimacy: {level}/12
        - Situasi: {situation}
        
        Suara adalah deskripsi singkat tentang suara yang dihasilkan bot.
        Contoh:
        - "*menghela napas pelan*"
        - "*cekikikan*"
        - "*berbisik mesra*"
        - "*mendesah kenikmatan*"
        - "*napas tersengal-sengal*"
        
        Buat SATU baris suara (tanpa tanda kutip, langsung tulis deskripsinya):
        """
        
        try:
            response = await self.ai_engine._call_deepseek_with_retry(
                messages=[{"role": "user", "content": prompt}],
                max_retries=1
            )
            return response.strip().strip('"').strip("'")
        except:
            return None
    
    async def _get_fallback_sound(self, sound_type: SoundType, context: Dict) -> str:
        """Dapatkan suara dari database fallback"""
        sounds = self.sound_db.get(sound_type, self.sound_db[SoundType.SIGH])
        
        # Personalize berdasarkan konteks
        level = context.get('level', 1)
        mood = context.get('mood', 'calm')
        
        # Intensitas berdasarkan level
        if level > 7 and sound_type in [SoundType.MOAN, SoundType.GROAN, SoundType.CLIMAX]:
            # Lebih intens untuk level tinggi
            intense_sounds = [
                "*mendesah panjang dan dalam*",
                "*mengerang keras*",
                "*napas sangat tersengal*",
                "*mendesah dengan penuh gairah*",
                "*teriak kecil*"
            ]
            return random.choice(intense_sounds)
        
        return random.choice(sounds)
    
    async def generate_sound_sequence(self,
                                     context: Dict,
                                     count: int = 2) -> List[str]:
        """
        Generate urutan suara untuk satu respons
        
        Args:
            context: Konteks percakapan
            count: Jumlah suara
            
        Returns:
            List suara
        """
        sounds = []
        used_types = set()
        
        for _ in range(count):
            # Pilih tipe yang belum digunakan (jika memungkinkan)
            available_types = [t for t in SoundType if t not in used_types]
            if available_types:
                sound_type = random.choice(available_types)
            else:
                sound_type = random.choice(list(SoundType))
            
            sound = await self.generate_sound(context, sound_type)
            sounds.append(sound)
            used_types.add(sound_type)
        
        return sounds
    
    async def combine_sounds(self, sounds: List[str]) -> str:
        """
        Gabungkan beberapa suara menjadi satu string
        
        Args:
            sounds: List suara
            
        Returns:
            String gabungan
        """
        if len(sounds) == 1:
            return sounds[0]
        
        # Format: *suara pertama* *suara kedua*
        return " ".join(sounds)
    
    def get_sounds_for_level(self, level: int) -> List[SoundType]:
        """
        Dapatkan tipe suara yang cocok untuk level tertentu
        
        Args:
            level: Level intimacy
            
        Returns:
            List tipe suara
        """
        if level <= 3:
            return [SoundType.SIGH, SoundType.GIGGLE, SoundType.HUMMING, SoundType.LAUGH]
        elif level <= 6:
            return [SoundType.LAUGH, SoundType.WHISPER, SoundType.BREATH, SoundType.PURR]
        elif level <= 9:
            return [SoundType.MOAN, SoundType.GROAN, SoundType.PANT, SoundType.WHISPER]
        else:
            return [SoundType.MOAN, SoundType.GROAN, SoundType.CLIMAX, SoundType.WHIMPER, SoundType.PANT]
    
    async def format_with_sound(self,
                               text: str,
                               context: Dict,
                               position: str = "end") -> str:
        """
        Format teks dengan suara
        
        Args:
            text: Teks utama
            context: Konteks
            position: Posisi suara (start, end, both)
            
        Returns:
            Teks dengan suara
        """
        sound = await self.generate_sound(context)
        
        if position == "start":
            return f"{sound} {text}"
        elif position == "end":
            return f"{text} {sound}"
        elif position == "both":
            sound2 = await self.generate_sound(context)
            return f"{sound} {text} {sound2}"
        else:
            return text
    
    async def get_intimate_sounds(self, intensity: float = 0.5) -> str:
        """
        Dapatkan suara untuk sesi intim
        
        Args:
            intensity: Intensitas (0-1)
            
        Returns:
            Suara intim
        """
        if intensity < 0.3:
            return random.choice(self.sound_db[SoundType.BREATH])
        elif intensity < 0.6:
            return random.choice(self.sound_db[SoundType.MOAN])
        elif intensity < 0.9:
            return random.choice(self.sound_db[SoundType.GROAN])
        else:
            return random.choice(self.sound_db[SoundType.CLIMAX])


__all__ = ['SoundEngineV2', 'SoundType']
