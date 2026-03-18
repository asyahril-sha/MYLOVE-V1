#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - PROMETHEUS METRICS
=============================================================================
- Metrics collection untuk Prometheus
- Counter, Gauge, Histogram
- Export untuk Grafana dashboard
"""

import time
import logging
from typing import Dict, Any, Optional
from prometheus_client import (
    Counter, Gauge, Histogram, generate_latest,
    REGISTRY, start_http_server
)

from config import settings
from ..utils.performance import get_performance_monitor

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Collector untuk Prometheus metrics
    """
    
    def __init__(self):
        # ===== COUNTERS =====
        self.messages_total = Counter(
            'mylove_messages_total',
            'Total messages received',
            ['type']  # user, bot
        )
        
        self.commands_total = Counter(
            'mylove_commands_total',
            'Total commands executed',
            ['command']
        )
        
        self.intim_sessions_total = Counter(
            'mylove_intim_sessions_total',
            'Total intimacy sessions',
            ['role', 'location']
        )
        
        self.climax_total = Counter(
            'mylove_climax_total',
            'Total climax events',
            ['role', 'position']
        )
        
        self.errors_total = Counter(
            'mylove_errors_total',
            'Total errors',
            ['type']
        )
        
        self.sessions_total = Counter(
            'mylove_sessions_total',
            'Total sessions created',
            ['role']
        )
        
        # ===== GAUGES =====
        self.active_sessions = Gauge(
            'mylove_active_sessions',
            'Number of active sessions',
            ['role']
        )
        
        self.memory_usage = Gauge(
            'mylove_memory_usage_mb',
            'Memory usage in MB'
        )
        
        self.connected_users = Gauge(
            'mylove_connected_users',
            'Number of connected users'
        )
        
        self.response_time_avg = Gauge(
            'mylove_response_time_avg_seconds',
            'Average response time in seconds'
        )
        
        self.database_size = Gauge(
            'mylove_database_size_mb',
            'Database file size in MB'
        )
        
        # ===== HISTOGRAMS =====
        self.response_time = Histogram(
            'mylove_response_time_seconds',
            'Response time in seconds',
            ['operation'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        )
        
        self.intimacy_levels = Histogram(
            'mylove_intimacy_levels',
            'Intimacy level distribution',
            ['role'],
            buckets=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        )
        
        self._server_started = False
        
    def start_server(self, port: int = settings.prometheus_port):
        """Start Prometheus HTTP server"""
        if not self._server_started:
            try:
                start_http_server(port)
                self._server_started = True
                logger.info(f"📊 Prometheus metrics server started on port {port}")
            except Exception as e:
                logger.error(f"Failed to start Prometheus server: {e}")
                
    # ===== COUNTER METHODS =====
    
    def inc_message(self, msg_type: str = 'user'):
        """Increment message counter"""
        self.messages_total.labels(type=msg_type).inc()
        
    def inc_command(self, command: str):
        """Increment command counter"""
        self.commands_total.labels(command=command).inc()
        
    def inc_intim_session(self, role: str = 'unknown', location: str = 'unknown'):
        """Increment intimacy session counter"""
        self.intim_sessions_total.labels(role=role, location=location).inc()
        
    def inc_climax(self, role: str = 'unknown', position: str = 'unknown'):
        """Increment climax counter"""
        self.climax_total.labels(role=role, position=position).inc()
        
    def inc_error(self, error_type: str):
        """Increment error counter"""
        self.errors_total.labels(type=error_type).inc()
        
    def inc_session(self, role: str):
        """Increment session counter"""
        self.sessions_total.labels(role=role).inc()
        
    # ===== GAUGE METHODS =====
    
    def set_active_sessions(self, count: int, role: str = 'total'):
        """Set active sessions count"""
        self.active_sessions.labels(role=role).set(count)
        
    def update_memory_usage(self):
        """Update memory usage gauge"""
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / (1024 * 1024)
        self.memory_usage.set(memory_mb)
        
    def set_connected_users(self, count: int):
        """Set connected users count"""
        self.connected_users.set(count)
        
    def set_response_time_avg(self, avg: float):
        """Set average response time"""
        self.response_time_avg.set(avg)
        
    def set_database_size(self, size_mb: float):
        """Set database file size"""
        self.database_size.set(size_mb)
        
    # ===== HISTOGRAM METHODS =====
    
    def observe_response_time(self, duration: float, operation: str = 'unknown'):
        """Observe response time"""
        self.response_time.labels(operation=operation).observe(duration)
        
    def observe_intimacy_level(self, level: int, role: str):
        """Observe intimacy level"""
        self.intimacy_levels.labels(role=role).observe(level)
        
    # ===== COLLECTION =====
    
    def collect_all(self):
        """Collect all metrics from performance monitor"""
        monitor = get_performance_monitor()
        stats = monitor.get_stats()
        
        # Update gauges from stats
        self.set_response_time_avg(stats['response_time']['avg'])
        self.update_memory_usage()
        
        # Record slow operations as histograms
        for op in stats['slow_operations']:
            self.observe_response_time(op['duration'], op['operation'])
            
    def get_metrics(self) -> bytes:
        """Get all metrics in Prometheus format"""
        return generate_latest(REGISTRY)


# Global metrics collector instance
_metrics_collector = None


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector instance"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


__all__ = ['MetricsCollector', 'get_metrics_collector']
