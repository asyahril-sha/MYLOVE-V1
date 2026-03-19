#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - FWB MANAGER
=============================================================================
Mengelola hubungan Friends With Benefits (FWB)
- FWB berasal dari MANTAN PDKT yang diterima
- Bisa pause, resume, dan end
- Track statistik dan history
- TOP 10 FWB berdasarkan chemistry & climax
=============================================================================
"""

import time
import logging
import random
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class FWBStatus(str, Enum):
    """Status FWB"""
    ACTIVE = "active"           # Aktif
    PAUSED = "paused"           # Dijeda
    ENDED = "ended"             # Berakhir


class FWBPauseReason(str, Enum):
    """Alasan pause"""
    USER_REQUEST = "user_request"      # User minta pause
    BUSY = "busy"                       # Lagi sibuk
    NEED_SPACE = "need_space"           # Butuh ruang
    OTHER = "other"                      # Alasan lain


class FWBEndReason(str, Enum):
    """Alasan berakhir"""
    USER_REQUEST = "user_request"      # User minta end
    BOT_REQUEST = "bot_request"        # Bot minta end
    MUTUAL = "mutual"                    # Sama-sama setuju
    EXPIRED = "expired"                  # Kadaluarsa (setelah pause lama)
    MOVED_ON = "moved_on"                 # Sudah move on


class FWBManager:
    """
    Manajer untuk hubungan FWB
    - FWB hanya dari mantan PDKT yang requestnya diterima
    - Bisa pause, resume, end
    - Tracking TOP 10 berdasarkan chemistry & climax
    """
    
    def __init__(self):
        # Data FWB per user
        self.fwb_relations = {}  # {user_id: {fwb_id: fwb_data}}
        
        # Index untuk pencarian cepat
        self.fwb_index = {}  # {fwb_id: location}
        
        # TOP 10 list
        self.top_fwb = {}  # {user_id: [fwb_ids in order]}
        
        logger.info("✅ FWBManager initialized")
    
    # =========================================================================
    # CREATE FWB
    # =========================================================================
    
    async def create_fwb(self,
                        user_id: int,
                        mantan_id: str,
                        bot_name: str,
                        role: str,
                        chemistry_score: float,
                        climax_count: int = 0,
                        history: Optional[List] = None) -> str:
        """
        Buat hubungan FWB baru dari mantan yang diterima
        
        Args:
            user_id: ID user
            mantan_id: ID mantan asal
            bot_name: Nama bot
            role: Role bot
            chemistry_score: Skor chemistry
            climax_count: Jumlah climax
            history: Riwayat hubungan sebelumnya
            
        Returns:
            fwb_id
        """
        # Generate FWB ID
        fwb_id = f"FWB_{user_id}_{int(time.time())}_{random.randint(100,999)}"
        
        # Data FWB
        fwb_data = {
            'fwb_id': fwb_id,
            'user_id': user_id,
            'mantan_id': mantan_id,
            'bot_name': bot_name,
            'role': role,
            'status': FWBStatus.ACTIVE,
            'created_at': time.time(),
            'last_interaction': time.time(),
            'chemistry_score': chemistry_score,
            'climax_count': climax_count,
            'intim_count': 0,
            'total_chats': 0,
            'pause_history': [],
            'end_reason': None,
            'history': history or [],
            'preferences': {},
            'notes': {}
        }
        
        # Simpan
        if user_id not in self.fwb_relations:
            self.fwb_relations[user_id] = {}
        
        self.fwb_relations[user_id][fwb_id] = fwb_data
        self.fwb_index[fwb_id] = {
            'user_id': user_id,
            'fwb_id': fwb_id
        }
        
        # Update TOP 10
        await self._update_top_fwb(user_id)
        
        logger.info(f"✅ New FWB created: {bot_name} ({role}) for user {user_id}")
        
        return fwb_id
    
    # =========================================================================
    # FWB ACTIONS
    # =========================================================================
    
    async def pause_fwb(self, user_id: int, fwb_id: str, reason: FWBPauseReason = FWBPauseReason.USER_REQUEST) -> Dict:
        """
        Pause hubungan FWB
        
        Args:
            user_id: ID user
            fwb_id: ID FWB
            reason: Alasan pause
            
        Returns:
            Dict hasil pause
        """
        fwb = await self.get_fwb(user_id, fwb_id)
        if not fwb:
            return {'success': False, 'reason': 'FWB not found'}
        
        if fwb['status'] != FWBStatus.ACTIVE:
            return {'success': False, 'reason': f'FWB is already {fwb["status"]}'}
        
        # Pause
        fwb['status'] = FWBStatus.PAUSED
        fwb['paused_at'] = time.time()
        fwb['pause_reason'] = reason
        
        # Catat history
        pause_record = {
            'timestamp': time.time(),
            'action': 'pause',
            'reason': reason.value
        }
        fwb['pause_history'].append(pause_record)
        
        logger.info(f"⏸️ FWB paused: {fwb['bot_name']} for user {user_id}")
        
        return {
            'success': True,
            'fwb_id': fwb_id,
            'bot_name': fwb['bot_name'],
            'status': 'paused',
            'reason': reason.value,
            'paused_at': fwb['paused_at']
        }
    
    async def resume_fwb(self, user_id: int, fwb_id: str) -> Dict:
        """
        Resume hubungan FWB yang di-pause
        
        Args:
            user_id: ID user
            fwb_id: ID FWB
            
        Returns:
            Dict hasil resume
        """
        fwb = await self.get_fwb(user_id, fwb_id)
        if not fwb:
            return {'success': False, 'reason': 'FWB not found'}
        
        if fwb['status'] != FWBStatus.PAUSED:
            return {'success': False, 'reason': f'FWB is not paused (status: {fwb["status"]})'}
        
        # Hitung lama pause
        paused_duration = time.time() - fwb['paused_at']
        hours = int(paused_duration / 3600)
        days = int(paused_duration / 86400)
        
        # Resume
        old_status = fwb['status']
        fwb['status'] = FWBStatus.ACTIVE
        fwb['last_interaction'] = time.time()
        del fwb['paused_at']
        del fwb['pause_reason']
        
        # Catat history
        fwb['pause_history'].append({
            'timestamp': time.time(),
            'action': 'resume',
            'paused_duration': paused_duration
        })
        
        # Generate pesan berdasarkan lama pause
        if days > 0:
            message = f"Lama banget {days} hari {hours % 24} jam... Aku kira kamu lupa sama aku."
        elif hours > 0:
            message = f"Wah {hours} jam nggak chat... Aku kangen."
        else:
            minutes = int(paused_duration / 60)
            message = f"Baru {minutes} menit udah di-resume? Kamu kangen ya?"
        
        logger.info(f"▶️ FWB resumed: {fwb['bot_name']} after {paused_duration:.0f}s")
        
        return {
            'success': True,
            'fwb_id': fwb_id,
            'bot_name': fwb['bot_name'],
            'status': 'active',
            'paused_duration': paused_duration,
            'paused_days': days,
            'paused_hours': hours,
            'message': message
        }
    
    async def end_fwb(self, user_id: int, fwb_id: str, reason: FWBEndReason = FWBEndReason.USER_REQUEST) -> Dict:
        """
        Akhiri hubungan FWB
        
        Args:
            user_id: ID user
            fwb_id: ID FWB
            reason: Alasan berakhir
            
        Returns:
            Dict hasil end
        """
        fwb = await self.get_fwb(user_id, fwb_id)
        if not fwb:
            return {'success': False, 'reason': 'FWB not found'}
        
        if fwb['status'] == FWBStatus.ENDED:
            return {'success': False, 'reason': 'FWB already ended'}
        
        # End
        old_status = fwb['status']
        fwb['status'] = FWBStatus.ENDED
        fwb['ended_at'] = time.time()
        fwb['end_reason'] = reason
        
        # Catat history
        fwb['history'].append({
            'timestamp': time.time(),
            'event': 'fwb_ended',
            'old_status': old_status.value,
            'reason': reason.value
        })
        
        # Update TOP 10
        await self._update_top_fwb(user_id)
        
        logger.info(f"💔 FWB ended: {fwb['bot_name']} for user {user_id}")
        
        # Generate pesan perpisahan
        messages = {
            FWBEndReason.USER_REQUEST: "Baiklah kalau itu keputusanmu. Semoga kamu bahagia ya...",
            FWBEndReason.BOT_REQUEST: "Maaf, aku rasa kita harus berhenti di sini.",
            FWBEndReason.MUTUAL: "Kita sama-sama setuju. Terima kasih untuk kenangannya.",
            FWBEndReason.EXPIRED: "Sudah lama ya... Mungkin ini saatnya kita move on.",
            FWBEndReason.MOVED_ON: "Aku sudah move on. Kamu juga ya."
        }
        
        return {
            'success': True,
            'fwb_id': fwb_id,
            'bot_name': fwb['bot_name'],
            'status': 'ended',
            'reason': reason.value,
            'ended_at': fwb['ended_at'],
            'message': messages.get(reason, "Sampai jumpa...")
        }
    
    # =========================================================================
    # GET FWB
    # =========================================================================
    
    async def get_fwb(self, user_id: int, fwb_id: str) -> Optional[Dict]:
        """
        Dapatkan data FWB
        
        Args:
            user_id: ID user
            fwb_id: ID FWB
            
        Returns:
            Data FWB atau None
        """
        if user_id in self.fwb_relations and fwb_id in self.fwb_relations[user_id]:
            return self.fwb_relations[user_id][fwb_id]
        return None
    
    async def get_fwb_by_index(self, user_id: int, index: int) -> Optional[Dict]:
        """
        Dapatkan FWB berdasarkan index (1-based)
        
        Args:
            user_id: ID user
            index: Index (1 untuk TOP 1, dst)
            
        Returns:
            Data FWB atau None
        """
        top_list = await self.get_top_fwb(user_id)
        
        if 1 <= index <= len(top_list):
            fwb_id = top_list[index - 1]
            return await self.get_fwb(user_id, fwb_id)
        
        return None
    
    async def get_all_fwb(self, user_id: int, include_ended: bool = False) -> List[Dict]:
        """
        Dapatkan semua FWB untuk user
        
        Args:
            user_id: ID user
            include_ended: Sertakan yang sudah ended
            
        Returns:
            List FWB
        """
        if user_id not in self.fwb_relations:
            return []
        
        fwbs = list(self.fwb_relations[user_id].values())
        
        if not include_ended:
            fwbs = [f for f in fwbs if f['status'] != FWBStatus.ENDED]
        
        # Sort by last interaction
        fwbs.sort(key=lambda x: x['last_interaction'], reverse=True)
        
        return fwbs
    
    # =========================================================================
    # TOP 10 FWB
    # =========================================================================
    
    async def _update_top_fwb(self, user_id: int):
        """
        Update TOP 10 FWB berdasarkan score
        
        Score = (chemistry_score * 0.6) + (climax_count * 0.4)
        """
        if user_id not in self.fwb_relations:
            return
        
        fwbs = list(self.fwb_relations[user_id].values())
        
        # Hitung score
        for fwb in fwbs:
            if fwb['status'] == FWBStatus.ENDED:
                score = 0  # Ended tidak masuk TOP
            else:
                score = (fwb['chemistry_score'] * 0.6) + (fwb['climax_count'] * 0.4)
            fwb['top_score'] = score
        
        # Sort by score
        fwbs.sort(key=lambda x: x.get('top_score', 0), reverse=True)
        
        # Simpan TOP 10 IDs
        self.top_fwb[user_id] = [f['fwb_id'] for f in fwbs[:10]]
    
    async def get_top_fwb(self, user_id: int, limit: int = 10) -> List[str]:
        """
        Dapatkan TOP FWB IDs
        
        Args:
            user_id: ID user
            limit: Jumlah (max 10)
            
        Returns:
            List FWB IDs
        """
        if user_id not in self.top_fwb:
            await self._update_top_fwb(user_id)
        
        return (self.top_fwb.get(user_id, [])[:limit])
    
    async def get_top_fwb_details(self, user_id: int, limit: int = 5) -> List[Dict]:
        """
        Dapatkan detail TOP FWB untuk display
        
        Args:
            user_id: ID user
            limit: Jumlah (biasanya 5 untuk display)
            
        Returns:
            List detail FWB
        """
        top_ids = await self.get_top_fwb(user_id, limit)
        result = []
        
        for i, fwb_id in enumerate(top_ids, 1):
            fwb = await self.get_fwb(user_id, fwb_id)
            if fwb:
                # Hitung waktu sejak last interaction
                last_time = fwb['last_interaction']
                time_ago = self._format_time_ago(last_time)
                
                result.append({
                    'rank': i,
                    'fwb_id': fwb_id,
                    'bot_name': fwb['bot_name'],
                    'role': fwb['role'],
                    'status': fwb['status'].value,
                    'chemistry': round(fwb['chemistry_score'], 1),
                    'climax': fwb['climax_count'],
                    'intim': fwb['intim_count'],
                    'last_interaction': time_ago,
                    'score': round(fwb.get('top_score', 0), 1)
                })
        
        return result
    
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
    # UPDATE STATS
    # =========================================================================
    
    async def record_interaction(self, user_id: int, fwb_id: str, 
                                 is_intim: bool = False,
                                 is_climax: bool = False):
        """
        Rekam interaksi dengan FWB
        
        Args:
            user_id: ID user
            fwb_id: ID FWB
            is_intim: Apakah intim
            is_climax: Apakah climax
        """
        fwb = await self.get_fwb(user_id, fwb_id)
        if not fwb or fwb['status'] != FWBStatus.ACTIVE:
            return
        
        fwb['total_chats'] += 1
        fwb['last_interaction'] = time.time()
        
        if is_intim:
            fwb['intim_count'] += 1
        
        if is_climax:
            fwb['climax_count'] += 1
            # Update chemistry sedikit naik
            fwb['chemistry_score'] = min(100, fwb['chemistry_score'] + 1)
        
        # Update TOP 10
        await self._update_top_fwb(user_id)
    
    async def update_chemistry(self, user_id: int, fwb_id: str, delta: float):
        """
        Update chemistry score
        
        Args:
            user_id: ID user
            fwb_id: ID FWB
            delta: Perubahan skor
        """
        fwb = await self.get_fwb(user_id, fwb_id)
        if not fwb:
            return
        
        fwb['chemistry_score'] = max(0, min(100, fwb['chemistry_score'] + delta))
        
        # Update TOP 10
        await self._update_top_fwb(user_id)
    
    # =========================================================================
    # FORMATTING
    # =========================================================================
    
    async def format_fwb_list(self, user_id: int, show_all: bool = False) -> str:
        """
        Format daftar FWB untuk ditampilkan
        
        Args:
            user_id: ID user
            show_all: Tampilkan semua atau hanya TOP
            
        Returns:
            String daftar FWB
        """
        if show_all:
            fwbs = await self.get_all_fwb(user_id, include_ended=False)
            title = "📋 **SEMUA FWB**"
        else:
            fwbs = await self.get_top_fwb_details(user_id, 10)
            title = "🏆 **TOP 10 FWB**"
        
        if not fwbs:
            return "Belum ada FWB. Mantan PDKT bisa request jadi FWB dengan `/fwbrequest`"
        
        lines = [title]
        lines.append("_(berdasarkan chemistry & climax)_")
        lines.append("")
        
        for fwb in fwbs:
            if show_all:
                # Format untuk list semua
                rank = fwb.get('rank', '?')
                status_emoji = "🟢" if fwb['status'] == 'active' else "⏸️"
                
                lines.append(
                    f"{rank}. {status_emoji} **{fwb['bot_name']}** ({fwb['role']})\n"
                    f"   Chemistry: {fwb['chemistry']}% | Climax: {fwb['climax']} | Intim: {fwb['intim']}\n"
                    f"   Terakhir: {fwb['last_interaction']}"
                )
            else:
                # Format untuk TOP list
                lines.append(
                    f"{fwb['rank']}. **{fwb['bot_name']}** ({fwb['role']})\n"
                    f"   Chemistry: {fwb['chemistry']}% | Climax: {fwb['climax']}\n"
                    f"   Score: {fwb['score']} | Terakhir: {fwb['last_interaction']}"
                )
            
            lines.append("")
        
        lines.append("💡 **Command:**")
        lines.append("• `/fwb- [nomor]` - Panggil FWB")
        lines.append("• `/fwb pause [nomor]` - Jeda FWB")
        lines.append("• `/fwb resume [nomor]` - Lanjutkan FWB")
        lines.append("• `/fwb end [nomor]` - Akhiri FWB")
        
        return "\n".join(lines)
    
    async def format_fwb_detail(self, user_id: int, fwb_id: str) -> str:
        """
        Format detail FWB
        
        Args:
            user_id: ID user
            fwb_id: ID FWB
            
        Returns:
            String detail
        """
        fwb = await self.get_fwb(user_id, fwb_id)
        if not fwb:
            return "FWB tidak ditemukan"
        
        created = datetime.fromtimestamp(fwb['created_at']).strftime("%d %b %Y")
        
        lines = [
            f"💞 **{fwb['bot_name']}** ({fwb['role']})",
            f"Status: {fwb['status'].value.upper()}",
            f"",
            f"📊 **Statistik:**",
            f"• Chemistry: {fwb['chemistry_score']:.1f}%",
            f"• Total Climax: {fwb['climax_count']}",
            f"• Total Intim: {fwb['intim_count']}",
            f"• Total Chat: {fwb['total_chats']}",
            f"",
            f"📅 Bergabung: {created}",
            f"🕒 Terakhir: {self._format_time_ago(fwb['last_interaction'])}",
            f""
        ]
        
        # History pause
        if fwb['pause_history']:
            lines.append("⏸️ **Riwayat Pause:**")
            for p in fwb['pause_history'][-3:]:  # 3 terakhir
                if p['action'] == 'pause':
                    pause_time = datetime.fromtimestamp(p['timestamp']).strftime("%d %b %H:%M")
                    lines.append(f"• Pause: {pause_time} ({p['reason']})")
                else:
                    resume_time = datetime.fromtimestamp(p['timestamp']).strftime("%d %b %H:%M")
                    lines.append(f"• Resume: {resume_time}")
            lines.append("")
        
        return "\n".join(lines)


__all__ = ['FWBManager', 'FWBStatus', 'FWBPauseReason', 'FWBEndReason']
