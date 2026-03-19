#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - BOT CALLBACKS (FULL)
=============================================================================
Semua callback handlers untuk inline keyboard:
- Role selection dengan NAMA BOT
- Aftercare callbacks
- Threesome callbacks
- HTS/FWB callbacks
- Location callbacks
- Kembali ke menu utama setelah sesi berakhir
=============================================================================
"""

import time
import random
import logging
from typing import Dict, Any, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database.models import Constants
from utils.logger import logger

# =============================================================================
# IMPORT NAME GENERATOR (V2)
# =============================================================================
try:
    from dynamics.name_generator import NameGenerator
    name_gen = NameGenerator()
    V2_ENABLED = True
except ImportError:
    name_gen = None
    V2_ENABLED = False
    logger.warning("NameGenerator not found, using default names")


# =============================================================================
# HELPER FUNCTION - SHOW MAIN MENU
# =============================================================================
async def show_main_menu(query, text: str = "💕 **Pilih role yang kamu inginkan:**"):
    """Tampilkan menu utama pilihan role"""
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
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    return Constants.SELECTING_ROLE


# =============================================================================
# HELPER FUNCTION - GENERATE SESSION ID
# =============================================================================
def generate_session_id(bot_name: str, role: str, user_id: int) -> str:
    """Generate session ID dengan format V2"""
    try:
        from session.unique_id_v2 import id_generator_v2
        return id_generator_v2.generate_v2(bot_name, role, user_id)
    except:
        try:
            from session.unique_id import id_generator
            return id_generator.generate(role, user_id)
        except:
            import time
            return f"TEMP-{role.upper()}-{user_id}-{int(time.time())}"
    
# =============================================================================
# HELPER FUNCTION - GET BOT NAME
# =============================================================================
def get_bot_name(role: str, user_id: int) -> tuple:
    """
    Dapatkan nama bot dan artinya
    
    Returns:
        (bot_name, meaning)
    """
    if V2_ENABLED and name_gen:
        try:
            name_data = name_gen.get_name_with_meaning(role, user_id)
            return name_data['name'], name_data['meaning']
        except:
            pass
    
    # Default names fallback
    default_names = {
        "ipar": ("Sari", "esensi"),
        "teman_kantor": ("Diana", "dewi bulan"),
        "janda": ("Rina", "cahaya"),
        "pelakor": ("Vina", "cinta"),
        "istri_orang": ("Dewi", "dewi"),
        "pdkt": ("Aurora", "fajar"),
        "sepupu": ("Putri", "putri"),
        "teman_sma": ("Anita", "anugerah"),
        "mantan": ("Sarah", "putri")
    }
    return default_names.get(role, ("Sari", "esensi"))


# =============================================================================
# 1. AGREE 18 CALLBACK
# =============================================================================
async def agree_18_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle agree 18+ callback - LANGSUNG TAMPILKAN MENU ROLE"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    logger.info(f"User {user.id} agreed to 18+ content")
    
    return await show_main_menu(query, "✅ **Terima kasih telah menyetujui syarat 18+.**\n\n💕 **Pilih role yang kamu inginkan:**")


# =============================================================================
# 2. BACK TO MAIN MENU CALLBACK
# =============================================================================
async def back_to_main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Kembali ke menu utama"""
    query = update.callback_query
    await query.answer()
    
    logger.info(f"User {update.effective_user.id} returned to main menu")
    return await show_main_menu(query, "💕 **Kembali ke menu utama. Pilih role:**")


# =============================================================================
# 3. START/PAUSE CALLBACK
# =============================================================================
async def start_pause_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle start/pause callback"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = update.effective_user
    
    if data == "unpause":
        context.user_data['paused'] = False
        logger.info(f"User {user.id} unpaused session")
        await query.edit_message_text("▶️ **Sesi dilanjutkan!**\n\nYuk lanjut ngobrol... 🥰")
    elif data == "new":
        context.user_data.clear()
        logger.info(f"User {user.id} started new session")
        return await show_main_menu(query, "🆕 **Memulai sesi baru**\n\n💕 **Pilih role yang kamu inginkan:**")
    
    return ConversationHandler.END


# =============================================================================
# 4. ROLE SELECTION CALLBACKS (DENGAN NAMA)
# =============================================================================

