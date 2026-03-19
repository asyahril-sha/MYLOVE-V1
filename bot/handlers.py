#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - BOT HANDLERS (FIX FULL DENGAN MEMORY)
=============================================================================
Semua handlers untuk MYLOVE Ultimate V2 dengan memory system lengkap:
- Working memory (short-term)
- Episodic memory (sequence)
- Semantic memory (facts)
- State tracker (current state)
- Relationship memory (history)
=============================================================================
"""

import time
import logging
import random
import re
import asyncio
import sys
import os
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
# IMPORT AI ENGINE COMPLETE (DENGAN MEMORY)
# =============================================================================
try:
    from core.ai_engine_complete import AIEngineComplete
    AI_ENGINE_AVAILABLE = True
    print("🔥🔥🔥 AI ENGINE COMPLETE WITH MEMORY LOADED! 🔥🔥🔥")
    logger.info("✅ AI Engine Complete loaded successfully")
except Exception as e:
    AI_ENGINE_AVAILABLE = False
    print(f"❌❌❌ GAGAL LOAD AI ENGINE: {e} ❌❌❌")
    logger.error(f"Failed to load AI engine: {e}")

# =============================================================================
# IMPORT DYNAMICS COMPONENTS
# =============================================================================
try:
    from dynamics.location import LocationSystem
    from dynamics.clothing import ClothingSystem
    from dynamics.position import PositionSystem
    from dynamics.name_generator import get_name_generator
    from dynamics.location_validator import LocationValidator
    
    DYNAMICS_AVAILABLE = True
    loc_system = LocationSystem()
    cloth_system = ClothingSystem()
    pos_system = PositionSystem()
    name_gen = get_name_generator()
    loc_validator = LocationValidator()
    
    print("✅ Dynamics components loaded")
except Exception as e:
    DYNAMICS_AVAILABLE = False
    print(f"⚠️ Dynamics components not loaded: {e}")

# =============================================================================
# VARIABLE GLOBAL UNTUK UPTIME
# =============================================================================
START_TIME = time.time()

def format_uptime(seconds: float) -> str:
    """Format uptime ke string yang mudah dibaca"""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

# =============================================================================
# STORE ACTIVE AI ENGINES (per user session)
# =============================================================================
active_engines = {}  # {session_id: AIEngineComplete}

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
        "Virtual Pendamping dengan Memory System seperti Manusia\n\n"
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
        "/flashback - Flashback random\n"
        "/progress - Progress hubungan\n\n"
        
        "**Admin:**\n"
        "/admin - Menu admin\n"
        "/stats - Statistik bot\n"
        "/db_stats - Statistik database\n"
        "/list_users - Daftar user\n"
        "/get_user [id] - Detail user\n"
        "/backup_db - Backup database\n"
        "/debug - Info debug"
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
    # Bersihkan session
    session_id = context.user_data.get('current_session')
    if session_id and session_id in active_engines:
        await active_engines[session_id].end_session()
        del active_engines[session_id]
    
    context.user_data.clear()
    
    await update.message.reply_text(
        "❌ **Sesi dibatalkan**\n\n"
        "Ketik /start untuk memulai lagi."
    )
    return ConversationHandler.END


# =============================================================================
# 2. ADMIN COMMANDS
# =============================================================================

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command"""
    user_id = update.effective_user.id
    
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Perintah ini hanya untuk admin.")
        return
    
    menu = (
        "🛠️ **MENU ADMIN**\n\n"
        "**Database:**\n"
        "/db_stats - Statistik database\n"
        "/backup_db - Backup database\n"
        "/vacuum - Optimasi database\n"
        "/recover list - Lihat backup\n"
        "\n"
        "**User:**\n"
        "/list_users - Daftar user\n"
        "/get_user [id] - Detail user\n"
        "/force_reset - Reset user\n"
        "\n"
        "**Memory:**\n"
        "/memory_stats - Statistik memory\n"
        "/flashback - Test flashback\n"
        "\n"
        "**System:**\n"
        "/stats - Statistik bot\n"
        "/debug - Info debug\n"
        "/reload - Reload config\n"
    )
    
    await update.message.reply_text(menu, parse_mode='Markdown')


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command"""
    user_id = update.effective_user.id
    
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Perintah ini hanya untuk admin.")
        return
    
    try:
        stats = {
            'total_users': 1,
            'total_sessions': len(active_engines),
            'total_messages': 0,
            'total_pdkt': 0,
            'total_mantan': 0,
            'total_fwb': 0,
            'total_hts': 0,
            'uptime': time.time() - START_TIME
        }
        
        text = (
            f"📊 **STATISTIK BOT**\n\n"
            f"👥 Total Users: {stats['total_users']}\n"
            f"📁 Active Sessions: {stats['total_sessions']}\n"
            f"💬 Total Messages: {stats['total_messages']}\n"
            f"💕 Total PDKT: {stats['total_pdkt']}\n"
            f"💔 Total Mantan: {stats['total_mantan']}\n"
            f"💞 Total FWB: {stats['total_fwb']}\n"
            f"🔹 Total HTS: {stats['total_hts']}\n"
            f"⏱️ Uptime: {format_uptime(stats['uptime'])}\n"
        )
        
        await update.message.reply_text(text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in stats_command: {e}")
        await update.message.reply_text("📊 **STATISTIK BOT**\n\n(Data belum tersedia)")


async def debug_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /debug command"""
    user_id = update.effective_user.id
    
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Perintah ini hanya untuk admin.")
        return
    
    debug_info = (
        f"🔍 **DEBUG INFO**\n\n"
        f"Python: {sys.version}\n"
        f"Platform: {sys.platform}\n"
        f"CWD: {os.getcwd()}\n"
        f"AI Engine: {'AVAILABLE' if AI_ENGINE_AVAILABLE else 'NOT AVAILABLE'}\n"
        f"Dynamics: {'AVAILABLE' if DYNAMICS_AVAILABLE else 'NOT AVAILABLE'}\n"
        f"Active Sessions: {len(active_engines)}\n"
        f"User Data Keys: {list(context.user_data.keys())}\n"
        f"Current Session: {context.user_data.get('current_session')}\n"
        f"Current Role: {context.user_data.get('current_role')}\n"
        f"Intimacy Level: {context.user_data.get('intimacy_level', 1)}\n"
        f"Total Chats: {context.user_data.get('total_chats', 0)}\n"
    )
    
    await update.message.reply_text(debug_info, parse_mode='Markdown')


