#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - CALLBACKS V2
=============================================================================
Callback handlers untuk semua inline keyboard V2:
- PDKT callbacks (pause, resume, stop, detail)
- Mantan callbacks (fwb request, accept, decline)
- FWB callbacks (pause, resume, end)
- Back to main menu
=============================================================================
"""

import time
import logging
from typing import Dict, Any, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from database.models_v2 import Constants
from ..pdkt_natural.command_handler import PDKTCommandHandler
from ..pdkt_natural.mantan_manager import MantanManager
from ..relationship.fwb_manager import FWBManager

logger = logging.getLogger(__name__)


class CallbacksV2:
    """
    Handler untuk semua callback V2
    """
    
    def __init__(self,
                 pdkt_handler: PDKTCommandHandler,
                 mantan_manager: MantanManager,
                 fwb_manager: FWBManager):
        
        self.pdkt = pdkt_handler
        self.mantan = mantan_manager
        self.fwb = fwb_manager
        
        logger.info("✅ CallbacksV2 initialized")
    
    # =========================================================================
    # MAIN CALLBACK HANDLER
    # =========================================================================
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Main callback handler untuk semua pattern V2
        """
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user = update.effective_user
        user_id = user.id
        
        logger.info(f"🔄 V2 Callback: {data} from user {user_id}")
        
        # ===== PDKT CALLBACKS =====
        if data.startswith('pdkt_'):
            await self._handle_pdkt_callback(update, context)
        
        # ===== STOP PDKT CALLBACKS =====
        elif data.startswith('stoppdkt_'):
            await self._handle_stoppdkt_callback(update, context)
        
        # ===== MANTAN CALLBACKS =====
        elif data.startswith('mantan_'):
            await self._handle_mantan_callback(update, context)
        
        # ===== FWB CALLBACKS =====
        elif data.startswith('fwb_'):
            await self._handle_fwb_callback(update, context)
        
        # ===== BACK TO MAIN =====
        elif data == 'back_to_main_v2':
            await self._back_to_main(update, context)
        
        else:
            await query.edit_message_text("❌ Perintah tidak dikenal.")
    
    # =========================================================================
    # PDKT CALLBACK HANDLERS
    # =========================================================================
    
    async def _handle_pdkt_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle semua callback PDKT"""
        query = update.callback_query
        data = query.data
        
        if data == 'pdkt_list':
            await self.pdkt.handle_pdktlist_command(update, context)
        
        elif data.startswith('pdkt_detail_'):
            pdkt_id = data.replace('pdkt_detail_', '')
            context.args = [pdkt_id]
            await self.pdkt.handle_pdktdetail_command(update, context)
        
        elif data.startswith('pdkt_who_'):
            pdkt_id = data.replace('pdkt_who_', '')
            context.args = [pdkt_id]
            await self.pdkt.handle_pdktwho_command(update, context)
        
        elif data.startswith('pdkt_pause_'):
            pdkt_id = data.replace('pdkt_pause_', '')
            context.args = [pdkt_id]
            await self.pdkt.handle_pausepdkt_command(update, context)
        
        elif data.startswith('pdkt_resume_'):
            pdkt_id = data.replace('pdkt_resume_', '')
            context.args = [pdkt_id]
            await self.pdkt.handle_resumepdkt_command(update, context)
        
        elif data.startswith('pdkt_stop_'):
            pdkt_id = data.replace('pdkt_stop_', '')
            context.args = [pdkt_id]
            await self.pdkt.handle_stoppdkt_command(update, context)
        
        elif data == 'pdkt_cancel':
            await query.edit_message_text("✅ PDKT dibatalkan.")
        
        elif data.startswith('pdkt_force_new_'):
            await self.pdkt.handle_pdkt_force_new_callback(update, context)
    
    async def _handle_stoppdkt_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback untuk konfirmasi stop PDKT"""
        query = update.callback_query
        data = query.data
        
        if data.startswith('stoppdkt_confirm_'):
            pdkt_id = data.replace('stoppdkt_confirm_', '')
            context.args = [pdkt_id]
            await self.pdkt.handle_stoppdkt_callback(update, context)
        
        elif data == 'stoppdkt_cancel':
            await query.edit_message_text("✅ PDKT dilanjutkan.")
    
    # =========================================================================
    # MANTAN CALLBACK HANDLERS
    # =========================================================================
    
    async def _handle_mantan_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle semua callback mantan"""
        query = update.callback_query
        data = query.data
        user_id = update.effective_user.id
        
        if data.startswith('mantan_detail_'):
            try:
                idx = int(data.replace('mantan_detail_', ''))
                mantan = self.mantan.get_mantan_by_index(user_id, idx)
                if mantan:
                    formatted = self.mantan.format_mantan_detail(mantan)
                    await query.edit_message_text(formatted, parse_mode='Markdown')
                else:
                    await query.edit_message_text("❌ Mantan tidak ditemukan")
            except:
                await query.edit_message_text("❌ Terjadi kesalahan")
        
        elif data.startswith('mantan_fwb_request_'):
            try:
                idx = int(data.replace('mantan_fwb_request_', ''))
                
                # Tampilkan keyboard konfirmasi
                keyboard = [
                    [
                        InlineKeyboardButton("✅ Ya, request", callback_data=f"fwb_request_confirm_{idx}"),
                        InlineKeyboardButton("❌ Tidak", callback_data="mantan_cancel")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                mantan = self.mantan.get_mantan_by_index(user_id, idx)
                if mantan:
                    await query.edit_message_text(
                        f"⚠️ Yakin mau request FWB dengan {mantan['bot_name']}?\n\n"
                        f"Bot akan memutuskan menerima atau menolak.",
                        reply_markup=reply_markup
                    )
                else:
                    await query.edit_message_text("❌ Mantan tidak ditemukan")
            except:
                await query.edit_message_text("❌ Terjadi kesalahan")
        
        elif data == 'mantan_cancel':
            await query.edit_message_text("✅ Dibatalkan.")
    
    # =========================================================================
    # FWB CALLBACK HANDLERS
    # =========================================================================
    
    async def _handle_fwb_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle semua callback FWB"""
        query = update.callback_query
        data = query.data
        user_id = update.effective_user.id
        
        # ===== FWB REQUEST CONFIRMATION =====
        if data.startswith('fwb_request_confirm_'):
            try:
                idx = int(data.replace('fwb_request_confirm_', ''))
                user_name = update.effective_user.first_name or "User"
                
                mantan = self.mantan.get_mantan_by_index(user_id, idx)
                if mantan:
                    # Proses request
                    result = await self.mantan.request_fwb(
                        user_id=user_id,
                        mantan_id=mantan['mantan_id'],
                        message=""
                    )
                    
                    await query.edit_message_text(result['message'], parse_mode='Markdown')
                else:
                    await query.edit_message_text("❌ Mantan tidak ditemukan")
            except Exception as e:
                logger.error(f"Error in fwb request: {e}")
                await query.edit_message_text("❌ Terjadi kesalahan")
        
        # ===== FWB PAUSE =====
        elif data.startswith('fwb_pause_'):
            try:
                idx = int(data.replace('fwb_pause_', ''))
                fwb = await self.fwb.get_fwb_by_index(user_id, idx)
                
                if fwb:
                    result = await self.fwb.pause_fwb(user_id, fwb['fwb_id'])
                    await query.edit_message_text(
                        f"⏸️ **FWB dengan {result['bot_name']} di-pause**\n\n"
                        f"{result.get('message', '')}"
                    )
                else:
                    await query.edit_message_text("❌ FWB tidak ditemukan")
            except:
                await query.edit_message_text("❌ Terjadi kesalahan")
        
        # ===== FWB RESUME =====
        elif data.startswith('fwb_resume_'):
            try:
                idx = int(data.replace('fwb_resume_', ''))
                fwb = await self.fwb.get_fwb_by_index(user_id, idx)
                
                if fwb:
                    result = await self.fwb.resume_fwb(user_id, fwb['fwb_id'])
                    await query.edit_message_text(
                        f"▶️ **FWB dengan {result['bot_name']} dilanjutkan**\n\n"
                        f"{result['message']}"
                    )
                else:
                    await query.edit_message_text("❌ FWB tidak ditemukan")
            except:
                await query.edit_message_text("❌ Terjadi kesalahan")
        
        # ===== FWB END =====
        elif data.startswith('fwb_end_'):
            try:
                idx = int(data.replace('fwb_end_', ''))
                
                # Tampilkan keyboard konfirmasi
                keyboard = [
                    [
                        InlineKeyboardButton("✅ Ya, akhiri", callback_data=f"fwb_end_confirm_{idx}"),
                        InlineKeyboardButton("❌ Tidak", callback_data="fwb_cancel")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                fwb = await self.fwb.get_fwb_by_index(user_id, idx)
                if fwb:
                    await query.edit_message_text(
                        f"⚠️ Yakin mau akhiri FWB dengan {fwb['bot_name']}?",
                        reply_markup=reply_markup
                    )
                else:
                    await query.edit_message_text("❌ FWB tidak ditemukan")
            except:
                await query.edit_message_text("❌ Terjadi kesalahan")
        
        # ===== FWB END CONFIRM =====
        elif data.startswith('fwb_end_confirm_'):
            try:
                idx = int(data.replace('fwb_end_confirm_', ''))
                fwb = await self.fwb.get_fwb_by_index(user_id, idx)
                
                if fwb:
                    result = await self.fwb.end_fwb(user_id, fwb['fwb_id'])
                    await query.edit_message_text(
                        f"💔 **FWB dengan {result['bot_name']} diakhiri**\n\n"
                        f"{result['message']}"
                    )
                else:
                    await query.edit_message_text("❌ FWB tidak ditemukan")
            except:
                await query.edit_message_text("❌ Terjadi kesalahan")
        
        # ===== FWB DETAIL =====
        elif data.startswith('fwb_detail_'):
            try:
                idx = int(data.replace('fwb_detail_', ''))
                fwb = await self.fwb.get_fwb_by_index(user_id, idx)
                
                if fwb:
                    # Buat keyboard untuk actions
                    keyboard = [
                        [
                            InlineKeyboardButton("⏸️ Pause", callback_data=f"fwb_pause_{idx}"),
                            InlineKeyboardButton("▶️ Resume", callback_data=f"fwb_resume_{idx}")
                        ],
                        [
                            InlineKeyboardButton("💔 End", callback_data=f"fwb_end_{idx}"),
                            InlineKeyboardButton("🔙 Back", callback_data="fwb_list")
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    # Format detail
                    created = time.strftime('%d %b %Y', time.localtime(fwb['created_at']))
                    last = self._format_time_ago(fwb['last_interaction'])
                    
                    text = (
                        f"💕 **{fwb['bot_name']}** ({fwb['role']})\n"
                        f"Status: {fwb['status'].value.upper()}\n"
                        f"Chemistry: {fwb['chemistry_score']:.1f}%\n"
                        f"Climax: {fwb['climax_count']} | Intim: {fwb['intim_count']}\n"
                        f"Chat: {fwb['total_chats']}\n"
                        f"Bergabung: {created}\n"
                        f"Terakhir: {last}\n\n"
                        f"Pilih aksi:"
                    )
                    
                    await query.edit_message_text(text, reply_markup=reply_markup)
                else:
                    await query.edit_message_text("❌ FWB tidak ditemukan")
            except:
                await query.edit_message_text("❌ Terjadi kesalahan")
        
        # ===== FWB LIST =====
        elif data == 'fwb_list':
            # Panggil command fwblist
            context.args = []
            await self._show_fwb_list(update, context)
        
        elif data == 'fwb_cancel':
            await query.edit_message_text("✅ Dibatalkan.")
    
    async def _show_fwb_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Tampilkan daftar FWB"""
        query = update.callback_query
        user_id = update.effective_user.id
        
        fwbs = await self.fwb.get_user_fwb(user_id)
        
        if not fwbs:
            await query.edit_message_text(
                "💔 **Belum ada FWB**\n\n"
                "Mantan PDKT bisa request jadi FWB dengan `/fwbrequest [nomor]`"
            )
            return
        
        lines = ["💕 **DAFTAR FWB**\n"]
        
        for i, fwb in enumerate(fwbs[:10], 1):
            status_emoji = "🟢" if fwb['status'].value == 'active' else "⏸️"
            lines.append(
                f"{i}. {status_emoji} **{fwb['bot_name']}** ({fwb['role']})\n"
                f"   Chemistry: {fwb['chemistry_score']:.1f}% | Climax: {fwb['climax_count']}"
            )
        
        lines.append("\nPilih nomor untuk detail:")
        
        # Buat keyboard dengan nomor
        keyboard = []
        row = []
        for i in range(1, min(len(fwbs), 5) + 1):
            row.append(InlineKeyboardButton(str(i), callback_data=f"fwb_detail_{i}"))
        keyboard.append(row)
        
        if len(fwbs) > 5:
            row2 = []
            for i in range(6, min(len(fwbs), 10) + 1):
                row2.append(InlineKeyboardButton(str(i), callback_data=f"fwb_detail_{i}"))
            keyboard.append(row2)
        
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_main_v2")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("\n".join(lines), reply_markup=reply_markup)
    
    # =========================================================================
    # BACK TO MAIN
    # =========================================================================
    
    async def _back_to_main(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Kembali ke menu utama V2"""
        query = update.callback_query
        
        keyboard = [
            [InlineKeyboardButton("💕 PDKT", callback_data="pdkt_menu"),
             InlineKeyboardButton("💔 Mantan", callback_data="mantan_menu")],
            [InlineKeyboardButton("💞 FWB", callback_data="fwb_list"),
             InlineKeyboardButton("🔹 HTS", callback_data="hts_menu")],
            [InlineKeyboardButton("📊 Status", callback_data="status_menu"),
             InlineKeyboardButton("❌ Close", callback_data="close")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "💕 **Menu Utama V2**\n\n"
            "Pilih menu yang kamu inginkan:",
            reply_markup=reply_markup
        )
    
    # =========================================================================
    # UTILITY
    # =========================================================================
    
    def _format_time_ago(self, timestamp: float) -> str:
        """Format waktu yang lalu"""
        diff = time.time() - timestamp
        
        if diff < 60:
            return "baru saja"
        elif diff < 3600:
            return f"{int(diff / 60)} menit lalu"
        elif diff < 86400:
            return f"{int(diff / 3600)} jam lalu"
        else:
            return f"{int(diff / 86400)} hari lalu"


__all__ = ['CallbacksV2']
