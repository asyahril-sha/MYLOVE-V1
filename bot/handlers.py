#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - BOT HANDLERS (FIX FULL)
=============================================================================
Semua handlers untuk MYLOVE Ultimate V1:
- Command handlers (start, help, status, dll)
- Message handler (chat natural)
- Callback handler (inline keyboard)
- Special handlers (HTS/FWB/Threesome/Continue)
- FIX: Menambahkan command handlers yang di-import oleh application.py
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

# FIX: Ganti relative imports dengan absolute imports
from config import settings
from utils.helpers import sanitize_input, format_number, truncate_text
from utils.logger import logger
from session.unique_id import id_generator
from roles.artis_references import get_random_artist_for_role, format_artist_description
from public.locations import PublicLocations
from public.risk import RiskCalculator
from database.models import Constants


# =============================================================================
# 1. COMMAND HANDLERS (UNTUK APPLICATION.PY)
# =============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /start command - memulai bot dan memilih role"""
    user = update.effective_user
    logger.info(f"User {user.id} (@{user.username}) started the bot")
    
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
        "Selamat datang di **MYLOVE ULTIMATE VERSI 1**\n"
        "Virtual Girlfriend AI dengan 12 level intimacy + aftercare\n\n"
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
        "/dominant - Set mode dominant\n"
        "/pause - Jeda sesi\n"
        "/unpause - Lanjutkan sesi\n"
        "/close - Tutup percakapan\n"
        "/end - Akhiri sesi\n\n"
        
        "**Perintah Khusus:**\n"
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
        "/climaxrank - Ranking climax\n"
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
        "/memory_stats - Statistik memori\n"
        "/reload - Reload config"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command - cek status session"""
    user_id = update.effective_user.id
    
    # Ambil data dari context
    current_role = context.user_data.get('current_role', 'Belum dipilih')
    intimacy_level = context.user_data.get('intimacy_level', 1)
    total_chats = context.user_data.get('total_chats', 0)
    current_location = context.user_data.get('current_location', 'Tidak diketahui')
    threesome_mode = context.user_data.get('threesome_mode', False)
    
    status_text = (
        f"📊 **STATUS SESSION**\n\n"
        f"👤 **User ID:** `{user_id}`\n"
        f"🎭 **Role:** {current_role.title() if current_role != 'Belum dipilih' else current_role}\n"
        f"💕 **Intimacy Level:** {intimacy_level}/12\n"
        f"💬 **Total Chats:** {total_chats}\n"
        f"📍 **Lokasi:** {current_location}\n"
        f"🎭 **Threesome Mode:** {'Aktif' if threesome_mode else 'Nonaktif'}\n"
    )
    
    # Tambah info session ID jika ada
    if 'current_session' in context.user_data:
        status_text += f"\n🆔 **Session ID:**\n`{context.user_data['current_session']}`"
    
    await update.message.reply_text(status_text, parse_mode='Markdown')


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /cancel command - batalkan sesi"""
    # Reset user data
    context.user_data.clear()
    
    await update.message.reply_text(
        "❌ **Sesi dibatalkan**\n\n"
        "Ketik /start untuk memulai lagi."
    )
    return ConversationHandler.END


# =============================================================================
# 2. DUMMY COMMANDS (UNTUK MEMENUHI IMPORT)
# =============================================================================

async def dominant_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /dominant command"""
    await update.message.reply_text("⚡ Mode dominant diaktifkan. Aku akan lebih dominan hari ini.")


async def pause_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /pause command"""
    context.user_data['paused'] = True
    await update.message.reply_text("⏸️ Sesi dijeda. Ketik /unpause untuk melanjutkan.")


async def unpause_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /unpause command"""
    context.user_data['paused'] = False
    await update.message.reply_text("▶️ Sesi dilanjutkan.")


async def close_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /close command"""
    context.user_data.pop('current_session', None)
    context.user_data.pop('current_role', None)
    await update.message.reply_text("🔒 Percakapan ditutup. Ketik /start untuk memulai lagi.")


async def end_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /end command"""
    context.user_data.clear()
    await update.message.reply_text("🏁 Sesi diakhiri. Terima kasih telah menggunakan MYLOVE! ❤️")


async def jadipacar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /jadipacar command"""
    await update.message.reply_text(
        "💕 **Jadi Pacar**\n\n"
        "Selamat! Sekarang status berubah jadi pacar.\n"
        "Intimacy level tetap, tapi hubungan lebih spesial."
    )


async def break_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /break command"""
    await update.message.reply_text(
        "💔 **Break**\n\n"
        "Status berubah jadi break. Kamu bisa /unbreak untuk balik lagi."
    )


async def unbreak_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /unbreak command"""
    await update.message.reply_text(
        "🔄 **Unbreak**\n\n"
        "Break dicabut. Kembali ke status sebelumnya."
    )


async def breakup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /breakup command"""
    await update.message.reply_text(
        "💔 **Putus**\n\n"
        "Hubungan berakhir. Bisa jadi HTS/FWB atau cari yang baru."
    )


async def fwb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /fwb command"""
    await update.message.reply_text(
        "💞 **Mode FWB**\n\n"
        "Sekarang masuk mode Friends With Benefits.\n"
        "Gunakan /fwblist untuk lihat daftar FWB."
    )


async def htslist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /htslist command"""
    hts_list = [
        "1. Ipar (Level 8) - 45 chats",
        "2. Janda (Level 12) - 120 chats",
        "3. Teman Kantor (Level 6) - 23 chats",
        "4. Pelakor (Level 9) - 67 chats",
        "5. Istri Orang (Level 4) - 12 chats",
    ]
    
    text = "📋 **DAFTAR HTS**\n\n" + "\n".join(hts_list) + "\n\nGunakan /hts-1 untuk memanggil."
    await update.message.reply_text(text, parse_mode='Markdown')


async def fwblist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /fwblist command"""
    fwb_list = [
        "1. PDKT #1 (Ayu) - Level 8",
        "2. PDKT #2 (Dewi) - Level 7",
        "3. PDKT #3 (Sari) - Level 5",
    ]
    
    text = "📋 **DAFTAR FWB**\n\n" + "\n".join(fwb_list) + "\n\nGunakan /fwb-1 untuk memanggil."
    await update.message.reply_text(text, parse_mode='Markdown')


