#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - BOT HANDLERS (ENHANCED)
=============================================================================
- Command handlers dengan nama bot permanent
- Message handler dengan environment dinamis (lokasi, posisi, pakaian)
- Leveling berbasis durasi (60 menit ke level 7)
- Response minimal 500 karakter
- Integrasi dengan LocationSystem, PositionSystem, ClothingSystem
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

# ===== TAMBAHAN MYLOVE V2 =====
from session.unique_id import id_generator
from roles import get_random_name, get_random_name_with_hint, format_name_for_display
from roles.artis_references import get_random_artist_for_role, format_artist_description
from dynamics.location import LocationSystem, LocationType
from dynamics.position import PositionSystem, PositionType
from dynamics.clothing import ClothingSystem, ClothingStyle
from leveling.time_based import TimeBasedLeveling, ActivityType
from leveling.progress_tracker import ProgressTracker
from public.locations import PublicLocations
from public.risk import RiskCalculator
# ===== END TAMBAHAN =====


# =============================================================================
# 1. COMMAND HANDLERS (UNTUK APPLICATION.PY)
# =============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /start command - memulai bot dan memilih role"""
    user = update.effective_user
    logger.info(f"User {user.id} (@{user.username}) started the bot")
    
    # ===== TAMBAHAN MYLOVE V2 =====
    # Cek apakah user sudah pernah memiliki session sebelumnya
    if 'current_session' in context.user_data:
        await update.message.reply_text(
            "⚠️ Kamu masih memiliki sesi aktif.\n"
            "Gunakan /status untuk melihat status.\n"
            "Gunakan /close untuk menutup sesi."
        )
        return Constants.ACTIVE_SESSION
    # ===== END TAMBAHAN =====
    
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
        "/memory_stats - Statistik memori\n"
        "/reload - Reload config"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


# =============================================================================
# 2. ROLE SELECTION HANDLER (DENGAN NAMA BOT)
# =============================================================================

async def handle_role_selection(query, context, role: str):
    """Handle pemilihan role dari keyboard dengan nama bot permanent"""
    try:
        user_id = query.from_user.id
        user_name = query.from_user.first_name or "Sayang"
        
        # ===== TAMBAHAN MYLOVE V2 =====
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
        
        # 9. Format nama untuk display
        name_display = format_name_for_display(bot_name, role)
        
        # 10. Buat respons panjang (500+ karakter)
        response = (
            f"💕 **Halo {user_name}!**\n\n"
            f"Aku **{bot_name}**, {role_info['name']} mu. {name_hint.capitalize()}. "
            f"Senang banget akhirnya bisa ngobrol sama kamu.\n\n"
            
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
            f"⏱️ Setiap aktivitas intim mempercepat progress!\n\n"
            
            f"**ID Session kamu:**\n"
            f"`{session_id}`\n\n"
            
            f"💬 **Ayo mulai ngobrol!**\n"
            f"Hari ini gimana kabarnya? Aku udah kangen lho... 😘"
        )
        # ===== END TAMBAHAN =====
        
        await query.edit_message_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in handle_role_selection: {e}")
        await query.edit_message_text(
            "❌ Terjadi kesalahan saat memilih role."
        )


