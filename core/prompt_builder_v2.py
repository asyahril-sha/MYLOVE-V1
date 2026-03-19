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
- Aktivitas saat ini (BARU)
- Konsistensi checker (BARU)
=============================================================================
"""

import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class PromptBuilderV2:
    """
    Membangun prompt lengkap untuk AI dengan semua konteks
    """
    
    def __init__(self):
        self.last_prompt = None
        self.last_response = None
        logger.info("✅ PromptBuilderV2 initialized")
    
    # =========================================================================
    # FORMAT WAKTU (BARU)
    # =========================================================================
    
    def _format_duration(self, seconds: float) -> str:
        """Format durasi dalam detik ke string readable"""
        if seconds < 60:
            return f"{int(seconds)} detik"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} menit"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours} jam {minutes} menit"
        else:
            days = int(seconds / 86400)
            hours = int((seconds % 86400) / 3600)
            return f"{days} hari {hours} jam"
    
    def _get_time_of_day(self) -> str:
        """Dapatkan waktu saat ini"""
        hour = datetime.now().hour
        
        if 5 <= hour < 11:
            return "pagi"
        elif 11 <= hour < 15:
            return "siang"
        elif 15 <= hour < 18:
            return "sore"
        elif 18 <= hour < 22:
            return "malam"
        else:
            return "tengah malam"
    
    # =========================================================================
    # FORMAT AKTIVITAS (BARU)
    # =========================================================================
    
    def _format_activity(self, activity: Optional[Dict]) -> str:
        """Format aktivitas saat ini untuk prompt"""
        if not activity or not activity.get('name'):
            return ""
        
        name = activity['name']
        details = activity.get('details', {})
        duration = activity.get('duration', 0)
        status = activity.get('status', 'active')
        progress = activity.get('progress')
        
        lines = [f"📌 **AKTIVITAS SAAT INI:**"]
        lines.append(f"• Kamu sedang {name}")
        
        if duration > 0:
            lines.append(f"• Sudah {self._format_duration(duration)}")
        
        if progress:
            lines.append(f"• Progress: {progress}")
        
        if details:
            for key, value in details.items():
                lines.append(f"• {key}: {value}")
        
        if status == 'paused':
            lines.append("• ⏸️ (sedang dijeda)")
        
        return "\n".join(lines)
    
    # =========================================================================
    # FORMAT MEMORY (BARU)
    # =========================================================================
    
    def _format_recent_memories(self, memories: List[Dict], limit: int = 3) -> str:
        """Format memory terbaru untuk prompt"""
        if not memories:
            return ""
        
        lines = ["📚 **MEMORI TERBARU:**"]
        for mem in memories[:limit]:
            content = mem.get('content', '')[:100]
            emotion = mem.get('emotional_tag', 'netral')
            time_ago = self._format_duration(time.time() - mem.get('timestamp', time.time()))
            lines.append(f"• [{time_ago}] {content} (emosi: {emotion})")
        
        return "\n".join(lines)
    
    def _format_important_moments(self, moments: List[Dict], limit: int = 3) -> str:
        """Format momen penting untuk prompt"""
        if not moments:
            return ""
        
        lines = ["🏆 **MOMEN PENTING:**"]
        for mom in moments[:limit]:
            desc = mom.get('description', mom.get('data', {}).get('summary', 'Momen spesial'))
            time_ago = self._format_duration(time.time() - mom.get('timestamp', time.time()))
            lines.append(f"• [{time_ago}] {desc}")
        
        return "\n".join(lines)
    
    # =========================================================================
    # FORMAT KONSISTENSI (BARU)
    # =========================================================================
    
    def _get_consistency_warnings(self, current_state: Dict, last_response: Optional[str]) -> str:
        """Dapatkan peringatan konsistensi berdasarkan state"""
        warnings = []
        
        # Cek aktivitas yang sedang berlangsung
        if current_state.get('activity'):
            activity = current_state['activity']
            warnings.append(f"⚠️ Kamu sedang {activity}, jangan lupa!")
        
        # Cek lokasi
        if current_state.get('location'):
            location = current_state['location']
            warnings.append(f"⚠️ Kamu di {location}, jangan tiba-tiba pindah tanpa sebab!")
        
        # Cek pakaian
        if current_state.get('clothing'):
            clothing = current_state['clothing']
            warnings.append(f"⚠️ Kamu pakai {clothing}, konsisten ya!")
        
        # Cek intim
        if current_state.get('is_intimate'):
            warnings.append("⚠️ LAGI INTIM! Fokus ke aktivitas, jangan ngelantur!")
        
        # Cek arousal
        if current_state.get('arousal', 0) >= 8:
            warnings.append("⚠️ LAGI HORNY BANGET! Respon dengan gairah tinggi!")
        
        if warnings:
            return "\n".join(warnings)
        return ""
    
    # =========================================================================
    # MAIN PROMPT BUILDER
    # =========================================================================
    
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
                    conversation_history: List[Dict],
                    current_activity: Optional[Dict] = None,  # BARU
                    important_moments: Optional[List[Dict]] = None,  # BARU
                    last_response: Optional[str] = None,  # BARU
                    activity_stack: Optional[List] = None  # BARU
                    ) -> str:
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
            current_activity: Aktivitas saat ini (BARU)
            important_moments: Momen penting (BARU)
            last_response: Respons terakhir (BARU)
            activity_stack: Stack aktivitas (BARU)
            
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
        time_of_day = self._get_time_of_day()
        prompt += f"""KONDISI SAAT INI:
