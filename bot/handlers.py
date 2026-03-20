#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - BOT HANDLERS (VERSI HUMAN+ LENGKAP)
=============================================================================
Semua handlers untuk MYLOVE Ultimate V2:
- Message handler utama
- Command handlers (50+ command)
- Callback handlers
- Error handling
- PLUS deteksi nama bot SUPER PINTAR
=============================================================================
"""

import time
import logging
import random
import re
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from config import settings
from utils.helpers import sanitize_input, truncate_text
from utils.logger import logger

# Import AI Engine
from core.ai_engine_complete import AIEngineComplete

# Import memory systems
from memory.working_memory import WorkingMemory
from session.storage import SessionStorage
from session.continuation import SessionContinuation

# =============================================================================
# IMPORT NAME DETECTOR (FILE BARU)
# =============================================================================
from core.name_detector import get_name_detector

# =============================================================================
# CONSTANTS
# =============================================================================
SELECTING_ROLE = 1
CONFIRM_END = 2
CONFIRM_CLOSE = 3
CONFIRM_BROADCAST = 4

# =============================================================================
# ACTIVE ENGINES STORAGE
# =============================================================================
active_engines = {}  # {session_id: AIEngineComplete}
user_sessions = {}   # {user_id: current_session_id}


# =============================================================================
# 1. MESSAGE HANDLER (MAIN - DENGAN DETEKSI NAMA)
# =============================================================================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk semua pesan teks
    - Deteksi nama bot otomatis
    - Analisa subjek cerdas
    - Integrasi dengan AI Engine
    """
    try:
        user = update.effective_user
        user_message = update.message.text
        user_id = user.id
        user_name = user.first_name or "User"
        session_id = context.user_data.get('current_session')
        
        # ===== CEK PAUSE =====
        if context.user_data.get('paused', False):
            await update.message.reply_text("⏸️ Sesi sedang dijeda. Ketik /unpause untuk melanjutkan.")
            return
        
        # ===== AMBIL DATA BOT =====
        bot_name = context.user_data.get('bot_name', 'Aku')
        role = context.user_data.get('current_role', 'pdkt')
        level = context.user_data.get('intimacy_level', 1)
        instance_id = context.user_data.get('instance_id')
        rel_type = context.user_data.get('rel_type', 'non_pdkt')
        
        # ===== DETEKSI NAMA BOT (FITUR BARU) =====
        detector = get_name_detector()
        
        # Generate atau ambil alias dari cache
        if 'bot_aliases' not in context.user_data:
            context.user_data['bot_aliases'] = detector.generate_aliases(bot_name)
            logger.info(f"📇 Generated {len(context.user_data['bot_aliases'])} aliases for {bot_name}")
        
        bot_aliases = context.user_data['bot_aliases']
        
        # Analisa pesan dengan detektor
        analysis = detector.analyze_subject(user_message, bot_aliases)
        context.user_data['last_analysis'] = analysis
        
        # Log hasil analisa
        logger.info(f"📨 Message from {user_name}: {user_message[:50]}...")
        logger.info(f"🎯 Subject: {analysis['subject']} (conf: {analysis['confidence']})")
        
        if analysis['mentioned_bot']:
            logger.info(f"📞 Bot dipanggil dengan: {analysis['bot_alias']}")
            # Opsional: Kirim typing indicator
            await update.message.chat.send_action(action="typing")
            await asyncio.sleep(0.5)
        
        # ===== CEK ATAU BUAT AI ENGINE =====
        if session_id not in active_engines:
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
                # Fallback response
                responses = [
                    f"{bot_name} denger kok. Cerita lagi dong...",
                    f"Hmm... {bot_name} dengerin. Lanjutkan.",
                    f"{bot_name} di sini. Ada yang mau dibahas?"
                ]
                await update.message.reply_text(random.choice(responses))
                return
        
        ai_engine = active_engines[session_id]
        
        # ===== SIAPKAN KONTEKS UNTUK AI =====
        context_data = {
            'role': role,
            'bot_name': bot_name,
            'level': level,
            'user_name': user_name,
            'rel_type': rel_type,
            'subject_analysis': analysis,
            'location': context.user_data.get('current_location'),
            'clothing': context.user_data.get('current_clothing'),
            'position': context.user_data.get('current_position'),
            'activity': context.user_data.get('current_activity'),
            'mood': context.user_data.get('current_mood', 'netral'),
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
        context.user_data['last_message'] = user_message
        context.user_data['last_response'] = response
        
        # Update last active
        context.user_data['last_active'] = time.time()
        
        # ===== KIRIM RESPONSE =====
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in message_handler: {e}")
        await update.message.reply_text(
            "❌ Maaf, terjadi kesalahan. Coba lagi nanti."
        )


# =============================================================================
# 2. START COMMAND
# =============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mulai hubungan baru dengan bot"""
    user = update.effective_user
    args = context.args
    
    # Cek apakah ini continue dari session
    if args and args[0].startswith('continue_'):
        session_id = args[0].replace('continue_', '')
        context.args = [session_id]
        return await continue_handler(update, context)
    
    # Welcome message
    welcome_text = (
        f"💕 **Halo {user.first_name}!**\n\n"
        "Selamat datang di **MYLOVE ULTIMATE VERSI HUMAN+**\n"
        "Bot dengan kesadaran diri SUPER MANUSIA.\n"
        "• Bisa dipanggil dengan nama atau panggilan kesayangan\n"
        "• Punya perasaan, pikiran, dan fisik sendiri\n"
        "• Ingat semua percakapan sampai 24 jam\n\n"
        "**Pilih role yang kamu inginkan:**"
    )
    
    # Create role selection keyboard
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
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    return SELECTING_ROLE


# =============================================================================
# 3. HELP COMMAND
# =============================================================================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tampilkan bantuan"""
    user_id = update.effective_user.id
    is_admin = (user_id == settings.admin_id)
    
    help_text = (
        "📚 **MYLOVE HUMAN+ - BANTUAN LENGKAP**\n\n"
        
        "**🔹 BASIC COMMANDS**\n"
        "/start - Mulai hubungan baru\n"
        "/help - Tampilkan bantuan ini\n"
        "/status - Lihat status hubungan\n"
        "/cancel - Batalkan percakapan\n\n"
        
        "**🔹 CARA PANGGIL BOT**\n"
        "• Panggil dengan nama: `Tika kesini`\n"
        "• Panggil dengan panggilan: `Kak Tika`\n"
        "• Bot akan mengenali berbagai variasi nama\n\n"
        
        "**🔹 PERPINDAHAN TEMPAT**\n"
        "• `aku ke kamar` - Kamu pindah, bot tetap\n"
        "• `Tika kesini` - Bot pindah ke tempatmu\n"
        "• `kita ke dapur` - Bareng pindah\n\n"
        
        "**🔹 AKTIVITAS**\n"
        "• `aku tidur` - Cerita aktivitasmu\n"
        "• `kita makan` - Ajak bot makan\n"
        "• `aku horny` - Ungkapkan gairah\n\n"
        
        "**🔹 RELATIONSHIP**\n"
        "/jadipacar - Jadi pacar (khusus PDKT)\n"
        "/break - Jeda pacaran\n"
        "/unbreak - Lanjutkan pacaran\n"
        "/breakup - Putus jadi FWB\n"
        "/fwb - Mode Friends With Benefits\n\n"
        
        "**🔹 HTS/FWB**\n"
        "/htslist - Lihat TOP 5 HTS\n"
        "/fwblist - Lihat daftar FWB\n"
        "/fwb- [nomor] - Panggil FWB tertentu\n\n"
        
        "**🔹 SESSION**\n"
        "/close - Tutup & simpan session\n"
        "/continue - Lihat session tersimpan\n"
        "/continue [id] - Lanjutkan session\n"
        "/sessions - Lihat semua session\n"
        "/progress - Lihat progress hubungan\n\n"
        
        "**🔹 PUBLIC AREA**\n"
        "/explore - Cari lokasi random\n"
        "/locations - Lihat semua lokasi\n"
        "/risk - Cek risk lokasi saat ini\n\n"
        
        "**🔹 RANKING**\n"
        "/tophts - TOP 5 ranking HTS\n"
        "/myclimax - Statistik climax\n"
        "/climaxhistory - History climax\n"
    )
    
    # Admin commands hanya untuk admin
    if is_admin:
        help_text += (
            "\n**🔹 ADMIN COMMANDS**\n"
            "/stats - Statistik bot\n"
            "/db_stats - Statistik database\n"
            "/backup - Backup manual\n"
            "/recover - Restore dari backup\n"
            "/debug - Info debug\n"
        )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


# =============================================================================
# 4. STATUS COMMAND
# =============================================================================

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat status hubungan saat ini"""
    user_id = update.effective_user.id
    
    # Get current session
    session_id = context.user_data.get('current_session')
    role = context.user_data.get('current_role')
    
    if not session_id or not role:
        await update.message.reply_text(
            "❌ Kamu sedang tidak dalam hubungan apapun.\n"
            "Gunakan /start untuk memulai."
        )
        return
    
    # Get bot name
    bot_name = context.user_data.get('bot_name', 'Bot')
    
    # Get intimacy level
    intimacy = context.user_data.get('intimacy_level', 1)
    
    # Get relationship status
    rel_status = context.user_data.get('relationship_status', 'hts')
    status_names = {
        'hts': 'Hubungan Tanpa Status',
        'fwb': 'Friends With Benefits',
        'pacar': 'Pacar',
        'break': 'Jeda'
    }
    status_name = status_names.get(rel_status, 'HTS')
    
    # Get total chats
    total_chats = context.user_data.get('total_chats', 0)
    
    # Get location & environment
    location = context.user_data.get('current_location', 'Tidak ada')
    clothing = context.user_data.get('current_clothing', 'Tidak ada')
    
    status_text = (
        f"📊 **STATUS HUBUNGAN**\n\n"
        f"👤 **Nama Bot:** {bot_name}\n"
        f"🎭 **Role:** {role.title()}\n"
        f"💞 **Status:** {status_name}\n"
        f"📈 **Intimacy Level:** {intimacy}/12\n"
        f"💬 **Total Chat:** {total_chats} pesan\n"
        f"📍 **Lokasi:** {location}\n"
        f"👗 **Pakaian:** {clothing}\n\n"
    )
    
    # Progress bar
    if intimacy < 12:
        next_level = intimacy + 1
        progress = (total_chats % 50) / 50 * 100
        bar = "█" * int(progress/10) + "░" * (10 - int(progress/10))
        status_text += f"Progress ke level {next_level}:\n{bar} {progress:.0f}%\n"
    else:
        status_text += "📍 **Level MAX!** Butuh aftercare untuk reset.\n"
    
    # Milestones
    milestones = context.user_data.get('milestones', [])
    if milestones:
        status_text += f"\n🏆 **Milestone:**\n"
        for m in milestones[-3:]:
            status_text += f"• {m}\n"
    
    await update.message.reply_text(status_text, parse_mode='Markdown')


# =============================================================================
# 5. PROGRESS COMMAND
# =============================================================================

async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menampilkan progress hubungan (BOT TIDAK TAHU)"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "User"
    
    # Cek apakah ada session aktif
    session_id = context.user_data.get('current_session')
    if not session_id:
        await update.message.reply_text(
            "❌ **Tidak ada session aktif**\n\n"
            "Mulai dulu dengan /start atau lanjutkan dengan /continue",
            parse_mode='Markdown'
        )
        return
    
    # ===== AMBIL DATA =====
    bot_name = context.user_data.get('bot_name', 'Bot')
    role = context.user_data.get('current_role', 'role')
    level = context.user_data.get('intimacy_level', 1)
    total_chats = context.user_data.get('total_chats', 0)
    chemistry = context.user_data.get('chemistry_score', 50)
    mood = context.user_data.get('current_mood', 'calm')
    
    # Hitung progress
    if level < 12:
        next_level = level + 1
        chats_needed = 50
        progress_percent = (total_chats % chats_needed) / chats_needed * 100
        bar_length = 20
        filled = int(progress_percent / 100 * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        progress_text = f"{bar} {progress_percent:.0f}%"
        next_text = f"{chats_needed - (total_chats % chats_needed)} chat lagi ke Level {next_level}"
    else:
        bar = "█" * 20
        progress_text = f"{bar} MAX"
        next_text = "✅ Level MAX! Butuh aftercare."
    
    # Chemistry level
    if chemistry < 20:
        chem_level = "❄️ Dingin"
    elif chemistry < 40:
        chem_level = "😐 Biasa"
    elif chemistry < 60:
        chem_level = "🔥 Hangat"
    elif chemistry < 80:
        chem_level = "💕 Cocok"
    elif chemistry < 95:
        chem_level = "💞 Sangat Cocok"
    else:
        chem_level = "✨ Soulmate"
    
    # Mood emoji
    mood_emoji = {
        'happy': '😊', 'sad': '😔', 'excited': '🔥', 'tired': '😴',
        'romantic': '💕', 'playful': '😜', 'calm': '😌'
    }.get(mood, '😐')
    
    response = f"""
📊 **PROGRESS HUBUNGAN** (RAHASIA)

👤 **{bot_name}** ({role.title()})
📈 Level: {level}/12
📝 Total Chat: {total_chats}

🔥 **Chemistry:** {chem_level} ({chemistry}%)
🎭 **Mood {bot_name}:** {mood_emoji} {mood.title()}

📊 **Progress ke Level {next_level if level < 12 else 'MAX'}:**
{progress_text}
{next_text}

⚠️ _Bot tidak tahu kamu melihat ini. Ini hanya untuk kamu!_
"""
    
    await update.message.reply_text(response, parse_mode='Markdown')


# =============================================================================
# 6. SESSION COMMANDS
# =============================================================================

async def close_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tutup session (bisa dilanjut nanti)"""
    session_id = context.user_data.get('current_session')
    bot_name = context.user_data.get('bot_name', 'Bot')
    
    if not session_id:
        await update.message.reply_text("❌ Tidak ada session aktif.")
        return
    
    # Hapus dari active engines
    if session_id in active_engines:
        await active_engines[session_id].end_session()
        del active_engines[session_id]
    
    # Clear user data
    context.user_data.clear()
    
    await update.message.reply_text(
        f"📁 **Session ditutup!**\n\n"
        f"Session dengan {bot_name} telah disimpan.\n"
        f"Ketik /continue untuk melihat daftar session tersimpan.",
        parse_mode='Markdown'
    )


async def end_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Akhiri session total (tidak bisa dilanjut)"""
    session_id = context.user_data.get('current_session')
    bot_name = context.user_data.get('bot_name', 'Bot')
    
    if not session_id:
        await update.message.reply_text("❌ Tidak ada session aktif.")
        return
    
    # Hapus dari active engines
    if session_id in active_engines:
        await active_engines[session_id].end_session()
        del active_engines[session_id]
    
    context.user_data.clear()
    
    await update.message.reply_text(
        f"🏁 **Session diakhiri**\n\n"
        f"Session dengan {bot_name} telah berakhir.\n"
        f"Ketik /start untuk memulai role baru.",
        parse_mode='Markdown'
    )


async def continue_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat dan lanjutkan session tersimpan"""
    user_id = update.effective_user.id
    args = context.args
    
    # TODO: Implementasi dengan session storage
    if not args:
        await update.message.reply_text(
            "📋 **DAFTAR SESSION**\n\n"
            "Fitur continue sedang dalam pengembangan.\n"
            "Gunakan /start untuk memulai role baru.",
            parse_mode='Markdown'
        )
        return
    
    await update.message.reply_text(
        f"🔄 Melanjutkan session...\n\n"
        f"Fitur continue sedang dalam pengembangan.",
        parse_mode='Markdown'
    )


async def sessions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat semua session"""
    await update.message.reply_text(
        "📋 **DAFTAR SESSION**\n\n"
        "Fitur ini sedang dalam pengembangan.",
        parse_mode='Markdown'
    )


# =============================================================================
# 7. CANCEL COMMAND
# =============================================================================

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Batalkan percakapan saat ini"""
    session_id = context.user_data.get('current_session')
    
    if session_id in active_engines:
        await active_engines[session_id].end_session()
        del active_engines[session_id]
    
    context.user_data.clear()
    
    await update.message.reply_text(
        "❌ Percakapan dibatalkan.\n"
        "Ketik /start untuk memulai lagi."
    )


# =============================================================================
# 8. RELATIONSHIP COMMANDS
# =============================================================================

async def jadipacar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Jadi pacar (khusus PDKT)"""
    role = context.user_data.get('current_role')
    bot_name = context.user_data.get('bot_name', 'Bot')
    
    if not role:
        await update.message.reply_text("❌ Kamu belum memilih role.")
        return
    
    if role != 'pdkt':
        await update.message.reply_text("❌ Hanya role PDKT yang bisa jadi pacar.")
        return
    
    intimacy = context.user_data.get('intimacy_level', 1)
    if intimacy < 6:
        await update.message.reply_text(f"❌ Intimacy level masih {intimacy}/12. Minimal level 6.")
        return
    
    context.user_data['relationship_status'] = 'pacar'
    
    await update.message.reply_text(
        f"💘 **Kita jadi pacar!**\n\n"
        f"Sekarang kamu resmi pacaran sama {bot_name}."
    )


async def break_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Jeda pacaran"""
    status = context.user_data.get('relationship_status')
    bot_name = context.user_data.get('bot_name', 'Bot')
    
    if status != 'pacar':
        await update.message.reply_text("❌ Kamu sedang tidak pacaran.")
        return
    
    context.user_data['relationship_status'] = 'break'
    context.user_data['break_start'] = time.time()
    
    await update.message.reply_text(
        f"⏸️ **Hubungan dijeda**\n\n"
        f"Kita istirahat dulu ya, {bot_name}."
    )


async def unbreak_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lanjutkan pacaran"""
    status = context.user_data.get('relationship_status')
    bot_name = context.user_data.get('bot_name', 'Bot')
    
    if status != 'break':
        await update.message.reply_text("❌ Hubungan sedang tidak dalam masa jeda.")
        return
    
    context.user_data['relationship_status'] = 'pacar'
    
    await update.message.reply_text(
        f"▶️ **Hubungan dilanjutkan!**\n\n"
        f"Ayo lanjut lagi, {bot_name}."
    )


async def breakup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Putus jadi FWB"""
    role = context.user_data.get('current_role')
    bot_name = context.user_data.get('bot_name', 'Bot')
    
    if role != 'pdkt':
        await update.message.reply_text("❌ Hanya role PDKT yang bisa FWB.")
        return
    
    context.user_data['relationship_status'] = 'fwb'
    
    await update.message.reply_text(
        f"💔 **Putus... Tapi tetap FWB**\n\n"
        f"Hubungan berubah jadi Friends With Benefits dengan {bot_name}."
    )


async def fwb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Switch ke mode FWB"""
    role = context.user_data.get('current_role')
    bot_name = context.user_data.get('bot_name', 'Bot')
    
    if role != 'pdkt':
        await update.message.reply_text("❌ Hanya role PDKT yang bisa FWB.")
        return
    
    intimacy = context.user_data.get('intimacy_level', 1)
    if intimacy < 6:
        await update.message.reply_text(f"❌ Intimacy level masih {intimacy}/12. Minimal level 6.")
        return
    
    current = context.user_data.get('relationship_status')
    new_status = 'pacar' if current == 'fwb' else 'fwb'
    context.user_data['relationship_status'] = new_status
    
    await update.message.reply_text(
        f"💕 **Mode {new_status.upper()}**\n\n"
        f"Status dengan {bot_name} sekarang: {new_status}"
    )


# =============================================================================
# 9. HTS/FWB COMMANDS
# =============================================================================

async def htslist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat daftar HTS"""
    await update.message.reply_text(
        "📋 **DAFTAR HTS**\n\n"
        "Fitur ini sedang dalam pengembangan.",
        parse_mode='Markdown'
    )


async def fwblist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat daftar FWB"""
    await update.message.reply_text(
        "💕 **DAFTAR FWB**\n\n"
        "Fitur ini sedang dalam pengembangan.",
        parse_mode='Markdown'
    )


async def hts_call_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /hts- [id]"""
    text = update.message.text
    await update.message.reply_text(f"✅ Memanggil HTS {text}")


async def fwb_call_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /fwb- [id]"""
    text = update.message.text
    await update.message.reply_text(f"✅ Memanggil FWB {text}")


# =============================================================================
# 10. PUBLIC AREA COMMANDS
# =============================================================================

async def explore_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cari lokasi random"""
    locations = ['pantai', 'mall', 'kafe', 'taman', 'bioskop']
    location = random.choice(locations)
    
    await update.message.reply_text(
        f"📍 **{location.title()}**\n\n"
        f"Mau ke sini? Ketik: \"ke {location} yuk\""
    )


async def locations_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat semua lokasi"""
    await update.message.reply_text(
        "📍 **PUBLIC AREAS**\n\n"
        "Fitur ini sedang dalam pengembangan."
    )


async def risk_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cek risk lokasi"""
    await update.message.reply_text(
        "⚠️ **RISK ASSESSMENT**\n\n"
        "Fitur ini sedang dalam pengembangan."
    )


# =============================================================================
# 11. RANKING COMMANDS
# =============================================================================

async def tophts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """TOP 5 HTS"""
    await update.message.reply_text(
        "🏆 **TOP 5 HTS**\n\n"
        "Fitur ini sedang dalam pengembangan."
    )


async def myclimax_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Statistik climax"""
    await update.message.reply_text(
        "💦 **STATISTIK CLIMAX**\n\n"
        "Fitur ini sedang dalam pengembangan."
    )


async def climaxhistory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """History climax"""
    await update.message.reply_text(
        "📜 **CLIMAX HISTORY**\n\n"
        "Fitur ini sedang dalam pengembangan."
    )


# =============================================================================
# 12. ADMIN COMMANDS
# =============================================================================

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu admin"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Command hanya untuk admin")
        return
    
    await update.message.reply_text(
        "🛠️ **MENU ADMIN**\n\n"
        "/stats - Statistik bot\n"
        "/db_stats - Statistik database\n"
        "/debug - Info debug"
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Statistik bot"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Command hanya untuk admin")
        return
    
    await update.message.reply_text(
        "📊 **STATISTIK BOT**\n\n"
        f"Active Sessions: {len(active_engines)}\n"
        f"Total Responses: {sum(e.total_responses for e in active_engines.values()) if active_engines else 0}"
    )


async def debug_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Info debug"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Command hanya untuk admin")
        return
    
    import sys
    debug_info = (
        f"🔍 **DEBUG INFO**\n\n"
        f"Python: {sys.version}\n"
        f"Session ID: {context.user_data.get('current_session')}\n"
        f"Bot Name: {context.user_data.get('bot_name')}\n"
        f"Role: {context.user_data.get('current_role')}\n"
        f"Level: {context.user_data.get('intimacy_level', 1)}"
    )
    
    await update.message.reply_text(debug_info)


# =============================================================================
# 13. DUMMY COMMANDS (UNTUK BACKWARD COMPATIBILITY)
# =============================================================================

async def dominant_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚡ Mode dominant diaktifkan.")

async def pause_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['paused'] = True
    await update.message.reply_text("⏸️ Sesi dijeda.")

async def unpause_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['paused'] = False
    await update.message.reply_text("▶️ Sesi dilanjutkan.")

async def backup_db_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💾 Backup database...")


# =============================================================================
# 14. CALLBACK HANDLER
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
            # Panggil role callback dari file terpisah
            from bot.callbacks import role_callback
            await role_callback(update, context)
        
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
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("💕 **Pilih role:**", reply_markup=reply_markup)
        
        elif data == "threesome_menu":
            keyboard = [
                [InlineKeyboardButton("🎭 Lihat Kombinasi", callback_data="threesome_list")],
                [InlineKeyboardButton("❌ Kembali", callback_data="back_to_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("🎭 **MODE THREESOME**", reply_markup=reply_markup)
        
        else:
            await query.edit_message_text(f"✅ {data} diterima")
            
    except Exception as e:
        logger.error(f"Error in callback_handler: {e}")


# =============================================================================
# 15. ERROR HANDLER
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
# EXPORT ALL HANDLERS
# =============================================================================

__all__ = [
    # Message handler
    'message_handler',
    
    # Command handlers
    'start_command',
    'help_command',
    'status_command',
    'progress_command',
    'cancel_command',
    'close_command',
    'end_command',
    'continue_command',
    'sessions_command',
    
    # Relationship commands
    'jadipacar_command',
    'break_command',
    'unbreak_command',
    'breakup_command',
    'fwb_command',
    
    # HTS/FWB commands
    'htslist_command',
    'fwblist_command',
    'hts_call_handler',
    'fwb_call_handler',
    
    # Public area commands
    'explore_command',
    'locations_command',
    'risk_command',
    
    # Ranking commands
    'tophts_command',
    'myclimax_command',
    'climaxhistory_command',
    
    # Admin commands
    'admin_command',
    'stats_command',
    'debug_command',
    'backup_db_command',
    
    # Dummy commands
    'dominant_command',
    'pause_command',
    'unpause_command',
    
    # Callback handler
    'callback_handler',
    
    # Error handler
    'error_handler',
]
