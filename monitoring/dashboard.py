#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - GRAFANA DASHBOARD
=============================================================================
- Dashboard generator untuk Grafana
- JSON dashboard template
- Real-time monitoring
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from config import settings

logger = logging.getLogger(__name__)


class DashboardServer:
    """
    Server untuk menyediakan dashboard Grafana
    """
    
    def __init__(self, metrics_collector):
        self.metrics_collector = metrics_collector
        self.dashboard_path = Path("monitoring/dashboards")
        self.dashboard_path.mkdir(parents=True, exist_ok=True)
        
    def generate_overview_dashboard(self) -> Dict[str, Any]:
        """
        Generate overview dashboard untuk MYLOVE
        
        Returns:
            Dashboard JSON
        """
        dashboard = {
            "dashboard": {
                "title": "MYLOVE Ultimate - Overview",
                "description": "Real-time monitoring untuk MYLOVE bot",
                "schemaVersion": 36,
                "version": 1,
                "refresh": "30s",
                "time": {
                    "from": "now-6h",
                    "to": "now"
                },
                "panels": [
                    # ===== ROW 1: STATS CARDS =====
                    {
                        "id": 1,
                        "gridPos": {"h": 3, "w": 3, "x": 0, "y": 0},
                        "type": "stat",
                        "title": "Active Sessions",
                        "targets": [{
                            "expr": "mylove_active_sessions{role='total'}",
                            "legendFormat": "Active"
                        }],
                        "options": {
                            "colorMode": "value",
                            "graphMode": "area",
                            "justifyMode": "auto",
                            "orientation": "auto",
                            "reduceOptions": {
                                "calcs": ["lastNotNull"]
                            }
                        }
                    },
                    {
                        "id": 2,
                        "gridPos": {"h": 3, "w": 3, "x": 3, "y": 0},
                        "type": "stat",
                        "title": "Total Messages",
                        "targets": [{
                            "expr": "sum(mylove_messages_total)",
                            "legendFormat": "Messages"
                        }]
                    },
                    {
                        "id": 3,
                        "gridPos": {"h": 3, "w": 3, "x": 6, "y": 0},
                        "type": "stat",
                        "title": "Avg Response Time",
                        "targets": [{
                            "expr": "mylove_response_time_avg_seconds",
                            "legendFormat": "Response Time"
                        }],
                        "options": {
                            "unit": "s",
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"color": "green", "value": None},
                                    {"color": "yellow", "value": 2},
                                    {"color": "red", "value": 5}
                                ]
                            }
                        }
                    },
                    {
                        "id": 4,
                        "gridPos": {"h": 3, "w": 3, "x": 9, "y": 0},
                        "type": "stat",
                        "title": "Memory Usage",
                        "targets": [{
                            "expr": "mylove_memory_usage_mb",
                            "legendFormat": "Memory"
                        }],
                        "options": {
                            "unit": "MB",
                            "thresholds": {
                                "mode": "absolute",
                                "steps": [
                                    {"color": "green", "value": None},
                                    {"color": "yellow", "value": 400},
                                    {"color": "red", "value": 500}
                                ]
                            }
                        }
                    },
                    
                    # ===== ROW 2: TIME SERIES =====
                    {
                        "id": 5,
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 3},
                        "type": "graph",
                        "title": "Response Time (p95)",
                        "targets": [{
                            "expr": "histogram_quantile(0.95, sum(rate(mylove_response_time_seconds_bucket[5m])) by (le))",
                            "legendFormat": "p95"
                        }],
                        "options": {
                            "legend": {"show": True}
                        }
                    },
                    
                    # ===== ROW 3: COMMAND STATS =====
                    {
                        "id": 6,
                        "gridPos": {"h": 8, "w": 6, "x": 0, "y": 11},
                        "type": "piechart",
                        "title": "Commands Distribution",
                        "targets": [{
                            "expr": "topk(5, sum by (command) (mylove_commands_total))",
                            "legendFormat": "{{command}}"
                        }]
                    },
                    {
                        "id": 7,
                        "gridPos": {"h": 8, "w": 6, "x": 6, "y": 11},
                        "type": "piechart",
                        "title": "Intimacy by Role",
                        "targets": [{
                            "expr": "sum by (role) (mylove_intim_sessions_total)",
                            "legendFormat": "{{role}}"
                        }]
                    },
                    
                    # ===== ROW 4: SESSIONS BY ROLE =====
                    {
                        "id": 8,
                        "gridPos": {"h": 8, "w": 6, "x": 0, "y": 19},
                        "type": "barchart",
                        "title": "Sessions by Role",
                        "targets": [{
                            "expr": "sum by (role) (mylove_sessions_total)",
                            "legendFormat": "{{role}}"
                        }]
                    },
                    {
                        "id": 9,
                        "gridPos": {"h": 8, "w": 6, "x": 6, "y": 19},
                        "type": "barchart",
                        "title": "Climax by Position",
                        "targets": [{
                            "expr": "topk(10, sum by (position) (mylove_climax_total))",
                            "legendFormat": "{{position}}"
                        }]
                    },
                    
                    # ===== ROW 5: ERROR STATS =====
                    {
                        "id": 10,
                        "gridPos": {"h": 6, "w": 12, "x": 0, "y": 27},
                        "type": "graph",
                        "title": "Error Rate",
                        "targets": [{
                            "expr": "rate(mylove_errors_total[5m])",
                            "legendFormat": "{{type}}"
                        }],
                        "options": {
                            "legend": {"show": True}
                        }
                    }
                ],
                "templating": {
                    "list": [
                        {
                            "name": "role",
                            "type": "query",
                            "query": "label_values(mylove_sessions_total, role)",
                            "refresh": 1,
                            "options": [],
                            "includeAll": True,
                            "allValue": ".*"
                        }
                    ]
                },
                "annotations": {
                    "list": [
                        {
                            "name": "Deploy",
                            "type": "dashboard",
                            "builtIn": 1,
                            "datasource": "-- Grafana --",
                            "enable": True,
                            "hide": True,
                            "iconColor": "rgba(0, 211, 255, 1)",
                            "limit": 100
                        }
                    ]
                }
            }
        }
        
        return dashboard
        
    def generate_detailed_dashboard(self) -> Dict[str, Any]:
        """
        Generate detailed analytics dashboard
        
        Returns:
            Dashboard JSON
        """
        dashboard = {
            "dashboard": {
                "title": "MYLOVE Ultimate - Detailed Analytics",
                "description": "Detailed analytics untuk MYLOVE bot",
                "schemaVersion": 36,
                "version": 1,
                "refresh": "1m",
                "time": {
                    "from": "now-24h",
                    "to": "now"
                },
                "panels": [
                    # Intimacy level distribution
                    {
                        "id": 1,
                        "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0},
                        "type": "heatmap",
                        "title": "Intimacy Level Distribution",
                        "targets": [{
                            "expr": "mylove_intimacy_levels_bucket",
                            "legendFormat": "Level {{le}}"
                        }]
                    },
                    
                    # Peak hours
                    {
                        "id": 2,
                        "gridPos": {"h": 8, "w": 6, "x": 6, "y": 0},
                        "type": "graph",
                        "title": "Activity by Hour",
                        "targets": [{
                            "expr": "sum(rate(mylove_messages_total[1h])) by (hour)",
                            "legendFormat": "Messages"
                        }]
                    },
                    
                    # User growth
                    {
                        "id": 3,
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
                        "type": "graph",
                        "title": "User Growth",
                        "targets": [{
                            "expr": "sum(mylove_connected_users)",
                            "legendFormat": "Users"
                        }]
                    },
                    
                    # Performance heatmap
                    {
                        "id": 4,
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 16},
                        "type": "heatmap",
                        "title": "Response Time Heatmap",
                        "targets": [{
                            "expr": "sum(rate(mylove_response_time_seconds_bucket[5m])) by (le)",
                            "legendFormat": "{{le}}"
                        }]
                    }
                ]
            }
        }
        
        return dashboard
        
    def save_dashboard(self, dashboard: Dict[str, Any], filename: str):
        """Save dashboard JSON to file"""
        filepath = self.dashboard_path / filename
        with open(filepath, 'w') as f:
            json.dump(dashboard, f, indent=2)
        logger.info(f"✅ Dashboard saved to {filepath}")
        
    def export_all_dashboards(self):
        """Export all dashboards to JSON files"""
        overview = self.generate_overview_dashboard()
        detailed = self.generate_detailed_dashboard()
        
        self.save_dashboard(overview, "mylove_overview.json")
        self.save_dashboard(detailed, "mylove_detailed.json")
        
        return {
            "overview": str(self.dashboard_path / "mylove_overview.json"),
            "detailed": str(self.dashboard_path / "mylove_detailed.json")
        }


__all__ = ['DashboardServer']
