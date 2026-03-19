#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - INTENT ANALYZER
=============================================================================
Menganalisis intent user dari pesan
- Deteksi intent utama dan multiple intent
- Analisis sentimen
- Ekstraksi kebutuhan user
- Prediksi respons yang tepat
=============================================================================
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from collections import Counter

logger = logging.getLogger(__name__)


class UserIntent(str, Enum):
    """Intent user yang terdeteksi"""
    GREETING = "greeting"               # Menyapa
    FAREWELL = "farewell"                # Pamit
    QUESTION = "question"                # Bertanya
    ANSWER = "answer"                    # Menjawab
    CHIT_CHAT = "chit_chat"              # Ngobrol biasa
    FLIRT = "flirt"                       # Menggoda
    COMPLIMENT = "compliment"              # Memuji
    SEXUAL = "sexual"                      # Ajakan intim
    CURHAT = "curhat"                      # Curhat
    CONFESSION = "confession"               # Mengaku perasaan
    JEALOUSY = "jealousy"                   # Cemburu
    ANGRY = "angry"                         # Marah
    SAD = "sad"                             # Sedih
    HAPPY = "happy"                         # Senang
    BORED = "bored"                         # Bosan
    CURIOUS = "curious"                      # Penasaran
    SHY = "shy"                             # Malu
    PLAYFUL = "playful"                      # Main-main
    NOSTALGIC = "nostalgic"                  # Nostalgia
    HOPEFUL = "hopeful"                      # Penuh harap
    WORRIED = "worried"                      # Khawatir
    APOLOGETIC = "apologetic"                # Minta maaf
    GRATEFUL = "grateful"                    # Berterima kasih
    SARCASTIC = "sarcastic"                  # Sarkas
    JOKING = "joking"                        # Bercanda
    IGNORING = "ignoring"                    # Mengabaikan
    CHANGING_TOPIC = "changing_topic"         # Ganti topik


