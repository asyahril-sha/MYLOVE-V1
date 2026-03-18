#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - BACKUP VERIFICATION
=============================================================================
- Verifikasi integritas file backup
- Check checksum
- Test extract
- Report corrupted files
"""

import os
import zipfile
import hashlib
import json
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class BackupVerifier:
    """
    Verifikasi integritas backup files
    Memastikan backup tidak corrupt sebelum direstore
    """
    
    def __init__(self):
        self.checksum_algo = hashlib.sha256
        
    # =========================================================================
    # VERIFICATION METHODS
    # =========================================================================
    
    async def verify_backup(self, backup_path: Path) -> Dict[str, Any]:
        """
        Verify backup file integrity
        
        Args:
            backup_path: Path to backup ZIP file
            
        Returns:
            Dict with verification result
        """
        if not backup_path.exists():
            return {
                "valid": False,
                "error": "File not found",
                "filename": backup_path.name
            }
            
        result = {
            "filename": backup_path.name,
            "size_bytes": backup_path.stat().st_size,
            "size_mb": round(backup_path.stat().st_size / (1024 * 1024), 2),
            "checks": {}
        }
        
        # 1. Check ZIP integrity
        zip_check = await self._check_zip_integrity(backup_path)
        result["checks"]["zip_integrity"] = zip_check
        if not zip_check["valid"]:
            result["valid"] = False
            result["error"] = "ZIP file corrupted"
            return result
            
        # 2. Check metadata
        metadata_check = await self._check_metadata(backup_path)
        result["checks"]["metadata"] = metadata_check
        
        # 3. Check file structure
        structure_check = await self._check_file_structure(backup_path)
        result["checks"]["structure"] = structure_check
        
        # 4. Calculate checksum
        result["checksum"] = await self._calculate_checksum(backup_path)
        
        # Overall validity
        result["valid"] = (
            zip_check["valid"] and
            metadata_check["valid"] and
            structure_check["valid"]
        )
        
        if result["valid"]:
            result["files"] = structure_check["files"]
            result["metadata"] = metadata_check["metadata"]
            
        return result
        
    async def _check_zip_integrity(self, zip_path: Path) -> Dict:
        """Check ZIP file integrity"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                # Test ZIP integrity
                bad_file = zipf.testzip()
                if bad_file:
                    return {
                        "valid": False,
                        "error": f"Corrupted file in ZIP: {bad_file}"
                    }
                    
                # Get file list
                files = zipf.namelist()
                
                return {
                    "valid": True,
                    "file_count": len(files),
                    "files": files
                }
                
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
            
    async def _check_metadata(self, zip_path: Path) -> Dict:
        """Check metadata.json in backup"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                if 'metadata.json' not in zipf.namelist():
                    return {
                        "valid": False,
                        "error": "metadata.json not found"
                    }
                    
                # Read and parse metadata
                with zipf.open('metadata.json') as f:
                    metadata = json.loads(f.read().decode('utf-8'))
                    
                # Validate required fields
                required = ['created_at', 'version', 'files']
                missing = [f for f in required if f not in metadata]
                
                if missing:
                    return {
                        "valid": False,
                        "error": f"Missing fields: {missing}"
                    }
                    
                return {
                    "valid": True,
                    "metadata": metadata
                }
                
        except json.JSONDecodeError:
            return {
                "valid": False,
                "error": "metadata.json is corrupted"
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
            
    async def _check_file_structure(self, zip_path: Path) -> Dict:
        """Check backup file structure"""
        required_files = [
            'database.sqlite',
            'metadata.json'
        ]
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                files = zipf.namelist()
                
                # Check required files
                missing = []
                for req in required_files:
                    if req not in files:
                        missing.append(req)
                        
                if missing:
                    return {
                        "valid": False,
                        "error": f"Missing required files: {missing}"
                    }
                    
                # Optional directories
                optional_dirs = ['sessions/', 'vector_db/', 'memory/']
                present_dirs = []
                
                for opt_dir in optional_dirs:
                    if any(f.startswith(opt_dir) for f in files):
                        present_dirs.append(opt_dir.rstrip('/'))
                        
                return {
                    "valid": True,
                    "files": len(files),
                    "directories": present_dirs
                }
                
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
            
    async def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate file checksum"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
        
    # =========================================================================
    # TEST EXTRACT
    # =========================================================================
    
    async def test_extract(self, backup_path: Path) -> Dict:
        """
        Test extract backup to temporary directory
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            Dict with test results
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            try:
                # Extract
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    zipf.extractall(temp_path)
                    
                # Check extracted files
                extracted_files = list(temp_path.rglob('*'))
                file_count = len([f for f in extracted_files if f.is_file()])
                
                # Try to open database
                db_file = temp_path / 'database.sqlite'
                db_valid = db_file.exists() and db_file.stat().st_size > 0
                
                return {
                    "success": True,
                    "extracted_files": file_count,
                    "database_valid": db_valid,
                    "temp_dir": str(temp_path)
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }
                
    # =========================================================================
    # BATCH VERIFICATION
    # =========================================================================
    
    async def verify_all_backups(self, backup_dir: Path) -> List[Dict]:
        """Verify all backup files in directory"""
        results = []
        
        for backup_file in sorted(backup_dir.glob("mylove_backup_*.zip")):
            logger.info(f"Verifying {backup_file.name}...")
            result = await self.verify_backup(backup_file)
            results.append(result)
            
        return results
        
    async def find_corrupted_backups(self, backup_dir: Path) -> List[Path]:
        """Find corrupted backup files"""
        corrupted = []
        
        for backup_file in backup_dir.glob("mylove_backup_*.zip"):
            result = await self.verify_backup(backup_file)
            if not result["valid"]:
                corrupted.append(backup_file)
                
        return corrupted
        
    # =========================================================================
    # FORMATTING
    # =========================================================================
    
    def format_verify_result(self, result: Dict) -> str:
        """Format verification result for display"""
        if not result["valid"]:
            return (
                f"❌ **Backup corrupted:** {result['filename']}\n"
                f"Error: {result.get('error', 'Unknown')}"
            )
            
        lines = [
            f"✅ **Backup valid:** {result['filename']}",
            f"Size: {result['size_mb']} MB",
            f"Checksum: {result['checksum'][:16]}...",
            ""
        ]
        
        if "metadata" in result:
            meta = result["metadata"]
            created = datetime.fromtimestamp(meta['created_at']).strftime("%Y-%m-%d %H:%M:%S")
            lines.append(f"Created: {created}")
            lines.append(f"Version: {meta['version']}")
            
        if "files" in result:
            lines.append(f"Total files: {result['files']}")
            
        if "directories" in result.get("checks", {}).get("structure", {}):
            dirs = result["checks"]["structure"]["directories"]
            if dirs:
                lines.append(f"Directories: {', '.join(dirs)}")
                
        return "\n".join(lines)


__all__ = ['BackupVerifier']
