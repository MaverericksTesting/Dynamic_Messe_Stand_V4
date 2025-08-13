# core/config.py
"""
Zentrale Konfiguration für Dynamic Messe Stand V3
"""
import os
from pathlib import Path
from typing import Dict, Any

class Config:
    """Zentrale Konfigurationsklasse"""
    
    # Projekt-Info
    PROJECT_NAME = "Dynamic Messe Stand V3"
    PROJECT_VERSION = "3.0.0"
    PROJECT_TAGLINE = "Interactive Exhibition System"
    
    # Pfade
    BASE_DIR = Path(__file__).parent.parent
    CONTENT_DIR = BASE_DIR / "content"
    ASSETS_DIR = BASE_DIR / "assets"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Hardware-Konfiguration
    ESP32_1_PORT = "/dev/ttyUSB0"  # Haupt-ESP32
    ESP32_2_PORT = "/dev/ttyUSB1"  # ESP32.2 (Addon)
    ESP32_3_PORT = "/dev/ttyUSB2"  # ESP32.3 (Addon)
    GIGA_PORT = "/dev/ttyACM0"     # Arduino GIGA
    BAUD_RATE = 115200
    
    # GUI-Konfiguration
    WINDOW_TITLE = f"{PROJECT_NAME} - Bertrandt ESP32 Monitor"
    MIN_WINDOW_SIZE = (1280, 720)
    SUPPORTED_RESOLUTIONS = [
        (1280, 720),
        (1366, 768),
        (1600, 900),
        (1920, 1080)
    ]
    
    # Dark Mode Theme
    COLORS = {
        'background_primary': '#1E1E1E',     # Dunkler Haupthintergrund
        'background_secondary': '#2D2D2D',   # Sekundär-Hintergrund
        'background_tertiary': '#3A3A3A',    # Karten/Widgets
        'background_hover': '#404040',       # Hover-Zustand
        'text_primary': '#FFFFFF',           # Haupt-Text (weiß)
        'text_secondary': '#CCCCCC',         # Sekundär-Text
        'text_tertiary': '#999999',          # Tertiär-Text
        'accent_primary': '#003366',         # Bertrandt Corporate Blue
        'accent_secondary': '#FF6600',       # Bertrandt Corporate Orange
        'accent_tertiary': '#DC3545',        # Rot für Warnungen
        'accent_warning': '#FFC107',         # Gelb für Warnungen
        'border_light': '#404040',           # Helle Rahmen
        'border_medium': '#555555',          # Mittlere Rahmen
        'shadow': 'rgba(0, 0, 0, 0.3)',      # Dunkle Schatten
        'bertrandt_blue': '#003366',         # Bertrandt Corporate Blue
        'bertrandt_orange': '#FF6600',       # Bertrandt Corporate Orange
    }
    
    # Folien-Definitionen
    SLIDES = {
        1: {'name': 'Folie1', 'icon': '🏠', 'content_type': 'welcome'},
        2: {'name': 'Folie2', 'icon': '🏢', 'content_type': 'company'},
        3: {'name': 'Folie3', 'icon': '⚙️', 'content_type': 'products'},
        4: {'name': 'Folie4', 'icon': '💡', 'content_type': 'innovation'},
        5: {'name': 'Folie5', 'icon': '🔬', 'content_type': 'technology'},
        6: {'name': 'Folie6', 'icon': '⭐', 'content_type': 'references'},
        7: {'name': 'Folie7', 'icon': '👥', 'content_type': 'team'},
        8: {'name': 'Folie8', 'icon': '🚀', 'content_type': 'career'},
        9: {'name': 'Folie9', 'icon': '📞', 'content_type': 'contact'},
        10: {'name': 'Folie10', 'icon': '🙏', 'content_type': 'thanks'}
    }
    
    # Demo-Konfiguration
    AUTO_DEMO_INTERVAL = 5000  # 5 Sekunden pro Folie
    
    # Feature-Flags
    ENABLE_DEV_MODE = True
    ENABLE_HARDWARE_FLASH = True
    ENABLE_MULTI_ESP32 = True
    
    @classmethod
    def ensure_directories(cls):
        """Erstelle notwendige Verzeichnisse"""
        for dir_path in [cls.CONTENT_DIR, cls.ASSETS_DIR, cls.LOGS_DIR]:
            dir_path.mkdir(exist_ok=True)
    
    @classmethod
    def get_slide_color(cls, slide_id: int) -> str:
        """Farbe für Folie basierend auf ID"""
        colors = [
            cls.COLORS['accent_secondary'],
            cls.COLORS['bertrandt_blue'],
            cls.COLORS['bertrandt_orange'],
            cls.COLORS['accent_primary'],
        ]
        return colors[slide_id % len(colors)]

# Globale Config-Instanz
config = Config()