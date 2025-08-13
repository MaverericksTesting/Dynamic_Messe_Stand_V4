#!/usr/bin/env python3
"""
Theme Management für Dynamic Messe Stand V4
Bertrandt Corporate Design mit Dark/Light Mode
"""

class ThemeManager:
    """Verwaltet Farben, Schriftarten und Styles"""
    
    def __init__(self):
        self.dark_mode = False  # Standard: Light Mode
        self.setup_themes()
    
    def setup_themes(self):
        """Initialisiert alle Theme-Definitionen"""
        self.light_theme = {
            'background_primary': '#F5F5F7',     # Apple-ähnliches Hellgrau
            'background_secondary': '#FFFFFF',   # Reines Weiß für Karten
            'background_tertiary': '#F2F2F7',    # Sehr helles Grau (iOS Style)
            'background_hover': '#E5E5EA',       # Sanftes Grau für Hover
            'background_accent': '#003366',      # Bertrandt Blau für Akzente
            'text_primary': '#1D1D1F',          # Apple-ähnliches Schwarz
            'text_secondary': '#86868B',        # Apple Grau für Sekundärtext
            'text_tertiary': '#C7C7CC',         # Helles Grau für Hilfstext
            'text_on_accent': '#FFFFFF',        # Weiß auf Akzentfarben
            'accent_primary': '#003366',        # Bertrandt Corporate Blue
            'accent_secondary': '#FF6600',      # Bertrandt Corporate Orange
            'accent_tertiary': '#34C759',       # Apple Grün für Erfolg
            'accent_warning': '#FF9500',        # Apple Orange für Warnungen
            'accent_destructive': '#FF3B30',    # Apple Rot für Löschaktionen
            'border_light': '#E5E5EA',          # Sehr helle Borders
            'border_medium': '#D1D1D6',         # Mittlere Borders
            'border_accent': '#003366',         # Bertrandt Blau für Akzent-Borders
            'shadow_light': 'rgba(0, 0, 0, 0.04)',  # Sehr sanfte Schatten
            'shadow_medium': 'rgba(0, 0, 0, 0.08)', # Mittlere Schatten
            'shadow_strong': 'rgba(0, 0, 0, 0.15)', # Starke Schatten
            'bertrandt_blue': '#003366',        # Original Bertrandt
            'bertrandt_orange': '#FF6600',      # Original Bertrandt
            'glass_effect': 'rgba(255, 255, 255, 0.8)', # Glasmorphismus
        }
        
        self.dark_theme = {
            'background_primary': '#000000',     # Apple Pure Black
            'background_secondary': '#1C1C1E',   # Apple Dark Card Background
            'background_tertiary': '#2C2C2E',    # Apple Elevated Background
            'background_hover': '#3A3A3C',       # Hover State
            'background_accent': '#0A84FF',      # Apple Blue für Dark Mode
            'text_primary': '#FFFFFF',          # Pure White
            'text_secondary': '#EBEBF5',        # Apple Light Gray
            'text_tertiary': '#8E8E93',         # Apple Medium Gray
            'text_on_accent': '#FFFFFF',        # White on Accent
            'accent_primary': '#0A84FF',        # Apple Blue für Dark Mode
            'accent_secondary': '#FF6600',      # Bertrandt Orange (bleibt)
            'accent_tertiary': '#30D158',       # Apple Green Dark
            'accent_warning': '#FF9F0A',        # Apple Orange Dark
            'accent_destructive': '#FF453A',    # Apple Red Dark
            'border_light': '#38383A',          # Dark Borders
            'border_medium': '#48484A',         # Medium Dark Borders
            'border_accent': '#0A84FF',         # Apple Blue Borders
            'shadow_light': 'rgba(0, 0, 0, 0.2)',
            'shadow_medium': 'rgba(0, 0, 0, 0.3)',
            'shadow_strong': 'rgba(0, 0, 0, 0.5)',
            'bertrandt_blue': '#003366',        # Original Bertrandt
            'bertrandt_orange': '#FF6600',      # Original Bertrandt
            'glass_effect': 'rgba(28, 28, 30, 0.8)', # Dark Glasmorphismus
        }
    
    def get_colors(self):
        """Gibt das aktuelle Farbschema zurück"""
        return self.dark_theme if self.dark_mode else self.light_theme
    
    def get_fonts(self, window_width, window_height):
        """Gibt responsive Schriftarten für 24" 16:9 optimiert zurück"""
        # Optimiert für 24" Screen - größere Schriften für bessere Lesbarkeit
        if window_width >= 2560:
            base_multiplier = 1.15  # 4K/QHD - größer
        elif window_width >= 1920:
            base_multiplier = 1.0   # Full HD - Standard
        else:
            base_multiplier = 0.9   # Fallback - etwas kleiner
        
        return {
            'display': ('Helvetica', int(34 * base_multiplier), 'bold'),    # Display Font
            'title': ('Helvetica', int(28 * base_multiplier), 'bold'),      # Title (bold instead of 600)
            'subtitle': ('Helvetica', int(22 * base_multiplier), 'bold'),   # Subtitle (bold instead of 500)
            'body': ('Helvetica', int(17 * base_multiplier), 'normal'),     # Body text
            'label': ('Helvetica', int(15 * base_multiplier), 'bold'),      # Labels (bold instead of 500)
            'button': ('Helvetica', int(15 * base_multiplier), 'bold'),     # Button Font (bold instead of 600)
            'caption': ('Helvetica', int(13 * base_multiplier), 'normal'),  # Caption
            'nav': ('Helvetica', int(18 * base_multiplier), 'bold'),        # Navigation (bold instead of 600)
            'large_button': ('Helvetica', int(17 * base_multiplier), 'bold'), # Large Buttons (bold instead of 600)
            'monospace': ('Courier', int(14 * base_multiplier), 'normal'),  # Monospace
        }
    
    def toggle_theme(self):
        """Wechselt zwischen Dark und Light Mode"""
        self.dark_mode = not self.dark_mode
        return self.get_colors()

# Globale Theme-Instanz
theme_manager = ThemeManager()