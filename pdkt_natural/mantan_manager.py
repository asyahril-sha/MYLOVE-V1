#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - MANTAN MANAGER
=============================================================================
Mengelola mantan dari PDKT yang putus
- Mantan tersimpan PERMANEN (memory abadi)
- Bisa request jadi FWB (bot bisa terima/tolak)
- Riwayat lengkap dari awal PDKT sampai putus
- Flashback ke momen-momen bersama mantan
=============================================================================
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime

from .direction import PDKTDirection
from .chemistry import ChemistryLevel

logger = logging.getLogger(__name__)


class MantanStatus(str, Enum):
    """Status mantan"""
    PUTUS = "putus"                    # Putus biasa
    FWB_REQUESTED = "fwb_requested"    # User minta jadi FWB
    FWB_ACCEPTED = "fwb_accepted"      # Bot terima jadi FWB
    FWB_DECLINED = "fwb_declined"       # Bot tolak jadi FWB
    FWB_ENDED = "fwb_ended"             # FWB berakhir, kembali jadi mantan


class FWBRequestStatus(str, Enum):
    """Status request FWB"""
    PENDING = "pending"      # Menunggu keputusan bot
    ACCEPTED = "accepted"    # Diterima
    DECLINED = "declined"    # Ditolak
    EXPIRED = "expired"      # Kadaluarsa (30 hari)