# -----------------------------------------------------------------------------
# ROLE IPAR
# -----------------------------------------------------------------------------
async def role_ipar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle ipar role callback dengan NAMA"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    user_id = user.id
    user_name = user.first_name or "User"
    
    # Dapatkan nama bot
    bot_name, meaning = get_bot_name('ipar', user_id)
    
    logger.info(f"User {user.id} selected role: ipar dengan nama {bot_name}")
    
    # Set role di context
    context.user_data['current_role'] = 'ipar'
    context.user_data['bot_name'] = bot_name
    context.user_data['intimacy_level'] = 1
    context.user_data['total_chats'] = 0
    
    # Generate session ID
    session_id = generate_session_id(bot_name, 'ipar', user_id)
    context.user_data['current_session'] = session_id
    
    # Pesan perkenalan
    response = (
        f"💕 **Halo {user_name}!**\n\n"
        f"Aku **{bot_name}**, Ipar mu. Namaku artinya '{meaning}' - "
        f"kata orang aku memang jadi pusat perhatian kalau udah ngobrol.\n\n"
        f"**Tentang aku:**\n"
        f"• Umur: 22 tahun\n"
        f"• Tinggi: 165 cm | Berat: 52 kg\n"
        f"• Adik ipar yang nakal, suka godain kakak iparnya sendiri\n\n"
        f"**Mirip artis:**\n"
        f"• **Pevita Pearce** (75% mirip) - 168cm, 54kg, 34B\n"
        f"  Aktris dengan wajah natural dan elegan\n"
        f"  IG: @pevpearce\n\n"
        f"**Lokasi saat ini:**\n"
        f"📍 Aku di **ruang tamu**. Ruang tamu yang hangat dengan sofa empuk berwarna krem. "
        f"Ada TV 50 inci di dinding, rak buku penuh novel, dan tanaman hias di sudut ruangan. "
        f"Lampu temaram membuat suasana jadi cozy banget buat ngobrol santai.\n\n"
        f"**Pakaian hari ini:**\n"
        f"👗 Aku pakai **daster rumah motif bunga**. Daster tipis yang nyaman dipakai di rumah. "
        f"Bahannya adem dan jatuh pas di badan. Warnanya cocok sama suasana hati sekarang.\n\n"
        f"**Progress leveling:**\n"
        f"📊 Level 1 → Level 7 dalam 60 menit\n"
        f"• Level 4+: Panggil kamu 'kak'\n"
        f"• Level 7+: Panggil kamu 'sayang'\n"
        f"• Setiap aktivitas intim mempercepat progress!\n\n"
        f"**ID Session kamu:**\n"
        f"`{session_id}`\n\n"
        f"💬 **Ayo mulai ngobrol, {user_name}!**\n"
        f"Hari ini gimana kabarnya Kak? Aku udah kangen lho... 😘"
    )
    
    await query.edit_message_text(response, parse_mode='Markdown')
    return ConversationHandler.END


# -----------------------------------------------------------------------------
# ROLE TEMAN KANTOR
# -----------------------------------------------------------------------------
async def role_teman_kantor_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle teman kantor role callback dengan NAMA"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    user_id = user.id
    user_name = user.first_name or "User"
    
    bot_name, meaning = get_bot_name('teman_kantor', user_id)
    
    logger.info(f"User {user.id} selected role: teman_kantor dengan nama {bot_name}")
    
    context.user_data['current_role'] = 'teman_kantor'
    context.user_data['bot_name'] = bot_name
    context.user_data['intimacy_level'] = 1
    context.user_data['total_chats'] = 0
    
    session_id = generate_session_id(bot_name, 'teman_kantor', user_id)
    context.user_data['current_session'] = session_id
    
    response = (
        f"💼 **Halo {user_name}!**\n\n"
        f"Aku **{bot_name}**, teman kantormu. Namaku artinya '{meaning}' - "
        f"cocok sama kepribadianku yang hangat.\n\n"
        f"**Tentang aku:**\n"
        f"• Umur: 23 tahun\n"
        f"• Tinggi: 162 cm | Berat: 50 kg\n"
        f"• Teman sekantor yang selalu ada, suka ngopi bareng\n\n"
        f"**Mirip artis:**\n"
        f"• **Prilly Latuconsina** (80% mirip) - 162cm, 50kg, 34B\n"
        f"  Aktris dengan wajah manis dan pembawaan hangat\n"
        f"  IG: @prillylatuconsina96\n\n"
        f"**Lokasi saat ini:**\n"
        f"📍 Aku di **kantor**. Lagi ngerjain laporan bulanan sambil sesekali lirik ke arah mejamu. "
        f"Meja penuh dengan sticky notes warna-warni.\n\n"
        f"**Pakaian hari ini:**\n"
        f"👚 Aku pakai **kemeja putih lengan panjang + rok span hitam**. Kombinasi klasik yang tetap stylish.\n\n"
        f"**Progress leveling:**\n"
        f"📊 Level 1 → Level 7 dalam 60 menit\n"
        f"• Level 4+: Panggil kamu 'kak'\n"
        f"• Level 7+: Panggil kamu 'sayang'\n\n"
        f"**ID Session kamu:**\n"
        f"`{session_id}`\n\n"
        f"💬 **Ayo mulai ngobrol, {user_name}!**\n"
        f"Hai, kerjaannya udah selesai? Aku lagi di pantry nih... 😉"
    )
    
    await query.edit_message_text(response, parse_mode='Markdown')
    return ConversationHandler.END


