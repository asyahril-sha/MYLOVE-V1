#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
ADVANCED LOGGING SYSTEM
=============================================================================
Menggunakan loguru untuk logging dengan berbagai output
"""

import sys
from pathlib import Path
from loguru import logger as loguru_logger

# Coba import settings
try:
    from config import settings
except ImportError:
    settings = None

# Setup logger instance yang akan diekspor
logger = loguru_logger


def setup_logging(module_name: str = "MYLOVE-V1"):
    """
    Setup logging dengan loguru
    - Console logging dengan warna
    - File logging dengan rotation
    - JSON logging untuk production
    - Error tracking
    """
    
    # Tentukan direktori log dari settings
    if settings and hasattr(settings, 'logging') and hasattr(settings.logging, 'log_dir'):
        log_dir = Path(settings.logging.log_dir)
    else:
        # Fallback ke direktori logs lokal
        log_dir = Path("data/logs")
    
    # Pastikan direktori log ada
    log_dir.mkdir(exist_ok=True, parents=True)
    
    # Remove default handler
    logger.remove()
    
    # Console handler dengan warna (sesuai level dari settings)
    console_level = settings.logging.level if settings and hasattr(settings, 'logging') else "INFO"
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=console_level,
        colorize=True,
        enqueue=True,
        backtrace=True,
        diagnose=True
    )
    
    # File handler dengan rotation (semua level)
    log_file = log_dir / f"{module_name}.log"
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="50 MB",
        retention="30 days",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=True
    )
    
    # Error file handler (khusus error)
    error_file = log_dir / f"{module_name}_error.log"
    logger.add(
        error_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="50 MB",
        retention="90 days",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=True
    )
    
    # JSON handler untuk monitoring (opsional)
    json_log = log_dir / f"{module_name}_json.log"
    logger.add(
        json_log,
        format="{time} | {level} | {name} | {message}",
        level="INFO",
        rotation="100 MB",
        serialize=True,
        enqueue=True
    )
    
    logger.info(f"📝 Logging initialized")
    logger.info(f"   • Log file: {log_file}")
    logger.info(f"   • Error file: {error_file}")
    logger.info(f"   • JSON log: {json_log}")
    logger.info(f"   • Log level: {console_level}")
    
    return logger


# Export logger dan setup_logging
__all__ = ['setup_logging', 'logger']
