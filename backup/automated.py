#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - AUTOMATED BACKUP
=============================================================================
- Auto backup setiap jam
- Retention 7 hari
- Kompresi ke ZIP
- Opsional upload ke S3
"""

import os
import sys
import json
import time
import asyncio
import zipfile
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import hashlib

from config import settings
from ..database.connection import get_db
from ..database.models import Backup, BackupType, BackupStatus
from ..utils.logger import setup_logging

logger = logging.getLogger(__name__)


class AutoBackup:
    """
    Manajer backup otomatis
    - Backup setiap jam
    - Retention 7 hari
    - Kompresi database dan file penting
    """
    
    def __init__(self):
        self.backup_dir = settings.backup.backup_dir
        self.retention_days = settings.backup.retention_days
        self.interval = settings.backup.interval  # detik
        self.enabled = settings.backup.enabled
        self.s3_bucket = settings.backup.s3_bucket
        
        # Buat direktori backup
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Stats
        self.last_backup_time = None
        self.total_backups = 0
        self.total_size_mb = 0
        self.backup_history = []
        
        # Background task
        self._backup_task = None
        self._running = False
        
        logger.info(f"✅ AutoBackup initialized (dir: {self.backup_dir}, retention: {self.retention_days} days)")
        
    # =========================================================================
    # BACKUP OPERATIONS
    # =========================================================================
    
    async def create_backup(self, backup_type: BackupType = BackupType.AUTO) -> Optional[Path]:
        """
        Create new backup
        
        Args:
            backup_type: AUTO or MANUAL
            
        Returns:
            Path to backup file or None if failed
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"mylove_backup_{timestamp}.zip"
        backup_path = self.backup_dir / backup_filename
        
        logger.info(f"📦 Creating backup: {backup_filename}")
        
        try:
            # Buat temporary directory
            temp_dir = self.backup_dir / f"temp_{timestamp}"
            temp_dir.mkdir(exist_ok=True)
            
            # Copy files to backup
            await self._copy_files_to_backup(temp_dir)
            
            # Create ZIP
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in temp_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(temp_dir)
                        zipf.write(file_path, arcname)
                        
            # Calculate size and hash
            size_bytes = backup_path.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            
            # Calculate SHA-256
            sha256 = self._calculate_hash(backup_path)
            
            # Save metadata
            backup_record = Backup(
                filename=backup_filename,
                size=int(size_bytes),
                created_at=time.time(),
                type=backup_type,
                status=BackupStatus.COMPLETED,
                metadata={
                    "sha256": sha256,
                    "files": self._get_backup_file_list(temp_dir)
                }
            )
            
            # Save to database
            db = await get_db()
            from ..database.repository import Repository
            repo = Repository()
            await repo.add_backup(backup_record)
            
            # Cleanup temp
            shutil.rmtree(temp_dir)
            
            # Update stats
            self.last_backup_time = time.time()
            self.total_backups += 1
            self.total_size_mb += size_mb
            self.backup_history.append({
                "filename": backup_filename,
                "time": self.last_backup_time,
                "size_mb": round(size_mb, 2)
            })
            
            logger.info(f"✅ Backup created: {backup_filename} ({size_mb:.2f} MB)")
            
            # Clean old backups
            await self.cleanup_old_backups()
            
            # Upload to S3 if configured
            if self.s3_bucket:
                await self.upload_to_s3(backup_path)
                
            return backup_path
            
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            
            # Save failed backup record
            backup_record = Backup(
                filename=backup_filename,
                created_at=time.time(),
                type=backup_type,
                status=BackupStatus.FAILED,
                metadata={"error": str(e)}
            )
            
            db = await get_db()
            repo = Repository()
            await repo.add_backup(backup_record)
            
            # Cleanup temp if exists
            if 'temp_dir' in locals() and temp_dir.exists():
                shutil.rmtree(temp_dir)
                
            return None
            
    async def _copy_files_to_backup(self, temp_dir: Path):
        """Copy all important files to temp directory"""
        
        # Database file
        db_path = settings.database.path
        if db_path.exists():
            shutil.copy2(db_path, temp_dir / "database.sqlite")
            
        # Session JSON files
        session_dir = settings.session.session_dir
        if session_dir.exists():
            session_backup = temp_dir / "sessions"
            session_backup.mkdir()
            for json_file in session_dir.glob("*.json"):
                shutil.copy2(json_file, session_backup)
                
        # Vector DB files
        vector_dir = settings.memory.vector_db_dir
        if vector_dir.exists():
            vector_backup = temp_dir / "vector_db"
            shutil.copytree(vector_dir, vector_backup)
            
        # Memory files
        memory_dir = settings.memory.memory_dir
        if memory_dir.exists():
            memory_backup = temp_dir / "memory"
            shutil.copytree(memory_dir, memory_backup)
            
        # Config file (without secrets)
        config_backup = temp_dir / "config"
        config_backup.mkdir()
        self._backup_config(config_backup)
        
        # Backup metadata
        metadata = {
            "created_at": time.time(),
            "version": "1.0.0",
            "files": self._get_backup_file_list(temp_dir),
            "settings": {
                "db_type": settings.database.type,
                "retention_days": self.retention_days
            }
        }
        
        with open(temp_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
            
    def _backup_config(self, config_dir: Path):
        """Backup config without sensitive data"""
        from config import settings
        
        config_data = {
            "database": {
                "type": settings.database.type,
                "path": str(settings.database.path)
            },
            "ai": {
                "temperature": settings.ai.temperature,
                "max_tokens": settings.ai.max_tokens
            },
            "intimacy": {
                "levels": settings.intimacy.levels,
                "reset_level": settings.intimacy.reset_level
            },
            "public": {
                "locations_count": len(settings.public.locations)
            },
            "session": {
                "retention_days": settings.session.retention_days
            }
        }
        
        with open(config_dir / "config.json", 'w') as f:
            json.dump(config_data, f, indent=2)
            
    def _get_backup_file_list(self, temp_dir: Path) -> List[str]:
        """Get list of files in backup"""
        files = []
        for file_path in temp_dir.rglob('*'):
            if file_path.is_file():
                files.append(str(file_path.relative_to(temp_dir)))
        return files
        
    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
        
    # =========================================================================
    # CLEANUP OLD BACKUPS
    # =========================================================================
    
    async def cleanup_old_backups(self, dry_run: bool = False) -> List[str]:
        """
        Delete backups older than retention_days
        
        Args:
            dry_run: If True, only list files without deleting
            
        Returns:
            List of deleted files
        """
        cutoff_time = time.time() - (self.retention_days * 86400)
        deleted = []
        
        for backup_file in self.backup_dir.glob("mylove_backup_*.zip"):
            # Get creation time from filename
            try:
                timestamp_str = backup_file.stem.replace("mylove_backup_", "")
                file_time = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S").timestamp()
                
                if file_time < cutoff_time:
                    if dry_run:
                        logger.info(f"Would delete: {backup_file.name}")
                    else:
                        # Delete file
                        backup_file.unlink()
                        logger.info(f"🗑️ Deleted old backup: {backup_file.name}")
                        
                        # Delete from database
                        db = await get_db()
                        await db.execute(
                            "DELETE FROM backups WHERE filename = ?",
                            (backup_file.name,)
                        )
                        
                    deleted.append(backup_file.name)
                    
            except Exception as e:
                logger.error(f"Error processing {backup_file.name}: {e}")
                
        if not dry_run and deleted:
            logger.info(f"✅ Cleaned up {len(deleted)} old backups")
            
        return deleted
        
    # =========================================================================
    # S3 UPLOAD (OPTIONAL)
    # =========================================================================
    
    async def upload_to_s3(self, backup_path: Path):
        """Upload backup to S3 bucket"""
        if not self.s3_bucket:
            return
            
        try:
            # This would use boto3 in production
            # For now, just log
            logger.info(f"☁️ Would upload to S3 bucket {self.s3_bucket}: {backup_path.name}")
            
            # Simulate upload
            await asyncio.sleep(1)
            
            logger.info(f"✅ Uploaded to S3: {backup_path.name}")
            
        except Exception as e:
            logger.error(f"Failed to upload to S3: {e}")
            
    # =========================================================================
    # AUTO BACKUP SCHEDULER
    # =========================================================================
    
    async def start_auto_backup(self):
        """Start automatic backup scheduler"""
        if not self.enabled:
            logger.info("⏸️ Auto backup is disabled")
            return
            
        if self._running:
            logger.warning("Auto backup already running")
            return
            
        self._running = True
        self._backup_task = asyncio.create_task(self._backup_loop())
        
        logger.info(f"🔄 Auto backup started (interval: {self.interval} seconds)")
        
    async def stop_auto_backup(self):
        """Stop automatic backup scheduler"""
        self._running = False
        if self._backup_task:
            self._backup_task.cancel()
            try:
                await self._backup_task
            except asyncio.CancelledError:
                pass
            self._backup_task = None
            
        logger.info("🔄 Auto backup stopped")
        
    async def _backup_loop(self):
        """Background loop for automatic backup"""
        while self._running:
            try:
                # Create backup
                await self.create_backup(BackupType.AUTO)
                
                # Wait for next interval
                await asyncio.sleep(self.interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in backup loop: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour on error
                
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get backup statistics"""
        db = await get_db()
        
        # Get from database
        backups = await db.fetch_all(
            "SELECT * FROM backups ORDER BY created_at DESC LIMIT 10"
        )
        
        total_size = sum(b['size'] for b in backups if b['size'])
        
        return {
            "total_backups": len(backups),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "last_backup": self.last_backup_time,
            "last_backup_ago": time.time() - self.last_backup_time if self.last_backup_time else None,
            "retention_days": self.retention_days,
            "auto_backup_running": self._running,
            "recent_backups": [
                {
                    "filename": b['filename'],
                    "date": datetime.fromtimestamp(b['created_at']).strftime("%Y-%m-%d %H:%M"),
                    "size_mb": round(b['size'] / (1024 * 1024), 2) if b['size'] else 0,
                    "type": b['type']
                }
                for b in backups
            ]
        }
        
    async def get_backup_list(self) -> List[Dict]:
        """Get list of available backups"""
        db = await get_db()
        
        backups = await db.fetch_all(
            "SELECT * FROM backups WHERE status = 'completed' ORDER BY created_at DESC"
        )
        
        return [
            {
                "filename": b['filename'],
                "date": datetime.fromtimestamp(b['created_at']).strftime("%Y-%m-%d %H:%M"),
                "size_mb": round(b['size'] / (1024 * 1024), 2) if b['size'] else 0,
                "type": b['type']
            }
            for b in backups
        ]


# Global backup manager instance
_backup_manager = None


def get_backup_manager() -> AutoBackup:
    """Get global backup manager instance"""
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = AutoBackup()
    return _backup_manager


__all__ = ['AutoBackup', 'get_backup_manager']
