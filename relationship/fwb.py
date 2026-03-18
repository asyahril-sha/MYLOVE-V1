#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - FWB SYSTEM (ENHANCED)
=============================================================================
- Multiple FWB dengan role yang sama (beda orang)
- List FWB seperti HTS
- Track history putus-nyambung
- PDKT bisa pacaran lagi dengan orang baru setelah break up
- **Support untuk multiple FWB (untuk threesome)**
"""

import time
import logging
import random
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class FWBSystem:
    """
    Sistem FWB (Friends With Benefits) Enhanced
    Bisa multiple FWB dengan role yang sama (beda orang)
    Track history hubungan
    """
    
    def __init__(self, relationship_memory, ranking_system):
        self.relationship_memory = relationship_memory
        self.ranking_system = ranking_system
        
        # Role yang bisa FWB (hanya PDKT)
        self.fwb_eligible_roles = ['pdkt']
        
        # Intimacy level requirements
        self.min_intimacy_for_fwb = 6  # Minimal level 6 untuk FWB
        
        # Multiple FWB instances per role
        self.fwb_instances = {}  # {user_id: {role: [instances]}}
        
        logger.info("✅ FWBSystem Enhanced initialized")
        
    # =========================================================================
    # FWB INSTANCE MANAGEMENT
    # =========================================================================
    
    async def create_fwb_instance(self, user_id: int, role: str, name: str = "") -> Dict:
        """
        Create new FWB instance (orang baru)
        
        Args:
            user_id: ID user
            role: Role name (harus PDKT)
            name: Nama atau identitas orang (optional)
            
        Returns:
            FWB instance data
        """
        if role not in self.fwb_eligible_roles:
            raise ValueError(f"Role {role} tidak bisa jadi FWB")
            
        # Generate unique ID untuk instance
        instance_id = f"fwb_{user_id}_{role}_{int(time.time())}_{random.randint(100,999)}"
        
        # Create instance
        instance = {
            "instance_id": instance_id,
            "role": role,
            "name": name or f"{role.title()} #{random.randint(1,99)}",
            "created_at": time.time(),
            "status": "fwb",  # fwb, pacar, putus
            "intimacy_level": 1,
            "total_interactions": 0,
            "total_intim_sessions": 0,
            "total_climax": 0,
            "milestones": [],
            "history": [
                {
                    "event": "created",
                    "status": "fwb",
                    "timestamp": time.time()
                }
            ],
            "last_interaction": time.time()
        }
        
        # Store in instances
        user_key = str(user_id)
        if user_key not in self.fwb_instances:
            self.fwb_instances[user_key] = {}
        if role not in self.fwb_instances[user_key]:
            self.fwb_instances[user_key][role] = []
            
        self.fwb_instances[user_key][role].append(instance)
        
        logger.info(f"✅ Created new FWB instance: {instance['name']} for user {user_id}")
        
        return instance
        
    # =========================================================================
    # GET FWB INSTANCES
    # =========================================================================
    
    async def get_fwb_instances(self, user_id: int, role: Optional[str] = None) -> List[Dict]:
        """
        Get all FWB instances for user
        
        Args:
            user_id: ID user
            role: Optional role filter
            
        Returns:
            List of FWB instances
        """
        user_key = str(user_id)
        
        if user_key not in self.fwb_instances:
            return []
            
        if role:
            return self.fwb_instances[user_key].get(role, [])
        else:
            # Flatten all roles
            instances = []
            for role_instances in self.fwb_instances[user_key].values():
                instances.extend(role_instances)
            return instances
            
    async def get_fwb_instance(self, user_id: int, instance_id: str) -> Optional[Dict]:
        """Get specific FWB instance by ID"""
        user_key = str(user_id)
        
        if user_key not in self.fwb_instances:
            return None
            
        for role, instances in self.fwb_instances[user_key].items():
            for inst in instances:
                if inst['instance_id'] == instance_id:
                    return inst
                    
        return None
        
    async def get_fwb_by_index(self, user_id: int, index: int) -> Optional[Dict]:
        """
        Get FWB by index (untuk /fwb-1, /fwb-2)
        
        Args:
            user_id: ID user
            index: 1-based index
            
        Returns:
            FWB instance or None
        """
        instances = await self.get_fwb_instances(user_id)
        
        if 1 <= index <= len(instances):
            return instances[index - 1]
            
        return None
        
    # =========================================================================
    # GET FWB FOR THREESOME
    # =========================================================================
    
    async def get_fwb_for_threesome(self, user_id: int, min_level: int = 1) -> List[Dict]:
        """
        Get FWB instances yang eligible untuk threesome
        
        Args:
            user_id: ID user
            min_level: Minimal intimacy level
            
        Returns:
            List of FWB instances with selection info
        """
        instances = await self.get_fwb_instances(user_id)
        
        # Filter active FWB only (not putus)
        active = [i for i in instances if i['status'] in ['fwb', 'pacar']]
        
        # Filter by level
        eligible = [
            i for i in active 
            if i.get('intimacy_level', 1) >= min_level
        ]
        
        # Add selection info
        for i, inst in enumerate(eligible, 1):
            inst['select_id'] = i
            inst['select_name'] = f"{i}. {inst['name']} (Level {inst.get('intimacy_level', 1)})"
            inst['type'] = 'fwb'
            
        return eligible
        
    async def get_fwb_by_indices(self, user_id: int, indices: List[int]) -> List[Dict]:
        """
        Get multiple FWB instances by indices (untuk threesome)
        
        Args:
            user_id: ID user
            indices: List of indices from get_fwb_for_threesome
            
        Returns:
            List of FWB instances
        """
        eligible = await self.get_fwb_for_threesome(user_id)
        
        selected = []
        for idx in indices:
            if 1 <= idx <= len(eligible):
                selected.append(eligible[idx - 1])
                
        return selected
        
    async def get_fwb_by_role_and_index(self, user_id: int, role: str, index: int) -> Optional[Dict]:
        """
        Get FWB instance by role and index (untuk role yang sama)
        
        Args:
            user_id: ID user
            role: Role name
            index: 1-based index dalam role tersebut
            
        Returns:
            FWB instance or None
        """
        instances = await self.get_fwb_instances(user_id, role)
        
        if 1 <= index <= len(instances):
            return instances[index - 1]
            
        return None
        
    # =========================================================================
    # FWB STATUS MANAGEMENT
    # =========================================================================
    
    async def become_fwb(self, user_id: int, role: str, instance_id: Optional[str] = None) -> Dict:
        """
        Become FWB with someone
        
        Args:
            user_id: ID user
            role: Role name
            instance_id: Specific instance (if None, create new)
            
        Returns:
            Result with instance
        """
        # Check eligibility
        if role not in self.fwb_eligible_roles:
            return {
                'success': False,
                'reason': f"Role {role} tidak bisa jadi FWB. Hanya PDKT yang bisa."
            }
            
        # Get or create instance
        if instance_id:
            instance = await self.get_fwb_instance(user_id, instance_id)
            if not instance:
                return {'success': False, 'reason': 'Instance tidak ditemukan'}
        else:
            # Create new instance
            instance = await self.create_fwb_instance(user_id, role)
            
        # Update status
        instance['status'] = 'fwb'
        instance['history'].append({
            'event': 'became_fwb',
            'timestamp': time.time()
        })
        
        logger.info(f"💕 Became FWB: {instance['name']}")
        
        return {
            'success': True,
            'instance': instance,
            'message': f"Sekarang FWB dengan {instance['name']}"
        }
        
    async def become_pacar(self, user_id: int, instance_id: str) -> Dict:
        """
        Become pacar with FWB instance
        
        Args:
            user_id: ID user
            instance_id: FWB instance ID
            
        Returns:
            Result
        """
        instance = await self.get_fwb_instance(user_id, instance_id)
        
        if not instance:
            return {'success': False, 'reason': 'Instance tidak ditemukan'}
            
        if instance['status'] != 'fwb':
            return {'success': False, 'reason': f'Status sekarang {instance["status"]}'}
            
        # Check intimacy
        if instance['intimacy_level'] < self.min_intimacy_for_fwb:
            return {
                'success': False,
                'reason': f'Intimacy level terlalu rendah ({instance["intimacy_level"]}/12)'
            }
            
        # Update status
        old_status = instance['status']
        instance['status'] = 'pacar'
        instance['history'].append({
            'event': 'became_pacar',
            'from_status': old_status,
            'timestamp': time.time()
        })
        instance['milestones'].append('jadi_pacar')
        
        logger.info(f"💘 Became pacar: {instance['name']}")
        
        return {
            'success': True,
            'instance': instance,
            'message': f"Sekarang pacaran dengan {instance['name']}"
        }
        
    async def break_up(self, user_id: int, instance_id: str, become_fwb: bool = True) -> Dict:
        """
        Break up with FWB/pacar instance
        
        Args:
            user_id: ID user
            instance_id: Instance ID
            become_fwb: If True, become FWB again after break
            
        Returns:
            Result
        """
        instance = await self.get_fwb_instance(user_id, instance_id)
        
        if not instance:
            return {'success': False, 'reason': 'Instance tidak ditemukan'}
            
        old_status = instance['status']
        
        if become_fwb:
            # Jadi FWB lagi
            instance['status'] = 'fwb'
            new_status = 'fwb'
            message = f"Putus, tapi tetap FWB dengan {instance['name']}"
        else:
            # Putus total, tapi tetap di list
            instance['status'] = 'putus'
            new_status = 'putus'
            message = f"Putus total dengan {instance['name']}. Bisa cari orang baru."
            
        instance['history'].append({
            'event': 'break_up',
            'from_status': old_status,
            'to_status': new_status,
            'timestamp': time.time()
        })
        
        if not become_fwb:
            instance['milestones'].append('putus_total')
            
        logger.info(f"💔 Break up: {instance['name']} -> {new_status}")
        
        return {
            'success': True,
            'instance': instance,
            'message': message
        }
        
    # =========================================================================
    # FWB INTERACTIONS
    # =========================================================================
    
    async def interact_with_fwb(self, user_id: int, instance_id: str, message: str) -> Dict:
        """
        Interact with specific FWB instance
        
        Args:
            user_id: ID user
            instance_id: Instance ID
            message: User message
            
        Returns:
            Interaction result
        """
        instance = await self.get_fwb_instance(user_id, instance_id)
        
        if not instance:
            return {'success': False, 'reason': 'Instance tidak ditemukan'}
            
        # Update interaction count
        instance['total_interactions'] += 1
        instance['last_interaction'] = time.time()
        
        # Increase intimacy gradually
        if instance['total_interactions'] % 10 == 0:
            instance['intimacy_level'] = min(12, instance['intimacy_level'] + 1)
            
        return {
            'success': True,
            'instance': instance,
            'context': {
                'name': instance['name'],
                'status': instance['status'],
                'intimacy': instance['intimacy_level']
            }
        }
        
    async def record_intim(self, user_id: int, instance_id: str, climax: bool = False):
        """Record intimacy session with FWB"""
        instance = await self.get_fwb_instance(user_id, instance_id)
        
        if not instance:
            return
            
        instance['total_intim_sessions'] += 1
        
        if climax:
            instance['total_climax'] += 1
            instance['history'].append({
                'event': 'climax',
                'timestamp': time.time()
            })
            
        # Check for aftercare
        if instance['intimacy_level'] == 12:
            instance['needs_aftercare'] = True
            
    # =========================================================================
    # FWB LIST FORMATTING
    # =========================================================================
    
    async def get_fwb_list(self, user_id: int, include_putus: bool = False) -> List[Dict]:
        """
        Get formatted FWB list for display
        
        Args:
            user_id: ID user
            include_putus: Include putus status
            
        Returns:
            List of FWB instances
        """
        instances = await self.get_fwb_instances(user_id)
        
        # Filter by status
        if not include_putus:
            instances = [i for i in instances if i['status'] != 'putus']
            
        # Sort by last interaction
        instances.sort(key=lambda x: x['last_interaction'], reverse=True)
        
        # Add display info
        for i, inst in enumerate(instances, 1):
            inst['display_index'] = i
            inst['display_name'] = f"{i}. {inst['name']} ({inst['status']})"
            
        return instances
        
    def format_fwb_list(self, instances: List[Dict]) -> str:
        """Format FWB list for display"""
        if not instances:
            return "Belum ada FWB. Gunakan /fwb untuk memulai."
            
        lines = ["💕 **DAFTAR FWB**"]
        lines.append("_(Friends With Benefits - pilih dengan /fwb- [nomor])_")
        lines.append("")
        
        active = [i for i in instances if i['status'] == 'fwb']
        pacar = [i for i in instances if i['status'] == 'pacar']
        putus = [i for i in instances if i['status'] == 'putus']
        
        if pacar:
            lines.append("**💘 PACAR:**")
            for i, inst in enumerate(pacar, 1):
                lines.append(
                    f"{inst['display_index']}. **{inst['name']}**\n"
                    f"   Level {inst['intimacy_level']}/12 | {inst['total_interactions']} chat"
                )
            lines.append("")
                
        if active:
            lines.append("**💕 FWB AKTIF:**")
            for i, inst in enumerate(active, 1):
                lines.append(
                    f"{inst['display_index']}. **{inst['name']}**\n"
                    f"   Level {inst['intimacy_level']}/12 | {inst['total_intim_sessions']} intim"
                )
            lines.append("")
                
        if putus:
            lines.append("**💔 PUTUS:**")
            for i, inst in enumerate(putus[:3], 1):  # Show last 3
                lines.append(f"  • {inst['name']}")
                
        lines.append("")
        lines.append("💡 **Cara pakai:**")
        lines.append("• `/fwb-1` - Pilih FWB nomor 1")
        lines.append("• `/fwb-list` - Lihat semua FWB")
        lines.append("• `/fwb-break 1` - Putus dengan nomor 1")
        
        return "\n".join(lines)
        
    async def format_fwb_for_threesome(self, user_id: int) -> str:
        """
        Format daftar FWB untuk selection threesome
        """
        eligible = await self.get_fwb_for_threesome(user_id)
        
        if not eligible:
            return "Tidak ada FWB yang memenuhi syarat untuk threesome. Minimal level 1."
            
        lines = ["💞 **DAFTAR FWB UNTUK THREESOME**"]
        lines.append("_(pilih dengan nomor)_")
        lines.append("")
        
        for fwb in eligible:
            lines.append(
                f"{fwb['select_id']}. **{fwb['name']}**\n"
                f"   Level {fwb.get('intimacy_level', 1)}/12 | "
                f"{fwb.get('total_intim_sessions', 0)} intim"
            )
            
        return "\n".join(lines)
        
    # =========================================================================
    # FWB STATISTICS
    # =========================================================================
    
    async def get_fwb_stats(self, user_id: int) -> Dict:
        """Get FWB statistics"""
        instances = await self.get_fwb_instances(user_id)
        
        stats = {
            "total_fwb": len([i for i in instances if i['status'] == 'fwb']),
            "total_pacar": len([i for i in instances if i['status'] == 'pacar']),
            "total_putus": len([i for i in instances if i['status'] == 'putus']),
            "total_intim": sum(i['total_intim_sessions'] for i in instances),
            "total_climax": sum(i['total_climax'] for i in instances),
            "avg_intimacy": sum(i['intimacy_level'] for i in instances) / len(instances) if instances else 0
        }
        
        return stats
        
    async def get_fwb_history(self, user_id: int, instance_id: str) -> List[Dict]:
        """Get full history for FWB instance"""
        instance = await self.get_fwb_instance(user_id, instance_id)
        
        if not instance:
            return []
            
        return instance.get('history', [])


__all__ = ['FWBSystem']
