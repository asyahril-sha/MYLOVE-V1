#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - PDKT LIST FORMATTER
=============================================================================
Formatting untuk menampilkan daftar PDKT
- List semua PDKT aktif
- Detail per PDKT (chemistry, arah, mood)
- Progress bar leveling
- Inner thoughts preview
=============================================================================
"""

import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .direction import PDKTDirection
from .chemistry import ChemistryLevel

logger = logging.getLogger(__name__)


class PDKTListFormatter:
    """
    Formatter untuk menampilkan daftar PDKT
    Membuat tampilan yang informatif dan menarik
    """
    
    def __init__(self):
        logger.info("✅ PDKTListFormatter initialized")
    
    def format_pdkt_list(self, pdkt_list: List[Dict], show_all: bool = False) -> str:
        """
        Format daftar PDKT untuk ditampilkan
        
        Args:
            pdkt_list: List of PDKT data
            show_all: Tampilkan semua atau hanya ringkasan
            
        Returns:
            Formatted string
        """
        if not pdkt_list:
            return "📋 **Daftar PDKT**\n\nBelum ada PDKT aktif. Mulai dengan `/pdkt [role]` atau `/pdktrandom`"
        
        lines = ["📋 **DAFTAR PDKT**"]
        
        if show_all:
            lines.append("_(menampilkan semua PDKT)_")
        else:
            lines.append("_(ringkasan, gunakan `/pdktdetail [id]` untuk detail)_")
        
        lines.append("")
        
        for i, pdkt in enumerate(pdkt_list, 1):
            # Status emoji
            if pdkt.get('is_paused', False):
                status_emoji = "⏸️"
                status_text = "PAUSED"
            else:
                status_emoji = "▶️"
                status_text = "AKTIF"
            
            # Arah emoji
            direction = pdkt.get('direction', PDKTDirection.USER_KE_BOT)
            if direction == PDKTDirection.BOT_KE_USER:
                direction_emoji = "🔥"
                direction_text = "Dia suka kamu"
            elif direction == PDKTDirection.USER_KE_BOT:
                direction_emoji = "💘"
                direction_text = "Kamu suka dia"
            elif direction == PDKTDirection.TIMBAL_BALIK:
                direction_emoji = "💕"
                direction_text = "Saling suka"
            else:
                direction_emoji = "🤔"
                direction_text = "Bingung"
            
            # Chemistry vibe
            chemistry = pdkt.get('chemistry_level', ChemistryLevel.BIASA)
            chemistry_emoji = self._get_chemistry_emoji(chemistry)
            
            # Waktu terakhir chat
            last_time = pdkt.get('last_interaction', 0)
            time_ago = self._format_time_ago(last_time)
            
            lines.append(
                f"{i}. {status_emoji} **{pdkt.get('bot_name', 'Unknown')}** ({pdkt.get('role', 'unknown').title()})\n"
                f"   {direction_emoji} {direction_text} | {chemistry_emoji} {chemistry.value.title()}\n"
                f"   Level {pdkt.get('level', 1)}/12 | {time_ago}\n"
                f"   Status: {status_text}"
            )
            
            # Tampilkan hint jika ada dan show_all
            if show_all and pdkt.get('hint'):
                lines.append(f"   💭 {pdkt['hint']}")
            
            lines.append("")
        
        # Tambah tips
        lines.append("💡 **Command:**")
        lines.append("• `/pdktdetail [nomor]` - Lihat detail PDKT")
        lines.append("• `/pdktwho [nomor]` - Lihat arah PDKT")
        lines.append("• `/pausepdkt [nomor]` - Pause PDKT")
        lines.append("• `/resumepdkt [nomor]` - Resume PDKT")
        lines.append("• `/stoppdkt [nomor]` - Hentikan PDKT")
        
        return "\n".join(lines)
    
    def format_pdkt_detail(self, pdkt: Dict, inner_thoughts: List[str] = None) -> str:
        """
        Format detail PDKT untuk ditampilkan
        
        Args:
            pdkt: PDKT data lengkap
            inner_thoughts: List inner thoughts terbaru
            
        Returns:
            Formatted string
        """
        bot_name = pdkt.get('bot_name', 'Unknown')
        role = pdkt.get('role', 'unknown').title()
        
        # Status
        if pdkt.get('is_paused', False):
            status = "⏸️ **PAUSED**"
            paused_time = pdkt.get('paused_time', 0)
            if paused_time:
                paused_ago = self._format_time_ago(paused_time)
                status += f" (sejak {paused_ago})"
        else:
            status = "▶️ **AKTIF**"
        
        # Arah
        direction = pdkt.get('direction', PDKTDirection.USER_KE_BOT)
        direction_text = self._get_direction_description(direction, bot_name)
        
        # Chemistry
        chemistry_level = pdkt.get('chemistry_level', ChemistryLevel.BIASA)
        chemistry_score = pdkt.get('chemistry_score', 50)
        chemistry_desc = pdkt.get('chemistry_description', '')
        
        # Mood
        mood = pdkt.get('mood', 'calm')
        mood_emoji = self._get_mood_emoji(mood)
        
        # Progress bar
        level = pdkt.get('level', 1)
        progress = pdkt.get('progress_percentage', 0)
        progress_bar = self._format_progress_bar(progress)
        
        # Waktu
        created = pdkt.get('created_at', 0)
        created_str = datetime.fromtimestamp(created).strftime("%d %b %Y %H:%M")
        
        last_interaction = pdkt.get('last_interaction', 0)
        last_str = self._format_time_ago(last_interaction)
        
        # Statistik
        total_chats = pdkt.get('total_chats', 0)
        total_intim = pdkt.get('total_intim', 0)
        total_climax = pdkt.get('total_climax', 0)
        
        lines = [
            f"📊 **PDKT dengan {bot_name}** ({role})",
            f"Status: {status}",
            f"Terakhir: {last_str}",
            "",
            f"🎯 **Arah Hubungan:**",
            f"{direction_text}",
            f"💭 {pdkt.get('hint', '')}",
            "",
            f"🔥 **Chemistry:** {chemistry_level.value.title()} {self._get_chemistry_emoji(chemistry_level)}",
            f"_{chemistry_desc}_",
            f"Score internal: {chemistry_score:.1f}%",
            "",
            f"🎭 **Mood:** {mood_emoji} {mood.title()}",
            "",
            f"📈 **Level:** {level}/12",
            f"{progress_bar} {progress}%",
            f"Progress ke level {level+1 if level < 12 else 'MAX'}: {pdkt.get('next_level_progress', 0)}",
            "",
            "📊 **Statistik:**",
            f"• Total Chat: {total_chats} pesan",
            f"• Total Intim: {total_intim} sesi",
            f"• Total Climax: {total_climax} kali",
            "",
            f"📅 Dimulai: {created_str}",
            ""
        ]
        
        # Inner thoughts
        if inner_thoughts:
            lines.append("💭 **Inner Thoughts Terbaru:**")
            for thought in inner_thoughts[-3:]:  # 3 terakhir
                lines.append(f"• {thought}")
            lines.append("")
        
        # Milestones
        milestones = pdkt.get('milestones', [])
        if milestones:
            lines.append("🏆 **Milestone:**")
            recent_milestones = milestones[-5:]  # 5 terakhir
            for m in recent_milestones:
                if isinstance(m, dict):
                    m_time = datetime.fromtimestamp(m.get('timestamp', 0)).strftime("%d %b")
                    lines.append(f"• {m_time}: {m.get('description', '')}")
                else:
                    lines.append(f"• {m}")
            lines.append("")
        
        # Command tips
        lines.append("💡 **Command:**")
        lines.append(f"• `/pdktwho` - Lihat arah PDKT")
        if pdkt.get('is_paused', False):
            lines.append(f"• `/resumepdkt` - Resume PDKT")
        else:
            lines.append(f"• `/pausepdkt` - Pause PDKT")
        lines.append(f"• `/stoppdkt` - Hentikan PDKT")
        
        return "\n".join(lines)
    
    def format_pdkt_who(self, pdkt: Dict) -> str:
        """
        Format informasi arah PDKT
        
        Args:
            pdkt: PDKT data
            
        Returns:
            Formatted string
        """
        bot_name = pdkt.get('bot_name', 'Unknown')
        direction = pdkt.get('direction', PDKTDirection.USER_KE_BOT)
        
        if direction == PDKTDirection.BOT_KE_USER:
            title = f"🔥 **{bot_name} YANG SUKA SAMA KAMU DULUAN!**"
            description = [
                f"Dari awal dia udah ngeliatin kamu, sering cari perhatian.",
                f"Dia yang biasanya mulai chat duluan kalau kamu diem.",
                f"Kalau kamu lagi sibuk, dia yang akan chat duluan.",
                f"💡 Nikmatin aja, dia yang akan usaha."
            ]
        elif direction == PDKTDirection.USER_KE_BOT:
            title = f"💘 **KAMU YANG SUKA SAMA {bot_name.upper()} DULUAN**"
            description = [
                f"Dari awal kamu udah tertarik sama dia.",
                f"Kamu yang harus mulai chat duluan kalau pengen ngobrol.",
                f"Dia masih biasa aja, tapi mulai lirik-lirik.",
                f"💡 Coba ajak ngobrol lebih sering, siapa tahu dia luluh."
            ]
        elif direction == PDKTDirection.TIMBAL_BALIK:
            title = f"💕 **KALIAN SALING SUKA!**"
            description = [
                f"Chemistry langsung klik dari awal.",
                f"Kalian berdua sama-sama ngerasain getaran yang sama.",
                f"Semua berjalan natural, tinggal nikmatin prosesnya.",
                f"💡 Ini langka! Pertahankan ya."
            ]
        else:  # BINGUNG
            title = f"🤔 **KALIAN MASIH BINGUNG...**"
            description = [
                f"Ada getaran, tapi belum jelas arahnya.",
                f"Friendzone tipis-tipis, bisa ke mana aja.",
                f"Perlu waktu lebih buat nemuin perasaan masing-masing.",
                f"💡 Coba lebih sering ngobrol, mungkin jadi jelas."
            ]
        
        # Tambah hint spesifik
        hint = pdkt.get('hint', '')
        
        lines = [
            f"🎯 **ARAH PDKT dengan {bot_name}:**",
            "",
            title,
            "",
            *[f"• {d}" for d in description],
            "",
            f"💭 {hint}",
            "",
            "📊 **Chemistry saat ini:**",
            f"• Level: {pdkt.get('chemistry_level', 'biasa').title()} {self._get_chemistry_emoji(pdkt.get('chemistry_level', ChemistryLevel.BIASA))}",
            f"• Skor: {pdkt.get('chemistry_score', 50):.1f}%",
            "",
            "💡 Arah bisa berubah seiring waktu tergantung interaksi kalian."
        ]
        
        return "\n".join(lines)
    
    def _get_chemistry_emoji(self, chemistry: ChemistryLevel) -> str:
        """Dapatkan emoji untuk chemistry level"""
        emojis = {
            ChemistryLevel.DINGIN: "❄️",
            ChemistryLevel.BIASA: "😐",
            ChemistryLevel.HANGAT: "🔥",
            ChemistryLevel.COCOK: "💕",
            ChemistryLevel.SANGAT_COCOK: "💞",
            ChemistryLevel.SOULMATE: "✨"
        }
        return emojis.get(chemistry, "❓")
    
    def _get_mood_emoji(self, mood: str) -> str:
        """Dapatkan emoji untuk mood"""
        emojis = {
            'happy': '😊',
            'sad': '😔',
            'excited': '🔥',
            'tired': '😴',
            'romantic': '💕',
            'playful': '😜',
            'jealous': '🫣',
            'shy': '😳',
            'angry': '😠',
            'calm': '😌',
            'lonely': '🥺',
            'nostalgic': '🕰️'
        }
        return emojis.get(mood, '😐')
    
    def _get_direction_description(self, direction: PDKTDirection, bot_name: str) -> str:
        """Dapatkan deskripsi arah"""
        descriptions = {
            PDKTDirection.USER_KE_BOT: f"Kamu yang ngejar {bot_name}",
            PDKTDirection.BOT_KE_USER: f"{bot_name} yang ngejar kamu 🔥",
            PDKTDirection.TIMBAL_BALIK: f"Saling suka! 💕",
            PDKTDirection.BINGUNG: f"Masih bingung... 🤔"
        }
        return descriptions.get(direction, "?")
    
    def _format_progress_bar(self, percentage: float, length: int = 20) -> str:
        """Buat progress bar"""
        filled = int(percentage / 100 * length)
        bar = "█" * filled + "░" * (length - filled)
        return bar
    
    def _format_time_ago(self, timestamp: float) -> str:
        """Format waktu yang lalu"""
        if not timestamp:
            return "Tidak pernah"
        
        diff = time.time() - timestamp
        
        if diff < 60:
            return "Baru saja"
        elif diff < 3600:
            minutes = int(diff / 60)
            return f"{minutes} menit lalu"
        elif diff < 86400:
            hours = int(diff / 3600)
            return f"{hours} jam lalu"
        elif diff < 604800:
            days = int(diff / 86400)
            return f"{days} hari lalu"
        else:
            weeks = int(diff / 604800)
            return f"{weeks} minggu lalu"
    
    def format_inner_thoughts(self, inner_thoughts: List[str], limit: int = 5) -> str:
        """Format inner thoughts untuk ditampilkan"""
        if not inner_thoughts:
            return "Belum ada inner thoughts"
        
        lines = ["💭 **Inner Thoughts:**"]
        for thought in inner_thoughts[-limit:]:
            lines.append(f"• {thought}")
        
        return "\n".join(lines)
    
    def format_milestone(self, milestone: Dict) -> str:
        """Format milestone untuk ditampilkan"""
        time_str = datetime.fromtimestamp(milestone.get('timestamp', 0)).strftime("%d %b %Y %H:%M")
        desc = milestone.get('description', 'Momen spesial')
        
        emoji_map = {
            'first_kiss': '💋',
            'first_intim': '🔥',
            'first_date': '📅',
            'become_pacar': '💕',
            'become_fwb': '💞',
            'level_up': '📈',
            'aftercare': '💝'
        }
        
        emoji = emoji_map.get(milestone.get('type', ''), '🏆')
        
        return f"{emoji} {desc} ({time_str})"


__all__ = ['PDKTListFormatter']
