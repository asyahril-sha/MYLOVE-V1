#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - WEBHOOK HANDLER
=============================================================================
- Setup webhook dengan retry mechanism
- Fallback ke polling jika webhook gagal
- Health check endpoint
"""

import os
import logging
import asyncio
from typing import Optional
from telegram import Update
from telegram.ext import Application
from fastapi import FastAPI, Request, Response
import uvicorn

from config import settings
from ..utils.logger import setup_logging

logger = logging.getLogger(__name__)


class WebhookManager:
    """
    Manajer webhook dengan retry mechanism dan fallback ke polling
    """
    
    def __init__(self, app: Application):
        self.app = app
        self.fastapi_app = FastAPI(title="MYLOVE Ultimate", version="1.0")
        self.webhook_url: Optional[str] = None
        self.webhook_mode = False
        self.retry_count = 0
        self.max_retries = 5
        self.backoff_factor = 2
        
        # Setup routes
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup FastAPI routes untuk webhook"""
        
        @self.fastapi_app.get("/")
        async def root():
            """Root endpoint - info bot"""
            return {
                "name": "MYLOVE Ultimate V1",
                "status": "running",
                "mode": "webhook" if self.webhook_mode else "polling",
                "admin_id": settings.admin_id
            }
            
        @self.fastapi_app.get("/health")
        async def health_check():
            """Health check endpoint untuk Railway"""
            return {
                "status": "healthy",
                "bot_running": self.app is not None,
                "webhook_mode": self.webhook_mode,
                "webhook_url": self.webhook_url
            }
            
        @self.fastapi_app.get("/debug")
        async def debug_info():
            """Debug endpoint"""
            webhook_info = None
            if self.app and self.app.bot:
                try:
                    webhook_info = await self.app.bot.get_webhook_info()
                except:
                    pass
                    
            return {
                "webhook_mode": self.webhook_mode,
                "webhook_url": self.webhook_url,
                "webhook_info": {
                    "url": webhook_info.url if webhook_info else None,
                    "pending_updates": webhook_info.pending_update_count if webhook_info else 0,
                    "last_error": str(webhook_info.last_error_message) if webhook_info and webhook_info.last_error_message else None
                } if webhook_info else None,
                "retry_count": self.retry_count,
                "admin_id": settings.admin_id
            }
            
        @self.fastapi_app.post(f"/webhook/{settings.telegram_token}")
        async def webhook(request: Request):
            """
            Endpoint utama webhook dari Telegram
            URL: https://domain.com/webhook/TOKEN
            """
            if not self.app:
                logger.error("Bot not initialized")
                return Response(status_code=503, content="Bot not ready")
                
            try:
                # Parse update dari Telegram
                data = await request.json()
                update = Update.de_json(data, self.app.bot)
                
                # Process update di background
                asyncio.create_task(self._process_update(update))
                
                return Response(status_code=200)
                
            except Exception as e:
                logger.error(f"Webhook error: {e}")
                return Response(status_code=500)
                
        @self.fastapi_app.post("/webhook/test")
        async def test_webhook():
            """Test endpoint untuk verifikasi webhook"""
            return {"message": "Webhook is working!"}
            
    async def _process_update(self, update: Update):
        """Process update in background"""
        try:
            await self.app.process_update(update)
            logger.debug(f"Processed update: {update.update_id}")
        except Exception as e:
            logger.error(f"Error processing update: {e}")
            
    async def setup_webhook(self, retry: bool = True) -> bool:
        """
        Setup webhook dengan retry mechanism
        
        Args:
            retry: Jika True, akan retry jika gagal
            
        Returns:
            True jika sukses, False jika fallback ke polling
        """
        # Tentukan URL webhook
        if settings.railway.public_domain:
            base_url = f"https://{settings.railway.public_domain}"
        elif settings.webhook.url:
            base_url = settings.webhook.url.rstrip('/')
        else:
            # Untuk local development
            base_url = f"http://localhost:{settings.webhook.port}"
            logger.warning(f"No public domain, using local URL: {base_url}")
            
        self.webhook_url = f"{base_url}/webhook/{settings.telegram_token}"
        
        logger.info(f"🔗 Setting webhook to: {self.webhook_url}")
        
        if not retry:
            # Single attempt
            return await self._set_webhook_single()
        else:
            # With retry
            return await self._set_webhook_with_retry()
            
    async def _set_webhook_single(self) -> bool:
        """Set webhook single attempt"""
        try:
            await self.app.bot.set_webhook(
                url=self.webhook_url,
                allowed_updates=['message', 'callback_query', 'inline_query'],
                drop_pending_updates=True,
                max_connections=40,
                timeout=30
            )
            
            # Verify
            webhook_info = await self.app.bot.get_webhook_info()
            if webhook_info.url == self.webhook_url:
                logger.info(f"✅ Webhook set successfully: {webhook_info.url}")
                logger.info(f"   Pending updates: {webhook_info.pending_update_count}")
                self.webhook_mode = True
                return True
            else:
                logger.error(f"Webhook verification failed: {webhook_info.url}")
                return False
                
        except Exception as e:
            logger.error(f"Webhook setup failed: {e}")
            return False
            
    async def _set_webhook_with_retry(self) -> bool:
        """Set webhook dengan exponential backoff retry"""
        for attempt in range(self.max_retries):
            logger.info(f"Webhook attempt {attempt + 1}/{self.max_retries}")
            
            if await self._set_webhook_single():
                self.retry_count = 0
                return True
                
            # Hitung waktu tunggu
            wait_time = self.backoff_factor ** attempt
            logger.warning(f"Webhook failed, retrying in {wait_time}s...")
            
            await asyncio.sleep(wait_time)
            
        # Semua percobaan gagal
        logger.error(f"All {self.max_retries} webhook attempts failed")
        self.retry_count = self.max_retries
        
        return False
        
    async def delete_webhook(self):
        """Delete webhook (fallback ke polling)"""
        try:
            await self.app.bot.delete_webhook(drop_pending_updates=True)
            logger.info("✅ Webhook deleted")
            self.webhook_mode = False
        except Exception as e:
            logger.error(f"Error deleting webhook: {e}")
            
    async def get_webhook_info(self):
        """Get current webhook info"""
        try:
            return await self.app.bot.get_webhook_info()
        except Exception as e:
            logger.error(f"Error getting webhook info: {e}")
            return None
            
    async def start_polling(self):
        """Fallback ke polling mode"""
        logger.info("📡 Starting in polling mode...")
        
        await self.app.initialize()
        await self.app.start()
        
        # Start polling
        await self.app.updater.start_polling(
            allowed_updates=['message', 'callback_query'],
            drop_pending_updates=True,
            poll_interval=1.0,
            timeout=30
        )
        
        self.webhook_mode = False
        logger.info("✅ Polling started")
        
    async def run_webhook_server(self, host: str = "0.0.0.0", port: Optional[int] = None):
        """
        Run FastAPI server untuk webhook
        
        Args:
            host: Host to bind
            port: Port to bind (default: settings.webhook.port)
        """
        if port is None:
            port = settings.webhook.port
            
        logger.info(f"🌐 Starting webhook server on {host}:{port}")
        
        config = uvicorn.Config(
            self.fastapi_app,
            host=host,
            port=port,
            log_level="info",
            reload=False
        )
        server = uvicorn.Server(config)
        
        try:
            await server.serve()
        except KeyboardInterrupt:
            logger.info("Webhook server stopped by user")
        except Exception as e:
            logger.error(f"Webhook server error: {e}")
            raise
            