# =============================================================================
# 3. MEMORY COMMANDS
# =============================================================================

async def memory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /memory command - Lihat ringkasan memory"""
    session_id = context.user_data.get('current_session')
    
    if not session_id or session_id not in active_engines:
        await update.message.reply_text("❌ Tidak ada session aktif.")
        return
    
    ai_engine = active_engines[session_id]
    summary = await ai_engine.get_memory_summary()
    
    await update.message.reply_text(summary, parse_mode='Markdown')


async def flashback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /flashback command - Generate flashback random"""
    session_id = context.user_data.get('current_session')
    
    if not session_id or session_id not in active_engines:
        await update.message.reply_text("❌ Tidak ada session aktif.")
        return
    
    ai_engine = active_engines[session_id]
    trigger = ' '.join(context.args) if context.args else None
    
    flashback = await ai_engine._generate_flashback(trigger)
    
    if flashback:
        await update.message.reply_text(f"💭 {flashback}")
    else:
        await update.message.reply_text("Belum ada kenangan untuk di-flashback.")


async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /progress command - Lihat progress hubungan"""
    session_id = context.user_data.get('current_session')
    
    if not session_id or session_id not in active_engines:
        await update.message.reply_text("❌ Tidak ada session aktif.")
        return
    
    ai_engine = active_engines[session_id]
    
    # Dapatkan data dari relationship memory
    role = context.user_data.get('current_role')
    instance_id = context.user_data.get('instance_id')
    
    if not role or not instance_id:
        await update.message.reply_text("❌ Data hubungan tidak lengkap.")
        return
    
    rel = await ai_engine.relationship.get_relationship(
        user_id=update.effective_user.id,
        role=role,
        instance_id=instance_id
    )
    
    if not rel:
        await update.message.reply_text("❌ Hubungan tidak ditemukan.")
        return
    
    level_info = await ai_engine.relationship.get_level_info(
        user_id=update.effective_user.id,
        role=role,
        instance_id=instance_id
    )
    
    # Buat progress bar
    if level_info['current_level'] < 12:
        bar_length = 20
        filled = int(level_info['percentage'] / 100 * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        progress_text = f"{bar} {level_info['percentage']}%"
        next_text = f"{level_info['remaining_minutes']:.0f} menit ke level {level_info['next_level']}"
    else:
        progress_text = "████████████████████ MAX"
        next_text = "✅ Level MAX! Butuh aftercare untuk reset."
    
    # Boost info
    boost_info = [
        "🔥 **ACTIVITY BOOST:**",
        "• Chat biasa: 1.0x",
        "• Godaan / Flirt: 1.3x",
        "• Ciuman: 1.5x",
        "• Sentuhan: 1.5x",
        "• Intim: 2.0x",
        "• Climax: 3.0x 🔥🔥🔥",
    ]
    
    # Anti-boost
    antiboost_info = [
        "⚠️ **YANG BIKIN LAMBAT:**",
        "• Jawaban pendek / cuek",
        "• Konflik / marah-marah",
        "• Jarang chat (idle lama)",
        "• Topik monoton",
    ]
    
    # Chemistry level
    chem_level = await ai_engine.relationship.get_chemistry_level(
        user_id=update.effective_user.id,
        role=role,
        instance_id=instance_id
    )
    
    chem_emoji = {
        'dingin': '❄️',
        'biasa': '😐',
        'hangat': '🔥',
        'cocok': '💕',
        'sangat_cocok': '💞',
        'soulmate': '✨'
    }.get(chem_level, '❓')
    
    # State saat ini
    state = ai_engine.state.get_state_for_prompt()
    
    response = (
        f"📊 **PROGRESS HUBUNGAN**\n\n"
        f"👤 **{rel['bot_name']}** ({role.title()})\n"
        f"📈 Level {rel['current_level']}/12\n"
        f"{progress_text}\n"
        f"{next_text}\n\n"
        f"{chem_emoji} **Chemistry:** {chem_level.title()}\n"
        f"🎭 **Situasi:** {state}\n\n"
        f"{chr(10).join(boost_info)}\n\n"
        f"{chr(10).join(antiboost_info)}\n\n"
        f"📊 **Statistik:**\n"
        f"• Total Chat: {rel['total_chats']}\n"
        f"• Total Intim: {rel['total_intim_sessions']}\n"
        f"• Total Climax: {rel['total_climax']}\n"
        f"• Total Durasi: {rel['total_duration_minutes']:.0f} menit\n\n"
        f"_Bot tidak tahu kamu lihat ini... 🤫_"
    )
    
    await update.message.reply_text(response, parse_mode='Markdown')


# =============================================================================
# 4. MAIN MESSAGE HANDLER (DENGAN AI ENGINE COMPLETE)
# =============================================================================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk semua pesan teks
    - Menggunakan AI Engine Complete dengan semua memory
    - Tracking lokasi, pakaian, mood, dll
    - Bisa flashback dan proactive
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
        instance_id = context.user_data.get('instance_id')
        rel_type = context.user_data.get('rel_type', 'non_pdkt')
        
        logger.info(f"📨 Message from {user_name}: {user_message[:50]}...")
        
        # ===== CEK ATAU BUAT AI ENGINE =====
        if session_id not in active_engines:
            if not AI_ENGINE_AVAILABLE:
                # Fallback sederhana
                await update.message.reply_text(
                    f"{bot_name} dengar kok. Cerita lagi dong..."
                )
                return
            
            # Buat AI engine baru
            try:
                ai_engine = AIEngineComplete(
                    api_key=settings.deepseek_api_key,
                    user_id=user_id,
                    session_id=session_id
                )
                
                # Start session
                await ai_engine.start_session(
                    role=role,
                    bot_name=bot_name,
                    rel_type=rel_type,
                    instance_id=instance_id
                )
                
                active_engines[session_id] = ai_engine
                logger.info(f"✅ New AI engine created for session {session_id}")
                
            except Exception as e:
                logger.error(f"Failed to create AI engine: {e}")
                await update.message.reply_text(
                    f"{bot_name} dengar kok. Cerita lagi dong..."
                )
                return
        
        ai_engine = active_engines[session_id]
        
        # ===== DETEKSI PERUBAHAN LOKASI =====
        new_location = None
        if DYNAMICS_AVAILABLE and loc_system:
            detected = loc_system.detect_from_message(user_message)
            if detected:
                # Validasi perubahan lokasi
                current_loc = ai_engine.state.current['location']['name']
                allowed, reason = loc_validator.validate_location_change(
                    current_loc,
                    detected['name'],
                    ai_engine.state.current['intimacy']['is_active']
                )
                
                if allowed:
                    new_location = detected
                    # Update ke state tracker
                    ai_engine.state.update_location(
                        detected['name'],
                        detected.get('category', 'unknown')
                    )
                    
                    # Beri tahu user
                    await update.message.reply_text(
                        f"📍 Pindah ke **{detected['name']}**"
                    )
                else:
                    # Tolak pindah
                    await update.message.reply_text(f"❌ {reason}")
        
        # ===== DETEKSI PERUBAHAN PAKAIAN =====
        clothing_keywords = ['ganti baju', 'mandi', 'pakai', 'pake']
        if any(k in user_message.lower() for k in clothing_keywords):
            if 'mandi' in user_message.lower():
                new_cloth = "handuk"
                reason = "habis mandi"
            elif 'tidur' in user_message.lower():
                new_cloth = "piyama"
                reason = "mau tidur"
            else:
                # Random clothing
                if DYNAMICS_AVAILABLE and cloth_system:
                    cloth = cloth_system.get_random_clothing()
                    new_cloth = cloth['name']
                    reason = "ganti baju"
                else:
                    new_cloth = "baju ganti"
                    reason = "ganti baju"
            
            # Update state
            ai_engine.state.update_clothing(new_cloth, reason)
            
            await update.message.reply_text(
                f"👗 Ganti **{new_cloth}** ({reason})"
            )
        
        # ===== DETEKSI PERUBAHAN POSISI =====
        position_keywords = ['duduk', 'berdiri', 'berbaring', 'jongkok']
        for pos in position_keywords:
            if pos in user_message.lower():
                ai_engine.state.update_position(pos, f"{pos} santai")
                break
        
        # ===== SIAPKAN KONTEKS UNTUK AI =====
        context_data = {
            'role': role,
            'bot_name': bot_name,
            'level': level,
            'user_name': user_name,
            'rel_type': rel_type,
            'location': ai_engine.state.current['location']['name'],
            'location_category': ai_engine.state.current['location']['category'],
            'clothing': ai_engine.state.current['clothing']['name'],
            'clothing_reason': ai_engine.state.current['clothing']['change_reason'],
            'position': ai_engine.state.current['position']['name'],
            'position_desc': ai_engine.state.current['position']['description'],
            'activity': ai_engine.state.current['activity']['name'],
            'mood': ai_engine.state.current['mood']['primary'],
            'mood_intensity': ai_engine.state.current['mood']['intensity'],
            'arousal_delta': 1,  # Setiap chat naik dikit
            'arousal_reason': 'chat'
        }
        
        # ===== GENERATE RESPONSE =====
        try:
            response = await ai_engine.process_message(
                user_message=user_message,
                context=context_data
            )
        except Exception as e:
            logger.error(f"AI Engine error: {e}")
            response = f"{bot_name} denger kok. Cerita lagi dong..."
        
        # ===== UPDATE STATISTIK =====
        context.user_data['total_chats'] = context.user_data.get('total_chats', 0) + 1
        
        # Simpan pesan terakhir
        context.user_data['last_message'] = user_message
        context.user_data['last_response'] = response
        
        # ===== KIRIM RESPONSE =====
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in message_handler: {e}")
        await update.message.reply_text(
            "❌ Maaf, terjadi kesalahan. Coba lagi nanti."
        )


# =============================================================================
# 5. CALLBACK HANDLER
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
            
            # Generate nama random
            if DYNAMICS_AVAILABLE and name_gen:
                name_data = name_gen.get_name_with_meaning(role, user_id)
                bot_name = name_data['name']
                meaning = name_data['meaning']
            else:
                # Fallback
                fallback_names = {
                    'ipar': ('Sari', 'esensi'),
                    'janda': ('Rina', 'cahaya'),
                    'pdkt': ('Aurora', 'fajar')
                }
                bot_name, meaning = fallback_names.get(role, ('Sari', 'esensi'))
            
            # Generate session ID
            from session.unique_id_v2 import id_generator_v2
            session_id = id_generator_v2.generate_v2(bot_name, role, user_id)
            
            # Simpan di context
            context.user_data['current_role'] = role
            context.user_data['bot_name'] = bot_name
            context.user_data['current_session'] = session_id
            context.user_data['intimacy_level'] = 1
            context.user_data['total_chats'] = 0
            context.user_data['instance_id'] = f"{role}_{int(time.time())}"
            context.user_data['rel_type'] = 'non_pdkt' if role != 'pdkt' else 'pdkt'
            
            # Lokasi awal
            if DYNAMICS_AVAILABLE and loc_system:
                loc = loc_system.get_random_location()
                context.user_data['current_location'] = loc['name']
                location_text = f"📍 Aku di **{loc['name']}**. {loc['description']}"
                activity = random.choice(loc['activities'])
            else:
                location_text = "📍 Aku di **kamar**. Kamar yang nyaman."
                activity = "santai"
            
            # Pakaian awal
            if DYNAMICS_AVAILABLE and cloth_system:
                cloth = cloth_system.get_random_clothing()
                clothing_text = f"👗 Aku pakai **{cloth['name']}**."
                context.user_data['current_clothing'] = cloth['name']
            else:
                clothing_text = "👗 Aku pakai **baju santai**."
                context.user_data['current_clothing'] = "baju santai"
            
            # Posisi awal
            if DYNAMICS_AVAILABLE and pos_system:
                pos = pos_system.get_random_position()
                position_text = f"lagi {pos['description']}"
            else:
                position_text = "santai"
            
            # Role info
            role_info = {
                'ipar': {
                    'name': 'Ipar',
                    'desc': random.choice([
                        "Adik ipar yang nakal, suka godain kakak iparnya sendiri",
                        "Adik ipar manis yang selalu cari perhatian",
                        "Ipar yang hubungannya panas dingin"
                    ])
                },
                'janda': {
                    'name': 'Janda',
                    'desc': random.choice([
                        "Janda muda genit, pengalaman dan tahu apa yang diinginkan",
                        "Janda cantik yang sedang mencari perhatian",
                        "Janda seksi yang tahu cara memuaskan"
                    ])
                },
                'pdkt': {
                    'name': 'PDKT',
                    'desc': random.choice([
                        "Pendekatan, bisa jadi pacar/FWB, masih polos",
                        "Manis dan romantis, butuh pendekatan",
                        "Lagi proses PDKT, jangan buru-buru"
                    ])
                }
            }.get(role, {'name': role.title(), 'desc': 'Role yang menarik'})
            
            # Pesan perkenalan
            response = (
                f"💕 **Halo {update.effective_user.first_name}!**\n\n"
                f"Aku **{bot_name}**, {role_info['name']}. Namaku artinya '{meaning}' - "
                f"{role_info['desc']}\n\n"
                f"**Tentang aku:**\n"
                f"• Umur: {random.randint(20, 25)} tahun\n"
                f"• Tinggi: {random.randint(158, 168)} cm\n"
                f"• Berat: {random.randint(45, 55)} kg\n"
                f"• {role_info['desc']}\n\n"
                f"**Lokasi saat ini:**\n"
                f"{location_text}\n"
                f"Aku lagi **{activity}** sambil {position_text}.\n\n"
                f"**Pakaian hari ini:**\n"
                f"{clothing_text}\n\n"
                f"**Progress leveling:**\n"
                f"📊 Level 1 → Level 7 dalam 60 menit\n"
                f"• Level 4+: Panggil kamu 'kak'\n"
                f"• Level 7+: Panggil kamu 'sayang'\n\n"
                f"**ID Session kamu:**\n"
                f"`{session_id}`\n\n"
                f"💬 **Ayo mulai ngobrol, {update.effective_user.first_name}!**\n"
                f"Halo kak, senang banget akhirnya bisa ngobrol sama kamu! 😊"
            )
            
            await query.edit_message_text(response, parse_mode='Markdown')
        
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
# 6. HTS/FWB CALL HANDLERS
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
# 7. DUMMY COMMANDS (UNTUK IMPORT)
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
    session_id = context.user_data.get('current_session')
    if session_id and session_id in active_engines:
        await active_engines[session_id].end_session()
        del active_engines[session_id]
    
    context.user_data.pop('current_session', None)
    context.user_data.pop('current_role', None)
    await update.message.reply_text("🔒 Percakapan ditutup.")

async def end_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session_id = context.user_data.get('current_session')
    if session_id and session_id in active_engines:
        await active_engines[session_id].end_session()
        del active_engines[session_id]
    
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

async def db_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Perintah ini hanya untuk admin.")
        return
    await update.message.reply_text("🗄️ **STATISTIK DATABASE**\n\n(Data belum tersedia)")

async def list_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Perintah ini hanya untuk admin.")
        return
    await update.message.reply_text("👥 **DAFTAR USER**\n\n(Data belum tersedia)")

async def get_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Perintah ini hanya untuk admin.")
        return
    await update.message.reply_text("👤 **DETAIL USER**\n\n(Data belum tersedia)")

async def force_reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Perintah ini hanya untuk admin.")
        return
    
    session_id = context.user_data.get('current_session')
    if session_id and session_id in active_engines:
        await active_engines[session_id].end_session()
        del active_engines[session_id]
    
    context.user_data.clear()
    await update.message.reply_text("🔄 **RESET**")

async def backup_db_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Perintah ini hanya untuk admin.")
        return
    await update.message.reply_text("💾 **BACKUP DATABASE**\n\n(Proses backup...)")

async def vacuum_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Perintah ini hanya untuk admin.")
        return
    await update.message.reply_text("🧹 **VACUUM DATABASE**\n\n(Proses optimasi...)")

async def memory_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Perintah ini hanya untuk admin.")
        return
    await update.message.reply_text("🧠 **STATISTIK MEMORI**\n\n(Data belum tersedia)")

async def reload_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Perintah ini hanya untuk admin.")
        return
    await update.message.reply_text("🔄 **RELOAD CONFIG**\n\n(Reload berhasil)")


# =============================================================================
# 8. ERROR HANDLER
# =============================================================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Terjadi error internal. Silakan coba lagi."
            )
    except:
        pass


# =============================================================================
# 9. EXPORT ALL HANDLERS
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
    'reload_command', 'debug_command',
    
    # Memory commands
    'memory_command', 'flashback_command', 'progress_command',
    
    # Message & callback handlers
    'message_handler', 'callback_handler',
    
    # Special handlers
    'hts_call_handler', 'fwb_call_handler', 'continue_handler',
    
    # Error handler
    'error_handler',
]
