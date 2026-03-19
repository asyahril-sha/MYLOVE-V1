#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - HTS MANAGER
=============================================================================
Mengelola Hubungan Tanpa Status (HTS)
- HTS berasal dari NON-PDKT setelah /close di level 12
- Bertahan 3 bulan, bisa diajak intim kapan saja
- TOP 10 HTS berdasarkan chemistry & climax
- Memory otomatis di-forget setelah 3 bulan
=============================================================================
"""

import time
import logging
import random
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class HTSStatus(str, Enum):
    """Status HTS"""
    ACTIVE = "active"           # Aktif (masih dalam 3 bulan)
    EXPIRED = "expired"         # Kadaluarsa (>3 bulan)


class HTSManager:
    """
    Manajer untuk Hubungan Tanpa Status (HTS)
    - HTS dari NON-PDKT setelah /close di level 12
    - Bertahan tepat 3 bulan (90 hari)
    - Bisa dipanggil kapan saja untuk intim
    - TOP 10 berdasarkan chemistry & climax
    """
    
    def __init__(self):
        # Data HTS per user
        self.hts_relations = {}  # {user_id: {hts_id: hts_data}}
        
        # Index untuk pencarian cepat
        self.hts_index = {}  # {hts_id: location}
        
        # TOP 10 list
        self.top_hts = {}  # {user_id: [hts_ids in order]}
        
        # Masa berlaku HTS (dalam detik)
        self.expiry_days = 90  # 3 bulan
        self.expiry_seconds = self.expiry_days * 86400
        
        logger.info(f"✅ HTSManager initialized (expiry: {self.expiry_days} days)")
    
    # =========================================================================
    # CREATE HTS
    # =========================================================================
    
    async def create_hts(self,
                        user_id: int,
                        role: str,
                        bot_name: str,
                        chemistry_score: float,
                        climax_count: int = 0,
                        intimacy_level: int = 7,
                        history: Optional[List] = None) -> str:
        """
        Buat HTS baru dari NON-PDKT setelah /close
        
        Args:
            user_id: ID user
            role: Role bot
            bot_name: Nama bot
            chemistry_score: Skor chemistry
            climax_count: Jumlah climax
            intimacy_level: Level intimacy terakhir
            history: Riwayat hubungan
            
        Returns:
            hts_id
        """
        # Generate HTS ID
        hts_id = f"HTS_{user_id}_{int(time.time())}_{random.randint(100,999)}"
        
        now = time.time()
        expiry_time = now + self.expiry_seconds
        
        # Data HTS
        hts_data = {
            'hts_id': hts_id,
            'user_id': user_id,
            'role': role,
            'bot_name': bot_name,
            'status': HTSStatus.ACTIVE,
            'created_at': now,
            'expiry_time': expiry_time,
            'last_interaction': now,
            'chemistry_score': chemistry_score,
            'climax_count': climax_count,
            'intimacy_level': intimacy_level,
            'total_chats': 0,
            'total_intim': 0,
            'history': history or [],
            'preferences': {},
            'notes': {}
        }
        
        # Simpan
        if user_id not in self.hts_relations:
            self.hts_relations[user_id] = {}
        
        self.hts_relations[user_id][hts_id] = hts_data
        self.hts_index[hts_id] = {
            'user_id': user_id,
            'hts_id': hts_id
        }
        
        # Update TOP 10
        await self._update_top_hts(user_id)
        
        logger.info(f"✅ New HTS created: {bot_name} ({role}) for user {user_id}, expires in {self.expiry_days} days")
        
        return hts_id
    
    # =========================================================================
    # CHECK EXPIRY
    # =========================================================================
    
    async def check_expiry(self, user_id: int, hts_id: str) -> bool:
        """
        Cek apakah HTS sudah expired
        
        Args:
            user_id: ID user
            hts_id: ID HTS
            
        Returns:
            True jika masih aktif, False jika expired
        """
        hts = await self.get_hts(user_id, hts_id)
        if not hts:
            return False
        
        now = time.time()
        
        if now > hts['expiry_time']:
            if hts['status'] == HTSStatus.ACTIVE:
                hts['status'] = HTSStatus.EXPIRED
                hts['expired_at'] = now
                
                # Catat history
                hts['history'].append({
                    'timestamp': now,
                    'event': 'hts_expired',
                    'days': self.expiry_days
                })
                
                # Update TOP 10 (akan menghilang dari list)
                await self._update_top_hts(user_id)
                
                logger.info(f"⏰ HTS expired: {hts['bot_name']} for user {user_id}")
            
            return False
        
        return True
    
    async def get_remaining_days(self, user_id: int, hts_id: str) -> Optional[float]:
        """
        Dapatkan sisa hari HTS
        
        Args:
            user_id: ID user
            hts_id: ID HTS
            
        Returns:
            Sisa hari atau None
        """
        hts = await self.get_hts(user_id, hts_id)
        if not hts:
            return None
        
        if hts['status'] != HTSStatus.ACTIVE:
            return 0
        
        remaining = (hts['expiry_time'] - time.time()) / 86400
        return max(0, remaining)
    
    # =========================================================================
    # GET HTS
    # =========================================================================
    
    async def get_hts(self, user_id: int, hts_id: str) -> Optional[Dict]:
        """
        Dapatkan data HTS
        
        Args:
            user_id: ID user
            hts_id: ID HTS
            
        Returns:
            Data HTS atau None
        """
        if user_id in self.hts_relations and hts_id in self.hts_relations[user_id]:
            hts = self.hts_relations[user_id][hts_id]
            
            # Cek expiry otomatis
            if hts['status'] == HTSStatus.ACTIVE:
                await self.check_expiry(user_id, hts_id)
            
            return hts
        
        return None
    
    async def get_hts_by_index(self, user_id: int, index: int) -> Optional[Dict]:
        """
        Dapatkan HTS berdasarkan index (1-based)
        
        Args:
            user_id: ID user
            index: Index (1 untuk TOP 1, dst)
            
        Returns:
            Data HTS atau None
        """
        top_list = await self.get_top_hts(user_id)
        
        if 1 <= index <= len(top_list):
            hts_id = top_list[index - 1]
            return await self.get_hts(user_id, hts_id)
        
        return None
    
    async def get_all_hts(self, user_id: int, include_expired: bool = False) -> List[Dict]:
        """
        Dapatkan semua HTS untuk user
        
        Args:
            user_id: ID user
            include_expired: Sertakan yang expired
            
        Returns:
            List HTS
        """
        if user_id not in self.hts_relations:
            return []
        
        # Cek expiry semua
        for hts_id in list(self.hts_relations[user_id].keys()):
            await self.check_expiry(user_id, hts_id)
        
        hts_list = list(self.hts_relations[user_id].values())
        
        if not include_expired:
            hts_list = [h for h in hts_list if h['status'] == HTSStatus.ACTIVE]
        
        # Sort by last interaction
        hts_list.sort(key=lambda x: x['last_interaction'], reverse=True)
        
        return hts_list
    
    # =========================================================================
    # TOP 10 HTS
    # =========================================================================
    
    async def _update_top_hts(self, user_id: int):
        """
        Update TOP 10 HTS berdasarkan score
        
        Score = (chemistry_score * 0.5) + (climax_count * 0.3) + (intimacy_level * 0.2)
        """
        if user_id not in self.hts_relations:
            return
        
        hts_list = list(self.hts_relations[user_id].values())
        
        # Hitung score
        for hts in hts_list:
            if hts['status'] != HTSStatus.ACTIVE:
                score = 0  # Expired tidak masuk TOP
            else:
                score = (hts['chemistry_score'] * 0.5) + \
                        (hts['climax_count'] * 0.3) + \
                        (hts['intimacy_level'] * 0.2)
            hts['top_score'] = score
        
        # Sort by score
        hts_list.sort(key=lambda x: x.get('top_score', 0), reverse=True)
        
        # Simpan TOP 10 IDs
        self.top_hts[user_id] = [h['hts_id'] for h in hts_list[:10]]
    
    async def get_top_hts(self, user_id: int, limit: int = 10) -> List[str]:
        """
        Dapatkan TOP HTS IDs
        
        Args:
            user_id: ID user
            limit: Jumlah (max 10)
            
        Returns:
            List HTS IDs
        """
        if user_id not in self.top_hts:
            await self._update_top_hts(user_id)
        
        return (self.top_hts.get(user_id, [])[:limit])
    
    async def get_top_hts_details(self, user_id: int, limit: int = 5) -> List[Dict]:
        """
        Dapatkan detail TOP HTS untuk display
        
        Args:
            user_id: ID user
            limit: Jumlah (biasanya 5 untuk display)
            
        Returns:
            List detail HTS
        """
        top_ids = await self.get_top_hts(user_id, limit)
        result = []
        
        for i, hts_id in enumerate(top_ids, 1):
            hts = await self.get_hts(user_id, hts_id)
            if hts:
                # Hitung sisa hari
                remaining = await self.get_remaining_days(user_id, hts_id)
                
                # Format waktu
                if remaining and remaining > 0:
                    if remaining < 1:
                        time_left = f"{int(remaining * 24)} jam"
                    else:
                        time_left = f"{int(remaining)} hari"
                else:
                    time_left = "Expired"
                
                result.append({
                    'rank': i,
                    'hts_id': hts_id,
                    'bot_name': hts['bot_name'],
                    'role': hts['role'],
                    'chemistry': round(hts['chemistry_score'], 1),
                    'climax': hts['climax_count'],
                    'intimacy': hts['intimacy_level'],
                    'last_interaction': self._format_time_ago(hts['last_interaction']),
                    'remaining': time_left,
                    'score': round(hts.get('top_score', 0), 1)
                })
        
        return result
    
    # =========================================================================
    # UPDATE STATS
    # =========================================================================
    
    async def record_interaction(self, user_id: int, hts_id: str, 
                                 is_intim: bool = False,
                                 is_climax: bool = False):
        """
        Rekam interaksi dengan HTS
        
        Args:
            user_id: ID user
            hts_id: ID HTS
            is_intim: Apakah intim
            is_climax: Apakah climax
        """
        hts = await self.get_hts(user_id, hts_id)
        if not hts or hts['status'] != HTSStatus.ACTIVE:
            return
        
        hts['total_chats'] += 1
        hts['last_interaction'] = time.time()
        
        if is_intim:
            hts['total_intim'] += 1
        
        if is_climax:
            hts['climax_count'] += 1
            # Update chemistry sedikit naik
            hts['chemistry_score'] = min(100, hts['chemistry_score'] + 0.5)
        
        # Update TOP 10
        await self._update_top_hts(user_id)
    
    async def update_chemistry(self, user_id: int, hts_id: str, delta: float):
        """
        Update chemistry score
        
        Args:
            user_id: ID user
            hts_id: ID HTS
            delta: Perubahan skor
        """
        hts = await self.get_hts(user_id, hts_id)
        if not hts or hts['status'] != HTSStatus.ACTIVE:
            return
        
        hts['chemistry_score'] = max(0, min(100, hts['chemistry_score'] + delta))
        
        # Update TOP 10
        await self._update_top_hts(user_id)
    
    # =========================================================================
    # FORMATTING
    # =========================================================================
    
    async def format_hts_list(self, user_id: int, show_all: bool = False) -> str:
        """
        Format daftar HTS untuk ditampilkan
        
        Args:
            user_id: ID user
            show_all: Tampilkan semua atau hanya TOP
            
        Returns:
            String daftar HTS
        """
        if show_all:
            hts_list = await self.get_all_hts(user_id, include_expired=False)
            title = "📋 **SEMUA HTS**"
        else:
            hts_list = await self.get_top_hts_details(user_id, 10)
            title = "🏆 **TOP 10 HTS**"
        
        if not hts_list:
            return "Belum ada HTS. Selesaikan NON-PDKT sampai level 12 dan /close untuk mendapatkan HTS."
        
        lines = [title]
        lines.append("_(berdasarkan chemistry, climax & intimacy)_")
        lines.append("")
        
        for hts in hts_list:
            if show_all:
                # Format untuk list semua
                remaining = await self.get_remaining_days(user_id, hts['hts_id'])
                if remaining:
                    if remaining < 1:
                        time_left = f"{int(remaining * 24)} jam"
                    else:
                        time_left = f"{int(remaining)} hari"
                else:
                    time_left = "Expired"
                
                lines.append(
                    f"**{hts['bot_name']}** ({hts['role']})\n"
                    f"   Chemistry: {hts['chemistry']}% | Climax: {hts['climax']}\n"
                    f"   Sisa: {time_left} | Terakhir: {hts['last_interaction']}"
                )
            else:
                # Format untuk TOP list
                lines.append(
                    f"{hts['rank']}. **{hts['bot_name']}** ({hts['role']})\n"
                    f"   Chemistry: {hts['chemistry']}% | Climax: {hts['climax']}\n"
                    f"   Score: {hts['score']} | Sisa: {hts['remaining']}"
                )
            
            lines.append("")
        
        lines.append("💡 **Command:**")
        lines.append("• `/hts- [nomor]` - Panggil HTS untuk intim")
        lines.append("• `/htslist all` - Lihat semua HTS")
        
        return "\n".join(lines)
    
    async def format_hts_detail(self, user_id: int, hts_id: str) -> str:
        """
        Format detail HTS
        
        Args:
            user_id: ID user
            hts_id: ID HTS
            
        Returns:
            String detail
        """
        hts = await self.get_hts(user_id, hts_id)
        if not hts:
            return "HTS tidak ditemukan"
        
        created = datetime.fromtimestamp(hts['created_at']).strftime("%d %b %Y")
        remaining = await self.get_remaining_days(user_id, hts_id)
        
        if remaining and remaining > 0:
            if remaining < 1:
                time_left = f"{int(remaining * 24)} jam"
            else:
                time_left = f"{int(remaining)} hari"
            expiry_status = f"⏳ Sisa waktu: {time_left}"
        else:
            expiry_status = "❌ EXPIRED"
        
        lines = [
            f"💕 **{hts['bot_name']}** ({hts['role']})",
            f"Status: HTS",
            f"{expiry_status}",
            f"",
            f"📊 **Statistik:**",
            f"• Chemistry: {hts['chemistry_score']:.1f}%",
            f"• Climax: {hts['climax_count']}",
            f"• Intimacy Level: {hts['intimacy_level']}/12",
            f"• Total Intim: {hts['total_intim']}",
            f"• Total Chat: {hts['total_chats']}",
            f"",
            f"📅 Dibuat: {created}",
            f"🕒 Terakhir: {self._format_time_ago(hts['last_interaction'])}",
            f""
        ]
        
        return "\n".join(lines)
    
    def _format_time_ago(self, timestamp: float) -> str:
        """Format waktu yang lalu"""
        diff = time.time() - timestamp
        
        if diff < 60:
            return "baru saja"
        elif diff < 3600:
            return f"{int(diff / 60)} menit lalu"
        elif diff < 86400:
            return f"{int(diff / 3600)} jam lalu"
        elif diff < 604800:
            return f"{int(diff / 86400)} hari lalu"
        else:
            return f"{int(diff / 604800)} minggu lalu"
    
    # =========================================================================
    # CLEANUP EXPIRED
    # =========================================================================
    
    async def cleanup_expired(self, user_id: Optional[int] = None):
        """
        Bersihkan HTS yang expired (opsional)
        Sebenarnya tidak perlu dihapus, hanya ditandai expired
        
        Args:
            user_id: ID user (None untuk semua)
        """
        if user_id:
            users = [user_id]
        else:
            users = list(self.hts_relations.keys())
        
        expired_count = 0
        
        for uid in users:
            if uid in self.hts_relations:
                for hts_id in list(self.hts_relations[uid].keys()):
                    if await self.check_expiry(uid, hts_id) is False:
                        expired_count += 1
        
        logger.info(f"🧹 Cleaned up {expired_count} expired HTS")
        
        return expired_count


__all__ = ['HTSManager', 'HTSStatus']
