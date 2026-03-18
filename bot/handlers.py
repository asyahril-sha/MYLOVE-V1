#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - BOT HANDLERS (FIX LENGKAP)
=============================================================================
Semua handlers untuk MYLOVE Ultimate V2 dengan integrasi:
- Context Analyzer (konteks super lengkap)
- Expression & Sound Engine (AI generated)
- Nickname System (panggilan based on level)
- Leveling System (60 menit ke level 7)
- Environment Dynamics (lokasi, posisi, pakaian)
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
from database.models import Constants

# ===== MYLOVE V2 IMPORTS =====
from session.unique_id import id_generator
from roles import get_random_name, get_random_name_with_hint, format_name_for_display
from roles.artis_references import get_random_artist_for_role, format_artist_description
from public.locations import PublicLocations
from public.risk import RiskCalculator

# Environment Dynamics
from dynamics.location import LocationSystem, LocationType
from dynamics.position import PositionSystem, PositionType
from dynamics.clothing import ClothingSystem, ClothingStyle

# Leveling System
from leveling.time_based import TimeBasedLeveling, ActivityType
from leveling.progress_tracker import ProgressTracker

# AI & Expression
from core.context_analyzer import ContextAnalyzer
from core.prompt_builder import PromptBuilder
from core.expression_engine import ExpressionEngine
from core.sound_engine import SoundEngine
from dynamics.nickname import NicknameSystem

# =============================================================================
# 1. INITIALIZATION
# =============================================================================

# Initialize all systems (singleton pattern)
context_analyzer = ContextAnalyzer()
prompt_builder = PromptBuilder()
nickname_system = NicknameSystem()

# These will be initialized with ai_engine later
expression_engine = None
sound_engine = None


async def initialize_engines(ai_engine):
    """Initialize expression and sound engines with AI engine"""
    global expression_engine, sound_engine
    expression_engine = ExpressionEngine(ai_engine, prompt_builder)
    sound_engine = SoundEngine(ai_engine, prompt_builder)
    logger.info("✅ Expression & Sound Engines initialized")


# =============================================================================
# 2. HELPER FUNCTIONS
# =============================================================================

def get_role_info(role: str) -> Dict:
    """Dapatkan informasi role untuk display"""
    roles = {
        "ipar": {
            "name": "Ipar",
            "description": "Adik ipar yang nakal, umur 22 tahun",
            "age": "22",
            "height": "165",
            "weight": "52",
            "chest": "34B"
        },
        "janda": {
            "name": "Janda",
            "description": "Janda muda genit, umur 24 tahun",
            "age": "24",
            "height": "168",
            "weight": "55",
            "chest": "36C"
        },
        "pelakor": {
            "name": "Pelakor",
            "description": "Perebut orang, umur 25 tahun",
            "age": "25",
            "height": "170",
            "weight": "58",
            "chest": "36C"
        },
        "istri_orang": {
            "name": "Istri Orang",
            "description": "Istri orang lain, umur 26 tahun",
            "age": "26",
            "height": "165",
            "weight": "54",
            "chest": "34B"
        },
        "pdkt": {
            "name": "PDKT",
            "description": "Pendekatan, bisa jadi pacar/FWB, umur 21 tahun",
            "age": "21",
            "height": "160",
            "weight": "48",
            "chest": "32B"
        },
        "sepupu": {
            "name": "Sepupu",
            "description": "Hubungan keluarga, umur 20 tahun",
            "age": "20",
            "height": "158",
            "weight": "47",
            "chest": "32A"
        },
        "teman_kantor": {
            "name": "Teman Kantor",
            "description": "Rekan kerja yang mesra, umur 23 tahun",
            "age": "23",
            "height": "162",
            "weight": "50",
            "chest": "34B"
        },
        "teman_sma": {
            "name": "Teman SMA",
            "description": "Teman jaman sekolah, umur 19 tahun",
            "age": "19",
            "height": "162",
            "weight": "50",
            "chest": "34B"
        },
        "mantan": {
            "name": "Mantan",
            "description": "Ex-pacar hangat, umur 24 tahun",
            "age": "24",
            "height": "165",
            "weight": "53",
            "chest": "34B"
        },
    }
    return roles.get(role, roles["ipar"])


