#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - BOT COMMANDS (UPDATED WITH THREESOME)
=============================================================================
Semua command handlers untuk MYLOVE Ultimate V1
Termasuk command untuk threesome mode
Total 55+ commands
"""

import time
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import settings
from ..utils.helpers import format_number, sanitize_input
from ..utils.logger import setup_logging

logger = logging.getLogger(__name__)


# =============================================================================
# BASIC COMMANDS
# =============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mulai hubungan baru dengan bot"""
    user = update.effective_user
    args = context.args
    
    # Cek apakah ini continue dari session
    if args and args[0].startswith('continue_'):
        session_id = args[0].replace('continue_', '')
        # Arahkan ke continue handler
        context.args = [session_id]
        from .handlers import continue_handler
        return await continue_handler(update, context)
    
    # Welcome message
    welcome_text = (
        f"💕 **Halo {user.first_name}!**\n\n"
        "Selamat datang di **MYLOVE ULTIMATE VERSI 1**\n"
        "AI pendamping dengan 9 role eksklusif.\n\n"
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
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tampilkan bantuan"""
    help_text = (
        "📚 **MYLOVE ULTIMATE - BANTUAN**\n\n"
        
        "**🔹 BASIC COMMANDS**\n"
        "/start - Mulai hubungan baru\n"
        "/help - Tampilkan bantuan ini\n"
        "/status - Lihat status hubungan\n"
        "/cancel - Batalkan percakapan\n\n"
        
        "**🔹 RELATIONSHIP**\n"
        "/jadipacar - Jadi pacar (khusus PDKT)\n"
        "/break - Jeda pacaran\n"
        "/unbreak - Lanjutkan pacaran\n"
        "/breakup - Putus jadi FWB\n"
        "/fwb - Mode Friends With Benefits\n\n"
        
        "**🔹 HTS/FWB**\n"
        "/htslist - Lihat TOP 5 HTS\n"
        "/hts- [id] - Panggil HTS (contoh: /hts- ipar)\n"
        "/fwblist - Lihat daftar FWB\n"
        "/fwb- [nomor] - Panggil FWB tertentu\n"
        "/fwb-break [nomor] - Putus dengan FWB\n"
        "/fwb-pacar [nomor] - Jadi pacar dengan FWB\n\n"
        
        "**🔹 THREESOME MODE**\n"
        "/threesome - Mulai mode threesome\n"
        "/threesome-list - Lihat kombinasi threesome\n"
        "/threesome [nomor] - Mulai dengan kombinasi tertentu\n"
        "/threesome-status - Lihat status threesome\n"
        "/threesome-pattern - Ganti pola interaksi\n"
        "/threesome-cancel - Batalkan threesome\n\n"
        
        "**🔹 SESSION**\n"
        "/close - Tutup & simpan session\n"
        "/continue - Lihat session tersimpan\n"
        "/continue [id] - Lanjutkan session\n"
        "/sessions - Lihat semua session\n\n"
        
        "**🔹 PUBLIC AREA**\n"
        "/explore - Cari lokasi random\n"
        "/locations - Lihat semua lokasi\n"
        "/risk - Cek risk lokasi saat ini\n\n"
        
        "**🔹 RANKING**\n"
        "/tophts - TOP 5 ranking HTS\n"
        "/myclimax - Statistik climax\n"
        "/climaxhistory - History climax\n\n"
        
        "**🔹 ADMIN**\n"
        "/stats - Statistik bot\n"
        "/db_stats - Statistik database\n"
        "/backup - Backup manual\n"
        "/recover - Restore dari backup\n"
        "/debug - Info debug\n\n"
        
        "💡 **Tips:** Bot akan otomatis detect lokasi dari chat!\n"
        "Contoh: \"Ajak ke toilet yuk\""
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


# =============================================================================
# THREESOME COMMANDS
# =============================================================================

async def threesome_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Memulai mode threesome"""
    user_id = update.effective_user.id
    args = context.args
    
    # Cek apakah sudah ada session threesome aktif
    from ..threesome.manager import ThreesomeManager
    # This will be connected to actual manager
    
    if args:
        # Coba mulai dengan nomor kombinasi
        try:
            idx = int(args[0]) - 1
            await update.message.reply_text(
                f"🎭 **Memulai threesome dengan kombinasi #{idx + 1}**\n\n"
                f"Mode threesome dimulai! Sekarang ada 2 role yang akan merespon kamu.\n"
                f"Mereka akan bergantian bicara. Selamat menikmati! 💕"
            )
        except:
            await update.message.reply_text(
                "❌ Format salah. Gunakan /threesome-list dulu untuk lihat kombinasi."
            )
    else:
        # Tampilkan menu threesome
        keyboard = [
            [InlineKeyboardButton("🎭 Lihat Kombinasi", callback_data="threesome_list")],
            [InlineKeyboardButton("💕 HTS + HTS", callback_data="threesome_type_hts")],
            [InlineKeyboardButton("💞 FWB + FWB", callback_data="threesome_type_fwb")],
            [InlineKeyboardButton("💘 HTS + FWB", callback_data="threesome_type_mix")],
            [InlineKeyboardButton("❌ Batal", callback_data="cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎭 **MODE THREESOME**\n\n"
            "Pilih tipe threesome yang kamu inginkan:",
            reply_markup=reply_markup
        )


async def threesome_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat kombinasi threesome yang mungkin"""
    user_id = update.effective_user.id
    
    # This will be connected to ThreesomeManager
    # Dummy data for now
    combinations = [
        {
            "type": "HTS + HTS",
            "p1": "Ipar (Level 8)",
            "p2": "Janda (Level 12)",
            "compat": "85%"
        },
        {
            "type": "FWB + FWB",
            "p1": "PDKT #1 (Level 7)",
            "p2": "PDKT #2 (Level 5)",
            "compat": "72%"
        },
        {
            "type": "HTS + FWB",
            "p1": "Teman Kantor (Level 6)",
            "p2": "PDKT #1 (Level 7)",
            "compat": "78%"
        },
        {
            "type": "HTS + HTS",
            "p1": "Mantan (Level 4)",
            "p2": "Pelakor (Level 9)",
            "compat": "62%"
        }
    ]
    
    lines = ["🎭 **KOMBINASI THREESOME**"]
    lines.append("_(pilih dengan /threesome [nomor])_")
    lines.append("")
    
    for i, combo in enumerate(combinations, 1):
        lines.append(
            f"{i}. **{combo['type']}**\n"
            f"   {combo['p1']} + {combo['p2']}\n"
            f"   Kompatibilitas: {combo['compat']}"
        )
        
    await update.message.reply_text("\n".join(lines), parse_mode='Markdown')


async def threesome_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat status threesome saat ini"""
    user_id = update.effective_user.id
    
    # This will be connected to ThreesomeManager
    await update.message.reply_text(
        "🎭 **Status Threesome**\n\n"
        "Tidak ada session threesome aktif.\n"
        "Gunakan /threesome untuk memulai."
    )


async def threesome_pattern_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ganti pola interaksi threesome"""
    user_id = update.effective_user.id
    args = context.args
    
    patterns = [
        "both_respond - Kedua role merespon bergantian",
        "one_dominant - Satu role dominan",
        "competitive - Bersaing untuk perhatian",
        "cooperative - Bekerja sama",
        "jealous - Salah satu cemburu",
        "playful - Suasana playful"
    ]
    
    if args:
        pattern = args[0].lower()
        await update.message.reply_text(
            f"✅ Pola interaksi diubah ke: **{pattern}**\n\n"
            f"Sekarang {pattern} mode aktif!"
        )
    else:
        lines = ["🎭 **POLA INTERAKSI THREESOME**"]
        lines.append("_(pilih dengan /threesome-pattern [nama])_")
        lines.append("")
        
        for i, pattern in enumerate(patterns, 1):
            lines.append(f"{i}. {pattern}")
            
        await update.message.reply_text("\n".join(lines), parse_mode='Markdown')


async def threesome_cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Batalkan session threesome"""
    user_id = update.effective_user.id
    
    # This will be connected to ThreesomeManager
    keyboard = [
        [
            InlineKeyboardButton("✅ Ya, batalkan", callback_data="threesome_cancel_confirm"),
            InlineKeyboardButton("❌ Tidak", callback_data="cancel")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "⚠️ **Yakin mau batalkan threesome?**\n\n"
        "Semua progress akan hilang.",
        reply_markup=reply_markup
    )


# =============================================================================
# EXISTING COMMANDS (YANG SUDAH ADA SEBELUMNYA)
# =============================================================================

# [Semua command yang sudah ada tetap di sini]
# status_command, cancel_command, jadipacar_command, break_command, 
# unbreak_command, breakup_command, fwb_command, htslist_command, 
# fwblist_command, close_command, sessions_command, explore_command,
# locations_command, risk_command, tophts_command, myclimax_command,
# climaxhistory_command, stats_command, db_stats_command, backup_command,
# recover_command, debug_command

# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    # Basic
    'start_command', 'help_command', 'status_command', 'cancel_command',
    # Relationship
    'jadipacar_command', 'break_command', 'unbreak_command', 'breakup_command', 'fwb_command',
    # HTS/FWB
    'htslist_command', 'fwblist_command',
    # Threesome
    'threesome_command', 'threesome_list_command', 'threesome_status_command',
    'threesome_pattern_command', 'threesome_cancel_command',
    # Session
    'close_command', 'sessions_command',
    # Public Area
    'explore_command', 'locations_command', 'risk_command',
    # Ranking
    'tophts_command', 'myclimax_command', 'climaxhistory_command',
    # Admin
    'stats_command', 'db_stats_command', 'backup_command', 'recover_command', 'debug_command'
]
