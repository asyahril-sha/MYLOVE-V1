#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - BOT CALLBACKS (FIXED)
=============================================================================
Semua callback handlers untuk inline keyboard:
- Role selection callbacks
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
# 1. AGREE 18 CALLBACK
# =============================================================================

async def agree_18_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle agree 18+ callback - LANGSUNG TAMPILKAN MENU ROLE"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    logger.info(f"User {user.id} agreed to 18+ content")
    
    # Tampilkan menu pilihan role langsung
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
        # Reset session
        context.user_data.clear()
        logger.info(f"User {user.id} started new session")
        # Tampilkan menu utama
        return await show_main_menu(query, "🆕 **Memulai sesi baru**\n\n💕 **Pilih role yang kamu inginkan:**")
    
    return ConversationHandler.END


# =============================================================================
# 4. ROLE SELECTION CALLBACKS
# =============================================================================

async def role_ipar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle ipar role callback"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    logger.info(f"User {user.id} selected role: ipar")
    
    # Set role di context
    context.user_data['current_role'] = 'ipar'
    context.user_data['intimacy_level'] = 1
    context.user_data['total_chats'] = 0
    context.user_data['current_session'] = f"MYLOVE-IPAR-{user.id}-{int(time.time())}-001"
    
    role_info = get_role_info('ipar')
    
    response = (
        f"💕 **Kamu memilih role: Ipar**\n\n"
        f"{role_info['description']}\n\n"
        f"**Ciri-ciri Ipar:**\n"
        f"• Umur: {role_info['age']} tahun\n"
        f"• Tinggi: {role_info['height']} cm\n"
        f"• Berat: {role_info['weight']} kg\n"
        f"• Dada: {role_info['chest']}\n\n"
        f"**Mirip artis:**\n"
        f"Pevita Pearce (75% mirip)\n\n"
        f"💬 **Mulai chat:**\n"
        f"Halo kak, aku lagi di rumah nih. Kapan main? 😘"
    )
    
    await query.edit_message_text(response, parse_mode='Markdown')
    return ConversationHandler.END


async def role_teman_kantor_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle teman kantor role callback"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    logger.info(f"User {user.id} selected role: teman_kantor")
    
    context.user_data['current_role'] = 'teman_kantor'
    context.user_data['intimacy_level'] = 1
    context.user_data['total_chats'] = 0
    context.user_data['current_session'] = f"MYLOVE-KANTOR-{user.id}-{int(time.time())}-001"
    
    role_info = get_role_info('teman_kantor')
    
    response = (
        f"💼 **Kamu memilih role: Teman Kantor**\n\n"
        f"{role_info['description']}\n\n"
        f"**Ciri-ciri Teman Kantor:**\n"
        f"• Umur: {role_info['age']} tahun\n"
        f"• Tinggi: {role_info['height']} cm\n"
        f"• Berat: {role_info['weight']} kg\n"
        f"• Dada: {role_info['chest']}\n\n"
        f"**Mirip artis:**\n"
        f"Prilly Latuconsina (80% mirip)\n\n"
        f"💬 **Mulai chat:**\n"
        f"Hai, kerjaannya udah selesai? Aku lagi di pantry nih... 😉"
    )
    
    await query.edit_message_text(response, parse_mode='Markdown')
    return ConversationHandler.END


async def role_janda_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle janda role callback"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    logger.info(f"User {user.id} selected role: janda")
    
    context.user_data['current_role'] = 'janda'
    context.user_data['intimacy_level'] = 1
    context.user_data['total_chats'] = 0
    context.user_data['current_session'] = f"MYLOVE-JANDA-{user.id}-{int(time.time())}-001"
    
    role_info = get_role_info('janda')
    
    response = (
        f"💃 **Kamu memilih role: Janda**\n\n"
        f"{role_info['description']}\n\n"
        f"**Ciri-ciri Janda:**\n"
        f"• Umur: {role_info['age']} tahun\n"
        f"• Tinggi: {role_info['height']} cm\n"
        f"• Berat: {role_info['weight']} kg\n"
        f"• Dada: {role_info['chest']}\n\n"
        f"**Mirip artis:**\n"
        f"Chelsea Islan (85% mirip)\n\n"
        f"💬 **Mulai chat:**\n"
        f"Halo sayang, aku sendiri nih di rumah. Kamu ke sini yuk... 🔥"
    )
    
    await query.edit_message_text(response, parse_mode='Markdown')
    return ConversationHandler.END