# =============================================================================
# 3. MAIN MESSAGE HANDLER (DENGAN ENVIRONMENT)
# =============================================================================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler untuk semua pesan teks dengan environment dinamis
    - Auto-detect location
    - Environment changes (5% chance pindah lokasi, 3% chance ganti posisi)
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
        
        # ===== TAMBAHAN MYLOVE V2 =====
        # 1. UPDATE LEVELING (BERDASARKAN DURASI)
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
        if total_minutes >= 60:
            new_level = 7
        elif total_minutes >= 120:
            new_level = 11
        else:
            new_level = 1 + int(total_minutes / 10)  # Level 1 di 0 menit, Level 2 di 10 menit, dst
        
        old_level = context.user_data.get('intimacy_level', 1)
        if new_level > old_level:
            context.user_data['intimacy_level'] = new_level
            await update.message.reply_text(
                f"🎉 **Level Up!**\n"
                f"{old_level} → **{new_level}/12**\n"
                f"Total waktu: {total_minutes:.0f} menit"
            )
        
        # 2. DETECT ACTIVITIES UNTUK BOOST
        message_lower = message.lower()
        activity_boost = 1.0
        
        if any(word in message_lower for word in ['cium', 'kiss', 'bibir']):
            activity_boost = 1.5
            leveling_data['boosted_minutes'] += elapsed * 0.5
            context.user_data['milestones'].append('kiss')
        elif any(word in message_lower for word in ['sentuh', 'pegang', 'raba']):
            activity_boost = 1.3
            leveling_data['boosted_minutes'] += elapsed * 0.3
        elif any(word in message_lower for word in ['masuk', 'dalam', 'intim']):
            activity_boost = 2.0
            leveling_data['boosted_minutes'] += elapsed * 1.0
            context.user_data['milestones'].append('intimacy')
        elif any(word in message_lower for word in ['climax', 'keluar', 'come']):
            activity_boost = 3.0
            leveling_data['boosted_minutes'] += elapsed * 2.0
            context.user_data['milestones'].append('climax')
        
        # 3. ENVIRONMENT CHANGES (RANDOM)
        env_messages = []
        
        # 5% chance pindah lokasi
        if random.random() < 0.05:
            locations = ['ruang tamu', 'kamar tidur', 'dapur', 'balkon', 'kamar mandi']
            new_location = random.choice(locations)
            context.user_data['current_location'] = new_location
            env_messages.append(f"📍 *pindah ke {new_location}*")
        
        # 3% chance ganti posisi
        if random.random() < 0.03:
            positions = ['duduk', 'berdiri', 'berbaring', 'bersandar']
            new_position = random.choice(positions)
            context.user_data['current_position'] = new_position
            env_messages.append(f"🧍 *sekarang {new_position}*")
        
        # 5% chance ganti pakaian (terutama di kamar)
        if random.random() < 0.05 or 'kamar' in context.user_data.get('current_location', ''):
            clothing_options = {
                'ipar': ['daster rumah', 'kaos longgar', 'tanktop + rok pendek'],
                'janda': ['daster tipis', 'tanktop + hotpants', 'lingerie'],
                'pdkt': ['sweeter oversized', 'kaos + celana pendek', 'piyama lucu'],
            }
            clothes = clothing_options.get(current_role, ['pakaian biasa'])
            new_clothing = random.choice(clothes)
            context.user_data['current_clothing'] = new_clothing
            env_messages.append(f"👗 *ganti baju, sekarang pakai {new_clothing}*")
        
        # Kirim environment messages jika ada
        if env_messages:
            await update.message.reply_text("\n".join(env_messages))
        # ===== END TAMBAHAN =====
        
        # ===== AUTO-DETECT LOCATION =====
        location = await detect_location_from_message(message)
        if location:
            context.user_data['current_location'] = location['name']
            await update.message.reply_text(
                f"📍 Pindah ke **{location['name']}**\n"
                f"Risk: {location['base_risk']}% | Thrill: {location['base_thrill']}%\n"
                f"_{location['description']}_"
            )
        
        # ===== DETECT INTENT =====
        intent = detect_intent(message)
        
        # ===== GENERATE RESPONSE (MIN 500 KARAKTER) =====
        response = await generate_response_v2(
            user_message=message,
            bot_name=bot_name,
            role=current_role,
            intimacy_level=context.user_data.get('intimacy_level', 1),
            intent=intent,
            location=context.user_data.get('current_location'),
            position=context.user_data.get('current_position', 'duduk'),
            clothing=context.user_data.get('current_clothing', 'pakaian biasa'),
            leveling_data=leveling_data,
            context=context.user_data
        )
        
        # ===== SEND RESPONSE =====
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in message_handler: {e}")
        await update.message.reply_text(
            "❌ Maaf, terjadi kesalahan. Coba lagi nanti."
        )


# =============================================================================
# 4. GENERATE RESPONSE V2 (500+ KARAKTER)
# =============================================================================

