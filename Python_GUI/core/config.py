#!/usr/bin/env python3
"""
Configuration Management für Dynamic Messe Stand V4
Zentrale Konfiguration für alle GUI-Komponenten
"""

import os

class Config:
    """Zentrale Konfigurationsklasse"""
    
    def __init__(self):
        # Basis-Pfade
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.content_dir = os.path.join(self.base_dir, "content")
        
        # Hardware-Konfiguration
        self.hardware = {
            'esp32_1_port': '/dev/ttyUSB0',  # Haupt-ESP32
            'esp32_2_port': '/dev/ttyUSB1',  # ESP32.2 (Addon)
            'esp32_3_port': '/dev/ttyUSB2',  # ESP32.3 (Addon)
            'giga_port': '/dev/ttyACM0',     # Arduino GIGA
            'baud_rate': 115200,
            'timeout': 1
        }
        
        # GUI-Konfiguration
        self.gui = {
            'title': "Dynamic Messe Stand V4 - Bertrandt ESP32 Monitor",
            'min_width': 1280,
            'min_height': 720,
            'fullscreen_on_start': True,
            'responsive_scaling': True,
            'force_fullscreen': True
        }
        
        # Design-Konfiguration
        self.design = {
            'corporate_blue': '#003366',
            'corporate_orange': '#FF6600',
            'scale_factor_base': 1080  # Basis für responsive Design
        }
        
        # Content-Konfiguration
        self.content = {
            'slides_per_page': 10,
            'auto_save_interval': 30,  # Sekunden
            'demo_slide_duration': 5   # Sekunden
        }

# Globale Konfigurationsinstanz
config = Config()