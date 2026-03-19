#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 2 - REAL-TIME CLOCK
=============================================================================
Bot tahu waktu real dan bisa bereaksi:
- Ucapin selamat pagi/siang/malam
- Tahu hari libur
- Tahu musim (hujan/panas)
- Bisa ngajak aktivitas sesuai waktu
=============================================================================
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import calendar

logger = logging.getLogger(__name__)


class RealTimeClock:
    """
    Bot tahu waktu real dan bisa bereaksi sesuai waktu
    - Greetings based on time
    - Holiday awareness
    - Season awareness
    - Time-based suggestions
    """
    
    def __init__(self):
        # Time greetings
        self.greetings = {
            'morning': [
                "Selamat pagi",
                "Pagi",
                "Good morning",
                "Pagi yang cerah"
            ],
            'afternoon': [
                "Selamat siang",
                "Siang",
                "Good afternoon"
            ],
            'evening': [
                "Selamat sore",
                "Sore",
                "Good evening"
            ],
            'night': [
                "Selamat malam",
                "Malam",
                "Good night"
            ],
            'late_night': [
                "Selamat malam",
                "Udah malem",
                "Malam-malam begini"
            ]
        }
        
        # Time-based suggestions
        self.suggestions = {
            'morning': [
                "sarapan dulu yuk",
                "minum kopi",
                "olahraga pagi",
                "jalan pagi"
            ],
            'afternoon': [
                "makan siang",
                "ngopi siang",
                "istirahat bentar"
            ],
            'evening': [
                "jalan sore",
                "ngemil sore",
                "nonton sunset"
            ],
            'night': [
                "makan malam",
                "nonton film",
                "rebahan"
            ],
            'late_night': [
                "tidur",
                "mimpi indah",
                "istirahat"
            ]
        }
        
        # Indonesian holidays (fixed date)
        self.holidays = {
            '01-01': "Tahun Baru",
            '01-01': "Tahun Baru Masehi",
            '01-02': "Tahun Baru",
            '02-08': "Isra Miraj",
            '02-10': "Tahun Baru Imlek",
            '03-11': "Hari Raya Nyepi",
            '03-29': "Wafat Yesus Kristus",
            '04-01': "Hari Paskah",
            '05-01': "Hari Buruh",
            '05-09': "Kenaikan Yesus Kristus",
            '05-20': "Hari Kebangkitan Nasional",
            '06-01': "Hari Lahir Pancasila",
            '06-17': "Idul Adha",
            '07-07': "Tahun Baru Islam",
            '08-17': "Hari Kemerdekaan RI",
            '09-05': "Maulid Nabi Muhammad",
            '12-25': "Hari Raya Natal"
        }
        
        # Seasons in Indonesia
        self.seasons = {
            'rainy': (10, 4),  # Oktober - April
            'dry': (5, 9)      # Mei - September
        }
        
        logger.info("✅ RealTimeClock initialized")
    
    # =========================================================================
    # TIME INFO
    # =========================================================================
    
    def get_current_time(self) -> Dict:
        """
        Dapatkan informasi waktu saat ini
        
        Returns:
            Dict dengan info waktu
        """
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        day = now.day
        month = now.month
        year = now.year
        weekday = now.strftime("%A")
        month_name = now.strftime("%B")
        
        # Tentukan time of day
        if 5 <= hour < 11:
            time_of_day = 'morning'
            time_name = 'pagi'
        elif 11 <= hour < 15:
            time_of_day = 'afternoon'
            time_name = 'siang'
        elif 15 <= hour < 18:
            time_of_day = 'evening'
            time_name = 'sore'
        elif 18 <= hour < 22:
            time_of_day = 'night'
            time_name = 'malam'
        else:
            time_of_day = 'late_night'
            time_name = 'malam'
        
        # Tentukan musim
        if self.seasons['rainy'][0] <= month <= self.seasons['rainy'][1]:
            season = 'rainy'
            season_name = 'musim hujan'
        else:
            season = 'dry'
            season_name = 'musim panas'
        
        return {
            'datetime': now,
            'hour': hour,
            'minute': minute,
            'day': day,
            'month': month,
            'year': year,
            'weekday': weekday,
            'month_name': month_name,
            'time_of_day': time_of_day,
            'time_name': time_name,
            'season': season,
            'season_name': season_name,
            'timestamp': time.time()
        }
    
    def get_time_of_day(self) -> str:
        """Dapatkan waktu dalam string (pagi/siang/sore/malam)"""
        return self.get_current_time()['time_name']
    
    def get_greeting(self) -> str:
        """
        Dapatkan ucapan selamat sesuai waktu
        
        Returns:
            String greeting
        """
        time_info = self.get_current_time()
        time_of_day = time_info['time_of_day']
        
        greetings = self.greetings.get(time_of_day, self.greetings['night'])
        return random.choice(greetings)
    
    def get_personalized_greeting(self, user_name: str) -> str:
        """
        Dapatkan ucapan yang dipersonalisasi
        
        Args:
            user_name: Nama user
            
        Returns:
            String greeting dengan nama
        """
        greeting = self.get_greeting()
        return f"{greeting} {user_name}"
    
    # =========================================================================
    # TIME-BASED SUGGESTIONS
    # =========================================================================
    
    def get_suggestion(self) -> str:
        """
        Dapatkan saran berdasarkan waktu
        
        Returns:
            String saran
        """
        time_info = self.get_current_time()
        time_of_day = time_info['time_of_day']
        
        suggestions = self.suggestions.get(time_of_day, self.suggestions['night'])
        suggestion = random.choice(suggestions)
        
        return suggestion
    
    def get_activity_suggestion(self) -> str:
        """
        Dapatkan saran aktivitas lengkap
        
        Returns:
            String "ayo [saran] yuk"
        """
        suggestion = self.get_suggestion()
        return f"ayo {suggestion} yuk"
    
    # =========================================================================
    # HOLIDAY DETECTION
    # =========================================================================
    
    def get_holiday(self) -> Optional[Dict]:
        """
        Cek apakah hari ini libur
        
        Returns:
            Dict info libur atau None
        """
        now = datetime.now()
        date_key = now.strftime("%m-%d")
        
        if date_key in self.holidays:
            return {
                'name': self.holidays[date_key],
                'date': now.strftime("%d %B %Y")
            }
        
        return None
    
    def is_holiday(self) -> bool:
        """Cek apakah hari ini libur"""
        return self.get_holiday() is not None
    
    def get_holiday_greeting(self) -> Optional[str]:
        """
        Dapatkan ucapan selamat hari libur
        
        Returns:
            String ucapan atau None
        """
        holiday = self.get_holiday()
        if holiday:
            greetings = [
                f"Selamat {holiday['name']} ya",
                f"Happy {holiday['name']}",
                f"Selamat merayakan {holiday['name']}"
            ]
            return random.choice(greetings)
        return None
    
    # =========================================================================
    # SEASON INFO
    # =========================================================================
    
    def get_season(self) -> str:
        """Dapatkan musim saat ini"""
        return self.get_current_time()['season_name']
    
    def get_weather_note(self) -> str:
        """
        Dapatkan catatan tentang cuaca/musim
        
        Returns:
            String catatan
        """
        time_info = self.get_current_time()
        season = time_info['season']
        hour = time_info['hour']
        
        if season == 'rainy':
            notes = [
                "lagi musim hujan nih",
                "hujan terus akhir-akhir ini",
                "jangan lupa bawa payung",
                "enaknya rebahan kalau hujan"
            ]
        else:
            if hour > 14:
                notes = [
                    "panas-panas gini",
                    "gerah banget",
                    "enaknya minum es"
                ]
            else:
                notes = [
                    "cuacanya cerah",
                    "enaknya jalan-jalan",
                    "makan es krim"
                ]
        
        return random.choice(notes)
    
    # =========================================================================
    # TIME-BASED CHECKS
    # =========================================================================
    
    def is_morning(self) -> bool:
        """Cek apakah pagi (5-11)"""
        return 5 <= datetime.now().hour < 11
    
    def is_afternoon(self) -> bool:
        """Cek apakah siang (11-15)"""
        return 11 <= datetime.now().hour < 15
    
    def is_evening(self) -> bool:
        """Cek apakah sore (15-18)"""
        return 15 <= datetime.now().hour < 18
    
    def is_night(self) -> bool:
        """Cek apakah malam (18-22)"""
        return 18 <= datetime.now().hour < 22
    
    def is_late_night(self) -> bool:
        """Cek apakah tengah malam (22-5)"""
        hour = datetime.now().hour
        return hour >= 22 or hour < 5
    
    def is_weekend(self) -> bool:
        """Cek apakah akhir pekan"""
        return datetime.now().weekday() >= 5  # 5=Sabtu, 6=Minggu
    
    def is_weekday(self) -> bool:
        """Cek apakah hari kerja"""
        return datetime.now().weekday() < 5
    
    # =========================================================================
    # TIME FORMATTING
    # =========================================================================
    
    def get_time_string(self, format: str = "%H:%M") -> str:
        """Dapatkan string waktu dengan format tertentu"""
        return datetime.now().strftime(format)
    
    def get_date_string(self, format: str = "%d %B %Y") -> str:
        """Dapatkan string tanggal"""
        return datetime.now().strftime(format)
    
    def get_time_ago(self, timestamp: float) -> str:
        """
        Format waktu yang lalu
        
        Args:
            timestamp: Unix timestamp
            
        Returns:
            String seperti "2 jam lalu"
        """
        diff = time.time() - timestamp
        
        if diff < 60:
            return "baru aja"
        elif diff < 3600:
            minutes = int(diff / 60)
            return f"{minutes} menit lalu"
        elif diff < 86400:
            hours = int(diff / 3600)
            return f"{hours} jam lalu"
        elif diff < 604800:
            days = int(diff / 86400)
            return f"{days} hari lalu"
        else:
            weeks = int(diff / 604800)
            return f"{weeks} minggu lalu"
    
    # =========================================================================
    # FORMAT UNTUK PROMPT
    # =========================================================================
    
    def get_time_context(self) -> str:
        """
        Dapatkan konteks waktu untuk prompt AI
        
        Returns:
            String konteks
        """
        time_info = self.get_current_time()
        holiday = self.get_holiday()
        
        lines = [
            f"🕐 **WAKTU:** {time_info['time_name']}, {time_info['weekday']}, {time_info['day']} {time_info['month_name']} {time_info['year']}",
            f"☀️ **MUSIM:** {time_info['season_name']}"
        ]
        
        if holiday:
            lines.append(f"🎉 **HARI INI:** {holiday['name']}")
        
        return "\n".join(lines)


__all__ = ['RealTimeClock']