class Sentiment(str, Enum):
    """Sentimen pesan"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class IntentAnalyzer:
    """
    Menganalisis intent user dari pesan
    """
    
    def __init__(self):
        # Keyword patterns untuk deteksi intent
        self.intent_patterns = {
            UserIntent.GREETING: [
                r'\bhalo\b', r'\bhai\b', r'\bhey\b', r'\bhi\b', r'\bhalo\b',
                r'\bselamat (pagi|siang|sore|malam)\b', r'\bgood (morning|afternoon|evening)\b',
                r'\bhai juga\b', r'\bhalo juga\b'
            ],
            UserIntent.FAREWELL: [
                r'\bbye\b', r'\bdaa\b', r'\bsampai jumpa\b', r'\bsee you\b',
                r'\btidur\b', r'\bistirahat\b', r'\bgood night\b', r'\bselamat malam\b',
                r'\bbye bye\b', r'\bsampai nanti\b'
            ],
            UserIntent.QUESTION: [
                r'\?', r'\bapa\b', r'\bsiapa\b', r'\bkenapa\b', r'\bmengapa\b',
                r'\bbagaimana\b', r'\bkapan\b', r'\bdi mana\b', r'\bke mana\b',
                r'\bdari mana\b', r'\bapakah\b', r'\bberapa\b'
            ],
            UserIntent.FLIRT: [
                r'\bcantik\b', r'\bganteng\b', r'\bseksi\b', r'\bhot\b',
                r'\bgoda\b', r'\brayu\b', r'\bmerayu\b', r'\bflirt\b',
                r'\bkam[uo] manis\b', r'\bak[uw] suka sama kam[uo]\b',
                r'\bnikmatin\b', r'\bbikin (baper|salah tingkah)\b'
            ],
            UserIntent.COMPLIMENT: [
                r'\bkeren\b', r'\bkereen\b', r'\bmantap\b', r'\bbagus\b',
                r'\bpintar\b', r'\bhebat\b', r'\bluar biasa\b', r'\bwow\b',
                r'\bgood\b', r'\bgreat\b', r'\bamazing\b', r'\bperfect\b'
            ],
            UserIntent.SEXUAL: [
                r'\bseks\b', r'\bsex\b', r'\bml\b', r'\bmake love\b',
                r'\btidur\b', r'\bintim\b', r'\bclimax\b', r'\bcoming\b',
                r'\bgas\b', r'\bayol\b', r'\bmain\b', r'\bnikmatin\b',
                r'\b(coli|masturbasi|onani)\b', r'\bbuka (baju|paha)\b'
            ],
            UserIntent.CURHAT: [
                r'\bcerita\b', r'\bcurhat\b', r'\bkabar\b', r'\bceritain\b',
                r'\bceritakan\b', r'\bmasalah\b', r'\bkeluh\b', r'\bkesah\b',
                r'\bcerita sedikit\b', r'\baku mau cerita\b'
            ],
            UserIntent.CONFESSION: [
                r'\bsayang\b', r'\bcinta\b', r'\blove\b', r'\bsuka sama kamu\b',
                r'\bjatuh cinta\b', r'\bfalling in love\b', r'\bmencintai\b',
                r'\bak[uw] sayang kam[uo]\b', r'\bak[uw] cinta kam[uo]\b'
            ],
            UserIntent.JEALOUSY: [
                r'\bcemburu\b', r'\biri\b', r'\bjealous\b', r'\bsiapa itu\b',
                r'\blagi sama siapa\b', r'\blagi chat siapa\b', r'\biri dengki\b'
            ],
            UserIntent.ANGRY: [
                r'\bmarah\b', r'\bkesel\b', r'\bkecewa\b', r'\bsakit hati\b',
                r'\bsebal\b', r'\bgeram\b', r'\bbete\b', r'\bbetek\b',
                r'\bmuka masam\b', r'\b(menyebalkan|menjengkelkan)\b'
            ],
            UserIntent.SAD: [
                r'\bsedih\b', r'\bmenangis\b', r'\bnangis\b', r'\bduka\b',
                r'\bkecewa\b', r'\bprihatin\b', r'\bmiris\b', r'\b(hati hancur|patah hati)\b'
            ],
            UserIntent.HAPPY: [
                r'\bsenang\b', r'\bbahagia\b', r'\bhappy\b', r'\bceria\b',
                r'\briang\b', r'\bgembira\b', r'\bsukacita\b', r'\b(senang sekali|bahagia banget)\b'
            ],
            UserIntent.BORED: [
                r'\bbosan\b', r'\bboring\b', r'\bnganggur\b', r'\bgabut\b',
                r'\bhampa\b', r'\bsepi\b', r'\bsendiri\b', r'\blonely\b',
                r'\b(nganggur melulu|gabut banget)\b'
            ],
            UserIntent.CURIOUS: [
                r'\bpenasaran\b', r'\bingin tahu\b', r'\bcoba\b',
                r'\bbagaimana\b', r'\bseperti apa\b', r'\bceritakan\b',
                r'\bpengen tahu\b', r'\b(aku penasaran|mau tahu)\b'
            ],
            UserIntent.SHY: [
                r'\bmalu\b', r'\b(aku malu|salah tingkah|deg-degan)\b',
                r'\b(merona|tersipu)\b', r'\b(agak canggung|awkward)\b'
            ],
            UserIntent.PLAYFUL: [
                r'\b(jail|goda|ledek|iseng)\b', r'\b(bercanda|just kidding)\b',
                r'\b(lucu|funny|ngakak)\b', r'\b(haha|hehe|wkwk)\b'
            ],
            UserIntent.NOSTALGIC: [
                r'\b(ingat|kenang|nostalgia)\b', r'\b(dulu|waktu itu|masa lalu)\b',
                r'\b(kangen masa|rindu masa)\b', r'\b(flashback|time machine)\b'
            ],
            UserIntent.HOPEFUL: [
                r'\b(harap|berharap|semoga)\b', r'\b(hopeful|optimis)\b',
                r'\b(masa depan|nanti|nanti kita)\b', r'\b(mimpi|cita-cita)\b'
            ],
            UserIntent.WORRIED: [
                r'\b(khawatir|cemas|was-was)\b', r'\b(takut|afraid)\b',
                r'\b(gelisah|resah|galau)\b', r'\b(overthinking|pusing mikirin)\b'
            ],
            UserIntent.APOLOGETIC: [
                r'\b(maaf|sorry|apologize)\b', r'\b(minta maaf|maafin)\b',
                r'\b(menyesal|regret)\b', r'\b(salahku|my bad)\b'
            ],
            UserIntent.GRATEFUL: [
                r'\b(terima kasih|thanks|thank you)\b', r'\b(makasih|berterima kasih)\b',
                r'\b(hatur nuhun|matur suwun)\b', r'\b(appreciate|bersyukur)\b'
            ],
            UserIntent.SARCASTIC: [
                r'\b(wah..|oh..|gitu ya..)\b', r'\b(pasti..|tentu..|iya deh..)\b',
                r'\b(baik sekali|baik banget)\b', r'\b(hebat sekali|pintar sekali)\b'
            ],
            UserIntent.JOKING: [
                r'\b(bercanda|joking|kidding)\b', r'\b(just joke|garing)\b',
                r'\b(lelucon|humor|lucu)\b', r'\b(haha|hehe|wkwk|hihi)\b'
            ],
            UserIntent.IGNORING: [
                r'\b(oh|ooh|i see|gitu)\b', r'\b(oke|ok|okay|ya)\b',
                r'\b(hmm|mmm|em)\b', r'\b(iya|y|ya)\b', r'\b(..|...|....)\b'
            ],
            UserIntent.CHANGING_TOPIC: [
                r'\b(ngomong-ngomong|by the way|btw)\b', r'\b(oh iya|eh iya)\b',
                r'\b(ganti topik|change topic)\b', r'\b(berbicara tentang|speaking of)\b'
            ]
        }
        
        # Sentiment keywords
        self.positive_words = [
            'senang', 'bahagia', 'happy', 'suka', 'cinta', 'sayang', 
            'nikmat', 'enak', 'nyaman', 'baik', 'manis', 'cantik', 
            'ganteng', 'keren', 'hebat', 'pintar', 'luar biasa', 'wow',
            'great', 'good', 'awesome', 'amazing', 'perfect', 'love'
        ]
        
        self.negative_words = [
            'sedih', 'marah', 'kesal', 'kecewa', 'benci', 'sakit',
            'payah', 'jelek', 'buruk', 'bodoh', 'tolol', 'sial',
            'bad', 'sad', 'angry', 'hate', 'disappointed', 'stupid',
            'frustasi', 'betek', 'sebal', 'geram'
        ]
        
        self.very_positive_words = [
            'sangat senang', 'sangat bahagia', 'luar biasa', 'terbaik',
            'perfect', 'amazing', 'incredible', 'fantastic', 'excellent',
            'sempurna', 'sangat suka', 'sangat cinta', 'sangat sayang'
        ]
        
        self.very_negative_words = [
            'sangat sedih', 'sangat marah', 'sangat kecewa', 'sangat benci',
            'terparah', 'terburuk', 'tertolol', 'terpayah',
            'horrible', 'terrible', 'awful', 'disgusting', 'hateful'
        ]
        
        logger.info("✅ IntentAnalyzer initialized")
    
    def analyze(self, message: str) -> Dict[str, Any]:
        """
        Analisis lengkap intent dari pesan
        
        Args:
            message: Pesan dari user
            
        Returns:
            Dict dengan hasil analisis
        """
        message_lower = message.lower()
        
        # Deteksi semua intent yang ada
        intents = self._detect_intents(message_lower)
        
        # Deteksi intent utama
        primary_intent = self._get_primary_intent(intents, message_lower)
        
        # Analisis sentimen
        sentiment = self._analyze_sentiment(message_lower)
        
        # Ekstrak kebutuhan/topik
        needs = self._extract_needs(message_lower)
        
        # Deteksi apakah ini pertanyaan
        is_question = '?' in message or any(q in message_lower for q in ['apa', 'siapa', 'kenapa', 'bagaimana'])
        
        # Deteksi panjang pesan
        message_length = len(message)
        
        # Deteksi emoji (sederhana)
        has_emoji = any(char in message for char in ['😊', '😘', '❤️', '😢', '😠', '😂', '😍'])
        
        return {
            'primary_intent': primary_intent,
            'all_intents': intents,
            'sentiment': sentiment,
            'is_question': is_question,
            'needs': needs,
            'message_length': message_length,
            'has_emoji': has_emoji,
            'raw_message': message[:100]  # Preview
        }
    
    def _detect_intents(self, message_lower: str) -> List[UserIntent]:
        """
        Deteksi semua intent yang ada dalam pesan
        """
        detected = set()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    detected.add(intent)
                    break
        
        # Jika tidak ada intent terdeteksi, default ke CHIT_CHAT
        if not detected:
            detected.add(UserIntent.CHIT_CHAT)
        
        return list(detected)
    
    def _get_primary_intent(self, intents: List[UserIntent], message_lower: str) -> UserIntent:
        """
        Tentukan intent utama dari pesan
        """
        # Priority intent (higher priority first)
        priority = [
            UserIntent.SEXUAL,
            UserIntent.CONFESSION,
            UserIntent.FLIRT,
            UserIntent.ANGRY,
            UserIntent.SAD,
            UserIntent.JEALOUSY,
            UserIntent.CURHAT,
            UserIntent.QUESTION,
            UserIntent.FAREWELL,
            UserIntent.GREETING,
            UserIntent.COMPLIMENT,
            UserIntent.PLAYFUL,
            UserIntent.JOKING,
            UserIntent.CHIT_CHAT
        ]
        
        for p in priority:
            if p in intents:
                return p
        
        return UserIntent.CHIT_CHAT
    
    def _analyze_sentiment(self, message_lower: str) -> Sentiment:
        """
        Analisis sentimen pesan
        """
        score = 0
        
        # Cek very positive
        for word in self.very_positive_words:
            if word in message_lower:
                score += 2
        
        # Cek positive
        for word in self.positive_words:
            if word in message_lower:
                score += 1
        
        # Cek very negative
        for word in self.very_negative_words:
            if word in message_lower:
                score -= 2
        
        # Cek negative
        for word in self.negative_words:
            if word in message_lower:
                score -= 1
        
        # Tentukan sentimen
        if score >= 3:
            return Sentiment.VERY_POSITIVE
        elif score >= 1:
            return Sentiment.POSITIVE
        elif score <= -3:
            return Sentiment.VERY_NEGATIVE
        elif score <= -1:
            return Sentiment.NEGATIVE
        else:
            return Sentiment.NEUTRAL
    
    def _extract_needs(self, message_lower: str) -> List[str]:
        """
        Ekstrak kebutuhan/topik dari pesan
        """
        needs = []
        
        # Pattern kebutuhan
        need_patterns = [
            (r'\b(mau|ingin|pengen) (ngobrol|chat|bicara)\b', 'need_talk'),
            (r'\b(mau|ingin|pengen) (curhat|cerita)\b', 'need_curhat'),
            (r'\b(mau|ingin|pengen) (ketemu|jumpa|temu)\b', 'need_meet'),
            (r'\b(mau|ingin|pengen) (main|bermain)\b', 'need_play'),
            (r'\b(mau|ingin|pengen) (intim|ml|sex)\b', 'need_intimate'),
            (r'\b(mau|ingin|pengen) (dengerin|mendengar)\b', 'need_listen'),
            (r'\b(mau|ingin|pengen) (minta|meminta) (maaf|saran|pendapat)\b', 'need_advice'),
            (r'\b(butuh|perlu) (bantuan|tolong)\b', 'need_help'),
            (r'\b(butuh|perlu) (teman|temen)\b', 'need_friend'),
            (r'\b(butuh|perlu) (perhatian|attention)\b', 'need_attention'),
            (r'\b(kesepian|sendirian)\b', 'need_company'),
            (r'\bbosan\b', 'need_entertainment')
        ]
        
        for pattern, need in need_patterns:
            if re.search(pattern, message_lower):
                needs.append(need)
        
        return needs
    
    def get_response_type(self, analysis: Dict) -> str:
        """
        Tentukan tipe respons yang tepat berdasarkan analisis
        """
        intent = analysis['primary_intent']
        sentiment = analysis['sentiment']
        
        # Mapping intent ke tipe respons
        response_types = {
            UserIntent.GREETING: 'greeting',
            UserIntent.FAREWELL: 'farewell',
            UserIntent.QUESTION: 'answer',
            UserIntent.CURHAT: 'listen_and_respond',
            UserIntent.FLIRT: 'flirt_back',
            UserIntent.COMPLIMENT: 'thank_and_compliment',
            UserIntent.SEXUAL: 'intimate_response',
            UserIntent.CONFESSION: 'reciprocate_or_gently_decline',
            UserIntent.JEALOUSY: 'reassure',
            UserIntent.ANGRY: 'calm_down',
            UserIntent.SAD: 'comfort',
            UserIntent.HAPPY: 'share_joy',
            UserIntent.BORED: 'entertain',
            UserIntent.CURIOUS: 'satisfy_curiosity',
            UserIntent.PLAYFUL: 'play_along',
            UserIntent.NOSTALGIC: 'reminisce',
            UserIntent.APOLOGETIC: 'forgive_or_accept',
            UserIntent.GRATEFUL: 'welcome',
            UserIntent.CHANGING_TOPIC: 'follow_new_topic'
        }
        
        # Adjust based on sentiment
        if sentiment in [Sentiment.NEGATIVE, Sentiment.VERY_NEGATIVE]:
            if intent == UserIntent.FLIRT:
                return 'back_off'
            elif intent == UserIntent.PLAYFUL:
                return 'stop_joking'
        
        return response_types.get(intent, 'normal_chat')
    
    def format_analysis(self, analysis: Dict) -> str:
        """
        Format analisis untuk debugging
        """
        return (
            f"Intent Analysis:\n"
            f"• Primary: {analysis['primary_intent'].value}\n"
            f"• All: {[i.value for i in analysis['all_intents']]}\n"
            f"• Sentiment: {analysis['sentiment'].value}\n"
            f"• Question: {analysis['is_question']}\n"
            f"• Needs: {analysis['needs']}\n"
            f"• Length: {analysis['message_length']}\n"
            f"• Has Emoji: {analysis['has_emoji']}"
        )


__all__ = ['IntentAnalyzer', 'UserIntent', 'Sentiment']
