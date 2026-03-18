#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - SEMANTIC MEMORY
=============================================================================
Menyimpan fakta dan preferensi user
- Fakta-fakta tentang user (pekerjaan, hobi, dll)
- Preferensi seksual user (posisi favorit, area favorit)
- Knowledge graph sederhana
"""

import json
import time
import asyncio
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from pathlib import Path
import logging
import re

logger = logging.getLogger(__name__)


class SemanticMemory:
    """
    Menyimpan fakta dan preferensi user
    Seperti knowledge graph sederhana
    """
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.facts = {}  # {user_id: {role: {fact_type: value}}}
        self.preferences = {}  # {user_id: {role: {pref_type: {item: score}}}}
        self.relationships = {}  # {user_id: {role: relationship_data}}
        self.loaded = False
        
        # Pattern untuk mengekstrak fakta dari percakapan
        self.fact_patterns = [
            (r'kerja (?:sebagai|di|jadi) (\w+)', 'pekerjaan'),
            (r'umur (\d+)', 'umur'),
            (r'tinggal di (\w+)', 'kota'),
            (r'suka (makanan|masakan) (\w+)', 'makanan_favorit'),
            (r'hobi (\w+)', 'hobi'),
            (r'punya (anak|adik|kakak) (\d+)', 'keluarga'),
        ]
        
    async def initialize(self):
        """Load semantic memories from file"""
        try:
            facts_path = self.db_path.parent / "semantic_facts.json"
            prefs_path = self.db_path.parent / "semantic_preferences.json"
            rels_path = self.db_path.parent / "semantic_relationships.json"
            
            # Load facts
            if facts_path.exists():
                with open(facts_path, 'r') as f:
                    self.facts = json.load(f)
                    
            # Load preferences
            if prefs_path.exists():
                with open(prefs_path, 'r') as f:
                    self.preferences = json.load(f)
                    
            # Load relationships
            if rels_path.exists():
                with open(rels_path, 'r') as f:
                    self.relationships = json.load(f)
                    
            logger.info(f"📚 Loaded semantic memories: "
                       f"{len(self.facts)} users facts, "
                       f"{len(self.preferences)} users prefs")
            self.loaded = True
            
        except Exception as e:
            logger.error(f"Error loading semantic memories: {e}")
            self.facts = {}
            self.preferences = {}
            self.relationships = {}
            self.loaded = True
            
    async def save(self):
        """Save all semantic memories"""
        if not self.loaded:
            return
            
        try:
            # Create directory
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save facts
            with open(self.db_path.parent / "semantic_facts.json", 'w') as f:
                json.dump(self.facts, f, indent=2)
                
            # Save preferences
            with open(self.db_path.parent / "semantic_preferences.json", 'w') as f:
                json.dump(self.preferences, f, indent=2)
                
            # Save relationships
            with open(self.db_path.parent / "semantic_relationships.json", 'w') as f:
                json.dump(self.relationships, f, indent=2)
                
            logger.debug("Saved semantic memories")
            
        except Exception as e:
            logger.error(f"Error saving semantic memories: {e}")
            
    # =========================================================================
    # FACT MANAGEMENT
    # =========================================================================
    
    async def add_fact(self, user_id: int, role: str, fact_type: str, value: Any):
        """
        Tambah fakta tentang user
        
        Args:
            user_id: ID user
            role: Role name
            fact_type: 'pekerjaan', 'umur', 'hobi', dll
            value: Nilai fakta
        """
        user_key = str(user_id)
        
        if user_key not in self.facts:
            self.facts[user_key] = {}
            
        if role not in self.facts[user_key]:
            self.facts[user_key][role] = {}
            
        self.facts[user_key][role][fact_type] = {
            'value': value,
            'timestamp': time.time(),
            'confidence': 1.0,
            'source': 'conversation'
        }
        
        logger.info(f"Added fact for user {user_id} role {role}: {fact_type}={value}")
        await self.save()
        
    async def get_fact(self, user_id: int, role: str, fact_type: str) -> Optional[Any]:
        """Get specific fact"""
        user_key = str(user_id)
        
        if (user_key in self.facts and 
            role in self.facts[user_key] and
            fact_type in self.facts[user_key][role]):
            return self.facts[user_key][role][fact_type]['value']
            
        return None
        
    async def get_all_facts(self, user_id: int, role: Optional[str] = None) -> Dict:
        """Get all facts for user"""
        user_key = str(user_id)
        
        if user_key not in self.facts:
            return {}
            
        if role:
            return self.facts[user_key].get(role, {})
        else:
            # Merge all roles
            all_facts = {}
            for r, facts in self.facts[user_key].items():
                for fact_type, data in facts.items():
                    if fact_type not in all_facts:
                        all_facts[fact_type] = data
            return all_facts
            
    async def extract_facts_from_message(self, user_id: int, role: str, message: str):
        """Ekstrak fakta dari pesan user"""
        message_lower = message.lower()
        
        for pattern, fact_type in self.fact_patterns:
            match = re.search(pattern, message_lower)
            if match:
                value = match.group(1)
                await self.add_fact(user_id, role, fact_type, value)
                
    # =========================================================================
    # PREFERENCE MANAGEMENT
    # =========================================================================
    
    async def update_preference(self, user_id: int, role: str, 
                                 pref_type: str, item: str, 
                                 delta: float = 0.1):
        """
        Update preference score
        
        Args:
            user_id: ID user
            role: Role name
            pref_type: 'positions', 'areas', 'activities', 'locations'
            item: Nama item (misal: 'doggy style')
            delta: Perubahan score (+ suka, - tidak suka)
        """
        user_key = str(user_id)
        
        if user_key not in self.preferences:
            self.preferences[user_key] = {}
            
        if role not in self.preferences[user_key]:
            self.preferences[user_key][role] = {
                'positions': {},
                'areas': {},
                'activities': {},
                'locations': {}
            }
            
        if pref_type not in self.preferences[user_key][role]:
            self.preferences[user_key][role][pref_type] = {}
            
        current = self.preferences[user_key][role][pref_type].get(item, 0.5)
        new_score = max(0.1, min(1.0, current + delta))
        
        self.preferences[user_key][role][pref_type][item] = {
            'score': new_score,
            'count': self.preferences[user_key][role][pref_type].get(item, {}).get('count', 0) + 1,
            'last_updated': time.time()
        }
        
        logger.debug(f"Updated preference: user {user_id} {role} {pref_type} {item} -> {new_score}")
        await self.save()
        
    async def get_top_preferences(self, user_id: int, role: str, 
                                    pref_type: str, limit: int = 5) -> List[str]:
        """Get top preferences for user"""
        user_key = str(user_id)
        
        if (user_key not in self.preferences or
            role not in self.preferences[user_key] or
            pref_type not in self.preferences[user_key][role]):
            return []
            
        prefs = self.preferences[user_key][role][pref_type]
        
        # Sort by score
        sorted_items = sorted(
            prefs.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        return [item for item, _ in sorted_items[:limit]]
        
    async def get_preference_score(self, user_id: int, role: str,
                                    pref_type: str, item: str) -> float:
        """Get preference score for specific item"""
        user_key = str(user_id)
        
        if (user_key in self.preferences and
            role in self.preferences[user_key] and
            pref_type in self.preferences[user_key][role] and
            item in self.preferences[user_key][role][pref_type]):
            return self.preferences[user_key][role][pref_type][item]['score']
            
        return 0.5  # Default neutral
        
    # =========================================================================
    # RELATIONSHIP MANAGEMENT
    # =========================================================================
    
    async def update_relationship(self, user_id: int, role: str, data: Dict):
        """Update relationship data"""
        user_key = str(user_id)
        
        if user_key not in self.relationships:
            self.relationships[user_key] = {}
            
        if role not in self.relationships[user_key]:
            self.relationships[user_key][role] = {
                'started_at': time.time(),
                'total_interactions': 0,
                'total_intimacy': 0,
                'last_interaction': time.time(),
                'milestones': [],
                'status': 'hts'  # hts, fwb, pacar
            }
            
        # Update fields
        for key, value in data.items():
            self.relationships[user_key][role][key] = value
            
        self.relationships[user_key][role]['last_interaction'] = time.time()
        
        if 'total_interactions' in data:
            self.relationships[user_key][role]['total_interactions'] += 1
            
        await self.save()
        
    async def get_relationship(self, user_id: int, role: str) -> Optional[Dict]:
        """Get relationship data"""
        user_key = str(user_id)
        
        if user_key in self.relationships and role in self.relationships[user_key]:
            return self.relationships[user_key][role]
            
        return None
        
    async def get_all_relationships(self, user_id: int) -> List[Dict]:
        """Get all relationships for user"""
        user_key = str(user_id)
        
        if user_key not in self.relationships:
            return []
            
        relationships = []
        for role, data in self.relationships[user_key].items():
            relationships.append({
                'role': role,
                **data
            })
            
        # Sort by last interaction
        relationships.sort(key=lambda x: x.get('last_interaction', 0), reverse=True)
        
        return relationships
        
    # =========================================================================
    # QUERY & UTILITY
    # =========================================================================
    
    async def get_user_summary(self, user_id: int) -> str:
        """Get summary of all known information about user"""
        user_key = str(user_id)
        
        facts = await self.get_all_facts(user_id)
        relationships = await self.get_all_relationships(user_id)
        
        summary = []
        
        # Facts
        if facts:
            fact_str = "Diketahui tentang kamu: "
            facts_list = []
            for fact_type, data in facts.items():
                facts_list.append(f"{fact_type}: {data['value']}")
            summary.append(fact_str + ", ".join(facts_list))
            
        # Relationships
        if relationships:
            rel_str = "Hubungan aktif: "
            rel_list = []
            for rel in relationships[:3]:
                status = rel.get('status', 'hts')
                rel_list.append(f"{rel['role']} ({status})")
            summary.append(rel_str + ", ".join(rel_list))
            
        # Top preferences
        for role in set(rel['role'] for rel in relationships):
            top_positions = await self.get_top_preferences(user_id, role, 'positions', 3)
            if top_positions:
                summary.append(f"Dengan role {role}, kamu suka: {', '.join(top_positions)}")
                
        return "\n".join(summary) if summary else "Belum ada data tentang user"
        
    async def delete_user_data(self, user_id: int):
        """Delete all data for user"""
        user_key = str(user_id)
        
        if user_key in self.facts:
            del self.facts[user_key]
        if user_key in self.preferences:
            del self.preferences[user_key]
        if user_key in self.relationships:
            del self.relationships[user_key]
            
        await self.save()
        logger.info(f"Deleted all semantic data for user {user_id}")
        
    async def get_stats(self) -> Dict:
        """Get statistics"""
        return {
            "total_users_facts": len(self.facts),
            "total_users_preferences": len(self.preferences),
            "total_users_relationships": len(self.relationships),
            "total_facts": sum(len(facts) for facts in self.facts.values()),
            "total_preferences": sum(
                sum(len(prefs) for prefs in user_prefs.values())
                for user_prefs in self.preferences.values()
            ),
            "total_relationships": sum(
                len(rels) for rels in self.relationships.values()
            )
        }


__all__ = ['SemanticMemory']
