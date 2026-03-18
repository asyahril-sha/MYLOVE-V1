#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - VECTOR DATABASE (ChromaDB)
=============================================================================
- Semantic search untuk memory
- Menyimpan interaksi dalam bentuk vector
- Fast similarity search
"""

import chromadb
from chromadb.config import Settings
import json
import uuid
import time
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import logging

from config import settings

logger = logging.getLogger(__name__)


class VectorMemory:
    """
    Vector database menggunakan ChromaDB
    Untuk semantic search dan memory retrieval
    """
    
    def __init__(self, persist_directory: Path):
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Create directory if not exists
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            
            # Initialize client
            self.client = chromadb.PersistentClient(
                path=str(self.persist_directory),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Create or get collection
            try:
                self.collection = self.client.get_collection("mylove_memories")
                logger.info("📚 Loaded existing vector collection")
            except:
                self.collection = self.client.create_collection(
                    name="mylove_memories",
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info("📚 Created new vector collection")
                
            self.initialized = True
            logger.info(f"✅ VectorMemory initialized at {self.persist_directory}")
            
        except Exception as e:
            logger.error(f"Failed to initialize VectorMemory: {e}")
            raise
            
    async def save_interaction(self, user_id: int, message: str, response: str, 
                               context: Dict[str, Any]):
        """
        Simpan interaksi ke vector database
        
        Args:
            user_id: ID user
            message: Pesan dari user
            response: Respon bot
            context: Konteks tambahan (role, mood, intimacy, dll)
        """
        if not self.initialized:
            logger.warning("VectorMemory not initialized")
            return
            
        try:
            # Generate unique ID
            memory_id = str(uuid.uuid4())
            
            # Combine text for embedding
            text = f"User: {message}\nBot: {response}"
            
            # Metadata untuk filtering
            metadata = {
                "user_id": str(user_id),
                "role": context.get('role', 'unknown'),
                "timestamp": time.time(),
                "date": datetime.now().isoformat(),
                "mood": context.get('mood', 'netral'),
                "intimacy_level": context.get('intimacy', 1),
                "importance": context.get('importance', 0.5),
                "has_sexual": str('sex' in message.lower() or 'sex' in response.lower())
            }
            
            # Add to collection
            self.collection.add(
                documents=[text],
                metadatas=[metadata],
                ids=[memory_id]
            )
            
            logger.debug(f"Saved memory {memory_id} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error saving to vector DB: {e}")
            
    async def search(self, query: str, user_id: Optional[int] = None, 
                     role: Optional[str] = None, limit: int = 5) -> List[Dict]:
        """
        Search for similar memories
        
        Args:
            query: Query text
            user_id: Filter by user ID
            role: Filter by role
            limit: Max results
            
        Returns:
            List of similar memories
        """
        if not self.initialized:
            logger.warning("VectorMemory not initialized")
            return []
            
        try:
            # Build where clause
            where = {}
            if user_id:
                where["user_id"] = str(user_id)
            if role:
                where["role"] = role
                
            # Query
            results = self.collection.query(
                query_texts=[query],
                n_results=min(limit * 2, 20),  # Get more for filtering
                where=where if where else None
            )
            
            # Format results
            memories = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    memories.append({
                        "content": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else 0,
                        "id": results['ids'][0][i] if results['ids'] else None
                    })
                    
            return memories[:limit]
            
        except Exception as e:
            logger.error(f"Error searching vector DB: {e}")
            return []
            
    async def get_recent(self, user_id: int, role: Optional[str] = None, 
                         limit: int = 10) -> List[Dict]:
        """Get recent memories for user"""
        
        if not self.initialized:
            return []
            
        try:
            # Get all memories for user
            results = self.collection.get(
                where={"user_id": str(user_id)},
                limit=limit * 2
            )
            
            # Sort by timestamp
            memories = []
            if results['metadatas']:
                for i, metadata in enumerate(results['metadatas']):
                    if role and metadata.get('role') != role:
                        continue
                    memories.append({
                        "content": results['documents'][i],
                        "metadata": metadata,
                        "id": results['ids'][i]
                    })
                    
            # Sort by timestamp (newest first)
            memories.sort(key=lambda x: x['metadata'].get('timestamp', 0), reverse=True)
            
            return memories[:limit]
            
        except Exception as e:
            logger.error(f"Error getting recent memories: {e}")
            return []
            
    async def get_random(self, user_id: Optional[int] = None, limit: int = 1) -> List[Dict]:
        """Get random memories"""
        
        if not self.initialized:
            return []
            
        try:
            where = {"user_id": str(user_id)} if user_id else None
            
            results = self.collection.get(
                where=where,
                limit=100  # Get many then random pick
            )
            
            if not results['documents']:
                return []
                
            # Random selection
            import random
            indices = random.sample(range(len(results['documents'])), 
                                   min(limit, len(results['documents'])))
            
            memories = []
            for idx in indices:
                memories.append({
                    "content": results['documents'][idx],
                    "metadata": results['metadatas'][idx],
                    "id": results['ids'][idx]
                })
                
            return memories
            
        except Exception as e:
            logger.error(f"Error getting random memories: {e}")
            return []
            
    async def delete_memory(self, memory_id: str):
        """Delete specific memory"""
        
        if not self.initialized:
            return
            
        try:
            self.collection.delete(ids=[memory_id])
            logger.info(f"Deleted memory {memory_id}")
        except Exception as e:
            logger.error(f"Error deleting memory: {e}")
            
    async def delete_user_memories(self, user_id: int):
        """Delete all memories for user"""
        
        if not self.initialized:
            return
            
        try:
            # Get all IDs for user
            results = self.collection.get(where={"user_id": str(user_id)})
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                logger.info(f"Deleted {len(results['ids'])} memories for user {user_id}")
        except Exception as e:
            logger.error(f"Error deleting user memories: {e}")
            
    async def get_stats(self) -> Dict:
        """Get collection statistics"""
        
        if not self.initialized:
            return {"error": "Not initialized"}
            
        try:
            count = self.collection.count()
            
            # Get sample metadata
            sample = self.collection.get(limit=10)
            
            # Count by role
            roles = {}
            if sample['metadatas']:
                for meta in sample['metadatas']:
                    role = meta.get('role', 'unknown')
                    roles[role] = roles.get(role, 0) + 1
                    
            return {
                "total_memories": count,
                "roles_distribution": roles,
                "collection_name": "mylove_memories",
                "persist_directory": str(self.persist_directory)
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}
            
    async def close(self):
        """Close connection"""
        # ChromaDB doesn't need explicit close
        self.initialized = False
        logger.info("VectorMemory closed")


__all__ = ['VectorMemory']
