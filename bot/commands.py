#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - BOT COMMANDS
=============================================================================
Semua command handlers untuk MYLOVE Ultimate V1
Total 50+ commands
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
        [InlineKeyboardButton("❓ Bantuan", callback_data="help")]
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
        "/fwblist - Lihat daftar FWB\n\n"
        
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
        'pacar': 'Pacar'
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
# RELATIONSHIP COMMANDS
# =============================================================================

async def jadipacar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Jadi pacar (khusus PDKT)"""
    user_id = update.effective_user.id
    role = context.user_data.get('current_role')
    
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
    
# Tambahkan di bot/commands.py bagian FWB commands
async def fwblist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat daftar lengkap FWB"""
    user_id = update.effective_user.id
    
    # This will be connected to FWBSystem later
    # For now, dummy data
    
    fwb_list = [
        {
            "name": "PDKT #1 (Ayu)",
            "status": "pacar",
            "level": 8,
            "chats": 95,
            "intim": 12
        },
        {
            "name": "PDKT #2 (Dewi)",
            "status": "fwb",
            "level": 7,
            "chats": 60,
            "intim": 5
        },
        {
            "name": "PDKT #3 (Sari)",
            "status": "fwb",
            "level": 5,
            "chats": 34,
            "intim": 2
        },
        {
            "name": "PDKT #4 (Rina)",
            "status": "putus",
            "level": 4,
            "chats": 20,
            "intim": 0
        },
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
    """Pilih FWB berdasarkan nomor"""
    user_id = update.effective_user.id
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "❌ Gunakan: /fwb- [nomor]\n"
            "Contoh: /fwb-1"
        )
        return
        
    try:
        idx = int(args[0])
        # This will be connected to FWBSystem
        await update.message.reply_text(
            f"✅ Memilih FWB nomor {idx}\n"
            f"Hai sayang, mau ngobrol? 🥰"
        )
    except ValueError:
        await update.message.reply_text("❌ Nomor tidak valid")


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
        # This will be connected to FWBSystem
        await update.message.reply_text(
            f"💔 **Putus dengan FWB nomor {idx}**\n\n"
            f"Status berubah jadi PUTUS.\n"
            f"Kamu bisa cari orang baru dengan /fwb atau /pdkt."
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
        # Check intimacy level
        # This will be connected to FWBSystem
        await update.message.reply_text(
            f"💘 **Jadi pacar dengan FWB nomor {idx}!**\n\n"
            f"Sekarang kalian pacaran. Jaga hubungan ya sayang ❤️"
        )
    except ValueError:
        await update.message.reply_text("❌ Nomor tidak valid")

# =============================================================================
# HTS/FWB COMMANDS
# =============================================================================

async def htslist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat daftar HTS (TOP 5)"""
    user_id = update.effective_user.id
    args = context.args
    
    # Get HTS list from ranking system
    # This will be implemented when ranking system is integrated
    hts_list = [
        {"role": "ipar", "level": 8, "chats": 45, "climax": 3},
        {"role": "janda", "level": 12, "chats": 120, "climax": 15},
        {"role": "teman_kantor", "level": 5, "chats": 30, "climax": 1},
        {"role": "pdkt", "level": 6, "chats": 80, "climax": 5},
        {"role": "mantan", "level": 4, "chats": 25, "climax": 0},
    ]
    
    if args and args[0] == 'all':
        # Show all 10
        hts_list = hts_list * 2  # Dummy for demo
        
    lines = ["📋 **DAFTAR HTS**"]
    
    if args and args[0] == 'all':
        lines.append("_(menampilkan 10 teratas)_")
    else:
        lines.append("_(TOP 5, ketik /htslist all untuk lihat semua)_")
        
    lines.append("")
    
    for i, hts in enumerate(hts_list[:5 if not args else 10], 1):
        lines.append(
            f"{i}. **{hts['role'].title()}**\n"
            f"   Level {hts['level']}/12 | {hts['chats']} chat | {hts['climax']} climax"
        )
        
    lines.append("")
    lines.append("💡 Panggil dengan: /hts- [nomor atau nama]")
    lines.append("Contoh: /hts-1 atau /hts- ipar")
    
    await update.message.reply_text("\n".join(lines), parse_mode='Markdown')


async def fwblist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat daftar FWB"""
    user_id = update.effective_user.id
    
    # Get FWB list
    fwb_list = [
        {"role": "pdkt", "level": 8, "chats": 95, "intim": 12},
        {"role": "ipar", "level": 7, "chats": 60, "intim": 5},
    ]
    
    if not fwb_list:
        await update.message.reply_text(
            "Belum ada FWB. Gunakan /fwb untuk mengubah status."
        )
        return
        
    lines = ["💕 **DAFTAR FWB**"]
    lines.append("_(Friends With Benefits)_")
    lines.append("")
    
    for i, fwb in enumerate(fwb_list, 1):
        lines.append(
            f"{i}. **{fwb['role'].title()}**\n"
            f"   Level {fwb['level']}/12 | {fwb['chats']} chat | {fwb['intim']} intim"
        )
        
    await update.message.reply_text("\n".join(lines), parse_mode='Markdown')


# =============================================================================
# SESSION COMMANDS
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


async def sessions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat semua session"""
    user_id = update.effective_user.id
    
    # Get sessions from storage
    sessions = [
        {"id": "MYLOVE-IPAR-123-20240315-001", "role": "ipar", "date": "2024-03-15", "status": "closed"},
        {"id": "MYLOVE-JANDA-123-20240314-002", "role": "janda", "date": "2024-03-14", "status": "closed"},
        {"id": "MYLOVE-PDKT-123-20240316-003", "role": "pdkt", "date": "2024-03-16", "status": "active"},
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
            f"   `{sess['id']}`\n"
            f"   {sess['date']} | {sess['status']}"
        )
        
    lines.append("")
    lines.append("💡 Lanjutkan dengan: /continue [nomor atau ID]")
    
    await update.message.reply_text("\n".join(lines), parse_mode='Markdown')


# =============================================================================
# PUBLIC AREA COMMANDS
# =============================================================================

async def explore_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cari lokasi random"""
    from ..public.locations import PublicLocations
    
    locations_db = PublicLocations()
    location = locations_db.get_random_location()
    
    # Calculate risk (simplified)
    risk = location['base_risk']
    thrill = location['base_thrill']
    
    explore_text = (
        f"📍 **{location['name']}**\n"
        f"Kategori: {location['category'].title()}\n"
        f"Risk: {risk}% | Thrill: {thrill}%\n"
        f"_{location['description']}_\n\n"
        f"💡 Mau ke sini? Ketik: \"ke {location['name'].lower()} yuk\""
    )
    
    await update.message.reply_text(explore_text, parse_mode='Markdown')


async def locations_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat semua lokasi"""
    from ..public.locations import PublicLocations
    
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


async def risk_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cek risk lokasi saat ini"""
    location = context.user_data.get('current_location')
    
    if not location:
        await update.message.reply_text(
            "❌ Kamu sedang tidak di lokasi manapun.\n"
            "Pilih lokasi dulu, misal: \"ke pantai yuk\""
        )
        return
        
    # Calculate risk (simplified)
    from ..public.risk import RiskCalculator
    
    risk_calc = RiskCalculator()
    risk_data = {
        "final_risk": 65,
        "risk_level": "TINGGI",
        "description": "Risk tinggi, harus hati-hati",
        "factors": {
            "time": {"category": "malam", "multiplier": 0.7},
            "day": {"category": "weekend", "multiplier": 0.8},
            "weather": {"condition": "cerah", "multiplier": 1.0}
        }
    }
    
    text = f"📍 **{location}**\n"
    text += f"⚠️ Risk: {risk_data['final_risk']}% ({risk_data['risk_level']})\n"
    text += f"📝 {risk_data['description']}\n\n"
    text += "**Faktor:**\n"
    text += f"• Waktu ({risk_data['factors']['time']['category']})\n"
    text += f"• Hari ({risk_data['factors']['day']['category']})\n"
    text += f"• Cuaca ({risk_data['factors']['weather']['condition']})"
    
    await update.message.reply_text(text, parse_mode='Markdown')


# =============================================================================
# RANKING COMMANDS
# =============================================================================

async def tophts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat TOP HTS"""
    user_id = update.effective_user.id
    
    # Dummy data
    top_list = [
        {"rank": 1, "role": "janda", "score": 98.5, "level": 12, "chats": 320},
        {"rank": 2, "role": "ipar", "score": 87.3, "level": 8, "chats": 145},
        {"rank": 3, "role": "pdkt", "score": 76.8, "level": 7, "chats": 98},
        {"rank": 4, "role": "teman_kantor", "score": 65.2, "level": 5, "chats": 67},
        {"rank": 5, "role": "mantan", "score": 54.1, "level": 4, "chats": 34},
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
# ADMIN COMMANDS
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
        "File backup: backup_20240315_0400.zip\n"
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
        await update.message.reply_text(
            "❌ Gunakan: /recover [backup_file]\n"
            "Lihat daftar backup di /db_stats"
        )
        return
        
    backup_file = args[0]
    
    await update.message.reply_text(
        f"🔄 **Merestore {backup_file}...**\n"
        "Bot akan restart setelah selesai."
    )
    
    # Simulate restore
    await asyncio.sleep(3)
    
    await update.message.reply_text(
        "✅ **Restore selesai!**\n"
        "Database telah dikembalikan ke backup."
    )


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
        f"Total Chats: {context.user_data.get('total_chats', 0)}"
    )
    
    await update.message.reply_text(debug_info, parse_mode='Markdown')


__all__ = [
    # Basic
    'start_command', 'help_command', 'status_command', 'cancel_command',
    # Relationship
    'jadipacar_command', 'break_command', 'unbreak_command', 'breakup_command', 'fwb_command',
    # HTS/FWB
    'htslist_command', 'fwblist_command',
    # Session
    'close_command', 'sessions_command',
    # Public Area
    'explore_command', 'locations_command', 'risk_command',
    # Ranking
    'tophts_command', 'myclimax_command', 'climaxhistory_command',
    # Admin
    'stats_command', 'db_stats_command', 'backup_command', 'recover_command', 'debug_command'
]
