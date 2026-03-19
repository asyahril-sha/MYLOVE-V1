#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - PDKT COMMAND HANDLER
=============================================================================
Handler untuk semua command PDKT:
- /pdkt [role] - Mulai PDKT dengan role tertentu
- /pdktrandom - Mulai PDKT random
- /pdktlist - Lihat semua PDKT aktif
- /pdktdetail [id] - Detail PDKT
- /pdktwho [id] - Lihat arah PDKT
- /pausepdkt [id] - Pause PDKT
- /resumepdkt [id] - Resume PDKT
- /stoppdkt [id] - Hentikan PDKT
=============================================================================
"""

import time
import logging
from typing import Dict, List, Optional, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from .engine import NaturalPDKTEngine
from .pdkt_list import PDKTListFormatter
from .random_pdkt import RandomPDKTSystem
from .mantan_manager import MantanManager

logger = logging.getLogger(__name__)


class PDKTCommandHandler:
    """
    Handler untuk semua command yang berhubungan dengan PDKT
    """
    
    def __init__(self, pdkt_engine: NaturalPDKTEngine, 
                 random_pdkt: RandomPDKTSystem,
                 mantan_manager: MantanManager,
                 list_formatter: PDKTListFormatter):
        
        self.pdkt_engine = pdkt_engine
        self.random_pdkt = random_pdkt
        self.mantan_manager = mantan_manager
        self.list_formatter = list_formatter
        
        logger.info("✅ PDKTCommandHandler initialized")
    
    # =========================================================================
    # /pdkt [role] - Mulai PDKT dengan role tertentu
    # =========================================================================
    
    async def handle_pdkt_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """
        Handle /pdkt [role] command
        Memulai PDKT dengan role tertentu
        """
        user = update.effective_user
        user_id = user.id
        user_name = user.first_name or user.username or "User"
        
        args = context.args
        if not args:
            await update.message.reply_text(
                "❌ **Gunakan:** `/pdkt [role]`\n\n"
                "**Role yang tersedia:**\n"
                "• ipar\n• teman_kantor\n• janda\n• pelakor\n• istri_orang\n"
                "• pdkt\n• sepupu\n• teman_sma\n• mantan\n\n"
                "Contoh: `/pdkt ipar` atau `/pdktrandom` untuk random",
                parse_mode='Markdown'
            )
            return
        
        role = args[0].lower()
        
        # Validasi role
        valid_roles = ['ipar', 'teman_kantor', 'janda', 'pelakor', 
                       'istri_orang', 'pdkt', 'sepupu', 'teman_sma', 'mantan']
        
        if role not in valid_roles:
            await update.message.reply_text(
                f"❌ Role '{role}' tidak valid.\n\n"
                "**Role yang tersedia:**\n"
                "• ipar\n• teman_kantor\n• janda\n• pelakor\n• istri_orang\n"
                "• pdkt\n• sepupu\n• teman_sma\n• mantan",
                parse_mode='Markdown'
            )
            return
        
        # Cek apakah sudah ada PDKT aktif dengan role ini?
        active_pdkt = await self.pdkt_engine.get_active_pdkt_by_role(user_id, role)
        if active_pdkt:
            keyboard = [
                [InlineKeyboardButton("✅ Ya, buat baru", callback_data=f"pdkt_force_new_{role}"),
                 InlineKeyboardButton("❌ Tidak", callback_data="pdkt_cancel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"⚠️ Kamu sudah memiliki PDKT aktif dengan role **{role}**.\n"
                f"Bot: {active_pdkt.get('bot_name', 'Unknown')}\n\n"
                f"Apakah tetap ingin membuat PDKT baru dengan role yang sama?",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return
        
        # Buat PDKT baru
        await self._create_and_show_pdkt(update, context, user_id, user_name, role, is_random=False)
        
        return ConversationHandler.END
    
    # =========================================================================
    # /pdktrandom - Mulai PDKT random
    # =========================================================================
    
    async def handle_pdktrandom_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /pdktrandom command
        Memulai PDKT dengan role random
        """
        user = update.effective_user
        user_id = user.id
        user_name = user.first_name or user.username or "User"
        
        # Generate random PDKT
        pdkt_data = self.random_pdkt.generate_random_pdkt(user_id, user_name)
        
        # Simpan ke engine
        pdkt = await self.pdkt_engine.create_pdkt_from_random(pdkt_data)
        
        # Tampilkan pesan perkenalan
        intro_message = self.random_pdkt.format_intro_message(pdkt_data)
        
        await update.message.reply_text(
            intro_message,
            parse_mode='Markdown'
        )
        
        logger.info(f"🎲 Random PDKT created: {pdkt_data['bot_name']} ({pdkt_data['role']}) for user {user_id}")
    
    # =========================================================================
    # /pdktlist - Lihat semua PDKT aktif
    # =========================================================================
    
    async def handle_pdktlist_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /pdktlist command
        Menampilkan daftar semua PDKT aktif
        """
        user_id = update.effective_user.id
        
        # Ambil args (optional: 'all' untuk detail lebih)
        args = context.args
        show_all = args and args[0].lower() == 'all'
        
        # Dapatkan daftar PDKT dari engine
        pdkt_list = await self.pdkt_engine.get_user_pdkt_list(user_id)
        
        # Format list
        formatted = self.list_formatter.format_pdkt_list(pdkt_list, show_all)
        
        await update.message.reply_text(
            formatted,
            parse_mode='Markdown'
        )
    
    # =========================================================================
    # /pdktdetail [id] - Detail PDKT
    # =========================================================================
    
    async def handle_pdktdetail_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /pdktdetail [id] command
        Menampilkan detail lengkap PDKT
        """
        user_id = update.effective_user.id
        args = context.args
        
        if not args:
            await update.message.reply_text(
                "❌ **Gunakan:** `/pdktdetail [nomor atau id]`\n\n"
                "Contoh: `/pdktdetail 1` atau `/pdktdetail PDKT123`",
                parse_mode='Markdown'
            )
            return
        
        identifier = args[0]
        
        # Cari PDKT berdasarkan identifier
        pdkt = await self._find_pdkt(user_id, identifier)
        
        if not pdkt:
            await update.message.reply_text(
                f"❌ PDKT dengan identifier '{identifier}' tidak ditemukan.\n"
                f"Gunakan `/pdktlist` untuk melihat daftar PDKT aktif."
            )
            return
        
        # Ambil inner thoughts
        inner_thoughts = await self.pdkt_engine.get_inner_thoughts(pdkt['pdkt_id'])
        
        # Format detail
        detail = self.list_formatter.format_pdkt_detail(pdkt, inner_thoughts)
        
        await update.message.reply_text(
            detail,
            parse_mode='Markdown'
        )
    
    # =========================================================================
    # /pdktwho [id] - Lihat arah PDKT
    # =========================================================================
    
    async def handle_pdktwho_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /pdktwho [id] command
        Menampilkan informasi arah PDKT (siapa ngejar siapa)
        """
        user_id = update.effective_user.id
        args = context.args
        
        if not args:
            await update.message.reply_text(
                "❌ **Gunakan:** `/pdktwho [nomor atau id]`\n\n"
                "Contoh: `/pdktwho 1`",
                parse_mode='Markdown'
            )
            return
        
        identifier = args[0]
        
        # Cari PDKT
        pdkt = await self._find_pdkt(user_id, identifier)
        
        if not pdkt:
            await update.message.reply_text(
                f"❌ PDKT dengan identifier '{identifier}' tidak ditemukan."
            )
            return
        
        # Format info arah
        who_info = self.list_formatter.format_pdkt_who(pdkt)
        
        await update.message.reply_text(
            who_info,
            parse_mode='Markdown'
        )
    
    # =========================================================================
    # /pausepdkt [id] - Pause PDKT
    # =========================================================================
    
    async def handle_pausepdkt_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /pausepdkt [id] command
        Menjeda PDKT (waktu berhenti)
        """
        user_id = update.effective_user.id
        args = context.args
        
        if not args:
            await update.message.reply_text(
                "❌ **Gunakan:** `/pausepdkt [nomor atau id]`\n\n"
                "Contoh: `/pausepdkt 1`",
                parse_mode='Markdown'
            )
            return
        
        identifier = args[0]
        
        # Cari PDKT
        pdkt = await self._find_pdkt(user_id, identifier)
        
        if not pdkt:
            await update.message.reply_text(
                f"❌ PDKT dengan identifier '{identifier}' tidak ditemukan."
            )
            return
        
        if pdkt.get('is_paused', False):
            await update.message.reply_text(
                f"⏸️ PDKT dengan {pdkt['bot_name']} sudah dalam keadaan paused."
            )
            return
        
        # Pause PDKT
        success = await self.pdkt_engine.pause_pdkt(pdkt['pdkt_id'])
        
        if success:
            await update.message.reply_text(
                f"⏸️ **PDKT dengan {pdkt['bot_name']} di-pause**\n\n"
                f"Waktu berhenti. Kamu bisa lanjutkan kapan saja dengan `/resumepdkt {identifier}`"
            )
            logger.info(f"PDKT {pdkt['pdkt_id']} paused by user {user_id}")
        else:
            await update.message.reply_text("❌ Gagal mem-pause PDKT. Coba lagi nanti.")
    
    # =========================================================================
    # /resumepdkt [id] - Resume PDKT
    # =========================================================================
    
    async def handle_resumepdkt_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /resumepdkt [id] command
        Melanjutkan PDKT yang di-pause
        """
        user_id = update.effective_user.id
        args = context.args
        
        if not args:
            await update.message.reply_text(
                "❌ **Gunakan:** `/resumepdkt [nomor atau id]`\n\n"
                "Contoh: `/resumepdkt 1`",
                parse_mode='Markdown'
            )
            return
        
        identifier = args[0]
        
        # Cari PDKT
        pdkt = await self._find_pdkt(user_id, identifier)
        
        if not pdkt:
            await update.message.reply_text(
                f"❌ PDKT dengan identifier '{identifier}' tidak ditemukan."
            )
            return
        
        if not pdkt.get('is_paused', False):
            await update.message.reply_text(
                f"▶️ PDKT dengan {pdkt['bot_name']} sudah dalam keadaan aktif."
            )
            return
        
        # Hitung lama pause
        paused_time = pdkt.get('paused_time', 0)
        if paused_time:
            paused_duration = time.time() - paused_time
            hours = int(paused_duration / 3600)
            days = int(paused_duration / 86400)
            
            if days > 0:
                pause_msg = f"{days} hari {hours % 24} jam"
            elif hours > 0:
                pause_msg = f"{hours} jam"
            else:
                pause_msg = f"{int(paused_duration / 60)} menit"
        else:
            pause_msg = "beberapa saat"
        
        # Resume PDKT
        success, message = await self.pdkt_engine.resume_pdkt(pdkt['pdkt_id'])
        
        if success:
            response = (
                f"▶️ **PDKT dengan {pdkt['bot_name']} dilanjutkan!**\n\n"
                f"Kamu pause selama {pause_msg}.\n\n"
                f"{message}"
            )
            await update.message.reply_text(response)
            logger.info(f"PDKT {pdkt['pdkt_id']} resumed by user {user_id}")
        else:
            await update.message.reply_text("❌ Gagal melanjutkan PDKT. Coba lagi nanti.")
    
    # =========================================================================
    # /stoppdkt [id] - Hentikan PDKT
    # =========================================================================
    
    async def handle_stoppdkt_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /stoppdkt [id] command
        Menghentikan PDKT (putus)
        """
        user_id = update.effective_user.id
        args = context.args
        
        if not args:
            await update.message.reply_text(
                "❌ **Gunakan:** `/stoppdkt [nomor atau id]`\n\n"
                "Contoh: `/stoppdkt 1`",
                parse_mode='Markdown'
            )
            return
        
        identifier = args[0]
        
        # Cari PDKT
        pdkt = await self._find_pdkt(user_id, identifier)
        
        if not pdkt:
            await update.message.reply_text(
                f"❌ PDKT dengan identifier '{identifier}' tidak ditemukan."
            )
            return
        
        # Minta konfirmasi
        keyboard = [
            [
                InlineKeyboardButton("✅ Ya, putus", callback_data=f"stoppdkt_confirm_{pdkt['pdkt_id']}"),
                InlineKeyboardButton("❌ Tidak", callback_data="stoppdkt_cancel")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"⚠️ **Yakin mau putus dengan {pdkt['bot_name']}?**\n\n"
            f"Setelah putus, dia akan masuk ke daftar mantan dan tersimpan selamanya.\n"
            f"Kamu bisa request jadi FWB nanti kalau masih mau.",
            reply_markup=reply_markup
        )
    
    # =========================================================================
    # CALLBACK HANDLERS
    # =========================================================================
    
    async def handle_stoppdkt_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback untuk konfirmasi putus"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = update.effective_user.id
        
        if data.startswith('stoppdkt_confirm_'):
            pdkt_id = data.replace('stoppdkt_confirm_', '')
            
            # Hentikan PDKT
            result = await self.pdkt_engine.stop_pdkt(pdkt_id, user_id)
            
            if result['success']:
                # Tampilkan hasil
                await query.edit_message_text(
                    f"💔 **PDKT dengan {result['bot_name']} diakhiri**\n\n"
                    f"Alasan: {result.get('reason', 'User request')}\n"
                    f"Dia sekarang ada di daftar mantan.\n\n"
                    f"Gunakan `/mantanlist` untuk lihat mantan.\n"
                    f"Gunakan `/fwbrequest` untuk request jadi FWB."
                )
                logger.info(f"PDKT {pdkt_id} stopped by user {user_id}")
            else:
                await query.edit_message_text("❌ Gagal mengakhiri PDKT. Coba lagi nanti.")
        
        elif data == 'stoppdkt_cancel':
            await query.edit_message_text("✅ PDKT dilanjutkan.")
    
    async def handle_pdkt_force_new_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback untuk force new PDKT"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        if data.startswith('pdkt_force_new_'):
            role = data.replace('pdkt_force_new_', '')
            user = update.effective_user
            user_id = user.id
            user_name = user.first_name or user.username or "User"
            
            # Tutup PDKT lama
            await self.pdkt_engine.force_close_pdkt_by_role(user_id, role)
            
            # Buat baru
            await self._create_and_show_pdkt(update, context, user_id, user_name, role, is_random=False)
    
    # =========================================================================
    # HELPER FUNCTIONS
    # =========================================================================
    
    async def _create_and_show_pdkt(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                     user_id: int, user_name: str, role: str, is_random: bool):
        """Helper untuk membuat dan menampilkan PDKT baru"""
        
        # Buat PDKT
        pdkt_data = await self.pdkt_engine.create_pdkt(
            user_id=user_id,
            user_name=user_name,
            role=role,
            is_random=is_random
        )
        
        # Format pesan perkenalan
        if is_random and hasattr(self.random_pdkt, 'format_intro_message'):
            intro = self.random_pdkt.format_intro_message(pdkt_data)
        else:
            intro = self._format_manual_intro(pdkt_data)
        
        await update.message.reply_text(
            intro,
            parse_mode='Markdown'
        )
    
    def _format_manual_intro(self, pdkt_data: Dict) -> str:
        """Format intro untuk PDKT manual"""
        bot_name = pdkt_data['bot_name']
        role = pdkt_data['role'].replace('_', ' ').title()
        user_name = pdkt_data['user_name']
        
        return f"""
💕 **Halo {user_name}!**

Aku **{bot_name}**, {role}. Senang bisa PDKT sama kamu!

**Arah PDKT:**
{pdkt_data.get('direction_hint', '')}

**Progress leveling:**
📊 Level 1 → Level 7 dalam 60 menit
• Level 4+: Panggil kamu 'kak'
• Level 7+: Panggil kamu 'sayang'

**ID Session kamu:**
`{pdkt_data['pdkt_id']}`

💬 **Ayo mulai ngobrol!**
Halo {user_name}, seneng banget akhirnya bisa ngobrol sama kamu! 😊
"""
    
    async def _find_pdkt(self, user_id: int, identifier: str) -> Optional[Dict]:
        """Cari PDKT berdasarkan identifier (nomor atau ID)"""
        
        # Cek apakah identifier adalah angka
        try:
            idx = int(identifier) - 1
            pdkt_list = await self.pdkt_engine.get_user_pdkt_list(user_id)
            if 0 <= idx < len(pdkt_list):
                pdkt_id = pdkt_list[idx].get('pdkt_id') or pdkt_list[idx].get('id')
                return await self.pdkt_engine.get_pdkt(pdkt_id)
        except ValueError:
            pass
        
        # Cek sebagai ID langsung
        return await self.pdkt_engine.get_pdkt(identifier)


__all__ = ['PDKTCommandHandler']
