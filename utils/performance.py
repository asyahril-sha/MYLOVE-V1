#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - PERFORMANCE MONITORING
=============================================================================
- Tracking response time
- Memory usage monitoring
- Performance decorators
"""

import time
import functools
import psutil
import logging
from typing import Dict, Any, Optional, Callable
from collections import deque
from datetime import datetime, timedelta

from config import settings

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """
    Monitor performa bot
    - Response time tracking
    - Memory usage
    - Slow operation alerts
    """
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.response_times = deque(maxlen=max_history)
        self.slow_operations = deque(maxlen=100)
        self.error_counts = {}
        self.command_counts = {}
        self.start_time = time.time()
        self.memory_samples = deque(maxlen=100)
        
        # Thresholds (dari config)
        self.slow_threshold = settings.performance.target_response_time
        self.memory_warning_mb = settings.performance.max_memory_mb * 0.8
        
    def record_response_time(self, operation: str, duration: float):
        """Record response time for operation"""
        self.response_times.append({
            'operation': operation,
            'duration': duration,
            'timestamp': time.time()
        })
        
        # Check if slow
        if duration > self.slow_threshold:
            self.slow_operations.append({
                'operation': operation,
                'duration': duration,
                'threshold': self.slow_threshold,
                'timestamp': time.time()
            })
            logger.warning(f"⚠️ Slow operation: {operation} took {duration:.2f}s")
            
    def record_command(self, command: str, duration: float):
        """Record command execution"""
        self.command_counts[command] = self.command_counts.get(command, 0) + 1
        self.record_response_time(f"cmd_{command}", duration)
        
    def record_error(self, error_type: str):
        """Record error occurrence"""
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
    def sample_memory(self):
        """Sample current memory usage"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        memory_mb = memory_info.rss / (1024 * 1024)
        self.memory_samples.append({
            'rss_mb': memory_mb,
            'vms_mb': memory_info.vms / (1024 * 1024),
            'timestamp': time.time()
        })
        
        # Check if memory high
        if memory_mb > self.memory_warning_mb:
            logger.warning(f"⚠️ High memory usage: {memory_mb:.1f} MB")
            
        return memory_mb
        
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        now = time.time()
        
        # Response time stats
        if self.response_times:
            recent = [r for r in self.response_times if r['timestamp'] > now - 3600]
            durations = [r['duration'] for r in recent]
            
            avg_response = sum(durations) / len(durations) if durations else 0
            max_response = max(durations) if durations else 0
            p95_response = sorted(durations)[int(len(durations) * 0.95)] if len(durations) > 20 else 0
        else:
            avg_response = max_response = p95_response = 0
            
        # Memory stats
        if self.memory_samples:
            mem_values = [m['rss_mb'] for m in self.memory_samples]
            current_mem = mem_values[-1] if mem_values else 0
            avg_mem = sum(mem_values) / len(mem_values) if mem_values else 0
            max_mem = max(mem_values) if mem_values else 0
        else:
            current_mem = avg_mem = max_mem = 0
            
        return {
            'uptime': now - self.start_time,
            'total_commands': sum(self.command_counts.values()),
            'commands': dict(self.command_counts),
            'errors': dict(self.error_counts),
            'response_time': {
                'avg': round(avg_response, 2),
                'max': round(max_response, 2),
                'p95': round(p95_response, 2),
                'samples': len(self.response_times)
            },
            'memory': {
                'current_mb': round(current_mem, 1),
                'avg_mb': round(avg_mem, 1),
                'max_mb': round(max_mem, 1),
                'samples': len(self.memory_samples)
            },
            'slow_operations': list(self.slow_operations)[-10:]  # Last 10
        }
        
    def check_health(self) -> Dict[str, str]:
        """
        Check system health
        
        Returns:
            Dict with health status
        """
        status = {}
        
        # Response time health
        if self.response_times:
            recent = list(self.response_times)[-100:]  # Last 100
            slow_count = sum(1 for r in recent if r['duration'] > self.slow_threshold)
            slow_percent = (slow_count / len(recent)) * 100 if recent else 0
            
            if slow_percent > 20:
                status['response_time'] = 'critical'
            elif slow_percent > 10:
                status['response_time'] = 'warning'
            else:
                status['response_time'] = 'healthy'
                
        # Memory health
        if self.memory_samples:
            current_mem = self.memory_samples[-1]['rss_mb']
            if current_mem > settings.performance.max_memory_mb:
                status['memory'] = 'critical'
            elif current_mem > self.memory_warning_mb:
                status['memory'] = 'warning'
            else:
                status['memory'] = 'healthy'
                
        return status


# =============================================================================
# DECORATORS
# =============================================================================

_monitor = PerformanceMonitor()


def measure_time(func: Callable) -> Callable:
    """
    Decorator untuk mengukur waktu eksekusi function
    
    Args:
        func: Function to measure
        
    Returns:
        Wrapped function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start
            _monitor.record_response_time(func.__name__, duration)
            return result
        except Exception as e:
            _monitor.record_error(type(e).__name__)
            raise
    return wrapper


def async_measure_time(func: Callable) -> Callable:
    """
    Decorator untuk mengukur waktu eksekusi async function
    
    Args:
        func: Async function to measure
        
    Returns:
        Wrapped function
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start
            _monitor.record_response_time(func.__name__, duration)
            return result
        except Exception as e:
            _monitor.record_error(type(e).__name__)
            raise
    return wrapper


def measure_command(command_name: str) -> Callable:
    """
    Decorator khusus untuk command handlers
    
    Args:
        command_name: Nama command
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(update, context):
            start = time.time()
            try:
                result = await func(update, context)
                duration = time.time() - start
                _monitor.record_command(command_name, duration)
                return result
            except Exception as e:
                _monitor.record_error(type(e).__name__)
                raise
        return wrapper
    return decorator


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    return _monitor


__all__ = [
    'PerformanceMonitor',
    'measure_time',
    'async_measure_time',
    'measure_command',
    'get_performance_monitor',
]