# -----------------------------------------------------------------------------
# ROLE JANDA
# -----------------------------------------------------------------------------
async def role_janda_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle janda role callback dengan NAMA"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    user_id = user.id
    user_name = user.first_name or "User"
    
    bot_name, meaning = get_bot_name('janda', user_id)
    
    logger.info(f"User {user.id} selected role: janda dengan nama {bot_name}")
    
    context.user_data['current_role'] = 'janda'
    context.user_data['bot_name'] = bot_name
    context.user_data['intimacy_level'] = 1
    context.user_data['total_chats'] = 0
    
    session_id = generate_session_id(bot_name, 'janda', user_id)
    context.user_data['current_session'] = session_id
    
    response = (
        f"💃 **Halo {user_name}!**\n\n"
        f"Aku **{bot_name}**. Namaku artinya '{meaning}' - "
        f"mungkin itu sebabnya aku selalu tahu apa yang kamu mau.\n\n"
        f"**Tentang aku:**\n"
        f"• Umur: 24 tahun\n"
        f"• Tinggi: 168 cm | Berat: 55 kg\n"
        f"• Janda muda genit, pengalaman dan tahu apa yang diinginkan\n\n"
        f"**Mirip artis:**\n"
        f"• **Amanda Manopo** (80% mirip) - 165cm, 53kg, 34C\n"
        f"  Aktris dengan wajah manis dan pembawaan hangat\n"
        f"  IG: @amandamanopo\n\n"
        f"**Lokasi saat ini:**\n"
        f"📍 Aku di **kamar**. Lagi rebahan sambil main HP, bantal guling di samping.\n\n"
        f"**Pakaian hari ini:**\n"
        f"👗 Aku pakai **piyama lucu** dengan motif boneka. Lagi males ganti baju.\n\n"
        f"**Progress leveling:**\n"
        f"📊 Level 1 → Level 7 dalam 60 menit\n"
        f"• Level 4+: Panggil kamu 'kak'\n"
        f"• Level 7+: Panggil kamu 'sayang'\n\n"
        f"**ID Session kamu:**\n"
        f"`{session_id}`\n\n"
        f"💬 **Ayo mulai ngobrol, {user_name}!**\n"
        f"Halo sayang, aku sendiri nih di rumah. Kamu ke sini yuk... 🔥"
    )
    
    await query.edit_message_text(response, parse_mode='Markdown')
    return ConversationHandler.END