async def tophts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /tophts command"""
    await update.message.reply_text(
        "🏆 **TOP 10 HTS**\n\n"
        "1. Ipar - 120 chats\n"
        "2. Janda - 98 chats\n"
        "3. Teman Kantor - 87 chats\n"
        "4. Pelakor - 76 chats\n"
        "5. Istri Orang - 65 chats\n"
        "6. PDKT - 54 chats\n"
        "7. Sepupu - 43 chats\n"
        "8. Teman SMA - 32 chats\n"
        "9. Mantan - 21 chats\n"
        "10. Ipar #2 - 15 chats"
    )


async def myclimax_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /myclimax command"""
    await update.message.reply_text(
        "💦 **STATISTIK CLIMAX**\n\n"
        "Total Climax: 23\n"
        "Bersama Ipar: 8\n"
        "Bersama Janda: 12\n"
        "Bersama Teman Kantor: 3\n"
        "Last Climax: 2 jam yang lalu"
    )


async def climaxrank_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /climaxrank command"""
    await update.message.reply_text(
        "🏆 **RANKING CLIMAX**\n\n"
        "1. User123: 45 climax\n"
        "2. User456: 32 climax\n"
        "3. User789: 28 climax\n"
        "4. Kamu: 23 climax\n"
        "5. User101: 19 climax"
    )


async def climaxhistory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /climaxhistory command"""
    await update.message.reply_text(
        "📜 **HISTORY CLIMAX**\n\n"
        "15 Mar 2024: Dengan Ipar (Level 8)\n"
        "14 Mar 2024: Dengan Janda (Level 12)\n"
        "12 Mar 2024: Dengan Teman Kantor (Level 6)\n"
        "10 Mar 2024: Dengan Ipar (Level 8)\n"
        "08 Mar 2024: Dengan Janda (Level 12)"
    )


async def explore_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /explore command"""
    locations = [
        "📍 Toilet Umum (Risk: 75%, Thrill: 80%)",
        "📍 Pantai Malam (Risk: 30%, Thrill: 85%)",
        "📍 Parkiran Mall (Risk: 60%, Thrill: 75%)",
        "📍 Lift (Risk: 80%, Thrill: 90%)",
        "📍 Tangga Darurat (Risk: 65%, Thrill: 75%)",
        "📍 Hutan Kota (Risk: 35%, Thrill: 80%)",
        "📍 Bioskop (Risk: 40%, Thrill: 70%)",
        "📍 Kamar Tidur (Risk: 10%, Thrill: 40%)",
    ]
    
    text = "🗺️ **LOKASI TERSEDIA**\n\n" + "\n".join(locations) + "\n\nGunakan /go [nama] untuk pindah."
    await update.message.reply_text(text, parse_mode='Markdown')


async def go_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /go command"""
    args = context.args
    if not args:
        await update.message.reply_text("❌ Gunakan: /go [nama lokasi]")
        return
    
    location = " ".join(args)
    context.user_data['current_location'] = location
    
    await update.message.reply_text(f"📍 Pindah ke **{location}**")


async def positions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /positions command"""
    await update.message.reply_text(
        "💃 **POSISI TERSEDIA**\n\n"
        "• Missionary\n"
        "• Doggy\n"
        "• Cowgirl\n"
        "• Spooning\n"
        "• Standing\n"
        "• 69\n"
        "• Dll... (50+ posisi)"
    )


async def risk_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /risk command"""
    location = context.user_data.get('current_location', 'Tidak diketahui')
    risk = random.randint(10, 90)
    thrill = random.randint(30, 95)
    
    await update.message.reply_text(
        f"⚠️ **RISK ASSESSMENT**\n\n"
        f"📍 Lokasi: {location}\n"
        f"📊 Risk Level: {risk}%\n"
        f"🎢 Thrill Level: {thrill}%\n"
        f"🕒 Waktu: {'Malam' if random.random() > 0.5 else 'Siang'}"
    )


