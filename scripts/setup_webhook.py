#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script untuk setup webhook manual
Berguna untuk debugging webhook issues
"""

import asyncio
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from telegram import Bot
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

async def check_webhook():
    """Check current webhook status"""
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        logger.error("TELEGRAM_TOKEN not found in .env")
        return
        
    bot = Bot(token=token)
    
    # Get webhook info
    info = await bot.get_webhook_info()
    
    logger.info("="*50)
    logger.info("WEBHOOK STATUS")
    logger.info("="*50)
    logger.info(f"URL: {info.url}")
    logger.info(f"Pending updates: {info.pending_update_count}")
    logger.info(f"Last error: {info.last_error_date} - {info.last_error_message}")
    logger.info(f"Max connections: {info.max_connections}")
    logger.info("="*50)
    
    return info

async def set_webhook():
    """Set webhook manually"""
    token = os.getenv("TELEGRAM_TOKEN")
    railway_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN")
    
    if not token:
        logger.error("TELEGRAM_TOKEN not found")
        return
        
    if not railway_domain:
        logger.error("RAILWAY_PUBLIC_DOMAIN not found")
        return
        
    bot = Bot(token=token)
    webhook_url = f"https://{railway_domain}/webhook/{token}"
    
    logger.info(f"Setting webhook to: {webhook_url}")
    
    # Set webhook
    await bot.set_webhook(
        url=webhook_url,
        allowed_updates=['message', 'callback_query', 'inline_query'],
        drop_pending_updates=True,
        max_connections=40
    )
    
    # Verify
    await check_webhook()

async def delete_webhook():
    """Delete webhook (fallback to polling)"""
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        logger.error("TELEGRAM_TOKEN not found")
        return
        
    bot = Bot(token=token)
    
    logger.info("Deleting webhook...")
    await bot.delete_webhook(drop_pending_updates=True)
    
    logger.info("Webhook deleted, bot will use polling")
    await check_webhook()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Webhook Manager")
    parser.add_argument("action", choices=["check", "set", "delete"], 
                       help="Action to perform")
    
    args = parser.parse_args()
    
    if args.action == "check":
        asyncio.run(check_webhook())
    elif args.action == "set":
        asyncio.run(set_webhook())
    elif args.action == "delete":
        asyncio.run(delete_webhook())