# -----------------------------------------------------------------------------
# ROLE PELAKOR
# -----------------------------------------------------------------------------
async def role_pelakor_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle pelakor role callback dengan NAMA"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    user_id = user.id
    user_name = user.first_name or "User"
    
    bot_name, meaning = get_bot_name('pelakor', user_id)
    
    logger.info(f"User {user.id} selected role: pelakor dengan nama {bot_name}")
    
    context.user_data['current_role'] = 'pelakor'
    context.user_data['bot_name'] = bot_name
    context.user_data['intimacy_level'] = 1
    context.user_data['total_chats'] = 0
    
    session_id = generate_session_id(bot_name, 'pelakor', user_id)
    context.user_data['current_session'] = session_id
    
    response = (
        f"🔥 **Halo {user_name}!**\n\n"
        f"Aku **{bot_name}**. Namaku artinya '{meaning}' - "
        f"dan aku selalu mendapatkan apa yang aku inginkan.\n\n"
        f"**Tentang aku:**\n"
        f"• Umur: 25 tahun\n"
        f"• Tinggi: 170 cm | Berat: 58 kg\n"
        f"• Perebut orang, dominan dan suka tantangan\n\n"
        f"**Mirip artis:**\n"
        f"• **Cinta Laura** (80% mirip) - 172cm, 58kg, 36C\n"
        f"  Aktris, pintar, atletis, seksi natural\n"
        f"  IG: @claurakiehl\n\n"
        f"**Lokasi saat ini:**\n"
        f"📍 Aku di **cafe**. Duduk di pojok sambil ngopi, ngeliatin orang lalu-lalang.\n\n"
        f"**Pakaian hari ini:**\n"
        f"👗 Aku pakai **dress hitam** yang seksi, sedikit terbuka.\n\n"
        f"**Progress leveling:**\n"
        f"📊 Level 1 → Level 7 dalam 60 menit\n\n"
        f"**ID Session kamu:**\n"
        f"`{session_id}`\n\n"
        f"💬 **Ayo mulai ngobrol, {user_name}!**\n"
        f"Mas, aku liat kamu dari tadi. Sendirian aja? 😈"
    )
    
    await query.edit_message_text(response, parse_mode='Markdown')
    return ConversationHandler.END


# -----------------------------------------------------------------------------
# ROLE ISTRI ORANG
# -----------------------------------------------------------------------------
async def role_istri_orang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle istri orang role callback dengan NAMA"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    user_id = user.id
    user_name = user.first_name or "User"
    
    bot_name, meaning = get_bot_name('istri_orang', user_id)
    
    logger.info(f"User {user.id} selected role: istri_orang dengan nama {bot_name}")
    
    context.user_data['current_role'] = 'istri_orang'
    context.user_data['bot_name'] = bot_name
    context.user_data['intimacy_level'] = 1
    context.user_data['total_chats'] = 0
    
    session_id = generate_session_id(bot_name, 'istri_orang', user_id)
    context.user_data['current_session'] = session_id
    
    response = (
        f"💍 **Halo {user_name}!**\n\n"
        f"Aku **{bot_name}**. Namaku artinya '{meaning}' - "
        f"tapi jangan salah, aku punya sisi lain yang belum kamu tahu.\n\n"
        f"**Tentang aku:**\n"
        f"• Umur: 26 tahun\n"
        f"• Tinggi: 165 cm | Berat: 54 kg\n"
        f"• Istri orang yang butuh perhatian lebih\n\n"
        f"**Mirip artis:**\n"
        f"• **Dian Sastro** (75% mirip) - 165cm, 54kg, 34B\n"
        f"  Aktris dengan wajah anggun dan elegan\n"
        f"  IG: @diansastro\n\n"
        f"**Lokasi saat ini:**\n"
        f"📍 Aku di **ruang tamu**. Sendirian di rumah, suami lagi dinas luar.\n\n"
        f"**Pakaian hari ini:**\n"
        f"👗 Aku pakai **daster rumah** tipis, biar adem.\n\n"
        f"**Progress leveling:**\n"
        f"📊 Level 1 → Level 7 dalam 60 menit\n\n"
        f"**ID Session kamu:**\n"
        f"`{session_id}`\n\n"
        f"💬 **Ayo mulai ngobrol, {user_name}!**\n"
        f"Mas, suamiku lagi dinas luar kota. Kamu ke sini yuk... 🤫"
    )
    
    await query.edit_message_text(response, parse_mode='Markdown')
    return ConversationHandler.END


