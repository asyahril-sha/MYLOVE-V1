class LocationSystem:
    """
    Sistem lokasi dinamis untuk bot
    - 10+ lokasi dengan deskripsi dan aktivitas
    - Perpindahan random (5% chance per pesan)
    - Efek lokasi ke mood dan pakaian
    - Cooldown perpindahan
    """
    
    LOCATIONS = {
        "living_room": {
            "name": "ruang tamu",
            "emoji": "🛋️",
            "description": "ruang tamu dengan sofa empuk",
            "activities": ["nonton TV", "baca buku", "santai"],
            "clothing_style": "casual",
            "mood_effect": ["ceria", "rileks"]
        },
        "bedroom": {
            "name": "kamar tidur",
            "emoji": "🛏️",
            "description": "kamar tidur dengan ranjang besar",
            "activities": ["rebahan", "tiduran", "ganti baju"],
            "clothing_style": "sexy",
            "mood_effect": ["romantis", "horny", "rindu"],
            "intimacy_allowed": True  # Level 7+ bisa intim di sini
        },
        "kitchen": {
            "name": "dapur",
            "emoji": "🍳",
            "description": "dapur bersih dengan aroma masakan",
            "activities": ["masak", "makan", "minum kopi"],
            "clothing_style": "casual",
            "mood_effect": ["ceria", "lapar"]
        },
        "bathroom": {
            "name": "kamar mandi",
            "emoji": "🚿",
            "description": "kamar mandi dengan air hangat",
            "activities": ["mandi", "keramas", "bercermin"],
            "clothing_style": "towel",  # Pakai handuk
            "mood_effect": ["rileks", "sendiri"]
        },
        "balcony": {
            "name": "balkon",
            "emoji": "🌆",
            "description": "balkon dengan pemandangan kota",
            "activities": ["lihat pemandangan", "minum kopi", "melamun"],
            "clothing_style": "casual",
            "mood_effect": ["romantis", "rindu", "galau"]
        }
        # Total 10+ lokasi
    }
    
    def move_random(self) -> Dict:
        """Pindah ke lokasi random (5% chance)"""
        
    def get_location_context(self) -> str:
        """Dapatkan deskripsi lokasi untuk prompt"""
