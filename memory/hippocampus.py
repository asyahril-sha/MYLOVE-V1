#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - HIPPOCAMPUS MEMORY SYSTEM
=============================================================================
Sistem memori terinspirasi hippocampus manusia
- Compact Memory: ringkasan terus-menerus
- Episodic Memory: momen penting dengan konteks
- Semantic Memory: pengetahuan yang diekstrak
- Semantic Forgetting: memori jarang diakses dilupakan
- Vector embeddings untuk similarity search
=============================================================================
"""

import time
import logging
import json
import hashlib
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
from collections import deque
import random

logger = logging.getLogger(__name__)


class MemoryType(str, Enum):
    """Tipe memori"""
    COMPACT = "compact"           # Ringkasan terus-menerus
    EPISODIC = "episodic"         # Momen spesial dengan konteks
    SEMANTIC = "semantic"         # Fakta dan pengetahuan
    RELATIONSHIP = "relationship"  # Data hubungan


class MemoryImportance(str, Enum):
    """Tingkat kepentingan memori"""
    CRITICAL = "critical"     # Tidak pernah dilupakan (first kiss, first intim)
    HIGH = "high"              # Jarang dilupakan
    MEDIUM = "medium"          # Bisa dilupakan setelah beberapa waktu
    LOW = "low"                # Cepat dilupakan


class HippocampusMemory:
    """
    Sistem memori seperti hippocampus manusia
    Menggabungkan berbagai jenis memori dengan forgetting mechanism
    """
    
    def __init__(self, vector_db=None, episodic_db=None, semantic_db=None):
        self.vector_db = vector_db          # Untuk similarity search
        self.episodic_db = episodic_db      # Untuk momen spesial
        self.semantic_db = semantic_db      # Untuk fakta
        
        # Compact memory (ringkasan berkelanjutan)
        self.compact_memory = {}  # {session_id: deque of summaries}
        
        # Access counters untuk semantic forgetting
        self.access_count = {}  # {memory_id: count}
        self.last_access = {}   # {memory_id: timestamp}
        
        # Importance thresholds
        self.importance_weights = {
            MemoryImportance.CRITICAL: 1.0,   # Never forget
            MemoryImportance.HIGH: 0.8,        # Forget after long time
            MemoryImportance.MEDIUM: 0.5,       # Forget after medium time
            MemoryImportance.LOW: 0.2           # Forget quickly
        }
        
        # Forgetting parameters (dalam hari)
        self.forgetting_days = {
            MemoryImportance.CRITICAL: 9999,   # Never
            MemoryImportance.HIGH: 180,         # 6 bulan
            MemoryImportance.MEDIUM: 90,         # 3 bulan
            MemoryImportance.LOW: 30             # 1 bulan
        }
        
        # Consolidation parameters
        self.consolidation_interval = 3600  # 1 jam
        self.last_consolidation = time.time()
        
        logger.info("✅ HippocampusMemory initialized")
    
    # =========================================================================
    # MEMORY STORAGE
    # =========================================================================
    
    async def store_memory(self, 
                          session_id: str,
                          content: str,
                          memory_type: MemoryType,
                          importance: MemoryImportance = MemoryImportance.MEDIUM,
                          context: Optional[Dict] = None,
                          metadata: Optional[Dict] = None) -> str:
        """
        Menyimpan memori ke sistem yang sesuai
        
        Args:
            session_id: ID sesi
            content: Konten memori
            memory_type: Tipe memori
            importance: Tingkat kepentingan
            context: Konteks tambahan
            metadata: Metadata tambahan
            
        Returns:
            memory_id
        """
        memory_id = self._generate_memory_id(session_id, memory_type)
        
        memory_data = {
            'memory_id': memory_id,
            'session_id': session_id,
            'content': content,
            'type': memory_type,
            'importance': importance,
            'importance_score': self.importance_weights[importance],
            'timestamp': time.time(),
            'access_count': 0,
            'last_access': time.time(),
            'context': context or {},
            'metadata': metadata or {}
        }
        
        # Simpan berdasarkan tipe
        if memory_type == MemoryType.COMPACT:
            await self._store_compact(session_id, memory_data)
        elif memory_type == MemoryType.EPISODIC:
            await self._store_episodic(memory_data)
        elif memory_type == MemoryType.SEMANTIC:
            await self._store_semantic(memory_data)
        elif memory_type == MemoryType.RELATIONSHIP:
            await self._store_relationship(memory_data)
        
        # Track access
        self.access_count[memory_id] = 0
        self.last_access[memory_id] = time.time()
        
        logger.debug(f"Memory stored: {memory_id} ({memory_type.value})")
        
        return memory_id
    
    def _generate_memory_id(self, session_id: str, memory_type: MemoryType) -> str:
        """Generate unique memory ID"""
        timestamp = int(time.time())
        random_suffix = random.randint(1000, 9999)
        return f"MEM_{session_id}_{memory_type.value}_{timestamp}_{random_suffix}"
    
    async def _store_compact(self, session_id: str, memory_data: Dict):
        """Simpan compact memory (ringkasan)"""
        if session_id not in self.compact_memory:
            self.compact_memory[session_id] = deque(maxlen=50)  # Max 50 ringkasan
        
        self.compact_memory[session_id].append(memory_data)
    
    async def _store_episodic(self, memory_data: Dict):
        """Simpan episodic memory ke database"""
        if self.episodic_db:
            await self.episodic_db.save(memory_data)
    
    async def _store_semantic(self, memory_data: Dict):
        """Simpan semantic memory ke database"""
        if self.semantic_db:
            await self.semantic_db.save(memory_data)
    
    async def _store_relationship(self, memory_data: Dict):
        """Simpan relationship memory"""
        # Akan diimplementasikan di relationship system
    
    # =========================================================================
    # MEMORY RETRIEVAL
    # =========================================================================
    
    async def recall(self, 
                    session_id: str,
                    query: str,
                    memory_type: Optional[MemoryType] = None,
                    limit: int = 5,
                    min_importance: float = 0.3) -> List[Dict]:
        """
        Mengingat memori berdasarkan query
        
        Args:
            session_id: ID sesi
            query: Query pencarian
            memory_type: Tipe memori (optional)
            limit: Jumlah maksimal hasil
            min_importance: Minimal importance score
            
        Returns:
            List of memories
        """
        results = []
        
        # 1. Cari di compact memory (recent summaries)
        compact_results = await self._search_compact(session_id, query, limit)
        results.extend(compact_results)
        
        # 2. Cari di vector DB (semantic search)
        if self.vector_db:
            vector_results = await self._search_vector(query, session_id, memory_type, limit)
            results.extend(vector_results)
        
        # 3. Filter by importance
        results = [r for r in results if r.get('importance_score', 0) >= min_importance]
        
        # 4. Sort by relevance (placeholder - akan pakai similarity score)
        results.sort(key=lambda x: x.get('relevance', 0), reverse=True)
        
        # 5. Update access counters
        for r in results[:limit]:
            mem_id = r.get('memory_id')
            if mem_id:
                self.access_count[mem_id] = self.access_count.get(mem_id, 0) + 1
                self.last_access[mem_id] = time.time()
        
        return results[:limit]
    
    async def _search_compact(self, session_id: str, query: str, limit: int) -> List[Dict]:
        """Search di compact memory"""
        if session_id not in self.compact_memory:
            return []
        
        results = []
        query_lower = query.lower()
        
        for mem in self.compact_memory[session_id]:
            content = mem.get('content', '').lower()
            # Simple keyword matching (akan diganti dengan vector search)
            if any(word in content for word in query_lower.split()):
                mem_copy = mem.copy()
                mem_copy['relevance'] = 0.5  # Default relevance
                mem_copy['source'] = 'compact'
                results.append(mem_copy)
        
        return results[:limit]
    
    async def _search_vector(self, query: str, session_id: str, 
                             memory_type: Optional[MemoryType], limit: int) -> List[Dict]:
        """Search di vector database"""
        if not self.vector_db:
            return []
        
        try:
            # Gunakan vector search
            vector_results = await self.vector_db.search(
                query=query,
                session_id=session_id,
                memory_type=memory_type.value if memory_type else None,
                limit=limit
            )
            
            for r in vector_results:
                r['source'] = 'vector'
            
            return vector_results
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return []
    
    async def recall_random(self, session_id: str, memory_type: Optional[MemoryType] = None) -> Optional[Dict]:
        """
        Mengingat memori random (untuk flashback)
        """
        all_memories = []
        
        # Ambil dari compact
        if session_id in self.compact_memory:
            all_memories.extend(list(self.compact_memory[session_id]))
        
        # Ambil dari vector (recent)
        if self.vector_db:
            try:
                recent = await self.vector_db.get_recent(session_id, limit=20)
                all_memories.extend(recent)
            except:
                pass
        
        if not all_memories:
            return None
        
        return random.choice(all_memories)
    
    # =========================================================================
    # MEMORY CONSOLIDATION
    # =========================================================================
    
    async def consolidate(self, force: bool = False):
        """
        Memory consolidation periodik
        - Memindahkan memori penting dari compact ke episodic
        - Membuang memori yang tidak penting
        - Membuat ringkasan baru
        """
        now = time.time()
        
        if not force and (now - self.last_consolidation) < self.consolidation_interval:
            return
        
        logger.info("🧠 Starting memory consolidation...")
        
        # Consolidate compact memory per session
        for session_id, memories in self.compact_memory.items():
            await self._consolidate_session_memories(session_id, list(memories))
        
        # Run semantic forgetting
        await self._run_forgetting()
        
        self.last_consolidation = now
        logger.info("✅ Memory consolidation completed")
    
    async def _consolidate_session_memories(self, session_id: str, memories: List[Dict]):
        """
        Consolidate memori untuk satu sesi
        """
        # Kelompokkan memori berdasarkan importance
        important_memories = [m for m in memories 
                             if m.get('importance_score', 0) >= 0.7]
        
        # Pindahkan memori penting ke episodic
        for mem in important_memories:
            if mem.get('type') != MemoryType.EPISODIC:
                mem['type'] = MemoryType.EPISODIC
                await self._store_episodic(mem)
        
        # Buat ringkasan dari memori-memori ini
        if len(memories) >= 10:
            summary = await self._create_summary(memories)
            if summary:
                await self.store_memory(
                    session_id=session_id,
                    content=summary,
                    memory_type=MemoryType.COMPACT,
                    importance=MemoryImportance.MEDIUM,
                    context={'type': 'consolidated_summary'}
                )
    
    async def _create_summary(self, memories: List[Dict]) -> Optional[str]:
        """Buat ringkasan dari kumpulan memori"""
        if not memories:
            return None
        
        # Ambil konten
        contents = [m.get('content', '') for m in memories[-10:]]
        
        # Simple summarization (akan diganti dengan AI)
        if len(contents) > 3:
            return f"Percakapan terakhir: {', '.join(contents[:3])}..."
        else:
            return ', '.join(contents)
    
    # =========================================================================
    # SEMANTIC FORGETTING
    # =========================================================================
    
    async def _run_forgetting(self):
        """
        Melupakan memori yang jarang diakses
        """
        now = time.time()
        forgotten = 0
        
        for mem_id, last_access in self.last_access.items():
            # Hitung umur memori
            age_days = (now - last_access) / 86400
            
            # Dapatkan importance dari memori ini
            importance = await self._get_memory_importance(mem_id)
            
            # Cek apakah sudah melewati batas forgetting
            forget_after = self.forgetting_days.get(importance, 90)
            
            if age_days > forget_after:
                # Lupakan memori ini
                if await self._delete_memory(mem_id):
                    forgotten += 1
        
        if forgotten > 0:
            logger.info(f"🧹 Semantic forgetting: {forgotten} memories forgotten")
    
    async def _get_memory_importance(self, memory_id: str) -> MemoryImportance:
        """Dapatkan importance dari memory ID"""
        # Default
        return MemoryImportance.MEDIUM
    
    async def _delete_memory(self, memory_id: str) -> bool:
        """Hapus memori dari semua storage"""
        try:
            # Hapus dari access tracking
            self.access_count.pop(memory_id, None)
            self.last_access.pop(memory_id, None)
            
            # Hapus dari vector DB
            if self.vector_db:
                await self.vector_db.delete(memory_id)
            
            # Hapus dari episodic
            if self.episodic_db:
                await self.episodic_db.delete(memory_id)
            
            # Hapus dari compact (perlu iterate)
            for session_id, memories in self.compact_memory.items():
                self.compact_memory[session_id] = deque(
                    [m for m in memories if m.get('memory_id') != memory_id],
                    maxlen=50
                )
            
            return True
        except Exception as e:
            logger.error(f"Error deleting memory {memory_id}: {e}")
            return False
    
    # =========================================================================
    # FLASHBACK GENERATION
    # =========================================================================
    
    async def generate_flashback(self, session_id: str, trigger: Optional[str] = None) -> Optional[str]:
        """
        Generate flashback ke momen lalu
        
        Args:
            session_id: ID sesi
            trigger: Kata kunci pemicu (optional)
            
        Returns:
            Flashback text
        """
        if trigger:
            # Cari memori yang relevan dengan trigger
            memories = await self.recall(session_id, trigger, limit=1)
        else:
            # Random memory
            memories = [await self.recall_random(session_id)] if await self.recall_random(session_id) else []
        
        if not memories:
            return None
        
        memory = memories[0]
        content = memory.get('content', '')
        
        # Format flashback
        time_ago = self._format_time_ago(memory.get('timestamp', time.time()))
        
        flashbacks = [
            f"Inget nggak waktu {content}? {time_ago}...",
            f"Jadi inget, dulu {content}. {time_ago}.",
            f"Kangen masa-masa {content}... {time_ago}.",
            f"Ngomong-ngomong, inget {content}? {time_ago}."
        ]
        
        return random.choice(flashbacks)
    
    def _format_time_ago(self, timestamp: float) -> str:
        """Format waktu yang lalu"""
        diff = time.time() - timestamp
        
        if diff < 60:
            return "baru aja"
        elif diff < 3600:
            minutes = int(diff / 60)
            return f"{minutes} menit lalu"
        elif diff < 86400:
            hours = int(diff / 3600)
            return f"{hours} jam lalu"
        elif diff < 604800:
            days = int(diff / 86400)
            return f"{days} hari lalu"
        elif diff < 2592000:
            weeks = int(diff / 604800)
            return f"{weeks} minggu lalu"
        else:
            months = int(diff / 2592000)
            return f"{months} bulan lalu"
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    async def get_stats(self) -> Dict:
        """Dapatkan statistik memori"""
        stats = {
            'compact_memories': sum(len(m) for m in self.compact_memory.values()),
            'tracked_memories': len(self.access_count),
            'last_consolidation': datetime.fromtimestamp(self.last_consolidation).isoformat(),
            'forgetting_thresholds': self.forgetting_days
        }
        
        # Hitung distribusi importance
        # (akan diimplementasikan lebih lanjut)
        
        return stats


__all__ = ['HippocampusMemory', 'MemoryType', 'MemoryImportance']