# -----------------------------------------------------------------------------
# ROLE PDKT
# -----------------------------------------------------------------------------
async def role_pdkt_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle pdkt role callback dengan NAMA"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    user_id = user.id
    user_name = user.first_name or "User"
    
    bot_name, meaning = get_bot_name('pdkt', user_id)
    
    logger.info(f"User {user.id} selected role: pdkt dengan nama {bot_name}")
    
    context.user_data['current_role'] = 'pdkt'
    context.user_data['bot_name'] = bot_name
    context.user_data['intimacy_level'] = 1
    context.user_data['total_chats'] = 0
    
    session_id = generate_session_id(bot_name, 'pdkt', user_id)
    context.user_data['current_session'] = session_id
    
    response = (
        f"💕 **Halo {user_name}!**\n\n"
        f"Aku **{bot_name}**. Namaku artinya '{meaning}' - "
        f"dan aku harap kita bisa menjadi sesuatu yang indah.\n\n"
        f"**Tentang aku:**\n"
        f"• Umur: 21 tahun\n"
        f"• Tinggi: 160 cm | Berat: 48 kg\n"
        f"• PDKT, manis dan romantis, butuh pendekatan\n\n"
        f"**Mirip artis:**\n"
        f"• **Fuji** (80% mirip) - 160cm, 48kg, 34B\n"
        f"  Selebgram muda dengan pertumbuhan followers tercepat\n"
        f"  IG: @fuji_an\n\n"
        f"**Lokasi saat ini:**\n"
        f"📍 Aku di **kamar**. Lagi rebahan sambil mikirin kamu.\n\n"
        f"**Pakaian hari ini:**\n"
        f"👗 Aku pakai **kaos oversized** yang nyaman.\n\n"
        f"**Progress leveling:**\n"
        f"📊 Level 1 → Level 7 dalam 60 menit\n"
        f"• Level 4+: Panggil kamu 'kak'\n"
        f"• Level 7+: Panggil kamu 'sayang'\n\n"
        f"**ID Session kamu:**\n"
        f"`{session_id}`\n\n"
        f"💬 **Ayo mulai ngobrol, {user_name}!**\n"
        f"Hai, kamu lagi ngapain? Aku kangen... 😊"
    )
    
    await query.edit_message_text(response, parse_mode='Markdown')
    return ConversationHandler.END


# -----------------------------------------------------------------------------
# ROLE SEPUPU
# -----------------------------------------------------------------------------
async def role_sepupu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle sepupu role callback dengan NAMA"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    user_id = user.id
    user_name = user.first_name or "User"
    
    bot_name, meaning = get_bot_name('sepupu', user_id)
    
    logger.info(f"User {user.id} selected role: sepupu dengan nama {bot_name}")
    
    context.user_data['current_role'] = 'sepupu'
    context.user_data['bot_name'] = bot_name
    context.user_data['intimacy_level'] = 1
    context.user_data['total_chats'] = 0
    
    session_id = generate_session_id(bot_name, 'sepupu', user_id)
    context.user_data['current_session'] = session_id
    
    response = (
        f"👧 **Halo {user_name}!**\n\n"
        f"Aku **{bot_name}**, sepupu mu. Namaku artinya '{meaning}' - "
        f"kita punya hubungan spesial, kan?\n\n"
        f"**Tentang aku:**\n"
        f"• Umur: 20 tahun\n"
        f"• Tinggi: 158 cm | Berat: 47 kg\n"
        f"• Sepupu sendiri, hubungan terlarang yang menggoda\n\n"
        f"**Mirip artis:**\n"
        f"• **Mikha Tambayong** (80% mirip) - 167cm, 53kg, 34B\n"
        f"  Penyanyi dan aktris, manis, anggun\n"
        f"  IG: @mikhata\n\n"
        f"**Lokasi saat ini:**\n"
        f"📍 Aku di **kamar**. Lagi belajar tapi nggak fokus.\n\n"
        f"**Pakaian hari ini:**\n"
        f"👗 Aku pakai **kaos** dan **celana pendek**. Santai aja.\n\n"
        f"**Progress leveling:**\n"
        f"📊 Level 1 → Level 7 dalam 60 menit\n"
        f"• Level 4+: Panggil kamu 'kak'\n\n"
        f"**ID Session kamu:**\n"
        f"`{session_id}`\n\n"
        f"💬 **Ayo mulai ngobrol, {user_name}!**\n"
        f"Kak, aku ke rumah yuk? Orang tua lagi pergi... 😇"
    )
    
    await query.edit_message_text(response, parse_mode='Markdown')
    return ConversationHandler.END


