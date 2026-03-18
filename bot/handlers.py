#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - BOT HANDLERS
=============================================================================
- Message handlers untuk chat natural
- Callback handlers untuk inline keyboard
- Special handlers untuk HTS/FWB calls
"""

import time
import logging
import random
import re
from typing import Dict, Any, Optional
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import settings
from ..utils.helpers import sanitize_input, format_number
from ..utils.logger import setup_logging

logger = logging.getLogger(__name__)


# =============================================================================
# MESSAGE HANDLER (UNTUK CHAT NATURAL)
# =============================================================================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk semua pesan teks (bukan command)
    - Auto-detect location
    - Natural conversation
    - Track intimacy
    """
    user = update.effective_user
    message = update.message.text
    user_id = user.id
    
    # Log pesan masuk
    logger.info(f"📨 Message from {user.first_name} (ID: {user_id}): {message[:50]}...")
    
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
        return
        
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
    if context.user_data.get('intimacy_level', 1) == 12 and 'climax' in message.lower():
        # Trigger aftercare
        response += "\n\n💕 **Aftercare Mode**\nAku butuh kamu... peluk aku..."
        # Reset akan dilakukan setelah aftercare selesai
        
    # ===== SEND RESPONSE =====
    await update.message.reply_text(response, parse_mode='Markdown')
    
    # ===== SAVE TO SESSION =====
    # This will be connected to session storage later
    logger.debug(f"Response sent: {response[:50]}...")