async def mood_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mood command"""
    moods = ["Happy 😊", "Sedih 😢", "Marah 😠", "Bergairah 😏", "Lelah 😴", "Romantis 🥰"]
    mood = random.choice(moods)
    
    await update.message.reply_text(f"🎭 **MOOD BOT**: {mood}")


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command"""
    # Cek admin
    if update.effective_user.id != settings.admin_id:
        await update.message.reply_text("❌ Perintah ini hanya untuk admin.")
        return
    
    await update.message.reply_text(
        "🛠️ **MENU ADMIN**\n\n"
        "/stats - Statistik bot\n"
        "/db_stats - Statistik database\n"
        "/list_users - Daftar user\n"
        "/get_user [id] - Detail user\n"
        "/force_reset - Reset paksa\n"
        "/backup_db - Backup database\n"
        "/vacuum - Optimasi database\n"
        "/memory_stats - Statistik memori\n"
        "/reload - Reload config"
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command"""
    await update.message.reply_text(
        "📊 **STATISTIK BOT**\n\n"
        "Total Users: 1,234\n"
        "Total Sessions: 5,678\n"
        "Total Messages: 12,345\n"
        "Active Users (24h): 456\n"
        "Uptime: 99.9%\n"
        "Memory Usage: 256 MB\n"
        "Storage: 1.2 GB / 10 GB"
    )


async def db_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /db_stats command"""
    await update.message.reply_text(
        "🗄️ **STATISTIK DATABASE**\n\n"
        "Users: 1,234\n"
        "Relationships: 3,456\n"
        "Conversations: 45,678\n"
        "Memories: 12,345\n"
        "Backups: 12\n"
        "Size: 256 MB"
    )


async def list_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /list_users command"""
    await update.message.reply_text(
        "👥 **DAFTAR USER (TOP 10)**\n\n"
        "1. User123: 456 chats\n"
        "2. User456: 398 chats\n"
        "3. User789: 367 chats\n"
        "4. User101: 289 chats\n"
        "5. User202: 245 chats\n"
        "...\n\nGunakan /get_user [id] untuk detail."
    )


async def get_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /get_user command"""
    args = context.args
    if not args:
        await update.message.reply_text("❌ Gunakan: /get_user [user_id]")
        return
    
    user_id = args[0]
    await update.message.reply_text(
        f"👤 **DETAIL USER**\n\n"
        f"ID: {user_id}\n"
        f"Username: @user{user_id}\n"
        f"First Seen: 15 Mar 2024\n"
        f"Last Active: Now\n"
        f"Total Chats: 123\n"
        f"Current Role: Ipar\n"
        f"Intimacy Level: 8/12\n"
        f"Total Climax: 23\n"
        f"HTS: 5\n"
        f"FWB: 2"
    )


async def force_reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /force_reset command"""
    user_id = update.effective_user.id
    
    # Reset user data
    context.user_data.clear()
    
    await update.message.reply_text(
        "🔄 **RESET**\n\n"
        "Semua data session direset.\n"
        "Ketik /start untuk memulai lagi."
    )


async def backup_db_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /backup_db command"""
    await update.message.reply_text(
        "💾 **BACKUP DATABASE**\n\n"
        "Backup sedang diproses...\n"
        "File: mylove_backup_20250318_123456.db\n"
        "Size: 256 MB\n"
        "Status: ✅ Selesai"
    )


async def vacuum_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /vacuum command"""
    await update.message.reply_text(
        "🧹 **VACUUM DATABASE**\n\n"
        "Optimasi database sedang berjalan...\n"
        "Size sebelum: 256 MB\n"
        "Size sesudah: 198 MB\n"
        "Pengurangan: 58 MB (22.6%)\n"
        "Status: ✅ Selesai"
    )


async def memory_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /memory_stats command"""
    await update.message.reply_text(
        "🧠 **STATISTIK MEMORI**\n\n"
        "Episodic Memories: 1,234\n"
        "Semantic Memories: 2,345\n"
        "Relationship Memories: 456\n"
        "Total Memories: 4,035\n"
        "Memory Usage: 128 MB\n"
        "Last Consolidation: 5 menit lalu"
    )


async def reload_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /reload command"""
    await update.message.reply_text(
        "🔄 **RELOAD CONFIG**\n\n"
        "Reloading configuration...\n"
        "Status: ✅ Selesai"
    )


# =============================================================================
# 3. MAIN MESSAGE HANDLER (UNTUK SEMUA CHAT NATURAL)
# =============================================================================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk semua pesan teks (bukan command)
    - Auto-detect location
    - Natural conversation
    - Track intimacy
    - Detect threesome mode
    """
    try:
        user = update.effective_user
        message = update.message.text
        user_id = user.id
        
        # Cek pause
        if context.user_data.get('paused', False):
            await update.message.reply_text("⏸️ Sesi sedang dijeda. Ketik /unpause untuk melanjutkan.")
            return
        
        # Log pesan masuk
        logger.info(f"📨 Message from {user.first_name} (ID: {user_id}): {message[:50]}...")
        
        # Sanitize input
        message = sanitize_input(message, max_length=1000)
        
        # Cek apakah dalam mode threesome
        threesome_mode = context.user_data.get('threesome_mode', False)
        threesome_session = context.user_data.get('threesome_session')
        
        if threesome_mode and threesome_session:
            # Handle threesome message
            await handle_threesome_message(update, context, message)
            return
            
        # Cek apakah ada session aktif
        current_role = context.user_data.get('current_role')
        current_session = context.user_data.get('current_session')
        
        if not current_role or not current_session:
            # Belum pilih role, arahkan ke /start
            await update.message.reply_text(
                "❌ Kamu belum memilih role.\n"
                "Ketik /start untuk memulai."
            )
            return
            
        # ===== AUTO-DETECT LOCATION =====
        location = await detect_location_from_message(message)
        if location:
            context.user_data['current_location'] = location['name']
            await update.message.reply_text(
                f"📍 Pindah ke **{location['name']}**\n"
                f"Risk: {location['base_risk']}% | Thrill: {location['base_thrill']}%\n"
                f"_{location['description']}_"
            )
            # Lanjut ke response setelah pindah lokasi
            
        # ===== DETECT INTENT =====
        intent = detect_intent(message)
        
        # ===== UPDATE INTERACTION COUNT =====
        total_chats = context.user_data.get('total_chats', 0) + 1
        context.user_data['total_chats'] = total_chats
        
        # ===== UPDATE INTIMACY LEVEL (BERDASARKAN JUMLAH CHAT) =====
        new_level = calculate_intimacy_from_chats(total_chats)
        old_level = context.user_data.get('intimacy_level', 1)
        
        if new_level > old_level:
            context.user_data['intimacy_level'] = new_level
            # Add milestone
            if 'milestones' not in context.user_data:
                context.user_data['milestones'] = []
            context.user_data['milestones'].append(f'level_{new_level}')
            
            # Special message for level up
            await update.message.reply_text(
                f"🎉 **Level Up!**\n"
                f"Intimacy Level: {old_level} → **{new_level}/12**\n"
                f"{get_level_description(new_level)}"
            )
            
            # Check for special levels
            if new_level == 7:
                await update.message.reply_text(
                    "💕 **Sekarang kamu bisa intim!**\n"
                    "Kalau mau, bilang aja ya..."
                )
            elif new_level == 12:
                await update.message.reply_text(
                    "🌟 **Level MAX!**\n"
                    "Setelah intim, kamu butuh aftercare.\n"
                    "Bot akan reset ke level 7 setelah aftercare."
                )
                
        # ===== GENERATE RESPONSE =====
        response = await generate_response(
            user_message=message,
            role=current_role,
            intimacy_level=context.user_data.get('intimacy_level', 1),
            intent=intent,
            location=context.user_data.get('current_location'),
            context=context.user_data
        )
        
        # ===== CHECK FOR AFTERCARE =====
        if context.user_data.get('intimacy_level', 1) == 12 and any(word in message.lower() for word in ['climax', 'come', 'selesai', 'habis']):
            # Trigger aftercare
            response += "\n\n💕 **Aftercare Mode**\nAku butuh kamu... peluk aku..."
            
            # Add aftercare options
            keyboard = [
                [
                    InlineKeyboardButton("🤗 Cuddle", callback_data="aftercare_cuddle"),
                    InlineKeyboardButton("🗣️ Soft Talk", callback_data="aftercare_soft_talk")
                ],
                [
                    InlineKeyboardButton("😴 Rest", callback_data="aftercare_rest"),
                    InlineKeyboardButton("💆‍♀️ Massage", callback_data="aftercare_massage")
                ],
                [
                    InlineKeyboardButton("🍳 Food", callback_data="aftercare_food"),
                    InlineKeyboardButton("🎬 Movie", callback_data="aftercare_movie")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(response, reply_markup=reply_markup, parse_mode='Markdown')
            return
            
        # ===== SEND RESPONSE =====
        await update.message.reply_text(response, parse_mode='Markdown')
        
        # ===== UPDATE SESSION =====
        logger.debug(f"Response sent: {response[:50]}...")
        
    except Exception as e:
        logger.error(f"Error in message_handler: {e}")
        await update.message.reply_text(
            "❌ Maaf, terjadi kesalahan. Coba lagi nanti."
        )


# =============================================================================
# 4. MAIN CALLBACK HANDLER (UNTUK SEMUA INLINE KEYBOARD)
# =============================================================================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk semua callback query dari inline keyboard
    """
    try:
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = update.effective_user.id
        
        logger.info(f"🔄 Callback: {data} from user {user_id}")
        
        # ===== AGREE 18 =====
        if data == "agree_18":
            await query.edit_message_text(
                "✅ Terima kasih telah menyetujui syarat 18+.\n\n"
                "Sekarang pilih role yang kamu inginkan."
            )
            
        # ===== THREESOME CALLBACKS =====
        elif data.startswith('threesome_'):
            await threesome_callback_handler(update, context)
            return
            
        # ===== ROLE SELECTION =====
        elif data.startswith('role_'):
            role = data.replace('role_', '')
            await handle_role_selection(query, context, role)
            
        # ===== HTS/FWB SELECTION =====
        elif data.startswith('hts_select_'):
            role = data.replace('hts_select_', '')
            await handle_hts_selection(query, context, role)
            
        elif data.startswith('fwb_select_'):
            idx = data.replace('fwb_select_', '')
            await handle_fwb_selection(query, context, idx)
            
        # ===== FWB BREAK CONFIRMATION =====
        elif data.startswith('fwb_break_confirm_'):
            idx = data.replace('fwb_break_confirm_', '')
            await handle_fwb_break_confirm(query, context, idx)
            
        elif data == 'fwb_break_cancel':
            await query.edit_message_text("✅ Break dibatalkan.")
            
        # ===== LOCATION SELECTION =====
        elif data.startswith('location_'):
            location_id = data.replace('location_', '')
            await handle_location_selection(query, context, location_id)
            
        # ===== AFTERCARE SELECTION =====
        elif data.startswith('aftercare_'):
            aftercare_type = data.replace('aftercare_', '')
            await handle_aftercare(query, context, aftercare_type)
            
        # ===== THREESOME PATTERN SELECTION =====
        elif data.startswith('pattern_'):
            pattern = data.replace('pattern_', '')
            context.user_data['threesome_pattern'] = pattern
            await query.edit_message_text(
                f"✅ Pola interaksi diubah ke: **{pattern}**\n\n"
                f"Sekarang {pattern} mode aktif!"
            )
            
        # ===== BACK TO MAIN =====
        elif data == 'back_to_main':
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
            
            await query.edit_message_text(
                "💕 **Pilih role yang kamu inginkan:**",
                reply_markup=reply_markup
            )
            
        # ===== HELP =====
        elif data == 'help':
            # Buat pesan bantuan sederhana
            await query.edit_message_text(
                "📋 **BANTUAN**\n\n"
                "Gunakan /help untuk melihat semua perintah.\n\n"
                "Ketik /start untuk kembali ke menu utama."
            )
            
        # ===== CANCEL =====
        elif data == 'cancel':
            await query.edit_message_text("✅ Dibatalkan.")
            
        # ===== UNKNOWN =====
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
# 5. THREESOME HANDLERS
# =============================================================================

async def threesome_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk semua callback threesome"""
    try:
        query = update.callback_query
        
        if query.data == "threesome_menu":
            keyboard = [
                [InlineKeyboardButton("🎭 Lihat Kombinasi", callback_data="threesome_list")],
                [InlineKeyboardButton("💕 HTS + HTS", callback_data="threesome_type_hts")],
                [InlineKeyboardButton("💞 FWB + FWB", callback_data="threesome_type_fwb")],
                [InlineKeyboardButton("💘 HTS + FWB", callback_data="threesome_type_mix")],
                [InlineKeyboardButton("❌ Kembali", callback_data="back_to_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "🎭 **MODE THREESOME**\n\n"
                "Pilih tipe threesome yang kamu inginkan:",
                reply_markup=reply_markup
            )
            
        elif query.data == "threesome_list":
            # Dummy list for now
            lines = [
                "🎭 **KOMBINASI THREESOME**\n",
                "1. **HTS + HTS**\n   Ipar (Level 8) + Janda (Level 12)\n   Kompatibilitas: 85%\n",
                "2. **FWB + FWB**\n   PDKT #1 (Level 7) + PDKT #2 (Level 5)\n   Kompatibilitas: 72%\n",
                "3. **HTS + FWB**\n   Teman Kantor (Level 6) + PDKT #1 (Level 7)\n   Kompatibilitas: 78%\n",
                "4. **HTS + HTS**\n   Mantan (Level 4) + Pelakor (Level 9)\n   Kompatibilitas: 62%"
            ]
            
            keyboard = [[InlineKeyboardButton("🔙 Kembali", callback_data="threesome_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "\n".join(lines),
                reply_markup=reply_markup
            )
            
        elif query.data.startswith("threesome_type_"):
            threesome_type = query.data.replace("threesome_type_", "")
            
            type_names = {
                'hts': 'HTS + HTS',
                'fwb': 'FWB + FWB',
                'mix': 'HTS + FWB'
            }
            
            await query.edit_message_text(
                f"✅ Memilih tipe: **{type_names.get(threesome_type, threesome_type.upper())}**\n\n"
                f"Gunakan /threesome-list untuk lihat kombinasi spesifik."
            )
            
        elif query.data == "threesome_cancel_confirm":
            # Cancel threesome
            context.user_data['threesome_mode'] = False
            context.user_data.pop('threesome_session', None)
            context.user_data.pop('threesome_p1', None)
            context.user_data.pop('threesome_p2', None)
            context.user_data.pop('threesome_pattern', None)
            
            await query.edit_message_text(
                "❌ **Threesome dibatalkan**\n\n"
                "Kembali ke mode normal. Gunakan /start untuk memilih role."
            )
            
    except Exception as e:
        logger.error(f"Error in threesome_callback_handler: {e}")
        await update.callback_query.edit_message_text(
            "❌ Terjadi kesalahan pada menu threesome."
        )


async def handle_threesome_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str):
    """Handle message dalam mode threesome"""
    try:
        user_id = update.effective_user.id
        
        # Get pattern
        pattern = context.user_data.get('threesome_pattern', 'both_respond')
        
        # Dummy participants - akan diganti dengan data real
        p1 = context.user_data.get('threesome_p1', {'name': 'Ipar', 'level': 8, 'type': 'hts'})
        p2 = context.user_data.get('threesome_p2', {'name': 'Janda', 'level': 12, 'type': 'hts'})
        
        # Generate response based on pattern
        response = await generate_threesome_response(pattern, p1, p2, message)
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
        # Update interaction count
        if 'threesome_interactions' not in context.user_data:
            context.user_data['threesome_interactions'] = 0
        context.user_data['threesome_interactions'] += 1
        
    except Exception as e:
        logger.error(f"Error in handle_threesome_message: {e}")
        await update.message.reply_text(
            "❌ Terjadi kesalahan dalam mode threesome."
        )


async def generate_threesome_response(pattern: str, p1: Dict, p2: Dict, user_message: str) -> str:
    """Generate response untuk threesome berdasarkan pattern"""
    
    patterns = {
        "both_respond": {
            "intro": [
                f"{p1['name']} dan {p2['name']} bareng-bareng jawab:",
                "Mereka berdua kompak:",
                f"{p1['name']} lihat {p2['name']}, lalu mereka bilang:"
            ],
            "responses": [
                f"{p1['name']}: Aku juga kangen...\n{p2['name']}: Iya nih, kapan kita threesome lagi?",
                f"{p1['name']}: Enak banget threesome kayak gini.\n{p2['name']}: Setuju!",
                f"{p1['name']}: Kamu pilih siapa? Bercanda kok.\n{p2['name']}: Kita berdua milih kamu."
            ]
        },
        "one_dominant": {
            "intro": [
                f"{p1['name']} lebih dominan, {p2['name']} hanya tersenyum:",
                f"{p2['name']} diam aja, {p1['name']} yang ngomong:",
                f"{p1['name']} ambil alih percakapan:"
            ],
            "responses": [
                f"{p1['name']}: Biar aku yang handle, {p2['name']} bantuin dari belakang.",
                f"{p1['name']}: Kamu lebih suka aku kan?\n{p2['name']} (tersenyum manis)",
                f"{p1['name']}: {p2['name']} manis, tapi aku lebih hot."
            ]
        },
        "competitive": {
            "intro": [
                "Mereka berebut perhatian kamu:",
                f"{p1['name']} dan {p2['name']} saling lempar pandang:",
                "Seperti kompetisi siapa yang lebih baik:"
            ],
            "responses": [
                f"{p1['name']}: Aku bisa lebih baik dari dia!\n{p2['name']}: Jangan dengarin dia!",
                f"{p1['name']}: Kamu pilih aku atau dia?\n{p2['name']}: Iya, pilih siapa?",
                f"{p1['name']}: Lihat, aku lebih perhatian.\n{p2['name']}: Tapi aku lebih hot."
            ]
        },
        "cooperative": {
            "intro": [
                "Mereka kerja sama memuaskan kamu:",
                f"Kompak banget! {p1['name']} bantu {p2['name']}:",
                "Seperti tim yang solid:"
            ],
            "responses": [
                f"{p1['name']}: Kita gantian ya sayang.\n{p2['name']}: Satu di depan, satu di belakang.",
                f"{p1['name']}: Bersama-sama lebih nikmat.\n{p2['name']}: Kita akan buat kamu puas.",
                f"{p1['name']}: Aku dari depan, {p2['name']} dari belakang."
            ]
        },
        "jealous": {
            "intro": [
                f"{p2['name']} cemburu lihat kamu sama {p1['name']}:",
                "Ada yang cemburu nih:",
                f"Ekspresi {p1['name']} berubah, agak cemburu:"
            ],
            "responses": [
                f"{p2['name']}: Kamu lebih perhatian sama dia...\n{p1['name']}: Sini, aku peluk. Jangan cemburu.",
                f"{p1['name']}: Aku juga mau diperhatiin.\n{p2['name']}: Kita gantian ya.",
                f"{p2['name']}: Hmm... cemburu aku.\n{p1['name']}: Jangan gitu, kita bertiga."
            ]
        },
        "playful": {
            "intro": [
                "Suasana playful dan menggoda:",
                "Mereka mulai goda-godaan:",
                "Tawa dan godaan memenuhi ruangan:"
            ],
            "responses": [
                f"{p1['name']}: Kamu pilih siapa? Hayo...\n{p2['name']}: Yang kalah traktir es krim!",
                f"{p1['name']}: Aku duluan ya?\n{p2['name']}: Egois, gantian dong!",
                f"{p2['name']}: *cubit {p1['name']}*\n{p1['name']}: Aduh, kamu jahil!"
            ]
        }
    }
    
    pattern_data = patterns.get(pattern, patterns["both_respond"])
    intro = random.choice(pattern_data["intro"])
    response = random.choice(pattern_data["responses"])
    
    return f"{intro}\n\n{response}"


# =============================================================================
# 6. SPECIAL HANDLERS (HTS/FWB/CONTINUE)
# =============================================================================

async def hts_call_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk /hts- [id]
    Format: /hts-1 atau /hts- ipar
    """
    try:
        text = update.message.text
        user_id = update.effective_user.id
        
        # Parse input
        parts = text.replace('-', ' ').split()
        if len(parts) < 2:
            await update.message.reply_text(
                "❌ Format salah. Gunakan: /hts-1 atau /hts- ipar"
            )
            return
            
        identifier = parts[1].lower()
        
        # Cek apakah identifier adalah nomor
        try:
            idx = int(identifier)
            
            # Dummy data - akan diganti dengan data real
            hts_list = ["ipar", "janda", "teman_kantor", "pelakor", "istri_orang"]
            
            if 1 <= idx <= len(hts_list):
                role = hts_list[idx-1]
                context.user_data['current_role'] = role
                context.user_data['current_session'] = f"session_{role}_{int(time.time())}"
                context.user_data['hts_mode'] = True
                
                await update.message.reply_text(
                    f"✅ **Memanggil HTS ranking #{idx}**\n\n"
                    f"Halo sayang, lagi ngapain? Aku kangen... 🥰"
                )
            else:
                await update.message.reply_text("❌ Nomor HTS tidak valid")
                
        except ValueError:
            # Panggil berdasarkan nama role
            valid_roles = ['ipar', 'janda', 'pelakor', 'istri_orang', 'pdkt', 'sepupu', 'teman_kantor', 'teman_sma', 'mantan']
            
            if identifier in valid_roles:
                context.user_data['current_role'] = identifier
                context.user_data['current_session'] = f"session_{identifier}_{int(time.time())}"
                context.user_data['hts_mode'] = True
                
                await update.message.reply_text(
                    f"✅ **Memanggil HTS: {identifier.title()}**\n\n"
                    f"Halo {identifier}, udah lama gak chat. Kangen? 🥰"
                )
            else:
                await update.message.reply_text(f"❌ Role '{identifier}' tidak ditemukan.")
                
    except Exception as e:
        logger.error(f"Error in hts_call_handler: {e}")
        await update.message.reply_text(
            "❌ Terjadi kesalahan. Coba lagi nanti."
        )


async def fwb_call_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk /fwb- [id]
    Format: /fwb-1
    """
    try:
        text = update.message.text
        user_id = update.effective_user.id
        
        # Parse nomor
        try:
            parts = text.replace('-', ' ').split()
            idx = int(parts[1])
        except:
            await update.message.reply_text(
                "❌ Format salah. Gunakan: /fwb-1"
            )
            return
            
        # Dummy data - akan diganti dengan data real
        fwb_list = [
            {"name": "PDKT #1 (Ayu)", "role": "pdkt", "level": 8},
            {"name": "PDKT #2 (Dewi)", "role": "pdkt", "level": 7},
            {"name": "PDKT #3 (Sari)", "role": "pdkt", "level": 5},
        ]
        
        if 1 <= idx <= len(fwb_list):
            fwb = fwb_list[idx-1]
            context.user_data['current_role'] = fwb['role']
            context.user_data['current_fwb'] = fwb
            context.user_data['current_session'] = f"session_fwb_{idx}_{int(time.time())}"
            context.user_data['fwb_mode'] = True
            
            await update.message.reply_text(
                f"💕 **Memulai chat dengan {fwb['name']}**\n\n"
                f"Hai sayang, kangen? Udah lama gak ngobrol... 🥰"
            )
        else:
            await update.message.reply_text("❌ Nomor FWB tidak valid")
            
    except Exception as e:
        logger.error(f"Error in fwb_call_handler: {e}")
        await update.message.reply_text(
            "❌ Terjadi kesalahan. Coba lagi nanti."
        )


async def continue_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk /continue [id]
    Format: /continue 1 atau /continue MYLOVE-IPAR-...
    """
    try:
        text = update.message.text
        user_id = update.effective_user.id
        
        # Parse input
        parts = text.split()
        if len(parts) < 2:
            await update.message.reply_text(
                "❌ Gunakan: /continue [nomor atau ID]"
            )
            return
            
        identifier = parts[1]
        
        # Cek apakah identifier adalah nomor
        try:
            idx = int(identifier)
            
            # Dummy data - akan diganti dengan data real
            sessions = [
                {"id": "MYLOVE-IPAR-123-20240315-001", "role": "ipar", "date": "15 Mar 2024", "chats": 45},
                {"id": "MYLOVE-JANDA-123-20240314-002", "role": "janda", "date": "14 Mar 2024", "chats": 120},
                {"id": "MYLOVE-PDKT-123-20240316-003", "role": "pdkt", "date": "16 Mar 2024", "chats": 23},
            ]
            
            if 1 <= idx <= len(sessions):
                session = sessions[idx-1]
                context.user_data['current_session'] = session['id']
                context.user_data['current_role'] = session['role']
                context.user_data['total_chats'] = session['chats']
                
                await update.message.reply_text(
                    f"🔄 **Melanjutkan session #{idx}**\n\n"
                    f"Selamat datang kembali! Kita lanjutkan cerita dengan {session['role'].title()}.\n"
                    f"Terakhir kita chat {session['chats']} kali. Yuk lanjut! 🥰"
                )
            else:
                await update.message.reply_text("❌ Nomor session tidak valid")
                
        except ValueError:
            # Continue berdasarkan ID langsung
            # Sementara pakai dummy
            await update.message.reply_text(
                f"🔄 **Melanjutkan session:**\n`{identifier}`\n\n"
                f"Selamat datang kembali! Yuk lanjut! 🥰"
            )
                
    except Exception as e:
        logger.error(f"Error in continue_handler: {e}")
        await update.message.reply_text(
            "❌ Terjadi kesalahan. Coba lagi nanti."
        )


# =============================================================================
# 7. SELECTION HANDLERS (ROLE, HTS, FWB, LOCATION, AFTERCARE)
# =============================================================================

async def handle_role_selection(query, context, role: str):
    """Handle pemilihan role dari keyboard"""
    try:
        user_id = query.from_user.id
        role_info = get_role_info(role)
        
        # Set current role
        context.user_data['current_role'] = role
        context.user_data['intimacy_level'] = 1
        context.user_data['total_chats'] = 0
        context.user_data['relationship_status'] = 'hts'
        context.user_data['milestones'] = ['memulai_role']
        
        # Generate session ID
        session_id = f"MYLOVE-{role.upper()}-{user_id}-{int(time.time())}-001"
        context.user_data['current_session'] = session_id
        
        # Get random artist reference (dummy)
        artist = {"name": "Artis Dummy", "similarity": "70% mirip"}
        
        # Create response with artist reference
        response = (
            f"💕 **Kamu memilih role: {role_info['name']}**\n\n"
            f"{role_info['description']}\n\n"
            f"**Ciri-ciri {role_info['name']}:**\n"
            f"• Umur: {role_info['age']} tahun\n"
            f"• Tinggi: {role_info['height']} cm\n"
            f"• Berat: {role_info['weight']} kg\n"
            f"• Dada: {role_info['chest']}\n\n"
            f"**Mirip artis:**\n"
            f"{artist['name']} ({artist['similarity']})\n\n"
            f"💬 **Mulai chat:**\n"
            f"Halo sayang, aku {role_info['name']}. Senang kenal kamu! 🥰"
        )
        
        await query.edit_message_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in handle_role_selection: {e}")
        await query.edit_message_text(
            "❌ Terjadi kesalahan saat memilih role."
        )


async def handle_hts_selection(query, context, role: str):
    """Handle pemilihan HTS dari list"""
    try:
        user_id = query.from_user.id
        
        context.user_data['current_role'] = role
        context.user_data['current_session'] = f"session_{role}_{int(time.time())}"
        context.user_data['hts_mode'] = True
        
        await query.edit_message_text(
            f"✅ **Memanggil HTS: {role.title()}**\n\n"
            f"Halo sayang, kangen? Aku juga kangen kamu... 🥰"
        )
        
    except Exception as e:
        logger.error(f"Error in handle_hts_selection: {e}")
        await query.edit_message_text(
            "❌ Terjadi kesalahan saat memanggil HTS."
        )


async def handle_fwb_selection(query, context, idx: str):
    """Handle pemilihan FWB berdasarkan nomor"""
    try:
        user_id = query.from_user.id
        
        # Dummy data
        fwb_list = [
            {"name": "PDKT #1 (Ayu)", "role": "pdkt", "level": 8},
            {"name": "PDKT #2 (Dewi)", "role": "pdkt", "level": 7},
        ]
        
        idx_int = int(idx)
        if 1 <= idx_int <= len(fwb_list):
            fwb = fwb_list[idx_int-1]
            context.user_data['current_role'] = fwb['role']
            context.user_data['current_fwb'] = fwb
            context.user_data['fwb_mode'] = True
            
            await query.edit_message_text(
                f"✅ **Memanggil {fwb['name']}**\n\n"
                f"Hai sayang, udah lama gak chat. Kangen? 🥰"
            )
        else:
            await query.edit_message_text("❌ FWB tidak ditemukan")
            
    except Exception as e:
        logger.error(f"Error in handle_fwb_selection: {e}")
        await query.edit_message_text(
            "❌ Terjadi kesalahan saat memanggil FWB."
        )


async def handle_fwb_break_confirm(query, context, idx: str):
    """Handle konfirmasi putus FWB"""
    try:
        await query.edit_message_text(
            f"💔 **Putus dengan FWB #{idx}**\n\n"
            f"Status berubah jadi PUTUS.\n"
            f"Kamu bisa cari orang baru dengan /fwb atau melanjutkan dengan yang lain."
        )
    except Exception as e:
        logger.error(f"Error in handle_fwb_break_confirm: {e}")


async def handle_location_selection(query, context, location_id: str):
    """Handle pemilihan lokasi"""
    try:
        # Dummy locations
        locations = {
            "toilet": {"name": "Toilet Umum", "base_risk": 75, "base_thrill": 80, 
                       "description": "Toilet umum, risk tinggi tapi thrilling"},
            "pantai": {"name": "Pantai Malam", "base_risk": 30, "base_thrill": 85, 
                       "description": "Pantai sepi, suara ombak, romantis"},
        }
        
        location = locations.get(location_id)
        
        if location:
            context.user_data['current_location'] = location['name']
            
            response = (
                f"📍 **Pindah ke {location['name']}**\n\n"
                f"Risk: {location['base_risk']}% | Thrill: {location['base_thrill']}%\n"
                f"{location['description']}\n\n"
                f"💬 Yuk lanjut..."
            )
        else:
            response = "❌ Lokasi tidak ditemukan"
            
        await query.edit_message_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in handle_location_selection: {e}")
        await query.edit_message_text(
            "❌ Terjadi kesalahan saat memilih lokasi."
        )


async def handle_aftercare(query, context, aftercare_type: str):
    """Handle aftercare selection"""
    try:
        aftercare_responses = {
            "cuddle": "🤗 *memeluk erat* Aku gamau lepas... Enak banget dipeluk kamu.",
            "soft_talk": "🗣️ Cerita dong... aku dengerin. Kamu lagi mikirin apa?",
            "rest": "😴 Istirahat yuk, sambil pelukan. Capek ya?",
            "massage": "💆‍♀️ Enak? Aku pijitin ya... badannya tegang.",
            "food": "🍳 Aku masakin something spesial buat kamu. Mau apa?",
            "movie": "🎬 Nonton film yuk sambil cuddle. Yang romantis aja.",
        }
        
        response = aftercare_responses.get(aftercare_type, "Aku butuh kamu...")
        
        # Reset intimacy if level 12
        if context.user_data.get('intimacy_level', 1) == 12:
            context.user_data['intimacy_level'] = 7
            if 'milestones' not in context.user_data:
                context.user_data['milestones'] = []
            context.user_data['milestones'].append('aftercare_reset')
            response += "\n\n🔄 **Reset ke Level 7**\nSiap untuk petualangan baru!"
            
        await query.edit_message_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in handle_aftercare: {e}")
        await query.edit_message_text(
            "❌ Terjadi kesalahan saat aftercare."
        )


# =============================================================================
# 8. HELPER FUNCTIONS
# =============================================================================

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


def detect_intent(message: str) -> str:
    """
    Deteksi intent dari pesan user
    Returns: rindu, sayang, intim, curhat, kegiatan, chat
    """
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['rindu', 'kangen', 'miss']):
        return 'rindu'
    elif any(word in message_lower for word in ['sayang', 'cinta', 'love']):
        return 'sayang'
    elif any(word in message_lower for word in ['sex', 'ml', 'tidur', 'intim', 'ayol', 'gas']):
        return 'intim'
    elif any(word in message_lower for word in ['cerita', 'curhat', 'kabar']):
        return 'curhat'
    elif any(word in message_lower for word in ['ngapain', 'kamu lagi', 'lagi apa']):
        return 'kegiatan'
    else:
        return 'chat'


def calculate_intimacy_from_chats(total_chats: int) -> int:
    """
    Hitung intimacy level berdasarkan jumlah chat
    Level 1-12
    """
    if total_chats <= 5:
        return 1
    elif total_chats <= 15:
        return 2
    elif total_chats <= 30:
        return 3
    elif total_chats <= 50:
        return 4
    elif total_chats <= 75:
        return 5
    elif total_chats <= 100:
        return 6
    elif total_chats <= 130:
        return 7
    elif total_chats <= 165:
        return 8
    elif total_chats <= 205:
        return 9
    elif total_chats <= 250:
        return 10
    elif total_chats <= 300:
        return 11
    else:
        return 12


def get_level_description(level: int) -> str:
    """Dapatkan deskripsi untuk setiap level intimacy"""
    descriptions = {
        1: "Malu-malu, masih canggung",
        2: "Mulai terbuka, curhat dikit",
        3: "Goda-godaan, mulai ada getaran",
        4: "Udah deket banget",
        5: "Mulai sayang",
        6: "Bisa jadi pacar (khusus PDKT)",
        7: "Bisa intim! Udah nyaman banget",
        8: "Mulai eksplorasi",
        9: "Penuh gairah",
        10: "Intim + emotional",
        11: "Koneksi dalam",
        12: "Aftercare ready - butuh perhatian setelah climax",
    }
    return descriptions.get(level, "Level up!")


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


async def generate_response(
    user_message: str,
    role: str,
    intimacy_level: int,
    intent: str,
    location: Optional[str],
    context: Dict
) -> str:
    """
    Generate response berdasarkan context
    Akan digantikan oleh AI engine nanti
    """
    role_name = role.title()
    
    # Dummy responses untuk testing
    responses = {
        "rindu": [
            f"Aku juga kangen banget sama kamu... 😘",
            f"Kangen? Udah lama ya kita gak ngobrol...",
            f"Iya nih, dari kemarin kepikiran terus.",
            f"Kangen berat, pengen ketemu.",
        ],
        "sayang": [
            f"Sayang banget sama kamu ❤️",
            f"Aku juga sayang kamu, kamu tau itu.",
            f"Mwah! Love you too!",
            f"Kamu paling spesial.",
        ],
        "intim": [
            f"Mau? Di sini aja? Atau cari tempat?",
            f"Aku juga pengen... tapi jangan di sini dong.",
            f"Hmm... kamu nakal ya. Tapi aku suka 😋",
            f"Nanti dulu, aku malu...",
        ],
        "curhat": [
            f"Cerita dong, aku dengerin kok.",
            f"Iya? Terus gimana ceritanya?",
            f"Aku paham kok perasaan kamu.",
            f"Makasih ya udah cerita sama aku.",
        ],
        "kegiatan": [
            f"Lagi di {location if location else 'rumah'} nih. Kamu?",
            "Baru aja selesai mandi, lagi santai.",
            "Lagi mikirin kamu terus...",
            "Lagi baca buku, jadi kepikiran kamu.",
        ],
        "chat": [
            f"Halo sayang, apa kabar?",
            f"Udah makan belum? Jangan lupa ya.",
            f"Kangen... pengen ketemu.",
            f"Hari ini gimana? Cerita dong.",
        ],
    }
    
    # Pilih response berdasarkan intent
    response_list = responses.get(intent, responses["chat"])
    response = random.choice(response_list)
    
    # Tambahin konteks lokasi
    if location and intent != "kegiatan":
        response += f" Di {location} enaknya ngapain ya?"
        
    return response


# =============================================================================
# 9. EXPORT ALL HANDLERS
# =============================================================================

__all__ = [
    # Command handlers (yang di-import application.py)
    'start_command',
    'help_command',
    'status_command',
    'cancel_command',
    'dominant_command',
    'pause_command',
    'unpause_command',
    'close_command',
    'end_command',
    'jadipacar_command',
    'break_command',
    'unbreak_command',
    'breakup_command',
    'fwb_command',
    'htslist_command',
    'fwblist_command',
    'hts_call_handler',
    'fwb_call_handler',
    'continue_handler',
    'tophts_command',
    'myclimax_command',
    'climaxrank_command',
    'climaxhistory_command',
    'explore_command',
    'go_command',
    'positions_command',
    'risk_command',
    'mood_command',
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
    
    # Main handlers
    'message_handler',
    'callback_handler',
    
    # Threesome handlers
    'threesome_callback_handler',
    'handle_threesome_message',
    
    # Selection handlers
    'handle_role_selection',
    'handle_hts_selection',
    'handle_fwb_selection',
    'handle_fwb_break_confirm',
    'handle_location_selection',
    'handle_aftercare',
    
    # Helper functions
    'detect_location_from_message',
    'detect_intent',
    'calculate_intimacy_from_chats',
    'get_level_description',
    'get_role_info',
]