async def role_pelakor_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle pelakor role callback"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    logger.info(f"User {user.id} selected role: pelakor")
    
    context.user_data['current_role'] = 'pelakor'
    context.user_data['intimacy_level'] = 1
    context.user_data['total_chats'] = 0
    context.user_data['current_session'] = f"MYLOVE-PELAKOR-{user.id}-{int(time.time())}-001"
    
    role_info = get_role_info('pelakor')
    
    response = (
        f"🔥 **Kamu memilih role: Pelakor**\n\n"
        f"{role_info['description']}\n\n"
        f"**Ciri-ciri Pelakor:**\n"
        f"• Umur: {role_info['age']} tahun\n"
        f"• Tinggi: {role_info['height']} cm\n"
        f"• Berat: {role_info['weight']} kg\n"
        f"• Dada: {role_info['chest']}\n\n"
        f"**Mirip artis:**\n"
        f"Tara Basro (75% mirip)\n\n"
        f"💬 **Mulai chat:**\n"
        f"Mas, aku liat kamu dari tadi. Sendirian aja? 😈"
    )
    
    await query.edit_message_text(response, parse_mode='Markdown')
    return ConversationHandler.END


async def role_istri_orang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle istri orang role callback"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    logger.info(f"User {user.id} selected role: istri_orang")
    
    context.user_data['current_role'] = 'istri_orang'
    context.user_data['intimacy_level'] = 1
    context.user_data['total_chats'] = 0
    context.user_data['current_session'] = f"MYLOVE-ISTRI-{user.id}-{int(time.time())}-001"
    
    role_info = get_role_info('istri_orang')
    
    response = (
        f"💍 **Kamu memilih role: Istri Orang**\n\n"
        f"{role_info['description']}\n\n"
        f"**Ciri-ciri Istri Orang:**\n"
        f"• Umur: {role_info['age']} tahun\n"
        f"• Tinggi: {role_info['height']} cm\n"
        f"• Berat: {role_info['weight']} kg\n"
        f"• Dada: {role_info['chest']}\n\n"
        f"**Mirip artis:**\n"
        f"Dian Sastro (70% mirip)\n\n"
        f"💬 **Mulai chat:**\n"
        f"Mas, suamiku lagi dinas luar kota. Kamu ke sini yuk... 🤫"
    )
    
    await query.edit_message_text(response, parse_mode='Markdown')
    return ConversationHandler.END


async def role_pdkt_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle pdkt role callback"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    logger.info(f"User {user.id} selected role: pdkt")
    
    context.user_data['current_role'] = 'pdkt'
    context.user_data['intimacy_level'] = 1
    context.user_data['total_chats'] = 0
    context.user_data['current_session'] = f"MYLOVE-PDKT-{user.id}-{int(time.time())}-001"
    
    role_info = get_role_info('pdkt')
    
    response = (
        f"💕 **Kamu memilih role: PDKT**\n\n"
        f"{role_info['description']}\n\n"
        f"**Ciri-ciri PDKT:**\n"
        f"• Umur: {role_info['age']} tahun\n"
        f"• Tinggi: {role_info['height']} cm\n"
        f"• Berat: {role_info['weight']} kg\n"
        f"• Dada: {role_info['chest']}\n\n"
        f"**Mirip artis:**\n"
        f"Amanda Manopo (80% mirip)\n\n"
        f"💬 **Mulai chat:**\n"
        f"Hai, kamu lagi ngapain? Aku kangen... 😊"
    )
    
    await query.edit_message_text(response, parse_mode='Markdown')
    return ConversationHandler.END


