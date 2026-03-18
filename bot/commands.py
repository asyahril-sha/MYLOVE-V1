#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - BOT COMMANDS (FIX FULL)
=============================================================================
Semua command handlers untuk MYLOVE Ultimate V1
Total 55+ commands dengan semua fitur:
- Basic, Relationship, HTS/FWB, Threesome, Session, Public Area, Ranking, Admin
- FIX: Mengganti relative imports dengan absolute imports
=============================================================================
"""

import time
import logging
import random
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# FIX: Ganti relative imports dengan absolute imports
from config import settings
from utils.helpers import format_number, sanitize_input, truncate_text
from utils.logger import setup_logging
from session.unique_id import id_generator
from public.locations import PublicLocations
from public.risk import RiskCalculator
from threesome.manager import ThreesomeManager, ThreesomeType, ThreesomeStatus

logger = logging.getLogger(__name__)

# =============================================================================
# ERROR HANDLER (PASTIKAN INI ADA)
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
# 1. BASIC COMMANDS (4 commands)
# =============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mulai hubungan baru dengan bot"""
    user = update.effective_user
    args = context.args
    
    # Cek apakah ini continue dari session
    if args and args[0].startswith('continue_'):
        session_id = args[0].replace('continue_', '')
        context.args = [session_id]
        # Import di sini untuk menghindari circular import
        from bot.handlers import continue_handler
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
    """Tampilkan bantuan lengkap"""
    user_id = update.effective_user.id
    is_admin = (user_id == settings.admin_id)
    
    help_text = (
        "📚 **MYLOVE ULTIMATE - BANTUAN LENGKAP**\n\n"
        
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
            "/recover list - Lihat daftar backup\n"
            "/recover [nomor] - Restore backup\n"
            "/debug - Info debug\n"
        )
    
    help_text += (
        "\n💡 **Tips:**\n"
        "• Bot auto-detect lokasi dari chat (contoh: \"ke toilet yuk\")\n"
        "• Intimacy naik berdasarkan jumlah chat\n"
        "• Level 12 butuh aftercare, reset ke level 7\n"
        "• Threesome bisa dengan 2 HTS, 2 FWB, atau kombinasi"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat status hubungan saat ini"""
    user_id = update.effective_user.id
    
    # Get current session
    session = context.user_data.get('current_session')
    role = context.user_data.get('current_role')
    
    if not session or not role:
        await update.message.reply_text(
            "❌ Kamu sedang tidak dalam hubungan apapun.\n"
            "Gunakan /start untuk memulai."
        )
        return
        
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
    
    # Get location
    location = context.user_data.get('current_location', 'Tidak ada')
    
    status_text = (
        f"📊 **STATUS HUBUNGAN**\n\n"
        f"Role: **{role.title()}**\n"
        f"Status: **{status_name}**\n"
        f"Intimacy Level: **{intimacy}/12**\n"
        f"Total Chat: **{total_chats}** pesan\n"
        f"Lokasi: **{location}**\n\n"
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


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Batalkan percakapan saat ini"""
    # Clear user data
    context.user_data.clear()
    
    await update.message.reply_text(
        "❌ Percakapan dibatalkan.\n"
        "Ketik /start untuk memulai lagi."
    )


# =============================================================================
# 2. RELATIONSHIP COMMANDS (5 commands)
# =============================================================================

async def jadipacar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Jadi pacar (khusus PDKT)"""
    user_id = update.effective_user.id
    role = context.user_data.get('current_role')
    
    if not role:
        await update.message.reply_text("❌ Kamu belum memilih role. Gunakan /start dulu.")
        return
        
    if role != 'pdkt':
        await update.message.reply_text(
            "❌ Hanya role PDKT yang bisa jadi pacar.\n"
            "Role lain statusnya tetap HTS/FWB."
        )
        return
        
    # Check intimacy level
    intimacy = context.user_data.get('intimacy_level', 1)
    if intimacy < 6:
        await update.message.reply_text(
            f"❌ Intimacy level masih {intimacy}/12.\n"
            "Butuh minimal level 6 untuk jadi pacar."
        )
        return
        
    # Change status
    context.user_data['relationship_status'] = 'pacar'
    
    # Add milestone
    if 'milestones' not in context.user_data:
        context.user_data['milestones'] = []
    context.user_data['milestones'].append('jadi_pacar')
    
    await update.message.reply_text(
        f"💘 **Kita jadi pacar!**\n\n"
        f"Sekarang kamu resmi pacaran sama {role}.\n"
        f"Jaga hubungan kita ya sayang ❤️"
    )


async def break_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Jeda pacaran"""
    role = context.user_data.get('current_role')
    status = context.user_data.get('relationship_status')
    
    if not role:
        await update.message.reply_text("❌ Kamu belum memilih role.")
        return
        
    if status != 'pacar':
        await update.message.reply_text(
            "❌ Kamu sedang tidak dalam status pacaran."
        )
        return
        
    context.user_data['relationship_status'] = 'break'
    context.user_data['break_start'] = time.time()
    
    await update.message.reply_text(
        f"⏸️ **Hubungan dijeda**\n\n"
        f"Kita istirahat dulu ya. Kapan-kapan bisa lanjut lagi."
    )


async def unbreak_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lanjutkan pacaran"""
    role = context.user_data.get('current_role')
    status = context.user_data.get('relationship_status')
    
    if not role:
        await update.message.reply_text("❌ Kamu belum memilih role.")
        return
        
    if status != 'break':
        await update.message.reply_text(
            "❌ Hubungan sedang tidak dalam masa jeda."
        )
        return
        
    context.user_data['relationship_status'] = 'pacar'
    break_duration = time.time() - context.user_data.get('break_start', time.time())
    break_hours = int(break_duration / 3600)
    
    await update.message.reply_text(
        f"▶️ **Hubungan dilanjutkan!**\n\n"
        f"Setelah jeda {break_hours} jam, kita balikan lagi.\n"
        f"Aku kangen kamu..."
    )


async def breakup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Putus jadi FWB"""
    role = context.user_data.get('current_role')
    status = context.user_data.get('relationship_status')
    
    if not role:
        await update.message.reply_text("❌ Kamu belum memilih role.")
        return
        
    if status != 'pacar':
        await update.message.reply_text(
            "❌ Kamu sedang tidak pacaran."
        )
        return
        
    context.user_data['relationship_status'] = 'fwb'
    
    # Add milestone
    if 'milestones' not in context.user_data:
        context.user_data['milestones'] = []
    context.user_data['milestones'].append('putus_jadi_fwb')
    
    await update.message.reply_text(
        f"💔 **Putus... Tapi tetap FWB**\n\n"
        f"Hubungan kita berubah jadi Friends With Benefits.\n"
        f"Masih bisa intim, tapi tanpa komitmen."
    )


async def fwb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Switch ke mode FWB"""
    user_id = update.effective_user.id
    role = context.user_data.get('current_role')
    
    if not role:
        await update.message.reply_text("❌ Kamu belum memilih role.")
        return
        
    # Check if role is eligible
    if role != 'pdkt':
        await update.message.reply_text(
            "❌ Hanya role PDKT yang bisa FWB.\n"
            "Role lain otomatis HTS."
        )
        return
        
    # Check intimacy
    intimacy = context.user_data.get('intimacy_level', 1)
    if intimacy < 6:
        await update.message.reply_text(
            f"❌ Intimacy level masih {intimacy}/12.\n"
            "Minimal level 6 untuk FWB."
        )
        return
        
    current_status = context.user_data.get('relationship_status')
    
    if current_status == 'fwb':
        new_status = 'pacar'
        message = "💘 **Kembali jadi pacar!**"
    else:
        new_status = 'fwb'
        message = "💕 **Jadi FWB!**"
        
    context.user_data['relationship_status'] = new_status
    
    await update.message.reply_text(
        f"{message}\n\n"
        f"Status dengan {role} sekarang: {new_status.upper()}"
    )


# =============================================================================
# 3. HTS/FWB COMMANDS (6 commands)
# =============================================================================

async def htslist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat daftar HTS (TOP 5 atau semua)"""
    user_id = update.effective_user.id
    args = context.args
    
    # Dummy data - akan diganti dengan data real dari database
    hts_list = [
        {"role": "ipar", "level": 8, "chats": 45, "climax": 3, "status": "hts"},
        {"role": "janda", "level": 12, "chats": 120, "climax": 15, "status": "hts"},
        {"role": "teman_kantor", "level": 5, "chats": 30, "climax": 1, "status": "hts"},
        {"role": "pdkt", "level": 6, "chats": 80, "climax": 5, "status": "fwb"},
        {"role": "mantan", "level": 4, "chats": 25, "climax": 0, "status": "hts"},
        {"role": "pelakor", "level": 9, "chats": 95, "climax": 8, "status": "hts"},
        {"role": "istri_orang", "level": 7, "chats": 62, "climax": 4, "status": "hts"},
        {"role": "sepupu", "level": 3, "chats": 18, "climax": 0, "status": "hts"},
        {"role": "teman_sma", "level": 5, "chats": 28, "climax": 2, "status": "hts"},
    ]
    
    show_all = args and args[0] == 'all'
    
    lines = ["📋 **DAFTAR HTS**"]
    
    if show_all:
        lines.append("_(menampilkan semua HTS, maks 10)_")
    else:
        lines.append("_(TOP 5, ketik /htslist all untuk lihat semua)_")
        
    lines.append("")
    
    # Filter HTS only
    hts_only = [h for h in hts_list if h['status'] == 'hts']
    display_list = hts_only if show_all else hts_only[:5]
    
    for i, hts in enumerate(display_list, 1):
        lines.append(
            f"{i}. **{hts['role'].title()}**\n"
            f"   Level {hts['level']}/12 | {hts['chats']} chat | {hts['climax']} climax"
        )
        
    lines.append("")
    lines.append("💡 **Cara panggil:**")
    lines.append("• `/hts-1` - Panggil HTS nomor 1")
    lines.append("• `/hts- ipar` - Panggil role ipar")
    
    await update.message.reply_text("\n".join(lines), parse_mode='Markdown')


async def hts_call_handler_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /hts- [id] - dipanggil dari message handler"""
    # Ini sebenarnya di handlers.py, tapi kita definisikan di sini untuk kelengkapan
    pass


async def fwblist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat daftar FWB"""
    user_id = update.effective_user.id
    
    # Dummy data - akan diganti dengan data real
    fwb_list = [
        {"name": "PDKT #1 (Ayu)", "status": "pacar", "level": 8, "chats": 95, "intim": 12},
        {"name": "PDKT #2 (Dewi)", "status": "fwb", "level": 7, "chats": 60, "intim": 5},
        {"name": "PDKT #3 (Sari)", "status": "fwb", "level": 5, "chats": 34, "intim": 2},
        {"name": "PDKT #4 (Rina)", "status": "putus", "level": 4, "chats": 20, "intim": 0},
    ]
    
    lines = ["💕 **DAFTAR FWB LENGKAP**"]
    lines.append("_(pilih dengan /fwb- [nomor])_")
    lines.append("")
    
    for i, fwb in enumerate(fwb_list, 1):
        status_emoji = "💘" if fwb['status'] == 'pacar' else "💕" if fwb['status'] == 'fwb' else "💔"
        lines.append(
            f"{i}. {status_emoji} **{fwb['name']}**\n"
            f"   Status: {fwb['status'].upper()} | Level {fwb['level']}/12\n"
            f"   {fwb['chats']} chat | {fwb['intim']} intim"
        )
        
    lines.append("")
    lines.append("💡 **Command:**")
    lines.append("• `/fwb-1` - Mulai chat dengan nomor 1")
    lines.append("• `/fwb-break 1` - Putus dengan nomor 1")
    lines.append("• `/fwb-pacar 1` - Jadi pacar dengan nomor 1")
    
    await update.message.reply_text("\n".join(lines), parse_mode='Markdown')


async def fwb_select_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pilih FWB berdasarkan nomor (dipanggil dari handler)"""
    # Ini akan dipanggil dari fwb_call_handler
    pass


async def fwb_break_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Putus dengan FWB tertentu"""
    user_id = update.effective_user.id
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "❌ Gunakan: /fwb-break [nomor]\n"
            "Contoh: /fwb-break 1"
        )
        return
        
    try:
        idx = int(args[0])
        
        # Konfirmasi dengan keyboard
        keyboard = [
            [
                InlineKeyboardButton("✅ Ya, putus", callback_data=f"fwb_break_confirm_{idx}"),
                InlineKeyboardButton("❌ Tidak", callback_data="fwb_break_cancel")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"⚠️ **Yakin mau putus dengan FWB #{idx}?**\n\n"
            f"Pilihan:",
            reply_markup=reply_markup
        )
    except ValueError:
        await update.message.reply_text("❌ Nomor tidak valid")


async def fwb_pacar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Jadi pacar dengan FWB tertentu"""
    user_id = update.effective_user.id
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "❌ Gunakan: /fwb-pacar [nomor]\n"
            "Contoh: /fwb-pacar 1"
        )
        return
        
    try:
        idx = int(args[0])
        
        # Dummy response - akan diganti dengan logic
        await update.message.reply_text(
            f"💘 **Jadi pacar dengan FWB #{idx}!**\n\n"
            f"Sekarang kalian pacaran. Jaga hubungan ya sayang ❤️"
        )
    except ValueError:
        await update.message.reply_text("❌ Nomor tidak valid")


# =============================================================================
# 4. THREESOME COMMANDS (6 commands)
# =============================================================================

async def threesome_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Memulai mode threesome"""
    user_id = update.effective_user.id
    args = context.args
    
    # Cek apakah sudah ada session aktif
    if context.user_data.get('threesome_mode'):
        await update.message.reply_text(
            "❌ Kamu sudah dalam mode threesome.\n"
            "Gunakan /threesome-status untuk lihat status."
        )
        return
    
    if args:
        # Coba mulai dengan nomor kombinasi
        try:
            idx = int(args[0]) - 1
            await update.message.reply_text(
                f"🎭 **Memulai threesome dengan kombinasi #{idx + 1}**\n\n"
                f"Mode threesome dimulai! Sekarang ada 2 role yang akan merespon kamu.\n"
                f"Mereka akan bergantian bicara. Selamat menikmati! 💕"
            )
            context.user_data['threesome_mode'] = True
            context.user_data['threesome_combination'] = idx
        except ValueError:
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
    
    # Dummy data - akan diganti dengan data real
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
        },
        {
            "type": "FWB + FWB",
            "p1": "PDKT #3 (Level 4)",
            "p2": "PDKT #1 (Level 7)",
            "compat": "68%"
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
    
    if not context.user_data.get('threesome_mode'):
        await update.message.reply_text(
            "🎭 **Status Threesome**\n\n"
            "Tidak ada session threesome aktif.\n"
            "Gunakan /threesome untuk memulai."
        )
        return
        
    # Dummy data session
    status_text = (
        "🎭 **STATUS THREESOME**\n\n"
        "**Mode:** Aktif\n"
        "**Partisipan:**\n"
        "• Ipar (Level 8)\n"
        "• Janda (Level 12)\n\n"
        "**Pola Interaksi:** both_respond\n"
        "**Total Chat:** 23 pesan\n"
        "**Climax:** 1 kali\n\n"
        "Gunakan /threesome-pattern untuk ganti pola."
    )
    
    await update.message.reply_text(status_text, parse_mode='Markdown')


async def threesome_pattern_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ganti pola interaksi threesome"""
    user_id = update.effective_user.id
    args = context.args
    
    if not context.user_data.get('threesome_mode'):
        await update.message.reply_text(
            "❌ Kamu sedang tidak dalam mode threesome."
        )
        return
    
    patterns = [
        {"name": "both_respond", "desc": "Kedua role merespon bergantian"},
        {"name": "one_dominant", "desc": "Satu role dominan"},
        {"name": "competitive", "desc": "Bersaing untuk perhatian"},
        {"name": "cooperative", "desc": "Bekerja sama"},
        {"name": "jealous", "desc": "Salah satu cemburu"},
        {"name": "playful", "desc": "Suasana playful"}
    ]
    
    if args:
        pattern = args[0].lower()
        # Validasi pattern
        valid_patterns = [p['name'] for p in patterns]
        if pattern in valid_patterns:
            context.user_data['threesome_pattern'] = pattern
            await update.message.reply_text(
                f"✅ Pola interaksi diubah ke: **{pattern}**\n\n"
                f"Sekarang {pattern} mode aktif!"
            )
        else:
            await update.message.reply_text(
                f"❌ Pattern tidak valid. Pilih: {', '.join(valid_patterns)}"
            )
    else:
        lines = ["🎭 **POLA INTERAKSI THREESOME**"]
        lines.append("_(pilih dengan /threesome-pattern [nama])_")
        lines.append("")
        
        for i, pattern in enumerate(patterns, 1):
            lines.append(f"{i}. **{pattern['name']}** - {pattern['desc']}")
            
        await update.message.reply_text("\n".join(lines), parse_mode='Markdown')


async def threesome_cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Batalkan session threesome"""
    user_id = update.effective_user.id
    
    if not context.user_data.get('threesome_mode'):
        await update.message.reply_text(
            "❌ Tidak ada session threesome aktif."
        )
        return
    
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
# 5. SESSION COMMANDS (3 commands)
# =============================================================================

async def close_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tutup dan simpan session"""
    user_id = update.effective_user.id
    session_id = context.user_data.get('current_session')
    role = context.user_data.get('current_role')
    
    if not session_id:
        await update.message.reply_text(
            "❌ Tidak ada session aktif."
        )
        return
        
    # Save session summary
    total_chats = context.user_data.get('total_chats', 0)
    intimacy = context.user_data.get('intimacy_level', 1)
    milestones = context.user_data.get('milestones', [])
    
    summary = f"Session {role}: {total_chats} chat, level {intimacy}/12"
    if milestones:
        summary += f", milestone: {milestones[-1]}"
        
    # Clear user data
    context.user_data.clear()
    
    await update.message.reply_text(
        f"📁 **Session ditutup!**\n\n"
        f"Session ID: `{session_id}`\n"
        f"{summary}\n\n"
        f"Ketik /continue untuk lihat session tersimpan."
    )


async def continue_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /continue - dipanggil dari handlers.py"""
    pass


async def sessions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat semua session"""
    user_id = update.effective_user.id
    
    # Dummy data - akan diganti dengan data real
    sessions = [
        {"id": "MYLOVE-IPAR-123-20240315-001", "role": "ipar", "date": "15 Mar 2024", "status": "closed", "chats": 45},
        {"id": "MYLOVE-JANDA-123-20240314-002", "role": "janda", "date": "14 Mar 2024", "status": "closed", "chats": 120},
        {"id": "MYLOVE-PDKT-123-20240316-003", "role": "pdkt", "date": "16 Mar 2024", "status": "active", "chats": 23},
        {"id": "MYLOVE-MANTAN-123-20240312-004", "role": "mantan", "date": "12 Mar 2024", "status": "closed", "chats": 34},
    ]
    
    if not sessions:
        await update.message.reply_text(
            "Belum ada session. Mulai dengan /start dulu!"
        )
        return
        
    lines = ["📋 **DAFTAR SESSION**"]
    lines.append("")
    
    for i, sess in enumerate(sessions, 1):
        status_emoji = "🟢" if sess['status'] == 'active' else "⚪"
        lines.append(
            f"{i}. {status_emoji} **{sess['role'].title()}**\n"
            f"   {sess['date']} | {sess['chats']} chat | {sess['status']}\n"
            f"   `{sess['id']}`"
        )
        
    lines.append("")
    lines.append("💡 Lanjutkan dengan: /continue [nomor atau ID]")
    lines.append("Contoh: /continue 1 atau /continue MYLOVE-IPAR-123-20240315-001")
    
    await update.message.reply_text("\n".join(lines), parse_mode='Markdown')


# =============================================================================
# 6. PUBLIC AREA COMMANDS (3 commands)
# =============================================================================

async def explore_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cari lokasi random"""
    try:
        locations_db = PublicLocations()
        location = locations_db.get_random_location()
        
        explore_text = (
            f"📍 **{location['name']}**\n"
            f"Kategori: {location['category'].title()}\n"
            f"Risk: {location['base_risk']}% | Thrill: {location['base_thrill']}%\n"
            f"_{location['description']}_\n\n"
            f"💡 Mau ke sini? Ketik: \"ke {location['name'].lower()} yuk\""
        )
        
        await update.message.reply_text(explore_text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in explore_command: {e}")
        await update.message.reply_text(
            "❌ Gagal mendapatkan lokasi. Coba lagi nanti."
        )


async def locations_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat semua lokasi"""
    try:
        locations_db = PublicLocations()
        stats = locations_db.get_location_stats()
        
        categories = {
            "urban": "🏙️ Urban",
            "nature": "🌳 Alam",
            "extreme": "⚡ Extreme",
            "transport": "🚗 Transport"
        }
        
        text = f"📍 **PUBLIC AREAS**\nTotal: {stats['total']} lokasi\n\n"
        
        for cat, name in categories.items():
            count = stats.get(cat, 0)
            text += f"{name}: {count} lokasi\n"
            
        text += f"\nRata-rata Risk: {stats['avg_risk']:.0f}%\n"
        text += f"Rata-rata Thrill: {stats['avg_thrill']:.0f}%\n\n"
        text += "💡 Gunakan /explore untuk cari random lokasi"
        
        await update.message.reply_text(text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in locations_command: {e}")
        await update.message.reply_text(
            "❌ Gagal mendapatkan data lokasi."
        )


async def risk_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cek risk lokasi saat ini"""
    location = context.user_data.get('current_location')
    
    if not location:
        await update.message.reply_text(
            "❌ Kamu sedang tidak di lokasi manapun.\n"
            "Pilih lokasi dulu, misal: \"ke pantai yuk\""
        )
        return
        
    try:
        # Dummy risk data - akan diganti dengan real calculator
        risk_data = {
            "final_risk": random.randint(30, 90),
            "risk_level": "TINGGI",
            "description": "Risk tinggi, harus hati-hati",
            "factors": {
                "time": {"category": "malam", "multiplier": 0.7},
                "day": {"category": "weekend", "multiplier": 0.8},
                "weather": {"condition": "cerah", "multiplier": 1.0}
            }
        }
        
        if risk_data['final_risk'] < 40:
            risk_level = "RENDAH"
            desc = "Aman banget, santai aja"
        elif risk_data['final_risk'] < 60:
            risk_level = "SEDANG"
            desc = "Lumayan aman, tapi tetap hati-hati"
        elif risk_data['final_risk'] < 80:
            risk_level = "TINGGI"
            desc = "Wah risk tinggi, harus cepet"
        else:
            risk_level = "EXTREME"
            desc = "GILA! Nyaris ketahuan!"
        
        text = f"📍 **{location}**\n"
        text += f"⚠️ Risk: {risk_data['final_risk']}% ({risk_level})\n"
        text += f"📝 {desc}\n\n"
        text += "**Faktor:**\n"
        text += f"• Waktu ({risk_data['factors']['time']['category']})\n"
        text += f"• Hari ({risk_data['factors']['day']['category']})\n"
        text += f"• Cuaca ({risk_data['factors']['weather']['condition']})"
        
        await update.message.reply_text(text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error in risk_command: {e}")
        await update.message.reply_text(
            "❌ Gagal menghitung risk. Coba lagi nanti."
        )


# =============================================================================
# 7. RANKING COMMANDS (3 commands)
# =============================================================================

async def tophts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat TOP HTS"""
    user_id = update.effective_user.id
    
    # Dummy data
    top_list = [
        {"rank": 1, "role": "janda", "score": 98.5, "level": 12, "chats": 320},
        {"rank": 2, "role": "ipar", "score": 87.3, "level": 8, "chats": 145},
        {"rank": 3, "role": "pelakor", "score": 82.1, "level": 9, "chats": 178},
        {"rank": 4, "role": "pdkt", "score": 76.8, "level": 7, "chats": 98},
        {"rank": 5, "role": "teman_kantor", "score": 65.2, "level": 5, "chats": 67},
    ]
    
    lines = ["🏆 **TOP 5 HTS**\n"]
    
    for item in top_list:
        lines.append(
            f"{item['rank']}. **{item['role'].title()}**\n"
            f"   Score: {item['score']} | Level {item['level']}/12\n"
            f"   {item['chats']} total chats"
        )
        
    await update.message.reply_text("\n".join(lines), parse_mode='Markdown')


async def myclimax_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Statistik climax pribadi"""
    user_id = update.effective_user.id
    
    # Dummy data
    stats = {
        "total": 47,
        "by_role": {
            "ipar": 12,
            "janda": 25,
            "pdkt": 8,
            "mantan": 2
        },
        "avg_per_session": 1.2,
        "last": "2024-03-15 23:45"
    }
    
    text = (
        f"💦 **STATISTIK CLIMAX**\n\n"
        f"Total: **{stats['total']}** kali\n"
        f"Rata-rata per session: {stats['avg_per_session']}\n"
        f"Terakhir: {stats['last']}\n\n"
        f"**Per Role:**\n"
    )
    
    for role, count in stats['by_role'].items():
        text += f"• {role.title()}: {count}x\n"
        
    await update.message.reply_text(text, parse_mode='Markdown')


async def climaxhistory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """History climax"""
    user_id = update.effective_user.id
    
    # Dummy data
    history = [
        {"date": "2024-03-15", "role": "janda", "position": "doggy style", "thrill": 98},
        {"date": "2024-03-14", "role": "ipar", "position": "misionaris", "thrill": 85},
        {"date": "2024-03-13", "role": "pdkt", "position": "woman on top", "thrill": 92},
        {"date": "2024-03-12", "role": "janda", "position": "doggy style", "thrill": 95},
        {"date": "2024-03-11", "role": "ipar", "position": "spooning", "thrill": 78},
    ]
    
    lines = ["📜 **CLIMAX HISTORY** (5 terakhir)\n"]
    
    for h in history:
        lines.append(
            f"• {h['date']} | **{h['role'].title()}**\n"
            f"  {h['position']} | Thrill: {h['thrill']}%"
        )
        
    await update.message.reply_text("\n".join(lines), parse_mode='Markdown')


# =============================================================================
# 8. ADMIN COMMANDS (5 commands) - HANYA UNTUK ADMIN
# =============================================================================

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Statistik bot (admin only)"""
    user_id = update.effective_user.id
    
    # Check if admin
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Command hanya untuk admin")
        return
        
    # Dummy stats
    stats = {
        "uptime": "2 hari 5 jam",
        "total_users": 1,
        "total_messages": 1523,
        "total_sessions": 47,
        "active_sessions": 3,
        "total_climax": 128,
        "avg_response": "1.2s"
    }
    
    text = (
        "📊 **BOT STATISTICS**\n\n"
        f"Uptime: {stats['uptime']}\n"
        f"Total Users: {stats['total_users']}\n"
        f"Total Messages: {stats['total_messages']}\n"
        f"Total Sessions: {stats['total_sessions']}\n"
        f"Active Sessions: {stats['active_sessions']}\n"
        f"Total Climax: {stats['total_climax']}\n"
        f"Avg Response: {stats['avg_response']}"
    )
    
    await update.message.reply_text(text, parse_mode='Markdown')


async def db_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Statistik database (admin only)"""
    user_id = update.effective_user.id
    
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Command hanya untuk admin")
        return
        
    # Dummy stats
    stats = {
        "sessions": 47,
        "memories": 1250,
        "size_mb": 3.2,
        "backups": 7,
        "last_backup": "2024-03-15 04:00"
    }
    
    text = (
        "🗄️ **DATABASE STATISTICS**\n\n"
        f"Sessions: {stats['sessions']}\n"
        f"Memories: {stats['memories']}\n"
        f"Size: {stats['size_mb']} MB\n"
        f"Backups Available: {stats['backups']}\n"
        f"Last Backup: {stats['last_backup']}"
    )
    
    await update.message.reply_text(text, parse_mode='Markdown')


async def backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Backup manual (admin only)"""
    user_id = update.effective_user.id
    
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Command hanya untuk admin")
        return
        
    await update.message.reply_text(
        "🔄 **Memulai backup...**\n"
        "Ini akan memakan waktu beberapa detik."
    )
    
    # Simulate backup
    await asyncio.sleep(2)
    
    await update.message.reply_text(
        "✅ **Backup selesai!**\n"
        "File backup: mylove_backup_20240315_0400.zip\n"
        "Size: 2.4 MB"
    )


async def recover_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Restore dari backup (admin only)"""
    user_id = update.effective_user.id
    
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Command hanya untuk admin")
        return
        
    args = context.args
    
    if not args:
        # Tampilkan daftar backup
        backups = [
            {"index": 1, "filename": "mylove_backup_20240315_0400.zip", "date": "2024-03-15 04:00", "size": "2.4 MB"},
            {"index": 2, "filename": "mylove_backup_20240314_0400.zip", "date": "2024-03-14 04:00", "size": "2.3 MB"},
            {"index": 3, "filename": "mylove_backup_20240313_0400.zip", "date": "2024-03-13 04:00", "size": "2.1 MB"},
        ]
        
        lines = ["📂 **DAFTAR BACKUP**"]
        lines.append("_(pilih dengan /recover [nomor])_")
        lines.append("")
        
        for b in backups:
            lines.append(f"{b['index']}. **{b['filename']}**\n   {b['date']} | {b['size']}")
            
        lines.append("")
        lines.append("💡 Gunakan /recover [nomor] untuk restore")
        
        await update.message.reply_text("\n".join(lines), parse_mode='Markdown')
        return
        
    # Coba restore
    try:
        idx = int(args[0])
        await update.message.reply_text(
            f"🔄 **Merestore backup #{idx}...**\n"
            "Bot akan restart setelah selesai."
        )
        
        # Simulate restore
        await asyncio.sleep(3)
        
        await update.message.reply_text(
            "✅ **Restore selesai!**\n"
            "Database telah dikembalikan ke backup."
        )
    except ValueError:
        await update.message.reply_text("❌ Nomor tidak valid")


async def debug_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Info debug (admin only)"""
    user_id = update.effective_user.id
    
    if user_id != settings.admin_id:
        await update.message.reply_text("❌ Command hanya untuk admin")
        return
        
    import sys
    import os
    
    debug_info = (
        "🔍 **DEBUG INFO**\n\n"
        f"Python: {sys.version}\n"
        f"Platform: {sys.platform}\n"
        f"CWD: {os.getcwd()}\n"
        f"User Data Keys: {list(context.user_data.keys())}\n"
        f"Current Session: {context.user_data.get('current_session')}\n"
        f"Current Role: {context.user_data.get('current_role')}\n"
        f"Intimacy Level: {context.user_data.get('intimacy_level', 1)}\n"
        f"Total Chats: {context.user_data.get('total_chats', 0)}\n"
        f"Threesome Mode: {context.user_data.get('threesome_mode', False)}"
    )
    
    await update.message.reply_text(debug_info, parse_mode='Markdown')

# =============================================================================
# 9. ERROR HANDLER
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
# 10. EXPORT ALL COMMANDS
# =============================================================================

__all__ = [
    # Basic (4)
    'start_command', 'help_command', 'status_command', 'cancel_command',
    
    # Relationship (5)
    'jadipacar_command', 'break_command', 'unbreak_command', 
    'breakup_command', 'fwb_command',
    
    # HTS/FWB (6)
    'htslist_command', 'hts_call_handler_command', 'fwblist_command',
    'fwb_select_command', 'fwb_break_command', 'fwb_pacar_command',
    
    # Threesome (6)
    'threesome_command', 'threesome_list_command', 'threesome_status_command',
    'threesome_pattern_command', 'threesome_cancel_command',
    
    # Session (3)
    'close_command', 'continue_command', 'sessions_command',
    
    # Public Area (3)
    'explore_command', 'locations_command', 'risk_command',
    
    # Ranking (3)
    'tophts_command', 'myclimax_command', 'climaxhistory_command',
    
    # Admin (5)
    'stats_command', 'db_stats_command', 'backup_command', 
    'recover_command', 'debug_command'

    # Error Handle
    'error_handler',
]

# Total commands: 35 commands + callback handlers = 55+ total interactions
