#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - EXPRESSION DATABASE
=============================================================================
Database ekspresi untuk fallback
- 50+ ekspresi
- Kategorisasi
=============================================================================
"""

import random
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ExpressionDatabase:
    """
    Database ekspresi untuk fallback
    """
    
    def __init__(self):
        self.expressions = {
            "senyum": [
                "*tersenyum manis*",
                "*tersenyum lebar*",
                "*tersenyum malu-malu*",
                "*tersenyum simpul*",
                "*senyum sumringah*"
            ],
            "tertawa": [
                "*tertawa kecil*",
                "*terkekeh*",
                "*tertawa geli*",
                "*tertawa lepas*",
                "*ngakak*"
            ],
            "malu": [
                "*merona*",
                "*tersipu malu*",
                "*menunduk malu*",
                "*wajah memerah*",
                "*nutup muka*"
            ],
            "kaget": [
                "*terkejut*",
                "*tercengang*",
                "*melongo*",
                "*mata membesar*",
                "*kaget*"
            ],
            "sedih": [
                "*murung*",
                "*lesu*",
                "*cemberut*",
                "*mata berkaca-kaca*",
                "*sedih*"
            ],
            "marah": [
                "*cemberut*",
                "*betek*",
                "*ngambek*",
                "*manyun*",
                "*sebal*"
            ],
            "goda": [
                "*mengedipkan mata*",
                "*nyengir nakal*",
                "*melirik genit*",
                "*tersenyum misterius*",
                "*godain*"
            ],
            "intim": [
                "*menggigit bibir*",
                "*menjilat bibir*",
                "*napas berat*",
                "*merapat*",
                "*berbisik*"
            ],
            "sayang": [
                "*melirik mesra*",
                "*tatapan penuh cinta*",
                "*tersenyum manja*",
                "*mengelus lembut*",
                "*memeluk*"
            ],
            "bingung": [
                "*mengerutkan dahi*",
                "*garuk kepala*",
                "*miringin kepala*",
                "*bengong*",
                "*mikir keras*"
            ]
        }
        
        logger.info(f"✅ ExpressionDatabase initialized with {self.count()} expressions")
    
    def get_random(self, category: str = None) -> str:
        """
        Dapatkan ekspresi random
        
        Args:
            category: Kategori ekspresi (None untuk semua)
        
        Returns:
            String ekspresi
        """
        if category and category in self.expressions:
            return random.choice(self.expressions[category])
        else:
            all_expr = []
            for expr_list in self.expressions.values():
                all_expr.extend(expr_list)
            return random.choice(all_expr)
    
    def get_by_category(self, category: str) -> List[str]:
        """Dapatkan semua ekspresi dalam kategori"""
        return self.expressions.get(category, [])
    
    def get_categories(self) -> List[str]:
        """Dapatkan semua kategori"""
        return list(self.expressions.keys())
    
    def count(self) -> int:
        """Hitung total ekspresi"""
        return sum(len(expr) for expr in self.expressions.values())
    
    def add_expression(self, category: str, expression: str):
        """Tambah ekspresi baru"""
        if category not in self.expressions:
            self.expressions[category] = []
        if expression not in self.expressions[category]:
            self.expressions[category].append(expression)
    
    def format_for_prompt(self, category: str = None, count: int = 3) -> str:
        """
        Format contoh ekspresi untuk prompt
        
        Args:
            category: Kategori
            count: Jumlah contoh
        
        Returns:
            String contoh
        """
        if category:
            examples = random.sample(self.expressions[category], min(count, len(self.expressions[category])))
        else:
            all_expr = []
            for expr_list in self.expressions.values():
                all_expr.extend(expr_list)
            examples = random.sample(all_expr, min(count, len(all_expr)))
        
        return "\n".join([f"  • {ex}" for ex in examples])
