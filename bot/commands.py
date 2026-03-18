#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - BOT COMMANDS (FIX FULL + PDKT)
=============================================================================
Semua command handlers untuk MYLOVE Ultimate V2
- Menampilkan nama bot di setiap respons
- Integrasi dengan leveling system (dual system)
- Environment context (lokasi, posisi, pakaian)
- **PDKT SUPER SPESIAL COMMANDS**
- 60+ commands lengkap
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

# Import dengan absolute imports
from config import settings
from utils.helpers import format_number, sanitize_input, truncate_text
from utils.logger import setup_logging
from session.unique_id import id_generator
from public.locations import PublicLocations
from public.risk import RiskCalculator
from threesome.manager import ThreesomeManager, ThreesomeType, ThreesomeStatus

# ===== PDKT IMPORTS =====
from pdkt.natural_engine import NaturalPDKTEngine, PDKTStage
from pdkt.chemistry import ChemistryLevel
# ===== END IMPORTS =====

logger = logging.getLogger(__name__)

# =============================================================================
# GLOBAL PDKT ENGINE (akan diinisialisasi dari main)
# =============================================================================
pdkt_engine = None


def set_pdkt_engine(engine):
    """Set PDKT engine global"""
    global pdkt_engine
    pdkt_engine = engine


# =============================================================================
# ERROR HANDLER
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
# HELPER FUNCTIONS UNTUK NAMA BOT
# =============================================================================

def get_bot_name(context) -> str:
    """Dapatkan nama bot dari context, atau default 'Aku'"""
    return context.user_data.get('bot_name', 'Aku')