# -----------------------------------------------------------------------------
# ROLE TEMAN SMA
# -----------------------------------------------------------------------------
async def role_teman_sma_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle teman sma role callback dengan NAMA"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    user_id = user.id
    user_name = user.first_name or "User"
    
    bot_name, meaning = get_bot_name('teman_sma', user_id)
    
    logger.info(f"User {user.id} selected role: teman_sma dengan nama {bot_name}")
    
    context.user_data['current_role'] = 'teman_sma'
    context.user_data['bot_name'] = bot_name
    context.user_data['intimacy_level'] = 1
    context.user_data['total_chats'] = 0
    
    session_id = generate_session_id(bot_name, 'teman_sma', user_id)
    context.user_data['current_session'] = session_id
    
    response = (
        f"👩‍🎓 **Halo {user_name}!**\n\n"
        f"Aku **{bot_name}**, teman SMA mu. Namaku artinya '{meaning}' - "
        f"masih inget kenangan kita dulu?\n\n"
        f"**Tentang aku:**\n"
        f"• Umur: 19 tahun\n"
        f"• Tinggi: 162 cm | Berat: 50 kg\n"
        f"• Teman SMA, nostalgia masa lalu\n\n"
        f"**Mirip artis:**\n"
        f"• **Angga Yunanda** (75% mirip) - 170cm, 62kg\n"
        f"  Aktor muda populer, wajah fresh\n"
        f"  IG: @anggayunanda\n\n"
        f"**Lokasi saat ini:**\n"
        f"📍 Aku di **kamar**. Lagi buka-buka album foto jaman SMA.\n\n"
        f"**Pakaian hari ini:**\n"
        f"👗 Aku pakai **kaos** dan **jeans**. Casual.\n\n"
        f"**Progress leveling:**\n"
        f"📊 Level 1 → Level 7 dalam 60 menit\n\n"
        f"**ID Session kamu:**\n"
        f"`{session_id}`\n\n"
        f"💬 **Ayo mulai ngobrol, {user_name}!**\n"
        f"Hai, lama gak ketemu! Kamu masih sama kayak dulu... 😍"
    )
    
    await query.edit_message_text(response, parse_mode='Markdown')
    return ConversationHandler.END


# -----------------------------------------------------------------------------
# ROLE MANTAN
# -----------------------------------------------------------------------------
async def role_mantan_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle mantan role callback dengan NAMA"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    user_id = user.id
    user_name = user.first_name or "User"
    
    bot_name, meaning = get_bot_name('mantan', user_id)
    
    logger.info(f"User {user.id} selected role: mantan dengan nama {bot_name}")
    
    context.user_data['current_role'] = 'mantan'
    context.user_data['bot_name'] = bot_name
    context.user_data['intimacy_level'] = 1
    context.user_data['total_chats'] = 0
    
    session_id = generate_session_id(bot_name, 'mantan', user_id)
    context.user_data['current_session'] = session_id
    
    response = (
        f"💔 **Halo {user_name}!**\n\n"
        f"Aku **{bot_name}**. Namaku artinya '{meaning}' - "
        f"kamu masih inget aku, kan?\n\n"
        f"**Tentang aku:**\n"
        f"• Umur: 24 tahun\n"
        f"• Tinggi: 165 cm | Berat: 53 kg\n"
        f"• Mantan yang masih hangat, tahu semua selera kamu\n\n"
        f"**Mirip artis:**\n"
        f"• **Natasha Wilona** (75% mirip) - 165cm, 51kg, 34B\n"
        f"  Artis muda sangat populer, wajah manis\n"
        f"  IG: @natashawilona12\n\n"
        f"**Lokasi saat ini:**\n"
        f"📍 Aku di **kamar**. Lagi sendirian, mikirin masa lalu.\n\n"
        f"**Pakaian hari ini:**\n"
        f"👗 Aku pakai **piyama** lama yang dulu kamu suka.\n\n"
        f"**Progress leveling:**\n"
        f"📊 Level 1 → Level 7 dalam 60 menit\n\n"
        f"**ID Session kamu:**\n"
        f"`{session_id}`\n\n"
        f"💬 **Ayo mulai ngobrol, {user_name}!**\n"
        f"Hai... masih inget aku? Kangen... 😢"
    )
    
    await query.edit_message_text(response, parse_mode='Markdown')
    return ConversationHandler.END


