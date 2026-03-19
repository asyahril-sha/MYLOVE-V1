#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - COMMANDS V2 (FIX FULL)
=============================================================================
Semua command baru untuk V2:
- PDKT commands
- Mantan commands
- FWB commands
- Threesome commands
- Memory & Story commands
- PROGRESS command untuk info leveling
=============================================================================
"""

import time
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from ..pdkt_natural.command_handler import PDKTCommandHandler
from ..pdkt_natural.mantan_manager import MantanManager
from ..relationship.fwb_manager import FWBManager
from ..relationship.hts_manager import HTSManager
from ..relationship.intimacy_v2 import IntimacySystemV2
from ..core.story_predictor import StoryPredictor
from ..memory.memory_bridge import MemoryBridge

logger = logging.getLogger(__name__)


class CommandsV2:
    """
    Handler untuk semua command V2
    """
    
    def __init__(self, 
                 pdkt_handler: PDKTCommandHandler,
                 mantan_manager: MantanManager,
                 fwb_manager: FWBManager,
                 hts_manager: HTSManager,
                 memory_bridge: MemoryBridge = None):
        
        self.pdkt = pdkt_handler
        self.mantan = mantan_manager
        self.fwb = fwb_manager
        self.hts = hts_manager
        self.memory = memory_bridge
        self.intimacy = IntimacySystemV2()
        self.story = StoryPredictor()
        
        logger.info("✅ CommandsV2 initialized")
    
    # =========================================================================
    # PDKT COMMANDS
    # =========================================================================
    
    async def cmd_pdkt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mulai PDKT dengan role tertentu"""
        await self.pdkt.handle_pdkt_command(update, context)
    
    async def cmd_pdktrandom(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mulai PDKT random (arah random 50:50)"""
        await self.pdkt.handle_pdktrandom_command(update, context)
    
    async def cmd_pdktlist(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lihat semua PDKT aktif"""
        await self.pdkt.handle_pdktlist_command(update, context)
    
    async def cmd_pdktdetail(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Detail PDKT (chemistry, arah, inner thoughts)"""
        await self.pdkt.handle_pdktdetail_command(update, context)
    
    async def cmd_pdktwho(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lihat arah PDKT (siapa ngejar siapa)"""
        await self.pdkt.handle_pdktwho_command(update, context)
    
    async def cmd_pausepdkt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Pause PDKT (waktu berhenti)"""
        await self.pdkt.handle_pausepdkt_command(update, context)
    
    async def cmd_resumepdkt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Resume PDKT yang di-pause"""
        await self.pdkt.handle_resumepdkt_command(update, context)
    
    async def cmd_stoppdkt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Hentikan PDKT (putus)"""
        await self.pdkt.handle_stoppdkt_command(update, context)
    
    # =========================================================================
    # MANTAN COMMANDS
    # =========================================================================
    
    async def cmd_mantanlist(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lihat daftar mantan (dari PDKT)"""
        user_id = update.effective_user.id
        mantan_list = self.mantan.get_mantan_list(user_id)
        
        if not mantan_list:
            await update.message.reply_text("💔 Belum ada mantan. PDKT dulu yuk!")
            return
        
        formatted = self.mantan.format_mantan_list(user_id)
        await update.message.reply_text(formatted, parse_mode='Markdown')
    
    async def cmd_mantan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lihat detail mantan"""
        args = context.args
        if not args:
            await update.message.reply_text("Gunakan: /mantan [nomor]")
            return
        
        try:
            idx = int(args[0])
            user_id = update.effective_user.id
            mantan = self.mantan.get_mantan_by_index(user_id, idx)
            
            if mantan:
                formatted = self.mantan.format_mantan_detail(mantan)
                await update.message.reply_text(formatted, parse_mode='Markdown')
            else:
                await update.message.reply_text("Mantan tidak ditemukan")
        except ValueError:
            await update.message.reply_text("Nomor tidak valid")
    
    async def cmd_fwbrequest(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Request jadi FWB dengan mantan"""
        args = context.args
        if not args:
            await update.message.reply_text("Gunakan: /fwbrequest [nomor mantan]")
            return
        
        try:
            idx = int(args[0])
            user_id = update.effective_user.id
            user_name = update.effective_user.first_name or "User"
            
            mantan = self.mantan.get_mantan_by_index(user_id, idx)
            if not mantan:
                await update.message.reply_text("Mantan tidak ditemukan")
                return
            
            # Proses request
            result = await self.mantan.request_fwb(
                user_id=user_id,
                mantan_id=mantan['mantan_id'],
                message=' '.join(args[1:]) if len(args) > 1 else ""
            )
            
            await update.message.reply_text(result['message'], parse_mode='Markdown')
            
        except ValueError:
            await update.message.reply_text("Nomor tidak valid")
    
    # =========================================================================
    # FWB COMMANDS
    # =========================================================================
    
    async def cmd_fwblist(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lihat daftar FWB"""
        user_id = update.effective_user.id
        args = context.args
        show_all = args and args[0].lower() == 'all'
        
        formatted = await self.fwb.format_fwb_list(user_id, show_all)
        await update.message.reply_text(formatted, parse_mode='Markdown')
    
    async def cmd_fwb_call(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Panggil FWB berdasarkan nomor (format: /fwb-1)"""
        text = update.message.text
        user_id = update.effective_user.id
        
        try:
            # Parse /fwb-1
            idx = int(text.replace('/fwb-', ''))
            fwb = await self.fwb.get_fwb_by_index(user_id, idx)
            
            if fwb:
                # Set session ke FWB ini
                context.user_data['current_fwb'] = fwb
                context.user_data['current_mode'] = 'fwb'
                context.user_data['bot_name'] = fwb['bot_name']
                context.user_data['current_role'] = fwb['role']
                
                await update.message.reply_text(
                    f"💕 **{fwb['bot_name']}**\n\n"
                    f"Halo sayang, udah lama gak chat. Kangen... 🥰"
                )
                
                # Record interaction
                await self.fwb.record_interaction(user_id, fwb['fwb_id'])
            else:
                await update.message.reply_text("FWB tidak ditemukan")
        except:
            await update.message.reply_text("Format salah. Gunakan: /fwb-1")
    
    async def cmd_fwb_pause(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Pause FWB"""
        args = context.args
        if not args:
            await update.message.reply_text("Gunakan: /fwb pause [nomor]")
            return
        
        try:
            idx = int(args[0])
            user_id = update.effective_user.id
            fwb = await self.fwb.get_fwb_by_index(user_id, idx)
            
            if fwb:
                result = await self.fwb.pause_fwb(user_id, fwb['fwb_id'])
                await update.message.reply_text(
                    f"⏸️ **FWB dengan {result['bot_name']} di-pause**\n\n"
                    f"{result.get('message', '')}"
                )
            else:
                await update.message.reply_text("FWB tidak ditemukan")
        except ValueError:
            await update.message.reply_text("Nomor tidak valid")
    
    async def cmd_fwb_resume(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Resume FWB"""
        args = context.args
        if not args:
            await update.message.reply_text("Gunakan: /fwb resume [nomor]")
            return
        
        try:
            idx = int(args[0])
            user_id = update.effective_user.id
            fwb = await self.fwb.get_fwb_by_index(user_id, idx)
            
            if fwb:
                result = await self.fwb.resume_fwb(user_id, fwb['fwb_id'])
                await update.message.reply_text(
                    f"▶️ **FWB dengan {result['bot_name']} dilanjutkan**\n\n"
                    f"{result['message']}"
                )
            else:
                await update.message.reply_text("FWB tidak ditemukan")
        except ValueError:
            await update.message.reply_text("Nomor tidak valid")
    
    async def cmd_fwb_end(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Akhiri FWB"""
        args = context.args
        if not args:
            await update.message.reply_text("Gunakan: /fwb end [nomor]")
            return
        
        try:
            idx = int(args[0])
            user_id = update.effective_user.id
            fwb = await self.fwb.get_fwb_by_index(user_id, idx)
            
            if fwb:
                result = await self.fwb.end_fwb(user_id, fwb['fwb_id'])
                await update.message.reply_text(
                    f"💔 **FWB dengan {result['bot_name']} diakhiri**\n\n"
                    f"{result['message']}"
                )
            else:
                await update.message.reply_text("FWB tidak ditemukan")
        except ValueError:
            await update.message.reply_text("Nomor tidak valid")
    
    # =========================================================================
    # HTS COMMANDS
    # =========================================================================
    
    async def cmd_htslist(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lihat daftar HTS"""
        user_id = update.effective_user.id
        args = context.args
        show_all = args and args[0].lower() == 'all'
        
        formatted = await self.hts.format_hts_list(user_id, show_all)
        await update.message.reply_text(formatted, parse_mode='Markdown')
    
    async def cmd_hts_call(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Panggil HTS berdasarkan nomor (format: /hts-1)"""
        text = update.message.text
        user_id = update.effective_user.id
        
        try:
            # Parse /hts-1
            idx = int(text.replace('/hts-', ''))
            hts = await self.hts.get_hts_by_index(user_id, idx)
            
            if hts:
                # Set session ke HTS ini
                context.user_data['current_hts'] = hts
                context.user_data['current_mode'] = 'hts'
                context.user_data['bot_name'] = hts['bot_name']
                context.user_data['current_role'] = hts['role']
                
                await update.message.reply_text(
                    f"💕 **{hts['bot_name']}**\n\n"
                    f"Halo, udah lama gak intim. Ayo... 🔥"
                )
                
                # Record interaction
                await self.hts.record_interaction(user_id, hts['hts_id'])
            else:
                await update.message.reply_text("HTS tidak ditemukan")
        except:
            await update.message.reply_text("Format salah. Gunakan: /hts-1")
    
    # =========================================================================
    # PROGRESS COMMAND (BARU)
    # =========================================================================
    
    async def cmd_progress(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Menampilkan progress level, boost info, dan story arc
        TAPI BOT TIDAK TAHU BAHWA USER LIHAT INI
        """
        user_id = update.effective_user.id
        session_id = context.user_data.get('current_session')
        bot_name = context.user_data.get('bot_name', 'Bot')
        role = context.user_data.get('current_role', 'unknown')
        
        if not session_id:
            await update.message.reply_text(
                "❌ Tidak ada session aktif.\n"
                "Mulai dengan /start atau /pdkt dulu ya!"
            )
            return
        
        try:
            # ===== 1. AMBIL DATA LEVELING =====
            status = await self.intimacy.get_status(session_id)
            
            if not status:
                await update.message.reply_text("❌ Gagal mengambil data leveling.")
                return
            
            # ===== 2. PROGRESS BAR VISUAL =====
            progress = status.get('progress', 0)
            bar_length = 20
            filled = int(progress / 100 * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            # ===== 3. INFO NEXT LEVEL =====
            current_level = status.get('current_level', 1)
            if current_level < 12:
                next_level = current_level + 1
                next_level_in = status.get('next_level_in', 0)
                next_text = f"{next_level_in} menit lagi ke Level {next_level}"
            else:
                next_text = "✅ **MAX LEVEL!** Butuh aftercare untuk reset."
            
            # ===== 4. BOOST INFO (APA YANG CEPETIN) =====
            boost_info = [
                "🔥 **ACTIVITY BOOST:**",
                "• Chat biasa: 1.0x",
                "• Godaan / Flirt: 1.3x",
                "• Ciuman: 1.5x",
                "• Sentuhan: 1.5x",
                "• Intim: 2.0x",
                "• Climax: 3.0x 🔥🔥🔥",
            ]
            
            # ===== 5. ANTI-BOOST (APA YANG BIKIN LAMBAT) =====
            antiboost_info = [
                "⚠️ **YANG BIKIN LAMBAT:**",
                "• Jawaban pendek / cuek",
                "• Konflik / marah-marah",
                "• Jarang chat (idle lama)",
                "• Topik monoton",
            ]
            
            # ===== 6. STORY ARC =====
            current_arc = self.story.story_arcs.get(session_id, 'get_to_know')
            arc_desc = self.story.get_arc_description(current_arc)
            
            arc_info = [
                f"📖 **ARAH CERITA:** {current_arc.replace('_', ' ').title()}",
                f"_{arc_desc}_",
            ]
            
            # ===== 7. TIPS BERDASARKAN ARC =====
            tips_map = {
                'get_to_know': "💡 **Tips:** Sering chat biar cepet akrab. Tanya tentang kesehariannya.",
                'friendship': "💡 **Tips:** Curhat, cerita kegiatan sehari-hari, bangun kepercayaan.",
                'romance': "💡 **Tips:** Puji dia, bilang 'sayang', ajak ngobrol romantis.",
                'intimate': "💡 **Tips:** Ajak intim, sentuhan, climax buat naik level cepet!",
                'conflict': "💡 **Tips:** Jangan lanjutin konflik. Minta maaf, tenangkan dia.",
                'reconciliation': "💡 **Tips:** Perbaiki hubungan, buat dia nyaman lagi.",
                'deep_connection': "💡 **Tips:** Bahas hal-hal dalam, masa depan, perasaan.",
                'nostalgia': "💡 **Tips:** Ingat kenangan manis, flashback ke momen indah."
            }
            tips = tips_map.get(current_arc, "💡 **Tips:** Chat rutin, variasi topik, jangan cuek.")
            
            # ===== 8. GABUNGKAN SEMUA =====
            response_lines = [
                f"📊 **PROGRESS HUBUNGAN dengan {bot_name}**\n",
                f"Level {current_level} → Level {next_level if current_level < 12 else 'MAX'}",
                f"{bar} {progress:.0f}%",
                f"{next_text}\n",
                "\n".join(boost_info),
                "",
                "\n".join(antiboost_info),
                "",
                "\n".join(arc_info),
                "",
                tips,
                "",
                "_Bot tidak tahu kamu lihat ini... 🤫_"
            ]
            
            response = "\n".join(response_lines)
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in progress command: {e}")
            await update.message.reply_text(
                "❌ Terjadi kesalahan. Coba lagi nanti."
            )
    
    # =========================================================================
    # MEMORY COMMANDS
    # =========================================================================
    
    async def cmd_memory(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Lihat ringkasan memory"""
        if not self.memory:
            await update.message.reply_text("❌ Memory system tidak tersedia.")
            return
        
        user_id = update.effective_user.id
        summary = await self.memory.format_memory_summary()
        await update.message.reply_text(summary, parse_mode='Markdown')
    
    async def cmd_flashback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate flashback random"""
        if not self.memory:
            await update.message.reply_text("❌ Memory system tidak tersedia.")
            return
        
        trigger = ' '.join(context.args) if context.args else None
        flashback = await self.memory.generate_flashback(trigger)
        
        if flashback:
            await update.message.reply_text(f"💭 {flashback}")
        else:
            await update.message.reply_text("Belum ada kenangan untuk di-flashback.")


__all__ = ['CommandsV2']