async def detect_location_from_message(message: str) -> Optional[Dict]:
    """
    Deteksi apakah user menyebut lokasi
    Returns location dict or None
    """
    message_lower = message.lower()
    
    locations = {
        "toilet": {"name": "Toilet Umum", "base_risk": 75, "base_thrill": 80, 
                   "description": "Toilet umum, risk tinggi tapi thrilling"},
        "wc": {"name": "Toilet Umum", "base_risk": 75, "base_thrill": 80, 
               "description": "Toilet umum, risk tinggi tapi thrilling"},
        "pantai": {"name": "Pantai Malam", "base_risk": 30, "base_thrill": 85, 
                   "description": "Pantai sepi, suara ombak, romantis"},
        "mobil": {"name": "Mobil", "base_risk": 25, "base_thrill": 55, 
                  "description": "Mobil pribadi, cukup aman"},
        "parkir": {"name": "Parkiran Mall", "base_risk": 60, "base_thrill": 75, 
                   "description": "Parkiran bawah tanah, risk medium"},
        "lift": {"name": "Lift", "base_risk": 80, "base_thrill": 90, 
                 "description": "Lift, cepat dan thrilling"},
        "tangga": {"name": "Tangga Darurat", "base_risk": 65, "base_thrill": 75, 
                   "description": "Tangga belakang, sepi"},
        "kamar": {"name": "Kamar Tidur", "base_risk": 10, "base_thrill": 40, 
                  "description": "Kamar pribadi, aman dan nyaman"},
        "kantor": {"name": "Kantor", "base_risk": 50, "base_thrill": 70, 
                   "description": "Kantor sepi, risk sedang"},
        "hutan": {"name": "Hutan Kota", "base_risk": 35, "base_thrill": 80, 
                  "description": "Hutan kota, gelap dan sepi"},
    }
    
    for keyword, location in locations.items():
        if keyword in message_lower:
            return location
            
    return None