async def setup_webhook_with_fallback(app: Application) -> WebhookManager:
    """
    Setup webhook dengan fallback ke polling
    
    Returns:
        WebhookManager instance
    """
    manager = WebhookManager(app)
    
    # Coba setup webhook
    webhook_success = await manager.setup_webhook(retry=True)
    
    if webhook_success:
        logger.info("🚀 Running in WEBHOOK mode")
        # Jalankan webhook server
        await manager.run_webhook_server()
    else:
        logger.warning("⚠️ Falling back to POLLING mode")
        # Fallback ke polling
        await manager.start_polling()
        
        # Keep running
        while True:
            await asyncio.sleep(1)
            
    return manager


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

async def check_webhook_status(app: Application) -> dict:
    """Check current webhook status"""
    try:
        info = await app.bot.get_webhook_info()
        return {
            "url": info.url,
            "pending_updates": info.pending_update_count,
            "last_error": info.last_error_message,
            "last_error_date": info.last_error_date,
            "max_connections": info.max_connections,
            "allowed_updates": info.allowed_updates
        }
    except Exception as e:
        return {"error": str(e)}


async def reset_webhook(app: Application, url: Optional[str] = None):
    """Reset webhook (delete then set new)"""
    try:
        # Delete existing
        await app.bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Existing webhook deleted")
        
        # Set new if url provided
        if url:
            await app.bot.set_webhook(url=url)
            logger.info(f"✅ New webhook set: {url}")
            
    except Exception as e:
        logger.error(f"Error resetting webhook: {e}")

# =============================================================================
# SYNC WRAPPER FOR MAIN.PY
# =============================================================================

async def check_webhook_status(app: Application) -> dict:
    """Check current webhook status"""
    try:
        info = await app.bot.get_webhook_info()
        return {
            "url": info.url,
            "pending_updates": info.pending_update_count,
            "last_error": info.last_error_message,
            "last_error_date": info.last_error_date,
            "max_connections": info.max_connections,
            "allowed_updates": info.allowed_updates
        }
    except Exception as e:
        return {"error": str(e)}


async def reset_webhook(app: Application, url: Optional[str] = None):
    """Reset webhook"""
    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Existing webhook deleted")
        
        if url:
            await app.bot.set_webhook(url=url)
            logger.info(f"✅ New webhook set: {url}")
    except Exception as e:
        logger.error(f"Error resetting webhook: {e}")     

__all__ = [
    'WebhookManager',
    'setup_webhook_with_fallback',
    'check_webhook_status',
    'reset_webhook',
    'setup_webhook_sync',
]
