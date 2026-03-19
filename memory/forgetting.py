#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - SEMANTIC FORGETTING
=============================================================================
BUKAN menghapus memory, tapi mengurangi prioritas/akses
- Memory tetap ada, tapi "terkubur" jika jarang diakses
- Seperti manusia: ingat tapi butuh waktu untuk mengingat
- Prioritas naik kembali jika diakses lagi
- Untuk single user dengan memory PERMANEN
=============================================================================
"""

import time
import logging
import math
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ForgetType(str, Enum):
    """Tipe forgetting"""
    DECAY = "decay"               # Meluruh karena waktu
    INTERFERENCE = "interference"  # Tertimpa memori baru
    RETRIEVAL = "retrieval"       # Jarang diambil
    CONSOLIDATION = "consolidation" # Digabung dengan memori lain


class MemoryTrace:
    """
    Jejak memori yang melacak akses dan kekuatan
    """
    def __init__(self, memory_id: str, initial_strength: float = 1.0):
        self.memory_id = memory_id
        self.strength = initial_strength  # Kekuatan memori (0-1)
        self.access_count = 0
        self.last_access = time.time()
        self.creation_time = time.time()
        self.access_timeline = []  # Riwayat akses
        
    def access(self):
        """Memori diakses"""
        self.access_count += 1
        self.last_access = time.time()
        self.access_timeline.append(time.time())
        # Akses meningkatkan kekuatan
        self.strength = min(1.0, self.strength + 0.1)
        
        # Simpan hanya 10 akses terakhir
        if len(self.access_timeline) > 10:
            self.access_timeline = self.access_timeline[-10:]
    
    def decay(self, hours: float, decay_rate: float = 0.01):
        """Meluruh berdasarkan waktu"""
        # Rumus decay: strength * e^(-decay_rate * hours)
        decay_factor = math.exp(-decay_rate * hours)
        self.strength *= decay_factor
        
        # Minimal strength 0.1 (tidak pernah 0)
        self.strength = max(0.1, self.strength)
    
    def get_recall_probability(self) -> float:
        """
        Probabilitas memori bisa diingat
        Semakin rendah strength, semakin sulit diingat
        """
        # Threshold: strength < 0.3 = sulit diingat
        if self.strength < 0.3:
            return self.strength * 2  # Max 0.6
        else:
            return 1.0
    
    def get_recall_time(self) -> float:
        """
        Estimasi waktu yang dibutuhkan untuk mengingat (detik)
        Strength rendah = butuh waktu lebih lama
        """
        if self.strength >= 0.8:
            return 0.1  # Instan
        elif self.strength >= 0.5:
            return 0.5  # Setengah detik
        elif self.strength >= 0.3:
            return 1.0  # 1 detik
        else:
            return 2.0 + (1.0 - self.strength) * 5  # 2-7 detik
    
    def to_dict(self) -> Dict:
        """Konversi ke dictionary"""
        return {
            'memory_id': self.memory_id,
            'strength': self.strength,
            'access_count': self.access_count,
            'last_access': self.last_access,
            'creation_time': self.creation_time,
            'recall_probability': self.get_recall_probability(),
            'recall_time': self.get_recall_time()
        }


class SemanticForgetting:
    """
    Sistem forgetting ala manusia:
    - Memory tidak pernah dihapus
    - Yang jarang diakses "terkubur" (strength turun)
    - Tapi bisa diingat lagi jika ada trigger
    - Seperti manusia: "Tunggu, aku ingat..."
    """
    
    def __init__(self):
        # Memory traces untuk setiap memori
        self.memory_traces = {}  # {memory_id: MemoryTrace}
        
        # Kategori memori dengan decay rate berbeda
        self.decay_rates = {
            'episodic': 0.005,    # Momen spesial: decay lambat
            'semantic': 0.01,      # Fakta: decay sedang
            'compact': 0.02,       # Ringkasan: decay cepat
            'relationship': 0.003   # Hubungan: decay sangat lambat
        }
        
        # Thresholds
        self.forgotten_threshold = 0.3  # Di bawah ini = "terlupakan"
        self.remembered_threshold = 0.7  # Di atas ini = "sangat diingat"
        
        # Cache untuk akses cepat
        self.recent_memories = []  # 10 memori terakhir diakses
        
        logger.info("✅ SemanticForgetting initialized (memories are NEVER deleted)")
    
    # =========================================================================
    # TRACK MEMORY
    # =========================================================================
    
    async def track_memory(self, memory_id: str, memory_type: str, initial_strength: float = 1.0):
        """
        Mulai tracking sebuah memori
        
        Args:
            memory_id: ID memori
            memory_type: Tipe memori (episodic, semantic, dll)
            initial_strength: Kekuatan awal
        """
        self.memory_traces[memory_id] = MemoryTrace(memory_id, initial_strength)
        self.memory_traces[memory_id].memory_type = memory_type
        logger.debug(f"Now tracking memory: {memory_id}")
    
    async def access_memory(self, memory_id: str):
        """
        Memori diakses, perkuat jejaknya
        
        Args:
            memory_id: ID memori
        """
        if memory_id in self.memory_traces:
            self.memory_traces[memory_id].access()
            
            # Update recent memories
            trace = self.memory_traces[memory_id]
            self.recent_memories.insert(0, {
                'memory_id': memory_id,
                'strength': trace.strength,
                'time': time.time()
            })
            self.recent_memories = self.recent_memories[:10]
    
    async def decay_all(self, hours_passed: float):
        """
        Apply decay ke semua memori
        
        Args:
            hours_passed: Jam yang telah berlalu
        """
        for memory_id, trace in self.memory_traces.items():
            memory_type = getattr(trace, 'memory_type', 'semantic')
            decay_rate = self.decay_rates.get(memory_type, 0.01)
            
            trace.decay(hours_passed, decay_rate)
    
    # =========================================================================
    # RECALL MEMORY
    # =========================================================================
    
    async def should_recall(self, memory_id: str) -> Tuple[bool, float]:
        """
        Cek apakah memori bisa diingat
        
        Args:
            memory_id: ID memori
            
        Returns:
            (can_recall, probability)
        """
        if memory_id not in self.memory_traces:
            return False, 0.0
        
        trace = self.memory_traces[memory_id]
        prob = trace.get_recall_probability()
        
        # Simulasi: random berdasarkan probabilitas
        can_recall = random.random() < prob
        
        return can_recall, prob
    
    async def recall_with_effort(self, memory_id: str, trigger_strength: float = 0.0) -> Tuple[bool, float]:
        """
        Mengingat dengan usaha (butuh waktu)
        
        Args:
            memory_id: ID memori
            trigger_strength: Kekuatan pemicu (0-1)
            
        Returns:
            (success, time_taken)
        """
        if memory_id not in self.memory_traces:
            return False, 0.0
        
        trace = self.memory_traces[memory_id]
        
        # Kombinasi strength memori + trigger
        effective_strength = min(1.0, trace.strength + trigger_strength)
        
        # Probabilitas mengingat
        recall_prob = effective_strength
        
        # Waktu yang dibutuhkan
        if effective_strength >= 0.8:
            time_needed = 0.1
        elif effective_strength >= 0.5:
            time_needed = 0.5
        elif effective_strength >= 0.3:
            time_needed = 1.0
        else:
            time_needed = 2.0 + (1.0 - effective_strength) * 5
        
        # Simulasi mengingat
        success = random.random() < recall_prob
        
        if success:
            # Berhasil mengingat, perkuat memori
            trace.access()
            logger.debug(f"Recalled {memory_id} after {time_needed:.2f}s")
        else:
            logger.debug(f"Failed to recall {memory_id}")
        
        return success, time_needed
    
    async def get_forgotten_memories(self, threshold: float = 0.3) -> List[Dict]:
        """
        Dapatkan memori yang "terlupakan" (strength di bawah threshold)
        
        Args:
            threshold: Batas strength
            
        Returns:
            List of forgotten memories
        """
        forgotten = []
        
        for memory_id, trace in self.memory_traces.items():
            if trace.strength < threshold:
                forgotten.append({
                    'memory_id': memory_id,
                    'strength': trace.strength,
                    'last_access': trace.last_access,
                    'recall_prob': trace.get_recall_probability()
                })
        
        return forgotten
    
    # =========================================================================
    # STRENGTHEN MEMORY
    # =========================================================================
    
    async def strengthen_memory(self, memory_id: str, amount: float = 0.1):
        """
        Perkuat memori secara manual
        
        Args:
            memory_id: ID memori
            amount: Jumlah penguatan
        """
        if memory_id in self.memory_traces:
            self.memory_traces[memory_id].strength = min(
                1.0, 
                self.memory_traces[memory_id].strength + amount
            )
            logger.debug(f"Strengthened memory {memory_id}")
    
    async def strengthen_by_trigger(self, memory_id: str, trigger_match: float):
        """
        Perkuat memori karena trigger cocok
        
        Args:
            memory_id: ID memori
            trigger_match: Seberapa cocok trigger (0-1)
        """
        await self.strengthen_memory(memory_id, trigger_match * 0.2)
    
    # =========================================================================
    # MEMORY CONSOLIDATION
    # =========================================================================
    
    async def consolidate(self, memory_ids: List[str], new_memory_id: str):
        """
        Gabungkan beberapa memori menjadi satu (konsolidasi)
        Memori asli tetap ada, tapi strength turun
        
        Args:
            memory_ids: List memori yang digabung
            new_memory_id: ID memori baru hasil gabungan
        """
        # Hitung strength rata-rata
        total_strength = 0
        count = 0
        
        for mem_id in memory_ids:
            if mem_id in self.memory_traces:
                total_strength += self.memory_traces[mem_id].strength
                count += 1
                
                # Turunkan strength memori asli
                self.memory_traces[mem_id].strength *= 0.5
        
        if count > 0:
            avg_strength = total_strength / count
            
            # Buat memori baru dengan strength lebih tinggi
            await self.track_memory(new_memory_id, 'consolidated', avg_strength * 1.2)
            logger.info(f"Consolidated {count} memories into {new_memory_id}")
    
    # =========================================================================
    # FLASHBACK EFFECT
    # =========================================================================
    
    async def simulate_flashback(self, memory_id: str) -> Dict:
        """
        Simulasi efek flashback: memori tiba-tiba muncul
        
        Args:
            memory_id: ID memori
            
        Returns:
            Flashback effect data
        """
        if memory_id not in self.memory_traces:
            return {'success': False}
        
        trace = self.memory_traces[memory_id]
        
        # Flashback menguatkan memori
        old_strength = trace.strength
        trace.strength = min(1.0, trace.strength + 0.3)
        
        return {
            'success': True,
            'old_strength': old_strength,
            'new_strength': trace.strength,
            'recall_time': trace.get_recall_time(),
            'intensity': trace.strength - old_strength
        }
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    async def get_stats(self) -> Dict:
        """Dapatkan statistik forgetting"""
        total = len(self.memory_traces)
        
        if total == 0:
            return {'total_memories': 0}
        
        # Distribusi strength
        strong = sum(1 for t in self.memory_traces.values() if t.strength >= 0.7)
        medium = sum(1 for t in self.memory_traces.values() if 0.3 <= t.strength < 0.7)
        weak = sum(1 for t in self.memory_traces.values() if t.strength < 0.3)
        
        # Rata-rata strength
        avg_strength = sum(t.strength for t in self.memory_traces.values()) / total
        
        # Rata-rata akses
        avg_access = sum(t.access_count for t in self.memory_traces.values()) / total
        
        return {
            'total_memories': total,
            'strong_memories': strong,
            'medium_memories': medium,
            'weak_memories': weak,
            'avg_strength': round(avg_strength, 2),
            'avg_access_count': round(avg_access, 1),
            'recent_memories': self.recent_memories
        }
    
    async def get_memory_status(self, memory_id: str) -> Optional[Dict]:
        """
        Dapatkan status sebuah memori
        
        Args:
            memory_id: ID memori
            
        Returns:
            Status memori
        """
        if memory_id not in self.memory_traces:
            return None
        
        trace = self.memory_traces[memory_id]
        return trace.to_dict()
    
    def format_forgotten_list(self, forgotten: List[Dict]) -> str:
        """
        Format daftar memori terlupakan untuk debugging
        
        Args:
            forgotten: List dari get_forgotten_memories
            
        Returns:
            Formatted string
        """
        if not forgotten:
            return "Tidak ada memori yang terlupakan"
        
        lines = ["📀 **Memori yang Terlupakan:**"]
        
        for mem in forgotten[:10]:  # Max 10
            days_ago = (time.time() - mem['last_access']) / 86400
            lines.append(
                f"• {mem['memory_id'][:20]}... | "
                f"Strength: {mem['strength']:.2f} | "
                f"Recall: {mem['recall_prob']:.0%} | "
                f"Terakhir: {days_ago:.0f} hari lalu"
            )
        
        return "\n".join(lines)


__all__ = ['SemanticForgetting', 'ForgetType', 'MemoryTrace']
