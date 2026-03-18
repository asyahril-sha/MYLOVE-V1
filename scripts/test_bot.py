#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script untuk testing bot components
Berguna untuk debug sebelum deploy
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_config():
    """Test configuration loading"""
    logger.info("Testing configuration...")
    
    try:
        from config import settings
        logger.info(f"✅ Config loaded: Database={settings.database.type}")
        logger.info(f"✅ Admin ID: {settings.admin_id}")
        logger.info(f"✅ AI Model: {settings.ai.model}")
        return True
    except Exception as e:
        logger.error(f"❌ Config error: {e}")
        return False

async def test_database():
    """Test database connection"""
    logger.info("Testing database...")
    
    try:
        from database.connection import init_db_sync, get_db_sync
        
        # Test SQLite
        init_db_sync()
        logger.info("✅ Database initialized")
        
        # Test query
        with get_db_sync() as db:
            result = db.execute("SELECT 1").fetchone()
            logger.info(f"✅ Query test: {result}")
            
        return True
    except Exception as e:
        logger.error(f"❌ Database error: {e}")
        return False

async def test_memory():
    """Test memory system"""
    logger.info("Testing memory system...")
    
    try:
        from memory.vector_db import VectorMemory
        from config import settings
        
        memory = VectorMemory(settings.memory.vector_db_dir)
        await memory.initialize()
        
        # Test save
        await memory.save_interaction(
            user_id=123,
            message="Test message",
            response="Test response",
            context={"role": "test"}
        )
        logger.info("✅ Memory save test passed")
        
        # Test search
        results = await memory.search("test", limit=5)
        logger.info(f"✅ Memory search test: {len(results)} results")
        
        await memory.close()
        return True
    except Exception as e:
        logger.error(f"❌ Memory error: {e}")
        return False

async def test_ai():
    """Test AI engine (requires API key)"""
    logger.info("Testing AI engine...")
    
    try:
        from core.ai_engine import DeepSeekEngine
        from config import settings
        
        if not settings.deepseek_api_key or settings.deepseek_api_key == "your_deepseek_api_key_here":
            logger.warning("⚠️ DeepSeek API key not set, skipping AI test")
            return True
            
        engine = DeepSeekEngine(
            api_key=settings.deepseek_api_key,
            memory=None
        )
        
        # Test simple prompt
        response = await engine._call_deepseek([
            {"role": "user", "content": "Say 'test passed'"}
        ])
        
        logger.info(f"✅ AI test: {response[:50]}...")
        return True
    except Exception as e:
        logger.error(f"❌ AI error: {e}")
        return False

async def test_session():
    """Test session management"""
    logger.info("Testing session management...")
    
    try:
        from session.storage import SessionStorage
        from session.unique_id import SessionID
        from config import settings
        
        storage = SessionStorage(
            db_path=settings.database.path,
            session_dir=settings.session.session_dir
        )
        
        # Test ID generation
        session_id = SessionID.generate("ipar", 12345)
        logger.info(f"✅ Session ID: {session_id}")
        
        # Test parse
        parsed = SessionID.parse(session_id)
        logger.info(f"✅ Session parse: {parsed}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Session error: {e}")
        return False

async def test_public_areas():
    """Test public areas system"""
    logger.info("Testing public areas...")
    
    try:
        from public.auto_select import LocationAutoSelector
        from config import settings
        
        selector = LocationAutoSelector()
        
        # Test location count
        total = sum(len(v) for v in settings.public.locations.values())
        logger.info(f"✅ {total} locations loaded")
        
        # Test auto-detect
        test_messages = [
            "Ajak ke toilet umum yuk",
            "Di mobil aja",
            "Ke pantai malam"
        ]
        
        for msg in test_messages:
            location = await selector.detect_location_intent(msg)
            logger.info(f"  '{msg}' → {location}")
            
        return True
    except Exception as e:
        logger.error(f"❌ Public areas error: {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    logger.info("="*50)
    logger.info("MYLOVE ULTIMATE - SYSTEM TEST")
    logger.info("="*50)
    
    tests = [
        ("Config", test_config),
        ("Database", test_database),
        ("Memory", test_memory),
        ("AI", test_ai),
        ("Session", test_session),
        ("Public Areas", test_public_areas),
    ]
    
    results = []
    
    for name, test_func in tests:
        logger.info("-"*40)
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"Test {name} crashed: {e}")
            results.append((name, False))
            
    logger.info("="*50)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("="*50)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {name}")
        if not result:
            all_passed = False
            
    logger.info("="*50)
    
    if all_passed:
        logger.info("✅ ALL TESTS PASSED - Ready for deployment!")
        return 0
    else:
        logger.error("❌ SOME TESTS FAILED - Check logs above")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