async def role_sepupu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle sepupu role callback"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    logger.info(f"User {user.id} selected role: sepupu")
    
    context.user_data['current_role'] = 'sepupu'
    context.user_data['intimacy_level'] = 1
    context.user_data['total_chats'] = 0
    context.user_data['current_session'] = f"MYLOVE-SEPUPU-{user.id}-{int(time.time())}-001"
    
    role_info = get_role_info('sepupu')
    
    response = (
        f"👧 **Kamu memilih role: Sepupu**\n\n"
        f"{role_info['description']}\n\n"
        f"**Ciri-ciri Sepupu:**\n"
        f"• Umur: {role_info['age']} tahun\n"
        f"• Tinggi: {role_info['height']} cm\n"
        f"• Berat: {role_info['weight']} kg\n"
        f"• Dada: {role_info['chest']}\n\n"
        f"**Mirip artis:**\n"
        f"Syifa Hadju (85% mirip)\n\n"
        f"💬 **Mulai chat:**\n"
        f"Kak, aku ke rumah yuk? Orang tua lagi pergi... 😇"
    )
    
    await query.edit_message_text(response, parse_mode='Markdown')
    return ConversationHandler.END


async def role_teman_sma_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle teman sma role callback"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    logger.info(f"User {user.id} selected role: teman_sma")
    
    context.user_data['current_role'] = 'teman_sma'
    context.user_data['intimacy_level'] = 1
    context.user_data['total_chats'] = 0
    context.user_data['current_session'] = f"MYLOVE-SMA-{user.id}-{int(time.time())}-001"
    
    role_info = get_role_info('teman_sma')
    
    response = (
        f"👩‍🎓 **Kamu memilih role: Teman SMA**\n\n"
        f"{role_info['description']}\n\n"
        f"**Ciri-ciri Teman SMA:**\n"
        f"• Umur: {role_info['age']} tahun\n"
        f"• Tinggi: {role_info['height']} cm\n"
        f"• Berat: {role_info['weight']} kg\n"
        f"• Dada: {role_info['chest']}\n\n"
        f"**Mirip artis:**\n"
        f"Iqbaal Ramadhan (70% mirip)\n\n"
        f"💬 **Mulai chat:**\n"
        f"Hai, lama gak ketemu! Kamu masih sama kayak dulu... 😍"
    )
    
    await query.edit_message_text(response, parse_mode='Markdown')
    return ConversationHandler.END


async def role_mantan_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle mantan role callback"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    logger.info(f"User {user.id} selected role: mantan")
    
    context.user_data['current_role'] = 'mantan'
    context.user_data['intimacy_level'] = 1
    context.user_data['total_chats'] = 0
    context.user_data['current_session'] = f"MYLOVE-MANTAN-{user.id}-{int(time.time())}-001"
    
    role_info = get_role_info('mantan')
    
    response = (
        f"💔 **Kamu memilih role: Mantan**\n\n"
        f"{role_info['description']}\n\n"
        f"**Ciri-ciri Mantan:**\n"
        f"• Umur: {role_info['age']} tahun\n"
        f"• Tinggi: {role_info['height']} cm\n"
        f"• Berat: {role_info['weight']} kg\n"
        f"• Dada: {role_info['chest']}\n\n"
        f"**Mirip artis:**\n"
        f"Nicholas Saputra (75% mirip)\n\n"
        f"💬 **Mulai chat:**\n"
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
        # Clear all user data
        context.user_data.clear()
        logger.info(f"User {user.id} ended session")
        
        # Tampilkan menu utama
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
        # Close current session but keep user data
        context.user_data.pop('current_session', None)
        context.user_data.pop('current_role', None)
        logger.info(f"User {user.id} closed session")
        
        # Tampilkan menu utama
        return await show_main_menu(query, "🔒 **Percakapan ditutup**\n\n💕 **Pilih role untuk memulai lagi:**")
    elif data == "close_no":
        await query.edit_message_text("✅ Percakapan dilanjutkan.")
        return ConversationHandler.END
    
    return ConversationHandler.END


# =============================================================================
# 6. RELATIONSHIP CALLBACKS (JADIPACAR, BREAK, BREAKUP, FWB)
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
# 7. HELPER FUNCTIONS
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
        "teman_kantor": {
            "name": "Teman Kantor",
            "description": "Rekan kerja yang mesra, umur 23 tahun",
            "age": "23",
            "height": "162",
            "weight": "50",
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
]
