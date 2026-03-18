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
