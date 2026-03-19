#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - BOT HANDLERS (FIX LENGKAP)
=============================================================================
Semua handlers untuk MYLOVE Ultimate V2:
- Command handlers
- Message handler dengan AI Engine
- Callback handler
- FIX: Terhubung ke AI engine untuk respons natural
=============================================================================
"""

import time
import logging
import random
import re
import asyncio
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from config import settings
from utils.helpers import sanitize_input, format_number, truncate_text
from utils.logger import logger
from session.unique_id import id_generator
from database.models import Constants

# =============================================================================
# IMPORT AI ENGINE V2
# =============================================================================
try:
    from core.ai_engine_v2 import AIEngineV2 as AIEngineV2
    import core.ai_engine_v2
    AI_ENGINE_AVAILABLE = True
except ImportError:
    AI_ENGINE_AVAILABLE = False
    logger.warning("AI Engine V2 not available, using fallback responses")


# =============================================================================
# 1. COMMAND HANDLERS
# =============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /start command"""
    user = update.effective_user
    logger.info(f"User {user.id} (@{user.username}) started the bot")
    
    keyboard = [
        [InlineKeyboardButton("👩 Ipar", callback_data="role_ipar"),
         InlineKeyboardButton("👩‍💼 Teman Kantor", callback_data="role_teman_kantor")],
        [InlineKeyboardButton("👩 Janda", callback_data="role_janda"),
         InlineKeyboardButton("💃 Pelakor", callback_data="role_pelakor")],
        [InlineKeyboardButton("👰 Istri Orang", callback_data="role_istri_orang"),
         InlineKeyboardButton("💕 PDKT", callback_data="role_pdkt")],
        [InlineKeyboardButton("👧 Sepupu", callback_data="role_sepupu"),
         InlineKeyboardButton("👩‍🎓 Teman SMA", callback_data="role_teman_sma")],
        [InlineKeyboardButton("💔 Mantan", callback_data="role_mantan")],
        [InlineKeyboardButton("🎭 Threesome", callback_data="threesome_menu"),
         InlineKeyboardButton("❓ Bantuan", callback_data="help")],
        [InlineKeyboardButton("✅ Setuju 18+", callback_data="agree_18")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"💕 **Halo {user.first_name}!**\n\n"
        "Selamat datang di **MYLOVE ULTIMATE VERSI 2**\n"
        "Virtual Pendamping dengan PDKT Natural 99%\n\n"
        "⚠️ **Konten 18+**\n"
        "Dengan melanjutkan, kamu menyatakan sudah berusia 18+.\n\n"
        "**Pilih role yang kamu inginkan:**"
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return Constants.SELECTING_ROLE


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "📋 **DAFTAR PERINTAH**\n\n"
        "**Perintah Dasar:**\n"
        "/start - Mulai bot dan pilih role\n"
        "/help - Tampilkan bantuan ini\n"
        "/status - Cek status session\n"
        "/cancel - Batalkan sesi\n\n"
        
        "**PDKT Commands:**\n"
        "/pdkt [role] - Mulai PDKT natural\n"
        "/pdktrandom - Mulai PDKT random\n"
        "/pdktlist - Lihat daftar PDKT\n"
        "/pdktdetail [id] - Detail PDKT\n"
        "/pdktwho [id] - Lihat arah PDKT\n"
        "/pausepdkt [id] - Pause PDKT\n"
        "/resumepdkt [id] - Resume PDKT\n"
        "/stoppdkt [id] - Hentikan PDKT\n\n"
        
        "**Mantan & FWB:**\n"
        "/mantanlist - Lihat daftar mantan\n"
        "/fwbrequest [id] - Request jadi FWB\n"
        "/fwblist - Lihat daftar FWB\n"
        "/fwb pause [id] - Jeda FWB\n"
        "/fwb resume [id] - Lanjutkan FWB\n"
        "/fwb end [id] - Akhiri FWB\n\n"
        
        "**HTS:**\n"
        "/htslist - Lihat TOP 10 HTS\n"
        "/hts- [nomor] - Panggil HTS\n\n"
        
        "**Memory:**\n"
        "/memory - Ringkasan memory\n"
        "/flashback - Flashback random"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    user_id = update.effective_user.id
    
    current_role = context.user_data.get('current_role', 'Belum dipilih')
    bot_name = context.user_data.get('bot_name', '')
    intimacy_level = context.user_data.get('intimacy_level', 1)
    total_chats = context.user_data.get('total_chats', 0)
    current_location = context.user_data.get('current_location', 'Tidak diketahui')
    
    status_text = (
        f"📊 **STATUS SESSION**\n\n"
        f"👤 **User ID:** `{user_id}`\n"
        f"🎭 **Role:** {current_role.title() if current_role != 'Belum dipilih' else current_role}\n"
        f"💕 **Bot:** {bot_name}\n"
        f"📈 **Intimacy Level:** {intimacy_level}/12\n"
        f"💬 **Total Chats:** {total_chats}\n"
        f"📍 **Lokasi:** {current_location[:50]}...\n"
    )
    
    if 'current_session' in context.user_data:
        status_text += f"\n🆔 **Session ID:**\n`{context.user_data['current_session']}`"
    
    await update.message.reply_text(status_text, parse_mode='Markdown')


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /cancel command"""
    context.user_data.clear()
    await update.message.reply_text(
        "❌ **Sesi dibatalkan**\n\n"
        "Ketik /start untuk memulai lagi."
    )
    return ConversationHandler.END


# =============================================================================
# 2. DUMMY COMMANDS (UNTUK IMPORT)
# =============================================================================

async def dominant_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚡ Mode dominant diaktifkan.")

async def pause_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['paused'] = True
    await update.message.reply_text("⏸️ Sesi dijeda.")

async def unpause_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['paused'] = False
    await update.message.reply_text("▶️ Sesi dilanjutkan.")

async def close_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop('current_session', None)
    context.user_data.pop('current_role', None)
    await update.message.reply_text("🔒 Percakapan ditutup.")

async def end_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("🏁 Sesi diakhiri.")

async def jadipacar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💕 **Jadi Pacar**")

async def break_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💔 **Break**")

async def unbreak_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 **Unbreak**")

async def breakup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💔 **Putus**")

async def fwb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💞 **Mode FWB**")

async def htslist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📋 **DAFTAR HTS**\n\nGunakan /hts-1 untuk memanggil.")

async def fwblist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📋 **DAFTAR FWB**\n\nGunakan /fwb-1 untuk memanggil.")

async def tophts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏆 **TOP 10 HTS**")

async def myclimax_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💦 **STATISTIK CLIMAX**")

async def climaxrank_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏆 **RANKING CLIMAX**")

async def climaxhistory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📜 **HISTORY CLIMAX**")

async def explore_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🗺️ **LOKASI TERSEDIA**")

async def go_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if args:
        location = " ".join(args)
        context.user_data['current_location'] = location
        await update.message.reply_text(f"📍 Pindah ke **{location}**")
    else:
        await update.message.reply_text("❌ Gunakan: /go [nama lokasi]")

async def positions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💃 **POSISI TERSEDIA**")

async def risk_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚠️ **RISK ASSESSMENT**")

async def mood_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎭 **MOOD BOT**: Senang 😊")

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != settings.admin_id:
        await update.message.reply_text("❌ Perintah ini hanya untuk admin.")
        return
    await update.message.reply_text("🛠️ **MENU ADMIN**")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 **STATISTIK BOT**")

async def db_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🗄️ **STATISTIK DATABASE**")

async def list_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👥 **DAFTAR USER**")

async def get_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👤 **DETAIL USER**")

async def force_reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("🔄 **RESET**")

async def backup_db_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💾 **BACKUP DATABASE**")

async def vacuum_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧹 **VACUUM DATABASE**")

async def memory_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧠 **STATISTIK MEMORI**")

async def reload_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 **RELOAD CONFIG**")


# =============================================================================
# 3. MESSAGE HANDLER (DENGAN AI ENGINE)
# =============================================================================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk semua pesan teks
    - Menggunakan AI Engine V2 untuk respons natural
    - Fallback ke respons sederhana jika AI tidak tersedia
    """
    try:
        user = update.effective_user
        user_message = update.message.text
        user_id = user.id
        user_name = user.first_name or "User"
        session_id = context.user_data.get('current_session')
        
        # Cek pause
        if context.user_data.get('paused', False):
            await update.message.reply_text("⏸️ Sesi sedang dijeda. Ketik /unpause untuk melanjutkan.")
            return
        
        # Ambil data dari context
        bot_name = context.user_data.get('bot_name', 'Aku')
        role = context.user_data.get('current_role', 'pdkt')
        level = context.user_data.get('intimacy_level', 1)
        total_chats = context.user_data.get('total_chats', 0)
        
        logger.info(f"📨 Message from {user_name}: {user_message[:50]}...")
        
        # ===== GENERATE RESPONSE DENGAN AI ENGINE =====
        response = None
        
        if AI_ENGINE_AVAILABLE and settings.deepseek_api_key:
            try:
                # Inisialisasi AI engine
                ai_engine = AIEngineV2(api_key=settings.deepseek_api_key)
                
                # Siapkan konteks
                context_data = {
                    'role': role,
                    'bot_name': bot_name,
                    'level': level,
                    'user_name': user_name,
                    'mood': context.user_data.get('mood', 'netral'),
                    'location': context.user_data.get('current_location', 'Tidak diketahui'),
                    'clothing': context.user_data.get('current_clothing', 'Pakaian biasa'),
                    'total_chats': total_chats
                }
                
                # Generate response dari AI
                response = await ai_engine.generate_response(
                    user_id=user_id,
                    session_id=session_id,
                    user_message=user_message,
                    context=context_data
                )
                
                logger.info(f"✅ AI response generated ({len(response)} chars)")
                
            except Exception as e:
                logger.error(f"AI Engine error: {e}")
                # Fallback ke response manual
        
        # ===== FALLBACK RESPONSE JIKA AI GAGAL =====
        if not response:
            # Template fallback sederhana
            fallbacks = [
                f"{bot_name} dengar kok. Kamu bilang: {user_message[:50]}...",
                f"Hmm... {bot_name} mikir dulu ya. Kamu tadi bilang apa?",
                f"{user_name}, {bot_name} lagi dengerin. Lanjutkan...",
                f"{bot_name} ngerti. Cerita lagi dong...",
            ]
            response = random.choice(fallbacks)
        
        # ===== UPDATE STATISTIK =====
        context.user_data['total_chats'] = total_chats + 1
        
        # Update intimacy level sederhana (setiap 5 chat)
        if (total_chats + 1) % 5 == 0:
            new_level = min(12, level + 1)
            context.user_data['intimacy_level'] = new_level
            logger.info(f"Level up! {level} → {new_level}")
        
        # Simpan pesan terakhir
        context.user_data['last_message'] = user_message
        context.user_data['last_response'] = response
        
        # Kirim response
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in message_handler: {e}")
        await update.message.reply_text(
            "❌ Maaf, terjadi kesalahan. Coba lagi nanti."
        )


# =============================================================================
# 4. CALLBACK HANDLER
# =============================================================================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk semua callback query"""
    try:
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = update.effective_user.id
        
        logger.info(f"🔄 Callback: {data}")
        
        if data == "agree_18":
            await query.edit_message_text("✅ Terima kasih telah menyetujui syarat 18+.")
        
        elif data.startswith('role_'):
            role = data.replace('role_', '')
            await query.edit_message_text(f"💕 Kamu memilih role: **{role.title()}**")
        
        elif data == "back_to_main":
            keyboard = [
                [InlineKeyboardButton("👩 Ipar", callback_data="role_ipar"),
                 InlineKeyboardButton("👩‍💼 Teman Kantor", callback_data="role_teman_kantor")],
                [InlineKeyboardButton("👩 Janda", callback_data="role_janda"),
                 InlineKeyboardButton("💃 Pelakor", callback_data="role_pelakor")],
                [InlineKeyboardButton("👰 Istri Orang", callback_data="role_istri_orang"),
                 InlineKeyboardButton("💕 PDKT", callback_data="role_pdkt")],
                [InlineKeyboardButton("👧 Sepupu", callback_data="role_sepupu"),
                 InlineKeyboardButton("👩‍🎓 Teman SMA", callback_data="role_teman_sma")],
                [InlineKeyboardButton("💔 Mantan", callback_data="role_mantan")],
                [InlineKeyboardButton("🎭 Threesome", callback_data="threesome_menu"),
                 InlineKeyboardButton("❓ Bantuan", callback_data="help")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("💕 **Pilih role:**", reply_markup=reply_markup)
        
        elif data == "threesome_menu":
            keyboard = [
                [InlineKeyboardButton("🎭 Lihat Kombinasi", callback_data="threesome_list")],
                [InlineKeyboardButton("💕 HTS + HTS", callback_data="threesome_type_hts")],
                [InlineKeyboardButton("💞 FWB + FWB", callback_data="threesome_type_fwb")],
                [InlineKeyboardButton("💘 HTS + FWB", callback_data="threesome_type_mix")],
                [InlineKeyboardButton("❌ Kembali", callback_data="back_to_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "🎭 **MODE THREESOME**\n\nPilih tipe threesome:",
                reply_markup=reply_markup
            )
        
        else:
            await query.edit_message_text(f"✅ {data} diterima")
            
    except Exception as e:
        logger.error(f"Error in callback_handler: {e}")


# =============================================================================
# 5. HTS/FWB CALL HANDLERS
# =============================================================================

async def hts_call_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /hts- [id]"""
    text = update.message.text
    try:
        idx = int(text.replace('/hts-', ''))
        await update.message.reply_text(f"✅ Memanggil HTS #{idx}")
    except:
        await update.message.reply_text("❌ Format salah. Gunakan: /hts-1")


async def fwb_call_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /fwb- [id]"""
    text = update.message.text
    try:
        idx = int(text.replace('/fwb-', ''))
        await update.message.reply_text(f"✅ Memanggil FWB #{idx}")
    except:
        await update.message.reply_text("❌ Format salah. Gunakan: /fwb-1")


async def continue_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /continue"""
    await update.message.reply_text("🔄 Melanjutkan session...")


# =============================================================================
# 6. EXPORT ALL HANDLERS
# =============================================================================

__all__ = [
    # Command handlers
    'start_command', 'help_command', 'status_command', 'cancel_command',
    'dominant_command', 'pause_command', 'unpause_command',
    'close_command', 'end_command', 'jadipacar_command',
    'break_command', 'unbreak_command', 'breakup_command', 'fwb_command',
    'htslist_command', 'fwblist_command', 'tophts_command',
    'myclimax_command', 'climaxrank_command', 'climaxhistory_command',
    'explore_command', 'go_command', 'positions_command', 'risk_command',
    'mood_command', 'admin_command', 'stats_command', 'db_stats_command',
    'list_users_command', 'get_user_command', 'force_reset_command',
    'backup_db_command', 'vacuum_command', 'memory_stats_command',
    'reload_command',
    
    # Message & callback handlers
    'message_handler', 'callback_handler',
    
    # Special handlers
    'hts_call_handler', 'fwb_call_handler', 'continue_handler',
]
