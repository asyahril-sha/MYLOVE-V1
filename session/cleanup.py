#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - SESSION CLEANUP
=============================================================================
- Auto-delete sessions setelah 30 hari
- Background job untuk cleanup
- Bisa manual cleanup dengan command
"""

import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

from .storage import SessionStorage
from .unique_id import id_generator

logger = logging.getLogger(__name__)


class SessionCleanup:
    """
    Membersihkan session lama secara otomatis
    Session yang lebih dari 30 hari akan dihapus
    """
    
    def __init__(self, storage: SessionStorage, retention_days: int = 30):
        self.storage = storage
        self.retention_days = retention_days
        self.cleanup_running = False
        self.cleanup_task = None
        
        # Statistics
        self.total_cleaned = 0
        self.last_cleanup = None
        self.cleaned_today = 0
        
        logger.info(f"✅ SessionCleanup initialized (retention: {retention_days} days)")
        
    # =========================================================================
    # CLEANUP LOGIC
    # =========================================================================
    
    async def cleanup_old_sessions(self, dry_run: bool = False) -> Dict:
        """
        Hapus session yang lebih dari retention_days
        
        Args:
            dry_run: Jika True, hanya hitung tanpa menghapus
            
        Returns:
            Dict dengan hasil cleanup
        """
        cutoff_time = time.time() - (self.retention_days * 86400)
        
        # Get old sessions
        old_sessions = await self.storage.get_old_sessions(self.retention_days)
        
        if not old_sessions:
            return {
                "deleted": 0,
                "dry_run": dry_run,
                "message": "Tidak ada session lama"
            }
            
        deleted_count = 0
        deleted_ids = []
        
        for session_id in old_sessions:
            # Double-check age
            age_days = id_generator.get_session_age_days(session_id)
            if age_days and age_days >= self.retention_days:
                if not dry_run:
                    await self.storage.delete_session(session_id)
                    self.total_cleaned += 1
                    self.cleaned_today += 1
                    
                deleted_count += 1
                deleted_ids.append(session_id)
                logger.info(f"🧹 Cleaned old session: {session_id} (age: {age_days} days)")
                
        self.last_cleanup = time.time()
        
        return {
            "deleted": deleted_count,
            "deleted_ids": deleted_ids[:10],  # Show first 10 only
            "dry_run": dry_run,
            "retention_days": self.retention_days,
            "cutoff_date": datetime.fromtimestamp(cutoff_time).strftime("%Y-%m-%d")
        }
        
    async def cleanup_user_sessions(self, user_id: int, days: Optional[int] = None) -> Dict:
        """
        Hapus sessions user tertentu yang lebih dari X hari
        
        Args:
            user_id: ID user
            days: Umur session dalam hari (default: retention_days)
            
        Returns:
            Dict hasil cleanup
        """
        if days is None:
            days = self.retention_days
            
        cutoff_time = time.time() - (days * 86400)
        
        # Get user sessions
        sessions = await self.storage.get_user_sessions(user_id, limit=100)
        
        deleted = []
        for session in sessions:
            if session.get('last_message_time', 0) < cutoff_time:
                await self.storage.delete_session(session['id'])
                deleted.append(session['id'])
                
        return {
            "user_id": user_id,
            "deleted": len(deleted),
            "deleted_ids": deleted[:10],
            "days": days
        }
        
    # =========================================================================
    # BACKGROUND CLEANUP
    # =========================================================================
    
    async def start_auto_cleanup(self, interval_hours: int = 24):
        """
        Start background cleanup job
        
        Args:
            interval_hours: Interval cleanup dalam jam
        """
        if self.cleanup_running:
            logger.warning("Cleanup already running")
            return
            
        self.cleanup_running = True
        self.cleanup_task = asyncio.create_task(
            self._cleanup_loop(interval_hours)
        )
        
        logger.info(f"🔄 Auto cleanup started (interval: {interval_hours} hours)")
        
    async def stop_auto_cleanup(self):
        """Stop background cleanup"""
        self.cleanup_running = False
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
            self.cleanup_task = None
            
        logger.info("🔄 Auto cleanup stopped")
        
    async def _cleanup_loop(self, interval_hours: int):
        """Background loop untuk cleanup"""
        while self.cleanup_running:
            try:
                # Reset daily counter
                self.cleaned_today = 0
                
                # Run cleanup
                result = await self.cleanup_old_sessions()
                
                if result['deleted'] > 0:
                    logger.info(f"🧹 Cleaned {result['deleted']} old sessions")
                    
                # Sleep until next cleanup
                await asyncio.sleep(interval_hours * 3600)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(3600)  # Retry after 1 hour
                
    # =========================================================================
    # MANUAL CLEANUP COMMAND
    # =========================================================================
    
    async def handle_cleanup_command(self, args: List[str]) -> str:
        """
        Handle manual cleanup command
        
        Args:
            args: Command arguments
            
        Returns:
            Response string
        """
        if not args:
            # Show status
            return self.get_cleanup_status()
            
        cmd = args[0].lower()
        
        if cmd == "now":
            # Run cleanup now
            result = await self.cleanup_old_sessions()
            return (
                f"🧹 **Cleanup Result**\n"
                f"Deleted: {result['deleted']} sessions\n"
                f"Retention: {result['retention_days']} days\n"
                f"Cutoff: {result['cutoff_date']}"
            )
            
        elif cmd == "dry":
            # Dry run
            result = await self.cleanup_old_sessions(dry_run=True)
            return (
                f"🔍 **Dry Run**\n"
                f"Would delete: {result['deleted']} sessions\n"
                f"Retention: {result['retention_days']} days\n"
                f"Cutoff: {result['cutoff_date']}\n\n"
                f"Gunakan `/cleanup now` untuk benar-benar menghapus"
            )
            
        elif cmd == "stats":
            # Show stats
            return self.get_cleanup_stats()
            
        else:
            return (
                "❌ Command tidak dikenal\n\n"
                "**Usage:**\n"
                "/cleanup - Lihat status\n"
                "/cleanup now - Jalankan cleanup sekarang\n"
                "/cleanup dry - Dry run (lihat yang akan dihapus)\n"
                "/cleanup stats - Lihat statistik cleanup"
            )
            
    # =========================================================================
    # STATUS & STATISTICS
    # =========================================================================
    
    def get_cleanup_status(self) -> str:
        """Get cleanup system status"""
        status = "🟢 Running" if self.cleanup_running else "🔴 Stopped"
        
        lines = [
            "🧹 **Session Cleanup Status**",
            f"Status: {status}",
            f"Retention: {self.retention_days} hari",
            f"Total cleaned: {self.total_cleaned} sessions",
            f"Cleaned today: {self.cleaned_today} sessions",
        ]
        
        if self.last_cleanup:
            last = datetime.fromtimestamp(self.last_cleanup).strftime("%Y-%m-%d %H:%M")
            lines.append(f"Last cleanup: {last}")
            
        lines.append("")
        lines.append("**Commands:**")
        lines.append("• `/cleanup now` - Jalankan sekarang")
        lines.append("• `/cleanup dry` - Dry run")
        lines.append("• `/cleanup stats` - Statistik detail")
        
        return "\n".join(lines)
        
    def get_cleanup_stats(self) -> str:
        """Get detailed cleanup statistics"""
        return (
            f"📊 **Cleanup Statistics**\n\n"
            f"Total sessions cleaned: {self.total_cleaned}\n"
            f"Cleaned today: {self.cleaned_today}\n"
            f"Retention period: {self.retention_days} days\n"
            f"Auto cleanup: {'ON' if self.cleanup_running else 'OFF'}\n"
            f"Last run: {datetime.fromtimestamp(self.last_cleanup).strftime('%Y-%m-%d %H:%M') if self.last_cleanup else 'Never'}"
        )
        
    # =========================================================================
    # UTILITY
    # =========================================================================
    
    async def estimate_size(self) -> Dict:
        """
        Estimasi ukuran session storage
        
        Returns:
            Dict dengan estimasi
        """
        # Hitung jumlah file JSON
        json_files = list(Path(self.storage.session_dir).glob("*.json"))
        
        # Hitung total size
        total_size = sum(f.stat().st_size for f in json_files)
        
        # Dapatkan total sessions dari DB
        stats = await self.storage.get_stats()
        
        return {
            "total_sessions": stats.get('total_sessions', 0),
            "json_files": len(json_files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "avg_size_kb": round(total_size / len(json_files) / 1024, 1) if json_files else 0,
            "retention_days": self.retention_days,
            "estimated_cleanup": len(await self.storage.get_old_sessions(self.retention_days))
        }
        
    async def cleanup_stats_string(self) -> str:
        """Get cleanup stats in string format"""
        stats = await self.estimate_size()
        
        return (
            f"📦 **Storage Usage**\n"
            f"Total sessions: {stats['total_sessions']}\n"
            f"JSON files: {stats['json_files']}\n"
            f"Total size: {stats['total_size_mb']} MB\n"
            f"Avg per session: {stats['avg_size_kb']} KB\n"
            f"Estimated to clean: {stats['estimated_cleanup']} sessions"
        )


__all__ = ['SessionCleanup']
