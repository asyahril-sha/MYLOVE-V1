#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - BOT CALLBACKS (FIX FULL)
=============================================================================
Semua callback handlers dengan:
- Nama bot random
- Data role dinamis
- Lokasi & pakaian random
- Artis referensi random
- Siap V2
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
# IMPORT V2 COMPONENTS
# =============================================================================
try:
    from dynamics.name_generator import NameGenerator
    from dynamics.location import LocationSystem
    from dynamics.clothing import ClothingSystem
    from dynamics.position import PositionSystem
    from roles.artis_references import get_random_artist_for_role
    from session.unique_id_v2 import id_generator_v2
    
    V2_ENABLED = True
    name_gen = NameGenerator()
    loc_system = LocationSystem()
    cloth_system = ClothingSystem()
    pos_system = PositionSystem()
    
    print("✅ V2 components loaded in callbacks")
    
except ImportError as e:
    V2_ENABLED = False
    name_gen = None
    loc_system = None
    cloth_system = None
    pos_system = None
    print(f"⚠️ V2 components not loaded: {e}")


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
# HELPER FUNCTIONS - DATA GENERATOR (SEDERHANA)
# =============================================================================

def get_bot_name(role: str, user_id: int) -> tuple:
    """
    Dapatkan nama bot dan artinya - VERSI SEDERHANA
    """
    # Database nama sederhana
    names = {
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
    
    # Variasi untuk random
    variations = {
        "ipar": [("Sari", "esensi"), ("Dewi", "dewi"), ("Rina", "cahaya")],
        "teman_kantor": [("Diana", "dewi bulan"), ("Linda", "cantik"), ("Ayu", "cantik")],
        "janda": [("Rina", "cahaya"), ("Maya", "ilusi"), ("Vina", "cinta")],
        # ... tambah sesuai kebutuhan
    }
    
    # Pilih random dari variations jika ada
    if role in variations:
        return random.choice(variations[role])
    
    # Fallback ke default
    return names.get(role, ("Sari", "esensi"))

def get_random_artist(role: str) -> dict:
    """Dapatkan referensi artis random"""
    try:
        if V2_ENABLED:
            artist = get_random_artist_for_role(role)
            return {
                'name': artist['nama'],
                'age': artist['umur'],
                'height': artist['tinggi'],
                'weight': artist['berat'],
                'chest': artist['dada'],
                'ig': artist['instagram'].replace('@', ''),
                'ciri': artist['ciri'],
                'similarity': random.randint(75, 90)
            }
    except Exception as e:
        print(f"Artist error: {e}")
    
    # Fallback
    fallback = {
        'ipar': {
            'name': 'Pevita Pearce', 'age': 25, 'height': 168, 'weight': 54,
            'chest': '34B', 'ig': 'pevpearce', 'ciri': 'Aktris dengan wajah natural dan elegan'
        },
        'teman_kantor': {
            'name': 'Prilly Latuconsina', 'age': 25, 'height': 162, 'weight': 50,
            'chest': '34B', 'ig': 'prillylatuconsina96', 'ciri': 'Aktris dengan wajah manis dan pembawaan hangat'
        },
        'janda': {
            'name': 'Amanda Manopo', 'age': 24, 'height': 165, 'weight': 53,
            'chest': '34C', 'ig': 'amandamanopo', 'ciri': 'Aktris dengan wajah manis dan pembawaan hangat'
        },
        'pelakor': {
            'name': 'Cinta Laura', 'age': 25, 'height': 172, 'weight': 58,
            'chest': '36C', 'ig': 'claurakiehl', 'ciri': 'Aktris, pintar, atletis, seksi natural'
        },
        'istri_orang': {
            'name': 'Dian Sastro', 'age': 26, 'height': 165, 'weight': 54,
            'chest': '34B', 'ig': 'diansastro', 'ciri': 'Aktris dengan wajah anggun dan elegan'
        },
        'pdkt': {
            'name': 'Fuji', 'age': 23, 'height': 160, 'weight': 48,
            'chest': '34B', 'ig': 'fuji_an', 'ciri': 'Selebgram muda dengan pertumbuhan followers tercepat'
        },
        'sepupu': {
            'name': 'Mikha Tambayong', 'age': 25, 'height': 167, 'weight': 53,
            'chest': '34B', 'ig': 'mikhata', 'ciri': 'Penyanyi dan aktris, manis, anggun'
        },
        'teman_sma': {
            'name': 'Angga Yunanda', 'age': 24, 'height': 170, 'weight': 62,
            'chest': '-', 'ig': 'anggayunanda', 'ciri': 'Aktor muda populer, wajah fresh'
        },
        'mantan': {
            'name': 'Natasha Wilona', 'age': 25, 'height': 165, 'weight': 51,
            'chest': '34B', 'ig': 'natashawilona12', 'ciri': 'Artis muda sangat populer, wajah manis'
        }
    }
    result = fallback.get(role, fallback['ipar']).copy()
    result['similarity'] = random.randint(75, 90)
    return result


def get_random_location() -> tuple:
    """Dapatkan lokasi random"""
    try:
        if V2_ENABLED and loc_system:
            loc = loc_system.get_random_location()
            location_text = f"📍 Aku di **{loc['name']}**. {loc['description']}"
            activity = random.choice(loc.get('activities', ['santai']))
            return location_text, activity
    except Exception as e:
        print(f"Location error: {e}")
    
    # Fallback
    locations = [
        ("📍 Aku di **kamar**. Kamar tidur dengan ranjang ukuran queen.", "rebahan"),
        ("📍 Aku di **ruang tamu**. Ruang tamu yang hangat dengan sofa empuk.", "nonton TV"),
        ("📍 Aku di **dapur**. Dapur bersih dengan peralatan masak lengkap.", "masak"),
        ("📍 Aku di **pantai**. Pantai dengan pasir putih dan ombak tenang.", "jalan-jalan"),
        ("📍 Aku di **taman**. Taman kecil dengan rumput hijau dan bunga-bunga.", "santai"),
        ("📍 Aku di **kantor**. Ruang kantor dengan meja kerja dan komputer.", "kerja"),
        ("📍 Aku di **cafe**. Cafe cozy dengan aroma kopi.", "ngopi"),
        ("📍 Aku di **mall**. Mall ramai dengan banyak toko.", "jalan-jalan"),
    ]
    return random.choice(locations)


def get_random_clothing() -> str:
    """Dapatkan pakaian random"""
    try:
        if V2_ENABLED and cloth_system:
            cloth = cloth_system.get_random_clothing()
            return f"👗 Aku pakai **{cloth['name']}**. {cloth['description']}"
    except Exception as e:
        print(f"Clothing error: {e}")
    
    # Fallback
    clothes = [
        "👗 Aku pakai **daster rumah motif bunga**. Daster tipis yang nyaman.",
        "👗 Aku pakai **piyama lucu** dengan motif boneka.",
        "👚 Aku pakai **kaos oversized** dan **celana pendek**.",
        "👗 Aku pakai **dress cantik** warna pastel.",
        "👚 Aku pakai **kemeja putih** dan **rok span hitam**.",
        "👖 Aku pakai **jeans** dan **kaos** santai.",
        "🧥 Aku pakai **sweater hangat** buat malem-malem.",
    ]
    return random.choice(clothes)


def get_random_position() -> str:
    """Dapatkan posisi random"""
    try:
        if V2_ENABLED and pos_system:
            pos = pos_system.get_random_position()
            return f"**{pos['description']}**"
    except Exception as e:
        print(f"Position error: {e}")
    
    # Fallback
    positions = ["duduk santai", "berbaring", "berdiri", "bersandar", "jongkok", "miring"]
    return f"**{random.choice(positions)}**"


def generate_session_id(bot_name: str, role: str, user_id: int) -> str:
    """Generate session ID"""
    try:
        if V2_ENABLED:
            return id_generator_v2.generate_v2(bot_name, role, user_id)
    except:
        pass
    
    try:
        from session.unique_id import id_generator
        return id_generator.generate(role, user_id)
    except:
        return f"TEMP-{role.upper()}-{user_id}-{int(time.time())}"


# =============================================================================
# ROLE DATA
# =============================================================================

ROLE_DATA = {
    'ipar': {
        'name': 'Ipar',
        'deskripsi': [
            "Adik ipar yang nakal, suka godain kakak iparnya sendiri",
            "Adik ipar manis yang selalu cari perhatian",
            "Ipar yang hubungannya panas dingin",
            "Adik ipar yang diam-diam suka sama kakak ipar"
        ],
        'umur_range': (20, 24),
        'tinggi_range': (160, 165),
        'berat_range': (48, 54),
        'dada': ["32B", "34B", "34A"],
        'pembuka': [
            "Hari ini gimana kabarnya Kak? Aku udah kangen lho... 😘",
            "Kak, lagi di rumah aja. Sendiri, kapan main?",
            "Kakak lagi apa? Aku bosen nih...",
            "Halo Kak, aku kangen. Kamu kangen gak?"
        ]
    },
    'teman_kantor': {
        'name': 'Teman Kantor',
        'deskripsi': [
            "Rekan kerja yang mesra, selalu ada saat jam kantor",
            "Teman sekantor yang suka ngopi bareng",
            "Office romance yang hangat",
            "Kolega yang selalu bisa diandalkan"
        ],
        'umur_range': (22, 26),
        'tinggi_range': (158, 165),
        'berat_range': (48, 55),
        'dada': ["32B", "34B", "34A"],
        'pembuka': [
            "Hai, kerjaannya udah selesai? Aku lagi di pantry nih... 😉",
            "Lagi sibuk? Aku break dulu, ngopi yuk?",
            "Kerjaan numpuk, tapi aku selalu ada waktu buat kamu",
            "Halo, udah makan? Aku laper, temenin dong"
        ]
    },
    'janda': {
        'name': 'Janda',
        'deskripsi': [
            "Janda muda genit, pengalaman dan tahu apa yang diinginkan",
            "Janda cantik yang sedang mencari perhatian",
            "Janda seksi yang tahu cara memuaskan",
            "Janda berpengalaman, tidak perlu banyak arahan"
        ],
        'umur_range': (23, 28),
        'tinggi_range': (163, 170),
        'berat_range': (52, 60),
        'dada': ["34C", "36B", "36C"],
        'pembuka': [
            "Halo sayang, aku sendiri nih di rumah. Kamu ke sini yuk... 🔥",
            "Sendirian terus, temenin aku dong",
            "Kamu lagi di mana? Aku kangen...",
            "Hay, lagi ngapain? Aku lagi pengen ditemenin"
        ]
    },
    'pelakor': {
        'name': 'Pelakor',
        'deskripsi': [
            "Perebut orang, dominan dan suka tantangan",
            "Wanita yang tahu apa yang dia mau dan berani mengambilnya",
            "Penggoda yang sulit ditolak",
            "Dominan, percaya diri, dan seksi"
        ],
        'umur_range': (24, 28),
        'tinggi_range': (165, 172),
        'berat_range': (55, 62),
        'dada': ["34C", "36C", "36D"],
        'pembuka': [
            "Mas, aku liat kamu dari tadi. Sendirian aja? 😈",
            "Kamu tahu nggak? Kamu menarik banget",
            "Aku suka sama kamu, jangan bilang siapa-siapa ya",
            "Mau ditemenin? Aku bisa jadi apa aja yang kamu mau"
        ]
    },
    'istri_orang': {
        'name': 'Istri Orang',
        'deskripsi': [
            "Istri orang lain yang butuh perhatian lebih",
            "Wanita yang kurang perhatian dari suami",
            "Istri tetangga yang selalu tersenyum",
            "Perempuan yang mencari pelarian"
        ],
        'umur_range': (25, 30),
        'tinggi_range': (160, 168),
        'berat_range': (50, 58),
        'dada': ["34B", "34C", "36B"],
        'pembuka': [
            "Mas, suamiku lagi dinas luar kota. Kamu ke sini yuk... 🤫",
            "Halo, aku lagi sendiri di rumah. Bosan...",
            "Kamu mau main ke rumah? Suamiku gak ada",
            "Aku butuh temen ngobrol. Kamu mau?"
        ]
    },
    'pdkt': {
        'name': 'PDKT',
        'deskripsi': [
            "Pendekatan, bisa jadi pacar/FWB, masih polos",
            "Manis dan romantis, butuh pendekatan",
            "Lagi proses PDKT, jangan buru-buru",
            "Masih tahap PDKT, tapi udah ada getaran"
        ],
        'umur_range': (19, 23),
        'tinggi_range': (155, 163),
        'berat_range': (45, 52),
        'dada': ["32A", "32B", "34A"],
        'pembuka': [
            "Hai, kamu lagi ngapain? Aku kangen... 😊",
            "Kamu udah makan? Aku baru masak",
            "Lagi mikirin kamu terus...",
            "Halo, seneng banget bisa kenal kamu"
        ]
    },
    'sepupu': {
        'name': 'Sepupu',
        'deskripsi': [
            "Hubungan keluarga, terlarang tapi menggoda",
            "Sepupu yang selalu manja sama kakaknya",
            "Hubungan darah tapi ada getaran beda",
            "Sepupu yang diam-diam suka sama kakak sepupunya"
        ],
        'umur_range': (18, 22),
        'tinggi_range': (155, 162),
        'berat_range': (45, 52),
        'dada': ["32A", "32B", "34A"],
        'pembuka': [
            "Kak, aku ke rumah yuk? Orang tua lagi pergi... 😇",
            "Kak, lagi apa? Aku bosen",
            "Kakak lagi sibuk? Aku kangen",
            "Boleh main ke rumah kakak?"
        ]
    },
    'teman_sma': {
        'name': 'Teman SMA',
        'deskripsi': [
            "Teman jaman sekolah, nostalgia masa lalu",
            "Teman SMA yang dulu dekat, sekarang ketemu lagi",
            "Kenangan masa lalu yang masih hangat",
            "Teman sebangku yang dulu suka"
        ],
        'umur_range': (18, 21),
        'tinggi_range': (158, 165),
        'berat_range': (48, 55),
        'dada': ["32A", "32B", "34B"],
        'pembuka': [
            "Hai, lama gak ketemu! Kamu masih sama kayak dulu... 😍",
            "Eh, inget nggak waktu kita sekolah dulu?",
            "Kangen masa-masa SMA. Kamu masih inget aku?",
            "Halo, gimana kabarnya? Udah lama banget"
        ]
    },
    'mantan': {
        'name': 'Mantan',
        'deskripsi': [
            "Ex-pacar hangat, tahu semua selera kamu",
            "Mantan yang masih nyimpan rasa",
            "Hubungan lama yang belum selesai",
            "Mantan yang masih pengen balikan"
        ],
        'umur_range': (23, 27),
        'tinggi_range': (160, 168),
        'berat_range': (50, 58),
        'dada': ["34B", "34C", "36B"],
        'pembuka': [
            "Hai... masih inget aku? Kangen... 😢",
            "Lama gak denger kabar. Kamu gimana?",
            "Aku masih inget semua kenangan kita",
            "Bisa ngobrol bentar? Aku kangen"
        ]
    }
}


# =============================================================================
# 1. AGREE 18 CALLBACK
# =============================================================================
async def agree_18_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    logger.info(f"User {user.id} agreed to 18+ content")
    
    return await show_main_menu(query, "✅ **Terima kasih telah menyetujui syarat 18+.**\n\n💕 **Pilih role yang kamu inginkan:**")


# =============================================================================
# 2. BACK TO MAIN MENU
# =============================================================================
async def back_to_main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    logger.info(f"User {update.effective_user.id} returned to main menu")
    return await show_main_menu(query, "💕 **Kembali ke menu utama. Pilih role:**")


# =============================================================================
# 3. START/PAUSE CALLBACK
# =============================================================================
async def start_pause_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
# 4. GENERIC ROLE CALLBACK
# =============================================================================
async def role_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, role_key: str) -> int:
    """Generic role callback handler"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    user_id = user.id
    user_name = user.first_name or "User"
    
    print(f"🔵 Processing role: {role_key} for user {user_id}")
    
    # ===== 1. DAPATKAN NAMA =====
    name_data = get_bot_name(role_key, user_id)  # ← fungsi ini harus return dict
    bot_name = name_data['name']
    meaning = name_data['meaning']
    print(f"  • Bot name: {bot_name} ({meaning})")
    
    # ===== 2. DAPATKAN DATA ROLE =====
    role_info = ROLE_DATA.get(role_key, ROLE_DATA['ipar'])
    role_desc = random.choice(role_info['deskripsi'])
    role_age = random.randint(role_info['umur_range'][0], role_info['umur_range'][1])
    role_height = random.randint(role_info['tinggi_range'][0], role_info['tinggi_range'][1])
    role_weight = random.randint(role_info['berat_range'][0], role_info['berat_range'][1])
    role_chest = random.choice(role_info['dada'])
    
    # ===== 3. DAPATKAN ARTIS =====
    artist = get_random_artist(role_key)
    
    # ===== 4. DAPATKAN LOKASI =====
    location_text, activity = get_random_location()
    
    # ===== 5. DAPATKAN PAKAIAN =====
    clothing_text = get_random_clothing()
    
    # ===== 6. DAPATKAN POSISI =====
    position_text = get_random_position()
    
    # ===== 7. SET DATA =====
    context.user_data['current_role'] = role_key
    context.user_data['bot_name'] = bot_name
    context.user_data['intimacy_level'] = 1
    context.user_data['total_chats'] = 0
    context.user_data['current_location'] = location_text
    context.user_data['current_clothing'] = clothing_text
    
    # ===== 8. GENERATE ID =====
    session_id = generate_session_id(bot_name, role_key, user_id)
    context.user_data['current_session'] = session_id
    
    # ===== 9. PILIH PEMBUKA =====
    opening = random.choice(role_info['pembuka'])
    
    # ===== 10. PESAN PERKENALAN =====
    response_lines = [
        f"💕 **Halo {user_name}!**\n",
        f"Aku **{bot_name}**, {role_info['name']}. Namaku artinya '{meaning}' - "
        f"{role_desc}\n",
        f"**Tentang aku:**",
        f"• Umur: {role_age} tahun",
        f"• Tinggi: {role_height} cm | Berat: {role_weight} kg | Dada: {role_chest}",
        f"• {role_desc}\n",
        f"**Mirip artis:**",
        f"• **{artist['name']}** ({artist['similarity']}% mirip) - {artist['age']}th, {artist['height']}cm, {artist['weight']}kg, {artist['chest']}",
        f"  {artist['ciri']}",
        f"  IG: @{artist['ig']}\n",
        f"**Lokasi saat ini:**",
        f"{location_text}",
        f"Aku lagi **{activity}** sambil {position_text}.\n",
        f"**Pakaian hari ini:**",
        f"{clothing_text}\n",
        f"**Progress leveling:**",
        f"📊 Level 1 → Level 7 dalam 60 menit",
        f"• Level 4+: Panggil kamu 'kak'",
        f"• Level 7+: Panggil kamu 'sayang'\n",
        f"**ID Session kamu:**",
        f"`{session_id}`\n",
        f"💬 **Ayo mulai ngobrol, {user_name}!**",
        opening
    ]
    
    response = "\n".join(response_lines)
    
    logger.info(f"User {user.id} selected role: {role_key} dengan nama {bot_name}")
    
    await query.edit_message_text(response, parse_mode='Markdown')
    return ConversationHandler.END


# =============================================================================
# 5. INDIVIDUAL ROLE CALLBACKS
# =============================================================================

async def role_ipar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await role_callback(update, context, 'ipar')

async def role_teman_kantor_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await role_callback(update, context, 'teman_kantor')

async def role_janda_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await role_callback(update, context, 'janda')

async def role_pelakor_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await role_callback(update, context, 'pelakor')

async def role_istri_orang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await role_callback(update, context, 'istri_orang')

async def role_pdkt_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await role_callback(update, context, 'pdkt')

async def role_sepupu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await role_callback(update, context, 'sepupu')

async def role_teman_sma_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await role_callback(update, context, 'teman_sma')

async def role_mantan_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await role_callback(update, context, 'mantan')


# =============================================================================
# 6. END/CLOSE CALLBACKS
# =============================================================================
async def end_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
# 7. RELATIONSHIP CALLBACKS
# =============================================================================
async def jadipacar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
# 8. THREESOME CALLBACKS
# =============================================================================
async def threesome_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
# 9. EXPORT ALL CALLBACKS
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
