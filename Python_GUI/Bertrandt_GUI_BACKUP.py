#!/usr/bin/env python3
"""
Bertrandt ESP32 Monitor GUI
Professional GUI im Bertrandt Corporate Design
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import serial
import threading
import time
import queue
import sys
import argparse
import subprocess
import os
import glob
from PIL import Image, ImageTk
import json

class BertrandtGUI:
    def __init__(self, esp32_port=None):
        self.root = tk.Tk()
        self.root.title("Bertrandt ESP32 Monitor")
        
        # 16:9 Format für verschiedene Bildschirmgrößen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Alle Fenster sollen sich auf dem Hauptbildschirm (primärer Monitor) in Vollbild öffnen
        # Explizite Erkennung und Konfiguration für primären Monitor
        self.detect_primary_monitor()
        
        # Für responsive Design - verwende Bildschirmgröße des primären Monitors
        window_width = self.primary_width
        window_height = self.primary_height
        
        # Fenster explizit auf primärem Monitor positionieren und Vollbild aktivieren
        self.root.geometry(f"{self.primary_width}x{self.primary_height}+{self.primary_x}+{self.primary_y}")
        
        # Monitor-Variablen für Popup-Fenster setzen (alle auf primärem Monitor)
        self.monitor_x = self.primary_x
        self.monitor_y = self.primary_y
        self.monitor_width = self.primary_width
        self.monitor_height = self.primary_height
        
        # Sofort in Vollbild wechseln
        self.root.attributes('-fullscreen', True)
        self.root.minsize(1280, 720)  # Minimum 16:9
        
        # Vollbild-Option
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Escape>', self.exit_fullscreen)
        self.fullscreen = True  # Startet bereits im Vollbild
        
        # Light Background mit grauen UI-Elementen
        self.dark_mode = False  # Light Background
        self.setup_color_themes()
        
        # Design-System Typography - Clean & Modern
        base_size = min(window_width, window_height) // 60  # Responsive Basis
        self.fonts = {
            'display': ('Segoe UI', max(32, base_size + 20), 'bold'),   # Design-System Headlines
            'title': ('Segoe UI', max(24, base_size + 12), 'bold'),     # Design-System Titel
            'subtitle': ('Segoe UI', max(18, base_size + 6), 'normal'), # Design-System Untertitel
            'body': ('Segoe UI', max(14, base_size + 2), 'normal'),     # Design-System Body
            'label': ('Segoe UI', max(12, base_size), 'normal'),        # Design-System Labels
            'button': ('Segoe UI', max(14, base_size + 2), 'bold'),     # Design-System Buttons
            'caption': ('Segoe UI', max(11, base_size - 1), 'normal'),  # Design-System Caption
            'nav': ('Segoe UI', max(14, base_size + 2), 'normal'),      # Design-System Navigation
        }
        
        # Nach Farb-Setup initialisieren
        self.__init_after_colors__(esp32_port)
        
    def setup_color_themes(self):
        """Setup für Light/Dark Mode Farben"""
        if False:  # Dark Mode deaktiviert - verwende immer Custom Dark Mode
            pass
        else:
            # Neues Farbschema - Weiß/Schwarz mit Blautönen
            self.colors = {
                'background_primary': '#FFFFFF',     # Weißer Haupthintergrund
                'background_secondary': '#FFFFFF',   # Weißer Hintergrund für Bereiche
                'background_tertiary': '#d2e0e8',    # Kasten Farbe 4 - Hellstes Blau
                'background_hover': '#93b1bf',       # Kasten Farbe 3 - Mittleres Blau für Hover
                'text_primary': '#000000',           # Schwarzer Haupttext
                'text_secondary': '#000000',         # Schwarzer Sekundärtext
                'text_tertiary': '#000000',          # Schwarzer Tertiärtext
                'accent_primary': '#3C5A69',         # Kasten Farbe 1 - Dunkelstes Blau
                'accent_secondary': '#44778D',       # Kasten Farbe 2 - Mitteldunkles Blau
                'accent_tertiary': '#E60000',        # Rot für Warnungen (beibehalten)
                'accent_warning': '#FF8C00',         # Orange für Warnungen (beibehalten)
                'accent_success': '#00B050',         # Grün für Erfolg (beibehalten)
                'border_light': '#d2e0e8',           # Kasten Farbe 4 für helle Rahmen
                'border_medium': '#93b1bf',          # Kasten Farbe 3 für mittlere Rahmen
                'shadow': 'rgba(60, 90, 105, 0.1)',  # Kasten Farbe 1 Shadow
                'bertrandt_blue': '#3C5A69',         # Kasten Farbe 1 - Primärfarbe
                'bertrandt_light_blue': '#44778D',   # Kasten Farbe 2 - Sekundärfarbe
                'bertrandt_dark_blue': '#3C5A69',    # Kasten Farbe 1 - Dunkle Variante
                'bertrandt_gray': '#93b1bf',         # Kasten Farbe 3 - Grau-Ersatz
                'card_background': '#FFFFFF',        # Weißer Kartenhintergrund
                'card_border': '#d2e0e8',            # Kasten Farbe 4 für Kartenrahmen
                'tile_background': '#d2e0e8',        # Kasten Farbe 4 für Tiles
                'widget_background': '#FFFFFF',      # Weißer Widget-Hintergrund
                # Neue Kasten-Farben explizit definiert
                'kasten_1': '#3C5A69',              # Kasten Farbe 1 - Dunkelstes Blau
                'kasten_2': '#44778D',              # Kasten Farbe 2 - Mitteldunkles Blau
                'kasten_3': '#93b1bf',              # Kasten Farbe 3 - Mittleres Blau
                'kasten_4': '#d2e0e8',              # Kasten Farbe 4 - Hellstes Blau
            }
        
    def __init_after_colors__(self, esp32_port):
        """Initialisierung nach Farb-Setup"""
        self.root.configure(bg=self.colors['background_primary'])
        
        # Serial-Verbindung
        self.esp32_port = esp32_port or '/dev/ttyUSB0'
        self.serial_connection = None
        self.serial_thread = None
        self.running = False
        
        # Daten-Queue
        self.data_queue = queue.Queue()
        
        # Aktuelle Werte
        self.current_signal = 0
        self.client_count = 0
        self.signal_history = []
        
        # Multimedia-Seiten Definitionen (für Messestand) - Bertrandt Corporate Colors
        self.signal_definitions = {
            1: {'name': 'Willkommen', 'color': self.colors['bertrandt_blue'], 'icon': '1', 'content_type': 'welcome'},
            2: {'name': 'Unternehmen', 'color': self.colors['bertrandt_light_blue'], 'icon': '2', 'content_type': 'company'},
            3: {'name': 'Produkte', 'color': self.colors['bertrandt_blue'], 'icon': '3', 'content_type': 'products'},
            4: {'name': 'Innovation', 'color': self.colors['bertrandt_light_blue'], 'icon': '4', 'content_type': 'innovation'},
            5: {'name': 'Technologie', 'color': self.colors['bertrandt_blue'], 'icon': '5', 'content_type': 'technology'},
            6: {'name': 'Referenzen', 'color': self.colors['bertrandt_light_blue'], 'icon': '6', 'content_type': 'references'},
            7: {'name': 'Team', 'color': self.colors['bertrandt_blue'], 'icon': '7', 'content_type': 'team'},
            8: {'name': 'Karriere', 'color': self.colors['bertrandt_light_blue'], 'icon': '8', 'content_type': 'career'},
            9: {'name': 'Kontakt', 'color': self.colors['bertrandt_blue'], 'icon': '9', 'content_type': 'contact'},
            10: {'name': 'Danke', 'color': self.colors['bertrandt_light_blue'], 'icon': '10', 'content_type': 'thanks'}
        }
        
        # Multimedia Content Storage
        self.content_pages = {}
        self.current_page = 1
        self.media_player = None
        
        # Content-Ordner erstellen
        self.content_dir = os.path.join(os.path.dirname(__file__), "content")
        self.ensure_content_structure()
        
        # Multimedia-Komponenten
        self.current_image = None
        self.current_video = None
        
        # Dev Mode
        self.dev_mode = False
        self.dev_timer = None
        
        self.setup_styles()
        self.setup_gui()
        self.setup_serial()
        
        # GUI ist jetzt vollständig buttonbasiert - keine Tastatur-Shortcuts mehr nötig
        
        # Slide-Daten laden
        self.slide_data = {}
        self.load_slides_from_file()
        

    def detect_primary_monitor(self):
        """Erkennt explizit den primären Monitor und seine Eigenschaften"""
        try:
            # Versuche, primären Monitor über xrandr zu ermitteln (Linux)
            try:
                import subprocess
                result = subprocess.run(['xrandr', '--query'], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if ' connected primary' in line or (' connected' in line and 'primary' in line):
                            # Primärer Monitor gefunden
                            parts = line.split()
                            for part in parts:
                                if 'x' in part and '+' in part:
                                    # Format: WIDTHxHEIGHT+X+Y
                                    resolution_pos = part.split('+')
                                    if len(resolution_pos) >= 3:
                                        resolution = resolution_pos[0]
                                        x_pos = int(resolution_pos[1])
                                        y_pos = int(resolution_pos[2])
                                        width, height = map(int, resolution.split('x'))
                                        self.primary_width = width
                                        self.primary_height = height
                                        self.primary_x = x_pos
                                        self.primary_y = y_pos
                                        print(f"Primärer Monitor erkannt: {width}x{height} bei Position ({x_pos}, {y_pos})")
                                        return
                                    break
                    
                    # Fallback: Ersten Monitor als primär verwenden
                    for line in lines:
                        if ' connected' in line and 'disconnected' not in line:
                            parts = line.split()
                            for part in parts:
                                if 'x' in part and '+' in part:
                                    resolution_pos = part.split('+')
                                    if len(resolution_pos) >= 3:
                                        resolution = resolution_pos[0]
                                        x_pos = int(resolution_pos[1])
                                        y_pos = int(resolution_pos[2])
                                        width, height = map(int, resolution.split('x'))
                                        self.primary_width = width
                                        self.primary_height = height
                                        self.primary_x = x_pos
                                        self.primary_y = y_pos
                                        print(f"Erster Monitor als primär verwendet: {width}x{height} bei Position ({x_pos}, {y_pos})")
                                        return
                                    break
            except Exception as e:
                print(f"xrandr-Erkennung fehlgeschlagen: {e}")
            
            # Fallback: Standard-Werte für primären Monitor
            # Bei Multi-Monitor-Setup ist der primäre Monitor normalerweise bei (0,0)
            total_width = self.root.winfo_screenwidth()
            total_height = self.root.winfo_screenheight()
            
            # Wenn Gesamtbreite > 2560, nehmen wir an, dass es mehrere Monitore gibt
            # und der primäre Monitor die linke Hälfte ist
            if total_width > 2560:
                self.primary_width = 1920  # Standard-Breite für primären Monitor
                self.primary_height = total_height
                self.primary_x = 0  # Primärer Monitor beginnt bei x=0
                self.primary_y = 0
                print(f"Multi-Monitor-Fallback: Primärer Monitor bei (0,0) mit {self.primary_width}x{self.primary_height}")
            else:
                # Einzelner Monitor
                self.primary_width = total_width
                self.primary_height = total_height
                self.primary_x = 0
                self.primary_y = 0
                print(f"Einzelner Monitor: {self.primary_width}x{self.primary_height}")
                
        except Exception as e:
            print(f"Monitor-Erkennung fehlgeschlagen: {e}")
            # Sicherer Fallback
            self.primary_width = 1920
            self.primary_height = 1080
            self.primary_x = 0
            self.primary_y = 0
            print(f"Fallback: Standard-Monitor 1920x1080 bei (0,0)")

    def setup_styles(self):
        """Modern Clean UI Styles - Minimalistisch & Intuitiv"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Clean Header Style
        self.style.configure('Header.TFrame', 
                           background=self.colors['background_primary'],
                           relief='flat',
                           borderwidth=0)
        
        # Modern Card Style mit subtilen Schatten
        self.style.configure('Card.TFrame',
                           background=self.colors['background_primary'],
                           relief='flat',
                           borderwidth=1,
                           lightcolor=self.colors['border_light'],
                           darkcolor=self.colors['border_light'])
        
        # Primary Button - Google Material Design inspiriert
        self.style.configure('Primary.TButton',
                           background=self.colors['accent_primary'],
                           foreground='white',
                           font=self.fonts['button'],
                           relief='flat',
                           borderwidth=0,
                           focuscolor='none',
                           padding=(24, 12))
        
        self.style.map('Primary.TButton',
                      background=[('active', '#1557B0'),
                                ('pressed', '#1557B0'),
                                ('disabled', self.colors['border_medium'])])
        
        # Success Button - Clean Green
        self.style.configure('Success.TButton',
                           background=self.colors['accent_secondary'],
                           foreground='white',
                           font=self.fonts['button'],
                           relief='flat',
                           borderwidth=0,
                           focuscolor='none',
                           padding=(24, 12))
        
        self.style.map('Success.TButton',
                      background=[('active', '#2E7D32'),
                                ('pressed', '#2E7D32')])
        
        # Warning Button - Clean Orange/Red
        self.style.configure('Warning.TButton',
                           background=self.colors['accent_tertiary'],
                           foreground='white',
                           font=self.fonts['button'],
                           relief='flat',
                           borderwidth=0,
                           focuscolor='none',
                           padding=(24, 12))
        
        self.style.map('Warning.TButton',
                      background=[('active', '#C5221F'),
                                ('pressed', '#C5221F')])
        
        # Secondary Button - Outline Style
        self.style.configure('Secondary.TButton',
                           background=self.colors['background_primary'],
                           foreground=self.colors['accent_primary'],
                           font=self.fonts['button'],
                           relief='solid',
                           borderwidth=1,
                           focuscolor='none',
                           padding=(24, 12))
        
        self.style.map('Secondary.TButton',
                      background=[('active', self.colors['background_hover']),
                                ('pressed', self.colors['background_hover'])],
                      bordercolor=[('!active', self.colors['border_medium']),
                                 ('active', self.colors['accent_primary'])])
        
        # Chip Button - Moderne Pills
        self.style.configure('Chip.TButton',
                           background=self.colors['background_tertiary'],
                           foreground=self.colors['text_secondary'],
                           font=self.fonts['caption'],
                           relief='flat',
                           borderwidth=0,
                           focuscolor='none',
                           padding=(16, 8))
        
        self.style.map('Chip.TButton',
                      background=[('active', self.colors['accent_primary']),
                                ('pressed', self.colors['accent_primary'])],
                      foreground=[('active', 'white'),
                                ('pressed', 'white')])
        
        # Ghost Button - Sehr subtil
        self.style.configure('Ghost.TButton',
                           background=self.colors['background_primary'],
                           foreground=self.colors['text_secondary'],
                           font=self.fonts['button'],
                           relief='flat',
                           borderwidth=0,
                           focuscolor='none',
                           padding=(16, 8))
        
        self.style.map('Ghost.TButton',
                      background=[('active', self.colors['background_secondary']),
                                ('pressed', self.colors['background_tertiary'])],
                      foreground=[('active', self.colors['text_primary'])])
        
        # Modern Combobox
        self.style.configure('TCombobox',
                           fieldbackground=self.colors['background_primary'],
                           background=self.colors['background_primary'],
                           bordercolor=self.colors['border_medium'],
                           arrowcolor=self.colors['text_secondary'],
                           foreground=self.colors['text_primary'],
                           font=self.fonts['body'],
                           padding=(12, 8))
        
        # Modern Entry
        self.style.configure('TEntry',
                           fieldbackground=self.colors['background_primary'],
                           bordercolor=self.colors['border_medium'],
                           focuscolor=self.colors['accent_primary'],
                           foreground=self.colors['text_primary'],
                           font=self.fonts['body'],
                           padding=(12, 8))
        
    def setup_gui(self):
        """Hauptgui-Layout im Bertrandt Design"""
        
        # Header
        self.create_header()
        
        # Main Content Area
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # 16:9 Layout - Left Panel (3/10 Breite - Status-Spalte - immer sichtbar)
        left_panel = ttk.Frame(main_frame, style='Card.TFrame')
        left_panel.pack(side='left', fill='y', padx=(0, 5))
        left_panel.config(width=max(300, self.root.winfo_width() * 3 // 10))
        left_panel.pack_propagate(False)
        
        # Right Panel - Reiter-gesteuerte Inhalte (70% Breite)
        self.right_panel = ttk.Frame(main_frame, style='Card.TFrame')
        self.right_panel.pack(side='right', fill='both', expand=True)
        
        # Status-Spalte erstellen (bleibt immer sichtbar)
        self.create_status_panel(left_panel)
        
        # Reiter-System initialisieren - HOME beim Start öffnen
        self.current_tab = "home"
        
        # HOME-Tab sofort erstellen und aktivieren
        self.create_home_tab()
        
        # Sicherstellen dass HOME-Tab aktiv bleibt
        self.root.after(100, self.ensure_home_tab_active)
        self.root.after(500, self.ensure_home_tab_active)  # Zusätzliche Überprüfung
    
    def setup_responsive_design(self):
        """Konfiguriert intelligentes responsive Design mit garantierter Sichtbarkeit"""
        # Bildschirmgröße ermitteln
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Intelligente Skalierung - weniger aggressiv für bessere Usability
        if self.screen_width >= 1920:  # 24" oder größer
            self.scale_factor = 1.0
            self.layout_mode = "desktop_xl"
        elif self.screen_width >= 1600:  # 20-22" Monitore
            self.scale_factor = 0.9  # Weniger Reduktion
            self.layout_mode = "desktop_large"
        elif self.screen_width >= 1366:  # 15-17" Laptops
            self.scale_factor = 0.8  # Moderatere Skalierung
            self.layout_mode = "desktop_medium"
        elif self.screen_width >= 1280:  # 13-15" Laptops
            self.scale_factor = 0.75
            self.layout_mode = "laptop"
        else:  # Kleinere Bildschirme
            self.scale_factor = 0.7  # Minimum für Lesbarkeit
            self.layout_mode = "compact"
        
        # Fenster maximieren statt feste Größe
        self.root.state('zoomed')
        
        # Garantierte Mindestgrößen für alle wichtigen UI-Elemente
        self.responsive_dims = {
            # Header/Footer - immer sichtbar
            'header_height': max(120, int(156 * self.scale_factor)),
            'footer_height': max(18, int(20 * self.scale_factor)),
            
            # Navigation - Tabs müssen immer klickbar sein
            'tab_button_width': max(120, int(150 * self.scale_factor)),
            'tab_button_height': max(35, int(45 * self.scale_factor)),
            
            # Panels - anpassbar aber funktional
            'status_width': max(220, int(280 * self.scale_factor)),
            'left_panel_width': max(320, int(420 * self.scale_factor)),
            
            # Content - lesbar und bedienbar
            'card_width': max(200, int(280 * self.scale_factor)),
            'card_height': max(140, int(180 * self.scale_factor)),
            'button_height': max(30, int(40 * self.scale_factor)),
            'thumbnail_height': max(160, int(220 * self.scale_factor)),
            
            # Paddings - proportional aber nicht zu klein
            'padding_small': max(3, int(5 * self.scale_factor)),
            'padding_medium': max(6, int(10 * self.scale_factor)),
            'padding_large': max(10, int(15 * self.scale_factor)),
            
            # Text - immer lesbar
            'min_font_size': max(9, int(12 * self.scale_factor)),
            'icon_size': max(16, int(24 * self.scale_factor))
        }
        
        print(f"📱 Smart Responsive: {self.layout_mode} | Scale: {self.scale_factor} | Screen: {self.screen_width}x{self.screen_height}")
    
    def get_responsive_font(self, font_type, size_override=None):
        """Gibt responsive Schriftart mit garantierter Lesbarkeit zurück"""
        base_sizes = {
            'title': 28, 'subtitle': 20, 'header': 24, 'body': 16,
            'button': 14, 'small': 12, 'tiny': 10
        }
        
        if size_override:
            base_size = size_override
        else:
            base_size = base_sizes.get(font_type, 16)
            
        # Intelligente Skalierung mit Mindestgrößen
        scaled_size = int(base_size * self.scale_factor)
        
        # Garantierte Mindestgrößen für Lesbarkeit
        min_sizes = {
            'title': 20, 'subtitle': 16, 'header': 18, 'body': 12,
            'button': 11, 'small': 10, 'tiny': 9
        }
        
        min_size = min_sizes.get(font_type, 10)
        final_size = max(min_size, scaled_size)
        
        weight = 'bold' if font_type in ['title', 'header', 'button'] else 'normal'
        return ('PT Sans', final_size, weight)
    
    def get_responsive_padding(self, size='medium'):
        """Gibt responsive Padding zurück"""
        return self.responsive_dims.get(f'padding_{size}', 10)
        
        # Footer mit Reload-Button
        self.create_footer()
        
    def create_header(self):
        """Modern Clean Header - Minimalistisch & Intuitiv"""
        # Clean Header mit subtiler Trennung
        header_height = max(104, int(self.root.winfo_height() // 12 * 1.3))
        header_frame = tk.Frame(self.root, bg=self.colors['background_primary'], height=header_height)
        header_frame.pack(fill='x', pady=(0, 0))
        header_frame.pack_propagate(False)
        
        # Logo-Bereich (links) - Sticky Navigation
        logo_frame = tk.Frame(header_frame, bg=self.colors['background_primary'])
        logo_frame.pack(side='left', padx=32, pady=16)
        
        # Bertrandt Logo - Bild laden (angepasst für hellen Hintergrund) - vergrößert
        self.load_bertrandt_logo(logo_frame)
        
        # Bertrandt Tagline - Corporate
        tagline_label = tk.Label(logo_frame,
                               text="Engineering tomorrow",
                               font=self.fonts['caption'],
                               fg=self.colors['bertrandt_blue'],
                               bg=self.colors['background_primary'])
        tagline_label.pack(anchor='w')
        
        # Navigation (Mitte) - Horizontal Navigation
        nav_frame = tk.Frame(header_frame, bg=self.colors['background_primary'])
        nav_frame.pack(side='left', expand=True, padx=40, pady=16)
        
        # Navigation Buttons - Clean & Modern
        nav_buttons_frame = tk.Frame(nav_frame, bg=self.colors['background_primary'])
        nav_buttons_frame.pack()
        
        # Modern Navigation Buttons
        nav_btn_style = {
            'font': self.fonts['nav'],
            'bg': self.colors['background_primary'],
            'fg': self.colors['text_secondary'],
            'relief': 'flat',
            'borderwidth': 0,
            'padx': 20,
            'pady': 12,
            'activebackground': self.colors['background_hover'],
            'activeforeground': self.colors['accent_primary'],
            'cursor': 'hand2'
        }
        
        # Hauptnavigation - Übersichtliche Verlinkungen
        self.nav_buttons = {}
        
        # Bertrandt Corporate Navigation Tabs
        self.tab_buttons = {}
        tabs = [
            ("🏠 HOME", "home", self.colors['bertrandt_blue']),
            ("🎬 DEMO", "demo", self.colors['bertrandt_light_blue']),
            ("✏️ CREATOR", "creator", self.colors['accent_success']),
            ("📊 PRESENTATION", "presentation", self.colors['bertrandt_dark_blue'])
        ]
        
        for i, (text, tab_id, color) in enumerate(tabs):
            is_active = tab_id == "home"
            
            btn = tk.Button(nav_buttons_frame,
                           text=text,
                           command=lambda t=tab_id: self.switch_tab(t),
                           font=self.fonts['button'],
                           bg=color if is_active else self.colors['tile_background'],
                           fg='white' if is_active else self.colors['text_primary'],
                           relief='solid',
                           bd=2,
                           padx=20,
                           pady=12,
                           cursor='hand2',
                           activebackground=color,
                           activeforeground='white')
            btn.pack(side='left', padx=3)
            self.tab_buttons[tab_id] = btn
            
            # Store original color for switching
            btn.original_color = color
        
        # Status & Actions (rechts)
        status_frame = tk.Frame(header_frame, bg=self.colors['background_primary'])
        status_frame.pack(side='right', padx=32, pady=16)
        
        # Status Indicator - Subtil aber informativ
        status_container = tk.Frame(status_frame, bg=self.colors['background_primary'])
        status_container.pack(anchor='e')
        
        # Connection Status - Clean Design
        self.connection_status = tk.Label(status_container,
                                         text="● Offline",
                                         font=self.fonts['caption'],
                                         fg=self.colors['accent_tertiary'],
                                         bg=self.colors['background_primary'])
        self.connection_status.pack(anchor='e')
        
        # Zeit - Dezent
        self.time_label = tk.Label(status_container,
                                  text="",
                                  font=self.fonts['caption'],
                                  fg=self.colors['text_tertiary'],
                                  bg=self.colors['background_primary'])
        self.time_label.pack(anchor='e', pady=(4, 0))
        
        # Subtile Trennung - Moderne Border
        separator = tk.Frame(self.root, bg=self.colors['border_light'], height=1)
        separator.pack(fill='x')
        
        # Zeit aktualisieren
        self.update_time()
    
    def load_bertrandt_logo(self, parent):
        """Bertrandt Logo aus Datei laden"""
        logo_path = os.path.join(os.path.dirname(__file__), "Bertrandt_logo.svg.png")
        
        try:
            # Logo-Bild laden
            logo_image = Image.open(logo_path)
            
            # Logo zu Bertrandt Blau konvertieren für hellen Hintergrund
            logo_image = self.convert_logo_to_dark(logo_image)
            
            # Logo-Größe: 1/6 der Bildschirmbreite (vergrößert)
            logo_width = max(200, self.root.winfo_width() // 6)
            # Proportional skalieren
            aspect_ratio = logo_image.width / logo_image.height
            logo_height = int(logo_width / aspect_ratio)
            
            # Bild skalieren
            logo_image = logo_image.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            
            # Logo-Label erstellen
            logo_label = tk.Label(parent,
                                 image=self.logo_photo,
                                 bg=self.colors['background_secondary'])
            logo_label.pack()
            
            print(f"✅ Bertrandt Logo geladen: {logo_width}x{logo_height}px (vergrößert, 1/6 Breite)")
            
        except Exception as e:
            print(f"⚠️ Logo konnte nicht geladen werden: {e}")
            # Fallback: Text-Logo
            logo_label = tk.Label(parent, 
                                 text="BERTRANDT",
                                 font=self.fonts['display'],
                                 fg=self.colors['text_primary'],
                                 bg=self.colors['background_secondary'])
            logo_label.pack()
    
    def convert_logo_to_dark(self, image):
        """Logo zu dunkel konvertieren für hellen Hintergrund"""
        # Zu RGBA konvertieren falls nötig
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Pixel-Daten laden
        data = image.getdata()
        new_data = []
        
        for item in data:
            # Transparente Pixel beibehalten
            if item[3] == 0:  # Alpha = 0 (transparent)
                new_data.append(item)
            else:
                # Alle anderen Pixel zu Bertrandt Blau machen, Alpha beibehalten
                # Bertrandt Corporate Blue: #003366
                new_data.append((0, 51, 102, item[3]))
        
        # Neue Pixel-Daten setzen
        image.putdata(new_data)
        return image
        
    def create_status_panel(self, parent):
        """Minimalistisches Status Panel - nur essenzielle Informationen"""
        
        # Header - doppelt so hoch
        header = tk.Frame(parent, bg=self.colors['background_secondary'], height=80)
        header.pack(fill='x', padx=10, pady=5)
        header.pack_propagate(False)
        
        tk.Label(header, text="STATUS", 
                font=self.fonts['subtitle'], 
                fg=self.colors['text_primary'],
                bg=self.colors['background_secondary']).pack(pady=20)
        
        # Clients Card
        clients_card = tk.Frame(parent, bg=self.colors['background_tertiary'], relief='flat', bd=0)
        clients_card.pack(fill='x', padx=10, pady=5)
        
        tk.Label(clients_card, text="CLIENTS", 
                font=self.fonts['label'], 
                fg='#000000',
                bg=self.colors['kasten_1']).pack(pady=(8,2))
        
        self.client_count_label = tk.Label(clients_card,
                                          text="0",
                                          font=('Helvetica Neue', 24, 'bold'),
                                          fg=self.colors['accent_primary'],
                                          bg=self.colors['background_tertiary'])
        self.client_count_label.pack(pady=(0,8))
        
        # Mode Card
        mode_card = tk.Frame(parent, bg=self.colors['background_tertiary'], relief='flat', bd=0)
        mode_card.pack(fill='x', padx=10, pady=5)
        
        tk.Label(mode_card, text="MODE", 
                font=self.fonts['label'], 
                fg='#000000',
                bg=self.colors['kasten_2']).pack(pady=(8,2))
        
        self.mode_label = tk.Label(mode_card,
                                  text="DEV",
                                  font=self.fonts['body'],
                                  fg=self.colors['accent_warning'],
                                  bg=self.colors['background_tertiary'])
        self.mode_label.pack(pady=(0,8))
        
        # ESP32 Port Card
        esp32_card = tk.Frame(parent, bg=self.colors['background_tertiary'], relief='flat', bd=0)
        esp32_card.pack(fill='x', padx=10, pady=5)
        
        tk.Label(esp32_card, text="ESP32", 
                font=self.fonts['label'], 
                fg='#000000',
                bg=self.colors['kasten_3']).pack(pady=(8,2))
        
        self.esp32_port_label = tk.Label(esp32_card,
                                        text="❌ Nicht verbunden",
                                        font=self.fonts['body'],
                                        fg=self.colors['accent_tertiary'],
                                        bg=self.colors['background_tertiary'])
        self.esp32_port_label.pack(pady=(0,8))
        
        # GIGA Port Card
        giga_card = tk.Frame(parent, bg=self.colors['background_tertiary'], relief='flat', bd=0)
        giga_card.pack(fill='x', padx=10, pady=5)
        
        tk.Label(giga_card, text="GIGA", 
                font=self.fonts['label'], 
                fg='#000000',
                bg=self.colors['kasten_4']).pack(pady=(8,2))
        
        self.giga_port_label = tk.Label(giga_card,
                                       text="❌ Nicht verbunden",
                                       font=self.fonts['body'],
                                       fg=self.colors['accent_tertiary'],
                                       bg=self.colors['background_tertiary'])
        self.giga_port_label.pack(pady=(0,8))
        
        
        # Status-Updates initialisieren
        self.update_status_display()
        
    def update_status_display(self):
        """Aktualisiert die Status-Anzeige basierend auf aktuellen Verbindungen"""
        # Mode aktualisieren
        if hasattr(self, 'serial_connection') and self.serial_connection and self.serial_connection.is_open:
            self.mode_label.config(text="PLAY", fg=self.colors['accent_secondary'])
        else:
            self.mode_label.config(text="DEV", fg=self.colors['accent_warning'])
        
        # ESP32 Port Status
        if hasattr(self, 'serial_connection') and self.serial_connection and self.serial_connection.is_open:
            self.esp32_port_label.config(text=f"VERBUNDEN: {self.esp32_port}", fg=self.colors['accent_secondary'])
        else:
            self.esp32_port_label.config(text="NICHT VERBUNDEN", fg=self.colors['accent_tertiary'])
        
        # GIGA Port Status (Placeholder - kann später erweitert werden)
        self.giga_port_label.config(text="NICHT VERBUNDEN", fg=self.colors['accent_tertiary'])
    
    def manual_reload_gui(self):
        """Manueller GUI-Reload mit verbesserter Logik"""
        try:
            print("🔄 Manueller GUI-Reload gestartet...")
            
            # Aktuelle Einstellungen speichern
            current_port = getattr(self, 'esp32_port', '/dev/ttyUSB0')
            current_tab = getattr(self, 'current_tab', 'home')
            
            # File Observer stoppen falls aktiv
            if hasattr(self, 'file_observer') and self.file_observer:
                try:
                    self.file_observer.stop()
                    self.file_observer.join(timeout=1)
                except:
                    pass
            
            # Serielle Verbindung sauber schließen
            if hasattr(self, 'serial_connection') and self.serial_connection:
                try:
                    if self.serial_connection.is_open:
                        self.serial_connection.close()
                except:
                    pass
            
            # Threading stoppen
            if hasattr(self, 'running'):
                self.running = False
            
            # Timer stoppen
            if hasattr(self, 'dev_timer') and self.dev_timer:
                try:
                    self.root.after_cancel(self.dev_timer)
                except:
                    pass
            
            # GUI schließen
            self.root.quit()
            self.root.destroy()
            
            # Kurz warten
            import time
            time.sleep(0.5)
            
            # Module neu laden
            import importlib
            import sys
            
            # Alle relevanten Module neu laden
            modules_to_reload = []
            for module_name in list(sys.modules.keys()):
                if module_name.startswith('__main__') or 'Bertrandt' in module_name:
                    modules_to_reload.append(module_name)
            
            for module_name in modules_to_reload:
                try:
                    if module_name in sys.modules:
                        importlib.reload(sys.modules[module_name])
                except:
                    pass
            
            # Neue GUI-Instanz starten
            print("🚀 GUI wird neu gestartet...")
            new_app = BertrandtGUI(esp32_port=current_port)
            new_app.current_tab = current_tab
            new_app.run()
            
        except Exception as e:
            print(f"❌ Fehler beim manuellen Reload: {e}")
            # Fallback: Einfacher Neustart
            try:
                import subprocess
                import sys
                import os
                
                # Aktuelles Script neu starten
                script_path = os.path.abspath(__file__)
                subprocess.Popen([sys.executable, script_path])
                
                # Aktuellen Prozess beenden
                sys.exit(0)
                
            except Exception as fallback_error:
                print(f"❌ Fallback-Neustart fehlgeschlagen: {fallback_error}")
                print("💡 Bitte GUI manuell neu starten")

    def switch_tab(self, tab_id):
        """Wechselt zwischen den Tabs mit Bertrandt Design"""
        self.current_tab = tab_id
        
        # Update button states mit Corporate Colors
        for btn_id, btn in self.tab_buttons.items():
            if btn_id == tab_id:
                # Active tab - use original color
                btn.config(bg=btn.original_color, 
                          fg='white',
                          relief='solid',
                          bd=3)
            else:
                # Inactive tab - neutral design
                btn.config(bg=self.colors['tile_background'], 
                          fg=self.colors['text_primary'],
                          relief='solid',
                          bd=1)
        
        # Clear content area with fade effect
        for widget in self.right_panel.winfo_children():
            widget.destroy()
        
        # Load appropriate content
        if tab_id == "home":
            self.create_home_tab()
        elif tab_id == "demo":
            self.create_demo_tab_with_controls()
        elif tab_id == "creator":
            self.create_creator_tab()
        elif tab_id == "presentation":
            self.create_presentation_tab()
        
        # Update window title
        tab_names = {
            "home": "HOME - Bertrandt Digital Solutions",
            "demo": "DEMO - BumbleB Präsentation", 
            "creator": "CONTENT CREATOR - Folien Editor",
            "presentation": "PRESENTATION - Vollbild Modus"
        }
        if hasattr(self, 'root'):
            self.root.title(f"Bertrandt GUI - {tab_names.get(tab_id, 'Unbekannt')}")
        
        print(f"📋 Reiter gewechselt zu: {tab_id}")
    
    def ensure_home_tab_active(self):
        """Stellt sicher, dass HOME-Tab beim Start aktiv bleibt"""
        if self.current_tab == "home":
            # HOME-Tab erstellen falls nicht vorhanden
            if not self.right_panel.winfo_children():
                self.create_home_tab()
            
            # HOME-Button als aktiv markieren
            if hasattr(self, 'tab_buttons') and 'home' in self.tab_buttons:
                home_btn = self.tab_buttons['home']
                home_btn.config(bg=home_btn.original_color, 
                              fg='white',
                              relief='solid',
                              bd=3)
                
                # Andere Buttons als inaktiv markieren
                for btn_id, btn in self.tab_buttons.items():
                    if btn_id != 'home':
                        btn.config(bg=self.colors['tile_background'], 
                                  fg=self.colors['text_primary'],
                                  relief='solid',
                                  bd=1)
            
            print("✅ HOME-Tab erfolgreich aktiviert und fixiert")
    
    def create_home_tab(self):
        """Home-Reiter mit Multimedia-Präsentation"""
        # Header
        header = tk.Frame(self.right_panel, bg=self.colors['background_secondary'], height=100)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(header, text="HOME - MULTIMEDIA PRÄSENTATION",
                font=self.fonts['title'],
                fg=self.colors['text_primary'],
                bg=self.colors['background_secondary']).pack(pady=30)
        
        # Content Area
        content_frame = tk.Frame(self.right_panel, bg=self.colors['background_tertiary'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Multimedia Content laden
        self.load_multimedia_content(content_frame)
    
    def create_demo_tab_old(self):
        """Alte Demo-Funktion - nicht mehr verwendet"""
        pass
    
    def create_creator_tab(self):
        """Erstellt den Content Creator Tab direkt"""
        print("🎨 Erstelle Content Creator Tab...")
        
        # Bestimme den richtigen Container
        if hasattr(self, 'content_frame'):
            container = self.content_frame
        elif hasattr(self, 'right_panel'):
            container = self.right_panel
        else:
            print("❌ Kein Container gefunden für Content Creator!")
            return
        
        # Clear existing content
        for widget in container.winfo_children():
            widget.destroy()
        
        # Direkt den vollständigen Content Creator erstellen
        self.create_full_content_creator(container)
    
    def load_full_creator(self, container, loading_label):
        """Lädt den vollständigen Content Creator"""
        try:
            # Ladetext entfernen
            loading_label.destroy()
            
            print("🎨 Lade vollständigen Content Creator...")
            
            # Hier wird der vollständige Creator-Code eingefügt
            self.create_full_content_creator(container)
            
        except Exception as e:
            print(f"❌ Fehler beim Laden des Content Creators: {e}")
            # Fallback anzeigen
            error_label = tk.Label(container,
                                 text=f"❌ Content Creator konnte nicht geladen werden\n{str(e)}",
                                 font=self.get_responsive_font('body'),
                                 fg=self.colors['accent_tertiary'],
                                 bg='#FFFFFF')
            error_label.pack(expand=True)
    
    def create_full_content_creator(self, container):
        """Erstellt den vollständigen Content Creator mit allen Features"""
        print("🎨 Erstelle vollständigen Content Creator...")
        
        # Ribbon Interface (PowerPoint Style)
        ribbon_frame = tk.Frame(container, bg='#F8F8F8', height=int(120 * self.scale_factor))
        ribbon_frame.pack(fill='x')
        ribbon_frame.pack_propagate(False)
        
        # Ribbon Content
        ribbon_content = tk.Frame(ribbon_frame, bg='#F8F8F8')
        ribbon_content.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Ribbon Tabs
        ribbon_tabs_frame = tk.Frame(ribbon_content, bg='#F8F8F8')
        ribbon_tabs_frame.pack(fill='x')
        
        # Start und Einfügen Tabs
        for tab_text, tab_id in [("Start", "start"), ("Einfügen", "insert")]:
            is_active = tab_id == "start"
            tab_frame = tk.Frame(ribbon_tabs_frame, 
                               bg='#FFFFFF' if is_active else '#F8F8F8',
                               relief='solid' if is_active else 'flat',
                               bd=1 if is_active else 0)
            tab_frame.pack(side='left', padx=2)
            
            tk.Label(tab_frame,
                    text=tab_text,
                    font=self.get_responsive_font('small'),
                    fg='#000000',
                    bg='#FFFFFF' if is_active else '#F8F8F8',
                    padx=15, pady=5).pack()
        
        # Ribbon Tools
        tools_frame = tk.Frame(ribbon_content, bg='#F8F8F8')
        tools_frame.pack(fill='x', pady=(10, 0))
        
        # Speichern Button
        tk.Button(tools_frame,
                 text="💾 ALLE SPEICHERN",
                 font=self.get_responsive_font('button'),
                 bg=self.colors['accent_success'],
                 fg='white',
                 relief='flat',
                 padx=15, pady=8,
                 command=self.save_all_slides).pack(side='left', padx=5)
        
        # Vorschau Button
        tk.Button(tools_frame,
                 text="👁️ VORSCHAU",
                 font=self.get_responsive_font('button'),
                 bg=self.colors['accent_primary'],
                 fg='white',
                 relief='flat',
                 padx=15, pady=8,
                 command=self.preview_current_slide).pack(side='left', padx=5)
        
        # Hauptcontainer für Editor
        editor_container = tk.Frame(container, bg='#F8F9FA')
        editor_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Linke Seite - Folien-Thumbnails (90% Breite)
        left_width = self.responsive_dims['left_panel_width']
        left_frame = tk.Frame(editor_container, bg='#FFFFFF', relief='flat', bd=0, width=left_width)
        left_frame.pack(side='left', fill='y', padx=(0, 15))
        left_frame.pack_propagate(False)
        
        # Header für Folien-Panel
        header_height = max(50, int(60 * self.scale_factor))
        nav_header = tk.Frame(left_frame, bg=self.colors['bertrandt_blue'], height=header_height)
        nav_header.pack(fill='x')
        nav_header.pack_propagate(False)
        
        header_content = tk.Frame(nav_header, bg=self.colors['bertrandt_blue'])
        header_content.pack(expand=True, fill='both', padx=15, pady=12)
        
        tk.Label(header_content,
                text="📑 FOLIEN ÜBERSICHT",
                font=self.get_responsive_font('header', 18),
                fg='#FFFFFF',
                bg=self.colors['bertrandt_blue']).pack(side='left')
        
        tk.Button(header_content,
                 text="➕ NEUE FOLIE",
                 font=self.get_responsive_font('button', 12),
                 fg=self.colors['bertrandt_blue'],
                 bg='#FFFFFF',
                 relief='flat',
                 padx=15, pady=8,
                 command=self.add_new_slide).pack(side='right')
        
        # Scrollable Thumbnails
        slides_scroll_frame = tk.Frame(left_frame, bg='#FFFFFF')
        slides_scroll_frame.pack(fill='both', expand=True, padx=8, pady=8)
        
        slides_canvas = tk.Canvas(slides_scroll_frame, bg='#FFFFFF', highlightthickness=0)
        slides_scrollbar = tk.Scrollbar(slides_scroll_frame, orient="vertical", command=slides_canvas.yview, width=12)
        slides_frame = tk.Frame(slides_canvas, bg='#FFFFFF')
        
        slides_frame.bind("<Configure>", lambda e: slides_canvas.configure(scrollregion=slides_canvas.bbox("all")))
        slides_canvas.create_window((0, 0), window=slides_frame, anchor="nw")
        slides_canvas.configure(yscrollcommand=slides_scrollbar.set)
        
        slides_canvas.pack(side="left", fill="both", expand=True)
        slides_scrollbar.pack(side="right", fill="y")
        
        # Folien-Thumbnails (1-10) mit 90% Breite
        for i in range(1, 11):
            slide_config = self.load_slide_config(i)
            slide_title = slide_config.get('title', f'Folie {i}')
            
            # Thumbnail Container
            thumb_frame = tk.Frame(slides_frame, bg='#FFFFFF', relief='solid', bd=1)
            thumb_frame.pack(fill='x', pady=8, padx=5)
            
            if i == 1:  # Aktive Folie
                thumb_frame.config(bd=3, highlightbackground=self.colors['bertrandt_blue'], highlightthickness=2)
            
            # Header mit Folien-Nummer und Status
            header_row = tk.Frame(thumb_frame, bg='#FFFFFF')
            header_row.pack(fill='x', padx=15, pady=8)
            
            # Folien-Badge
            slide_badge = tk.Frame(header_row, bg=self.colors['bertrandt_blue'])
            slide_badge.pack(side='left')
            tk.Label(slide_badge, text=f"{i}", font=self.get_responsive_font('button', 14),
                    fg='#FFFFFF', bg=self.colors['bertrandt_blue'], padx=12, pady=4).pack()
            
            # Status-Badge
            status_color = self.colors['accent_success'] if i <= 3 else '#FFC107' if i <= 7 else self.colors['accent_tertiary']
            status_text = '✓ Fertig' if i <= 3 else '⚠ In Arbeit' if i <= 7 else '○ Neu'
            status_badge = tk.Frame(header_row, bg=status_color)
            status_badge.pack(side='right')
            tk.Label(status_badge, text=status_text, font=self.get_responsive_font('small', 11),
                    fg='#FFFFFF', bg=status_color, padx=10, pady=4).pack()
            
            # Preview Frame (90% Breite)
            preview_frame = tk.Frame(thumb_frame, bg='#F8F9FA', height=int(220 * self.scale_factor), relief='flat', bd=0)
            preview_frame.pack(fill='x', padx=21, pady=(0, 15))  # 21px = 90% von 420px
            preview_frame.pack_propagate(False)
            
            # Titel
            title_preview = slide_title[:80] + "..." if len(slide_title) > 80 else slide_title
            tk.Label(preview_frame, text=title_preview, font=self.get_responsive_font('body', 16),
                    fg='#333333', bg='#F8F9FA', wraplength=330, justify='left').pack(anchor='nw', padx=24, pady=15)
            
            # Untertitel
            subtitle = slide_config.get('subtitle', '')[:100] + "..." if len(slide_config.get('subtitle', '')) > 100 else slide_config.get('subtitle', '')
            if subtitle:
                tk.Label(preview_frame, text=subtitle, font=self.get_responsive_font('body', 14),
                        fg='#0078D4', bg='#F8F9FA', wraplength=330, justify='left').pack(anchor='nw', padx=24)
            
            # Content Preview
            content_preview = slide_config.get('text_content', '')[:180] + "..." if len(slide_config.get('text_content', '')) > 180 else slide_config.get('text_content', '')
            if content_preview:
                tk.Label(preview_frame, text=content_preview, font=self.get_responsive_font('small', 13),
                        fg='#666666', bg='#F8F9FA', wraplength=330, justify='left').pack(anchor='nw', padx=24, pady=(12, 0))
            
            # Click-Handler
            thumb_frame.bind("<Button-1>", lambda e, slide=i: self.select_slide_for_editing(slide))
            thumb_frame.bind("<Button-3>", lambda e, slide=i: self.show_slide_context_menu(e, slide))
        
        # Rechte Seite - Slide Editor
        main_frame = tk.Frame(editor_container, bg='#FFFFFF', relief='flat', bd=0)
        main_frame.pack(side='right', fill='both', expand=True, padx=(15, 0))
        
        # Canvas Header
        canvas_header = tk.Frame(main_frame, bg='#F0F0F0', height=40)
        canvas_header.pack(fill='x')
        canvas_header.pack_propagate(False)
        
        tk.Label(canvas_header, text="📝 SLIDE EDITOR - Folie 1",
                font=self.get_responsive_font('header'), fg='#333333', bg='#F0F0F0').pack(expand=True)
        
        # Canvas Content
        self.slide_canvas = tk.Frame(main_frame, bg='#FFFFFF')
        self.slide_canvas.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Editor Content
        tk.Label(self.slide_canvas,
                text="🎨 SLIDE EDITOR\n\nHier können Sie den Inhalt der ausgewählten Folie bearbeiten.\n\nKlicken Sie auf eine Folie links, um sie zu bearbeiten.",
                font=self.get_responsive_font('body'), fg='#666666', bg='#FFFFFF', justify='center').pack(expand=True)
        
        print("✅ Content Creator mit allen Features erfolgreich geladen!")
        
        # Modern Header - 24" Display optimiert
        header_frame = tk.Frame(main_container, bg=self.colors['kasten_1'], relief='flat', bd=0, height=120)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Header Content
        header_content = tk.Frame(header_frame, bg=self.colors['kasten_1'])
        header_content.pack(expand=True, fill='both', padx=40, pady=25)
        
        # Title mit Icon - größer für 24" Display
        title_frame = tk.Frame(header_content, bg=self.colors['kasten_1'])
        title_frame.pack(anchor='w')
        
        tk.Label(title_frame,
                text="✏️ CONTENT CREATOR",
                font=('PT Sans', 32, 'bold'),
                fg='#FFFFFF',
                bg=self.colors['kasten_1']).pack(side='left')
        
        # Subtitle - größer für bessere Lesbarkeit
        tk.Label(header_content,
                text="Erstellen und bearbeiten Sie BumbleB Präsentationsfolien - Optimiert für 24\" Full HD Display",
                font=('PT Sans', 18, 'normal'),
                fg='#FFFFFF',
                bg=self.colors['kasten_1']).pack(anchor='w', pady=(8, 0))
        
        # Toolbar - 24" Display optimiert
        toolbar_frame = tk.Frame(main_container, bg=self.colors['kasten_4'], relief='flat', bd=0, height=80)
        toolbar_frame.pack(fill='x', padx=0, pady=0)
        toolbar_frame.pack_propagate(False)
        
        toolbar_content = tk.Frame(toolbar_frame, bg=self.colors['kasten_4'])
        toolbar_content.pack(expand=True, fill='both', padx=30, pady=15)
        
        # Quick Actions - größere Schrift
        tk.Label(toolbar_content,
                text="🚀 SCHNELLAKTIONEN:",
                font=('PT Sans', 16, 'bold'),
                fg='#000000',
                bg=self.colors['kasten_4']).pack(side='left')
        
        # Action Buttons - größer für Touch-Bedienung
        action_frame = tk.Frame(toolbar_content, bg=self.colors['kasten_4'])
        action_frame.pack(side='left', padx=(30, 0))
        
        tk.Button(action_frame,
                 text="💾 ALLE SPEICHERN",
                 command=self.save_all_slides,
                 font=('PT Sans', 14, 'bold'),
                 bg=self.colors['kasten_2'],
                 fg='#FFFFFF',
                 relief='flat',
                 padx=25,
                 pady=10,
                 cursor='hand2').pack(side='left', padx=8)
        
        tk.Button(action_frame,
                 text="👁️ VORSCHAU",
                 command=self.preview_current_slide,
                 font=('PT Sans', 14, 'bold'),
                 bg=self.colors['kasten_3'],
                 fg='#FFFFFF',
                 relief='flat',
                 padx=25,
                 pady=10,
                 cursor='hand2').pack(side='left', padx=8)
        
        # PowerPoint-ähnliches Layout
        editor_container = tk.Frame(main_container, bg='#FFFFFF')
        editor_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Linke Seite - Folien-Thumbnails - Responsive
        left_width = self.responsive_dims['left_panel_width']
        left_frame = tk.Frame(editor_container, bg='#FFFFFF', relief='flat', bd=0, width=left_width)
        left_frame.pack(side='left', fill='y', padx=(0, self.get_responsive_padding('large')))
        left_frame.pack_propagate(False)
        
        # Schatten-Effekt für linken Frame
        shadow_frame = tk.Frame(editor_container, bg='#E0E0E0', width=2)
        shadow_frame.pack(side='left', fill='y')
        
        # Thumbnails Header - Responsive
        header_height = max(50, int(60 * self.scale_factor))
        nav_header = tk.Frame(left_frame, bg=self.colors['bertrandt_blue'], height=header_height)
        nav_header.pack(fill='x')
        nav_header.pack_propagate(False)
        
        header_content = tk.Frame(nav_header, bg=self.colors['bertrandt_blue'])
        header_content.pack(expand=True, fill='both', 
                           padx=self.get_responsive_padding('large'), 
                           pady=self.get_responsive_padding('medium'))
        
        tk.Label(header_content,
                text="📑 FOLIEN ÜBERSICHT",
                font=('PT Sans', 18, 'bold'),
                fg='#FFFFFF',
                bg=self.colors['bertrandt_blue']).pack(side='left')
        
        # Neue Folie Button
        tk.Button(header_content,
                 text="➕",
                 command=self.add_new_slide,
                 font=('PT Sans', 14, 'bold'),
                 bg='#4CAF50',
                 fg='#FFFFFF',
                 relief='flat',
                 bd=0,
                 padx=8,
                 pady=2,
                 cursor='hand2').pack(side='right')
        
        # Scrollable Thumbnails (24" optimiert) - Modernes Design
        slides_scroll_frame = tk.Frame(left_frame, bg='#FFFFFF')
        slides_scroll_frame.pack(fill='both', expand=True, padx=8, pady=8)
        
        # Canvas für Scrolling - Modernes Design
        slides_canvas = tk.Canvas(slides_scroll_frame, bg='#FFFFFF', highlightthickness=0)
        slides_scrollbar = tk.Scrollbar(slides_scroll_frame, orient="vertical", command=slides_canvas.yview, 
                                       width=12, bg='#F0F0F0', troughcolor='#E0E0E0')
        slides_frame = tk.Frame(slides_canvas, bg='#FFFFFF')
        
        slides_frame.bind(
            "<Configure>",
            lambda e: slides_canvas.configure(scrollregion=slides_canvas.bbox("all"))
        )
        
        slides_canvas.create_window((0, 0), window=slides_frame, anchor="nw")
        slides_canvas.configure(yscrollcommand=slides_scrollbar.set)
        
        # Initialisiere Editor-Variablen
        self.current_edit_slide = 1
        self.slide_buttons = {}
        
        # PowerPoint-Style Thumbnails (1-10) - Nur 10 Folien
        for i in range(1, 11):
            slide_config = self.load_slide_config(i)
            slide_title = slide_config.get('title', f'Folie {i}')
            
            # Thumbnail Container - 90% der Kastenbreite nutzen
            thumb_frame = tk.Frame(slides_frame, bg='#FFFFFF', relief='flat', bd=0)
            thumb_frame.pack(fill='x', pady=12, padx=5)  # Minimales Padding für maximale Breite
            
            # Card Shadow Effect
            if i == 1:  # Aktive Folie
                thumb_frame.config(relief='solid', bd=3, highlightbackground=self.colors['bertrandt_blue'], 
                                 highlightthickness=2)
            else:
                thumb_frame.config(relief='solid', bd=1, highlightbackground='#E0E0E0')
            thumb_frame.bind("<Button-1>", lambda e, x=i: self.select_slide_for_editing(x))
            thumb_frame.bind("<Button-3>", lambda e, x=i: self.show_slide_context_menu(e, x))  # Rechtsklick
            
            # Folien-Nummer und Status - 90% der Kastenbreite nutzen
            header_row = tk.Frame(thumb_frame, bg='#FFFFFF')
            header_row.pack(fill='x', padx=21, pady=10)  # Gleiche Padding wie Preview
            
            number_label = tk.Label(header_row,
                                   text=str(i),
                                   font=('PT Sans', 12, 'bold'),
                                   fg='#0078D4' if i == 1 else '#666666',
                                   bg='#FFFFFF')
            number_label.pack(side='left')
            
            # Status Indicator
            status_label = tk.Label(header_row,
                                   text="●" if i <= 3 else "○",
                                   font=('PT Sans', 10, 'normal'),
                                   fg='#4CAF50' if i <= 3 else '#FFC107',
                                   bg='#FFFFFF')
            status_label.pack(side='right')
            
            # Thumbnail Preview - 90% der Kastenbreite nutzen (420px * 0.9 = 378px)
            preview_frame = tk.Frame(thumb_frame, bg='#F8F9FA', height=220, relief='flat', bd=0)
            preview_frame.pack(fill='x', padx=21, pady=(0, 15))  # 21px padding = 378px nutzbare Breite
            preview_frame.pack_propagate(False)
            
            # Mini-Titel - 90% Kastenbreite optimal nutzen
            title_preview = slide_title[:80] + "..." if len(slide_title) > 80 else slide_title
            tk.Label(preview_frame,
                    text=title_preview,
                    font=('PT Sans', 16, 'bold'),
                    fg='#333333',
                    bg='#F8F9FA',
                    wraplength=330,  # 378px - 48px padding = 330px für Text
                    justify='left').pack(anchor='nw', padx=24, pady=15)
            
            # Untertitel - 90% Kastenbreite optimal nutzen
            subtitle = slide_config.get('subtitle', '')[:100] + "..." if len(slide_config.get('subtitle', '')) > 100 else slide_config.get('subtitle', '')
            if subtitle:
                tk.Label(preview_frame,
                        text=subtitle,
                        font=('PT Sans', 14, 'normal'),
                        fg='#0078D4',
                        bg='#F8F9FA',
                        wraplength=330,  # 378px - 48px padding = 330px für Text
                        justify='left').pack(anchor='nw', padx=24)
            
            # Content Preview - 90% Kastenbreite optimal nutzen
            content_preview = slide_config.get('text_content', '')[:180] + "..." if len(slide_config.get('text_content', '')) > 180 else slide_config.get('text_content', '')
            if content_preview:
                tk.Label(preview_frame,
                        text=content_preview,
                        font=('PT Sans', 13, 'normal'),
                        fg='#666666',
                        bg='#F8F9FA',
                        wraplength=330,  # 378px - 48px padding = 330px für Text
                        justify='left').pack(anchor='nw', padx=24, pady=(12, 0))
            
            self.slide_buttons[i] = thumb_frame
        
        # Pack scrollbar and canvas
        slides_canvas.pack(side="left", fill="both", expand=True)
        slides_scrollbar.pack(side="right", fill="y")
        
        # Mittlere Seite - Hauptarbeitsbereich (PowerPoint Style)
        middle_frame = tk.Frame(editor_container, bg='#FFFFFF', relief='solid', bd=1)
        middle_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # PowerPoint-Style Ribbon/Toolbar (24" optimiert)
        ribbon_frame = tk.Frame(middle_frame, bg='#F8F8F8', height=120, relief='solid', bd=1)
        ribbon_frame.pack(fill='x')
        ribbon_frame.pack_propagate(False)
        
        # Ribbon Content (24" optimiert)
        ribbon_content = tk.Frame(ribbon_frame, bg='#F8F8F8')
        ribbon_content.pack(fill='both', expand=True, padx=20, pady=12)
        
        # Tab-Gruppen (PowerPoint Style)
        tab_groups = tk.Frame(ribbon_content, bg='#F8F8F8')
        tab_groups.pack(fill='x')
        
        # Ribbon Tabs mit Funktionalität
        self.ribbon_tabs = {}
        self.current_ribbon_tab = "start"
        
        tabs = [("Start", "start"), ("Einfügen", "insert")]
        
        for tab_text, tab_id in tabs:
            is_active = tab_id == "start"
            tab_frame = tk.Frame(tab_groups, 
                               bg='#FFFFFF' if is_active else '#F8F8F8', 
                               relief='solid' if is_active else 'flat', 
                               bd=1 if is_active else 0)
            tab_frame.pack(side='left', padx=3)
            
            tab_btn = tk.Button(tab_frame,
                               text=tab_text,
                               command=lambda t=tab_id: self.switch_ribbon_tab(t),
                               font=('PT Sans', 14, 'normal'),
                               fg='#000000' if is_active else '#666666',
                               bg='#FFFFFF' if is_active else '#F8F8F8',
                               relief='flat',
                               bd=0,
                               padx=20,
                               pady=8,
                               cursor='hand2')
            tab_btn.pack()
            
            self.ribbon_tabs[tab_id] = tab_frame
        
        # Ribbon Tools Container
        self.ribbon_tools_frame = tk.Frame(ribbon_content, bg='#F8F8F8')
        self.ribbon_tools_frame.pack(fill='x', pady=(15, 0))
        
        # Lade Start-Tab Tools
        self.load_ribbon_tools("start")
        
        # Hauptarbeitsbereich (PowerPoint Slide View)
        work_area = tk.Frame(middle_frame, bg='#E5E5E5')
        work_area.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Slide Canvas (16:9 Format wie PowerPoint)
        canvas_container = tk.Frame(work_area, bg='#E5E5E5')
        canvas_container.pack(expand=True)
        
        # Berechne 16:9 Slide-Größe für 24" Display
        slide_width = 960  # Größer für 24" Display
        slide_height = int(slide_width * 9 / 16)  # 540px
        
        self.slide_canvas = tk.Frame(canvas_container, 
                                    bg='#FFFFFF', 
                                    relief='solid', 
                                    bd=3,
                                    width=slide_width,
                                    height=slide_height)
        self.slide_canvas.pack(pady=30)
        self.slide_canvas.pack_propagate(False)
        
        # Slide Header mit Titel
        slide_header = tk.Frame(self.slide_canvas, bg='#F8F9FA', height=40)
        slide_header.pack(fill='x')
        slide_header.pack_propagate(False)
        
        self.slide_title_label = tk.Label(slide_header,
                                         text="Folie 1 - BumbleB Willkommen",
                                         font=('PT Sans', 16, 'bold'),
                                         fg='#333333',
                                         bg='#F8F9FA')
        self.slide_title_label.pack(expand=True)
        
        # Editor Content Area (in der Slide)
        self.editor_content = tk.Frame(self.slide_canvas, bg='#FFFFFF')
        self.editor_content.pack(fill='both', expand=True, padx=25, pady=25)
        
        # Status und Zoom Controls (PowerPoint Style)
        status_frame = tk.Frame(work_area, bg='#E5E5E5')
        status_frame.pack(side='bottom', fill='x', pady=8)
        
        # Links - Slide Info
        info_left = tk.Frame(status_frame, bg='#E5E5E5')
        info_left.pack(side='left', padx=20)
        
        self.slide_status_label = tk.Label(info_left,
                                          text="Folie 1 von 10",
                                          font=('PT Sans', 12, 'normal'),
                                          fg='#666666',
                                          bg='#E5E5E5')
        self.slide_status_label.pack(side='left')
        
        # Rechts - Zoom Controls
        zoom_frame = tk.Frame(status_frame, bg='#E5E5E5')
        zoom_frame.pack(side='right', padx=20)
        
        tk.Button(zoom_frame,
                 text="🔍−",
                 command=self.zoom_out,
                 font=('PT Sans', 12, 'normal'),
                 bg='#F0F0F0',
                 fg='#666666',
                 relief='solid',
                 bd=1,
                 padx=8,
                 pady=4,
                 cursor='hand2').pack(side='left', padx=2)
        
        self.zoom_scale = tk.Scale(zoom_frame,
                                  from_=50, to=200,
                                  orient='horizontal',
                                  bg='#E5E5E5',
                                  length=180,
                                  showvalue=False,
                                  command=self.on_zoom_change)
        self.zoom_scale.set(100)
        self.zoom_scale.pack(side='left', padx=5)
        
        self.zoom_label = tk.Label(zoom_frame,
                                  text="100%",
                                  font=('PT Sans', 12, 'normal'),
                                  fg='#666666',
                                  bg='#E5E5E5')
        self.zoom_label.pack(side='left', padx=5)
        
        tk.Button(zoom_frame,
                 text="🔍+",
                 command=self.zoom_in,
                 font=('PT Sans', 12, 'normal'),
                 bg='#F0F0F0',
                 fg='#666666',
                 relief='solid',
                 bd=1,
                 padx=8,
                 pady=4,
                 cursor='hand2').pack(side='left', padx=2)
        
        
        # Initialisiere Editor
        self.current_editor_tab = "text"
        self.load_slide_editor(1)
    
    def load_ribbon_tools(self, tab_id):
        """Lädt Ribbon-Tools für spezifischen Tab"""
        # Clear existing tools
        for widget in self.ribbon_tools_frame.winfo_children():
            widget.destroy()
        
        if tab_id == "start":
            # Start Tab Tools
            tools_container = tk.Frame(self.ribbon_tools_frame, bg='#F8F8F8')
            tools_container.pack(fill='x')
            
            # Font Tools
            font_group = tk.Frame(tools_container, bg='#F8F8F8')
            font_group.pack(side='left', padx=10)
            
            tk.Label(font_group, text="Schrift", font=('PT Sans', 10, 'bold'),
                    bg='#F8F8F8').pack()
            
            tk.Button(font_group, text="B", font=('PT Sans', 12, 'bold'),
                     width=3, command=self.format_bold).pack(side='left', padx=2)
            tk.Button(font_group, text="I", font=('PT Sans', 12, 'italic'),
                     width=3, command=self.format_italic).pack(side='left', padx=2)
            
        elif tab_id == "insert":
            # Insert Tab Tools
            tools_container = tk.Frame(self.ribbon_tools_frame, bg='#F8F8F8')
            tools_container.pack(fill='x')
            
            tk.Button(tools_container, text="🖼️ Bild einfügen",
                     command=self.insert_image).pack(side='left', padx=10)
            tk.Button(tools_container, text="🎥 Video einfügen",
                     command=self.insert_video).pack(side='left', padx=10)
    
    def switch_ribbon_tab(self, tab_id):
        """Wechselt Ribbon Tab"""
        self.current_ribbon_tab = tab_id
        
        # Update tab appearance
        for t_id, tab_frame in self.ribbon_tabs.items():
            if t_id == tab_id:
                tab_frame.config(bg='#FFFFFF', relief='solid', bd=1)
            else:
                tab_frame.config(bg='#F8F8F8', relief='flat', bd=0)
        
        # Load tools for this tab
        self.load_ribbon_tools(tab_id)
    
    
    def format_bold(self):
        """Fett formatieren"""
        print("🔤 Text wird fett formatiert")
    
    def format_italic(self):
        """Kursiv formatieren"""
        print("🔤 Text wird kursiv formatiert")
    
    def insert_image(self):
        """Bild einfügen"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Bild auswählen",
            filetypes=[("Bilder", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            print(f"🖼️ Bild eingefügt: {file_path}")
    
    def insert_video(self):
        """Video einfügen"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Video auswählen",
            filetypes=[("Videos", "*.mp4 *.avi *.mov *.wmv")]
        )
        if file_path:
            print(f"🎥 Video eingefügt: {file_path}")
    
    def zoom_in(self):
        """Zoom vergrößern"""
        current_zoom = self.zoom_scale.get()
        new_zoom = min(200, current_zoom + 25)
        self.zoom_scale.set(new_zoom)
        self.on_zoom_change(new_zoom)
    
    def zoom_out(self):
        """Zoom verkleinern"""
        current_zoom = self.zoom_scale.get()
        new_zoom = max(50, current_zoom - 25)
        self.zoom_scale.set(new_zoom)
        self.on_zoom_change(new_zoom)
    
    def on_zoom_change(self, value):
        """Zoom-Änderung verarbeiten"""
        self.zoom_label.config(text=f"{value}%")
        print(f"🔍 Zoom geändert auf {value}%")
    
    def add_new_slide(self):
        """Neue Folie hinzufügen"""
        print("➕ Neue Folie wird hinzugefügt")
        messagebox.showinfo("Neue Folie", "Neue Folie hinzugefügt!")
    
    def show_slide_context_menu(self, event, slide_num):
        """Kontext-Menü für Folie anzeigen"""
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Bearbeiten", command=lambda: self.select_slide_for_editing(slide_num))
        context_menu.add_command(label="Duplizieren", command=lambda: self.duplicate_slide_action(slide_num))
        context_menu.add_command(label="Löschen", command=lambda: self.delete_slide_action(slide_num))
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def duplicate_slide_action(self, slide_num):
        """Folie duplizieren"""
        print(f"📋 Folie {slide_num} wird dupliziert")
        messagebox.showinfo("Duplizieren", f"Folie {slide_num} dupliziert!")
    
    def delete_slide_action(self, slide_num):
        """Folie löschen"""
        if messagebox.askyesno("Löschen", f"Folie {slide_num} wirklich löschen?"):
            print(f"🗑️ Folie {slide_num} wird gelöscht")
    
    def save_presentation_settings(self):
        """Speichert Präsentations-Einstellungen"""
        try:
            advance_time = float(self.advance_time_var.get())
            fullscreen_start = self.fullscreen_start_var.get()
            loop_enabled = self.loop_enabled_var.get()
            
            # Einstellungen anwenden
            self.presentation_advance_time = advance_time * 1000  # Convert to milliseconds
            self.presentation_fullscreen_start = fullscreen_start
            self.presentation_loop_enabled = loop_enabled
            
            print(f"⚙️ Einstellungen gespeichert: {advance_time}s, Vollbild: {fullscreen_start}, Loop: {loop_enabled}")
            messagebox.showinfo("Gespeichert", "Präsentations-Einstellungen wurden gespeichert!")
            
        except ValueError:
            messagebox.showerror("Fehler", "Ungültige Eingabe für Auto-Advance Zeit!")
        
        print("✅ Moderner Content Creator erstellt!")
        print("✅ Features: 3-Spalten Layout, Tabs, Properties Panel")
        print("✅ Funktionen: Speichern, Vorschau, Quick Tools")
    
    def switch_editor_tab(self, tab_id):
        """Wechselt zwischen Editor-Tabs"""
        self.current_editor_tab = tab_id
        
        # Update tab buttons
        for t_id, btn in self.editor_tabs.items():
            if t_id == tab_id:
                btn.config(bg='#FFFFFF', fg='#000000')
            else:
                btn.config(bg=self.colors['kasten_3'], fg='#FFFFFF')
        
        # Reload editor content for current tab
        self.load_slide_editor(self.current_edit_slide)
        print(f"📋 Editor-Tab gewechselt zu: {tab_id}")
    
    def save_all_slides(self):
        """Speichert alle Folien"""
        print("💾 Alle Folien werden gespeichert...")
        saved_count = 0
        for slide_id in range(1, 11):
            try:
                signal_info = self.signal_definitions.get(slide_id, {})
                content_type = signal_info.get('content_type', 'welcome')
                page_dir = os.path.join(self.content_dir, f"page_{slide_id}_{content_type}")
                
                if not os.path.exists(page_dir):
                    os.makedirs(page_dir)
                
                # Erstelle Standard-Konfiguration falls nicht vorhanden
                config_path = os.path.join(page_dir, "config.json")
                if not os.path.exists(config_path):
                    config = {
                        "title": signal_info.get('name', f'Folie {slide_id}'),
                        "subtitle": f"Bertrandt {signal_info.get('name', f'Folie {slide_id}')}",
                        "text_content": f"Inhalt für {signal_info.get('name', f'Folie {slide_id}')}",
                        "layout": "text_only",
                        "background_image": "",
                        "video": "",
                        "images": []
                    }
                    
                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(config, f, indent=2, ensure_ascii=False)
                    saved_count += 1
                    
            except Exception as e:
                print(f"❌ Fehler beim Speichern von Folie {slide_id}: {e}")
        
        print(f"✅ {saved_count} Folien gespeichert!")
        messagebox.showinfo("Erfolg", f"{saved_count} Folien wurden gespeichert!")
    
    def preview_current_slide(self):
        """Zeigt Vorschau der aktuellen Folie"""
        print(f"👁️ Vorschau für Folie {self.current_edit_slide}")
        
        # Wechsle zum HOME-Tab und zeige die Folie
        self.switch_tab("home")
        self.load_content_page(self.current_edit_slide)
        
        # Zeige Bestätigung
        messagebox.showinfo("Vorschau", f"Folie {self.current_edit_slide} wird im HOME-Tab angezeigt")
    
    def format_text(self):
        """Text-Formatierung"""
        print("🔤 Text-Formatierung geöffnet")
        # TODO: Implementierung
    
    def adjust_layout(self):
        """Layout anpassen"""
        print("📐 Layout-Anpassung geöffnet")
        # TODO: Implementierung
    
    def change_colors(self):
        """Farben ändern"""
        print("🎨 Farb-Editor geöffnet")
        # TODO: Implementierung
    
    def duplicate_slide(self):
        """Folie duplizieren"""
        print(f"📋 Folie {self.current_edit_slide} wird dupliziert")
        # TODO: Implementierung
    
    def load_slide_config(self, slide_num):
        """Lädt Konfiguration einer Folie"""
        signal_info = self.signal_definitions.get(slide_num, {})
        content_type = signal_info.get('content_type', 'welcome')
        page_dir = os.path.join(self.content_dir, f"page_{slide_num}_{content_type}")
        config_path = os.path.join(page_dir, "config.json")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {
                "title": f"Folie {slide_num}",
                "subtitle": "",
                "text_content": "",
                "background_image": "",
                "video": "",
                "images": [],
                "layout": "text_only"
            }
    
    def select_slide_for_editing(self, slide_num):
        """Wählt eine Folie zum Bearbeiten aus"""
        self.current_edit_slide = slide_num
        
        # Update Button-States
        for btn_id, btn in self.slide_buttons.items():
            if btn_id == slide_num:
                btn.config(bg=self.colors['bertrandt_blue'], fg='white')
            else:
                btn.config(bg=self.colors['tile_background'], fg=self.colors['text_primary'])
        
        # Update Header
        self.current_slide_label.config(text=f"📝 Folie {slide_num} bearbeiten")
        
        # Lade Editor für diese Folie
        self.load_slide_editor(slide_num)
        
        print(f"✏️ Folie {slide_num} zum Bearbeiten ausgewählt")
    
    def load_slide_editor(self, slide_num):
        """Lädt den Editor für eine spezifische Folie"""
        # Clear editor content
        for widget in self.editor_content.winfo_children():
            widget.destroy()
        
        # Lade aktuelle Konfiguration
        config = self.load_slide_config(slide_num)
        
        # Scrollable Editor mit CSS Template
        canvas = tk.Canvas(self.editor_content, bg='#FFFFFF', highlightthickness=0)
        scrollbar = tk.Scrollbar(self.editor_content, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#FFFFFF')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Titel Editor mit CSS Template
        tk.Label(scrollable_frame, text="📝 TITEL:", 
                font=('PT Sans', 15, 'bold'),
                fg='#000000', bg='#FFFFFF').pack(anchor='w', pady=(0,5))
        
        self.title_entry = tk.Text(scrollable_frame, height=3, 
                                  font=('PT Sans', 15, 'normal'),
                                  wrap='word', relief='flat', bd=0,
                                  bg='#FFFFFF', fg='#000000',
                                  insertbackground='#000000')
        self.title_entry.pack(fill='x', pady=(0,15))
        self.title_entry.insert('1.0', config.get('title', ''))
        
        # Untertitel Editor mit CSS Template
        tk.Label(scrollable_frame, text="📄 UNTERTITEL:", 
                font=('PT Sans', 15, 'bold'),
                fg='#000000', bg='#FFFFFF').pack(anchor='w', pady=(0,5))
        
        self.subtitle_entry = tk.Text(scrollable_frame, height=2, 
                                     font=('PT Sans', 15, 'normal'),
                                     wrap='word', relief='flat', bd=0,
                                     bg='#FFFFFF', fg='#000000',
                                     insertbackground='#000000')
        self.subtitle_entry.pack(fill='x', pady=(0,15))
        self.subtitle_entry.insert('1.0', config.get('subtitle', ''))
        
        # Text Content Editor mit CSS Template
        tk.Label(scrollable_frame, text="📝 HAUPTINHALT:", 
                font=('PT Sans', 15, 'bold'),
                fg='#000000', bg='#FFFFFF').pack(anchor='w', pady=(0,5))
        
        self.content_entry = tk.Text(scrollable_frame, height=8, 
                                    font=('PT Sans', 15, 'normal'),
                                    wrap='word', relief='flat', bd=0,
                                    bg='#FFFFFF', fg='#000000',
                                    insertbackground='#000000')
        self.content_entry.pack(fill='x', pady=(0,15))
        self.content_entry.insert('1.0', config.get('text_content', ''))
        
        # Media Section
        media_frame = tk.Frame(scrollable_frame, bg=self.colors['tile_background'], relief='solid', bd=1)
        media_frame.pack(fill='x', pady=(0,15), padx=5)
        
        tk.Label(media_frame, text="🎬 MEDIEN:", font=self.fonts['button'],
                fg=self.colors['bertrandt_blue'], bg=self.colors['tile_background']).pack(pady=10)
        
        # Media Buttons
        media_buttons = tk.Frame(media_frame, bg=self.colors['tile_background'])
        media_buttons.pack(pady=(0,10))
        
        tk.Button(media_buttons, text="🖼️ BILD HINZUFÜGEN",
                 command=lambda: self.add_image(slide_num),
                 font=self.fonts['caption'], bg=self.colors['bertrandt_light_blue'],
                 fg='white', relief='solid', bd=1, padx=10, pady=5).pack(side='left', padx=5)
        
        tk.Button(media_buttons, text="🎥 VIDEO HINZUFÜGEN",
                 command=lambda: self.add_video(slide_num),
                 font=self.fonts['caption'], bg=self.colors['bertrandt_light_blue'],
                 fg='white', relief='solid', bd=1, padx=10, pady=5).pack(side='left', padx=5)
        
        tk.Button(media_buttons, text="🖼️ HINTERGRUND",
                 command=lambda: self.set_background(slide_num),
                 font=self.fonts['caption'], bg=self.colors['bertrandt_gray'],
                 fg='white', relief='solid', bd=1, padx=10, pady=5).pack(side='left', padx=5)
        
        # Aktuelle Medien anzeigen
        if config.get('images') or config.get('video') or config.get('background_image'):
            current_media = tk.Frame(media_frame, bg=self.colors['tile_background'])
            current_media.pack(fill='x', padx=10, pady=(0,10))
            
            if config.get('background_image'):
                tk.Label(current_media, text=f"🖼️ Hintergrund: {os.path.basename(config['background_image'])}",
                        font=self.fonts['caption'], bg=self.colors['tile_background']).pack(anchor='w')
            
            if config.get('video'):
                tk.Label(current_media, text=f"🎥 Video: {os.path.basename(config['video'])}",
                        font=self.fonts['caption'], bg=self.colors['tile_background']).pack(anchor='w')
            
            for img in config.get('images', []):
                tk.Label(current_media, text=f"🖼️ Bild: {os.path.basename(img)}",
                        font=self.fonts['caption'], bg=self.colors['tile_background']).pack(anchor='w')
        
        # Save Button
        save_frame = tk.Frame(scrollable_frame, bg=self.colors['card_background'])
        save_frame.pack(fill='x', pady=20)
        
        tk.Button(save_frame, text="💾 FOLIE SPEICHERN",
                 command=lambda: self.save_slide(slide_num),
                 font=self.fonts['button'], bg=self.colors['accent_success'],
                 fg='white', relief='solid', bd=2, padx=20, pady=10,
                 cursor='hand2').pack()
        
        # Pack scrollbar and canvas
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def add_image(self, slide_num):
        """Fügt ein Bild zur Folie hinzu"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Bild auswählen",
            filetypes=[("Bilder", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Alle Dateien", "*.*")]
        )
        if file_path:
            print(f"🖼️ Bild hinzugefügt: {file_path}")
            self.load_slide_editor(slide_num)  # Refresh editor
    
    def add_video(self, slide_num):
        """Fügt ein Video zur Folie hinzu"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Video auswählen",
            filetypes=[("Videos", "*.mp4 *.avi *.mov *.wmv"), ("Alle Dateien", "*.*")]
        )
        if file_path:
            print(f"🎥 Video hinzugefügt: {file_path}")
            self.load_slide_editor(slide_num)  # Refresh editor
    
    def set_background(self, slide_num):
        """Setzt ein Hintergrundbild für die Folie"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Hintergrundbild auswählen",
            filetypes=[("Bilder", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Alle Dateien", "*.*")]
        )
        if file_path:
            print(f"🖼️ Hintergrund gesetzt: {file_path}")
            self.load_slide_editor(slide_num)  # Refresh editor
    
    def save_slide(self, slide_num):
        """Speichert die Änderungen an einer Folie"""
        # Sammle Daten aus den Eingabefeldern
        title = self.title_entry.get('1.0', 'end-1c')
        subtitle = self.subtitle_entry.get('1.0', 'end-1c')
        content = self.content_entry.get('1.0', 'end-1c')
        
        # Erstelle neue Konfiguration
        config = {
            "title": title,
            "subtitle": subtitle,
            "text_content": content,
            "background_image": "",
            "video": "",
            "images": [],
            "layout": "text_only"
        }
        
        # Speichere in JSON-Datei
        signal_info = self.signal_definitions.get(slide_num, {})
        content_type = signal_info.get('content_type', 'welcome')
        page_dir = os.path.join(self.content_dir, f"page_{slide_num}_{content_type}")
        config_path = os.path.join(page_dir, "config.json")
        
        try:
            os.makedirs(page_dir, exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Folie {slide_num} erfolgreich gespeichert!")
            
            # Update Folien-Button Text
            slide_title = title[:30] + "..." if len(title) > 30 else title
            self.slide_buttons[slide_num].config(text=f"{slide_num}. {slide_title}")
            
            # Zeige Erfolgs-Nachricht
            success_label = tk.Label(self.editor_content,
                                   text="✅ Folie gespeichert!",
                                   font=self.fonts['button'],
                                   fg=self.colors['accent_success'],
                                   bg=self.colors['card_background'])
            success_label.place(x=10, y=10)
            self.root.after(2000, success_label.destroy)
            
        except Exception as e:
            print(f"❌ Fehler beim Speichern: {e}")
            error_label = tk.Label(self.editor_content,
                                 text="❌ Speichern fehlgeschlagen!",
                                 font=self.fonts['button'],
                                 fg=self.colors['accent_tertiary'],
                                 bg=self.colors['card_background'])
            error_label.place(x=10, y=10)
            self.root.after(3000, error_label.destroy)
    
    def create_presentation_tab(self):
        """Erstellt den Presentation Tab - Bertrandt Design"""
        # Main container
        main_container = tk.Frame(self.right_panel, bg=self.colors['background_primary'])
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header mit Bertrandt Styling
        header_frame = tk.Frame(main_container, bg=self.colors['bertrandt_dark_blue'], relief='flat', bd=0)
        header_frame.pack(fill='x', pady=(0, 20))
        
        header_label = tk.Label(header_frame,
                               text="📊 PRESENTATION MODE",
                               font=self.fonts['title'],
                               fg='white',
                               bg=self.colors['bertrandt_dark_blue'])
        header_label.pack(pady=15)
        
        subtitle_label = tk.Label(header_frame,
                                 text="Vollbild BumbleB Präsentation für Messestand",
                                 font=self.fonts['subtitle'],
                                 fg=self.colors['bertrandt_light_blue'],
                                 bg=self.colors['bertrandt_dark_blue'])
        subtitle_label.pack(pady=(0, 15))
        
        # Presentation Controls
        controls_frame = tk.Frame(main_container, bg=self.colors['card_background'], relief='solid', bd=2)
        controls_frame.pack(fill='x', pady=(0, 20))
        
        controls_header = tk.Label(controls_frame,
                                  text="🎮 PRÄSENTATIONS-STEUERUNG",
                                  font=self.fonts['subtitle'],
                                  fg=self.colors['bertrandt_blue'],
                                  bg=self.colors['card_background'])
        controls_header.pack(pady=10)
        
        # Control Buttons
        button_frame = tk.Frame(controls_frame, bg=self.colors['card_background'])
        button_frame.pack(pady=(0, 15))
        
        # Fullscreen Button
        fullscreen_btn = tk.Button(button_frame,
                                  text="🖥️ VOLLBILD STARTEN",
                                  command=self.start_fullscreen_presentation,
                                  font=self.fonts['button'],
                                  bg=self.colors['bertrandt_blue'],
                                  fg='white',
                                  relief='solid',
                                  bd=2,
                                  padx=25,
                                  pady=12,
                                  cursor='hand2',
                                  activebackground=self.colors['bertrandt_light_blue'])
        fullscreen_btn.pack(side='left', padx=10)
        
        # Auto-Loop Button
        autoloop_btn = tk.Button(button_frame,
                                text="🔄 AUTO-LOOP",
                                command=self.start_auto_loop,
                                font=self.fonts['button'],
                                bg=self.colors['accent_success'],
                                fg='white',
                                relief='solid',
                                bd=2,
                                padx=25,
                                pady=12,
                                cursor='hand2',
                                activebackground='#00D060')
        autoloop_btn.pack(side='left', padx=10)
        
        # Settings Button
        settings_btn = tk.Button(button_frame,
                                text="⚙️ EINSTELLUNGEN",
                                command=self.open_presentation_settings,
                                font=self.fonts['button'],
                                bg=self.colors['bertrandt_gray'],
                                fg='white',
                                relief='solid',
                                bd=2,
                                padx=25,
                                pady=12,
                                cursor='hand2',
                                activebackground='#8A8A8A')
        settings_btn.pack(side='left', padx=10)
        
        # Features Overview
        features_frame = tk.Frame(main_container, bg=self.colors['card_background'], relief='solid', bd=2)
        features_frame.pack(fill='both', expand=True)
        
        features_text = """🚀 BERTRANDT PRESENTATION MODE

✨ Vollbild-Features:
• 16:9 Kinoformat für professionelle Präsentationen
• BumbleB Story in 10 Folien
• Automatische Folien-Rotation
• Touch-Navigation für Messestand

🎬 Präsentations-Modi:
• Vollbild-Modus für Projektoren
• Auto-Loop für Dauerpräsentation
• Manuelle Navigation mit Touch
• Bertrandt Corporate Design

🏢 Bertrandt Branding:
• Logo auf jeder Folie
• Corporate Colors durchgängig
• violis Plattform prominent
• "Engineering tomorrow" Tagline

🎯 Messestand-Optimiert:
• Touch-freundliche Bedienung
• Responsive für alle Bildschirmgrößen
• Automatische Rückkehr zur Startfolie
• Professionelle Übergänge

💡 Technische Features:
• Hardware-beschleunigte Darstellung
• Optimiert für Arduino GIGA + ESP32
• Real-Time Signal-Integration
• Modulare Architektur"""
        
        content_label = tk.Label(features_frame,
                                text=features_text,
                                font=self.fonts['body'],
                                fg=self.colors['text_primary'],
                                bg=self.colors['card_background'],
                                justify='left',
                                anchor='nw')
        content_label.pack(fill='both', expand=True, padx=30, pady=20)
    
    def start_fullscreen_presentation(self):
        """Startet Vollbild-Präsentation"""
        print("🖥️ Vollbild-Präsentation wird gestartet...")
        
        # Wechsle zu Vollbild-Modus
        if not self.fullscreen:
            self.toggle_fullscreen()
        
        # Wechsle zum DEMO-Tab für Präsentation
        self.switch_tab("demo")
        
        # Starte automatische Demo
        if hasattr(self, 'start_demo_play'):
            self.start_demo_play()
        
        messagebox.showinfo("Vollbild", "Vollbild-Präsentation gestartet!\nESC zum Beenden, F11 zum Umschalten")
        
    def start_auto_loop(self):
        """Startet Auto-Loop Präsentation"""
        print("🔄 Auto-Loop wird gestartet...")
        
        # Wechsle zum DEMO-Tab
        self.switch_tab("demo")
        
        # Starte automatische Demo mit Loop
        if hasattr(self, 'start_demo_play'):
            self.start_demo_play()
            
        # Zeige Info-Dialog
        messagebox.showinfo("Auto-Loop", 
            "Auto-Loop Präsentation gestartet!\n\n" +
            "• Automatischer Folienwechsel alle 2,5 Sekunden\n" +
            "• Endlos-Schleife von Folie 1-10\n" +
            "• PAUSE-Button zum Stoppen\n" +
            "• Perfekt für Messestand-Betrieb")
        
    def open_presentation_settings(self):
        """Öffnet Präsentations-Einstellungen"""
        print("⚙️ Präsentations-Einstellungen werden geöffnet...")
        
        # Einstellungs-Dialog erstellen
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Präsentations-Einstellungen")
        settings_window.geometry("500x400")
        settings_window.configure(bg=self.colors['background_primary'])
        
        # Header
        header_label = tk.Label(settings_window,
                               text="⚙️ PRÄSENTATIONS-EINSTELLUNGEN",
                               font=self.fonts['title'],
                               fg=self.colors['bertrandt_blue'],
                               bg=self.colors['background_primary'])
        header_label.pack(pady=20)
        
        # Einstellungen Frame
        settings_frame = tk.Frame(settings_window, bg=self.colors['background_secondary'])
        settings_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Auto-Advance Zeit
        tk.Label(settings_frame, text="Auto-Advance Zeit (Sekunden):",
                font=self.fonts['body'], fg=self.colors['text_primary'],
                bg=self.colors['background_secondary']).pack(anchor='w', pady=5)
        
        self.advance_time_var = tk.StringVar(value="2.5")
        advance_entry = tk.Entry(settings_frame, textvariable=self.advance_time_var,
                               font=self.fonts['body'], width=10)
        advance_entry.pack(anchor='w', pady=5)
        
        # Vollbild beim Start
        self.fullscreen_start_var = tk.BooleanVar(value=True)
        tk.Checkbutton(settings_frame, text="Vollbild beim Präsentations-Start",
                      variable=self.fullscreen_start_var,
                      font=self.fonts['body'], fg=self.colors['text_primary'],
                      bg=self.colors['background_secondary']).pack(anchor='w', pady=10)
        
        # Loop aktiviert
        self.loop_enabled_var = tk.BooleanVar(value=True)
        tk.Checkbutton(settings_frame, text="Endlos-Loop aktiviert",
                      variable=self.loop_enabled_var,
                      font=self.fonts['body'], fg=self.colors['text_primary'],
                      bg=self.colors['background_secondary']).pack(anchor='w', pady=5)
        
        # Buttons
        button_frame = tk.Frame(settings_window, bg=self.colors['background_primary'])
        button_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Button(button_frame, text="💾 SPEICHERN",
                 command=lambda: [self.save_presentation_settings(), settings_window.destroy()],
                 font=self.fonts['button'], bg=self.colors['accent_success'],
                 fg='white', padx=20, pady=10).pack(side='left', padx=10)
        
        tk.Button(button_frame, text="❌ ABBRECHEN",
                 command=settings_window.destroy,
                 font=self.fonts['button'], bg=self.colors['accent_tertiary'],
                 fg='white', padx=20, pady=10).pack(side='right', padx=10)
    
    def load_multimedia_content(self, parent):
        """Lädt den Multimedia-Inhalt für den Home-Tab"""
        # Hier wird der bestehende Multimedia-Content geladen
        self.content_frame = parent
        self.load_content_page(self.current_page)
        
        # Navigation hinzufügen
        nav_frame = tk.Frame(parent, bg=self.colors['background_secondary'], height=80)
        nav_frame.pack(fill='x', side='bottom')
        nav_frame.pack_propagate(False)
        
        # Navigation Grid
        self.nav_grid = tk.Frame(nav_frame, bg=self.colors['background_secondary'])
        self.nav_grid.pack(fill='x', padx=20, pady=10)
        
        # Navigation Cards erstellen
        self.nav_cards = {}
        for i, (signal_id, signal_info) in enumerate(self.signal_definitions.items()):
            col = i % 10  # 10 Karten in einer Reihe
            card = self.create_nav_card(self.nav_grid, signal_id, signal_info)
            card.grid(row=0, column=col, padx=2, pady=2, sticky='ew')
            self.nav_cards[signal_id] = card
    
    def load_content_creator(self, parent):
        """Lädt den Content Creator in den Creator-Tab"""
        # Vereinfachter Content Creator
        tk.Label(parent, text="Content Creator wird hier geladen...",
                font=self.fonts['subtitle'],
                fg=self.colors['text_secondary'],
                bg=self.colors['background_primary']).pack(pady=50)
    
    def start_presentation(self):
        """Startet die Präsentation"""
        print("📺 Präsentation gestartet")
        if hasattr(self, 'presentation_status_label'):
            self.presentation_status_label.config(text="Präsentation läuft...")
        # Hier kann die Präsentationslogik implementiert werden
                  
    def create_flash_section(self, parent):
        """Dark Theme Arduino Flash-Sektion"""
        # Flash Card
        flash_card = tk.Frame(parent, bg=self.colors['background_tertiary'], relief='flat', borderwidth=0)
        flash_card.pack(fill='x', padx=20, pady=15)
        
        # Card Header
        flash_header = tk.Frame(flash_card, bg=self.colors['accent_warning'], height=35)
        flash_header.pack(fill='x')
        flash_header.pack_propagate(False)
        
        tk.Label(flash_header,
                text="🔧 ARDUINO FLASH-TOOL",
                font=self.fonts['button'],
                fg=self.colors['background_primary'],
                bg=self.colors['accent_warning']).pack(pady=8)
        
        # Flash Content
        flash_content = tk.Frame(flash_card, bg=self.colors['background_tertiary'])
        flash_content.pack(fill='x', padx=15, pady=15)
        
        # Flash Status
        self.flash_status = tk.Label(flash_content,
                                    text="Bereit zum Flashen",
                                    font=self.fonts['label'],
                                    fg=self.colors['text_secondary'],
                                    bg=self.colors['background_tertiary'])
        self.flash_status.pack(anchor='w', pady=(0, 10))
        
        # Geräte-Auswahl Tabs
        device_frame = tk.Frame(flash_content, bg=self.colors['background_tertiary'])
        device_frame.pack(fill='x', pady=5)
        
        self.device_var = tk.StringVar(value="ESP32")
        
        tk.Radiobutton(device_frame,
                      text="📱 ESP32",
                      variable=self.device_var,
                      value="ESP32",
                      font=self.fonts['label'],
                      bg=self.colors['background_tertiary'],
                      fg=self.colors['text_primary'],
                      selectcolor=self.colors['background_secondary'],
                      activebackground=self.colors['background_tertiary'],
                      command=self.on_device_change).pack(side='left', padx=(0, 20))
        
        tk.Radiobutton(device_frame,
                      text="🔧 Arduino GIGA",
                      variable=self.device_var,
                      value="GIGA",
                      font=self.fonts['label'],
                      bg=self.colors['background_tertiary'],
                      fg=self.colors['text_primary'],
                      selectcolor=self.colors['background_secondary'],
                      activebackground=self.colors['background_tertiary'],
                      command=self.on_device_change).pack(side='left')
        
        # Port Auswahl
        port_frame = tk.Frame(flash_content, bg=self.colors['background_tertiary'])
        port_frame.pack(fill='x', pady=5)
        
        tk.Label(port_frame,
                text="Port:",
                font=self.fonts['label'],
                fg=self.colors['text_primary'],
                bg=self.colors['background_tertiary']).pack(side='left')
        
        self.flash_port_var = tk.StringVar()
        self.flash_port_combo = ttk.Combobox(port_frame, 
                                           textvariable=self.flash_port_var,
                                           width=15,
                                           state='readonly')
        self.flash_port_combo.pack(side='left', padx=(5, 0))
        
        ttk.Button(port_frame,
                  text="🔍",
                  width=3,
                  command=self.scan_ports).pack(side='left', padx=(5, 0))
        
        # Flash Buttons
        flash_btn_frame = tk.Frame(flash_content, bg=self.colors['background_tertiary'])
        flash_btn_frame.pack(fill='x', pady=10)
        
        self.flash_btn = ttk.Button(flash_btn_frame,
                                   text="📱 ESP32 FLASHEN",
                                   style='Primary.TButton',
                                   command=self.flash_device)
        self.flash_btn.pack(fill='x', pady=2)
        
        ttk.Button(flash_btn_frame,
                  text="📁 SKETCH AUSWÄHLEN",
                  style='Success.TButton',
                  command=self.select_sketch).pack(fill='x', pady=2)
        
        ttk.Button(flash_btn_frame,
                  text="🚀 BEIDE GERÄTE FLASHEN",
                  style='Warning.TButton',
                  command=self.flash_both_devices).pack(fill='x', pady=2)
        
        # Boot Button Hinweis
        self.hint_frame = tk.Frame(flash_content, 
                             bg=self.colors['accent_tertiary'],
                             relief='flat',
                             borderwidth=1)
        self.hint_frame.pack(fill='x', pady=10)
        
        self.hint_title = tk.Label(self.hint_frame,
                text="💡 ESP32 WICHTIG:",
                font=self.fonts['button'],
                fg=self.colors['text_primary'],
                bg=self.colors['accent_tertiary'])
        self.hint_title.pack(pady=(5, 0))
        
        self.hint_text = tk.Label(self.hint_frame,
                text="Boot-Button drücken wenn\n'Connecting...' erscheint!",
                font=self.fonts['label'],
                fg=self.colors['text_primary'],
                bg=self.colors['accent_tertiary'],
                justify='center')
        self.hint_text.pack(pady=(0, 5))
        
        # Sketch Pfade
        self.esp32_sketch_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                             "Arduino", "ESP32_UDP_Receiver")
        self.giga_sketch_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                            "Arduino", "GIGA_UDP_Sender")
        self.current_sketch_path = self.esp32_sketch_path
        
        # Ports beim Start scannen
        self.scan_ports()
    
    def create_gui_control_section(self, parent):
        """Moderne GUI-Steuerung mit Buttons (ersetzt Tastatureingaben)"""
        # GUI Control Card
        gui_card = tk.Frame(parent, bg=self.colors['background_tertiary'], relief='flat', borderwidth=0)
        gui_card.pack(fill='x', padx=20, pady=15)
        
        # Card Header
        gui_header = tk.Frame(gui_card, bg=self.colors['accent_secondary'], height=35)
        gui_header.pack(fill='x')
        gui_header.pack_propagate(False)
        
        tk.Label(gui_header,
                text="🎮 MANUELLE STEUERUNG",
                font=self.fonts['button'],
                fg=self.colors['text_primary'],
                bg=self.colors['accent_secondary']).pack(pady=8)
        
        # GUI Content
        gui_content = tk.Frame(gui_card, bg=self.colors['background_tertiary'])
        gui_content.pack(fill='x', padx=15, pady=15)
        
        # Info Text
        info_label = tk.Label(gui_content,
                             text="Klicken Sie auf die Seiten-Buttons für direkte Navigation:",
                             font=self.fonts['label'],
                             fg=self.colors['text_secondary'],
                             bg=self.colors['background_tertiary'])
        info_label.pack(anchor='w', pady=(0, 10))
        
        # Seiten-Buttons Grid (2 Reihen à 5 Buttons)
        pages_frame = tk.Frame(gui_content, bg=self.colors['background_tertiary'])
        pages_frame.pack(fill='x', pady=5)
        
        # Erste Reihe (Seiten 1-5)
        row1_frame = tk.Frame(pages_frame, bg=self.colors['background_tertiary'])
        row1_frame.pack(fill='x', pady=(0, 5))
        
        for i in range(1, 6):
            signal_info = self.signal_definitions[i]
            btn = ttk.Button(row1_frame,
                           text=f"{signal_info['icon']} {i}",
                           style='Chip.TButton',
                           command=lambda page=i: self.on_manual_page_select(page))
            btn.pack(side='left', padx=2, fill='x', expand=True)
        
        # Zweite Reihe (Seiten 6-10)
        row2_frame = tk.Frame(pages_frame, bg=self.colors['background_tertiary'])
        row2_frame.pack(fill='x')
        
        for i in range(6, 11):
            signal_info = self.signal_definitions[i]
            btn = ttk.Button(row2_frame,
                           text=f"{signal_info['icon']} {i}",
                           style='Chip.TButton',
                           command=lambda page=i: self.on_manual_page_select(page))
            btn.pack(side='left', padx=2, fill='x', expand=True)
        
        # Separator
        separator = tk.Frame(gui_content, bg=self.colors['background_secondary'], height=1)
        separator.pack(fill='x', pady=10)
        
        # Demo-Steuerung Buttons
        demo_frame = tk.Frame(gui_content, bg=self.colors['background_tertiary'])
        demo_frame.pack(fill='x', pady=5)
        
        ttk.Button(demo_frame,
                  text="🤖 AUTO-DEMO STARTEN",
                  style='Success.TButton',
                  command=self.start_auto_demo).pack(side='left', padx=(0, 5), fill='x', expand=True)
        
        ttk.Button(demo_frame,
                  text="⏹️ DEMO STOPPEN",
                  style='Warning.TButton',
                  command=self.stop_auto_demo).pack(side='left', padx=(5, 0), fill='x', expand=True)
        
        # Zusätzliche Steuerung
        extra_frame = tk.Frame(gui_content, bg=self.colors['background_tertiary'])
        extra_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(extra_frame,
                  text="🏠 STARTSEITE",
                  style='Secondary.TButton',
                  command=lambda: self.on_manual_page_select(1)).pack(fill='x', expand=True)
        
        # Status für manuelle Steuerung
        self.manual_status = tk.Label(gui_content,
                                     text="Bereit für manuelle Steuerung",
                                     font=self.fonts['label'],
                                     fg=self.colors['text_secondary'],
                                     bg=self.colors['background_tertiary'])
        self.manual_status.pack(anchor='w', pady=(10, 0))
        
    def on_manual_page_select(self, page_id):
        """Manuelle Seitenauswahl über GUI-Button"""
        signal_info = self.signal_definitions.get(page_id, {})
        page_name = signal_info.get('name', f'Seite {page_id}')
        
        print(f"🎮 Manuelle Auswahl: Seite {page_id} - {page_name}")
        
        # Status aktualisieren
        self.manual_status.config(
            text=f"Seite {page_id} ausgewählt: {page_name}",
            fg=self.colors['accent_primary']
        )
        
        # Signal simulieren (funktioniert sowohl im Dev Mode als auch normal)
        if self.dev_mode:
            self.simulate_signal(page_id)
        else:
            # Auch im normalen Modus direkte Navigation ermöglichen
            self.update_signal(page_id)
    
    def toggle_demo_mode(self):
        """Demo-Modus umschalten"""
        if hasattr(self, 'demo_running') and self.demo_running:
            self.stop_auto_demo()
        else:
            self.start_auto_demo()
    
    def toggle_presentation_mode(self):
        """Presentation Mode umschalten"""
        if hasattr(self, 'presentation_mode') and self.presentation_mode:
            self.exit_presentation_mode()
        else:
            self.enter_presentation_mode()
    
    def enter_presentation_mode(self):
        """Presentation Mode aktivieren - Vollbild ohne Ablenkungen"""
        self.presentation_mode = True
        # Navigation ausblenden
        if hasattr(self, 'nav_grid'):
            self.nav_grid.pack_forget()
        # Header minimieren oder ausblenden
        print("📺 Presentation Mode aktiviert")
    
    def exit_presentation_mode(self):
        """Presentation Mode deaktivieren"""
        self.presentation_mode = False
        # Navigation wieder anzeigen
        if hasattr(self, 'nav_grid'):
            self.nav_grid.pack(fill='x', padx=20, pady=(0, 10))
        print("📺 Presentation Mode deaktiviert")

    def show_content_creator(self):
        """Content Creator anzeigen - Erweiterte Content-Erstellung im Hauptfenster"""
        # Multimedia-Display temporär ausblenden
        if hasattr(self, 'content_frame'):
            self.content_frame.pack_forget()
        
        # Content Creator Frame erstellen
        self.creator_frame = tk.Frame(self.content_frame.master, bg=self.colors['background_tertiary'], relief='flat', borderwidth=0)
        self.creator_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Header
        header_frame = tk.Frame(self.creator_frame, bg=self.colors['background_secondary'], height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame,
                               text="✨ CONTENT CREATOR",
                               font=self.fonts['title'],
                               fg=self.colors['accent_primary'],
                               bg=self.colors['background_secondary'])
        header_label.pack(pady=15)
        
        # Zurück Button
        back_btn = tk.Button(header_frame,
                            text="← Zurück",
                            font=self.fonts['button'],
                            bg=self.colors['background_tertiary'],
                            fg=self.colors['text_primary'],
                            relief='flat',
                            borderwidth=0,
                            padx=15,
                            pady=5,
                            activebackground=self.colors['accent_primary'],
                            activeforeground=self.colors['text_primary'],
                            command=self.hide_content_creator)
        back_btn.place(x=20, y=15)
        
        # Main Content Frame
        main_frame = tk.Frame(self.creator_frame, bg=self.colors['background_tertiary'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left Panel - Seiten-Auswahl
        left_panel = tk.Frame(main_frame, bg=self.colors['background_secondary'], width=200)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Seiten-Liste
        pages_label = tk.Label(left_panel,
                              text="📄 SEITEN",
                              font=self.fonts['button'],
                              fg=self.colors['text_primary'],
                              bg=self.colors['background_secondary'])
        pages_label.pack(pady=10)
        
        # Seiten-Buttons
        self.creator_selected_page = tk.IntVar(value=1)
        for signal_id, signal_info in self.signal_definitions.items():
            page_btn = tk.Radiobutton(left_panel,
                                     text=f"{signal_info['icon']} {signal_id}. {signal_info['name']}",
                                     variable=self.creator_selected_page,
                                     value=signal_id,
                                     font=self.fonts['label'],
                                     bg=self.colors['background_secondary'],
                                     fg=self.colors['text_primary'],
                                     selectcolor=signal_info['color'],
                                     activebackground=self.colors['background_secondary'],
                                     command=lambda: self.update_creator_content())
            page_btn.pack(fill='x', padx=10, pady=2)
        
        # Right Panel - Content Editor
        right_panel = tk.Frame(main_frame, bg=self.colors['background_secondary'])
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Editor Header
        editor_header = tk.Frame(right_panel, bg=self.colors['accent_primary'], height=40)
        editor_header.pack(fill='x')
        editor_header.pack_propagate(False)
        
        self.creator_page_title = tk.Label(editor_header,
                                          text="Seite 1 - Willkommen",
                                          font=self.fonts['button'],
                                          fg=self.colors['text_primary'],
                                          bg=self.colors['accent_primary'])
        self.creator_page_title.pack(pady=10)
        
        # Editor Content
        editor_content = tk.Frame(right_panel, bg=self.colors['background_secondary'])
        editor_content.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Titel Editor
        tk.Label(editor_content,
                text="📝 Titel:",
                font=self.fonts['label'],
                fg=self.colors['text_primary'],
                bg=self.colors['background_secondary']).pack(anchor='w')
        
        self.creator_title_entry = tk.Entry(editor_content,
                                           font=self.fonts['body'],
                                           bg=self.colors['background_tertiary'],
                                           fg=self.colors['text_primary'],
                                           insertbackground=self.colors['text_primary'])
        self.creator_title_entry.pack(fill='x', pady=(5, 15))
        
        # Untertitel Editor
        tk.Label(editor_content,
                text="📄 Untertitel:",
                font=self.fonts['label'],
                fg=self.colors['text_primary'],
                bg=self.colors['background_secondary']).pack(anchor='w')
        
        self.creator_subtitle_entry = tk.Entry(editor_content,
                                              font=self.fonts['body'],
                                              bg=self.colors['background_tertiary'],
                                              fg=self.colors['text_primary'],
                                              insertbackground=self.colors['text_primary'])
        self.creator_subtitle_entry.pack(fill='x', pady=(5, 15))
        
        # Layout Auswahl
        tk.Label(editor_content,
                text="🎨 Layout:",
                font=self.fonts['label'],
                fg=self.colors['text_primary'],
                bg=self.colors['background_secondary']).pack(anchor='w')
        
        self.creator_layout_var = tk.StringVar(value="text_only")
        layout_frame = tk.Frame(editor_content, bg=self.colors['background_secondary'])
        layout_frame.pack(fill='x', pady=(5, 15))
        
        layouts = [
            ("📝 Nur Text", "text_only"),
            ("🖼️ Bild + Text", "image_text"),
            ("🎬 Video + Text", "video_text"),
            ("🖼️ Vollbild Bild", "fullscreen_image"),
            ("🎬 Vollbild Video", "fullscreen_video")
        ]
        
        for i, (text, value) in enumerate(layouts):
            tk.Radiobutton(layout_frame,
                          text=text,
                          variable=self.creator_layout_var,
                          value=value,
                          font=self.fonts['label'],
                          bg=self.colors['background_secondary'],
                          fg=self.colors['text_primary'],
                          selectcolor=self.colors['background_tertiary'],
                          activebackground=self.colors['background_secondary']).pack(anchor='w')
        
        # Text Editor
        tk.Label(editor_content,
                text="📝 Inhalt:",
                font=self.fonts['label'],
                fg=self.colors['text_primary'],
                bg=self.colors['background_secondary']).pack(anchor='w')
        
        text_frame = tk.Frame(editor_content, bg=self.colors['background_secondary'])
        text_frame.pack(fill='both', expand=True, pady=(5, 15))
        
        self.creator_text_widget = tk.Text(text_frame,
                                          font=self.fonts['body'],
                                          bg=self.colors['background_tertiary'],
                                          fg=self.colors['text_primary'],
                                          insertbackground=self.colors['text_primary'],
                                          wrap=tk.WORD,
                                          height=10)
        
        text_scrollbar = tk.Scrollbar(text_frame, orient='vertical', command=self.creator_text_widget.yview)
        self.creator_text_widget.configure(yscrollcommand=text_scrollbar.set)
        
        self.creator_text_widget.pack(side='left', fill='both', expand=True)
        text_scrollbar.pack(side='right', fill='y')
        
        # Buttons
        button_frame = tk.Frame(self.creator_frame, bg=self.colors['background_tertiary'])
        button_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Button(button_frame,
                  text="💾 SPEICHERN",
                  style='Success.TButton',
                  command=self.save_creator_content).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame,
                  text="👁️ VORSCHAU",
                  style='Primary.TButton',
                  command=self.preview_creator_content).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame,
                  text="📁 ORDNER ÖFFNEN",
                  style='Secondary.TButton',
                  command=self.open_creator_folder).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame,
                  text="🏠 HAUPTANSICHT",
                  style='Warning.TButton',
                  command=self.hide_content_creator).pack(side='right')
        
        # Erste Seite laden
        self.creator_active = True
        self.update_creator_content()
    
    def hide_content_creator(self):
        """Content Creator ausblenden und zur Hauptansicht zurückkehren"""
        if hasattr(self, 'creator_frame'):
            self.creator_frame.destroy()
        
        # Multimedia-Display wieder anzeigen
        if hasattr(self, 'content_frame'):
            self.content_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.creator_active = False
        # Aktuelle Seite neu laden
        self.load_content_page(self.current_page)
    
    def update_creator_content(self):
        """Content Creator Inhalt aktualisieren"""
        if not hasattr(self, 'creator_active') or not self.creator_active:
            return
            
        page_id = self.creator_selected_page.get()
        signal_info = self.signal_definitions[page_id]
        
        # Header aktualisieren
        self.creator_page_title.config(text=f"Seite {page_id} - {signal_info['name']}")
        
        # Content laden
        content_type = signal_info['content_type']
        page_dir = os.path.join(self.content_dir, f"page_{page_id}_{content_type}")
        config_path = os.path.join(page_dir, "config.json")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            config = {
                "title": signal_info['name'],
                "subtitle": f"Seite {page_id} - {signal_info['name']}",
                "text_content": f"Inhalt für Seite {page_id}",
                "layout": "text_only"
            }
        
        # Felder füllen
        self.creator_title_entry.delete(0, tk.END)
        self.creator_title_entry.insert(0, config.get('title', ''))
        
        self.creator_subtitle_entry.delete(0, tk.END)
        self.creator_subtitle_entry.insert(0, config.get('subtitle', ''))
        
        self.creator_layout_var.set(config.get('layout', 'text_only'))
        
        self.creator_text_widget.delete('1.0', tk.END)
        self.creator_text_widget.insert('1.0', config.get('text_content', ''))
    
    def save_creator_content(self):
        """Content Creator Inhalt speichern"""
        page_id = self.creator_selected_page.get()
        signal_info = self.signal_definitions[page_id]
        content_type = signal_info['content_type']
        page_dir = os.path.join(self.content_dir, f"page_{page_id}_{content_type}")
        
        if not os.path.exists(page_dir):
            os.makedirs(page_dir)
        
        config = {
            "title": self.creator_title_entry.get(),
            "subtitle": self.creator_subtitle_entry.get(),
            "layout": self.creator_layout_var.get(),
            "text_content": self.creator_text_widget.get('1.0', tk.END).strip(),
            "background_image": "",
            "video": "",
            "images": []
        }
        
        config_path = os.path.join(page_dir, "config.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        messagebox.showinfo("Erfolg", f"Seite {page_id} wurde gespeichert!")
    
    def preview_creator_content(self):
        """Content Creator Vorschau anzeigen"""
        page_id = self.creator_selected_page.get()
        # Zur Hauptansicht wechseln und Seite anzeigen
        self.hide_content_creator()
        self.load_content_page(page_id)
    
    def open_creator_folder(self):
        """Content Creator Ordner öffnen"""
        page_id = self.creator_selected_page.get()
        signal_info = self.signal_definitions[page_id]
        content_type = signal_info['content_type']
        page_dir = os.path.join(self.content_dir, f"page_{page_id}_{content_type}")
        
        if not os.path.exists(page_dir):
            os.makedirs(page_dir)
        
        self.open_page_folder(page_dir)
        
    def create_multimedia_display(self, parent):
        """Multimedia-Anzeige für Messestand"""
        # Header - doppelt so hoch
        panel_header = tk.Frame(parent, bg=self.colors['background_secondary'], height=100)
        panel_header.pack(fill='x')
        panel_header.pack_propagate(False)
        
        title_label = tk.Label(panel_header,
                              text="🎬 MULTIMEDIA PRÄSENTATION",
                              font=self.fonts['title'],
                              fg=self.colors['text_primary'],
                              bg=self.colors['background_secondary'])
        title_label.pack(pady=30)
        
        # Hauptcontainer für Content
        content_container = tk.Frame(parent, bg=self.colors['background_primary'])
        content_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Multimedia Content Area (Hauptbereich)
        self.content_frame = tk.Frame(content_container, bg=self.colors['background_tertiary'], relief='flat', borderwidth=0)
        self.content_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Navigation Panel (unten) - responsive Höhe
        nav_height = max(80, self.root.winfo_height() // 12)
        nav_panel = tk.Frame(content_container, bg=self.colors['background_secondary'], height=nav_height)
        nav_panel.pack(fill='x')
        nav_panel.pack_propagate(False)
        
        # Navigation Header
        nav_header = tk.Label(nav_panel,
                             text="📱 SEITEN-NAVIGATION",
                             font=self.fonts['subtitle'],
                             fg=self.colors['text_primary'],
                             bg=self.colors['background_secondary'])
        nav_header.pack(pady=(8, 5))
        
        # Navigation Grid
        self.nav_grid = tk.Frame(nav_panel, bg=self.colors['background_secondary'])
        self.nav_grid.pack(fill='x', padx=20, pady=(0, 10))
        
        # Navigation Cards erstellen
        self.nav_cards = {}
        for i, (signal_id, signal_info) in enumerate(self.signal_definitions.items()):
            col = i % 10  # 10 Karten in einer Reihe
            
            card = self.create_nav_card(self.nav_grid, signal_id, signal_info)
            card.grid(row=0, column=col, padx=2, pady=2, sticky='ew')
            self.nav_cards[signal_id] = card
            
            # GUI-Button Klick-Handler für alle Modi
            card.bind("<Button-1>", lambda e, sid=signal_id: self.on_manual_page_select(sid))
            card.icon_label.bind("<Button-1>", lambda e, sid=signal_id: self.on_manual_page_select(sid))
            card.number_label.bind("<Button-1>", lambda e, sid=signal_id: self.on_manual_page_select(sid))
        
        # Grid konfigurieren
        for i in range(10):
            self.nav_grid.columnconfigure(i, weight=1)
        
        # Initialen Content laden
        self.load_content_page(1)
        
    def ensure_content_structure(self):
        """Content-Ordnerstruktur erstellen"""
        if not os.path.exists(self.content_dir):
            os.makedirs(self.content_dir)
        
        # Unterordner für jeden Content-Typ erstellen
        for signal_id, signal_info in self.signal_definitions.items():
            content_type = signal_info['content_type']
            page_dir = os.path.join(self.content_dir, f"page_{signal_id}_{content_type}")
            if not os.path.exists(page_dir):
                os.makedirs(page_dir)
                
                # BumbleB Shuttle Präsentation - Originale Texte
                content_map = {
                    1: {
                        "title": "Schonmal ein automatisiert Shuttle gesehen, das aussieht wie eine Hummel?",
                        "subtitle": "Shuttle fährt los von Bushaltestelle an Bahnhof",
                        "text_content": "🐝 BumbleB - Das Hummel-Shuttle\n\n🚌 Willkommen zur Geschichte eines besonderen Shuttles:\n\n• Sieht aus wie eine Hummel\n• Fährt vollautomatisiert\n• Startet an der Bushaltestelle am Bahnhof\n• Bereit für seine erste Fahrt\n\n🎬 Die Reise beginnt...\n\n✨ Bertrandt Engineering macht das Unmögliche möglich!"
                    },
                    2: {
                        "title": "Es heißt BumbleB – und zum Glück weiß es nicht, dass es eigentlich gar nicht fahren dürfte.",
                        "subtitle": "Männchen von KBA hat Schranke unten und öffnet sie dann, sobald BumbleB ankommt.",
                        "text_content": "🐝 BumbleB und die Bürokratie\n\n🚧 Die Situation:\n• KBA-Beamter steht an der Schranke\n• Schranke ist zunächst unten\n• Offizielle Genehmigungen fehlen noch\n\n✨ Der magische Moment:\n• BumbleB nähert sich der Schranke\n• Der Beamte sieht das Shuttle\n• Schranke öffnet sich wie von selbst\n• Der Weg ist frei!\n\n🎯 Manchmal öffnet Innovation einfach Türen... und Schranken!"
                    },
                    3: {
                        "title": "Doch genau wie die Hummel einfach fliegt – fährt BumbleB einfach los.",
                        "subtitle": "Hält an STOP-Schild und fährt nach 3 Sek weiter",
                        "text_content": "🐝 Die Hummel-Philosophie\n\n🔬 Wissenschaftlich betrachtet:\n• Hummeln sind zu schwer zum Fliegen\n• Ihre Flügel sind zu klein\n• Die Aerodynamik spricht dagegen\n\n🚀 Aber sie fliegen trotzdem!\n\n🛑 BumbleB in Aktion:\n• Erreicht das STOP-Schild\n• Hält ordnungsgemäß an\n• Wartet genau 3 Sekunden\n• Fährt sicher weiter\n\n💡 Innovation kennt keine Grenzen!"
                    },
                    4: {
                        "title": "Automatisiert, sicher, und flexibel einsetzbar",
                        "subtitle": "Müsst ihr noch kreativ werden :)",
                        "text_content": "🤖 BumbleB Technologie-Features\n\n⚡ Vollautomatisierung:\n• Autonome Navigation\n• Intelligente Routenplanung\n• Adaptive Geschwindigkeitsregelung\n\n🛡️ Sicherheit an erster Stelle:\n• 360° Rundum-Sensorik\n• Predictive Safety Analytics\n• Notfall-Reaktionssysteme\n\n🔄 Maximale Flexibilität:\n• Verschiedene Einsatzgebiete\n• Anpassbare Konfigurationen\n• Modulare Systemarchitektur\n\n🎯 Hier könnt ihr kreativ werden! 🎨"
                    },
                    5: {
                        "title": "Egal ob Stadt oder Dorf – sie bringt dich überall sicher hin.",
                        "subtitle": "Ein paar Kühe am Straßenrand oder so (werdet kreativ)",
                        "text_content": "🌍 BumbleB überall einsetzbar\n\n🏙️ In der Stadt:\n• Enge Straßen? Kein Problem!\n• Fußgänger und Radfahrer\n• Komplexer Stadtverkehr\n\n🌾 Auf dem Land:\n• Schmale Landstraßen\n• Unvorhersehbare Situationen\n• Wetterresistente Navigation\n\n🐄 Besondere Herausforderungen:\n• Kühe am Straßenrand\n• Tiere auf der Fahrbahn\n• Kreative Lösungsansätze gefragt\n\n✨ Werdet kreativ mit den Szenarien! 🎨"
                    },
                    6: {
                        "title": "Möglich macht das nicht nur unsere Expertise zusammen mit der klaren Vision, dabei helfen zu wollen automatisierte Shuttles flächendeckend bereitzustellen",
                        "subtitle": "Viele kleine Shuttles stehen am Straßenrand",
                        "text_content": "🎯 Bertrandt Vision & Expertise\n\n🧠 Unsere Expertise:\n• 50+ Jahre Automotive-Erfahrung\n• Führende KI & Machine Learning\n• Sensor-Fusion Technologie\n\n🌐 Klare Vision:\n• Flächendeckende Shuttle-Verfügbarkeit\n• Vernetzte Mobilität für alle\n• Nachhaltige Verkehrslösungen\n\n🚌 Die Zukunft heute:\nViele kleine BumbleB Shuttles\nstehen bereit am Straßenrand\n\n💫 Bereit, wenn Sie sie brauchen!"
                    },
                    7: {
                        "title": "Und mit unserer Plattform violis machen wir es sicher.",
                        "subtitle": "Große Reclame mit violis über der Strecke oder daneben",
                        "text_content": "🛡️ violis - Die Sicherheitsplattform\n\n🔧 violis Plattform-Features:\n• Virtuelle Testumgebungen\n• Real-Time System-Monitoring\n• Predictive Maintenance\n\n📊 Sicherheits-Dashboard:\n• Live-Überwachung aller Shuttles\n• Automatische Anomalie-Erkennung\n• Sofortige Alert-Systeme\n\n🎯 Sichtbare Sicherheit:\n• Große violis Reklame über der Strecke\n• Vertrauen durch Transparenz\n• Technologie, die man sehen kann\n\n✨ violis - Ihr Sicherheitsversprechen!"
                    },
                    8: {
                        "title": "Auf der virtuellen Testplattform werden Funktionen von BumbleB bereitgestellt und getestet – und zwar schneller, effizienter und … als heute üblich.",
                        "subtitle": "HiLs am Straßenrand, BumbleB fährt langsam, HiL fällt auf die Straße und stellt sich wieder auf. Dann irgendwas von violis dazu (auf die Straße gedruckt?) und fährt schneller",
                        "text_content": "🔬 violis Virtuelle Testplattform\n\n⚡ Revolutionäre Test-Geschwindigkeit:\n• Hardware-in-the-Loop (HiL) Systeme\n• Millionen virtueller Testkilometer\n• Schneller, effizienter als je zuvor\n\n🎭 Kreative Test-Szenarien:\n• HiL-Systeme stehen am Straßenrand\n• BumbleB fährt langsam vorbei\n• HiL fällt auf die Straße\n• Stellt sich automatisch wieder auf\n• violis Logo auf die Straße gedruckt\n• BumbleB beschleunigt sicher\n\n🚀 Effizienz-Revolution durch violis!"
                    },
                    9: {
                        "title": "Steuergerätsoftware entsteht und Funktionen werden getestet, noch bevor die Räder der BumbleB rollen.",
                        "subtitle": "Einzelteile der BumbleB am Straßenrand und kleine Menschen, die das zusammenbauen?",
                        "text_content": "💻 Software-First Entwicklung\n\n🔧 Entwicklungsprozess:\n• Software entsteht vor Hardware\n• Virtuelle Prototypen zuerst\n• Funktionen getestet vor dem Bau\n\n🎨 Kreative Visualisierung:\n• BumbleB Einzelteile am Straßenrand\n• Kleine Menschen beim Zusammenbau\n• Software 'schwebt' über den Teilen\n• Digitale Blaupausen werden real\n\n⚡ Vorteile:\n• Frühe Funktionsvalidierung\n• Parallele Entwicklungsprozesse\n• Drastisch reduzierte Entwicklungszeit\n\n🎯 Die Zukunft baut sich selbst!"
                    },
                    10: {
                        "title": "So beschleunigen wir dank violis schon heute mit BumbleB die Entwicklung der Mobilität von morgen.",
                        "subtitle": "Irgendein toller Wow-Effekt (werdet kreativ :) )",
                        "text_content": "🚀 Der große Wow-Effekt!\n\n✨ Bertrandt + violis + BumbleB:\n• Revolutionäre Entwicklungsbeschleunigung\n• Mobilität von morgen - heute schon da\n• Innovation ohne Grenzen\n\n🌟 Spektakuläres Finale:\n• Feuerwerk der Innovation 🎆\n• Hologramm-BumbleB schwebt\n• Zukunfts-Stadtbild entsteht\n• Fliegende Shuttles überall\n• violis-Netzwerk leuchtet auf\n\n🎯 Engineering tomorrow:\nDie Zukunft fährt heute!\n\n💫 Werdet kreativ mit dem Wow-Effekt! 🎨"
                    }
                }
                
                slide_content = content_map.get(signal_id, {
                    "title": signal_info['name'],
                    "subtitle": f"Bertrandt {signal_info['name']}",
                    "text_content": f"Bertrandt Engineering Excellence\n\nModulare Lösungen für {signal_info['name']}"
                })
                
                config = {
                    "title": slide_content["title"],
                    "subtitle": slide_content["subtitle"],
                    "background_image": "",
                    "video": "",
                    "text_content": slide_content["text_content"],
                    "images": [],
                    "layout": "text_only"
                }
                
                config_path = os.path.join(page_dir, "config.json")
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
    
    def load_content_page(self, page_id):
        """Multimedia-Seite laden und anzeigen"""
        self.current_page = page_id
        
        # Alte Inhalte löschen
        if hasattr(self, 'content_frame'):
            # Use right_panel if content_frame doesn't exist
            content_container = getattr(self, 'content_frame', self.right_panel)
            for widget in content_container.winfo_children():
                widget.destroy()
        else:
            # Fallback: right_panel verwenden
            for widget in self.right_panel.winfo_children():
                widget.destroy()
        
        # Content-Konfiguration laden
        signal_info = self.signal_definitions.get(page_id, {})
        content_type = signal_info.get('content_type', 'welcome')
        page_dir = os.path.join(self.content_dir, f"page_{page_id}_{content_type}")
        config_path = os.path.join(page_dir, "config.json")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            # Fallback-Konfiguration
            config = {
                "title": signal_info.get('name', f'Seite {page_id}'),
                "subtitle": f"Seite {page_id}",
                "text_content": f"Seite {page_id} - Inhalt wird geladen...",
                "layout": "text_only"
            }
        
        # Layout basierend auf Konfiguration erstellen
        self.create_content_layout(config, page_dir)
        
        # Navigation aktualisieren
        self.update_navigation(page_id)
    
    def create_content_layout(self, config, page_dir):
        """Content-Layout basierend auf Konfiguration erstellen"""
        layout = config.get('layout', 'text_only')
        
        # Header mit Titel
        # Use right_panel if content_frame doesn't exist
        content_container = getattr(self, 'content_frame', self.right_panel)
        header_frame = tk.Frame(content_container, bg=self.colors['background_secondary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Titel - responsive
        title_label = tk.Label(header_frame,
                              text=config.get('title', 'Titel'),
                              font=self.fonts['display'],
                              fg=self.colors['text_primary'],
                              bg=self.colors['background_secondary'])
        title_label.pack(pady=15)
        
        # Untertitel
        if config.get('subtitle'):
            subtitle_label = tk.Label(header_frame,
                                     text=config.get('subtitle'),
                                     font=self.fonts['subtitle'],
                                     fg=self.colors['accent_primary'],
                                     bg=self.colors['background_secondary'])
            subtitle_label.pack()
        
        # Content Area - responsive Padding
        padding_x = max(10, self.root.winfo_width() // 80)
        padding_y = max(10, self.root.winfo_height() // 60)
        # Bestimme den richtigen Container
        if hasattr(self, 'content_frame'):
            container = self.content_frame
        elif hasattr(self, 'right_panel'):
            container = self.right_panel
        else:
            print("❌ Kein Container für Content gefunden!")
            return
            
        content_area = tk.Frame(container, bg=self.colors['background_tertiary'])
        content_area.pack(fill='both', expand=True, padx=padding_x, pady=padding_y)
        
        # Layout-spezifische Inhalte
        if layout == 'text_only':
            self.create_text_layout(content_area, config)
        elif layout == 'image_text':
            self.create_image_text_layout(content_area, config, page_dir)
        elif layout == 'video_text':
            self.create_video_text_layout(content_area, config, page_dir)
        elif layout == 'fullscreen_image':
            self.create_fullscreen_image_layout(content_area, config, page_dir)
        elif layout == 'fullscreen_video':
            self.create_fullscreen_video_layout(content_area, config, page_dir)
        else:
            self.create_text_layout(content_area, config)
    
    def create_text_layout(self, parent, config):
        """Nur-Text Layout - responsive"""
        text_frame = tk.Frame(parent, bg=self.colors['background_tertiary'])
        text_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Scrollbarer Text mit Scrollbar
        text_container = tk.Frame(text_frame, bg=self.colors['background_tertiary'])
        text_container.pack(fill='both', expand=True)
        
        # Text Widget
        text_widget = tk.Text(text_container,
                             font=self.fonts['label'],
                             bg=self.colors['background_secondary'],
                             fg=self.colors['text_primary'],
                             wrap=tk.WORD,
                             relief='flat',
                             borderwidth=0,
                             padx=15,
                             pady=15)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(text_container, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Text einfügen
        text_content = config.get('text_content', 'Kein Text verfügbar.')
        text_widget.insert('1.0', text_content)
        text_widget.config(state='disabled')  # Nur lesen
    
    def create_image_text_layout(self, parent, config, page_dir):
        """Bild + Text Layout"""
        # Horizontal aufteilen
        left_frame = tk.Frame(parent, bg=self.colors['background_tertiary'])
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        right_frame = tk.Frame(parent, bg=self.colors['background_tertiary'])
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Bild laden
        self.load_image_to_frame(left_frame, config, page_dir)
        
        # Text
        self.create_text_layout(right_frame, config)
    
    def create_video_text_layout(self, parent, config, page_dir):
        """Video + Text Layout"""
        # Vertikal aufteilen
        top_frame = tk.Frame(parent, bg=self.colors['background_tertiary'])
        top_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        bottom_frame = tk.Frame(parent, bg=self.colors['background_tertiary'], height=200)
        bottom_frame.pack(fill='x', pady=(10, 0))
        bottom_frame.pack_propagate(False)
        
        # Video-Platzhalter
        self.create_video_placeholder(top_frame, config, page_dir)
        
        # Text
        self.create_text_layout(bottom_frame, config)
    
    def create_fullscreen_image_layout(self, parent, config, page_dir):
        """Vollbild-Bild Layout"""
        self.load_image_to_frame(parent, config, page_dir, fullscreen=True)
    
    def create_fullscreen_video_layout(self, parent, config, page_dir):
        """Vollbild-Video Layout"""
        self.create_video_placeholder(parent, config, page_dir, fullscreen=True)
    
    def load_image_to_frame(self, parent, config, page_dir, fullscreen=False):
        """Bild in Frame laden"""
        image_path = None
        
        # Bild aus Konfiguration
        if config.get('background_image'):
            image_path = os.path.join(page_dir, config['background_image'])
        
        # Erstes Bild aus images-Liste
        elif config.get('images') and len(config['images']) > 0:
            image_path = os.path.join(page_dir, config['images'][0])
        
        # Fallback: Erstes gefundene Bild im Ordner
        if not image_path or not os.path.exists(image_path):
            for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                for file in os.listdir(page_dir):
                    if file.lower().endswith(ext):
                        image_path = os.path.join(page_dir, file)
                        break
                if image_path:
                    break
        
        if image_path and os.path.exists(image_path):
            try:
                # Bild laden und skalieren
                image = Image.open(image_path)
                
                if fullscreen:
                    # Vollbild-Größe - responsive
                    max_width = self.root.winfo_width() - 100
                    max_height = self.root.winfo_height() - 200
                else:
                    # Halbe Größe - responsive
                    max_width = (self.root.winfo_width() - 400) // 2
                    max_height = (self.root.winfo_height() - 300) // 2
                
                # Proportional skalieren
                image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                # Label für Bild
                image_label = tk.Label(parent, image=photo, bg=self.colors['background_tertiary'])
                image_label.image = photo  # Referenz behalten
                image_label.pack(expand=True)
                
            except Exception as e:
                # Fehler-Platzhalter
                error_label = tk.Label(parent,
                                      text=f"🖼️ Bild konnte nicht geladen werden\n{str(e)}",
                                      font=self.fonts['label'],
                                      fg=self.colors['accent_tertiary'],
                                      bg=self.colors['background_tertiary'])
                error_label.pack(expand=True)
        else:
            # Kein Bild gefunden
            placeholder_label = tk.Label(parent,
                                        text="🖼️ Kein Bild verfügbar\n\nFügen Sie Bilder in den Ordner hinzu:\n" + page_dir,
                                        font=self.fonts['label'],
                                        fg=self.colors['text_secondary'],
                                        bg=self.colors['background_tertiary'],
                                        justify='center')
            placeholder_label.pack(expand=True)
    
    def create_video_placeholder(self, parent, config, page_dir, fullscreen=False):
        """Video-Platzhalter erstellen"""
        # Video-Unterstützung würde hier implementiert werden
        # Für jetzt: Platzhalter
        video_frame = tk.Frame(parent, bg=self.colors['background_secondary'], relief='solid', borderwidth=2)
        video_frame.pack(fill='both', expand=True)
        
        placeholder_label = tk.Label(video_frame,
                                    text="🎬 VIDEO BEREICH\n\nVideo-Unterstützung wird implementiert\n\nUnterstützte Formate:\n• MP4\n• AVI\n• MOV",
                                    font=self.fonts['subtitle'],
                                    fg=self.colors['text_secondary'],
                                    bg=self.colors['background_secondary'],
                                    justify='center')
        placeholder_label.pack(expand=True)
    
    def safe_page_select(self, page_id):
        """Sichere Seitenauswahl mit Cleanup"""
        try:
            # Vorherige Seite cleanup
            if hasattr(self, 'current_page_id') and self.current_page_id != page_id:
                self.cleanup_current_page()
            
            # Neue Seite laden
            self.on_manual_page_select(page_id)
            self.current_page_id = page_id
            
            # Navigation aktualisieren
            self.update_navigation(page_id)
            
            print(f"🎯 Seite {page_id} erfolgreich geladen")
        except Exception as e:
            print(f"❌ Fehler beim Seitenwechsel: {e}")
    
    def cleanup_current_page(self):
        """Aktuelle Seite ordnungsgemäß schließen"""
        try:
            # Multimedia cleanup
            if hasattr(self, 'multimedia_frame'):
                for widget in self.multimedia_frame.winfo_children():
                    widget.destroy()
            
            # Timer cleanup falls vorhanden
            if hasattr(self, 'auto_demo_timer') and self.auto_demo_timer:
                self.root.after_cancel(self.auto_demo_timer)
                self.auto_demo_timer = None
                
        except Exception as e:
            print(f"⚠️ Cleanup Warnung: {e}")

    def update_navigation(self, active_page):
        """Navigation aktualisieren - Header und Sidebar"""
        try:
            # Header Navigation aktualisieren
            if hasattr(self, 'nav_buttons'):
                for page_id, button in self.nav_buttons.items():
                    try:
                        if page_id == active_page:
                            button.config(bg=self.colors['accent_primary'], 
                                        fg=self.colors['text_primary'])
                        else:
                            button.config(bg=self.colors['background_primary'], 
                                        fg=self.colors['text_secondary'])
                    except tk.TclError:
                        # Button existiert nicht mehr, aus Dictionary entfernen
                        pass
            
            # Sidebar Navigation aktualisieren (nur wenn nav_cards existieren und gültig sind)
            if hasattr(self, 'nav_cards') and self.nav_cards:
                for page_id, card in list(self.nav_cards.items()):
                    try:
                        if page_id == active_page:
                            # Aktive Seite hervorheben
                            card.config(bg=self.colors['background_secondary'], relief='solid', borderwidth=2)
                            if hasattr(card, 'card_header'):
                                card.card_header.config(bg=self.colors['accent_primary'])
                        else:
                            # Andere Seiten zurücksetzen
                            card.config(bg=self.colors['background_tertiary'], relief='flat', borderwidth=1)
                            if hasattr(card, 'card_header') and hasattr(card, 'signal_info'):
                                card.card_header.config(bg=card.signal_info['color'])
                    except tk.TclError:
                        # Card existiert nicht mehr, aus Dictionary entfernen
                        del self.nav_cards[page_id]
        except Exception as e:
            print(f"⚠️ Navigation-Update Warnung: {e}")
    
    def toggle_fullscreen(self, event=None):
        """Vollbild umschalten (F11)"""
        self.fullscreen = not self.fullscreen
        self.root.attributes('-fullscreen', self.fullscreen)
        if self.fullscreen:
            print("🖥️ Vollbild aktiviert (ESC zum Beenden)")
        else:
            print("🖥️ Fenstermodus aktiviert")
    
    def exit_fullscreen(self, event=None):
        """Vollbild beenden (ESC)"""
        self.fullscreen = False
        self.root.attributes('-fullscreen', False)
        print("🖥️ Vollbild beendet")
        
    def create_nav_card(self, parent, signal_id, signal_info):
        """Minimale Navigation-Karte für sehr schmale Sidebar (1/10)"""
        # Sehr kompakte Kartengröße für 1/10 Breite
        card_width = max(35, self.root.winfo_width() // 50)
        card_height = max(25, self.root.winfo_height() // 30)
        
        card = tk.Frame(parent,
                       bg=self.colors['background_tertiary'],
                       relief='flat',
                       borderwidth=1,
                       width=card_width,
                       height=card_height)
        
        # Minimaler Card Header
        card_header = tk.Frame(card, bg=signal_info['color'], height=2)
        card_header.pack(fill='x')
        card_header.pack_propagate(False)
        
        # Minimaler Card Content
        card_content = tk.Frame(card, bg=self.colors['background_tertiary'])
        card_content.pack(fill='both', expand=True, padx=2, pady=1)
        
        # Kleines Icon
        icon_size = max(8, self.root.winfo_width() // 120)
        icon_label = tk.Label(card_content,
                             text=signal_info['icon'],
                             font=('Helvetica Neue', icon_size),
                             bg=self.colors['background_tertiary'])
        icon_label.pack()
        
        # Kleine Nummer
        number_label = tk.Label(card_content,
                               text=str(signal_id),
                               font=('Helvetica Neue', 8, 'bold'),
                               fg=signal_info['color'],
                               bg=self.colors['background_tertiary'])
        number_label.pack()
        
        # Referenzen speichern
        card.icon_label = icon_label
        card.number_label = number_label
        card.signal_info = signal_info
        card.card_header = card_header
        
        return card
    
            
    def create_signal_card(self, parent, signal_id, signal_info):
        """Dark Theme Signal-Karte"""
        card = tk.Frame(parent,
                       bg=self.colors['background_tertiary'],
                       relief='flat',
                       borderwidth=1,
                       width=220,
                       height=160)
        
        # Dark Theme Card Header mit Farbe
        card_header = tk.Frame(card, bg=signal_info['color'], height=8)
        card_header.pack(fill='x')
        card_header.pack_propagate(False)
        
        # Card Content
        card_content = tk.Frame(card, bg=self.colors['background_tertiary'])
        card_content.pack(fill='both', expand=True, padx=15, pady=10)
        
        # Icon
        icon_label = tk.Label(card_content,
                             text=signal_info['icon'],
                             font=('Helvetica Neue', 28),
                             bg=self.colors['background_tertiary'])
        icon_label.pack(pady=(5, 10))
        
        # Signal Nummer
        number_label = tk.Label(card_content,
                               text=f"SIGNAL {signal_id}",
                               font=self.fonts['button'],
                               fg=signal_info['color'],
                               bg=self.colors['background_tertiary'])
        number_label.pack()
        
        # Signal Name
        name_label = tk.Label(card_content,
                             text=signal_info['name'].upper(),
                             font=self.fonts['label'],
                             fg=self.colors['text_primary'],
                             bg=self.colors['background_tertiary'],
                             wraplength=180,
                             justify='center')
        name_label.pack(pady=(5, 10))
        
        # Status Indikator
        status_indicator = tk.Frame(card,
                                   bg=self.colors['background_secondary'],
                                   height=4)
        status_indicator.pack(fill='x', side='bottom')
        
        # Referenzen speichern
        card.icon_label = icon_label
        card.number_label = number_label
        card.name_label = name_label
        card.status_indicator = status_indicator
        card.signal_info = signal_info
        card.card_header = card_header
        
        return card
        
    def create_footer(self):
        """Dark Theme Footer"""
        # Akzent-Linie über Footer
        separator = tk.Frame(self.root, bg=self.colors['accent_primary'], height=2)
        separator.pack(fill='x', side='bottom')
        
        footer_frame = tk.Frame(self.root, bg=self.colors['background_secondary'], height=45)
        footer_frame.pack(fill='x', side='bottom')
        footer_frame.pack_propagate(False)
        
        # Copyright (links)
        footer_text = tk.Label(footer_frame,
                              text="© 2024 Bertrandt AG | ESP32 Monitor System v2.0 | Engineering tomorrow",
                              font=self.fonts['label'],
                              fg=self.colors['text_primary'],
                              bg=self.colors['background_secondary'])
        footer_text.pack(side='left', padx=30, pady=12)
        
        # System Info (rechts)
        info_frame = tk.Frame(footer_frame, bg=self.colors['background_secondary'])
        info_frame.pack(side='right', padx=30, pady=12)
        
        self.fps_label = tk.Label(info_frame,
                                 text="FPS: --",
                                 font=self.fonts['label'],
                                 fg=self.colors['accent_secondary'],
                                 bg=self.colors['background_secondary'])
        self.fps_label.pack(side='right', padx=(20, 0))
        
        # Standort
        location_label = tk.Label(info_frame,
                                 text="Standort: Deutschland",
                                 font=self.fonts['label'],
                                 fg=self.colors['text_secondary'],
                                 bg=self.colors['background_secondary'])
        location_label.pack(side='right')
        
    def setup_serial(self):
        """Serial-Verbindung einrichten oder Dev Mode aktivieren"""
        try:
            self.serial_connection = serial.Serial(self.esp32_port, 115200, timeout=1)
            time.sleep(2)
            self.connection_status.config(text="● Online", fg=self.colors['accent_secondary'])
            self.dev_mode = False
            self.start_serial_reading()
        except Exception as e:
            # Dev Mode aktivieren
            self.dev_mode = True
            self.connection_status.config(text="● Dev Mode", fg=self.colors['accent_warning'])
            self.start_dev_mode()
            print(f"🔧 Dev Mode aktiviert - Keine Hardware gefunden: {e}")
    
    def start_dev_mode(self):
        """Dev Mode starten - Simuliert Arduino-Signale"""
        print("🔧 Dev Mode gestartet - Simuliere Arduino-Signale...")
        
        # Dev Mode Info anzeigen
        self.show_dev_mode_info()
        
        # Automatische Demo starten (optional) - aber erst nach GUI-Initialisierung
        self.root.after(1000, self.start_auto_demo)
    
    def show_dev_mode_info(self):
        """Dev Mode Information anzeigen"""
        dev_info = tk.Toplevel(self.root)
        dev_info.title("🔧 Dev Mode")
        # Auf Monitor 2 positionieren
        x = self.monitor_x + 100
        y = 100
        dev_info.geometry(f"500x400+{x}+{y}")
        dev_info.configure(bg=self.colors['background_primary'])
        
        # Header
        header_label = tk.Label(dev_info,
                               text="🔧 ENTWICKLERMODUS AKTIV",
                               font=self.fonts['title'],
                               fg=self.colors['accent_warning'],
                               bg=self.colors['background_primary'])
        header_label.pack(pady=20)
        
        # Info Text
        info_text = """
Keine Arduino/ESP32 Hardware gefunden!

Der Dev Mode ist aktiviert mit folgenden Features:

🎮 GUI-STEUERUNG:
• Klicken Sie auf die Seiten-Buttons (1-10)
• Nutzen Sie die Navigations-Karten
• Verwenden Sie die Schnellzugriff-Buttons

🤖 AUTO-DEMO:
• Automatischer Seitenwechsel alle 5 Sekunden
• Zeigt alle Multimedia-Inhalte
• Perfekt zum Testen und Präsentationen

🛠️ ENTWICKLUNG:
• Alle Multimedia-Features verfügbar
• Content Manager funktioniert normal
• Kein Arduino/ESP32 erforderlich
• Vollständig buttonbasierte Bedienung

Schließen Sie Hardware an und starten Sie neu
für den normalen Betrieb mit Arduino-Steuerung.
        """
        
        info_label = tk.Label(dev_info,
                             text=info_text,
                             font=self.fonts['label'],
                             fg=self.colors['text_primary'],
                             bg=self.colors['background_primary'],
                             justify='left')
        info_label.pack(padx=20, pady=10)
        
        # Buttons
        button_frame = tk.Frame(dev_info, bg=self.colors['background_primary'])
        button_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Button(button_frame,
                  text="🤖 AUTO-DEMO STARTEN",
                  style='Success.TButton',
                  command=lambda: [self.start_auto_demo(), dev_info.destroy()]).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame,
                  text="⏹️ AUTO-DEMO STOPPEN",
                  style='Warning.TButton',
                  command=self.stop_auto_demo).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame,
                  text="✅ OK",
                  style='Primary.TButton',
                  command=dev_info.destroy).pack(side='right')
    
    def start_auto_demo(self):
        """Automatische Demo starten"""
        if self.dev_mode:
            self.stop_auto_demo()  # Vorherige Demo stoppen
            self.auto_demo_page = 1
            self.demo_running = True
            self.schedule_next_demo_page()
            print("🤖 Auto-Demo gestartet")
    
    def stop_auto_demo(self):
        """Automatische Demo stoppen"""
        if hasattr(self, 'dev_timer') and self.dev_timer:
            self.root.after_cancel(self.dev_timer)
            self.dev_timer = None
            self.demo_running = False
            print("⏹️ Auto-Demo gestoppt")
    
    def schedule_next_demo_page(self):
        """Nächste Demo-Seite planen"""
        if self.dev_mode:
            # Aktuelle Seite laden
            self.simulate_signal(self.auto_demo_page)
            
            # Nächste Seite vorbereiten
            self.auto_demo_page += 1
            if self.auto_demo_page > 10:
                self.auto_demo_page = 1
            
            # Timer für nächste Seite setzen (5 Sekunden)
            self.dev_timer = self.root.after(5000, self.schedule_next_demo_page)
    
    def simulate_signal(self, signal_id):
        """Arduino-Signal simulieren"""
        if self.dev_mode:
            print(f"🎮 Dev Mode: Simuliere Signal {signal_id}")
            self.update_signal(signal_id)
            
            # Client Count simulieren
            import random
            client_count = random.randint(0, 3)
            self.update_client_count(client_count)
            
    def start_serial_reading(self):
        """Serial-Daten lesen starten"""
        self.running = True
        self.serial_thread = threading.Thread(target=self.read_serial_data)
        self.serial_thread.daemon = True
        self.serial_thread.start()
        
        # GUI-Update-Loop starten
        self.process_serial_data()
        
    def read_serial_data(self):
        """Serial-Daten in separatem Thread lesen"""
        while self.running and self.serial_connection:
            try:
                if self.serial_connection.in_waiting > 0:
                    line = self.serial_connection.readline().decode('utf-8').strip()
                    if line.startswith("SIGNAL:"):
                        signal_value = int(line.split(":")[1])
                        self.data_queue.put(('signal', signal_value))
                    elif line.startswith("Clients:"):
                        client_count = int(line.split(":")[1].strip())
                        self.data_queue.put(('clients', client_count))
            except Exception as e:
                print(f"Serial read error: {e}")
                time.sleep(0.1)
                
    def process_serial_data(self):
        """Serial-Daten verarbeiten (GUI-Thread)"""
        try:
            while not self.data_queue.empty():
                data_type, value = self.data_queue.get_nowait()
                
                if data_type == 'signal':
                    self.update_signal(value)
                elif data_type == 'clients':
                    self.update_client_count(value)
                    
        except queue.Empty:
            pass
        
        # Nächste Verarbeitung planen
        self.root.after(50, self.process_serial_data)
        
    def update_signal(self, signal_id):
        """Signal-Anzeige mit Bertrandt Design aktualisieren"""
        if signal_id in self.signal_definitions:
            self.current_signal = signal_id
            signal_info = self.signal_definitions[signal_id]
            
            # WICHTIG: Multimedia-Seite wechseln (nur wenn im Home-Tab)
            if hasattr(self, 'current_tab') and self.current_tab == "home":
                self.load_content_page(signal_id)
            
            # Navigation aktualisieren
            self.update_navigation(signal_id)
            
            # Historie aktualisieren
            self.signal_history.append({
                'signal': signal_id,
                'name': signal_info['name'],
                'timestamp': time.time()
            })
            
            # Nur letzte 100 Einträge behalten
            if len(self.signal_history) > 100:
                self.signal_history.pop(0)
                
    def update_client_count(self, count):
        """Client-Anzahl mit Bertrandt Styling aktualisieren"""
        self.client_count = count
        self.client_count_label.config(text=str(count))
        
        # Bertrandt Farben und Status je nach Anzahl
        if count == 0:
            color = self.colors['accent_tertiary']
            status_text = "KEINE VERBINDUNG"
        elif count == 1:
            color = self.colors['accent_secondary']
            status_text = "OPTIMAL VERBUNDEN"
        else:
            color = self.colors['accent_primary']
            status_text = f"{count} CLIENTS AKTIV"
            
        self.client_count_label.config(fg=color)
        if hasattr(self, 'client_status_text'):
            self.client_status_text.config(text=status_text, fg=color)
        
    def update_time(self):
        """Zeit im Header mit Bertrandt Format aktualisieren"""
        current_time = time.strftime("%H:%M:%S")
        current_date = time.strftime("%d.%m.%Y")
        self.time_label.config(text=f"{current_date} | {current_time}")
        self.root.after(1000, self.update_time)
        
    def restart_connection(self):
        """Verbindung neu starten"""
        if self.serial_connection:
            self.serial_connection.close()
        self.setup_serial()
        
    def show_history(self):
        """Signal-Historie anzeigen"""
        history_window = tk.Toplevel(self.root)
        history_window.title("Signal Historie")
        # Auf Monitor 2 positionieren
        x = self.monitor_x + 150
        y = 150
        history_window.geometry(f"600x400+{x}+{y}")
        history_window.configure(bg=self.colors['background_primary'])
        
        # Historie-Liste
        listbox = tk.Listbox(history_window, 
                            font=self.fonts['label'],
                            bg=self.colors['background_tertiary'],
                            fg=self.colors['text_primary'],
                            selectbackground=self.colors['accent_primary'])
        listbox.pack(fill='both', expand=True, padx=20, pady=20)
        
        for entry in reversed(self.signal_history[-20:]):  # Letzte 20 Einträge
            timestamp = time.strftime("%H:%M:%S", time.localtime(entry['timestamp']))
            listbox.insert(0, f"{timestamp} - Signal {entry['signal']}: {entry['name']}")
            
    def show_settings(self):
        """Einstellungen anzeigen"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Einstellungen")
        # Auf Monitor 2 positionieren
        x = self.monitor_x + 200
        y = 200
        settings_window.geometry(f"400x300+{x}+{y}")
        settings_window.configure(bg=self.colors['background_primary'])
        
        tk.Label(settings_window,
                text="ESP32 Port:",
                font=self.fonts['subtitle'],
                fg=self.colors['text_primary'],
                bg=self.colors['background_primary']).pack(pady=10)
        
        port_entry = tk.Entry(settings_window, 
                             font=self.fonts['body'],
                             bg=self.colors['background_secondary'],
                             fg=self.colors['text_primary'],
                             insertbackground=self.colors['text_primary'])
        port_entry.insert(0, self.esp32_port)
        port_entry.pack(pady=5)
        
        def save_settings():
            self.esp32_port = port_entry.get()
            self.esp32_port_label.config(text=f"✅ {self.esp32_port}", fg=self.colors['accent_secondary'])
            settings_window.destroy()
            
        ttk.Button(settings_window,
                  text="SPEICHERN",
                  style='Primary.TButton',
                  command=save_settings).pack(pady=20)
    
    def show_content_manager(self):
        """Content Manager anzeigen"""
        content_window = tk.Toplevel(self.root)
        content_window.title("Content Manager")
        # Auf Monitor 2 positionieren
        x = self.monitor_x + 50
        y = 50
        content_window.geometry(f"800x600+{x}+{y}")
        content_window.configure(bg=self.colors['background_primary'])
        
        # Header
        header_label = tk.Label(content_window,
                               text="🎬 CONTENT MANAGER",
                               font=self.fonts['title'],
                               fg=self.colors['text_primary'],
                               bg=self.colors['background_primary'])
        header_label.pack(pady=20)
        
        # Info
        info_label = tk.Label(content_window,
                             text="Verwalten Sie Multimedia-Inhalte für alle 10 Seiten",
                             font=self.fonts['subtitle'],
                             fg=self.colors['accent_primary'],
                             bg=self.colors['background_primary'])
        info_label.pack(pady=(0, 20))
        
        # Content-Ordner anzeigen
        content_frame = tk.Frame(content_window, bg=self.colors['background_tertiary'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Scrollbare Liste
        canvas = tk.Canvas(content_frame, bg=self.colors['background_tertiary'])
        scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['background_tertiary'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Content für jede Seite anzeigen
        for signal_id, signal_info in self.signal_definitions.items():
            self.create_content_item(scrollable_frame, signal_id, signal_info)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        button_frame = tk.Frame(content_window, bg=self.colors['background_primary'])
        button_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Button(button_frame,
                  text="📁 CONTENT-ORDNER ÖFFNEN",
                  style='Primary.TButton',
                  command=self.open_content_folder).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame,
                  text="🔄 CONTENT NEULADEN",
                  style='Success.TButton',
                  command=lambda: self.load_content_page(self.current_page)).pack(side='left', padx=(0, 10))
        
        ttk.Button(button_frame,
                  text="❌ SCHLIESSEN",
                  style='Warning.TButton',
                  command=content_window.destroy).pack(side='right')
    
    def create_content_item(self, parent, signal_id, signal_info):
        """Content-Item für eine Seite erstellen"""
        item_frame = tk.Frame(parent, bg=self.colors['background_secondary'], relief='solid', borderwidth=1)
        item_frame.pack(fill='x', pady=5, padx=10)
        
        # Header
        header_frame = tk.Frame(item_frame, bg=signal_info['color'], height=30)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(header_frame,
                               text=f"{signal_info['icon']} Seite {signal_id}: {signal_info['name']}",
                               font=self.fonts['button'],
                               fg=self.colors['text_primary'],
                               bg=signal_info['color'])
        header_label.pack(pady=5)
        
        # Content Info
        content_frame = tk.Frame(item_frame, bg=self.colors['background_secondary'])
        content_frame.pack(fill='x', padx=10, pady=10)
        
        # Ordner-Pfad
        content_type = signal_info['content_type']
        page_dir = os.path.join(self.content_dir, f"page_{signal_id}_{content_type}")
        
        path_label = tk.Label(content_frame,
                             text=f"📁 {page_dir}",
                             font=self.fonts['label'],
                             fg=self.colors['text_secondary'],
                             bg=self.colors['background_secondary'],
                             anchor='w')
        path_label.pack(fill='x')
        
        # Dateien auflisten
        if os.path.exists(page_dir):
            files = os.listdir(page_dir)
            if files:
                files_text = "📄 Dateien: " + ", ".join(files[:3])
                if len(files) > 3:
                    files_text += f" ... (+{len(files)-3} weitere)"
            else:
                files_text = "📄 Keine Dateien"
        else:
            files_text = "📄 Ordner nicht gefunden"
        
        files_label = tk.Label(content_frame,
                              text=files_text,
                              font=self.fonts['label'],
                              fg=self.colors['text_primary'],
                              bg=self.colors['background_secondary'],
                              anchor='w')
        files_label.pack(fill='x')
        
        # Buttons
        btn_frame = tk.Frame(content_frame, bg=self.colors['background_secondary'])
        btn_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Button(btn_frame,
                  text="📁 ÖFFNEN",
                  command=lambda: self.open_page_folder(page_dir)).pack(side='left', padx=(0, 5))
        
        ttk.Button(btn_frame,
                  text="👁️ VORSCHAU",
                  command=lambda: self.load_content_page(signal_id)).pack(side='left')
    
    def open_content_folder(self):
        """Haupt-Content-Ordner öffnen"""
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", self.content_dir])
        elif sys.platform == "win32":  # Windows
            subprocess.run(["explorer", self.content_dir])
        else:  # Linux
            subprocess.run(["xdg-open", self.content_dir])
    
    def open_page_folder(self, page_dir):
        """Spezifischen Seiten-Ordner öffnen"""
        if not os.path.exists(page_dir):
            os.makedirs(page_dir)
        
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", page_dir])
        elif sys.platform == "win32":  # Windows
            subprocess.run(["explorer", page_dir])
        else:  # Linux
            subprocess.run(["xdg-open", page_dir])
                  
    def scan_ports(self):
        """Verfügbare Serial-Ports scannen"""
        ports = []
        
        # Linux/Mac Ports
        for pattern in ['/dev/ttyUSB*', '/dev/ttyACM*', '/dev/cu.usbserial*', '/dev/cu.usbmodem*']:
            ports.extend(glob.glob(pattern))
        
        # Windows Ports (falls auf Windows)
        if sys.platform.startswith('win'):
            import serial.tools.list_ports
            ports.extend([port.device for port in serial.tools.list_ports.comports()])
        
        # Combobox aktualisieren
        self.flash_port_combo['values'] = ports
        if ports:
            self.flash_port_combo.set(ports[0])
            self.flash_status.config(text=f"Gefunden: {len(ports)} Port(s)")
        else:
            self.flash_status.config(text="Keine Ports gefunden")
    
    def on_device_change(self):
        """Geräte-Auswahl geändert"""
        device = self.device_var.get()
        if device == "ESP32":
            self.flash_btn.config(text="📱 ESP32 FLASHEN")
            self.current_sketch_path = self.esp32_sketch_path
            self.hint_title.config(text="💡 ESP32 WICHTIG:")
            self.hint_text.config(text="Boot-Button drücken wenn\n'Connecting...' erscheint!")
            self.hint_frame.config(bg=self.colors['accent_tertiary'])
            self.hint_title.config(bg=self.colors['accent_tertiary'])
            self.hint_text.config(bg=self.colors['accent_tertiary'])
        else:  # GIGA
            self.flash_btn.config(text="🔧 GIGA FLASHEN")
            self.current_sketch_path = self.giga_sketch_path
            self.hint_title.config(text="💡 GIGA INFO:")
            self.hint_text.config(text="Automatisches Flashen\nkein Button nötig!")
            self.hint_frame.config(bg=self.colors['accent_secondary'])
            self.hint_title.config(bg=self.colors['accent_secondary'])
            self.hint_text.config(bg=self.colors['accent_secondary'])
        
        sketch_name = os.path.basename(self.current_sketch_path)
        self.flash_status.config(text=f"Gerät: {device}, Sketch: {sketch_name}")

    def select_sketch(self):
        """Arduino Sketch auswählen"""
        initial_dir = os.path.dirname(self.current_sketch_path)
        sketch_dir = filedialog.askdirectory(
            title="Arduino Sketch Ordner auswählen",
            initialdir=initial_dir
        )
        if sketch_dir:
            self.current_sketch_path = sketch_dir
            sketch_name = os.path.basename(sketch_dir)
            device = self.device_var.get()
            self.flash_status.config(text=f"Gerät: {device}, Sketch: {sketch_name}")
    
    def check_arduino_cli(self):
        """Arduino CLI verfügbarkeit prüfen"""
        try:
            result = subprocess.run(['arduino-cli', 'version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def install_arduino_cli(self):
        """Arduino CLI installieren"""
        self.flash_status.config(text="Installiere Arduino CLI...")
        try:
            # Download und Installation
            install_cmd = "curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh"
            subprocess.run(install_cmd, shell=True, check=True)
            
            # Core installieren
            subprocess.run(['arduino-cli', 'core', 'update-index'], check=True)
            subprocess.run(['arduino-cli', 'core', 'install', 'esp32:esp32'], check=True)
            
            return True
        except Exception as e:
            self.flash_status.config(text=f"Installation fehlgeschlagen: {e}")
            return False
    
    def flash_device(self):
        """Aktuell ausgewähltes Gerät flashen"""
        device = self.device_var.get()
        if device == "ESP32":
            self.flash_esp32()
        else:
            self.flash_giga()
    
    def flash_esp32(self):
        """ESP32 flashen"""
        if not self.flash_port_var.get():
            messagebox.showerror("Fehler", "Bitte wählen Sie einen Port aus!")
            return
        
        if not os.path.exists(self.current_sketch_path):
            messagebox.showerror("Fehler", "ESP32 Sketch-Pfad nicht gefunden!")
            return
        
        # Arduino CLI prüfen
        if not self.check_arduino_cli():
            response = messagebox.askyesno(
                "Arduino CLI nicht gefunden",
                "Arduino CLI ist nicht installiert. Soll es automatisch installiert werden?"
            )
            if response:
                if not self.install_arduino_cli():
                    return
            else:
                return
        
        # Flash-Thread starten
        self.flash_btn.config(state='disabled', text="⏳ Flashe ESP32...")
        flash_thread = threading.Thread(target=self._flash_esp32_worker)
        flash_thread.daemon = True
        flash_thread.start()
    
    def flash_giga(self):
        """Arduino GIGA flashen"""
        if not self.flash_port_var.get():
            messagebox.showerror("Fehler", "Bitte wählen Sie einen Port aus!")
            return
        
        if not os.path.exists(self.current_sketch_path):
            messagebox.showerror("Fehler", "GIGA Sketch-Pfad nicht gefunden!")
            return
        
        # Arduino CLI prüfen
        if not self.check_arduino_cli():
            response = messagebox.askyesno(
                "Arduino CLI nicht gefunden",
                "Arduino CLI ist nicht installiert. Soll es automatisch installiert werden?"
            )
            if response:
                if not self.install_arduino_cli():
                    return
            else:
                return
        
        # Flash-Thread starten
        self.flash_btn.config(state='disabled', text="⏳ Flashe GIGA...")
        flash_thread = threading.Thread(target=self._flash_giga_worker)
        flash_thread.daemon = True
        flash_thread.start()
    
    def flash_both_devices(self):
        """Beide Geräte nacheinander flashen"""
        response = messagebox.askyesno(
            "Beide Geräte flashen",
            "Sollen ESP32 und Arduino GIGA nacheinander geflasht werden?\n\n" +
            "1. Zuerst wird Arduino GIGA geflasht\n" +
            "2. Dann ESP32 (Boot-Button bereithalten!)"
        )
        if response:
            self.flash_btn.config(state='disabled', text="⏳ Flashe beide...")
            flash_thread = threading.Thread(target=self._flash_both_worker)
            flash_thread.daemon = True
            flash_thread.start()
    
    def _flash_esp32_worker(self):
        """ESP32 Flash-Prozess in separatem Thread"""
        try:
            port = self.flash_port_var.get()
            
            # Status Updates im GUI-Thread
            self.root.after(0, lambda: self.flash_status.config(text="Kompiliere ESP32 Sketch..."))
            
            # Kompilieren
            compile_cmd = [
                'arduino-cli', 'compile',
                '--fqbn', 'esp32:esp32:esp32',
                self.esp32_sketch_path
            ]
            
            result = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                self.root.after(0, lambda: self.flash_status.config(text="ESP32 Kompilierung fehlgeschlagen"))
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"ESP32 Kompilierung fehlgeschlagen:\n{result.stderr}"))
                return
            
            # Upload
            self.root.after(0, lambda: self.flash_status.config(text="ESP32 Upload... BOOT-BUTTON DRÜCKEN!"))
            
            upload_cmd = [
                'arduino-cli', 'upload',
                '-p', port,
                '--fqbn', 'esp32:esp32:esp32',
                self.esp32_sketch_path
            ]
            
            result = subprocess.run(upload_cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.root.after(0, lambda: self.flash_status.config(text="✅ ESP32 Flash erfolgreich!"))
                self.root.after(0, lambda: messagebox.showinfo("Erfolg", "ESP32 erfolgreich geflasht!"))
                
                # Verbindung neu starten nach kurzer Pause
                self.root.after(3000, self.restart_connection)
            else:
                self.root.after(0, lambda: self.flash_status.config(text="❌ ESP32 Flash fehlgeschlagen"))
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"ESP32 Upload fehlgeschlagen:\n{result.stderr}"))
                
        except subprocess.TimeoutExpired:
            self.root.after(0, lambda: self.flash_status.config(text="❌ ESP32 Timeout"))
            self.root.after(0, lambda: messagebox.showerror("Fehler", "ESP32 Flash-Prozess Timeout. Boot-Button gedrückt?"))
        except Exception as e:
            self.root.after(0, lambda: self.flash_status.config(text=f"❌ ESP32 Fehler: {e}"))
            self.root.after(0, lambda: messagebox.showerror("Fehler", f"ESP32 Flash-Fehler:\n{e}"))
        finally:
            self.root.after(0, lambda: self.flash_btn.config(state='normal', text="📱 ESP32 FLASHEN"))
    
    def _flash_giga_worker(self):
        """Arduino GIGA Flash-Prozess in separatem Thread"""
        try:
            port = self.flash_port_var.get()
            
            # Status Updates im GUI-Thread
            self.root.after(0, lambda: self.flash_status.config(text="Kompiliere GIGA Sketch..."))
            
            # Kompilieren
            compile_cmd = [
                'arduino-cli', 'compile',
                '--fqbn', 'arduino:mbed_giga:giga',
                self.giga_sketch_path
            ]
            
            result = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                self.root.after(0, lambda: self.flash_status.config(text="GIGA Kompilierung fehlgeschlagen"))
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"GIGA Kompilierung fehlgeschlagen:\n{result.stderr}"))
                return
            
            # Upload
            self.root.after(0, lambda: self.flash_status.config(text="GIGA Upload läuft..."))
            
            upload_cmd = [
                'arduino-cli', 'upload',
                '-p', port,
                '--fqbn', 'arduino:mbed_giga:giga',
                self.giga_sketch_path
            ]
            
            result = subprocess.run(upload_cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.root.after(0, lambda: self.flash_status.config(text="✅ GIGA Flash erfolgreich!"))
                self.root.after(0, lambda: messagebox.showinfo("Erfolg", "Arduino GIGA erfolgreich geflasht!"))
            else:
                self.root.after(0, lambda: self.flash_status.config(text="❌ GIGA Flash fehlgeschlagen"))
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"GIGA Upload fehlgeschlagen:\n{result.stderr}"))
                
        except subprocess.TimeoutExpired:
            self.root.after(0, lambda: self.flash_status.config(text="❌ GIGA Timeout"))
            self.root.after(0, lambda: messagebox.showerror("Fehler", "GIGA Flash-Prozess Timeout"))
        except Exception as e:
            self.root.after(0, lambda: self.flash_status.config(text=f"❌ GIGA Fehler: {e}"))
            self.root.after(0, lambda: messagebox.showerror("Fehler", f"GIGA Flash-Fehler:\n{e}"))
        finally:
            self.root.after(0, lambda: self.flash_btn.config(state='normal', text="🔧 GIGA FLASHEN"))
    
    def _flash_both_worker(self):
        """Beide Geräte nacheinander flashen"""
        try:
            # Ports automatisch erkennen
            ports = []
            for pattern in ['/dev/ttyUSB*', '/dev/ttyACM*', '/dev/cu.usbserial*', '/dev/cu.usbmodem*']:
                ports.extend(glob.glob(pattern))
            
            if len(ports) < 2:
                self.root.after(0, lambda: messagebox.showerror("Fehler", 
                    f"Nicht genügend Ports gefunden!\nGefunden: {len(ports)}, Benötigt: 2\n" +
                    "Bitte beide Geräte anschließen."))
                return
            
            # Annahme: GIGA meist auf /dev/ttyACM*, ESP32 auf /dev/ttyUSB*
            giga_port = None
            esp32_port = None
            
            for port in ports:
                if '/dev/ttyACM' in port or '/dev/cu.usbmodem' in port:
                    giga_port = port
                elif '/dev/ttyUSB' in port or '/dev/cu.usbserial' in port:
                    esp32_port = port
            
            if not giga_port:
                giga_port = ports[0]
            if not esp32_port:
                esp32_port = ports[1] if len(ports) > 1 else ports[0]
            
            # 1. Arduino GIGA flashen
            self.root.after(0, lambda: self.flash_status.config(text="1/2: Flashe Arduino GIGA..."))
            
            # GIGA kompilieren
            compile_cmd = [
                'arduino-cli', 'compile',
                '--fqbn', 'arduino:mbed_giga:giga',
                self.giga_sketch_path
            ]
            
            result = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"GIGA Kompilierung fehlgeschlagen:\n{result.stderr}"))
                return
            
            # GIGA uploaden
            upload_cmd = [
                'arduino-cli', 'upload',
                '-p', giga_port,
                '--fqbn', 'arduino:mbed_giga:giga',
                self.giga_sketch_path
            ]
            
            result = subprocess.run(upload_cmd, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"GIGA Upload fehlgeschlagen:\n{result.stderr}"))
                return
            
            self.root.after(0, lambda: self.flash_status.config(text="✅ GIGA fertig! Warte 3 Sekunden..."))
            time.sleep(3)
            
            # 2. ESP32 flashen
            self.root.after(0, lambda: self.flash_status.config(text="2/2: Flashe ESP32..."))
            
            # ESP32 kompilieren
            compile_cmd = [
                'arduino-cli', 'compile',
                '--fqbn', 'esp32:esp32:esp32',
                self.esp32_sketch_path
            ]
            
            result = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"ESP32 Kompilierung fehlgeschlagen:\n{result.stderr}"))
                return
            
            # ESP32 uploaden
            self.root.after(0, lambda: self.flash_status.config(text="ESP32 Upload... BOOT-BUTTON DRÜCKEN!"))
            
            upload_cmd = [
                'arduino-cli', 'upload',
                '-p', esp32_port,
                '--fqbn', 'esp32:esp32:esp32',
                self.esp32_sketch_path
            ]
            
            result = subprocess.run(upload_cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.root.after(0, lambda: self.flash_status.config(text="✅ Beide Geräte erfolgreich geflasht!"))
                self.root.after(0, lambda: messagebox.showinfo("Erfolg", 
                    f"Beide Geräte erfolgreich geflasht!\n\n" +
                    f"GIGA Port: {giga_port}\n" +
                    f"ESP32 Port: {esp32_port}"))
                
                # ESP32 Verbindung neu starten
                self.esp32_port = esp32_port
                self.root.after(3000, self.restart_connection)
            else:
                self.root.after(0, lambda: messagebox.showerror("Fehler", f"ESP32 Upload fehlgeschlagen:\n{result.stderr}"))
                
        except subprocess.TimeoutExpired:
            self.root.after(0, lambda: self.flash_status.config(text="❌ Timeout"))
            self.root.after(0, lambda: messagebox.showerror("Fehler", "Flash-Prozess Timeout. ESP32 Boot-Button gedrückt?"))
        except Exception as e:
            self.root.after(0, lambda: self.flash_status.config(text=f"❌ Fehler: {e}"))
            self.root.after(0, lambda: messagebox.showerror("Fehler", f"Flash-Fehler:\n{e}"))
        finally:
            self.root.after(0, lambda: self.flash_btn.config(state='normal', text="🚀 BEIDE GERÄTE FLASHEN"))
        
    def create_footer(self):
        """Leerer Footer - Buttons entfernt"""
        footer_frame = tk.Frame(self.root, bg=self.colors['background_primary'], height=20)
        footer_frame.pack(side='bottom', fill='x')
        footer_frame.pack_propagate(False)

    def toggle_theme(self):
        """Wechselt zwischen Light und Dark Mode"""
        self.dark_mode = not self.dark_mode
        self.setup_color_themes()
        self.reload_gui()
    
    def create_home_tab(self):
        """Kompakte HOME-Seite ohne Scrollen - Projekt-Erklärung für Unwissende"""
        # Clear content
        for widget in self.right_panel.winfo_children():
            widget.destroy()
            
        # Main Container ohne Scrolling
        main_container = tk.Frame(self.right_panel, bg=self.colors['background_primary'])
        main_container.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Kompakter Header
        header_frame = tk.Frame(main_container, bg=self.colors['background_primary'])
        header_frame.pack(fill='x', pady=(0, 15))
        
        # Bertrandt Corporate Titel
        title_label = tk.Label(header_frame,
                              text="Interaktive Messestand-Lösung",
                              font=self.fonts['title'],
                              fg=self.colors['bertrandt_blue'],
                              bg=self.colors['background_primary'])
        title_label.pack()
        
        # Professional Beschreibung
        desc_label = tk.Label(header_frame,
                             text="End-to-End Lösung für interaktive Kundenerlebnisse",
                             font=self.fonts['subtitle'],
                             fg=self.colors['bertrandt_light_blue'],
                             bg=self.colors['background_primary'])
        desc_label.pack(pady=(5, 0))
        
        # Zusätzliche Erklärung
        detail_label = tk.Label(header_frame,
                               text="Berührungsbasierte Steuerung • Echtzeit-Reaktion • Modulares Design",
                               font=self.fonts['body'],
                               fg=self.colors['text_secondary'],
                               bg=self.colors['background_primary'])
        detail_label.pack(pady=(3, 0))
        
        # Kompakte Feature Cards - 3x2 Grid - weniger Platz
        features_frame = tk.Frame(main_container, bg=self.colors['background_primary'])
        features_frame.pack(fill='both', expand=True, pady=5)
        
        # Features mit neuen Kasten-Farben
        features = [
            {
                'icon': '🎯',
                'title': 'User-Centered Design',
                'desc': 'Nutzerzentrierte Entwicklung mit iterativem Designprozess',
                'color': self.colors['kasten_1']
            },
            {
                'icon': '⚡',
                'title': 'Real-Time Performance',
                'desc': 'Echtzeitvalidierung in realistischen Nutzungsszenarien',
                'color': self.colors['kasten_2']
            },
            {
                'icon': '🔧',
                'title': 'Modular Components',
                'desc': 'Wiederverwendbare UI-Bausteine und Widgets',
                'color': self.colors['kasten_3']
            },
            {
                'icon': '📊',
                'title': 'HMI/UX Integration',
                'desc': 'Ganzheitliche UX-Betrachtung bis zur Implementierung',
                'color': self.colors['kasten_4']
            },
            {
                'icon': '🚀',
                'title': 'Prototyping Excellence',
                'desc': 'Von Low- bis High-Fidelity Prototypen mit Tests',
                'color': self.colors['kasten_1']
            },
            {
                'icon': '💼',
                'title': 'Corporate Design',
                'desc': 'Konsistente Markenidentität über alle Plattformen',
                'color': self.colors['kasten_2']
            }
        ]
        
        # 3x2 Grid Layout - Bertrandt Tile System
        for i, feature in enumerate(features):
            row = i // 3
            col = i % 3
            
            # Bertrandt Tile/Widget Design
            tile_frame = tk.Frame(features_frame, 
                                 bg=self.colors['card_background'],
                                 relief='solid',
                                 bd=1,
                                 highlightthickness=0)
            tile_frame.config(highlightbackground=self.colors['border_light'])
            tile_frame.grid(row=row, column=col, padx=8, pady=6, sticky='nsew')
            
            # Header mit neuen Kasten-Farben
            header_frame = tk.Frame(tile_frame, 
                                   bg=feature['color'], 
                                   height=6)
            header_frame.pack(fill='x')
            header_frame.pack_propagate(False)
            
            # Tile Content Area - kompakter
            content_frame = tk.Frame(tile_frame, bg=self.colors['card_background'])
            content_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Icon mit Bertrandt Styling - kleiner
            icon_label = tk.Label(content_frame,
                                 text=feature['icon'],
                                 font=('Segoe UI', 20),
                                 fg=feature['color'],
                                 bg=self.colors['card_background'])
            icon_label.pack(pady=(0, 4))
            
            # Title mit Corporate Typography - kompakter
            title_label = tk.Label(content_frame,
                                  text=feature['title'],
                                  font=self.fonts['label'],
                                  fg=self.colors['text_primary'],
                                  bg=self.colors['card_background'])
            title_label.pack(pady=(0, 4))
            
            # Description mit Bertrandt Text Style - kompakter
            desc_label = tk.Label(content_frame,
                                 text=feature['desc'],
                                 font=self.fonts['caption'],
                                 fg=self.colors['text_secondary'],
                                 bg=self.colors['card_background'],
                                 wraplength=140,
                                 justify='center')
            desc_label.pack(pady=(0, 2), padx=3)
        
        # Grid gleichmäßig verteilen
        for i in range(3):
            features_frame.grid_columnconfigure(i, weight=1)
        for i in range(2):
            features_frame.grid_rowconfigure(i, weight=1)
        
        # Bertrandt Corporate Footer Widget - Kompakt für kleinere Bildschirme
        footer_widget = tk.Frame(main_container, 
                                bg=self.colors['bertrandt_dark_blue'], 
                                relief='flat', 
                                bd=0)
        footer_widget.pack(fill='x', pady=(10, 0))
        
        # Corporate Tagline - kompakter
        tagline_label = tk.Label(footer_widget,
                                text="Engineering tomorrow",
                                font=self.fonts['body'],
                                fg='white',
                                bg=self.colors['bertrandt_dark_blue'])
        tagline_label.pack(pady=(8, 2))
        
        # Tech Stack mit Bertrandt Styling - kompakter
        tech_label = tk.Label(footer_widget,
                             text="Bertrandt Digital Solutions: Arduino GIGA • ESP32 • Python • HMI/UX Excellence",
                             font=self.fonts['caption'],
                             fg=self.colors['bertrandt_light_blue'],
                             bg=self.colors['bertrandt_dark_blue'])
        tech_label.pack(pady=(0, 8))

    def create_content_creator_tab(self):
        """Content Creator - Drag & Drop Editor für Folien"""
        # Clear content
        for widget in self.right_panel.winfo_children():
            widget.destroy()
            
        # Main Container
        main_container = tk.Frame(self.right_panel, bg=self.colors['background_primary'])
        main_container.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Header
        header_frame = tk.Frame(main_container, bg=self.colors['background_primary'])
        header_frame.pack(fill='x', pady=(0, 15))
        
        title_label = tk.Label(header_frame,
                              text="Content Creator",
                              font=self.fonts['title'],
                              fg=self.colors['bertrandt_blue'],
                              bg=self.colors['background_primary'])
        title_label.pack()
        
        # Main Layout: Slides (rechts) + Editor (mitte)
        content_frame = tk.Frame(main_container, bg=self.colors['background_primary'])
        content_frame.pack(fill='both', expand=True)
        
        # Editor Area (Mitte - 70%)
        self.editor_frame = tk.Frame(content_frame, bg=self.colors['background_secondary'], relief='flat', bd=0)
        self.editor_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Editor Header
        editor_header = tk.Frame(self.editor_frame, bg=self.colors['background_tertiary'])
        editor_header.pack(fill='x', pady=2)
        
        self.current_slide_label = tk.Label(editor_header,
                                           text="Folie 1 - Willkommen",
                                           font=self.fonts['label'],
                                           fg='white',
                                           bg=self.colors['background_tertiary'])
        self.current_slide_label.pack(pady=5)
        
        # Canvas für Drag & Drop
        self.canvas = tk.Canvas(self.editor_frame, 
                               bg='white',
                               highlightthickness=1,
                               highlightbackground=self.colors['border_medium'])
        self.canvas.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Drag & Drop Setup
        self.setup_drag_drop()
        
        # Slides Panel (Rechts - 30%)
        slides_frame = tk.Frame(content_frame, bg=self.colors['background_tertiary'], relief='flat', bd=0)
        slides_frame.pack(side='right', fill='y', padx=(0, 0))
        slides_frame.config(width=250)
        slides_frame.pack_propagate(False)
        
        # Slides Header
        slides_header = tk.Label(slides_frame,
                                text="Folien (1-12)",
                                font=self.fonts['label'],
                                fg=self.colors['text_primary'],
                                bg=self.colors['background_tertiary'])
        slides_header.pack(pady=10)
        
        # Scrollable Slides List
        slides_canvas = tk.Canvas(slides_frame, bg=self.colors['background_tertiary'], highlightthickness=0)
        slides_scrollbar = ttk.Scrollbar(slides_frame, orient="vertical", command=slides_canvas.yview)
        self.slides_list_frame = tk.Frame(slides_canvas, bg=self.colors['background_tertiary'])
        
        self.slides_list_frame.bind(
            "<Configure>",
            lambda e: slides_canvas.configure(scrollregion=slides_canvas.bbox("all"))
        )
        
        slides_canvas.create_window((0, 0), window=self.slides_list_frame, anchor="nw")
        slides_canvas.configure(yscrollcommand=slides_scrollbar.set)
        
        # Create slide buttons
        self.current_slide = 1
        self.slide_data = {}  # Speichert Slide-Inhalte
        self.create_slide_buttons()
        
        slides_canvas.pack(side="left", fill="both", expand=True, padx=5)
        slides_scrollbar.pack(side="right", fill="y")
        
        # Toolbar unten
        toolbar_frame = tk.Frame(main_container, bg=self.colors['background_tertiary'])
        toolbar_frame.pack(fill='x', pady=(10, 0))
        
        # Text hinzufügen Button
        add_text_btn = tk.Button(toolbar_frame,
                                text="📝 Text hinzufügen",
                                command=self.add_text_element,
                                font=self.fonts['button'],
                                bg=self.colors['accent_primary'],
                                fg='white',
                                relief='flat',
                                padx=15,
                                pady=8,
                                cursor='hand2')
        add_text_btn.pack(side='left', padx=10, pady=10)
        
        # Speichern Button
        save_btn = tk.Button(toolbar_frame,
                            text="💾 Speichern",
                            command=self.save_slide,
                            font=self.fonts['button'],
                            bg=self.colors['accent_secondary'],
                            fg='white',
                            relief='flat',
                            padx=15,
                            pady=8,
                            cursor='hand2')
        save_btn.pack(side='left', padx=5, pady=10)
        
        # Löschen Button
        clear_btn = tk.Button(toolbar_frame,
                             text="🗑️ Löschen",
                             command=self.clear_slide,
                             font=self.fonts['button'],
                             bg=self.colors['accent_tertiary'],
                             fg='white',
                             relief='flat',
                             padx=15,
                             pady=8,
                             cursor='hand2')
        clear_btn.pack(side='left', padx=5, pady=10)
        
        # Load current slide
        self.load_slide(1)
    
    def create_slide_buttons(self):
        """Erstellt Buttons für alle 12 Folien"""
        for i in range(1, 13):
            slide_name = self.signal_definitions.get(i, {}).get('name', f'Folie {i}')
            
            btn = tk.Button(self.slides_list_frame,
                           text=f"{i}. {slide_name}",
                           command=lambda x=i: self.load_slide(x),
                           font=self.fonts['body'],
                           bg=self.colors['background_primary'] if i != self.current_slide else self.colors['accent_primary'],
                           fg=self.colors['text_primary'] if i != self.current_slide else 'white',
                           relief='flat',
                           anchor='w',
                           padx=10,
                           pady=8,
                           cursor='hand2')
            btn.pack(fill='x', padx=5, pady=2)
    
    def setup_drag_drop(self):
        """Setup für Drag & Drop Funktionalität"""
        self.dragging = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # Canvas Events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drop)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
    
    def add_text_element(self):
        """Fügt ein neues Textfeld hinzu"""
        x, y = 50, 50
        text_id = self.canvas.create_text(x, y, 
                                         text="Neuer Text", 
                                         font=self.fonts['body'],
                                         fill=self.colors['text_primary'],
                                         anchor='nw',
                                         tags="draggable")
        
        # Rahmen um Text
        bbox = self.canvas.bbox(text_id)
        if bbox:
            rect_id = self.canvas.create_rectangle(bbox[0]-5, bbox[1]-5, bbox[2]+5, bbox[3]+5,
                                                  outline=self.colors['border_medium'],
                                                  fill='',
                                                  tags=f"frame_{text_id}")
    
    def on_canvas_click(self, event):
        """Canvas Click Handler"""
        item = self.canvas.find_closest(event.x, event.y)[0]
        if "draggable" in self.canvas.gettags(item):
            self.dragging = item
            self.drag_start_x = event.x
            self.drag_start_y = event.y
    
    def on_drag(self, event):
        """Drag Handler"""
        if self.dragging:
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            self.canvas.move(self.dragging, dx, dy)
            
            # Move frame if exists
            frame_tag = f"frame_{self.dragging}"
            frame_items = self.canvas.find_withtag(frame_tag)
            if frame_items:
                self.canvas.move(frame_items[0], dx, dy)
            
            self.drag_start_x = event.x
            self.drag_start_y = event.y
    
    def on_drop(self, event):
        """Drop Handler"""
        self.dragging = None
    
    def on_double_click(self, event):
        """Doppelklick für Text-Bearbeitung"""
        item = self.canvas.find_closest(event.x, event.y)[0]
        if "draggable" in self.canvas.gettags(item):
            self.edit_text(item)
    
    def edit_text(self, text_item):
        """Text-Bearbeitungs-Dialog"""
        current_text = self.canvas.itemconfig(text_item, 'text')[-1]
        
        # Simple Input Dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Text bearbeiten")
        dialog.geometry("400x200")
        dialog.configure(bg=self.colors['background_primary'])
        
        tk.Label(dialog, text="Text eingeben:", 
                font=self.fonts['body'],
                bg=self.colors['background_primary'],
                fg=self.colors['text_primary']).pack(pady=10)
        
        text_var = tk.StringVar(value=current_text)
        entry = tk.Entry(dialog, textvariable=text_var, 
                        font=self.fonts['body'], width=40)
        entry.pack(pady=10)
        entry.focus()
        
        def save_text():
            new_text = text_var.get()
            self.canvas.itemconfig(text_item, text=new_text)
            
            # Update frame
            bbox = self.canvas.bbox(text_item)
            if bbox:
                frame_tag = f"frame_{text_item}"
                frame_items = self.canvas.find_withtag(frame_tag)
                if frame_items:
                    self.canvas.coords(frame_items[0], bbox[0]-5, bbox[1]-5, bbox[2]+5, bbox[3]+5)
            
            dialog.destroy()
        
        tk.Button(dialog, text="Speichern", command=save_text,
                 bg=self.colors['accent_primary'], fg='white',
                 font=self.fonts['button']).pack(pady=10)
        
        entry.bind('<Return>', lambda e: save_text())
    
    def load_slide(self, slide_num):
        """Lädt eine Folie"""
        self.current_slide = slide_num
        slide_name = self.signal_definitions.get(slide_num, {}).get('name', f'Folie {slide_num}')
        self.current_slide_label.config(text=f"Folie {slide_num} - {slide_name}")
        
        # Clear canvas
        self.canvas.delete("all")
        
        # Load saved data
        if slide_num in self.slide_data:
            for item_data in self.slide_data[slide_num]:
                if item_data['type'] == 'text':
                    text_id = self.canvas.create_text(item_data['x'], item_data['y'],
                                                     text=item_data['text'],
                                                     font=self.fonts['body'],
                                                     fill=self.colors['text_primary'],
                                                     anchor='nw',
                                                     tags="draggable")
                    
                    # Add frame
                    bbox = self.canvas.bbox(text_id)
                    if bbox:
                        self.canvas.create_rectangle(bbox[0]-5, bbox[1]-5, bbox[2]+5, bbox[3]+5,
                                                    outline=self.colors['border_medium'],
                                                    fill='',
                                                    tags=f"frame_{text_id}")
        
        # Update slide buttons
        for widget in self.slides_list_frame.winfo_children():
            widget.destroy()
        self.create_slide_buttons()
    
    def save_slide(self):
        """Speichert aktuelle Folie"""
        items = []
        for item in self.canvas.find_withtag("draggable"):
            if self.canvas.type(item) == "text":
                coords = self.canvas.coords(item)
                text = self.canvas.itemconfig(item, 'text')[-1]
                items.append({
                    'type': 'text',
                    'x': coords[0],
                    'y': coords[1],
                    'text': text
                })
        
        self.slide_data[self.current_slide] = items
        
        # Save to file
        self.save_slides_to_file()
        
        # Show confirmation
        self.show_message("Folie gespeichert!", self.colors['accent_secondary'])
    
    def clear_slide(self):
        """Löscht aktuelle Folie"""
        self.canvas.delete("all")
        if self.current_slide in self.slide_data:
            del self.slide_data[self.current_slide]
        self.show_message("Folie gelöscht!", self.colors['accent_tertiary'])
    
    def save_slides_to_file(self):
        """Speichert alle Folien in JSON-Datei"""
        slides_file = os.path.join(self.content_dir, "slides_data.json")
        try:
            with open(slides_file, 'w', encoding='utf-8') as f:
                json.dump(self.slide_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Fehler beim Speichern: {e}")
    
    def load_slides_from_file(self):
        """Lädt Folien aus JSON-Datei"""
        slides_file = os.path.join(self.content_dir, "slides_data.json")
        try:
            if os.path.exists(slides_file):
                with open(slides_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert string keys to int
                    self.slide_data = {int(k): v for k, v in data.items()}
        except Exception as e:
            print(f"Fehler beim Laden: {e}")
            self.slide_data = {}
    
    def show_message(self, message, color):
        """Zeigt temporäre Nachricht"""
        msg_label = tk.Label(self.editor_frame,
                            text=message,
                            font=self.fonts['body'],
                            fg='white',
                            bg=color,
                            padx=10,
                            pady=5)
        msg_label.place(relx=0.5, rely=0.1, anchor='center')
        
        # Auto-remove after 2 seconds
        self.root.after(2000, msg_label.destroy)

    def create_demo_tab(self):
        """Demo-Modus mit automatischer Folien-Wiedergabe"""
        # Clear content
        for widget in self.right_panel.winfo_children():
            widget.destroy()
            
        # Main Container
        main_container = tk.Frame(self.right_panel, bg=self.colors['background_primary'])
        main_container.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Header
        header_frame = tk.Frame(main_container, bg=self.colors['background_primary'])
        header_frame.pack(fill='x', pady=(0, 15))
        
        title_label = tk.Label(header_frame,
                              text="Demo Modus",
                              font=self.fonts['title'],
                              fg=self.colors['bertrandt_blue'],
                              bg=self.colors['background_primary'])
        title_label.pack()
        
        # Slide Display Area mit CSS Template
        self.demo_frame = tk.Frame(main_container, bg='#FFFFFF', relief='flat', bd=0)
        self.demo_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Calculate 16:9 dimensions based on available space
        available_width = self.root.winfo_width() - 100  # Account for margins
        available_height = self.root.winfo_height() - 300  # Account for header/footer
        
        # 16:9 aspect ratio calculation
        if available_width / 16 * 9 <= available_height:
            canvas_width = available_width
            canvas_height = int(available_width / 16 * 9)
        else:
            canvas_height = available_height
            canvas_width = int(available_height / 9 * 16)
        
        # Slide Header mit CSS Template
        slide_header = tk.Frame(self.demo_frame, bg='#FFFFFF', height=40)
        slide_header.pack(fill='x', pady=2)
        slide_header.pack_propagate(False)
        
        self.demo_slide_label = tk.Label(slide_header,
                                        text="Folie 1",
                                        font=('PT Sans', 16, 'bold'),
                                        fg='#000000',
                                        bg='#FFFFFF')
        self.demo_slide_label.pack(pady=8)
        
        # Canvas Container mit CSS Template
        canvas_container = tk.Frame(self.demo_frame, bg='#FFFFFF')
        canvas_container.pack(fill='both', expand=True, padx=0, pady=0)
        
        # Demo Canvas - 16:9 Format mit schwarzem Rahmen
        canvas_frame = tk.Frame(canvas_container, bg='#000000', relief='flat', bd=5)
        canvas_frame.pack(anchor='center', pady=10)
        
        self.demo_canvas = tk.Canvas(canvas_frame, 
                                    bg='#FFFFFF',
                                    highlightthickness=0,
                                    width=canvas_width,
                                    height=canvas_height)
        self.demo_canvas.pack()
        
        # Store canvas dimensions for content scaling
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        
        # Demo Controls direkt unter Canvas
        self.create_demo_slide_controls(main_container)
        
        # Lade erste Folie
        self.load_demo_slide(1)
        
        print("🎬 Demo Tab vollständig erstellt mit Controls")
    
    def create_demo_tab_with_controls(self):
        """Erstellt Demo Tab mit funktionsfähigen Steuerungsbuttons"""
        print("🎬 Erstelle Demo Tab mit Controls...")
        
        # Main container für Demo
        main_container = tk.Frame(self.right_panel, bg='#FFFFFF')
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Demo Header
        header_frame = tk.Frame(main_container, bg='#000000', relief='flat', bd=0)
        header_frame.pack(fill='x', pady=(0, 15))
        
        header_label = tk.Label(header_frame,
                               text="🎬 BUMBLEB DEMO PRÄSENTATION",
                               font=('PT Sans', 18, 'bold'),
                               fg='#FFFFFF',
                               bg='#000000')
        header_label.pack(pady=15)
        
        # Canvas Container mit schwarzem Rahmen - zentriert
        canvas_container = tk.Frame(main_container, bg='#000000', relief='flat', bd=5)
        canvas_container.pack(anchor='center', pady=(10, 0))
        
        # Demo Canvas - 16:9 Format - Größer aber mit Platz für Controls
        # Berechne verfügbaren Platz (Reserve 150px für Controls und Margins)
        available_width = 1000  # Vergrößert von 800
        available_height = 700  # Vergrößert von 600, aber Reserve für Controls
        
        # 16:9 Aspect Ratio beibehalten
        if available_width / 16 * 9 <= available_height:
            canvas_width = available_width
            canvas_height = int(available_width / 16 * 9)
        else:
            canvas_height = available_height
            canvas_width = int(available_height / 9 * 16)
        
        print(f"📐 Demo Canvas: {canvas_width}x{canvas_height} (16:9 Format)")
        
        self.demo_canvas = tk.Canvas(canvas_container, 
                                    bg='#FFFFFF',
                                    highlightthickness=0,
                                    width=canvas_width,
                                    height=canvas_height)
        self.demo_canvas.pack()
        
        # Store canvas dimensions
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        
        # Demo Controls Frame - Schwarzer Hintergrund, feste Position
        controls_frame = tk.Frame(main_container, bg='#000000', relief='flat', bd=0, height=90)
        controls_frame.pack(fill='x', pady=(20, 10))
        controls_frame.pack_propagate(False)
        
        # Demo Controls initialisieren
        self.demo_running = False
        self.demo_current_slide = 1
        self.demo_timer = None
        
        # Controls Container - Zentriert mit mehr Platz
        controls_container = tk.Frame(controls_frame, bg='#000000')
        controls_container.pack(expand=True, pady=20)
        
        # Zurück Button - größer für bessere Sichtbarkeit
        self.demo_prev_btn = tk.Button(controls_container,
                                      text="⏮️ ZURÜCK",
                                      command=self.demo_prev_slide,
                                      font=('PT Sans', 16, 'bold'),
                                      bg=self.colors['kasten_1'],
                                      fg='#FFFFFF',
                                      relief='flat',
                                      bd=0,
                                      padx=20,
                                      pady=12,
                                      cursor='hand2',
                                      activebackground=self.colors['kasten_2'])
        self.demo_prev_btn.pack(side='left', padx=15)
        
        # Play/Pause Button - prominenter
        self.demo_play_btn = tk.Button(controls_container,
                                      text="▶️ PLAY",
                                      command=self.toggle_demo_play,
                                      font=('PT Sans', 18, 'bold'),
                                      bg='#00AA00',
                                      fg='#FFFFFF',
                                      relief='flat',
                                      bd=0,
                                      padx=30,
                                      pady=15,
                                      cursor='hand2',
                                      activebackground='#00CC00')
        self.demo_play_btn.pack(side='left', padx=20)
        
        # Vor Button - größer für bessere Sichtbarkeit
        self.demo_next_btn = tk.Button(controls_container,
                                      text="VOR ⏭️",
                                      command=self.demo_next_slide,
                                      font=('PT Sans', 16, 'bold'),
                                      bg=self.colors['kasten_1'],
                                      fg='#FFFFFF',
                                      relief='flat',
                                      bd=0,
                                      padx=20,
                                      pady=12,
                                      cursor='hand2',
                                      activebackground=self.colors['kasten_2'])
        self.demo_next_btn.pack(side='left', padx=15)
        
        # Progress Info - größer und besser sichtbar
        progress_container = tk.Frame(controls_frame, bg='#000000')
        progress_container.pack(side='right', padx=30, pady=20)
        
        self.demo_progress_label = tk.Label(progress_container,
                                           text="Folie 1 von 10",
                                           font=('PT Sans', 14, 'bold'),
                                           fg='#FFFFFF',
                                           bg='#000000')
        self.demo_progress_label.pack()
        
        # Lade erste Folie
        self.load_demo_slide(1)
        
        print("✅ Demo Tab mit Controls erfolgreich erstellt!")
        print("✅ Buttons: ZURÜCK, PLAY/PAUSE, VOR")
        print("✅ Canvas: 16:9 Format mit schwarzem Rahmen")
        print("✅ Auto-Advance: 2500ms Intervall")
    
    def create_demo_slide_controls(self, parent_container):
        """Erstellt Play/Pause und Navigation Controls für Demo Slides"""
        # Demo Controls Frame direkt unter Canvas
        controls_frame = tk.Frame(parent_container, bg='#000000', relief='flat', bd=0, height=70)
        controls_frame.pack(fill='x', pady=(15, 0))
        controls_frame.pack_propagate(False)
        
        # Demo Controls initialisieren
        self.demo_running = False
        self.demo_current_slide = 1
        self.demo_timer = None
        
        print("🔧 Demo Slide Controls werden initialisiert...")
        
        # Controls Container - Zentriert
        controls_container = tk.Frame(controls_frame, bg='#000000')
        controls_container.pack(expand=True, pady=10)
        
        # Zurück Button
        self.demo_prev_btn = tk.Button(controls_container,
                                      text="⏮️ ZURÜCK",
                                      command=self.demo_prev_slide,
                                      font=('PT Sans', 14, 'bold'),
                                      bg='#333333',
                                      fg='#FFFFFF',
                                      relief='flat',
                                      bd=0,
                                      padx=15,
                                      pady=8,
                                      cursor='hand2',
                                      activebackground='#555555',
                                      activeforeground='#FFFFFF')
        self.demo_prev_btn.pack(side='left', padx=10)
        
        # Play/Pause Button - Prominenter
        self.demo_play_btn = tk.Button(controls_container,
                                      text="▶️ PLAY",
                                      command=self.toggle_demo_play,
                                      font=('PT Sans', 16, 'bold'),
                                      bg='#00AA00',
                                      fg='#FFFFFF',
                                      relief='flat',
                                      bd=0,
                                      padx=20,
                                      pady=10,
                                      cursor='hand2',
                                      activebackground='#00CC00',
                                      activeforeground='#FFFFFF')
        self.demo_play_btn.pack(side='left', padx=15)
        
        # Vor Button
        self.demo_next_btn = tk.Button(controls_container,
                                      text="VOR ⏭️",
                                      command=self.demo_next_slide,
                                      font=('PT Sans', 14, 'bold'),
                                      bg='#333333',
                                      fg='#FFFFFF',
                                      relief='flat',
                                      bd=0,
                                      padx=15,
                                      pady=8,
                                      cursor='hand2',
                                      activebackground='#555555',
                                      activeforeground='#FFFFFF')
        self.demo_next_btn.pack(side='left', padx=10)
        
        # Progress Info - Rechts
        progress_container = tk.Frame(controls_frame, bg='#000000')
        progress_container.pack(side='right', padx=20, pady=15)
        
        self.demo_progress_label = tk.Label(progress_container,
                                           text="Folie 1 von 10",
                                           font=('PT Sans', 12, 'normal'),
                                           fg='#CCCCCC',
                                           bg='#000000')
        self.demo_progress_label.pack()
        
        print("✅ Demo Slide Controls erstellt: ZURÜCK, PLAY/PAUSE, VOR")
        
        # Load first slide
        self.load_demo_slide(1)
    
    def toggle_demo(self):
        """Startet/Stoppt die automatische Demo"""
        if self.demo_running:
            self.stop_demo()
        else:
            self.start_demo()
    
    def toggle_demo_play(self):
        """Startet/Stoppt automatische BumbleB Demo mit 2500ms Intervall"""
        if hasattr(self, 'demo_running') and self.demo_running:
            self.stop_demo_play()
        else:
            self.start_demo_play()
    
    def start_demo_play(self):
        """Startet automatische BumbleB Demo"""
        self.demo_running = True
        if hasattr(self, 'demo_play_btn'):
            self.demo_play_btn.config(text="⏸️ PAUSE", bg='#CC0000')  # Pause Button rot
        self.schedule_next_demo_slide()
        print("▶️ BumbleB Auto-Demo gestartet (2500ms Intervall)")
    
    def stop_demo_play(self):
        """Stoppt automatische BumbleB Demo"""
        self.demo_running = False
        if hasattr(self, 'demo_play_btn'):
            self.demo_play_btn.config(text="▶️ PLAY", bg='#00AA00')  # Play Button grün
        if hasattr(self, 'demo_timer') and self.demo_timer:
            self.root.after_cancel(self.demo_timer)
            self.demo_timer = None
        print("⏸️ BumbleB Auto-Demo gestoppt")
    
    def stop_demo(self):
        """Legacy - Stoppt automatische Demo"""
        self.stop_demo_play()
    
    def schedule_next_demo_slide(self):
        """Plant nächste BumbleB Folie nach 2500ms"""
        if hasattr(self, 'demo_running') and self.demo_running:
            self.demo_timer = self.root.after(2500, self.auto_next_slide)
    
    def auto_next_slide(self):
        """Automatischer Wechsel zur nächsten Folie"""
        if self.demo_running:
            next_slide = self.demo_current_slide + 1
            if next_slide > 12:
                next_slide = 1  # Zurück zum Anfang
            
            self.load_demo_slide(next_slide)
            self.schedule_next_demo_slide()
    
    def demo_prev_slide(self):
        """Manuelle Navigation: Vorherige Folie"""
        prev_slide = self.demo_current_slide - 1
        if prev_slide < 1:
            prev_slide = 12  # Zum Ende springen
        self.load_demo_slide(prev_slide)
    
    def demo_next_slide(self):
        """Manuelle Navigation: Nächste Folie"""
        next_slide = self.demo_current_slide + 1
        if next_slide > 12:
            next_slide = 1  # Zum Anfang springen
        self.load_demo_slide(next_slide)
    
    def load_demo_slide(self, slide_num):
        """Lädt eine BumbleB Folie im Demo-Modus"""
        self.demo_current_slide = slide_num
        
        # Load BumbleB content from JSON files
        signal_info = self.signal_definitions.get(slide_num, {})
        content_type = signal_info.get('content_type', 'welcome')
        page_dir = os.path.join(self.content_dir, f"page_{slide_num}_{content_type}")
        config_path = os.path.join(page_dir, "config.json")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            # Fallback if JSON doesn't exist
            config = {
                "title": f"BumbleB Folie {slide_num}",
                "subtitle": f"Inhalt für Folie {slide_num}",
                "text_content": f"BumbleB Folie {slide_num} - Inhalt wird geladen..."
            }
        
        # Update progress label
        if hasattr(self, 'demo_progress_label'):
            self.demo_progress_label.config(text=f"Folie {slide_num} von 10")
        
        # Update slide label if it exists
        if hasattr(self, 'demo_slide_label'):
            self.demo_slide_label.config(text=f"Folie {slide_num}")
        
        # Clear canvas
        self.demo_canvas.delete("all")
        
        # Add Bertrandt Logo top right
        self.add_demo_logo()
        
        # Calculate responsive dimensions
        margin = 40
        content_width = self.canvas_width - (2 * margin) - 150  # Reserve space for logo
        
        # Create layout optimized for 16:9
        y_pos = margin
        
        # Main Title - BumbleB Style
        title = config.get('title', f'BumbleB Folie {slide_num}')
        title_font_size = max(20, int(self.canvas_width / 40))
        title_font = ('PT Sans', title_font_size, 'bold')
        
        title_text = self.demo_canvas.create_text(margin, y_pos,
                                                 text=title,
                                                 font=title_font,
                                                 fill='#0066CC',  # Bertrandt Blue für Titel
                                                 anchor='nw',
                                                 width=content_width)
        
        # Get title height for spacing
        title_bbox = self.demo_canvas.bbox(title_text)
        if title_bbox:
            y_pos = title_bbox[3] + 25
        else:
            y_pos += int(self.canvas_height * 0.15)
        
        # Subtitle - BumbleB Style
        subtitle = config.get('subtitle', '')
        if subtitle:
            subtitle_font_size = max(16, int(self.canvas_width / 50))
            subtitle_font = ('PT Sans', subtitle_font_size, 'normal')
            
            subtitle_text = self.demo_canvas.create_text(margin, y_pos,
                                                        text=subtitle,
                                                        font=subtitle_font,
                                                        fill='#00A0E6',  # Bertrandt Light Blue
                                                        anchor='nw',
                                                        width=content_width)
            
            # Get subtitle height for spacing
            subtitle_bbox = self.demo_canvas.bbox(subtitle_text)
            if subtitle_bbox:
                y_pos = subtitle_bbox[3] + 30
            else:
                y_pos += int(self.canvas_height * 0.12)
        
        # Main content - BumbleB Story
        content = config.get('text_content', '')
        if content:
            content_font_size = max(14, int(self.canvas_width / 60))
            content_font = ('PT Sans', content_font_size, 'normal')
            
            # Ensure content fits in remaining space
            remaining_height = self.canvas_height - y_pos - margin
            
            self.demo_canvas.create_text(margin, y_pos,
                                        text=content,
                                        font=content_font,
                                        fill='#000000',
                                        anchor='nw',
                                        width=content_width)
        
        print(f"📄 BumbleB Folie {slide_num} geladen: {title[:50]}...")
    
    def add_demo_logo(self):
        """Fügt das Bertrandt Logo oben rechts hinzu"""
        try:
            if hasattr(self, 'canvas_width') and hasattr(self, 'demo_canvas'):
                # Logo-Größe für Demo-Canvas anpassen
                logo_size = max(80, int(self.canvas_width / 15))
                
                # Logo oben rechts positionieren
                logo_x = self.canvas_width - logo_size - 20
                logo_y = 20
                
                # Erstelle ein kleineres Logo für den Demo-Canvas
                logo_path = os.path.join(os.path.dirname(__file__), "Bertrandt_logo.svg.png")
                if os.path.exists(logo_path) and hasattr(self, 'logo_photo'):
                    from PIL import Image, ImageTk
                    logo_image = Image.open(logo_path)
                    
                    # Proportional skalieren
                    aspect_ratio = logo_image.width / logo_image.height
                    logo_height = int(logo_size / aspect_ratio)
                    
                    logo_image = logo_image.resize((logo_size, logo_height), Image.Resampling.LANCZOS)
                    self.demo_logo_photo = ImageTk.PhotoImage(logo_image)
                    
                    # Logo auf Canvas platzieren
                    self.demo_canvas.create_image(logo_x, logo_y,
                                                 image=self.demo_logo_photo,
                                                 anchor='nw')
                else:
                    # Fallback: Text-Logo
                    self.demo_canvas.create_text(self.canvas_width - 120, 25,
                                                text="BERTRANDT",
                                                font=('PT Sans', 12, 'bold'),
                                                fill='#0066CC',
                                                anchor='nw')
        except Exception as e:
            print(f"⚠️ Demo-Logo konnte nicht geladen werden: {e}")
            # Fallback: Text-Logo
            if hasattr(self, 'demo_canvas') and hasattr(self, 'canvas_width'):
                self.demo_canvas.create_text(self.canvas_width - 120, 25,
                                            text="BERTRANDT",
                                            font=('PT Sans', 12, 'bold'),
                                            fill='#0066CC',
                                            anchor='nw')

    def run(self):
        """GUI starten"""
        try:
            self.root.mainloop()
        finally:
            self.running = False
            if self.dev_mode:
                self.stop_auto_demo()
            if self.serial_connection:
                self.serial_connection.close()

def main():
    parser = argparse.ArgumentParser(description='Bertrandt ESP32 Monitor')
    parser.add_argument('--esp32-port', default='/dev/ttyUSB0',
                       help='ESP32 Serial Port')
    
    args = parser.parse_args()
    
    app = BertrandtGUI(esp32_port=args.esp32_port)
    app.run()

if __name__ == "__main__":
    main()