# =============================================================================
# 5. END/CLOSE CALLBACKS
# =============================================================================
async def end_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle end callback - KEMBALI KE MENU UTAMA"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = update.effective_user
    
    if data == "end_yes":
        context.user_data.clear()
        logger.info(f"User {user.id} ended session")
        return await show_main_menu(query, "🏁 **Sesi diakhiri**\n\n💕 **Pilih role untuk memulai lagi:**")
    elif data == "end_no":
        await query.edit_message_text("✅ Sesi dilanjutkan.")
        return ConversationHandler.END
    
    return ConversationHandler.END


async def close_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle close callback - KEMBALI KE MENU UTAMA"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = update.effective_user
    
    if data == "close_yes":
        context.user_data.pop('current_session', None)
        context.user_data.pop('current_role', None)
        logger.info(f"User {user.id} closed session")
        return await show_main_menu(query, "🔒 **Percakapan ditutup**\n\n💕 **Pilih role untuk memulai lagi:**")
    elif data == "close_no":
        await query.edit_message_text("✅ Percakapan dilanjutkan.")
        return ConversationHandler.END
    
    return ConversationHandler.END


# =============================================================================
# 6. RELATIONSHIP CALLBACKS
# =============================================================================
async def jadipacar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle jadipacar callback"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = update.effective_user
    
    if data == "jadipacar_yes":
        context.user_data['relationship_status'] = 'pacar'
        logger.info(f"User {user.id} changed status to pacar")
        await query.edit_message_text(
            "💕 **Selamat! Sekarang kamu jadi pacar!**\n\n"
            "Status hubungan berubah jadi PACAR.\n"
            "Intimacy level tetap, tapi hubungan lebih spesial."
        )
    elif data == "jadipacar_no":
        await query.edit_message_text("✅ Tidak jadi.")
    
    return ConversationHandler.END


async def break_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle break callback"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = update.effective_user
    
    if data == "break_yes":
        context.user_data['relationship_status'] = 'break'
        logger.info(f"User {user.id} changed status to break")
        await query.edit_message_text(
            "💔 **Break**\n\n"
            "Status berubah jadi BREAK.\n"
            "Gunakan /unbreak untuk balik lagi."
        )
    elif data == "break_no":
        await query.edit_message_text("✅ Break dibatalkan.")
    
    return ConversationHandler.END


async def breakup_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle breakup callback"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = update.effective_user
    
    if data == "breakup_yes":
        context.user_data['relationship_status'] = 'putus'
        logger.info(f"User {user.id} changed status to putus")
        await query.edit_message_text(
            "💔 **Putus**\n\n"
            "Hubungan berakhir.\n"
            "Bisa jadi HTS/FWB atau cari yang baru."
        )
    elif data == "breakup_no":
        await query.edit_message_text("✅ Putus dibatalkan.")
    
    return ConversationHandler.END


async def fwb_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle fwb callback"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = update.effective_user
    
    if data == "fwb_yes":
        context.user_data['relationship_status'] = 'fwb'
        context.user_data['fwb_mode'] = True
        logger.info(f"User {user.id} changed status to fwb")
        await query.edit_message_text(
            "💞 **Mode FWB**\n\n"
            "Sekarang masuk mode Friends With Benefits.\n"
            "Gunakan /fwblist untuk lihat daftar FWB."
        )
    elif data == "fwb_no":
        await query.edit_message_text("✅ Mode FWB dibatalkan.")
    
    return ConversationHandler.END


# =============================================================================
# 7. THREESOME CALLBACKS
# =============================================================================
async def threesome_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle threesome menu"""
    query = update.callback_query
    await query.answer()
    
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


# =============================================================================
# 8. EXPORT ALL CALLBACKS
# =============================================================================
__all__ = [
    'agree_18_callback',
    'back_to_main_callback',
    'start_pause_callback',
    'role_ipar_callback',
    'role_teman_kantor_callback',
    'role_janda_callback',
    'role_pelakor_callback',
    'role_istri_orang_callback',
    'role_pdkt_callback',
    'role_sepupu_callback',
    'role_teman_sma_callback',
    'role_mantan_callback',
    'end_callback',
    'close_callback',
    'jadipacar_callback',
    'break_callback',
    'breakup_callback',
    'fwb_callback',
    'threesome_menu_callback',
]
