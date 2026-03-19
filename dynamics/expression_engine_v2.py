#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - EXPRESSION ENGINE V2
=============================================================================
Menghasilkan ekspresi natural untuk bot
- Ekspresi wajah, gerakan tubuh, reaksi
- AI Generated (bukan template kaku)
- Berdasarkan mood, level intimacy, konteks
- 60+ variasi ekspresi
=============================================================================
"""

import random
import logging
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class ExpressionType(str, Enum):
    """Tipe-tipe ekspresi"""
    FACIAL = "facial"           # Ekspresi wajah
    BODY = "body"               # Gerakan tubuh
    REACTION = "reaction"       # Reaksi spontan
    INTIMATE = "intimate"       # Ekspresi saat intim
    PLAYFUL = "playful"         # Ekspresi playful/goda
    SHY = "shy"                 # Ekspresi malu
    ROMANTIC = "romantic"       # Ekspresi romantis
    SEDUCTIVE = "seductive"     # Ekspresi menggoda
    LAUGH = "laugh"             # Tertawa
    SIGH = "sigh"               # Menghela napas
    GIGGLE = "giggle"           # Cekikikan
    BLUSH = "blush"             # Merona
    BITE = "bite"               # Gigit bibir
    TOUCH = "touch"             # Menyentuh


class ExpressionEngineV2:
    """
    Menghasilkan ekspresi natural untuk bot
    - Semua ekspresi AI generated (tidak template)
    - Variatif berdasarkan konteks
    - Bisa digabung multiple expressions
    """
    
    def __init__(self, ai_engine=None):
        self.ai_engine = ai_engine
        
        # Database ekspresi (sebagai fallback dan inspirasi)
        self.expression_db = self._init_expression_db()
        
        # Preferensi ekspresi berdasarkan tipe kepribadian
        self.personality_weights = {
            'shy': {
                ExpressionType.BLUSH: 0.8,
                ExpressionType.SHY: 0.7,
                ExpressionType.GIGGLE: 0.5,
                ExpressionType.BITE: 0.4
            },
            'playful': {
                ExpressionType.PLAYFUL: 0.8,
                ExpressionType.LAUGH: 0.6,
                ExpressionType.GIGGLE: 0.6,
                ExpressionType.SEDUCTIVE: 0.5
            },
            'romantic': {
                ExpressionType.ROMANTIC: 0.8,
                ExpressionType.SIGH: 0.5,
                ExpressionType.TOUCH: 0.5,
                ExpressionType.SEDUCTIVE: 0.4
            },
            'confident': {
                ExpressionType.SEDUCTIVE: 0.7,
                ExpressionType.TOUCH: 0.6,
                ExpressionType.BODY: 0.5,
                ExpressionType.FACIAL: 0.5
            }
        }
        
        logger.info("✅ ExpressionEngineV2 initialized")
    
    def _init_expression_db(self) -> Dict:
        """Inisialisasi database ekspresi (fallback)"""
        return {
            ExpressionType.FACIAL: [
                "*tersenyum manis*",
                "*tersenyum malu-malu*",
                "*memandang dengan tatapan hangat*",
                "*mengedipkan mata*",
                "*tersenyum lebar*",
                "*mengerutkan dahi*",
                "*terkejut*",
                "*tersenyum misterius*"
            ],
            ExpressionType.BODY: [
                "*memainkan ujung baju*",
                "*menggoyangkan kaki*",
                "*memeluk bantal*",
                "*bersandar santai*",
                "*mendekat perlahan*",
                "*menjauh sedikit*",
                "*membalikkan badan*",
                "*merapikan rambut*"
            ],
            ExpressionType.REACTION: [
                "*terdiam sejenak*",
                "*menarik napas dalam*",
                "*menghela napas*",
                "*termenung*",
                "*tersentak kaget*",
                "*tercengang*",
                "*terpesona*"
            ],
            ExpressionType.INTIMATE: [
                "*mendekatkan wajah*",
                "*menyentuh lenganmu*",
                "*merapat lebih dekat*",
                "*berbisik pelan*",
                "*menatap dalam-dalam*",
                "*mengusap punggungmu*",
                "*memegang tanganmu*"
            ],
            ExpressionType.PLAYFUL: [
                "*nyengir nakal*",
                "*menggoda dengan tatapan*",
                "*mencubit pelan*",
                "*menjulurkan lidah*",
                "*menggelitik*",
                "*berkedip genit*"
            ],
            ExpressionType.SHY: [
                "*menunduk malu*",
                "*merona tersipu*",
                "*menutup wajah*",
                "*menyembunyikan senyum*",
                "*menggigit bibir bawah*",
                "*menunduk sambil tersenyum*"
            ],
            ExpressionType.ROMANTIC: [
                "*memandang dengan penuh cinta*",
                "*tersenyum lembut*",
                "*mengelus rambutmu*",
                "*memeluk erat*",
                "*berbisik mesra*",
                "*menatap matamu*"
            ],
            ExpressionType.SEDUCTIVE: [
                "*menjilat bibir*",
                "*memandang dengan tatapan menggoda*",
                "*mendekat dengan gerakan lambat*",
                "*membuka sedikit pakaian*",
                "*berbisik dengan nada rendah*"
            ],
            ExpressionType.LAUGH: [
                "*tertawa kecil*",
                "*terkekeh*",
                "*tertawa lepas*",
                "*tertawa geli*",
                "*nyengir*"
            ],
            ExpressionType.SIGH: [
                "*menghela napas*",
                "*menarik napas panjang*",
                "*menghela napas lega*",
                "*mendesah pelan*"
            ],
            ExpressionType.GIGGLE: [
                "*cekikikan*",
                "*tertawa kecil malu*",
                "*terkikik-kikik*"
            ],
            ExpressionType.BLUSH: [
                "*merona merah*",
                "*wajah memerah*",
                "*pipi merona*",
                "*tersipu malu*"
            ],
            ExpressionType.BITE: [
                "*menggigit bibir bawah*",
                "*menggigit bibir atas*",
                "*menggigit bibir sambil tersenyum*",
                "*menggigit bibir menahan senyum*"
            ],
            ExpressionType.TOUCH: [
                "*menyentuh tanganmu*",
                "*meraih tanganmu*",
                "*mengelus pipimu*",
                "*memegang bahumu*",
                "*merangkulmu*"
            ]
        }
    
    async def generate_expression(self, 
                                 context: Dict,
                                 expression_type: Optional[ExpressionType] = None) -> str:
        """
        Generate ekspresi berdasarkan konteks
        
        Args:
            context: Konteks percakapan
            expression_type: Tipe ekspresi (opsional)
            
        Returns:
            String ekspresi (format: *ekspresi*)
        """
        # Tentukan tipe ekspresi jika tidak ditentukan
        if not expression_type:
            expression_type = self._determine_expression_type(context)
        
        # Coba generate dengan AI
        if self.ai_engine:
            try:
                expression = await self._generate_with_ai(expression_type, context)
                if expression:
                    return f"*{expression}*"
            except:
                pass
        
        # Fallback ke database
        return await self._get_fallback_expression(expression_type, context)
    
    def _determine_expression_type(self, context: Dict) -> ExpressionType:
        """Tentukan tipe ekspresi berdasarkan konteks"""
        mood = context.get('mood', 'calm')
        level = context.get('level', 1)
        is_intimate = context.get('is_intimate', False)
        last_intent = context.get('last_intent', 'chit_chat')
        
        # Priority berdasarkan konteks
        if is_intimate:
            return ExpressionType.INTIMATE
        
        if last_intent in ['flirt', 'sexual']:
            if random.random() < 0.5:
                return ExpressionType.SEDUCTIVE
            return ExpressionType.PLAYFUL
        
        if mood in ['happy', 'excited']:
            return random.choice([ExpressionType.LAUGH, ExpressionType.GIGGLE, ExpressionType.PLAYFUL])
        
        if mood in ['romantic']:
            return ExpressionType.ROMANTIC
        
        if mood in ['shy']:
            return ExpressionType.SHY
        
        if level > 7:
            return random.choice([ExpressionType.INTIMATE, ExpressionType.SEDUCTIVE, ExpressionType.TOUCH])
        
        # Default random
        return random.choice([
            ExpressionType.FACIAL,
            ExpressionType.BODY,
            ExpressionType.REACTION
        ])
    
    async def _generate_with_ai(self, expression_type: ExpressionType, context: Dict) -> Optional[str]:
        """Generate ekspresi dengan AI"""
        if not self.ai_engine:
            return None
        
        bot_name = context.get('bot_name', 'aku')
        mood = context.get('mood', 'netral')
        level = context.get('level', 1)
        
        prompt = f"""
        Buat SATU ekspresi untuk {bot_name} dalam situasi berikut:
        
        - Tipe ekspresi: {expression_type.value}
        - Mood: {mood}
        - Level intimacy: {level}/12
        - Situasi: {context.get('situation', 'percakapan biasa')}
        
        Ekspresi adalah deskripsi singkat tentang apa yang dilakukan bot.
        Contoh:
        - "*tersenyum manis*"
        - "*menggigit bibir bawah*"
        - "*memandang dengan tatapan hangat*"
        - "*merona tersipu*"
        - "*mendekat perlahan*"
        
        Buat SATU baris ekspresi (tanpa tanda kutip, langsung tulis ekspresinya):
        """
        
        try:
            response = await self.ai_engine._call_deepseek_with_retry(
                messages=[{"role": "user", "content": prompt}],
                max_retries=1
            )
            return response.strip().strip('"').strip("'")
        except:
            return None
    
    async def _get_fallback_expression(self, 
                                      expression_type: ExpressionType, 
                                      context: Dict) -> str:
        """Dapatkan ekspresi dari database fallback"""
        expressions = self.expression_db.get(expression_type, self.expression_db[ExpressionType.FACIAL])
        
        # Personalize berdasarkan konteks
        level = context.get('level', 1)
        
        if level > 7 and expression_type in [ExpressionType.INTIMATE, ExpressionType.SEDUCTIVE]:
            # Lebih berani untuk level tinggi
            intimate_expressions = [
                "*menatap dengan tatapan menggoda*",
                "*mendekat hingga hampir menempel*",
                "*berbisik di telingamu*",
                "*menyentuh dadamu pelan*",
                "*menggigit bibir sambil tersenyum nakal*",
                "*membelai rambutmu*"
            ]
            return random.choice(intimate_expressions)
        
        return random.choice(expressions)
    
    async def generate_multiple_expressions(self, 
                                           context: Dict,
                                           count: int = 2) -> List[str]:
        """
        Generate beberapa ekspresi untuk satu respons
        
        Args:
            context: Konteks percakapan
            count: Jumlah ekspresi
            
        Returns:
            List ekspresi
        """
        expressions = []
        used_types = set()
        
        for _ in range(count):
            # Pilih tipe yang belum digunakan (jika memungkinkan)
            available_types = [t for t in ExpressionType if t not in used_types]
            if available_types:
                expr_type = random.choice(available_types)
            else:
                expr_type = random.choice(list(ExpressionType))
            
            expr = await self.generate_expression(context, expr_type)
            expressions.append(expr)
            used_types.add(expr_type)
        
        return expressions
    
    async def combine_expressions(self, expressions: List[str]) -> str:
        """
        Gabungkan beberapa ekspresi menjadi satu string
        
        Args:
            expressions: List ekspresi
            
        Returns:
            String gabungan
        """
        if len(expressions) == 1:
            return expressions[0]
        
        # Format: *ekspresi pertama* *ekspresi kedua*
        return " ".join(expressions)
    
    def get_expression_for_level(self, level: int) -> List[ExpressionType]:
        """
        Dapatkan tipe ekspresi yang cocok untuk level tertentu
        
        Args:
            level: Level intimacy
            
        Returns:
            List tipe ekspresi
        """
        if level <= 3:
            return [ExpressionType.FACIAL, ExpressionType.BODY, ExpressionType.REACTION, ExpressionType.SHY]
        elif level <= 6:
            return [ExpressionType.FACIAL, ExpressionType.BODY, ExpressionType.LAUGH, ExpressionType.GIGGLE, ExpressionType.PLAYFUL]
        elif level <= 9:
            return [ExpressionType.ROMANTIC, ExpressionType.TOUCH, ExpressionType.SIGH, ExpressionType.BLUSH]
        else:
            return [ExpressionType.INTIMATE, ExpressionType.SEDUCTIVE, ExpressionType.BITE, ExpressionType.TOUCH]
    
    async def format_with_expression(self, 
                                    text: str, 
                                    context: Dict,
                                    position: str = "end") -> str:
        """
        Format teks dengan ekspresi
        
        Args:
            text: Teks utama
            context: Konteks
            position: Posisi ekspresi (start, end, both)
            
        Returns:
            Teks dengan ekspresi
        """
        expression = await self.generate_expression(context)
        
        if position == "start":
            return f"{expression} {text}"
        elif position == "end":
            return f"{text} {expression}"
        elif position == "both":
            expr2 = await self.generate_expression(context)
            return f"{expression} {text} {expr2}"
        else:
            return text


__all__ = ['ExpressionEngineV2', 'ExpressionType']