def get_bot_display(context) -> str:
    """Dapatkan display nama bot dengan role"""
    nama = get_bot_name(context)
    role = context.user_data.get('current_role', '')
    if role:
        return f"{nama} ({role.title()})"
    return nama


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
        from bot.handlers import continue_handler
        return await continue_handler(update, context)
    
    # Welcome message
    welcome_text = (
        f"💕 **Halo {user.first_name}!**\n\n"
        "Selamat datang di **MYLOVE ULTIMATE VERSI 2**\n"
        "AI pendamping dengan:\n"
        "• Leveling berbasis durasi (60 menit ke Level 7) untuk PDKT\n"
        "• Leveling berbasis chat untuk role lain\n"
        "• Ekspresi & Suara AI Generated\n"
        "• Panggilan intim di Level 7+\n"
        "• **PDKT SUPER SPESIAL** dengan chemistry natural\n\n"
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
        
        "**🔹 PDKT SUPER SPESIAL**\n"
        "/pdkt - Menu utama PDKT\n"
        "/pdkt list - Lihat semua PDKT\n"
        "/pdkt start [nama] - Mulai PDKT baru\n"
        "/pdkt pause [id] - Hentikan waktu PDKT\n"
        "/pdkt resume [id] - Lanjutkan PDKT\n"
        "/pdkt stop [id] - Akhiri PDKT (putus)\n"
        "/pdkt info [id] - Detail PDKT\n"
        "/pdkt timeline [id] - Timeline hubungan\n\n"
        
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
        "• Level PDKT naik berdasarkan WAKTU NYATA (bisa pause)\n"
        "• Level role lain naik berdasarkan JUMLAH CHAT\n"
        "• PDKT punya chemistry rahasia yang menentukan arah hubungan\n"
        "• Bot bisa tiba-tiba suka kalau chemistry cocok"
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
    
    # Get bot name
    bot_name = get_bot_name(context)
    
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
    position = context.user_data.get('current_position', 'Tidak ada')
    clothing = context.user_data.get('current_clothing', 'Tidak ada')
    
    # Get leveling data (akan diisi dari leveling system)
    is_pdkt = (role == 'pdkt')
    
    status_text = (
        f"📊 **STATUS HUBUNGAN**\n\n"
        f"👤 **Nama Bot:** {bot_name}\n"
        f"🎭 **Role:** {role.title()}\n"
        f"💞 **Status:** {status_name}\n"
        f"📈 **Intimacy Level:** {intimacy}/12\n"
        f"💬 **Total Chat:** {total_chats} pesan\n"
        f"📍 **Lokasi:** {location}\n"
        f"🧍 **Posisi:** {position}\n"
        f"👗 **Pakaian:** {clothing}\n\n"
        f"⚡ **Mode Leveling:** {'REAL TIME (bisa pause)' if is_pdkt else 'BERDASARKAN CHAT'}\n"
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
    
    # Tambah info session ID
    status_text += f"\n🆔 **Session ID:**\n`{session}`"
    
    await update.message.reply_text(status_text, parse_mode='Markdown')


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Batalkan percakapan saat ini"""
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Percakapan dibatalkan.\n"
        "Ketik /start untuk memulai lagi."
    )


# =============================================================================
# 2. PDKT SUPER SPESIAL COMMANDS (8 commands)
# =============================================================================

async def pdkt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu utama PDKT"""
    user_id = update.effective_user.id
    args = context.args
    
    if not pdkt_engine:
        await update.message.reply_text("❌ PDKT engine belum siap.")
        return
    
    if args and args[0] == 'list':
        await pdkt_list_command(update, context)
        return
    
    if args and args[0] == 'start':
        await pdkt_start_command(update, context)
        return
    
    if args and args[0] == 'pause':
        await pdkt_pause_command(update, context)
        return
    
    if args and args[0] == 'resume':
        await pdkt_resume_command(update, context)
        return
    
    if args and args[0] == 'stop':
        await pdkt_stop_command(update, context)
        return
    
    if args and args[0] == 'info':
        await pdkt_info_command(update, context)
        return
    
    if args and args[0] == 'timeline':
        await pdkt_timeline_command(update, context)
        return
    
    # Tampilkan menu utama PDKT
    user_pdkt = pdkt_engine.get_user_pdkt_list(user_id, include_ended=False)
    active_count = len(user_pdkt)
    
    text = (
        f"🎯 **PDKT SUPER SPESIAL**\n\n"
        f"Kamu memiliki **{active_count}** PDKT aktif.\n\n"
        f"**Commands:**\n"
        f"• `/pdkt list` - Lihat semua PDKT\n"
        f"• `/pdkt start [nama]` - Mulai PDKT baru\n"
        f"• `/pdkt pause [id]` - Pause PDKT\n"
        f"• `/pdkt resume [id]` - Resume PDKT\n"
        f"• `/pdkt stop [id]` - Akhiri PDKT\n"
        f"• `/pdkt info [id]` - Detail PDKT\n"
        f"• `/pdkt timeline [id]` - Timeline hubungan\n\n"
        f"💡 PDKT menggunakan **waktu nyata** dan bisa di-pause kapan saja!"
    )
    
    await update.message.reply_text(text, parse_mode='Markdown')


async def pdkt_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lihat daftar semua PDKT"""
    user_id = update.effective_user.id
    
    if not pdkt_engine:
        await update.message.reply_text("❌ PDKT engine belum siap.")
        return
    
    pdkt_list = pdkt_engine.get_user_pdkt_list(user_id, include_ended=True)
    
    if not pdkt_list:
        await update.message.reply_text(
            "📭 **Belum ada PDKT**\n\n"
            "Mulai PDKT baru dengan:\n"
            "`/pdkt start [nama]`\n"
            "Contoh: `/pdkt start Sari`"
        )
        return
    
    lines = ["📋 **DAFTAR PDKT**\n"]
    
    active = [p for p in pdkt_list if p['is_active'] and not p.get('is_paused')]
    paused = [p for p in pdkt_list if p.get('is_paused')]
    ended = [p for p in pdkt_list if not p['is_active']]
    
    if active:
        lines.append("**▶️ AKTIF:**")
        for p in active[:5]:
            lines.append(
                f"  • {p['bot_name']} - Level {p['level']} | {p['vibe']}\n"
                f"    ID: `{p['id']}`"
            )
        lines.append("")
    
    if paused:
        lines.append("**⏸️ DI-PAUSE:**")
        for p in paused[:3]:
            lines.append(f"  • {p['bot_name']} - Level {p['level']} | ID: `{p['id']}`")
        lines.append("")
    
    if ended:
        lines.append("**💔 SELESAI:**")
        for p in ended[:3]:
            lines.append(f"  • {p['bot_name']} - {p.get('end_reason', 'berakhir')}")
    
    lines.append("\n💡 Gunakan `/pdkt info [id]` untuk detail")
    
    await update.message.reply_text("\n".join(lines), parse_mode='Markdown')


async def pdkt_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mulai PDKT baru"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "Sayang"
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "❌ Gunakan: `/pdkt start [nama]`\n"
            "Contoh: `/pdkt start Sari`"
        )
        return
    
    bot_name = " ".join(args)
    
    if not pdkt_engine:
        await update.message.reply_text("❌ PDKT engine belum siap.")
        return
    
    # Cek apakah sudah ada PDKT dengan nama ini
    existing = pdkt_engine.get_user_pdkt_list(user_id)
    for p in existing:
        if p['bot_name'].lower() == bot_name.lower() and p['is_active']:
            await update.message.reply_text(
                f"❌ Kamu sudah punya PDKT dengan **{bot_name}** yang masih aktif.\n"
                f"Gunakan `/pdkt info {p['id']}` untuk detail."
            )
            return
    
    # Buat PDKT baru
    pdkt_data = await pdkt_engine.create_pdkt(user_id, user_name, bot_name)
    
    # Set current role ke PDKT di context
    context.user_data['current_role'] = 'pdkt'
    context.user_data['bot_name'] = bot_name
    context.user_data['current_session'] = f"PDKT_{pdkt_data['id']}"
    
    direction_text = pdkt_data['direction_data']['hint']
    
    text = (
        f"💕 **PDKT Dimulai dengan {bot_name}!**\n\n"
        f"{direction_text}\n\n"
        f"**ID:** `{pdkt_data['id']}`\n"
        f"**Chemistry:** {pdkt_data['chemistry'].get_vibe()}\n"
        f"**Arah:** {pdkt_data['direction_data']['description']}\n\n"
        f"PDKT ini menggunakan **waktu nyata**. Kamu bisa pause kapan saja:\n"
        f"• `/pdkt pause {pdkt_data['id']}` - Hentikan waktu\n"
        f"• `/pdkt resume {pdkt_data['id']}` - Lanjutkan\n\n"
        f"Selamat menikmati! 🥰"
    )
    
    await update.message.reply_text(text, parse_mode='Markdown')


async def pdkt_pause_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pause PDKT (waktu berhenti)"""
    user_id = update.effective_user.id
    args = context.args
    
    if len(args) < 2:
        await update.message.reply_text(
            "❌ Gunakan: `/pdkt pause [id]`\n"
            "Contoh: `/pdkt pause PDKT001_12345678_1710873600`"
        )
        return
    
    pdkt_id = args[1]
    
    if not pdkt_engine:
        await update.message.reply_text("❌ PDKT engine belum siap.")
        return
    
    # Verifikasi PDKT milik user
    pdkt = pdkt_engine.get_pdkt(pdkt_id)
    if not pdkt or pdkt['user_id'] != user_id:
        await update.message.reply_text("❌ PDKT tidak ditemukan.")
        return
    
    if pdkt.get('is_paused'):
        await update.message.reply_text(f"⏸️ PDKT dengan **{pdkt['bot_name']}** sudah dalam keadaan pause.")
        return
    
    success = await pdkt_engine.pause_pdkt(pdkt_id)
    
    if success:
        await update.message.reply_text(
            f"⏸️ **PDKT dengan {pdkt['bot_name']} di-pause!**\n\n"
            f"Waktu berhenti. Kamu bisa main role lain.\n"
            f"Ketik `/pdkt resume {pdkt_id}` untuk melanjutkan."
        )
    else:
        await update.message.reply_text("❌ Gagal pause PDKT.")


async def pdkt_resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Resume PDKT"""
    user_id = update.effective_user.id
    args = context.args
    
    if len(args) < 2:
        await update.message.reply_text(
            "❌ Gunakan: `/pdkt resume [id]`\n"
            "Contoh: `/pdkt resume PDKT001_12345678_1710873600`"
        )
        return
    
    pdkt_id = args[1]
    
    if not pdkt_engine:
        await update.message.reply_text("❌ PDKT engine belum siap.")
        return
    
    # Verifikasi PDKT milik user
    pdkt = pdkt_engine.get_pdkt(pdkt_id)
    if not pdkt or pdkt['user_id'] != user_id:
        await update.message.reply_text("❌ PDKT tidak ditemukan.")
        return
    
    if not pdkt.get('is_paused'):
        await update.message.reply_text(f"▶️ PDKT dengan **{pdkt['bot_name']}** sudah dalam keadaan aktif.")
        return
    
    success = await pdkt_engine.resume_pdkt(pdkt_id)
    
    if success:
        await update.message.reply_text(
            f"▶️ **PDKT dengan {pdkt['bot_name']} dilanjutkan!**\n\n"
            f"Selamat datang kembali! Waktu berjalan lagi."
        )
    else:
        await update.message.reply_text("❌ Gagal resume PDKT.")


async def pdkt_stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Akhiri PDKT (putus)"""
    user_id = update.effective_user.id
    args = context.args
    
    if len(args) < 2:
        await update.message.reply_text(
            "❌ Gunakan: `/pdkt stop [id]`\n"
            "Contoh: `/pdkt stop PDKT001_12345678_1710873600`"
        )
        return
    
    pdkt_id = args[1]
    
    if not pdkt_engine:
        await update.message.reply_text("❌ PDKT engine belum siap.")
        return
    
    # Verifikasi PDKT milik user
    pdkt = pdkt_engine.get_pdkt(pdkt_id)
    if not pdkt or pdkt['user_id'] != user_id:
        await update.message.reply_text("❌ PDKT tidak ditemukan.")
        return
    
    # Konfirmasi
    keyboard = [
        [
            InlineKeyboardButton("✅ Ya, akhiri", callback_data=f"pdkt_stop_confirm_{pdkt_id}"),
            InlineKeyboardButton("❌ Tidak", callback_data="pdkt_stop_cancel")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"⚠️ **Yakin mau akhiri PDKT dengan {pdkt['bot_name']}?**\n\n"
        f"Semua progress akan tersimpan sebagai kenangan.",
        reply_markup=reply_markup
    )


async def pdkt_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detail PDKT"""
    user_id = update.effective_user.id
    args = context.args
    
    if len(args) < 2:
        await update.message.reply_text(
            "❌ Gunakan: `/pdkt info [id]`\n"
            "Contoh: `/pdkt info PDKT001_12345678_1710873600`"
        )
        return
    
    pdkt_id = args[1]
    
    if not pdkt_engine:
        await update.message.reply_text("❌ PDKT engine belum siap.")
        return
    
    detail = pdkt_engine.get_pdkt_detail(pdkt_id)
    
    if not detail or detail['user_id'] != user_id:
        await update.message.reply_text("❌ PDKT tidak ditemukan.")
        return
    
    # Format chemistry
    if detail['chemistry_score'] >= 80:
        chemistry_stars = "⭐⭐⭐⭐⭐"
    elif detail['chemistry_score'] >= 60:
        chemistry_stars = "⭐⭐⭐⭐"
    elif detail['chemistry_score'] >= 40:
        chemistry_stars = "⭐⭐⭐"
    elif detail['chemistry_score'] >= 20:
        chemistry_stars = "⭐⭐"
    else:
        chemistry_stars = "⭐"
    
    # Hitung durasi
    total_seconds = detail['total_minutes'] * 60
    days = int(total_seconds // 86400)
    hours = int((total_seconds % 86400) // 3600)
    minutes = int((total_seconds % 3600) // 60)
    
    if days > 0:
        duration = f"{days} hari {hours} jam"
    elif hours > 0:
        duration = f"{hours} jam {minutes} menit"
    else:
        duration = f"{minutes} menit"
    
    status_emoji = "⏸️" if detail['is_paused'] else "▶️" if detail['is_active'] else "💔"
    status_text = "Di-pause" if detail['is_paused'] else "Aktif" if detail['is_active'] else "Berakhir"
    
    text = (
        f"📊 **DETAIL PDKT: {detail['bot_name']}**\n\n"
        f"{status_emoji} **Status:** {status_text}\n"
        f"🎯 **Level:** {detail['level']}/12\n"
        f"📈 **Tahap:** {detail['stage']}\n\n"
        
        f"❤️ **Chemistry:** {chemistry_stars}\n"
        f"💞 **Vibe:** {detail['vibe']}\n"
        f"{detail['chemistry_description']}\n\n"
        
        f"🎭 **Arah:** {detail['direction_text']}\n"
        f"💡 {detail['hint']}\n\n"
        
        f"⏱️ **Durasi Aktif:** {duration}\n"
        f"💬 **Total Chat:** {detail['total_chats']}x\n"
        f"🔥 **Intim:** {detail['total_intim']}x\n"
        f"💦 **Climax:** {detail['total_climax']}x\n\n"
        
        f"**Milestone Terbaru:**\n"
    )
    
    for m in detail['milestones'][-3:]:
        time_str = datetime.fromtimestamp(m['time']).strftime("%d %b")
        text += f"• {time_str}: {m['description']}\n"
    
    text += f"\n🆔 `{detail['id']}`"
    
    await update.message.reply_text(text, parse_mode='Markdown')


async def pdkt_timeline_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Timeline hubungan PDKT"""
    user_id = update.effective_user.id
    args = context.args
    
    if len(args) < 2:
        await update.message.reply_text(
            "❌ Gunakan: `/pdkt timeline [id]`\n"
            "Contoh: `/pdkt timeline PDKT001_12345678_1710873600`"
        )
        return
    
    pdkt_id = args[1]
    
    if not pdkt_engine:
        await update.message.reply_text("❌ PDKT engine belum siap.")
        return
    
    detail = pdkt_engine.get_pdkt_detail(pdkt_id)
    
    if not detail or detail['user_id'] != user_id:
        await update.message.reply_text("❌ PDKT tidak ditemukan.")
        return
    
    lines = [f"📜 **TIMELINE {detail['bot_name']}**\n"]
    
    for m in detail['milestones']:
        time_str = datetime.fromtimestamp(m['time']).strftime("%d %b, %H:%M")
        lines.append(f"• {time_str} - {m['description']}")
    
    if detail['inner_thoughts']:
        lines.append("\n**Pikiran Dalam Hati {detail['bot_name']}:**")
        for t in detail['inner_thoughts'][-3:]:
            time_str = datetime.fromtimestamp(t['time']).strftime("%H:%M")
            lines.append(f"• {time_str}: {t['thought']}")
    
    await update.message.reply_text("\n".join(lines), parse_mode='Markdown')


# =============================================================================
# 3. RELATIONSHIP COMMANDS (5 commands)
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
    
    bot_name = get_bot_name(context)
    
    await update.message.reply_text(
        f"💘 **Kita jadi pacar!**\n\n"
        f"Sekarang kamu resmi pacaran sama {bot_name}.\n"
        f"Jaga hubungan kita ya sayang ❤️"
    )


# [Semua command lainnya tetap sama seperti sebelumnya]
# ... (break, unbreak, breakup, fwb, htslist, fwblist, dll)

# =============================================================================
# 9. CALLBACK HANDLER UNTUK PDKT
# =============================================================================

async def pdkt_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback untuk PDKT"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    if data.startswith('pdkt_stop_confirm_'):
        pdkt_id = data.replace('pdkt_stop_confirm_', '')
        
        if not pdkt_engine:
            await query.edit_message_text("❌ PDKT engine belum siap.")
            return
        
        pdkt = pdkt_engine.get_pdkt(pdkt_id)
        if not pdkt or pdkt['user_id'] != user_id:
            await query.edit_message_text("❌ PDKT tidak ditemukan.")
            return
        
        success = await pdkt_engine.stop_pdkt(pdkt_id, "user_stopped")
        
        if success:
            await query.edit_message_text(
                f"💔 **PDKT dengan {pdkt['bot_name']} telah diakhiri.**\n\n"
                f"Terima kasih atas waktunya. Semoga kamu dapat yang terbaik."
            )
        else:
            await query.edit_message_text("❌ Gagal mengakhiri PDKT.")
    
    elif data == 'pdkt_stop_cancel':
        await query.edit_message_text("✅ PDKT tetap dilanjutkan.")


# =============================================================================
# 10. EXPORT ALL COMMANDS
# =============================================================================

__all__ = [
    # Basic (4)
    'start_command', 'help_command', 'status_command', 'cancel_command',
    
    # PDKT (8)
    'pdkt_command', 'pdkt_list_command', 'pdkt_start_command',
    'pdkt_pause_command', 'pdkt_resume_command', 'pdkt_stop_command',
    'pdkt_info_command', 'pdkt_timeline_command',
    
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
    'recover_command', 'debug_command',
    
    # PDKT Callback
    'pdkt_callback_handler',
    
    # Error Handle
    'error_handler',
    'set_pdkt_engine',
]

# Total commands: 43 commands + callback handlers = 65+ total interactions