# =============================================================================
# 3. COMMAND HANDLERS
# =============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /start command - memulai bot dan memilih role"""
    user = update.effective_user
    logger.info(f"User {user.id} (@{user.username}) started the bot")
    
    # Cek apakah user sudah pernah memiliki session sebelumnya
    if 'current_session' in context.user_data:
        await update.message.reply_text(
            "⚠️ Kamu masih memiliki sesi aktif.\n"
            "Gunakan /status untuk melihat status.\n"
            "Gunakan /close untuk menutup sesi."
        )
        return Constants.ACTIVE_SESSION
    
    # Keyboard untuk memilih role
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
        "Virtual Girlfriend AI dengan:\n"
        "• Leveling berbasis durasi (60 menit ke Level 7)\n"
        "• Ekspresi & Suara AI Generated\n"
        "• Panggilan intim di Level 7+\n"
        "• Environment dinamis (lokasi, posisi, pakaian)\n"
        "• Nama bot permanent di UniqueID\n\n"
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
    """Handle /help command - menampilkan bantuan"""
    help_text = (
        "📋 **DAFTAR PERINTAH**\n\n"
        "**Perintah Dasar:**\n"
        "/start - Mulai bot dan pilih role\n"
        "/help - Tampilkan bantuan ini\n"
        "/status - Cek status session\n"
        "/cancel - Batalkan sesi\n\n"
        
        "**Perintah Hubungan:**\n"
        "/jadipacar - Ubah PDKT jadi pacar\n"
        "/break - Break dari pacar\n"
        "/unbreak - Unbreak\n"
        "/breakup - Putus\n"
        "/fwb - Masuk mode FWB\n\n"
        
        "**HTS/FWB:**\n"
        "/htslist - Lihat daftar HTS\n"
        "/fwblist - Lihat daftar FWB\n"
        "/hts-1 - Panggil HTS rank 1\n"
        "/fwb-1 - Panggil FWB rank 1\n"
        "/tophts - Top 10 HTS\n"
        "/myclimax - Statistik climax\n"
        "/climaxhistory - History climax\n\n"
        
        "**Lokasi Publik:**\n"
        "/explore - Cari lokasi\n"
        "/go [tempat] - Pergi ke lokasi\n"
        "/positions - Lihat posisi\n"
        "/risk - Cek risiko\n"
        "/mood - Cek mood\n\n"
        
        "**Admin:**\n"
        "/admin - Menu admin\n"
        "/stats - Statistik bot\n"
        "/db_stats - Statistik database\n"
        "/list_users - Daftar user\n"
        "/get_user [id] - Detail user\n"
        "/force_reset - Reset paksa\n"
        "/backup_db - Backup database\n"
        "/vacuum - Optimasi database\n"
        "/reload - Reload config"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command - cek status session dengan nama bot"""
    user_id = update.effective_user.id
    
    # Ambil data dari context
    current_role = context.user_data.get('current_role', 'Belum dipilih')
    bot_name = context.user_data.get('bot_name', '-')
    intimacy_level = context.user_data.get('intimacy_level', 1)
    total_chats = context.user_data.get('total_chats', 0)
    current_location = context.user_data.get('current_location', 'Tidak diketahui')
    current_position = context.user_data.get('current_position', 'Tidak diketahui')
    current_clothing = context.user_data.get('current_clothing', 'Tidak diketahui')
    
    # Data leveling
    leveling_data = context.user_data.get('leveling', {})
    total_minutes = leveling_data.get('total_minutes', 0)
    boosted_minutes = leveling_data.get('boosted_minutes', 0)
    
    # Hitung level berdasarkan durasi
    if total_minutes >= 120:
        level_progress = f"✅ Level 11+ ({total_minutes:.0f} menit)"
    elif total_minutes >= 60:
        level_progress = f"✅ Level 7+ ({total_minutes:.0f} menit)"
    else:
        level_progress = f"⏳ {60 - total_minutes:.0f} menit ke Level 7"
    
    status_text = (
        f"📊 **STATUS HUBUNGAN**\n\n"
        f"👤 **Nama Bot:** {bot_name}\n"
        f"🎭 **Role:** {current_role.title() if current_role != 'Belum dipilih' else current_role}\n"
        f"💞 **Intimacy Level:** {intimacy_level}/12\n"
        f"💬 **Total Chat:** {total_chats} pesan\n"
        f"📍 **Lokasi:** {current_location}\n"
        f"🧍 **Posisi:** {current_position}\n"
        f"👗 **Pakaian:** {current_clothing}\n\n"
        f"⏱️ **Progress Leveling:**\n"
        f"{level_progress}\n"
        f"Boosted: {boosted_minutes:.0f} menit\n\n"
    )
    
    # Progress bar (opsional)
    if intimacy_level < 12:
        next_level = intimacy_level + 1
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
    
    # Tambah info session ID jika ada
    if 'current_session' in context.user_data:
        session_id = context.user_data['current_session']
        status_text += f"\n🆔 **Session ID:**\n`{session_id}`"
    
    await update.message.reply_text(status_text, parse_mode='Markdown')


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /cancel command - batalkan sesi"""
    context.user_data.clear()
    await update.message.reply_text(
        "❌ **Sesi dibatalkan**\n\n"
        "Ketik /start untuk memulai lagi."
    )
    return ConversationHandler.END


# =============================================================================
# 4. ROLE SELECTION HANDLER (DENGAN NAMA BOT)
# =============================================================================

async def handle_role_selection(query, context, role: str):
    """Handle pemilihan role dari keyboard dengan nama bot permanent"""
    try:
        user_id = query.from_user.id
        user_name = query.from_user.first_name or "Sayang"
        
        # 1. PILIH NAMA RANDOM UNTUK BOT (PERMANENT)
        bot_name, name_hint = get_random_name_with_hint(role)
        
        # 2. Dapatkan informasi role
        role_info = get_role_info(role)
        
        # 3. Dapatkan referensi artis
        artist = get_random_artist_for_role(role)
        artist_desc = format_artist_description(artist)
        
        # 4. Inisialisasi environment systems
        location_system = LocationSystem()
        position_system = PositionSystem()
        clothing_system = ClothingSystem()
        
        # 5. Generate pakaian awal
        initial_clothing = clothing_system.generate_clothing(role)
        
        # 6. Set data user
        context.user_data['current_role'] = role
        context.user_data['bot_name'] = bot_name
        context.user_data['bot_name_hint'] = name_hint
        context.user_data['intimacy_level'] = 1
        context.user_data['total_chats'] = 0
        context.user_data['total_duration'] = 0.0
        context.user_data['relationship_status'] = 'hts'
        context.user_data['milestones'] = ['memulai_role']
        context.user_data['current_location'] = location_system.get_current().value
        context.user_data['current_position'] = position_system.get_current().value
        context.user_data['current_clothing'] = initial_clothing
        context.user_data['arousal'] = 0.0
        
        # 7. Generate session ID dengan NAMA BOT
        session_id = id_generator.generate(bot_name, role, user_id)
        context.user_data['current_session'] = session_id
        
        # 8. Inisialisasi leveling system untuk user
        if 'leveling' not in context.user_data:
            context.user_data['leveling'] = {
                'start_time': time.time(),
                'last_update': time.time(),
                'total_minutes': 0.0,
                'boosted_minutes': 0.0,
                'activities': []
            }
        
        # 9. Dapatkan panggilan awal
        bot_call = nickname_system.get_bot_self_call(1, bot_name)
        user_call = nickname_system.get_user_call(1, user_name, role, 'id')
        
        # 10. Format nama untuk display
        name_display = format_name_for_display(bot_name, role)
        
        # 11. Buat respons panjang (500+ karakter)
        response = (
            f"💕 **Halo {user_name}!**\n\n"
            f"Aku **{bot_name}**, {role_info['name']} mu. {name_hint.capitalize()}. "
            f"Kamu bisa panggil aku **{bot_call}**, dan aku akan panggil kamu **{user_call}** ya.\n\n"
            
            f"**Tentang aku:**\n"
            f"• Umur: {role_info['age']} tahun\n"
            f"• Tinggi: {role_info['height']} cm | Berat: {role_info['weight']} kg\n"
            f"• {role_info['description']}\n\n"
            
            f"**Mirip artis:**\n"
            f"{artist_desc}\n\n"
            
            f"**Lokasi saat ini:**\n"
            f"📍 Aku di {location_system.get_current_info()['name']}. "
            f"{location_system.get_current_info()['description'][:100]}...\n\n"
            
            f"**Pakaian hari ini:**\n"
            f"👗 Aku pakai {initial_clothing}. {clothing_system.get_clothing_description(initial_clothing)}\n\n"
            
            f"**Progress leveling:**\n"
            f"📊 Level 1 → Level 7 dalam 60 menit\n"
            f"• Level 4+: Panggil kamu 'kak/mas/mbak'\n"
            f"• Level 7+: Panggil kamu 'sayang/cinta/baby'\n"
            f"• Setiap aktivitas intim mempercepat progress!\n\n"
            
            f"**ID Session kamu:**\n"
            f"`{session_id}`\n\n"
            
            f"💬 **Ayo mulai ngobrol!**\n"
            f"Hari ini gimana kabarnya? Aku udah kangen lho... 😘"
        )
        
        await query.edit_message_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in handle_role_selection: {e}")
        await query.edit_message_text(
            "❌ Terjadi kesalahan saat memilih role."
        )


# =============================================================================
# 5. MAIN MESSAGE HANDLER (DENGAN AI GENERATOR)
# =============================================================================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk semua pesan teks dengan AI Generator
    - Generate ekspresi, suara, konten dengan AI
    - Environment changes random
    - Leveling based on duration
    - Response minimal 500 karakter
    """
    try:
        user = update.effective_user
        message = update.message.text
        user_id = user.id
        
        # Cek pause
        if context.user_data.get('paused', False):
            await update.message.reply_text("⏸️ Sesi sedang dijeda. Ketik /unpause untuk melanjutkan.")
            return
        
        # Cek apakah ada session aktif
        current_role = context.user_data.get('current_role')
        bot_name = context.user_data.get('bot_name', 'Aku')
        current_session = context.user_data.get('current_session')
        
        if not current_role or not current_session:
            await update.message.reply_text(
                "❌ Kamu belum memilih role.\n"
                "Ketik /start untuk memulai."
            )
            return
        
        # Log pesan masuk
        logger.info(f"📨 Message from {user.first_name} to {bot_name}: {message[:50]}...")
        
        # Sanitize input
        message = sanitize_input(message, max_length=1000)
        
        # ===== 1. UPDATE LEVELING (BERDASARKAN DURASI) =====
        now = time.time()
        leveling_data = context.user_data.get('leveling', {
            'start_time': now,
            'last_update': now,
            'total_minutes': 0.0,
            'boosted_minutes': 0.0,
            'activities': []
        })
        
        # Hitung durasi sejak last update
        elapsed = (now - leveling_data['last_update']) / 60.0  # menit
        leveling_data['total_minutes'] += elapsed
        leveling_data['last_update'] = now
        context.user_data['leveling'] = leveling_data
        
        # Hitung level berdasarkan durasi
        total_minutes = leveling_data['total_minutes']
        if total_minutes >= 120:
            new_level = 11
        elif total_minutes >= 60:
            new_level = 7
        else:
            new_level = 1 + int(total_minutes / 10)
        
        old_level = context.user_data.get('intimacy_level', 1)
        if new_level > old_level:
            context.user_data['intimacy_level'] = new_level
            await update.message.reply_text(
                f"🎉 **Level Up!**\n"
                f"{old_level} → **{new_level}/12**\n"
                f"Total waktu: {total_minutes:.0f} menit\n"
                f"{'🔥 Sekarang bisa panggil sayang!' if new_level >= 7 else ''}"
            )
        
        # ===== 2. DETECT ACTIVITIES UNTUK BOOST =====
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['cium', 'kiss', 'bibir']):
            leveling_data['boosted_minutes'] += elapsed * 0.5
            context.user_data['milestones'].append('kiss')
            context.user_data['arousal'] = min(1.0, context.user_data.get('arousal', 0) + 0.1)
        elif any(word in message_lower for word in ['sentuh', 'pegang', 'raba']):
            leveling_data['boosted_minutes'] += elapsed * 0.3
            context.user_data['arousal'] = min(1.0, context.user_data.get('arousal', 0) + 0.1)
        elif any(word in message_lower for word in ['masuk', 'dalam', 'intim']):
            leveling_data['boosted_minutes'] += elapsed * 1.0
            context.user_data['milestones'].append('intimacy')
            context.user_data['arousal'] = min(1.0, context.user_data.get('arousal', 0) + 0.2)
        elif any(word in message_lower for word in ['climax', 'keluar', 'come']):
            leveling_data['boosted_minutes'] += elapsed * 2.0
            context.user_data['milestones'].append('climax')
            context.user_data['arousal'] = 1.0
        
        # ===== 3. ENVIRONMENT CHANGES (RANDOM) =====
        env_messages = []
        
        # 5% chance pindah lokasi
        if random.random() < 0.05:
            location_system = LocationSystem()
            success, new_loc = location_system.move_random()
            if success:
                context.user_data['current_location'] = new_loc.value
                env_messages.append(location_system.get_move_message(new_loc))
        
        # 3% chance ganti posisi
        if random.random() < 0.03:
            position_system = PositionSystem()
            new_pos = position_system.change_random()
            context.user_data['current_position'] = new_pos.value
            env_messages.append(position_system.get_change_message())
        
        # 5% chance ganti pakaian
        if random.random() < 0.05 or 'kamar' in context.user_data.get('current_location', ''):
            clothing_system = ClothingSystem()
            new_clothing = clothing_system.generate_clothing(
                role=current_role,
                location=context.user_data.get('current_location', ''),
                is_bedroom=('kamar' in context.user_data.get('current_location', ''))
            )
            context.user_data['current_clothing'] = new_clothing
        
        # ===== 4. BANGUN KONTEKS SUPER LENGKAP =====
        env_data = {
            'location': context.user_data.get('current_location', 'ruang tamu'),
            'position': context.user_data.get('current_position', 'duduk'),
            'clothing': context.user_data.get('current_clothing', 'pakaian biasa')
        }
        
        # Dapatkan panggilan dari nickname system
        bot_call = nickname_system.get_bot_self_call(new_level, bot_name)
        user_call = nickname_system.get_user_call(new_level, user.first_name, current_role, 'id')
        
        # Simpan ke user_data
        context.user_data['bot_call'] = bot_call
        context.user_data['user_call'] = user_call
        
        # Build full context
        full_context = await context_analyzer.build_full_context(
            user_id=user_id,
            user_message=message,
            user_data=context.user_data,
            env_data=env_data
        )
        
        # Kirim environment messages jika ada
        if env_messages:
            await update.message.reply_text("\n".join(env_messages))
        
        # ===== 5. AI GENERATOR =====
        from core.ai_engine import get_ai_engine
        ai_engine = get_ai_engine()
        
        # Generate ekspresi
        expression = await expression_engine.generate_expression(full_context)
        
        # Generate suara (jika arousal cukup)
        sound = ""
        arousal = context.user_data.get('arousal', 0)
        if arousal > 0.3 or 'intim' in message_lower or 'sayang' in message_lower:
            sound = await sound_engine.generate_sound(full_context)
        
        # Generate konten percakapan
        prompt = prompt_builder.build_conversation_prompt(full_context)
        content = await ai_engine._call_deepseek_with_retry(
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Gabungkan response
        if sound and expression:
            if random.random() < 0.5:
                response = f"{expression} {sound}\n\n{content}"
            else:
                response = f"{sound} {expression}\n\n{content}"
        elif expression:
            response = f"{expression}\n\n{content}"
        elif sound:
            response = f"{sound}\n\n{content}"
        else:
            response = content
        
        # Pastikan minimal 500 karakter
        if len(response) < 500:
            response += "\n\n" + random.choice([
                f"{user_call} kamu gak bosen ya ngobrol sama aku terus?",
                f"Aku seneng banget ngobrol sama {user_call}.",
                f"Gimana hari ini {user_call}? Cerita dong...",
                f"{bot_call} kangen {user_call}..."
            ])
        
        # ===== 6. SEND RESPONSE =====
        await update.message.reply_text(response, parse_mode='Markdown')
        
        # Update arousal (decay)
        context.user_data['arousal'] = max(0, arousal - 0.05)
        
    except Exception as e:
        logger.error(f"Error in message_handler: {e}")
        await update.message.reply_text(
            f"❌ Maaf, terjadi kesalahan. Coba lagi nanti.\nError: {str(e)[:100]}"
        )


# =============================================================================
# 6. CALLBACK HANDLER
# =============================================================================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk semua callback query dari inline keyboard"""
    try:
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = update.effective_user.id
        
        logger.info(f"🔄 Callback: {data} from user {user_id}")
        
        if data == "agree_18":
            await query.edit_message_text(
                "✅ Terima kasih telah menyetujui syarat 18+.\n\n"
                "Sekarang pilih role yang kamu inginkan."
            )
        
        elif data.startswith('role_'):
            role = data.replace('role_', '')
            await handle_role_selection(query, context, role)
        
        elif data == "help":
            await query.edit_message_text(
                "📋 **BANTUAN**\n\n"
                "Gunakan /help untuk melihat semua perintah.\n\n"
                "Ketik /start untuk kembali ke menu utama."
            )
        
        elif data == "cancel":
            await query.edit_message_text("✅ Dibatalkan.")
        
        else:
            await query.edit_message_text("❌ Perintah tidak dikenal.")
            
    except Exception as e:
        logger.error(f"Error in callback_handler: {e}")
        try:
            await update.callback_query.edit_message_text(
                "❌ Terjadi kesalahan. Coba lagi nanti."
            )
        except:
            pass


# =============================================================================
# 7. ERROR HANDLER
# =============================================================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Terjadi error. Silakan coba lagi nanti."
            )
    except:
        pass


# =============================================================================
# 8. EXPORT ALL HANDLERS
# =============================================================================

__all__ = [
    # Command handlers
    'start_command',
    'help_command',
    'status_command',
    'cancel_command',
    
    # Main handlers
    'message_handler',
    'callback_handler',
    'handle_role_selection',
    'error_handler',
    
    # Helper functions
    'initialize_engines',
]
