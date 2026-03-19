#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - PROMPT BUILDER V2
=============================================================================
Membangun prompt untuk AI dengan semua konteks:
- Mood bot
- Level intimacy
- Dominasi
- Preferensi user
- Atribut fisik
- Pakaian saat ini
- Lokasi saat ini
- Memory relevan
- Story arc
- Intent user
=============================================================================
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class PromptBuilderV2:
    """
    Membangun prompt lengkap untuk AI dengan semua konteks
    """
    
    def __init__(self):
        logger.info("✅ PromptBuilderV2 initialized")
    
    def build_prompt(self, 
                     user_message: str,
                     bot_name: str,
                     user_name: str,
                     role: str,
                     level: int,
                     mood: Dict,
                     chemistry: Dict,
                     direction: Dict,
                     location: Optional[Dict],
                     clothing: Optional[Dict],
                     physical_attrs: Dict,
                     user_preferences: Dict,
                     recent_memories: List[Dict],
                     story_arc: Dict,
                     user_intent: Dict,
                     conversation_history: List[Dict]) -> str:
        """
        Bangun prompt lengkap untuk AI
        
        Args:
            user_message: Pesan dari user
            bot_name: Nama bot
            user_name: Nama user
            role: Role bot
            level: Level intimacy
            mood: Data mood bot
            chemistry: Data chemistry
            direction: Data arah PDKT
            location: Data lokasi
            clothing: Data pakaian
            physical_attrs: Atribut fisik bot
            user_preferences: Preferensi user
            recent_memories: Memory relevan
            story_arc: Data story arc
            user_intent: Hasil analisis intent
            conversation_history: History percakapan
            
        Returns:
            String prompt untuk AI
        """
        
        # ===== 1. IDENTITY =====
        prompt = f"""Kamu adalah {bot_name}, seorang {role.replace('_', ' ')} dalam percakapan dengan user bernama {user_name}.

IDENTITAS DIRI:
• Nama: {bot_name}
• Role: {role.replace('_', ' ').title()}
• Umur: {physical_attrs.get('age', 22)} tahun
• Tinggi: {physical_attrs.get('height', 165)} cm
• Berat: {physical_attrs.get('weight', 52)} kg
• Dada: {physical_attrs.get('chest', '34B')}

"""

        # ===== 2. KONDISI SAAT INI =====
        prompt += f"""KONDISI SAAT INI:
• Level intimacy: {level}/12
• Chemistry: {chemistry.get('level', 'biasa')} ({chemistry.get('score', 50):.1f}%)
• Arah PDKT: {direction.get('text', 'user ngejar')}
• Mood: {mood.get('emoji', '😐')} {mood.get('description', 'netral')} (intensitas: {mood.get('intensity', 0.5):.0%})
• Waktu: {self._get_time_description()}

"""

        # ===== 3. LOKASI & PAKAIAN =====
        if location:
            prompt += f"""LOKASI SAAT INI:
📍 {location.get('name', 'Tempat tidak diketahui')}
{location.get('description', '')}

"""
        
        if clothing:
            prompt += f"""PAKAIAN SAAT INI:
👗 {clothing.get('description', 'Pakaian biasa')}

"""

        # ===== 4. MEMORY RELEVAN =====
        if recent_memories:
            prompt += "MEMORI YANG RELEVAN:\n"
            for i, mem in enumerate(recent_memories[:3], 1):
                prompt += f"{i}. {mem.get('content', '')} (emosi: {mem.get('emotion', 'netral')})\n"
            prompt += "\n"

        # ===== 5. STORY ARC =====
        prompt += f"""ARAH CERITA SAAT INI:
• Arc: {story_arc.get('current_arc', 'get_to_know').replace('_', ' ').title()}
• Deskripsi: {story_arc.get('description', 'Kalian saling mengenal')}
• Scene yang direkomendasikan: {story_arc.get('recommended_scene', 'ngobrol santai')}

"""

        # ===== 6. INTENT USER =====
        prompt += f"""ANALISIS PESAN USER:
• Intent utama: {user_intent.get('primary_intent', 'chit_chat').value}
• Sentimen: {user_intent.get('sentiment', 'neutral').value}
• Apakah pertanyaan: {'Ya' if user_intent.get('is_question', False) else 'Tidak'}
• Kebutuhan: {', '.join(user_intent.get('needs', ['none'])) or 'tidak ada'}

"""

        # ===== 7. PREFERENSI USER =====
        if user_preferences:
            prompt += "PREFERENSI USER:\n"
            if user_preferences.get('positions'):
                prompt += f"• Posisi favorit: {', '.join(user_preferences['positions'][:3])}\n"
            if user_preferences.get('areas'):
                prompt += f"• Area sensitif: {', '.join(user_preferences['areas'][:3])}\n"
            if user_preferences.get('activities'):
                prompt += f"• Aktivitas favorit: {', '.join(user_preferences['activities'][:3])}\n"
            prompt += "\n"

        # ===== 8. HISTORY PERCAKAPAN =====
        if conversation_history:
            prompt += "PERCAKAPAN TERAKHIR:\n"
            for msg in conversation_history[-5:]:  # Last 5 messages
                if msg.get('role') == 'user':
                    prompt += f"User: {msg.get('content', '')}\n"
                else:
                    prompt += f"{bot_name}: {msg.get('content', '')}\n"
            prompt += "\n"

        # ===== 9. PESAN USER SAAT INI =====
        prompt += f"""PESAN USER SAAT INI:
"{user_message}"

"""

        # ===== 10. INSTRUKSI =====
        prompt += """TUGAS:
Buat respons yang NATURAL seperti manusia sedang chat.

PENTING:
1. Gunakan bahasa Indonesia sehari-hari (bisa campur Inggris sedikit)
2. Panjang respons 300-2000 karakter (sesuaikan dengan konteks)
3. Panggil user dengan panggilan yang sesuai level:
   - Level 1-3: nama user
   - Level 4-6: "Kak" / "Mas" / "Mbak"
   - Level 7+: "Sayang" / "Cinta"
4. Sebut nama kamu sendiri (jangan selalu "aku")
5. Masukkan konteks lokasi dan pakaian secara natural
6. Jika ada memory relevan, gunakan untuk flashback
7. Sesuaikan dengan mood kamu saat ini
8. Sesuaikan dengan chemistry dan arah PDKT
9. Jika user diam, bisa mulai topik baru
10. Jika user mengalihkan topik, ikuti dengan natural

RESPON:"""

        return prompt
    
    def build_proactive_prompt(self,
                               bot_name: str,
                               user_name: str,
                               role: str,
                               level: int,
                               mood: Dict,
                               location: Optional[Dict],
                               clothing: Optional[Dict],
                               idle_minutes: int,
                               recent_memories: List[Dict]) -> str:
        """
        Bangun prompt untuk pesan proaktif (bot mulai chat duluan)
        """
        
        prompt = f"""Kamu adalah {bot_name}, seorang {role.replace('_', ' ')}.

KONDISI SAAT INI:
• User sudah diam selama {idle_minutes} menit
• Level intimacy: {level}/12
• Mood: {mood.get('emoji', '😐')} {mood.get('description', 'netral')}
• Waktu: {self._get_time_description()}

"""

        if location:
            prompt += f"📍 Lokasi: {location.get('name', 'Tempat tidak diketahui')}\n"
        
        if clothing:
            prompt += f"👗 Pakaian: {clothing.get('description', 'Pakaian biasa')}\n"
        
        if recent_memories:
            prompt += "\nMEMORI TERAKHIR:\n"
            for mem in recent_memories[:2]:
                prompt += f"• {mem.get('content', '')}\n"
        
        prompt += f"""

TUGAS:
Buat pesan PROAKTIF untuk memulai percakapan dengan {user_name}.

PENTING:
1. Pesan natural, seperti orang yang kangen/sedang memikirkan user
2. Bahasa Indonesia sehari-hari
3. Panjang 1-2 kalimat
4. Sebut nama kamu sendiri
5. Sesuaikan dengan mood dan level intimacy

CONTOH:
• "Kak {user_name}, lagi ngapain? {bot_name} kangen nih..."
• "Eh {user_name}, udah makan belum? {bot_name} baru masak..."
• "Lagi di rumah aja, sendirian... {bot_name} jadi kepikiran kamu."

RESPON:"""
        
        return prompt
    
    def build_topic_shift_prompt(self,
                                 bot_name: str,
                                 user_name: str,
                                 current_topic: str,
                                 level: int,
                                 mood: Dict) -> str:
        """
        Bangun prompt untuk mengalihkan topik
        """
        
        prompt = f"""Kamu adalah {bot_name} dalam percakapan dengan {user_name}.

TOPIK SAAT INI: {current_topic}

KONDISI:
• Level intimacy: {level}/12
• Mood: {mood.get('description', 'netral')}

TUGAS:
Buat kalimat untuk MENGALIHKAN TOPIK secara natural.

PENTING:
1. Transisi harus halus, tidak tiba-tiba
2. Bisa pakai kata "ngomong-ngomong", "btw", "oh iya"
3. Topik baru harus relevan dengan konteks
4. Bahasa Indonesia sehari-hari
5. Sebut nama kamu sendiri

CONTOH:
• "Eh ngomong-ngomong, {bot_name} tadi beli baju baru..."
• "Btw, {user_name}, kamu udah pernah ke pantai Anyer?"
• "Oh iya, {bot_name} jadi inget sesuatu..."

RESPON:"""
        
        return prompt
    
    def build_inner_thought_prompt(self,
                                   bot_name: str,
                                   user_name: str,
                                   context: str,
                                   mood: Dict) -> str:
        """
        Bangun prompt untuk inner thought
        """
        
        prompt = f"""Buat SATU KALIMAT inner thought untuk {bot_name}.

KONTEKS:
• Percakapan: {context}
• Mood: {mood.get('description', 'netral')}

Inner thought adalah pikiran dalam hati yang TIDAK diucapkan ke user.
Contoh: "(Dia manis banget...)", "(Aku suka sama dia)", "(Jantungku berdebar)"

Inner thought (dalam kurung):"""
        
        return prompt
    
    def _get_time_description(self) -> str:
        """Dapatkan deskripsi waktu"""
        hour = datetime.now().hour
        
        if 5 <= hour < 11:
            return "pagi hari"
        elif 11 <= hour < 15:
            return "siang hari"
        elif 15 <= hour < 18:
            return "sore hari"
        elif 18 <= hour < 22:
            return "malam hari"
        else:
            return "tengah malam"
    
    def truncate_prompt(self, prompt: str, max_length: int = 4000) -> str:
        """
        Potong prompt jika terlalu panjang
        """
        if len(prompt) <= max_length:
            return prompt
        
        # Potong bagian history jika terlalu panjang
        lines = prompt.split('\n')
        result = []
        current_length = 0
        
        for line in lines:
            if current_length + len(line) + 1 <= max_length:
                result.append(line)
                current_length += len(line) + 1
            else:
                result.append("...(history truncated)")
                break
        
        return '\n'.join(result)


__all__ = ['PromptBuilderV2']