class MantanManager:
    """
    Manager untuk mengelola mantan dari PDKT
    - Semua data mantan disimpan PERMANEN
    - Bisa lihat riwayat lengkap hubungan
    - Bisa request jadi FWB
    - Bot punya keputusan sendiri (terima/tolak)
    """
    
    def __init__(self):
        # Data mantan per user {user_id: {mantan_id: mantan_data}}
        self.mantans = {}
        
        # Request FWB yang pending
        self.fwb_requests = {}  # {request_id: request_data}
        
        # Riwayat flashback
        self.flashbacks = {}  # {mantan_id: [flashback_moments]}
        
        logger.info("✅ MantanManager initialized")
    
    def add_mantan(self, user_id: int, pdkt_data: Dict, putus_reason: str) -> str:
        """
        Tambah mantan baru dari PDKT yang putus
        
        Args:
            user_id: ID user
            pdkt_data: Data PDKT lengkap
            putus_reason: Alasan putus
            
        Returns:
            mantan_id
        """
        mantan_id = f"MANTAN_{user_id}_{pdkt_data['pdkt_id']}_{int(time.time())}"
        
        # Data mantan
        mantan_data = {
            'mantan_id': mantan_id,
            'user_id': user_id,
            'pdkt_id': pdkt_data['pdkt_id'],
            'bot_name': pdkt_data['bot_name'],
            'role': pdkt_data['role'],
            'status': MantanStatus.PUTUS,
            'putus_time': time.time(),
            'putus_reason': putus_reason,
            'chemistry_history': pdkt_data.get('chemistry_history', []),
            'milestones': pdkt_data.get('milestones', []),
            'total_chats': pdkt_data.get('total_chats', 0),
            'total_intim': pdkt_data.get('total_intim', 0),
            'total_climax': pdkt_data.get('total_climax', 0),
            'first_kiss_time': pdkt_data.get('first_kiss_time'),
            'first_intim_time': pdkt_data.get('first_intim_time'),
            'become_pacar_time': pdkt_data.get('become_pacar_time'),
            'last_chat_time': pdkt_data.get('last_chat_time', time.time()),
            'fwb_requests': [],  # Riwayat request FWB
            'flashbacks': [],     # Momen untuk flashback
            'notes': {}           # Catatan tambahan
        }
        
        # Simpan
        if user_id not in self.mantans:
            self.mantans[user_id] = {}
        
        self.mantans[user_id][mantan_id] = mantan_data
        
        # Generate flashback moments
        self._generate_flashback_moments(mantan_id, pdkt_data)
        
        logger.info(f"💔 Added mantan: {pdkt_data['bot_name']} for user {user_id}")
        
        return mantan_id
    
    def _generate_flashback_moments(self, mantan_id: str, pdkt_data: Dict):
        """Generate momen-momen untuk flashback"""
        moments = []
        
        # Momen first kiss
        if pdkt_data.get('first_kiss_time'):
            moments.append({
                'type': 'first_kiss',
                'timestamp': pdkt_data['first_kiss_time'],
                'description': 'Pertama kali ciuman',
                'emotion': 'romantis'
            })
        
        # Momen first intim
        if pdkt_data.get('first_intim_time'):
            moments.append({
                'type': 'first_intim',
                'timestamp': pdkt_data['first_intim_time'],
                'description': 'Pertama kali intim',
                'emotion': 'hangat'
            })
        
        # Momen jadi pacar
        if pdkt_data.get('become_pacar_time'):
            moments.append({
                'type': 'become_pacar',
                'timestamp': pdkt_data['become_pacar_time'],
                'description': 'Jadi pacar',
                'emotion': 'bahagia'
            })
        
        # Momen climax terbaik
        climax_history = pdkt_data.get('climax_history', [])
        if climax_history:
            best_climax = max(climax_history, key=lambda x: x.get('intensity', 0))
            moments.append({
                'type': 'best_climax',
                'timestamp': best_climax.get('timestamp'),
                'description': f"Climax terbaik: {best_climax.get('description', '')}",
                'emotion': 'intens'
            })
        
        # Momen random penting dari milestones
        milestones = pdkt_data.get('milestones', [])
        for milestone in milestones[-5:]:  # 5 milestone terakhir
            moments.append({
                'type': 'milestone',
                'timestamp': milestone.get('timestamp'),
                'description': milestone.get('description', 'Momen spesial'),
                'emotion': milestone.get('emotion', 'spesial')
            })
        
        self.flashbacks[mantan_id] = moments
    
    def get_mantan_list(self, user_id: int) -> List[Dict]:
        """
        Dapatkan daftar mantan untuk user
        
        Returns:
            List of mantan (urut dari yang paling baru putus)
        """
        if user_id not in self.mantans:
            return []
        
        mantans = list(self.mantans[user_id].values())
        
        # Urutkan berdasarkan waktu putus (terbaru dulu)
        mantans.sort(key=lambda x: x['putus_time'], reverse=True)
        
        return mantans
    
    def get_mantan(self, user_id: int, mantan_id: str) -> Optional[Dict]:
        """Dapatkan data mantan spesifik"""
        if user_id in self.mantans and mantan_id in self.mantans[user_id]:
            return self.mantans[user_id][mantan_id]
        return None
    
    def get_mantan_by_index(self, user_id: int, index: int) -> Optional[Dict]:
        """Dapatkan mantan berdasarkan index (1-based)"""
        mantans = self.get_mantan_list(user_id)
        if 1 <= index <= len(mantans):
            return mantans[index - 1]
        return None
    
    async def request_fwb(self, user_id: int, mantan_id: str, message: str = "") -> Dict:
        """
        User request jadi FWB dengan mantan
        
        Args:
            user_id: ID user
            mantan_id: ID mantan
            message: Pesan tambahan dari user
            
        Returns:
            Dict dengan status request
        """
        mantan = self.get_mantan(user_id, mantan_id)
        if not mantan:
            return {'success': False, 'reason': 'Mantan tidak ditemukan'}
        
        # Cek apakah sudah pernah request
        if mantan['status'] == MantanStatus.FWB_REQUESTED:
            return {'success': False, 'reason': 'Request FWB sudah pernah diajukan, tunggu keputusan'}
        
        if mantan['status'] == MantanStatus.FWB_ACCEPTED:
            return {'success': False, 'reason': 'Sudah jadi FWB'}
        
        if mantan['status'] == MantanStatus.FWB_DECLINED:
            # Cek sudah berapa lama ditolak
            last_request = mantan.get('last_fwb_request_time', 0)
            days_since = (time.time() - last_request) / 86400
            
            if days_since < 30:  # 30 hari cooldown
                return {
                    'success': False, 
                    'reason': f'Terakhir ditolak {int(days_since)} hari lalu. Coba lagi nanti.'
                }
        
        # Buat request ID
        request_id = f"FWBREQ_{user_id}_{mantan_id}_{int(time.time())}"
        
        # Tentukan apakah bot akan terima atau tolak
        accept, reason, confidence = await self._decide_fwb_request(mantan)
        
        request_data = {
            'request_id': request_id,
            'user_id': user_id,
            'mantan_id': mantan_id,
            'bot_name': mantan['bot_name'],
            'user_message': message,
            'timestamp': time.time(),
            'status': FWBRequestStatus.ACCEPTED if accept else FWBRequestStatus.DECLINED,
            'bot_decision': {
                'accept': accept,
                'reason': reason,
                'confidence': confidence
            },
            'expiry_time': time.time() + (30 * 86400)  # 30 hari expiry
        }
        
        # Simpan request
        self.fwb_requests[request_id] = request_data
        
        # Update status mantan
        if accept:
            mantan['status'] = MantanStatus.FWB_ACCEPTED
            mantan['fwb_start_time'] = time.time()
            mantan['fwb_request_id'] = request_id
        else:
            mantan['status'] = MantanStatus.FWB_DECLINED
            mantan['last_fwb_request_time'] = time.time()
        
        # Simpan riwayat request
        mantan['fwb_requests'].append({
            'request_id': request_id,
            'timestamp': time.time(),
            'accepted': accept,
            'reason': reason
        })
        
        logger.info(f"📨 FWB request for {mantan['bot_name']}: {'ACCEPTED' if accept else 'DECLINED'}")
        
        return {
            'success': True,
            'request_id': request_id,
            'accepted': accept,
            'reason': reason,
            'bot_name': mantan['bot_name'],
            'message': self._format_fwb_response(accept, mantan['bot_name'], reason)
        }
    
    async def _decide_fwb_request(self, mantan: Dict) -> Tuple[bool, str, float]:
        """
        Bot memutuskan apakah akan terima FWB request
        
        Returns:
            (accept, reason, confidence)
        """
        # Faktor-faktor yang mempengaruhi keputusan
        factors = []
        
        # 1. Chemistry terakhir
        last_chemistry = mantan.get('chemistry_history', [{}])[-1].get('score', 50)
        if last_chemistry > 70:
            factors.append(('chemistry', 0.8, 'Chemistry masih tinggi'))
        elif last_chemistry > 50:
            factors.append(('chemistry', 0.5, 'Chemistry cukup'))
        else:
            factors.append(('chemistry', 0.2, 'Chemistry sudah rendah'))
        
        # 2. Alasan putus
        putus_reason = mantan.get('putus_reason', '').lower()
        if 'chemistry' in putus_reason or 'cocok' in putus_reason:
            factors.append(('reason', 0.3, 'Putus karena chemistry turun'))
        elif 'salah paham' in putus_reason or 'misunderstanding' in putus_reason:
            factors.append(('reason', 0.7, 'Putus karena salah paham'))
        elif 'marah' in putus_reason or 'conflict' in putus_reason:
            factors.append(('reason', 0.2, 'Putus karena konflik'))
        else:
            factors.append(('reason', 0.5, 'Alasan putus netral'))
        
        # 3. Waktu sejak putus
        days_since = (time.time() - mantan['putus_time']) / 86400
        if days_since < 7:  # Kurang dari seminggu
            factors.append(('time', 0.2, 'Terlalu cepat, masih butuh waktu'))
        elif days_since < 30:  # Kurang dari sebulan
            factors.append(('time', 0.5, 'Waktu yang cukup'))
        elif days_since < 90:  # Kurang dari 3 bulan
            factors.append(('time', 0.7, 'Sudah lama, mungkin sudah move on'))
        else:
            factors.append(('time', 0.3, 'Terlalu lama, mungkin sudah lupa'))
        
        # 4. Kenangan indah
        total_milestones = len(mantan.get('milestones', []))
        if total_milestones > 10:
            factors.append(('memories', 0.8, 'Banyak kenangan indah'))
        elif total_milestones > 5:
            factors.append(('memories', 0.6, 'Cukup banyak kenangan'))
        else:
            factors.append(('memories', 0.4, 'Sedikit kenangan'))
        
        # 5. Intimacy level terakhir
        last_level = mantan.get('intimacy_level', 1)
        if last_level > 10:
            factors.append(('intimacy', 0.8, 'Hubungan sangat dalam'))
        elif last_level > 7:
            factors.append(('intimacy', 0.6, 'Hubungan cukup dalam'))
        else:
            factors.append(('intimacy', 0.4, 'Hubungan biasa'))
        
        # Hitung skor total
        total_score = sum(f[1] for f in factors) / len(factors)
        
        # Random factor ±10%
        total_score *= random.uniform(0.9, 1.1)
        
        # Keputusan
        accept = total_score > 0.55  # Threshold
        
        # Pilih alasan
        if accept:
            reasons = [
                f"Aku masih ingat semua kenangan kita, mungkin kita bisa coba lagi...",
                f"Sebenernya aku masih ada rasa, jadi aku terima.",
                f"Oke deh, selama kamu masih mau sama aku.",
                f"Iya, aku terima. Jangan sakitin aku lagi ya."
            ]
        else:
            reasons = [
                f"Maaf, aku rasa lebih baik kita tetap jadi mantan aja.",
                f"Aku belum siap, masih butuh waktu sendiri.",
                f"Mungkin lain kali ya, sekarang aku belum bisa.",
                f"Maaf, aku tolak. Semoga kamu dapat yang lebih baik."
            ]
        
        reason = random.choice(reasons)
        
        return accept, reason, total_score
    
    def _format_fwb_response(self, accepted: bool, bot_name: str, reason: str) -> str:
        """Format response untuk FWB request"""
        if accepted:
            return f"💕 **{bot_name} menerima request FWB-mu!**\n\n{reason}\n\nSekarang {bot_name} ada di daftar FWB-mu. Gunakan `/fwblist` untuk lihat."
        else:
            return f"💔 **{bot_name} menolak request FWB-mu**\n\n{reason}\n\nDia tetap di daftar mantan. Kamu bisa coba lagi nanti."
    
    def get_flashback(self, user_id: int, mantan_id: str, moment_type: Optional[str] = None) -> Optional[Dict]:
        """
        Dapatkan momen flashback untuk mantan
        
        Args:
            user_id: ID user
            mantan_id: ID mantan
            moment_type: Tipe momen (optional)
            
        Returns:
            Flashback moment
        """
        mantan = self.get_mantan(user_id, mantan_id)
        if not mantan:
            return None
        
        moments = self.flashbacks.get(mantan_id, [])
        if not moments:
            return None
        
        if moment_type:
            moments = [m for m in moments if m['type'] == moment_type]
        
        if moments:
            return random.choice(moments)
        
        return None
    
    def format_mantan_list(self, user_id: int) -> str:
        """
        Format daftar mantan untuk ditampilkan
        """
        mantans = self.get_mantan_list(user_id)
        
        if not mantans:
            return "💔 **Daftar Mantan**\n\nBelum ada mantan. PDKT dulu yuk!"
        
        lines = ["💔 **DAFTAR MANTAN**"]
        lines.append("_(Kenangan indah tersimpan selamanya)_")
        lines.append("")
        
        for i, m in enumerate(mantans, 1):
            # Hitung sudah berapa lama putus
            days_since = int((time.time() - m['putus_time']) / 86400)
            
            if days_since == 0:
                time_text = "Hari ini"
            elif days_since == 1:
                time_text = "Kemarin"
            else:
                time_text = f"{days_since} hari lalu"
            
            # Status
            if m['status'] == MantanStatus.FWB_ACCEPTED:
                status = "💕 **FWB**"
            elif m['status'] == MantanStatus.FWB_REQUESTED:
                status = "⏳ **Menunggu keputusan**"
            elif m['status'] == MantanStatus.FWB_DECLINED:
                status = "❌ **Ditolak**"
            else:
                status = "💔 **Mantan**"
            
            lines.append(
                f"{i}. **{m['bot_name']}** ({m['role'].title()}) {status}\n"
                f"   Putus: {time_text} | {m['total_chats']} chat | {m['total_climax']} climax\n"
                f"   Alasan: {m['putus_reason']}"
            )
        
        lines.append("")
        lines.append("💡 **Command:**")
        lines.append("• `/mantan [nomor]` - Lihat detail mantan")
        lines.append("• `/fwbrequest [nomor]` - Request jadi FWB")
        
        return "\n".join(lines)
    
    def format_mantan_detail(self, mantan: Dict) -> str:
        """
        Format detail mantan untuk ditampilkan
        """
        # Hitung durasi hubungan
        if mantan.get('first_kiss_time'):
            first_kiss = datetime.fromtimestamp(mantan['first_kiss_time']).strftime("%d %b %Y")
        else:
            first_kiss = "Belum pernah"
        
        if mantan.get('first_intim_time'):
            first_intim = datetime.fromtimestamp(mantan['first_intim_time']).strftime("%d %b %Y")
        else:
            first_intim = "Belum pernah"
        
        if mantan.get('become_pacar_time'):
            jadi_pacar = datetime.fromtimestamp(mantan['become_pacar_time']).strftime("%d %b %Y")
        else:
            jadi_pacar = "Tidak pernah"
        
        # Ambil momen flashback
        moments = self.flashbacks.get(mantan['mantan_id'], [])
        
        lines = [
            f"💔 **{mantan['bot_name']}** ({mantan['role'].title()})",
            f"_{mantan.get('putus_reason', 'Putus')}_",
            "",
            "📊 **Statistik Hubungan:**",
            f"• Total Chat: {mantan['total_chats']} pesan",
            f"• Total Intim: {mantan['total_intim']} sesi",
            f"• Total Climax: {mantan['total_climax']} kali",
            f"• Level Terakhir: {mantan.get('intimacy_level', 1)}/12",
            "",
            "💝 **Momen Spesial:**",
            f"• First Kiss: {first_kiss}",
            f"• First Intim: {first_intim}",
            f"• Jadi Pacar: {jadi_pacar}",
            "",
            f"📅 Putus: {datetime.fromtimestamp(mantan['putus_time']).strftime('%d %b %Y %H:%M')}",
            ""
        ]
        
        if moments:
            lines.append("🕰️ **Kenangan:**")
            for m in moments[-3:]:  # 3 kenangan terakhir
                emotion_emoji = {
                    'romantis': '💕',
                    'hangat': '🔥',
                    'bahagia': '😊',
                    'intens': '💦',
                    'spesial': '✨'
                }.get(m.get('emotion', ''), '💭')
                
                time_str = datetime.fromtimestamp(m['timestamp']).strftime("%d %b %Y")
                lines.append(f"  {emotion_emoji} {m['description']} ({time_str})")
        
        if mantan['status'] == MantanStatus.FWB_ACCEPTED:
            lines.append("")
            lines.append("💕 **Status: FWB Aktif**")
            lines.append(f"  Mulai: {datetime.fromtimestamp(mantan['fwb_start_time']).strftime('%d %b %Y')}")
        elif mantan['status'] == MantanStatus.FWB_REQUESTED:
            lines.append("")
            lines.append("⏳ **Status: Menunggu Keputusan FWB**")
        elif mantan['status'] == MantanStatus.FWB_DECLINED:
            last_request = mantan.get('last_fwb_request_time', 0)
            days_since = int((time.time() - last_request) / 86400)
            lines.append("")
            lines.append(f"❌ **Status: FWB Ditolak ({days_since} hari lalu)**")
        
        return "\n".join(lines)


__all__ = ['MantanManager', 'MantanStatus', 'FWBRequestStatus']