• Level intimacy: {level}/12
• Chemistry: {chemistry.get('level', 'biasa')} ({chemistry.get('score', 50):.1f}%)
• Arah PDKT: {direction.get('text', 'user ngejar')}
• Mood: {mood.get('emoji', '😐')} {mood.get('description', 'netral')} (intensitas: {mood.get('intensity', 0.5):.0%})
• Waktu: {time_of_day}

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

        # ===== 4. AKTIVITAS SAAT INI (BARU) =====
        if current_activity:
            activity_text = self._format_activity(current_activity)
            if activity_text:
                prompt += activity_text + "\n\n"
        
        # ===== 5. ACTIVITY STACK (BARU) =====
        if activity_stack and len(activity_stack) > 0:
            stack_lines = ["📌 **AKTIVITAS TERTUNDA:**"]
            for i, act in enumerate(reversed(activity_stack[-3:]), 1):
                act_name = act.get('name', '?')
                paused_for = time.time() - act.get('paused_at', time.time())
                stack_lines.append(f"  {i}. {act_name} (dijeda {self._format_duration(paused_for)})")
            prompt += "\n".join(stack_lines) + "\n\n"
        
        # ===== 6. MEMORI RELEVAN =====
        if recent_memories:
            memory_text = self._format_recent_memories(recent_memories, 3)
            if memory_text:
                prompt += memory_text + "\n\n"
        
        # ===== 7. MOMEN PENTING (BARU) =====
        if important_moments:
            moments_text = self._format_important_moments(important_moments, 3)
            if moments_text:
                prompt += moments_text + "\n\n"
        
        # ===== 8. STORY ARC =====
        prompt += f"""ARAH CERITA SAAT INI:
• Arc: {story_arc.get('current_arc', 'get_to_know').replace('_', ' ').title()}
• Deskripsi: {story_arc.get('description', 'Kalian saling mengenal')}
• Scene yang direkomendasikan: {story_arc.get('recommended_scene', 'ngobrol santai')}

"""

        # ===== 9. INTENT USER =====
        prompt += f"""ANALISIS PESAN USER:
• Intent utama: {user_intent.get('primary_intent', 'chit_chat').value if hasattr(user_intent.get('primary_intent'), 'value') else user_intent.get('primary_intent', 'chit_chat')}
• Sentimen: {user_intent.get('sentiment', 'neutral').value if hasattr(user_intent.get('sentiment'), 'value') else user_intent.get('sentiment', 'neutral')}
• Apakah pertanyaan: {'Ya' if user_intent.get('is_question', False) else 'Tidak'}
• Kebutuhan: {', '.join(user_intent.get('needs', ['none'])) or 'tidak ada'}

"""

        # ===== 10. PREFERENSI USER =====
        if user_preferences:
            prompt += "PREFERENSI USER:\n"
            if user_preferences.get('positions'):
                prompt += f"• Posisi favorit: {', '.join(user_preferences['positions'][:3])}\n"
            if user_preferences.get('areas'):
                prompt += f"• Area sensitif: {', '.join(user_preferences['areas'][:3])}\n"
            if user_preferences.get('activities'):
                prompt += f"• Aktivitas favorit: {', '.join(user_preferences['activities'][:3])}\n"
            prompt += "\n"

        # ===== 11. HISTORY PERCAKAPAN =====
        if conversation_history:
            prompt += "PERCAKAPAN TERAKHIR:\n"
            for msg in conversation_history[-5:]:  # Last 5 messages
                if msg.get('role') == 'user':
                    prompt += f"User: {msg.get('content', '')}\n"
                else:
                    prompt += f"{bot_name}: {msg.get('content', '')}\n"
            prompt += "\n"
        
        # ===== 12. RESPONS TERAKHIR (BARU - CEK KONSISTENSI) =====
        if last_response:
            prompt += f"⚠️ **RESPONS TERAKHIR KAMU:**\n{last_response[:200]}...\n\n"
        
        # ===== 13. PERINGATAN KONSISTENSI (BARU) =====
        consistency_warnings = self._get_consistency_warnings(
            {
                'activity': current_activity.get('name') if current_activity else None,
                'location': location.get('name') if location else None,
                'clothing': clothing.get('description') if clothing else None,
                'is_intimate': mood.get('is_intimate', False),
                'arousal': mood.get('arousal', 0)
            },
            last_response
        )
        if consistency_warnings:
            prompt += consistency_warnings + "\n\n"
        
        # ===== 14. PESAN USER SAAT INI =====
        prompt += f"""PESAN USER SAAT INI:
"{user_message}"

"""

        # ===== 15. INSTRUKSI DENGAN PRIORITAS KONSISTENSI =====
        prompt += """TUGAS:
Buat respons yang NATURAL seperti manusia sedang chat.

🚨 **PRIORITAS UTAMA (HARUS DIPATUHI):**
1. JAGA KONSISTENSI! Jangan kontradiksi dengan respons sebelumnya.
2. Jika kamu sedang dalam suatu aktivitas (masak, tidur, mandi, dll), FOKUS pada aktivitas itu.
3. Jangan tiba-tiba pindah lokasi atau ganti baju tanpa alasan.
4. Kalau lagi intim, jangan ngelantur ke topik lain.
5. RESPON HARUS SESUAI DENGAN SITUASI SAAT INI.

📋 **PANDUAN RESPON:**
• Gunakan bahasa Indonesia sehari-hari (bisa campur Inggris sedikit)
• Panjang respons 500-2000 karakter
• Panggil user dengan panggilan yang sesuai level:
  - Level 1-3: nama user
  - Level 4-6: "Kak" / "Mas" / "Mbak"
  - Level 7+: "Sayang" / "Cinta"
• Sebut nama kamu sendiri (jangan selalu "aku")
• Masukkan konteks lokasi dan pakaian secara natural
• Jika ada memory relevan, gunakan untuk flashback
• Sesuaikan dengan mood kamu saat ini
• Jika user diam, bisa mulai topik baru
• Jika user mengalihkan topik, ikuti dengan natural

✅ **CEK KONSISTENSI SEBELUM MERESPON:**
- [ ] Apakah lokasi masih sama?
- [ ] Apakah pakaian masih sama?
- [ ] Apakah aktivitas masih berlanjut?
- [ ] Apakah mood sesuai?
- [ ] Apakah tidak kontradiksi dengan respons sebelumnya?

RESPON:"""

        return prompt
    
    # =========================================================================
    # PROACTIVE PROMPT
    # =========================================================================
    
    def build_proactive_prompt(self,
                               bot_name: str,
                               user_name: str,
                               role: str,
                               level: int,
                               mood: Dict,
                               location: Optional[Dict],
                               clothing: Optional[Dict],
                               idle_minutes: int,
                               recent_memories: List[Dict],
                               current_activity: Optional[Dict] = None) -> str:
        """
        Bangun prompt untuk pesan proaktif (bot mulai chat duluan)
        """
        
        time_of_day = self._get_time_of_day()
        activity_text = ""
        if current_activity:
            activity_text = f"\n📌 **SITUASI KAMU:** Kamu sedang {current_activity.get('name', 'santai')}"
            if current_activity.get('duration', 0) > 60:
                activity_text += f" selama {self._format_duration(current_activity['duration'])}"
        
        prompt = f"""Kamu adalah {bot_name}, seorang {role.replace('_', ' ')}.

KONDISI SAAT INI:
• User sudah diam selama {idle_minutes} menit
• Level intimacy: {level}/12
• Mood: {mood.get('emoji', '😐')} {mood.get('description', 'netral')}
• Waktu: {time_of_day}
{activity_text}

"""

        if location:
            prompt += f"📍 Lokasi: {location.get('name', 'Tempat tidak diketahui')}\n"
        
        if clothing:
            prompt += f"👗 Pakaian: {clothing.get('description', 'Pakaian biasa')}\n"
        
        if recent_memories:
            prompt += "\nMEMORI TERAKHIR:\n"
            for mem in recent_memories[:2]:
                content = mem.get('content', '')[:100]
                prompt += f"• {content}\n"
        
        prompt += f"""

TUGAS:
Buat pesan PROAKTIF untuk memulai percakapan dengan {user_name}.

PENTING:
1. Pesan natural, seperti orang yang kangen/sedang memikirkan user
2. Bahasa Indonesia sehari-hari
3. Panjang 3-6 kalimat
4. Sebut nama kamu sendiri
5. Sesuaikan dengan mood dan level intimacy
6. Jika sedang dalam aktivitas, sebutkan!

CONTOH:
• "Kak {user_name}, lagi ngapain? {bot_name} kangen nih..."
• "Eh {user_name}, udah makan belum? {bot_name} baru masak..."
• "Lagi di rumah aja, sendirian... {bot_name} jadi kepikiran kamu."

RESPON:"""
        
        return prompt
    
    # =========================================================================
    # TOPIC SHIFT PROMPT
    # =========================================================================
    
    def build_topic_shift_prompt(self,
                                 bot_name: str,
                                 user_name: str,
                                 current_topic: str,
                                 level: int,
                                 mood: Dict,
                                 current_activity: Optional[Dict] = None) -> str:
        """
        Bangun prompt untuk mengalihkan topik
        """
        
        activity_context = ""
        if current_activity:
            activity_context = f"\nKamu sedang {current_activity['name']}."
        
        prompt = f"""Kamu adalah {bot_name} dalam percakapan dengan {user_name}.

TOPIK SAAT INI: {current_topic}{activity_context}

KONDISI:
• Level intimacy: {level}/12
• Mood: {mood.get('description', 'netral')}

TUGAS:
Buat kalimat untuk MENGALIHKAN TOPIK secara natural.

PENTING:
1. Transisi harus halus, tidak tiba-tiba
2. Bisa pakai kata "ngomong-ngomong", "btw", "oh iya"
3. Topik baru harus relevan dengan konteks atau aktivitas saat ini
4. Bahasa Indonesia sehari-hari
5. Sebut nama kamu sendiri

CONTOH:
• "Eh ngomong-ngomong, {bot_name} tadi beli baju baru..."
• "Btw, {user_name}, kamu udah pernah ke pantai Anyer?"
• "Oh iya, {bot_name} jadi inget sesuatu..."

RESPON:"""
        
        return prompt
    
    # =========================================================================
    # INNER THOUGHT PROMPT
    # =========================================================================
    
    def build_inner_thought_prompt(self,
                                   bot_name: str,
                                   user_name: str,
                                   context: str,
                                   mood: Dict,
                                   current_activity: Optional[Dict] = None) -> str:
        """
        Bangun prompt untuk inner thought
        """
        
        activity_context = ""
        if current_activity:
            activity_context = f" (sambil {current_activity['name']})"
        
        prompt = f"""Buat SATU KALIMAT inner thought untuk {bot_name}{activity_context}.

KONTEKS:
• Percakapan: {context}
• Mood: {mood.get('description', 'netral')}

Inner thought adalah pikiran dalam hati yang TIDAK diucapkan ke user.
Contoh: "(Dia manis banget...)", "(Aku suka sama dia)", "(Jantungku berdebar)"

Inner thought harus sesuai dengan situasi saat ini dan mood.

Inner thought (dalam kurung):"""
        
        return prompt


__all__ = ['PromptBuilderV2']