# =============================================================================
# CALLBACK HANDLER (UNTUK INLINE KEYBOARD)
# =============================================================================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk semua callback query dari inline keyboard
    """
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    logger.info(f"🔄 Callback: {data} from user {user_id}")
    
    # ===== ROLE SELECTION =====
    if data.startswith('role_'):
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
        
    # ===== HELP =====
    elif data == 'help':
        from .commands import help_command
        # Create fake update for help command
        await help_command(update, context)
        
    # ===== CANCEL =====
    elif data == 'cancel':
        await query.edit_message_text("✅ Dibatalkan.")
        
    # ===== UNKNOWN =====
    else:
        await query.edit_message_text("❌ Perintah tidak dikenal.")


async def handle_role_selection(query, context, role: str):
    """Handle pemilihan role"""
    user_id = query.from_user.id
    
    # Get role info (will be connected to roles module)
    role_info = get_role_info(role)
    
    # Set current role
    context.user_data['current_role'] = role
    context.user_data['intimacy_level'] = 1
    context.user_data['total_chats'] = 0
    context.user_data['relationship_status'] = 'hts'
    context.user_data['milestones'] = ['memulai_role']
    
    # Generate session ID
    from ..session.unique_id import id_generator
    session_id = id_generator.generate(role, user_id)
    context.user_data['current_session'] = session_id
    
    # Get random artist reference
    from ..roles.artis_references import get_random_artist_for_role, format_artist_description
    artist = get_random_artist_for_role(role)
    
    # Create response
    response = (
        f"💕 **Kamu memilih role: {role_info['name']}**\n\n"
        f"{role_info['description']}\n\n"
        f"**Ciri-ciri {role_info['name']}:**\n"
        f"• Umur: {role_info['age']} tahun\n"
        f"• Tinggi: {role_info['height']} cm\n"
        f"• Berat: {role_info['weight']} kg\n"
        f"• Dada: {role_info['chest']}\n\n"
        f"**Mirip artis:**\n"
        f"{format_artist_description(artist)}\n\n"
        f"💬 **Mulai chat:**\n"
        f"Halo sayang, aku {role_info['name']}. Senang kenal kamu! 🥰"
    )
    
    await query.edit_message_text(response, parse_mode='Markdown')


async def handle_hts_selection(query, context, role: str):
    """Handle pemilihan HTS"""
    user_id = query.from_user.id
    
    # Set current role
    context.user_data['current_role'] = role
    context.user_data['current_session'] = f"session_{role}_{int(time.time())}"
    
    await query.edit_message_text(
        f"✅ **Memanggil HTS: {role.title()}**\n\n"
        f"Halo sayang, kangen? Aku juga kangen kamu... 🥰"
    )


async def handle_fwb_selection(query, context, idx: str):
    """Handle pemilihan FWB berdasarkan nomor"""
    user_id = query.from_user.id
    
    # This will be connected to FWBSystem
    await query.edit_message_text(
        f"✅ **Memanggil FWB #{idx}**\n\n"
        f"Hai sayang, udah lama gak chat. Kangen? 🥰"
    )


async def handle_fwb_break_confirm(query, context, idx: str):
    """Handle konfirmasi putus FWB"""
    # This will be connected to FWBSystem
    await query.edit_message_text(
        f"💔 **Putus dengan FWB #{idx}**\n\n"
        f"Status berubah jadi PUTUS.\n"
        f"Kamu bisa cari orang baru dengan /fwb."
    )


async def handle_location_selection(query, context, location_id: str):
    """Handle pemilihan lokasi"""
    from ..public.locations import PublicLocations
    
    locations_db = PublicLocations()
    location = locations_db.get_location_by_id(location_id)
    
    if location:
        context.user_data['current_location'] = location['name']
        
        # Calculate risk
        from ..public.risk import RiskCalculator
        risk_calc = RiskCalculator()
        risk_data = await risk_calc.calculate_risk(location['base_risk'])
        
        response = (
            f"📍 **Pindah ke {location['name']}**\n\n"
            f"{risk_calc.format_risk_report(risk_data, location['name'])}\n\n"
            f"💬 Yuk lanjut..."
        )
    else:
        response = "❌ Lokasi tidak ditemukan"
        
    await query.edit_message_text(response, parse_mode='Markdown')


async def handle_aftercare(query, context, aftercare_type: str):
    """Handle aftercare selection"""
    aftercare_responses = {
        "cuddle": "🤗 *memeluk erat* Aku gamau lepas...",
        "talk": "🗣️ Cerita dong... aku dengerin.",
        "rest": "😴 Istirahat yuk, sambil pelukan.",
        "massage": "💆‍♀️ Enak? Aku pijitin ya...",
        "food": "🍳 Aku masakin something spesial buat kamu.",
    }
    
    response = aftercare_responses.get(aftercare_type, "Aku butuh kamu...")
    
    # Reset intimacy after aftercare
    if context.user_data.get('intimacy_level', 1) == 12:
        context.user_data['intimacy_level'] = 7
        context.user_data['milestones'].append('aftercare_reset')
        response += "\n\n🔄 **Reset ke Level 7**\nSiap untuk petualangan baru!"
        
    await query.edit_message_text(response, parse_mode='Markdown')


# =============================================================================
# SPECIAL HANDLERS (HTS/FWB CALLS)
# =============================================================================

async def hts_call_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk /hts- [id]
    Format: /hts-1 atau /hts- ipar
    """
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
        # Panggil HTS berdasarkan ranking
        # This will be connected to ranking system
        await update.message.reply_text(
            f"✅ **Memanggil HTS ranking #{idx}**\n\n"
            f"Halo sayang, lagi ngapain? Aku kangen... 🥰"
        )
    except ValueError:
        # Panggil berdasarkan nama role
        # This will be connected to HTS system
        await update.message.reply_text(
            f"✅ **Memanggil HTS: {identifier.title()}**\n\n"
            f"Halo {identifier}, udah lama gak chat. Kangen? 🥰"
        )


