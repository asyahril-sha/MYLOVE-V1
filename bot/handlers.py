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
# from core.ai_engine_complete import AIEngineComplete
from core.ai_engine_complete_simple import AIEngineComplete

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

# =============================================================================
# 6. SESSION COMMANDS (LANJUTAN)
# =============================================================================

async def continue_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk melanjutkan session yang tersimpan"""
    user_id = update.effective_user.id
    
    # Cek apakah ada session_id di args
    args = context.args
    if not args:
        await update.message.reply_text(
            "❌ **Gunakan:** `/continue [session_id]`\n\n"
            "Contoh: `/continue abc123`\n\n"
            "Ketik `/sessions` untuk melihat daftar session."
        )
        return
    
    session_id = args[0]
    
    try:
        # Coba load session dari database
        import sqlite3
        from pathlib import Path
        from datetime import datetime
        
        db_path = Path("database/gadis_v81.db")
        
        if not db_path.exists():
            await update.message.reply_text("❌ Database tidak ditemukan")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Cek apakah session ada
        cursor.execute("""
            SELECT session_id, user_id, role, bot_name, intimacy_level, 
                   relationship_status, created_at, last_active
            FROM sessions 
            WHERE session_id = ? AND user_id = ?
        """, (session_id, user_id))
        
        session = cursor.fetchone()
        conn.close()
        
        if not session:
            await update.message.reply_text(
                f"❌ Session dengan ID `{session_id}` tidak ditemukan atau bukan milik Anda."
            )
            return
        
        # Extract data
        session_id, db_user_id, role, bot_name, intimacy, rel_status, created_at, last_active = session
        
        # Set context user data
        context.user_data['current_session'] = session_id
        context.user_data['current_role'] = role
        context.user_data['bot_name'] = bot_name
        context.user_data['intimacy_level'] = intimacy
        context.user_data['relationship_status'] = rel_status
        context.user_data['paused'] = False
        
        # Update last active
        context.user_data['last_active'] = time.time()
        
        # Update di database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE sessions 
            SET last_active = datetime('now'), status = 'active'
            WHERE session_id = ?
        """, (session_id,))
        conn.commit()
        conn.close()
        
        # Format tanggal
        from datetime import datetime
        try:
            created_date = datetime.fromisoformat(created_at).strftime('%d/%m/%Y %H:%M')
        except:
            created_date = created_at[:16] if created_at else "Unknown"
        
        await update.message.reply_text(
            f"✅ **Session dilanjutkan!**\n\n"
            f"👤 **Bot:** {bot_name}\n"
            f"🎭 **Role:** {role}\n"
            f"📈 **Level:** {intimacy}/12\n"
            f"📅 **Dimulai:** {created_date}\n\n"
            f"Silakan lanjutkan percakapan."
        )
        
    except Exception as e:
        logger.error(f"Error continue session: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")
        
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


async def go_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pergi ke lokasi tertentu"""
    args = context.args
    if not args:
        await update.message.reply_text(
            "❌ **Gunakan:** `/go [lokasi]`\n\n"
            "Contoh: `/go dapur` atau `/go kamar`"
        )
        return
    
    location = ' '.join(args)
    context.user_data['current_location'] = location
    
    await update.message.reply_text(
        f"📍 Pindah ke **{location}**"
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
async def positions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menampilkan daftar posisi yang tersedia"""
    positions = [
        "• Duduk santai",
        "• Berdiri tegak", 
        "• Berbaring",
        "• Bersandar",
        "• Jongkok",
        "• Merangkak",
        "• Miring",
        "• Telentang"
    ]
    
    text = "🧘 **POSISI YANG TERSEDIA:**\n\n" + "\n".join(positions)
    text += "\n\n💡 _Ketik posisi yang kamu mau, misal: \"duduk santai\"_"
    
    await update.message.reply_text(text, parse_mode='Markdown')


