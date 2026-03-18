#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - LOGGING SETUP
=============================================================================
- Konfigurasi logging untuk file dan console
- Log rotation
- Debug level untuk development
"""

import os
import sys
import logging
import logging.handlers
from pathlib import Path
from typing import Optional
from datetime import datetime

from config import settings


# Format logging
DEFAULT_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEBUG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
SIMPLE_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'


class ColoredFormatter(logging.Formatter):
    """Custom formatter dengan warna untuk console"""
    
    # ANSI color codes
    GREY = "\x1b[38;21m"
    BLUE = "\x1b[38;5;39m"
    YELLOW = "\x1b[38;5;226m"
    RED = "\x1b[38;5;196m"
    BOLD_RED = "\x1b[31;1m"
    GREEN = "\x1b[38;5;40m"
    CYAN = "\x1b[36m"
    RESET = "\x1b[0m"
    
    COLORS = {
        logging.DEBUG: GREY,
        logging.INFO: GREEN,
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: BOLD_RED,
    }
    
    def __init__(self, fmt: str, use_color: bool = True):
        super().__init__(fmt)
        self.use_color = use_color
        
    def format(self, record):
        if self.use_color and sys.platform != 'win32':
            color = self.COLORS.get(record.levelno, self.GREY)
            record.levelname = f"{color}{record.levelname}{self.RESET}"
            
            # Colorize specific parts
            if hasattr(record, 'component'):
                record.component = f"{self.CYAN}{record.component}{self.RESET}"
                
        return super().format(record)


class LoggerManager:
    """Manajer logging global"""
    
    _instances = {}
    _initialized = False
    
    def __init__(self):
        self.loggers = {}
        self.log_dir = settings.logging.log_dir
        self.log_level = getattr(logging, settings.logging.level.upper())
        
        # Buat directory log
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup root logger
        self._setup_root_logger()
        
    def _setup_root_logger(self):
        """Setup root logger dengan file dan console handler"""
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # Remove existing handlers
        root_logger.handlers.clear()
        
        # File handler (all logs)
        log_file = self.log_dir / f"mylove_{datetime.now().strftime('%Y%m')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(logging.Formatter(DEFAULT_FORMAT))
        root_logger.addHandler(file_handler)
        
        # Console handler (colored)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        
        if settings.logging.level == 'DEBUG':
            console_formatter = ColoredFormatter(DEBUG_FORMAT)
        else:
            console_formatter = ColoredFormatter(SIMPLE_FORMAT)
            
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # Error file handler (errors only)
        error_log = self.log_dir / f"error_{datetime.now().strftime('%Y%m')}.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log,
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(DEFAULT_FORMAT))
        root_logger.addHandler(error_handler)
        
        # Debug file handler (debug only, if enabled)
        if settings.logging.level == 'DEBUG':
            debug_log = self.log_dir / f"debug_{datetime.now().strftime('%Y%m%d')}.log"
            debug_handler = logging.FileHandler(debug_log, encoding='utf-8')
            debug_handler.setLevel(logging.DEBUG)
            debug_handler.setFormatter(logging.Formatter(DEBUG_FORMAT))
            root_logger.addHandler(debug_handler)
            
        self._initialized = True
        
    def get_logger(self, name: str, component: Optional[str] = None) -> logging.Logger:
        """Get or create logger dengan component context"""
        if name in self.loggers:
            return self.loggers[name]
            
        logger = logging.getLogger(name)
        
        # Add component context if provided
        if component:
            old_factory = logging.getLogRecordFactory()
            
            def record_factory(*args, **kwargs):
                record = old_factory(*args, **kwargs)
                record.component = component
                return record
                
            logging.setLogRecordFactory(record_factory)
            
        self.loggers[name] = logger
        return logger


# Global logger manager instance
_logger_manager = None


def setup_logging(component: Optional[str] = None) -> logging.Logger:
    """Setup logging untuk komponen tertentu"""
    global _logger_manager
    
    if _logger_manager is None:
        _logger_manager = LoggerManager()
        
    # Get caller's name
    import inspect
    frame = inspect.currentframe().f_back
    module = frame.f_globals['__name__']
    
    return _logger_manager.get_logger(module, component)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get logger by name"""
    global _logger_manager
    
    if _logger_manager is None:
        _logger_manager = LoggerManager()
        
    if name is None:
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals['__name__']
        
    return _logger_manager.get_logger(name)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def log_function_call(logger: logging.Logger):
    """Decorator untuk log function calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"Calling {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func.__name__} completed")
                return result
            except Exception as e:
                logger.error(f"{func.__name__} failed: {e}")
                raise
        return wrapper
    return decorator


def async_log_function_call(logger: logging.Logger):
    """Decorator untuk async function calls"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            logger.debug(f"Calling {func.__name__}")
            try:
                result = await func(*args, **kwargs)
                logger.debug(f"{func.__name__} completed")
                return result
            except Exception as e:
                logger.error(f"{func.__name__} failed: {e}")
                raise
        return wrapper
    return decorator


__all__ = ['setup_logging', 'get_logger', 'log_function_call', 'async_log_function_call']