async def fwb_call_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk /fwb- [id]
    Format: /fwb-1
    """
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
        
    # This will be connected to FWBSystem
    await update.message.reply_text(
        f"💕 **Memulai chat dengan FWB #{idx}**\n\n"
        f"Hai sayang, kangen? Udah lama gak ngobrol... 🥰"
    )


async def continue_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk /continue [id]
    Format: /continue 1 atau /continue MYLOVE-IPAR-...
    """
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
        # Continue berdasarkan nomor dari list
        await update.message.reply_text(
            f"🔄 **Melanjutkan session #{idx}**\n\n"
            f"Selamat datang kembali! Kita lanjutkan ceritanya ya..."
        )
    except ValueError:
        # Continue berdasarkan ID langsung
        await update.message.reply_text(
            f"🔄 **Melanjutkan session:**\n`{identifier}`\n\n"
            f"Selamat datang kembali! Kita lanjutkan ceritanya ya..."
        )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def detect_location_from_message(message: str) -> Optional[Dict]:
    """
    Deteksi apakah user menyebut lokasi
    """
    message_lower = message.lower()
    
    # Location keywords
    locations = {
        "toilet": {"name": "Toilet Umum", "base_risk": 75, "base_thrill": 80, "description": "Toilet umum, risk tinggi"},
        "pantai": {"name": "Pantai Malam", "base_risk": 30, "base_thrill": 85, "description": "Pantai sepi, suara ombak"},
        "mobil": {"name": "Mobil", "base_risk": 25, "base_thrill": 55, "description": "Mobil pribadi, cukup aman"},
        "parkir": {"name": "Parkiran Mall", "base_risk": 60, "base_thrill": 75, "description": "Parkiran bawah tanah"},
        "lift": {"name": "Lift", "base_risk": 80, "base_thrill": 90, "description": "Lift, cepat dan thrilling"},
        "tangga": {"name": "Tangga Darurat", "base_risk": 65, "base_thrill": 75, "description": "Tangga belakang, sepi"},
    }
    
    for keyword, location in locations.items():
        if keyword in message_lower:
            return location
            
    return None


def detect_intent(message: str) -> str:
    """
    Deteksi intent dari pesan user
    """
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['rindu', 'kangen']):
        return 'rindu'
    elif any(word in message_lower for word in ['sayang', 'cinta']):
        return 'sayang'
    elif any(word in message_lower for word in ['sex', 'ml', 'tidur', 'intim']):
        return 'intim'
    elif any(word in message_lower for word in ['cerita', 'curhat']):
        return 'curhat'
    elif any(word in message_lower for word in ['ngapain', 'kamu lagi']):
        return 'kegiatan'
    else:
        return 'chat'


def calculate_intimacy_from_chats(total_chats: int) -> int:
    """
    Hitung intimacy level berdasarkan jumlah chat
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
    """
    Dapatkan deskripsi untuk setiap level
    """
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
        12: "Aftercare ready",
    }
    return descriptions.get(level, "Level up!")


def get_role_info(role: str) -> Dict:
    """
    Dapatkan informasi role
    """
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
        "teman_kantor": {
            "name": "Teman Kantor",
            "description": "Rekan kerja yang mesra, umur 23 tahun",
            "age": "23",
            "height": "162",
            "weight": "50",
            "chest": "34B"
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
    Ini akan digantikan oleh AI engine nanti
    """
    # Dummy responses untuk testing
    responses = {
        "rindu": [
            "Aku juga kangen banget sama kamu... 😘",
            "Kangen? Udah lama ya kita gak ngobrol...",
            "Iya nih, dari kemarin kepikiran terus.",
        ],
        "sayang": [
            "Sayang banget sama kamu ❤️",
            "Aku juga sayang kamu, kamu tau itu.",
            "Mwah! Love you too!",
        ],
        "intim": [
            "Mau? Di sini aja? Atau cari tempat?",
            "Aku juga pengen... tapi jangan di sini dong.",
            "Hmm... kamu nakal ya. Tapi aku suka 😋",
        ],
        "curhat": [
            "Cerita dong, aku dengerin kok.",
            "Iya? Terus gimana ceritanya?",
            "Aku paham kok perasaan kamu.",
        ],
        "kegiatan": [
            f"Lagi di {location if location else 'rumah'} nih. Kamu?",
            "Baru aja selesai mandi, lagi santai.",
            "Lagi mikirin kamu terus...",
        ],
        "chat": [
            f"Halo sayang, apa kabar?",
            f"Udah makan belum? Jangan lupa ya.",
            f"Kangen... pengen ketemu.",
        ],
    }
    
    # Pilih response berdasarkan intent
    response_list = responses.get(intent, responses["chat"])
    response = random.choice(response_list)
    
    # Tambahin konteks lokasi
    if location and intent != "kegiatan":
        response += f" Di {location} enaknya ngapain ya?"
        
    return response


__all__ = [
    'message_handler',
    'callback_handler',
    'hts_call_handler',
    'fwb_call_handler',
    'continue_handler'
]