async def mood_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menampilkan mood bot saat ini"""
    mood = context.user_data.get('current_mood', 'calm')
    bot_name = context.user_data.get('bot_name', 'Aku')
    
    mood_emojis = {
        'happy': '😊', 
        'sad': '😔', 
        'excited': '🔥', 
        'tired': '😴',
        'romantic': '💕', 
        'playful': '😜', 
        'calm': '😌', 
        'angry': '😠',
        'jealous': '🫣', 
        'lonely': '🥺', 
        'horny': '🔥'
    }
    
    emoji = mood_emojis.get(mood, '😐')
    
    await update.message.reply_text(
        f"🎭 **Mood {bot_name}:** {emoji} {mood.title()}",
        parse_mode='Markdown'
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

async def climaxrank_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ranking climax (alias untuk tophts)"""
    await update.message.reply_text(
        "🏆 **RANKING CLIMAX**\n\n"
        "Fitur ini sedang dalam pengembangan.",
        parse_mode='Markdown'
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


# ===== FUNGSI DB_STATS_COMMAND =====
async def db_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat statistik database (khusus admin)"""
    user_id = update.effective_user.id
    
    # Cek apakah user adalah admin
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Command ini hanya untuk admin")
        return
    
    # Coba ambil statistik database
    try:
        # Cek apakah database ada
        import os
        import sqlite3
        from pathlib import Path
        
        db_path = Path("database/gadis_v81.db")
        
        if not db_path.exists():
            await update.message.reply_text("❌ Database tidak ditemukan")
            return
        
        # Dapatkan ukuran database
        size_bytes = os.path.getsize(db_path)
        size_mb = size_bytes / (1024 * 1024)
        
        # Waktu modifikasi terakhir
        mod_time = os.path.getmtime(db_path)
        from datetime import datetime
        last_updated = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
        
        # Hitung jumlah record
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Cek tabel yang ada
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Inisialisasi statistik
        total_users = 0
        total_sessions = 0
        total_messages = 0
        
        # Hitung users
        if 'users' in tables:
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
        
        # Hitung sessions
        if 'sessions' in tables:
            cursor.execute("SELECT COUNT(*) FROM sessions")
            total_sessions = cursor.fetchone()[0]
        
        # Hitung messages
        if 'messages' in tables:
            cursor.execute("SELECT COUNT(*) FROM messages")
            total_messages = cursor.fetchone()[0]
        
        conn.close()
        
        # Buat pesan statistik
        stats_text = (
            "🗄️ **STATISTIK DATABASE**\n\n"
            f"📊 **Total Users:** {total_users}\n"
            f"💬 **Total Sessions:** {total_sessions}\n"
            f"📝 **Total Messages:** {total_messages}\n"
            f"📁 **Ukuran Database:** {size_mb:.2f} MB\n"
            f"⏱️ **Terakhir Update:** {last_updated}\n"
            f"📌 **Lokasi:** {db_path}"
        )
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error getting db stats: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


# ===== FUNGSI LIST_USERS_COMMAND (TERPISAH) =====
async def list_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat daftar users (khusus admin)"""
    user_id = update.effective_user.id
    
    # Cek apakah user adalah admin
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Command hanya untuk admin")
        return
    
    try:
        # Coba ambil data users dari database
        import sqlite3
        from pathlib import Path
        
        db_path = Path("database/gadis_v81.db")
        
        if not db_path.exists():
            await update.message.reply_text("❌ Database tidak ditemukan")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Cek apakah tabel users ada
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            await update.message.reply_text("❌ Tabel users tidak ditemukan")
            conn.close()
            return
        
        # Ambil daftar users
        cursor.execute("""
            SELECT user_id, username, first_name, created_at, total_chats 
            FROM users 
            ORDER BY created_at DESC 
            LIMIT 20
        """)
        
        users = cursor.fetchall()
        conn.close()
        
        if not users:
            await update.message.reply_text("📋 **DAFTAR USERS**\n\nBelum ada users.")
            return
        
        # Buat pesan daftar users
        text = "📋 **DAFTAR USERS (20 terbaru)**\n\n"
        
        for i, user in enumerate(users, 1):
            user_id_db, username, first_name, created_at, total_chats = user
            
            # Format nama
            name = first_name or "Unknown"
            if username:
                name += f" (@{username})"
            
            # Format tanggal
            if created_at:
                from datetime import datetime
                try:
                    created_date = datetime.fromisoformat(created_at).strftime('%d/%m/%Y')
                except:
                    created_date = created_at[:10] if created_at else "Unknown"
            else:
                created_date = "Unknown"
            
            text += f"{i}. **{name}**\n"
            text += f"   🆔 `{user_id_db}`\n"
            text += f"   📅 {created_date} | 💬 {total_chats or 0} chat\n\n"
        
        # Kirim pesan (mungkin panjang, kirim per bagian)
        if len(text) > 4000:
            # Kirim per 4000 karakter
            for i in range(0, len(text), 4000):
                await update.message.reply_text(text[i:i+4000], parse_mode='Markdown')
        else:
            await update.message.reply_text(text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")
        
# ===== FUNGSI GET_USER_COMMAND =====
async def get_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat detail user tertentu (khusus admin)"""
    user_id = update.effective_user.id
    
    # Cek apakah user adalah admin
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Command hanya untuk admin")
        return
    
    # Cek apakah ada argumen (user_id yang dicari)
    args = context.args
    if not args:
        await update.message.reply_text(
            "❌ **Gunakan:** `/get_user [user_id]`\n\n"
            "Contoh: `/get_user 123456789`"
        )
        return
    
    target_user_id = args[0]
    
    try:
        # Coba ambil data user dari database
        import sqlite3
        from pathlib import Path
        from datetime import datetime
        
        db_path = Path("database/gadis_v81.db")
        
        if not db_path.exists():
            await update.message.reply_text("❌ Database tidak ditemukan")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Cek apakah tabel users ada
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            await update.message.reply_text("❌ Tabel users tidak ditemukan")
            conn.close()
            return
        
        # Ambil data user
        cursor.execute("""
            SELECT user_id, username, first_name, last_name, created_at, 
                   total_chats, total_sessions, last_active
            FROM users 
            WHERE user_id = ?
        """, (target_user_id,))
        
        user = cursor.fetchone()
        
        if not user:
            await update.message.reply_text(f"❌ User dengan ID `{target_user_id}` tidak ditemukan")
            conn.close()
            return
        
        # Ambil sessions user
        cursor.execute("""
            SELECT session_id, role, bot_name, created_at, status, intimacy_level
            FROM sessions 
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 5
        """, (target_user_id,))
        
        sessions = cursor.fetchall()
        conn.close()
        
        # Format data user
        user_id_db, username, first_name, last_name, created_at, total_chats, total_sessions, last_active = user
        
        full_name = first_name or ""
        if last_name:
            full_name += f" {last_name}"
        if not full_name:
            full_name = "Unknown"
        
        # Format tanggal
        def format_date(date_str):
            if date_str:
                try:
                    return datetime.fromisoformat(date_str).strftime('%d/%m/%Y %H:%M')
                except:
                    return date_str[:16]
            return "Unknown"
        
        created_date = format_date(created_at)
        last_active_date = format_date(last_active) if last_active else "Never"
        
        # Buat pesan detail user
        text = (
            f"👤 **DETAIL USER**\n\n"
            f"🆔 **User ID:** `{user_id_db}`\n"
            f"📛 **Nama:** {full_name}\n"
        )
        
        if username:
            text += f"📧 **Username:** @{username}\n"
        
        text += (
            f"📅 **Bergabung:** {created_date}\n"
            f"⏱️ **Terakhir Aktif:** {last_active_date}\n"
            f"💬 **Total Chat:** {total_chats or 0}\n"
            f"📁 **Total Sessions:** {total_sessions or 0}\n\n"
        )
        
        # Tambahkan sessions
        if sessions:
            text += "📋 **Sessions Terbaru:**\n"
            for i, session in enumerate(sessions, 1):
                session_id, role, bot_name, created_at, status, intimacy = session
                status_emoji = {
                    'active': '🟢',
                    'paused': '⏸️',
                    'closed': '📁',
                    'ended': '🏁'
                }.get(status, '⚪')
                
                text += f"{i}. {status_emoji} **{role}** - {bot_name}\n"
                text += f"   📈 Level {intimacy} | 🆔 `{session_id[:8]}...`\n"
        else:
            text += "📋 **Tidak ada sessions**\n"
        
        await update.message.reply_text(text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ===== FUNGSI FORCE_RESET_COMMAND =====
async def force_reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Force reset session user (khusus admin)"""
    user_id = update.effective_user.id
    
    # Cek apakah user adalah admin
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Command hanya untuk admin")
        return
    
    # Cek apakah ada argumen (user_id yang di-reset)
    args = context.args
    if not args:
        await update.message.reply_text(
            "❌ **Gunakan:** `/force_reset [user_id]`\n\n"
            "Contoh: `/force_reset 123456789`"
        )
        return
    
    target_user_id = args[0]
    
    try:
        # Hapus session dari memory
        from bot.handlers import active_engines, user_sessions
        
        # Cari session untuk user tersebut
        sessions_to_remove = []
        for session_id, engine in list(active_engines.items()):
            if hasattr(engine, 'user_id') and str(engine.user_id) == str(target_user_id):
                sessions_to_remove.append(session_id)
        
        # Hapus dari active_engines
        for session_id in sessions_to_remove:
            if session_id in active_engines:
                del active_engines[session_id]
        
        # Hapus dari user_sessions
        if int(target_user_id) in user_sessions:
            del user_sessions[int(target_user_id)]
        
        # Update database (optional)
        import sqlite3
        from pathlib import Path
        
        db_path = Path("database/gadis_v81.db")
        if db_path.exists():
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Update sessions jadi ended
            cursor.execute("""
                UPDATE sessions 
                SET status = 'ended', ended_at = datetime('now')
                WHERE user_id = ? AND status IN ('active', 'paused')
            """, (target_user_id,))
            
            conn.commit()
            conn.close()
        
        await update.message.reply_text(
            f"✅ **Force reset berhasil**\n\n"
            f"User `{target_user_id}` telah di-reset.\n"
            f"Sessions dihapus: {len(sessions_to_remove)}"
        )
        
    except Exception as e:
        logger.error(f"Error force reset: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


# ===== FUNGSI BACKUP_DB_COMMAND =====
async def backup_db_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Backup database (khusus admin)"""
    user_id = update.effective_user.id
    
    # Cek apakah user adalah admin
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Command hanya untuk admin")
        return
    
    try:
        import shutil
        from pathlib import Path
        from datetime import datetime
        
        db_path = Path("database/gadis_v81.db")
        
        if not db_path.exists():
            await update.message.reply_text("❌ Database tidak ditemukan")
            return
        
        # Buat folder backup jika belum ada
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        # Nama file backup dengan timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"gadis_v81_backup_{timestamp}.db"
        
        # Copy database
        shutil.copy2(db_path, backup_path)
        
        # Hitung ukuran backup
        size_bytes = backup_path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        
        await update.message.reply_text(
            f"✅ **Backup database berhasil**\n\n"
            f"📁 **Lokasi:** `{backup_path}`\n"
            f"📊 **Ukuran:** {size_mb:.2f} MB\n"
            f"⏱️ **Waktu:** {timestamp}"
        )
        
    except Exception as e:
        logger.error(f"Error backup db: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


# ===== FUNGSI VACUUM_COMMAND =====
async def vacuum_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Vacuum database (optimasi) (khusus admin)"""
    user_id = update.effective_user.id
    
    # Cek apakah user adalah admin
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Command hanya untuk admin")
        return
    
    try:
        import sqlite3
        from pathlib import Path
        
        db_path = Path("database/gadis_v81.db")
        
        if not db_path.exists():
            await update.message.reply_text("❌ Database tidak ditemukan")
            return
        
        # Ukuran sebelum vacuum
        size_before = db_path.stat().st_size
        size_before_mb = size_before / (1024 * 1024)
        
        # Vacuum database
        conn = sqlite3.connect(db_path)
        conn.execute("VACUUM")
        conn.close()
        
        # Ukuran setelah vacuum
        size_after = db_path.stat().st_size
        size_after_mb = size_after / (1024 * 1024)
        
        # Pengurangan ukuran
        saved = size_before - size_after
        saved_mb = saved / (1024 * 1024)
        saved_percent = (saved / size_before * 100) if size_before > 0 else 0
        
        await update.message.reply_text(
            f"✅ **Vacuum database berhasil**\n\n"
            f"📊 **Ukuran sebelum:** {size_before_mb:.2f} MB\n"
            f"📊 **Ukuran setelah:** {size_after_mb:.2f} MB\n"
            f"💾 **Hemat:** {saved_mb:.2f} MB ({saved_percent:.1f}%)"
        )
        
    except Exception as e:
        logger.error(f"Error vacuum db: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


# ===== FUNGSI MEMORY_STATS_COMMAND =====
async def memory_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat statistik memory (khusus admin)"""
    user_id = update.effective_user.id
    
    # Cek apakah user adalah admin
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Command hanya untuk admin")
        return
    
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Memory info
        memory_info = process.memory_info()
        memory_rss = memory_info.rss / (1024 * 1024)  # MB
        memory_vms = memory_info.vms / (1024 * 1024)  # MB
        
        # CPU info
        cpu_percent = process.cpu_percent(interval=0.1)
        
        # Threads
        threads = process.num_threads()
        
        # Connections
        connections = len(process.connections())
        
        # Active engines
        from bot.handlers import active_engines, user_sessions
        
        text = (
            f"🧠 **STATISTIK MEMORY**\n\n"
            f"📊 **RSS Memory:** {memory_rss:.2f} MB\n"
            f"📊 **VMS Memory:** {memory_vms:.2f} MB\n"
            f"⚡ **CPU Usage:** {cpu_percent:.1f}%\n"
            f"🧵 **Threads:** {threads}\n"
            f"🔌 **Connections:** {connections}\n\n"
            f"🤖 **Active Engines:** {len(active_engines)}\n"
            f"👤 **User Sessions:** {len(user_sessions)}"
        )
        
        await update.message.reply_text(text)
        
    except ImportError:
        # Fallback jika psutil tidak tersedia
        from bot.handlers import active_engines, user_sessions
        await update.message.reply_text(
            f"🧠 **STATISTIK MEMORY (SEDERHANA)**\n\n"
            f"🤖 **Active Engines:** {len(active_engines)}\n"
            f"👤 **User Sessions:** {len(user_sessions)}\n\n"
            f"⚠️ Install psutil untuk statistik lengkap"
        )
    except Exception as e:
        logger.error(f"Error memory stats: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


# ===== FUNGSI RELOAD_COMMAND =====
async def reload_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reload konfigurasi (khusus admin)"""
    user_id = update.effective_user.id
    
    # Cek apakah user adalah admin
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Command hanya untuk admin")
        return
    
    try:
        # Reload settings
        import importlib
        import config.settings
        importlib.reload(config.settings)
        
        # Update settings - CARA BENAR
        from config import settings as new_settings
        
        # Update module settings secara global
        import sys
        sys.modules['config.settings'] = new_settings
        
        # Update variabel local
        global_vars = globals()
        global_vars['settings'] = new_settings
        
        await update.message.reply_text(
            f"✅ **Reload berhasil**\n\n"
            f"Settings telah dimuat ulang."
        )
        
    except Exception as e:
        logger.error(f"Error reload: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")
        
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
    'continue_handler', 
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
    'db_stats_command',
    'list_users_command',
    'get_user_command',
    'force_reset_command',
    'backup_db_command',
    'vacuum_command',
    'memory_stats_command', 
    'reload_command',
    'debug_command',
    
    # Dummy commands
    'dominant_command',
    'pause_command',
    'unpause_command',
    
    # Callback handler
    'callback_handler',
    
    # Error handler
    'error_handler',
]
