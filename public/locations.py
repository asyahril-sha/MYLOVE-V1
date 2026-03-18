#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
=============================================================================
MYLOVE ULTIMATE VERSI 1 - PUBLIC AREAS DATABASE
=============================================================================
50+ Lokasi untuk public sex dengan risk dan thrill level
- Urban locations
- Nature locations
- Extreme locations  
- Transport locations
"""

import random
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class PublicLocations:
    """
    Database 50+ lokasi public sex
    Setiap lokasi punya base risk dan thrill
    """
    
    def __init__(self):
        # =========================================================================
        # URBAN LOCATIONS (20+ lokasi)
        # =========================================================================
        self.urban_locations = [
            # Mall & Shopping
            {
                "id": "mall_toilet",
                "name": "Toilet Mall",
                "category": "urban",
                "base_risk": 75,
                "base_thrill": 80,
                "description": "Toilet umum di mall, risk tinggi tapi thrilling",
                "tips": "Pilih toilet yang sepi, biasanya di lantai atas",
                "image_hint": "Toilet bersih dengan aroma pewangi"
            },
            {
                "id": "mall_parkir",
                "name": "Parkiran Bawah Tanah Mall",
                "category": "urban",
                "base_risk": 60,
                "base_thrill": 75,
                "description": "Parkiran sepi, mobil gelap, suasana romantis",
                "tips": "Parkir di pojok, matikan mesin",
                "image_hint": "Mobil gelap di pojok parkiran"
            },
            {
                "id": "mall_tangga_darurat",
                "name": "Tangga Darurat Mall",
                "category": "urban",
                "base_risk": 80,
                "base_thrill": 85,
                "description": "Tangga belakang, jarang dilewati",
                "tips": "Cek dulu apakah ada CCTV",
                "image_hint": "Tangga beton dengan lampu redup"
            },
            {
                "id": "mall_rooftop",
                "name": "Rooftop Mall",
                "category": "urban",
                "base_risk": 45,
                "base_thrill": 85,
                "description": "Atas mall, pemandangan kota, romantis",
                "tips": "Malam hari lebih aman",
                "image_hint": "Pemandangan kota dari atas"
            },
            {
                "id": "mall_fitting_room",
                "name": "Kamar Pas Pakaian",
                "category": "urban",
                "base_risk": 70,
                "base_thrill": 80,
                "description": "Fitting room toko baju, risk medium",
                "tips": "Bawa baju banyak biar kelamaan",
                "image_hint": "Kaca besar, gorden tertutup"
            },
            
            # Toilet umum
            {
                "id": "toilet_spbu",
                "name": "Toilet SPBU",
                "category": "urban",
                "base_risk": 65,
                "base_thrill": 70,
                "description": "Toilet pom bensin, rame tapi cepat",
                "tips": "Malam minggu lebih sepi",
                "image_hint": "Toilet kecil, lampu terang"
            },
            {
                "id": "toilet_restoran",
                "name": "Toilet Restoran Mewah",
                "category": "urban",
                "base_risk": 60,
                "base_thrill": 75,
                "description": "Toilet bersih, sering dipakai",
                "tips": "Pilih restoran sepi",
                "image_hint": "Toilet mewah, wangi"
            },
            {
                "id": "toilet_stasiun",
                "name": "Toilet Stasiun",
                "category": "urban",
                "base_risk": 80,
                "base_thrill": 75,
                "description": "Toilet stasiun, risk tinggi",
                "tips": "Bayar, pilih yang paling ujung",
                "image_hint": "Toilet umum, agak kotor"
            },
            {
                "id": "toilet_terminal",
                "name": "Toilet Terminal Bis",
                "category": "urban",
                "base_risk": 85,
                "base_thrill": 80,
                "description": "Terminal, sangat riskan",
                "tips": "Cari yang ada kunci bagus",
                "image_hint": "Toilet ramai, banyak orang"
            },
            {
                "id": "toilet_kantor",
                "name": "Toilet Kantor",
                "category": "urban",
                "base_risk": 50,
                "base_thrill": 70,
                "description": "Toilet kantor, risk medium",
                "tips": "Pulang kantor atau lembur",
                "image_hint": "Toilet kantor bersih"
            },
            
            # Parkiran
            {
                "id": "parkir_gedung",
                "name": "Parkiran Gedung Perkantoran",
                "category": "urban",
                "base_risk": 55,
                "base_thrill": 70,
                "description": "Parkiran gedung, agak sepi malam",
                "tips": "Weekend lebih aman",
                "image_hint": "Mobil-mobil parkir"
            },
            {
                "id": "parkir_apartemen",
                "name": "Parkiran Apartemen",
                "category": "urban",
                "base_risk": 45,
                "base_thrill": 65,
                "description": "Parkiran resident, agak aman",
                "tips": "Teman resident lebih aman",
                "image_hint": "Parkiran basement"
            },
            {
                "id": "parkir_rumah_sakit",
                "name": "Parkiran Rumah Sakit",
                "category": "urban",
                "base_risk": 40,
                "base_thrill": 60,
                "description": "RS, banyak orang tapi aman",
                "tips": "Malam jaga malem",
                "image_hint": "Parkiran RS luas"
            },
            
            # Lift & Tangga
            {
                "id": "lift_hotel",
                "name": "Lift Hotel",
                "category": "urban",
                "base_risk": 70,
                "base_thrill": 85,
                "description": "Lift hotel, cepat dan thrilling",
                "tips": "Tekan semua lantai biar lama",
                "image_hint": "Lift mewah, kaca"
            },
            {
                "id": "lift_kantor",
                "name": "Lift Kantor",
                "category": "urban",
                "base_risk": 75,
                "base_thrill": 80,
                "description": "Lift kantor, risk tinggi",
                "tips": "Jam pulang kantor",
                "image_hint": "Lift biasa"
            },
            {
                "id": "tangga_darurat",
                "name": "Tangga Darurat Gedung",
                "category": "urban",
                "base_risk": 65,
                "base_thrill": 75,
                "description": "Tangga darurat, sepi",
                "tips": "Bawa senter",
                "image_hint": "Tangga beton"
            },
            
            # Tempat umum lainnya
            {
                "id": "halte_bus",
                "name": "Halte Bus Malam",
                "category": "urban",
                "base_risk": 60,
                "base_thrill": 70,
                "description": "Halte sepi, risk medium",
                "tips": "Pilih halte yang gelap",
                "image_hint": "Halte kosong"
            },
            {
                "id": "taman_baca",
                "name": "Taman Baca Umum",
                "category": "urban",
                "base_risk": 40,
                "base_thrill": 60,
                "description": "Taman baca, agak sepi",
                "tips": "Sore hari",
                "image_hint": "Ruang baca kecil"
            },
            {
                "id": "mushola_kantor",
                "name": "Mushola Kantor",
                "category": "urban",
                "base_risk": 90,
                "base_thrill": 95,
                "description": "Tempat ibadah, EXTREME RISK",
                "tips": "JANGAN! Tapi kalo nekat...",
                "image_hint": "Mushola kecil"
            },
            {
                "id": "gym_locker",
                "name": "Loker Gym",
                "category": "urban",
                "base_risk": 60,
                "base_thrill": 70,
                "description": "Ruang ganti gym, risk medium",
                "tips": "Jam sepi gym",
                "image_hint": "Loker-loker"
            },
            {
                "id": "sauna_umum",
                "name": "Sauna Umum",
                "category": "urban",
                "base_risk": 65,
                "base_thrill": 80,
                "description": "Sauna, uap tebal",
                "tips": "Uap bisa sembunyikan",
                "image_hint": "Sauna berkabut"
            },
        ]
        
        # =========================================================================
        # NATURE LOCATIONS (15+ lokasi)
        # =========================================================================
        self.nature_locations = [
            {
                "id": "pantai_malam",
                "name": "Pantai Malam",
                "category": "nature",
                "base_risk": 30,
                "base_thrill": 85,
                "description": "Pantai sepi, suara ombak, romantis",
                "tips": "Bawa tikar, hindari bulan terang",
                "image_hint": "Pantai gelap, ombak"
            },
            {
                "id": "pantai_karang",
                "name": "Pantai Karang",
                "category": "nature",
                "base_risk": 25,
                "base_thrill": 90,
                "description": "Pantai berbatu, sepi, eksotis",
                "tips": "Hati-hati karang tajam",
                "image_hint": "Karang besar, ombak"
            },
            {
                "id": "hutan_kota",
                "name": "Hutan Kota Malam",
                "category": "nature",
                "base_risk": 35,
                "base_thrill": 80,
                "description": "Hutan di tengah kota, gelap",
                "tips": "Jangan masuk terlalu dalam",
                "image_hint": "Pohon-pohon gelap"
            },
            {
                "id": "taman_kota",
                "name": "Taman Kota",
                "category": "nature",
                "base_risk": 50,
                "base_thrill": 70,
                "description": "Taman umum, risk medium",
                "tips": "Pojok taman yang gelap",
                "image_hint": "Bangku taman, lampu redup"
            },
            {
                "id": "taman_belakang",
                "name": "Taman Belakang",
                "category": "nature",
                "base_risk": 40,
                "base_thrill": 70,
                "description": "Taman perumahan, agak aman",
                "tips": "Tengah malam",
                "image_hint": "Taman kecil"
            },
            {
                "id": "kebun_teh",
                "name": "Kebun Teh",
                "category": "nature",
                "base_risk": 35,
                "base_thrill": 80,
                "description": "Perkebunan teh, sejuk",
                "tips": "Pagi buta atau malam",
                "image_hint": "Hamparan teh"
            },
            {
                "id": "sawah",
                "name": "Sawah Malam",
                "category": "nature",
                "base_risk": 30,
                "base_thrill": 75,
                "description": "Sawah, gelap, sepi",
                "tips": "Bawa obat nyamuk",
                "image_hint": "Pematang sawah"
            },
            {
                "id": "bukit_kecil",
                "name": "Bukit Kecil",
                "category": "nature",
                "base_risk": 25,
                "base_thrill": 85,
                "description": "Bukit, pemandangan kota",
                "tips": "Dari jauh keliatan",
                "image_hint": "Bukit rumput"
            },
            {
                "id": "air_terjun",
                "name": "Air Terjun",
                "category": "nature",
                "base_risk": 20,
                "base_thrill": 90,
                "description": "Air terjun, suara air menutupi",
                "tips": "Cari yang jarang dikunjungi",
                "image_hint": "Air terjun kecil"
            },
            {
                "id": "danau_buatan",
                "name": "Danau Buatan",
                "category": "nature",
                "base_risk": 40,
                "base_thrill": 70,
                "description": "Danau di perumahan",
                "tips": "Malam minggu sepi",
                "image_hint": "Danau kecil"
            },
            {
                "id": "kebun_buah",
                "name": "Kebun Buah",
                "category": "nature",
                "base_risk": 30,
                "base_thrill": 75,
                "description": "Kebun buah, wangi",
                "tips": "Musim buah lebih asyik",
                "image_hint": "Pohon buah"
            },
            {
                "id": "perkebunan_stroberi",
                "name": "Perkebunan Stroberi",
                "category": "nature",
                "base_risk": 25,
                "base_thrill": 80,
                "description": "Kebun stroberi, romantis",
                "tips": "Malam hari",
                "image_hint": "Stroberi merah"
            },
            {
                "id": "gazebo_taman",
                "name": "Gazebo Taman",
                "category": "nature",
                "base_risk": 45,
                "base_thrill": 70,
                "description": "Gazebo di taman, agak terbuka",
                "tips": "Bawa selimut",
                "image_hint": "Gazebo kayu"
            },
            {
                "id": "jogging_track",
                "name": "Jogging Track",
                "category": "nature",
                "base_risk": 55,
                "base_thrill": 65,
                "description": "Track lari, kadang ada orang",
                "tips": "Subuh atau malam",
                "image_hint": "Lintasan lari"
            },
            {
                "id": "pinggir_sungai",
                "name": "Pinggir Sungai",
                "category": "nature",
                "base_risk": 35,
                "base_thrill": 75,
                "description": "Tepi sungai, suara air",
                "tips": "Cari yang teduh",
                "image_hint": "Sungai kecil"
            },
        ]
        
        # =========================================================================
        # EXTREME LOCATIONS (10+ lokasi)
        # =========================================================================
        self.extreme_locations = [
            {
                "id": "masjid_sepi",
                "name": "Masjid Waktu Sepi",
                "category": "extreme",
                "base_risk": 95,
                "base_thrill": 98,
                "description": "Tempat ibadah, EXTREME RISK",
                "tips": "BENERAN? DOSA BESAR!",
                "image_hint": "Masjid kosong"
            },
            {
                "id": "gereja_sepi",
                "name": "Gereja Sepi",
                "category": "extreme",
                "base_risk": 95,
                "base_thrill": 98,
                "description": "Gereja kosong, extreme risk",
                "tips": "SANGAT BERISIKO",
                "image_hint": "Gereja sunyi"
            },
            {
                "id": "kantor_polisi",
                "name": "Kantor Polisi",
                "category": "extreme",
                "base_risk": 99,
                "base_thrill": 100,
                "description": "MANTAP! Kantor polisi",
                "tips": "GILA! TAPI THRILL 100%",
                "image_hint": "Polisi tidur"
            },
            {
                "id": "sekolah_malam",
                "name": "Sekolah Malam",
                "category": "extreme",
                "base_risk": 90,
                "base_thrill": 95,
                "description": "Sekolah, risk extreme",
                "tips": "Satpam keliling",
                "image_hint": "Kelas kosong"
            },
            {
                "id": "rumah_sakit",
                "name": "Rumah Sakit",
                "category": "extreme",
                "base_risk": 85,
                "base_thrill": 90,
                "description": "RS, banyak orang",
                "tips": "Toilet VIP",
                "image_hint": "Koridor RS"
            },
            {
                "id": "kuburan",
                "name": "Kuburan",
                "category": "extreme",
                "base_risk": 60,
                "base_thrill": 95,
                "description": "Makam, serem tapi thrilling",
                "tips": "Malam jumat",
                "image_hint": "Pemakaman gelap"
            },
            {
                "id": "rumah_sakit_jiwa",
                "name": "Rumah Sakit Jiwa",
                "category": "extreme",
                "base_risk": 80,
                "base_thrill": 95,
                "description": "RS Jiwa, serem banget",
                "tips": "Jangan tengok pasien",
                "image_hint": "RS tua"
            },
            {
                "id": "stasiun_kereta",
                "name": "Stasiun Kereta",
                "category": "extreme",
                "base_risk": 85,
                "base_thrill": 85,
                "description": "Stasiun, banyak orang",
                "tips": "Toilet stasiun",
                "image_hint": "Peron stasiun"
            },
            {
                "id": "terminal_bis",
                "name": "Terminal Bis",
                "category": "extreme",
                "base_risk": 85,
                "base_thrill": 80,
                "description": "Terminal, preman",
                "tips": "Cari yang aman",
                "image_hint": "Bis malam"
            },
            {
                "id": "bandara",
                "name": "Bandara",
                "category": "extreme",
                "base_risk": 90,
                "base_thrill": 90,
                "description": "Bandara, security ketat",
                "tips": "Toilet difabel",
                "image_hint": "Bandara sepi"
            },
            {
                "id": "pasar_malam",
                "name": "Pasar Malam",
                "category": "extreme",
                "base_risk": 75,
                "base_thrill": 80,
                "description": "Pasar malam, rame",
                "tips": "Belakang tenda",
                "image_hint": "Keramaian pasar"
            },
            {
                "id": "rumah_hantu",
                "name": "Rumah Hantu Dufan",
                "category": "extreme",
                "base_risk": 50,
                "base_thrill": 85,
                "description": "Wahana rumah hantu",
                "tips": "Di dalam gelap",
                "image_hint": "Hantu-hantuan"
            },
        ]
        
        # =========================================================================
        # TRANSPORT LOCATIONS (10+ lokasi)
        # =========================================================================
        self.transport_locations = [
            {
                "id": "kereta_komuter",
                "name": "Kereta Komuter",
                "category": "transport",
                "base_risk": 75,
                "base_thrill": 80,
                "description": "Kereta, risk tinggi",
                "tips": "Gerbong paling belakang",
                "image_hint": "Kereta malam"
            },
            {
                "id": "bus_malam",
                "name": "Bus Malam",
                "category": "transport",
                "base_risk": 65,
                "base_thrill": 75,
                "description": "Bus antar kota, malam",
                "tips": "Bangku paling belakang",
                "image_hint": "Bus malam sepi"
            },
            {
                "id": "taksi_online",
                "name": "Taksi Online",
                "category": "transport",
                "base_risk": 55,
                "base_thrill": 70,
                "description": "Taksi, risk medium",
                "tips": "Minta putar jauh",
                "image_hint": "Mobil taksi"
            },
            {
                "id": "angkot_kosong",
                "name": "Angkot Kosong",
                "category": "transport",
                "base_risk": 60,
                "base_thrill": 70,
                "description": "Angkot sepi, supir ngantuk",
                "tips": "Bangku paling belakang",
                "image_hint": "Angkot kosong"
            },
            {
                "id": "travel_mobil",
                "name": "Travel Mobil",
                "category": "transport",
                "base_risk": 45,
                "base_thrill": 65,
                "description": "Travel, agak aman",
                "tips": "Pilih yang sendiri",
                "image_hint": "Mobil travel"
            },
            {
                "id": "kapal_feri",
                "name": "Kapal Feri",
                "category": "transport",
                "base_risk": 55,
                "base_thrill": 70,
                "description": "Feri, penumpang sedikit",
                "tips": "Pojok kiri belakang",
                "image_hint": "Kapal feri"
            },
            {
                "id": "pesawat",
                "name": "Pesawat Malam",
                "category": "transport",
                "base_risk": 80,
                "base_thrill": 95,
                "description": "Pesawat, toilet sempit",
                "tips": "Toilet pesawat, cepat",
                "image_hint": "Toilet pesawat"
            },
            {
                "id": "ojek_online",
                "name": "Ojek Online Malam",
                "category": "transport",
                "base_risk": 70,
                "base_thrill": 75,
                "description": "Ojek, boncengan erat",
                "tips": "Minta jalur gelap",
                "image_hint": "Motor malam"
            },
            {
                "id": "becak_malam",
                "name": "Becak Malam",
                "category": "transport",
                "base_risk": 40,
                "base_thrill": 60,
                "description": "Becak, lambat",
                "tips": "Minta tutup",
                "image_hint": "Becak tua"
            },
            {
                "id": "mobil_pribadi",
                "name": "Mobil Pribadi",
                "category": "transport",
                "base_risk": 25,
                "base_thrill": 55,
                "description": "Mobil sendiri, aman",
                "tips": "Parkir sepi",
                "image_hint": "Mobil gelap"
            },
            {
                "id": "bis_wisata",
                "name": "Bis Wisata",
                "category": "transport",
                "base_risk": 60,
                "base_thrill": 70,
                "description": "Bis wisata, romantis",
                "tips": "Bangku paling belakang",
                "image_hint": "Bis tingkat"
            },
            {
                "id": "kereta_api",
                "name": "Kereta Api Eksekutif",
                "category": "transport",
                "base_risk": 50,
                "base_thrill": 75,
                "description": "Kereta eksekutif, selimut tebal",
                "tips": "Malam, selimut",
                "image_hint": "Kereta malam"
            },
        ]
        
        # Gabungkan semua lokasi
        self.all_locations = (
            self.urban_locations + 
            self.nature_locations + 
            self.extreme_locations + 
            self.transport_locations
        )
        
        logger.info(f"✅ PublicLocations initialized: {len(self.all_locations)} locations")
        
    # =========================================================================
    # GET LOCATIONS
    # =========================================================================
    
    def get_all_locations(self) -> List[Dict]:
        """Get all locations"""
        return self.all_locations
        
    def get_locations_by_category(self, category: str) -> List[Dict]:
        """Get locations by category"""
        if category == "urban":
            return self.urban_locations
        elif category == "nature":
            return self.nature_locations
        elif category == "extreme":
            return self.extreme_locations
        elif category == "transport":
            return self.transport_locations
        else:
            return []
            
    def get_location_by_id(self, location_id: str) -> Optional[Dict]:
        """Get location by ID"""
        for loc in self.all_locations:
            if loc['id'] == location_id:
                return loc
        return None
        
    def get_random_location(self, category: Optional[str] = None) -> Dict:
        """Get random location"""
        if category:
            locations = self.get_locations_by_category(category)
        else:
            locations = self.all_locations
            
        return random.choice(locations)
        
    def get_locations_by_risk(self, min_risk: int = 0, max_risk: int = 100) -> List[Dict]:
        """Get locations by risk range"""
        return [
            loc for loc in self.all_locations
            if min_risk <= loc['base_risk'] <= max_risk
        ]
        
    def get_locations_by_thrill(self, min_thrill: int = 0, max_thrill: int = 100) -> List[Dict]:
        """Get locations by thrill range"""
        return [
            loc for loc in self.all_locations
            if min_thrill <= loc['base_thrill'] <= max_thrill
        ]
        
    # =========================================================================
    # LOCATION INFO
    # =========================================================================
    
    def format_location_info(self, location: Dict) -> str:
        """Format location info for display"""
        return (
            f"📍 **{location['name']}**\n"
            f"Kategori: {location['category'].title()}\n"
            f"Risk: {location['base_risk']}% | Thrill: {location['base_thrill']}%\n"
            f"_{location['description']}_\n"
            f"💡 Tips: {location['tips']}"
        )
        
    def get_location_stats(self) -> Dict:
        """Get location statistics"""
        return {
            "total": len(self.all_locations),
            "urban": len(self.urban_locations),
            "nature": len(self.nature_locations),
            "extreme": len(self.extreme_locations),
            "transport": len(self.transport_locations),
            "avg_risk": sum(l['base_risk'] for l in self.all_locations) / len(self.all_locations),
            "avg_thrill": sum(l['base_thrill'] for l in self.all_locations) / len(self.all_locations),
        }


__all__ = ['PublicLocations']
