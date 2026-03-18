#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - BACKUP RECOVERY
=============================================================================
- Restore dari backup dengan /recover
- List available backups
- Dry run mode
- Integrity check sebelum restore
"""

import os
import sys
import json
import time
import zipfile
import shutil
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from config import settings
from ..database.connection import get_db
from ..database.models import Backup, BackupStatus
from ..utils.exceptions import BackupNotFoundError, BackupCorruptedError
from .automated import get_backup_manager
from .verify import BackupVerifier

logger = logging.getLogger(__name__)


class RecoveryManager:
    """
    Manajer untuk recovery dari backup
    Mendukung restore dengan /recover command
    """
    
    def __init__(self, backup_manager):
        self.backup_manager = backup_manager
        self.backup_dir = backup_manager.backup_dir
        self.verifier = BackupVerifier()
        
    # =========================================================================
    # LIST BACKUPS
    # =========================================================================
    
    async def list_backups(self, limit: int = 10) -> List[Dict]:
        """
        List available backups
        
        Args:
            limit: Max number of backups to list
            
        Returns:
            List of backup info
        """
        db = await get_db()
        
        backups = await db.fetch_all(
            """
            SELECT * FROM backups 
            WHERE status = 'completed' 
            ORDER BY created_at DESC 
            LIMIT ?
            """,
            (limit,)
        )
        
        result = []
        for i, backup in enumerate(backups, 1):
            result.append({
                "index": i,
                "filename": backup['filename'],
                "date": datetime.fromtimestamp(backup['created_at']).strftime("%Y-%m-%d %H:%M:%S"),
                "size_mb": round(backup['size'] / (1024 * 1024), 2) if backup['size'] else 0,
                "type": backup['type']
            })
            
        return result
        
    async def find_backup(self, identifier: str) -> Optional[Path]:
        """
        Find backup file by identifier (index or filename)
        
        Args:
            identifier: Index number (1,2,3) or filename
            
        Returns:
            Path to backup file or None
        """
        # Check if identifier is index
        try:
            idx = int(identifier)
            backups = await self.list_backups(limit=50)
            
            if 1 <= idx <= len(backups):
                backup_info = backups[idx - 1]
                backup_path = self.backup_dir / backup_info['filename']
                if backup_path.exists():
                    return backup_path
                    
        except ValueError:
            # Not a number, treat as filename
            backup_path = self.backup_dir / identifier
            if backup_path.exists():
                return backup_path
                
        return None
        
    # =========================================================================
    # RESTORE OPERATIONS
    # =========================================================================
    
    async def restore_backup(self, backup_path: Path, dry_run: bool = False) -> Dict:
        """
        Restore from backup
        
        Args:
            backup_path: Path to backup ZIP file
            dry_run: If True, only verify without restoring
            
        Returns:
            Dict with restore result
        """
        if not backup_path.exists():
            raise BackupNotFoundError(str(backup_path))
            
        logger.info(f"🔄 Restoring from backup: {backup_path.name}")
        
        # Verify backup first
        verify_result = await self.verifier.verify_backup(backup_path)
        
        if not verify_result['valid']:
            raise BackupCorruptedError(str(backup_path))
            
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "filename": backup_path.name,
                "files": verify_result['files'],
                "size_mb": verify_result['size_mb']
            }
            
        # Create temp directory for extraction
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = self.backup_dir / f"restore_temp_{timestamp}"
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # Extract backup
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(temp_dir)
                
            # Stop bot services
            await self._stop_services()
            
            # Restore files
            await self._restore_files(temp_dir)
            
            # Restart bot services
            await self._start_services()
            
            # Log restore
            logger.info(f"✅ Restore completed: {backup_path.name}")
            
            return {
                "success": True,
                "filename": backup_path.name,
                "files_restored": len(verify_result['files']),
                "size_mb": verify_result['size_mb'],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Restore failed: {e}")
            raise
            
        finally:
            # Cleanup temp
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                
    async def _stop_services(self):
        """Stop bot services before restore"""
        logger.info("⏸️ Stopping bot services...")
        # In production, this would signal the main bot to pause
        await asyncio.sleep(1)
        
    async def _start_services(self):
        """Restart bot services after restore"""
        logger.info("▶️ Starting bot services...")
        # In production, this would signal the main bot to resume
        await asyncio.sleep(1)
        
    async def _restore_files(self, temp_dir: Path):
        """Restore files from extracted backup"""
        
        # Restore database
        db_backup = temp_dir / "database.sqlite"
        if db_backup.exists():
            db_path = settings.database.path
            db_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(db_backup, db_path)
            logger.info("✅ Database restored")
            
        # Restore sessions
        session_backup = temp_dir / "sessions"
        if session_backup.exists():
            session_dir = settings.session.session_dir
            if session_dir.exists():
                shutil.rmtree(session_dir)
            shutil.copytree(session_backup, session_dir)
            logger.info("✅ Sessions restored")
            
        # Restore vector DB
        vector_backup = temp_dir / "vector_db"
        if vector_backup.exists():
            vector_dir = settings.memory.vector_db_dir
            if vector_dir.exists():
                shutil.rmtree(vector_dir)
            shutil.copytree(vector_backup, vector_dir)
            logger.info("✅ Vector DB restored")
            
        # Restore memory
        memory_backup = temp_dir / "memory"
        if memory_backup.exists():
            memory_dir = settings.memory.memory_dir
            if memory_dir.exists():
                shutil.rmtree(memory_dir)
            shutil.copytree(memory_backup, memory_dir)
            logger.info("✅ Memory restored")
            
    # =========================================================================
    # COMMAND HANDLERS
    # =========================================================================
    
    async def handle_recover_command(self, args: List[str]) -> str:
        """
        Handle /recover command
        
        Args:
            args: Command arguments
            
        Returns:
            Response string
        """
        if not args:
            return await self._format_backup_list()
            
        cmd = args[0].lower()
        
        if cmd == "list":
            return await self._format_backup_list()
            
        elif cmd == "latest":
            backups = await self.list_backups(limit=1)
            if not backups:
                return "❌ Tidak ada backup tersedia"
                
            backup_path = self.backup_dir / backups[0]['filename']
            return await self._confirm_restore(backup_path)
            
        elif cmd == "verify":
            if len(args) < 2:
                return "❌ Gunakan: /recover verify [index/filename]"
                
            backup_path = await self.find_backup(args[1])
            if not backup_path:
                return "❌ Backup tidak ditemukan"
                
            result = await self.verifier.verify_backup(backup_path)
            return self.verifier.format_verify_result(result)
            
        elif cmd == "dry":
            if len(args) < 2:
                return "❌ Gunakan: /recover dry [index/filename]"
                
            backup_path = await self.find_backup(args[1])
            if not backup_path:
                return "❌ Backup tidak ditemukan"
                
            try:
                result = await self.restore_backup(backup_path, dry_run=True)
                return (
                    f"🔍 **DRY RUN - Akan direstore:**\n\n"
                    f"File: {result['filename']}\n"
                    f"Size: {result['size_mb']} MB\n"
                    f"Files: {result['files']}\n\n"
                    f"Gunakan `/recover {args[1]}` untuk benar-benar restore"
                )
            except Exception as e:
                return f"❌ Error: {e}"
                
        else:
            # Try to restore by index/filename
            backup_path = await self.find_backup(cmd)
            if not backup_path:
                return "❌ Backup tidak ditemukan. Gunakan /recover list untuk melihat daftar."
                
            return await self._confirm_restore(backup_path)
            
    async def _format_backup_list(self) -> str:
        """Format backup list for display"""
        backups = await self.list_backups(limit=10)
        
        if not backups:
            return "📂 **Tidak ada backup tersedia**"
            
        lines = ["📂 **DAFTAR BACKUP**"]
        lines.append("_(pilih dengan /recover [nomor])_")
        lines.append("")
        
        for b in backups:
            lines.append(
                f"{b['index']}. **{b['filename']}**\n"
                f"   {b['date']} | {b['size_mb']} MB | {b['type']}"
            )
            
        lines.append("")
        lines.append("**Command:**")
        lines.append("• `/recover 1` - Restore backup nomor 1")
        lines.append("• `/recover latest` - Restore backup terbaru")
        lines.append("• `/recover verify 1` - Verifikasi backup")
        lines.append("• `/recover dry 1` - Dry run")
        
        return "\n".join(lines)
        
    async def _confirm_restore(self, backup_path: Path) -> str:
        """Format confirmation message for restore"""
        return (
            f"⚠️ **Yakin mau restore dari backup ini?**\n\n"
            f"File: `{backup_path.name}`\n\n"
            f"**Ini akan mengembalikan database ke kondisi backup.**\n"
            f"Data setelah backup akan hilang.\n\n"
            f"Ketik `/recover confirm {backup_path.name}` untuk melanjutkan, "
            f"atau `/recover cancel` untuk membatalkan."
        )
        
    async def confirm_restore(self, filename: str) -> str:
        """Confirm and execute restore"""
        backup_path = self.backup_dir / filename
        
        if not backup_path.exists():
            return "❌ Backup tidak ditemukan"
            
        try:
            result = await self.restore_backup(backup_path)
            return (
                f"✅ **Restore berhasil!**\n\n"
                f"File: {result['filename']}\n"
                f"Files restored: {result['files_restored']}\n"
                f"Size: {result['size_mb']} MB\n"
                f"Timestamp: {result['timestamp']}\n\n"
                f"Bot akan restart..."
            )
        except Exception as e:
            return f"❌ Restore gagal: {e}"


__all__ = ['RecoveryManager']