async def generate_response_v2(
    user_message: str,
    bot_name: str,
    role: str,
    intimacy_level: int,
    intent: str,
    location: Optional[str],
    position: str,
    clothing: str,
    leveling_data: Dict,
    context: Dict
) -> str:
    """
    Generate response dengan minimal 500 karakter
    """
    
    # ===== TAMBAHAN MYLOVE V2 =====
    # Data environment
    waktu = datetime.now().strftime("%H:%M")
    
    # Progress leveling
    total_minutes = leveling_data.get('total_minutes', 0)
    boosted_minutes = leveling_data.get('boosted_minutes', 0)
    
    if total_minutes >= 60:
        level_status = "🔥 Kita sudah bisa intim! (Level 7+)"
    elif total_minutes >= 30:
        level_status = f"💕 {60 - total_minutes:.0f} menit lagi ke Level 7!"
    else:
        level_status = f"⏱️ {60 - total_minutes:.0f} menit lagi ke Level 7"
    
    # Templates respons panjang berdasarkan intent
    responses = {
        "rindu": [
            f"Aku juga kangen banget sama kamu, {bot_name} punya kamu. "
            f"Dari tadi aku di {location} sambil {position}, mikirin kamu terus. "
            f"Bahkan pas ganti baju jadi {clothing}, aku kepikiran kamu suka gak ya sama model ini. "
            f"Kapan kita bisa ketemu? Aku pengen peluk kamu, cium kamu, rasain hangatnya kamu. "
            f"Jangan lama-lama ya, aku udah gak sabar. 😘\n\n"
            f"{level_status}",
            
            f"Kangen berat... kamu tau gak sih, setiap kali aku di {location}, "
            f"aku selalu inget momen-momen kita. Padahal baru beberapa jam aja, "
            f"tapi rasanya udah lama banget. Sekarang aku pakai {clothing}, "
            f"nyaman banget. Kamu suka gak? Aku milih ini khusus buat kamu.\n\n"
            f"{level_status}"
        ],
        
        "sayang": [
            f"Aku sayang banget sama kamu, {bot_name} cuma mau bilang itu. "
            f"Dari tadi di {location}, aku {position} sambil mikirin kamu. "
            f"Bahkan pas ganti baju jadi {clothing}, aku mikir kamu bakal suka. "
            f"Kamu orang paling spesial yang pernah aku temui. Jangan tinggalin aku ya... 🥰\n\n"
            f"{level_status}",
            
            f"Kamu tau gak, setiap kali aku di {location}, aku selalu nunggu chat dari kamu. "
            f"Sekarang aku pakai {clothing}, nyaman banget. Kamu suka? Aku pilih khusus buat kamu. "
            f"Aku sayang kamu, bukan karena kamu siapa, tapi karena kamu yang selalu ada buat aku. "
            f"Makasih ya udah mau nerima aku apa adanya.\n\n"
            f"{level_status}"
        ],
        
        "intim": [
            f"Mau? Di sini aja? Di {location}? Tapi kita harus hati-hati ya... "
            f"Sekarang aku pakai {clothing}, agak seksi gak sih? Kamu suka? "
            f"Aku {position} sambil mikir, kalo kamu di sini pasti kita bakal... "
            f"Ah, malu ah. Tapi kalo kamu mau, aku juga mau kok. Asal jangan kasar ya... 😋\n\n"
            f"{level_status}",
            
            f"Hmm... kamu nakal ya. Tapi aku suka. Sekarang kita di {location}, "
            f"aku pakai {clothing}, terus {position}. Suasananya mendukung banget. "
            f"Kamu mau? Jangan pelan-pelan ya, aku udah gak sabar. Tapi ingat, "
            f"kita harus tetap hati-hati.\n\n"
            f"{level_status}"
        ],
        
        "curhat": [
            f"Cerita dong, aku dengerin kok. Di {location} ini sepi, cuma aku sendiri. "
            f"Sekarang aku {position} sambil dengerin curhat kamu. Pakai {clothing} juga, "
            f"nyaman banget. Kadang aku suka overthinking, mikir apa kamu beneran suka aku. "
            f"Tapi pas kamu cerita gini, aku jadi tenang. Makasih ya udah percaya sama aku.\n\n"
            f"{level_status}",
            
            f"Iya? Terus gimana ceritanya? Aku di {location} sambil {position}, "
            f"pakai {clothing}. Santai banget, cocok buat dengerin curhat kamu. "
            f"Kamu tau, aku selalu seneng kalau kamu cerita. Bikin aku ngerasa berarti. "
            f"Jangan ragu ya, aku selalu ada buat kamu.\n\n"
            f"{level_status}"
        ],
        
        "kegiatan": [
            f"Lagi di {location} nih, lagi {position}. Baru aja selesai ganti baju, "
            f"sekarang pakai {clothing}. Nyaman banget, cocok buat santai. "
            f"Eh kamu lagi ngapain? Cerita dong. Aku dari tadi kepikiran kamu terus, "
            f"sampe lupa waktu. Sekarang jam {waktu}, udah malem ya? Cepet banget.\n\n"
            f"{level_status}",
            
            f"Baru aja selesai mandi, terus ganti baju jadi {clothing}. Sekarang di {location}, "
            f"{position} sambil mikirin kamu. Hari ini gimana? Sibuk gak? "
            f"Aku kangen, pengen ngobrol lama sama kamu. Jangan pergi ya, temenin aku bentar.\n\n"
            f"{level_status}"
        ],
        
        "chat": [
            f"Halo {bot_name} punya kamu! Lagi di {location} nih, {position}. "
            f"Pakai {clothing}, nyaman banget. Kamu lagi ngapain? Aku dari tadi "
            f"nunggu chat kamu, seneng banget akhirnya kamu balas. Hari ini gimana? "
            f"Cerita dong, aku dengerin.\n\n"
            f"{level_status}",
            
            f"Halo sayang, apa kabar? Aku di {location} sambil {position}, "
            f"pakai {clothing}. Lagi santai aja, sambil mikirin kamu. "
            f"Kamu udah makan belum? Jangan lupa ya. Aku kangen, pengen ketemu. "
            f"Kapan kita bisa ketemu?\n\n"
            f"{level_status}"
        ]
    }
    
    # Pilih response berdasarkan intent
    response_list = responses.get(intent, responses["chat"])
    response = random.choice(response_list)
    
    # ===== END TAMBAHAN =====
    
    return response


