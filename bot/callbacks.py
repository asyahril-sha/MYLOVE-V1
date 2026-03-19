# =============================================================================
# TAMBAHKAN DI ATAS (IMPORT)
# =============================================================================
from dynamics.name_generator import NameGenerator

# Buat instance
name_gen = NameGenerator()

# =============================================================================
# UPDATE ROLE CALLBACK (contoh untuk role ipar)
# =============================================================================
async def role_ipar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle ipar role callback dengan NAMA"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    user_id = user.id
    
    # ===== PILIH NAMA RANDOM =====
    name_data = name_gen.get_name_with_meaning('ipar', user_id)
    bot_name = name_data['name']
    meaning = name_data['meaning']
    # =====
    
    logger.info(f"User {user.id} selected role: ipar dengan nama {bot_name}")
    
    # Set role di context dengan NAMA
    context.user_data['current_role'] = 'ipar'
    context.user_data['bot_name'] = bot_name
    context.user_data['intimacy_level'] = 1
    context.user_data['total_chats'] = 0
    
    # Generate Unique ID dengan NAMA
    from session.unique_id_v2 import id_generator_v2
    session_id = id_generator_v2.generate_v2(bot_name, 'ipar', user_id)
    context.user_data['current_session'] = session_id
    
    # ===== PESAN PERKENALAN DENGAN NAMA =====
    response = (
        f"💕 **Halo {user.first_name}!**\n\n"
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
        f"Ada TV 50 inci di dinding, rak buku penuh novel, dan tanaman hias di sudut ruangan.\n\n"
        f"**Pakaian hari ini:**\n"
        f"👗 Aku pakai **daster rumah motif bunga**. Daster tipis yang nyaman dipakai di rumah.\n\n"
        f"**Progress leveling:**\n"
        f"📊 Level 1 → Level 7 dalam 60 menit\n"
        f"• Level 4+: Panggil kamu 'kak'\n"
        f"• Level 7+: Panggil kamu 'sayang'\n\n"
        f"**ID Session kamu:**\n"
        f"`{session_id}`\n\n"
        f"💬 **Ayo mulai ngobrol, {user.first_name}!**\n"
        f"Hari ini gimana kabarnya Kak? Aku udah kangen lho... 😘"
    )
    # =====
    
    await query.edit_message_text(response, parse_mode='Markdown')
    return ConversationHandler.END