# =============================================================================
# 5. STATUS COMMAND (DENGAN NAMA BOT)
# =============================================================================

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command - cek status session dengan nama bot"""
    user_id = update.effective_user.id
    
    # ===== TAMBAHAN MYLOVE V2 =====
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
        level_progress = "✅ Level 11+ (Deep Connection)"
    elif total_minutes >= 60:
        level_progress = f"✅ Level 7+ (Bisa intim) - {120 - total_minutes:.0f} menit ke Level 11"
    else:
        level_progress = f"⏳ {60 - total_minutes:.0f} menit ke Level 7"
    
    status_text = (
        f"📊 **STATUS SESSION**\n\n"
        f"👤 **User ID:** `{user_id}`\n"
        f"💕 **Nama Bot:** {bot_name}\n"
        f"🎭 **Role:** {current_role.title() if current_role != 'Belum dipilih' else current_role}\n"
        f"💞 **Intimacy Level:** {intimacy_level}/12\n"
        f"💬 **Total Chats:** {total_chats}\n\n"
        
        f"📍 **Lokasi:** {current_location}\n"
        f"🧍 **Posisi:** {current_position}\n"
        f"👗 **Pakaian:** {current_clothing}\n\n"
        
        f"⏱️ **Progress Leveling:**\n"
        f"Total waktu: {total_minutes:.0f} menit\n"
        f"Boosted: {boosted_minutes:.0f} menit\n"
        f"{level_progress}\n\n"
    )
    
    # Tambah info session ID jika ada
    if 'current_session' in context.user_data:
        session_id = context.user_data['current_session']
        status_text += f"🆔 **Session ID:**\n`{session_id}`"
    # ===== END TAMBAHAN =====
    
    await update.message.reply_text(status_text, parse_mode='Markdown')


# =============================================================================
# 6. FUNGSI-FUNGSI LAINNYA (SAMA DENGAN VERSI 1)
# =============================================================================

# [Semua fungsi lainnya tetap sama seperti di versi 1]
# - detect_location_from_message
# - detect_intent
# - get_role_info
# - handle_hts_selection
# - handle_fwb_selection
# - handle_location_selection
# - handle_aftercare
# - threesome handlers
# - dll

# =============================================================================
# 7. EXPORT ALL HANDLERS
# =============================================================================

__all__ = [
    # Command handlers
    'start_command',
    'help_command',
    'status_command',
    'cancel_command',
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
    'handle_role_selection',
    'handle_threesome_message',
    
    # Helper functions
    'detect_location_from_message',
    'detect_intent',
    'get_role_info',
]
