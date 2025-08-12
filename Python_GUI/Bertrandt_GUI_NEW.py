#!/usr/bin/env python3
"""
Bertrandt Interactive Display - Komplett überarbeitete GUI
Alle Funktionen korrekt verlinkt und strukturiert
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import threading
import time
from PIL import Image, ImageTk

class BertrandtGUI:
    def __init__(self, esp32_port=None):
        """Initialisiert die Bertrandt GUI mit korrekter Struktur"""
        print("🚀 Starte Bertrandt GUI - Komplett überarbeitet...")
        
        # Tkinter Root
        self.root = tk.Tk()
        self.root.title("Bertrandt Interactive Display - BumbleB Presentation")
        
        # Basis-Initialisierung
        self.esp32_port = esp32_port
        self.fullscreen = False
        self.current_tab = "home"
        self.current_slide = 1
        self.demo_running = False
        self.demo_timer = None
        self.current_edit_slide = 1
        
        # Content-Verzeichnis
        self.content_dir = os.path.join(os.path.dirname(__file__), "content")
        
        # Responsive Design Setup - ZUERST
        self.setup_responsive_design()
        
        # Setup in korrekter Reihenfolge
        self.setup_color_themes()
        self.setup_styles()
        self.setup_signal_definitions()
        self.setup_gui()
        
        # Initialisiere HOME-Tab
        self.current_tab = "home"
        self.switch_tab("home")
        
        print("✅ Bertrandt GUI erfolgreich initialisiert!")
    
    def setup_responsive_design(self):
        """Konfiguriert intelligentes responsive Design"""
        # Bildschirmgröße ermitteln
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Intelligente Skalierung
        if self.screen_width >= 1920:
            self.scale_factor = 1.0
            self.layout_mode = "desktop_xl"
        elif self.screen_width >= 1600:
            self.scale_factor = 0.9
            self.layout_mode = "desktop_large"
        elif self.screen_width >= 1366:
            self.scale_factor = 0.8
            self.layout_mode = "desktop_medium"
        elif self.screen_width >= 1280:
            self.scale_factor = 0.75
            self.layout_mode = "laptop"
        else:
            self.scale_factor = 0.7
            self.layout_mode = "compact"
        
        # Fenster maximieren
        self.root.state('zoomed')
        
        # Responsive Dimensionen
        self.responsive_dims = {
            'header_height': max(120, int(156 * self.scale_factor)),
            'footer_height': max(18, int(20 * self.scale_factor)),
            'tab_button_width': max(120, int(150 * self.scale_factor)),
            'tab_button_height': max(35, int(45 * self.scale_factor)),
            'status_width': max(220, int(280 * self.scale_factor)),
            'left_panel_width': max(320, int(420 * self.scale_factor)),
            'card_width': max(200, int(280 * self.scale_factor)),
            'card_height': max(140, int(180 * self.scale_factor)),
            'button_height': max(30, int(40 * self.scale_factor)),
            'thumbnail_height': max(160, int(220 * self.scale_factor)),
            'padding_small': max(3, int(5 * self.scale_factor)),
            'padding_medium': max(6, int(10 * self.scale_factor)),
            'padding_large': max(10, int(15 * self.scale_factor))
        }
        
        print(f"📱 Responsive: {self.layout_mode} | Scale: {self.scale_factor} | Screen: {self.screen_width}x{self.screen_height}")
    
    def get_responsive_font(self, font_type, size_override=None):
        """Gibt responsive Schriftart zurück"""
        base_sizes = {
            'title': 28, 'subtitle': 20, 'header': 24, 'body': 16,
            'button': 14, 'small': 12, 'tiny': 10
        }
        
        base_size = size_override if size_override else base_sizes.get(font_type, 16)
        scaled_size = int(base_size * self.scale_factor)
        
        # Mindestgrößen
        min_sizes = {'title': 20, 'subtitle': 16, 'header': 18, 'body': 12, 'button': 11, 'small': 10, 'tiny': 9}
        final_size = max(min_sizes.get(font_type, 10), scaled_size)
        
        weight = 'bold' if font_type in ['title', 'header', 'button'] else 'normal'
        return ('PT Sans', final_size, weight)
    
    def get_responsive_padding(self, size='medium'):
        """Gibt responsive Padding zurück"""
        return self.responsive_dims.get(f'padding_{size}', 10)
    
    def setup_color_themes(self):
        """Definiert das Bertrandt Corporate Design Farbschema"""
        self.dark_mode = False  # Standard: Light Mode
        
        # Bertrandt Corporate Colors
        self.colors = {
            # Primärfarben
            'bertrandt_blue': '#003366',      # Bertrandt Hauptblau
            'bertrandt_light_blue': '#0066CC', # Helles Bertrandt Blau
            
            # Hintergründe
            'background_primary': '#FFFFFF',   # Weiß
            'background_secondary': '#F8F9FA', # Sehr helles Grau
            'background_tertiary': '#E9ECEF',  # Helles Grau
            
            # Text
            'text_primary': '#212529',         # Dunkelgrau
            'text_secondary': '#6C757D',       # Mittelgrau
            'text_light': '#ADB5BD',          # Hellgrau
            
            # Akzentfarben
            'accent_primary': '#007BFF',       # Primär Blau
            'accent_secondary': '#6C757D',     # Sekundär Grau
            'accent_success': '#28A745',       # Erfolg Grün
            'accent_warning': '#FFC107',       # Warnung Gelb
            'accent_danger': '#DC3545',        # Fehler Rot
            'accent_info': '#17A2B8',         # Info Cyan
            'accent_tertiary': '#6F42C1',     # Tertiär Lila
            
            # Spezielle UI Farben
            'border_light': '#DEE2E6',        # Helle Rahmen
            'border_dark': '#ADB5BD',         # Dunkle Rahmen
            'shadow': '#00000020',            # Schatten (mit Alpha)
            'highlight': '#FFF3CD',           # Highlight Gelb
            'selection': '#CCE5FF'            # Auswahl Blau
        }
    
    def setup_styles(self):
        """Definiert responsive Schriftarten und Stile"""
        self.fonts = {
            'title': self.get_responsive_font('title'),
            'subtitle': self.get_responsive_font('subtitle'),
            'header': self.get_responsive_font('header'),
            'body': self.get_responsive_font('body'),
            'button': self.get_responsive_font('button'),
            'small': self.get_responsive_font('small'),
            'tiny': self.get_responsive_font('tiny')
        }
    
    def setup_signal_definitions(self):
        """Definiert die 10 BumbleB Folien-Signale"""
        self.signal_definitions = {
            1: {'name': 'Welcome', 'content_type': 'welcome', 'description': 'Willkommen bei Bertrandt'},
            2: {'name': 'Company', 'content_type': 'company', 'description': 'Unternehmen Bertrandt'},
            3: {'name': 'Products', 'content_type': 'products', 'description': 'Unsere Produkte'},
            4: {'name': 'Innovation', 'content_type': 'innovation', 'description': 'Innovation & Technologie'},
            5: {'name': 'Technology', 'content_type': 'technology', 'description': 'Technologie-Stack'},
            6: {'name': 'References', 'content_type': 'references', 'description': 'Referenzen & Projekte'},
            7: {'name': 'Team', 'content_type': 'team', 'description': 'Unser Team'},
            8: {'name': 'Career', 'content_type': 'career', 'description': 'Karriere bei Bertrandt'},
            9: {'name': 'Contact', 'content_type': 'contact', 'description': 'Kontakt & Standorte'},
            10: {'name': 'Thanks', 'content_type': 'thanks', 'description': 'Vielen Dank'}
        }
    
    def setup_gui(self):
        """Erstellt die Haupt-GUI-Struktur"""
        print("🎨 Erstelle GUI-Struktur...")
        
        # Header-Bereich mit Logo und Navigation
        self.create_header()
        
        # Hauptcontainer
        self.main_container = tk.Frame(self.root, bg=self.colors['background_primary'])
        self.main_container.pack(fill='both', expand=True)
        
        # Status Panel (links)
        self.create_status_panel()
        
        # Content-Bereich (rechts)
        self.content_frame = tk.Frame(self.main_container, bg=self.colors['background_primary'])
        self.content_frame.pack(side='right', fill='both', expand=True)
        
        # Footer
        self.create_footer()
        
        print("✅ GUI-Struktur erstellt!")
    
    def create_header(self):
        """Erstellt den Header mit Logo und Navigation"""
        # Header Frame
        header_height = self.responsive_dims['header_height']
        self.header_frame = tk.Frame(self.root, bg=self.colors['bertrandt_blue'], height=header_height)
        self.header_frame.pack(fill='x')
        self.header_frame.pack_propagate(False)
        
        # Header Content Container
        header_content = tk.Frame(self.header_frame, bg=self.colors['bertrandt_blue'])
        header_content.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Logo und Titel (links)
        logo_frame = tk.Frame(header_content, bg=self.colors['bertrandt_blue'])
        logo_frame.pack(side='left', fill='y')
        
        # Bertrandt Logo laden
        self.load_bertrandt_logo(logo_frame)
        
        # Titel
        title_frame = tk.Frame(header_content, bg=self.colors['bertrandt_blue'])
        title_frame.pack(side='left', fill='y', padx=(20, 0))
        
        tk.Label(title_frame,
                text="BERTRANDT",
                font=self.get_responsive_font('title'),
                fg='white',
                bg=self.colors['bertrandt_blue']).pack(anchor='w')
        
        tk.Label(title_frame,
                text="Interactive Display System",
                font=self.get_responsive_font('subtitle'),
                fg=self.colors['bertrandt_light_blue'],
                bg=self.colors['bertrandt_blue']).pack(anchor='w')
        
        # Navigation Tabs (rechts)
        self.create_navigation_tabs(header_content)
    
    def load_bertrandt_logo(self, parent):
        """Lädt das Bertrandt Logo"""
        try:
            logo_path = os.path.join(os.path.dirname(__file__), "Bertrandt_logo.svg.png")
            if os.path.exists(logo_path):
                # Logo laden und skalieren
                logo_image = Image.open(logo_path)
                logo_size = int(60 * self.scale_factor)
                logo_image = logo_image.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_image)
                
                logo_label = tk.Label(parent,
                                    image=self.logo_photo,
                                    bg=self.colors['bertrandt_blue'])
                logo_label.pack(side='left', padx=(0, 10))
                
                print(f"✅ Bertrandt Logo geladen: {logo_size}x{logo_size}px")
            else:
                # Fallback Text-Logo
                tk.Label(parent,
                        text="🏢",
                        font=self.get_responsive_font('title'),
                        fg='white',
                        bg=self.colors['bertrandt_blue']).pack(side='left', padx=(0, 10))
                print("⚠️ Logo-Datei nicht gefunden - Fallback verwendet")
        except Exception as e:
            print(f"⚠️ Logo konnte nicht geladen werden: {e}")
            # Fallback
            tk.Label(parent,
                    text="🏢",
                    font=self.get_responsive_font('title'),
                    fg='white',
                    bg=self.colors['bertrandt_blue']).pack(side='left', padx=(0, 10))
    
    def create_navigation_tabs(self, parent):
        """Erstellt die Navigation Tabs"""
        nav_frame = tk.Frame(parent, bg=self.colors['bertrandt_blue'])
        nav_frame.pack(side='right', padx=self.get_responsive_padding('large'), 
                      pady=self.get_responsive_padding('medium'))
        
        self.tab_buttons = {}
        
        # Responsive Tab-Texte
        if self.layout_mode in ["desktop_xl", "desktop_large"]:
            tabs = [
                ("🏠 HOME", "home"),
                ("🎮 DEMO", "demo"), 
                ("🎨 CREATOR", "creator"),
                ("📊 PRESENTATION", "presentation")
            ]
        elif self.layout_mode in ["desktop_medium", "laptop"]:
            tabs = [
                ("🏠 HOME", "home"),
                ("🎮 DEMO", "demo"), 
                ("🎨 CREATE", "creator"),
                ("📊 PRESENT", "presentation")
            ]
        else:  # compact
            tabs = [
                ("🏠", "home"),
                ("🎮", "demo"), 
                ("🎨", "creator"),
                ("📊", "presentation")
            ]
        
        for tab_text, tab_id in tabs:
            btn = tk.Button(nav_frame,
                           text=tab_text,
                           command=lambda t=tab_id: self.switch_tab(t),
                           font=self.get_responsive_font('button'),
                           fg='white',
                           bg=self.colors['accent_primary'] if tab_id == "home" else self.colors['bertrandt_blue'],
                           relief='flat',
                           padx=self.get_responsive_padding('medium'),
                           pady=self.get_responsive_padding('small'),
                           cursor='hand2')
            btn.pack(side='left', padx=self.get_responsive_padding('small'))
            self.tab_buttons[tab_id] = btn
    
    def create_status_panel(self):
        """Erstellt das Status Panel (links)"""
        status_width = self.responsive_dims['status_width']
        self.status_panel = tk.Frame(self.main_container, bg=self.colors['background_secondary'], width=status_width)
        self.status_panel.pack(side='left', fill='y')
        self.status_panel.pack_propagate(False)
        
        # Status Header
        status_header = tk.Frame(self.status_panel, bg=self.colors['bertrandt_blue'], height=50)
        status_header.pack(fill='x')
        status_header.pack_propagate(False)
        
        tk.Label(status_header,
                text="📊 STATUS",
                font=self.get_responsive_font('header'),
                fg='white',
                bg=self.colors['bertrandt_blue']).pack(expand=True)
        
        # Status Content
        status_content = tk.Frame(self.status_panel, bg=self.colors['background_secondary'])
        status_content.pack(fill='both', expand=True, padx=10, pady=10)
        
        # System Status
        tk.Label(status_content,
                text="🖥️ System Status",
                font=self.get_responsive_font('body'),
                fg=self.colors['text_primary'],
                bg=self.colors['background_secondary']).pack(anchor='w', pady=(0, 5))
        
        self.system_status_text = tk.Text(status_content,
                                         height=4,
                                         font=self.get_responsive_font('small'),
                                         bg=self.colors['background_primary'],
                                         fg=self.colors['text_secondary'],
                                         relief='solid',
                                         bd=1)
        self.system_status_text.pack(fill='x', pady=(0, 10))
        self.system_status_text.insert('1.0', "✅ GUI gestartet\n🔄 Responsive Design aktiv\n📱 Layout: " + self.layout_mode)
        self.system_status_text.config(state='disabled')
        
        # Current Slide Info
        tk.Label(status_content,
                text="📄 Aktuelle Folie",
                font=self.get_responsive_font('body'),
                fg=self.colors['text_primary'],
                bg=self.colors['background_secondary']).pack(anchor='w', pady=(10, 5))
        
        self.current_slide_label = tk.Label(status_content,
                                           text="Folie 1: Welcome",
                                           font=self.get_responsive_font('small'),
                                           fg=self.colors['accent_primary'],
                                           bg=self.colors['background_secondary'])
        self.current_slide_label.pack(anchor='w')
        
        # Quick Actions
        tk.Label(status_content,
                text="⚡ Quick Actions",
                font=self.get_responsive_font('body'),
                fg=self.colors['text_primary'],
                bg=self.colors['background_secondary']).pack(anchor='w', pady=(20, 5))
        
        # Fullscreen Toggle
        tk.Button(status_content,
                 text="🖥️ Vollbild",
                 font=self.get_responsive_font('button'),
                 bg=self.colors['accent_info'],
                 fg='white',
                 relief='flat',
                 command=self.toggle_fullscreen).pack(fill='x', pady=2)
        
        # Demo Start/Stop
        self.demo_button = tk.Button(status_content,
                                    text="▶️ Demo Start",
                                    font=self.get_responsive_font('button'),
                                    bg=self.colors['accent_success'],
                                    fg='white',
                                    relief='flat',
                                    command=self.toggle_demo)
        self.demo_button.pack(fill='x', pady=2)
    
    def create_footer(self):
        """Erstellt den Footer"""
        footer_height = self.responsive_dims['footer_height']
        self.footer_frame = tk.Frame(self.root, bg=self.colors['background_secondary'], height=footer_height)
        self.footer_frame.pack(side='bottom', fill='x')
        self.footer_frame.pack_propagate(False)
        
        # Footer Content
        footer_content = tk.Frame(self.footer_frame, bg=self.colors['background_secondary'])
        footer_content.pack(fill='both', expand=True, padx=10)
        
        # Status Text
        self.footer_status = tk.Label(footer_content,
                                     text="Bertrandt Interactive Display System - Bereit",
                                     font=self.get_responsive_font('tiny'),
                                     fg=self.colors['text_secondary'],
                                     bg=self.colors['background_secondary'])
        self.footer_status.pack(side='left', expand=True)
        
        # Version Info
        tk.Label(footer_content,
                text="v2.0",
                font=self.get_responsive_font('tiny'),
                fg=self.colors['text_light'],
                bg=self.colors['background_secondary']).pack(side='right')
    
    def switch_tab(self, tab_name):
        """Zentrale Tab-Switching Logik"""
        print(f"📋 Wechsle zu Tab: {tab_name}")
        
        self.current_tab = tab_name
        
        # Update button colors
        for tab_id, btn in self.tab_buttons.items():
            if tab_id == tab_name:
                btn.config(bg=self.colors['accent_primary'])
            else:
                btn.config(bg=self.colors['bertrandt_blue'])
        
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Load tab content
        try:
            if tab_name == "home":
                self.create_home_tab()
            elif tab_name == "demo":
                self.create_demo_tab()
            elif tab_name == "creator":
                self.create_creator_tab()
            elif tab_name == "presentation":
                self.create_presentation_tab()
            
            # Update footer status
            self.footer_status.config(text=f"Bertrandt Interactive Display - {tab_name.upper()} Tab aktiv")
            
        except Exception as e:
            print(f"❌ Fehler beim Laden von Tab {tab_name}: {e}")
            self.show_error_tab(tab_name, str(e))
    
    def show_error_tab(self, tab_name, error_msg):
        """Zeigt Fehler-Tab bei Problemen"""
        error_frame = tk.Frame(self.content_frame, bg=self.colors['background_primary'])
        error_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(error_frame,
                text=f"❌ Fehler beim Laden von {tab_name.upper()}",
                font=self.get_responsive_font('header'),
                fg=self.colors['accent_danger'],
                bg=self.colors['background_primary']).pack(pady=20)
        
        tk.Label(error_frame,
                text=f"Fehlermeldung:\n{error_msg}",
                font=self.get_responsive_font('body'),
                fg=self.colors['text_secondary'],
                bg=self.colors['background_primary'],
                justify='left').pack(pady=10)
        
        tk.Button(error_frame,
                 text="🔄 Erneut versuchen",
                 font=self.get_responsive_font('button'),
                 bg=self.colors['accent_primary'],
                 fg='white',
                 command=lambda: self.switch_tab(tab_name)).pack(pady=20)
    
    def create_home_tab(self):
        """Erstellt den HOME Tab mit 6 Feature-Cards"""
        print("🏠 Erstelle HOME Tab...")
        
        # Main container
        home_container = tk.Frame(self.content_frame, bg=self.colors['background_primary'])
        home_container.pack(fill='both', expand=True)
        
        # Header
        header_frame = tk.Frame(home_container, bg=self.colors['background_primary'])
        header_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(header_frame,
                text="🏠 BERTRANDT INTERACTIVE DISPLAY",
                font=self.get_responsive_font('title'),
                fg=self.colors['bertrandt_blue'],
                bg=self.colors['background_primary']).pack()
        
        tk.Label(header_frame,
                text="Willkommen bei der interaktiven Bertrandt Präsentation",
                font=self.get_responsive_font('subtitle'),
                fg=self.colors['text_secondary'],
                bg=self.colors['background_primary']).pack(pady=(5, 0))
        
        # Cards Container (3x2 Grid)
        cards_frame = tk.Frame(home_container, bg=self.colors['background_primary'])
        cards_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Configure grid
        for i in range(3):
            cards_frame.grid_columnconfigure(i, weight=1)
        for i in range(2):
            cards_frame.grid_rowconfigure(i, weight=1)
        
        # Feature Cards Data
        cards_data = [
            {
                'title': '🎮 DEMO MODUS',
                'subtitle': 'Automatische Präsentation',
                'description': 'Erleben Sie unsere BumbleB Technologie in einer automatischen Demo-Präsentation',
                'button_text': 'Demo starten',
                'button_color': self.colors['accent_success'],
                'action': lambda: self.switch_tab('demo')
            },
            {
                'title': '🎨 CONTENT CREATOR',
                'subtitle': 'Inhalte bearbeiten',
                'description': 'Bearbeiten und erstellen Sie Präsentationsinhalte mit unserem Editor',
                'button_text': 'Editor öffnen',
                'button_color': self.colors['accent_primary'],
                'action': lambda: self.switch_tab('creator')
            },
            {
                'title': '📊 PRÄSENTATION',
                'subtitle': 'Vollbild-Modus',
                'description': 'Starten Sie die Vollbild-Präsentation für Ihren Messestand',
                'button_text': 'Präsentation',
                'button_color': self.colors['accent_info'],
                'action': lambda: self.switch_tab('presentation')
            },
            {
                'title': '🚗 BUMBLEBEE',
                'subtitle': 'Autonomes Fahrzeug',
                'description': 'Entdecken Sie unser autonomes Shuttle-System der nächsten Generation',
                'button_text': 'Mehr erfahren',
                'button_color': self.colors['bertrandt_blue'],
                'action': lambda: self.load_content_page(1)
            },
            {
                'title': '🔧 TECHNOLOGIE',
                'subtitle': 'Innovation & Engineering',
                'description': 'Modernste Technologien und Entwicklungsmethoden bei Bertrandt',
                'button_text': 'Technologien',
                'button_color': self.colors['accent_warning'],
                'action': lambda: self.load_content_page(5)
            },
            {
                'title': '👥 KARRIERE',
                'subtitle': 'Werden Sie Teil des Teams',
                'description': 'Entdecken Sie spannende Karrieremöglichkeiten bei Bertrandt',
                'button_text': 'Jobs ansehen',
                'button_color': self.colors['accent_tertiary'],
                'action': lambda: self.load_content_page(8)
            }
        ]
        
        # Create cards
        for i, card_data in enumerate(cards_data):
            row = i // 3
            col = i % 3
            self.create_feature_card(cards_frame, card_data, row, col)
        
        # Current content display area
        self.content_display_frame = tk.Frame(home_container, bg=self.colors['background_secondary'], relief='solid', bd=1)
        self.content_display_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Load initial content (Welcome page)
        self.load_content_page(1)
        
        print("✅ HOME Tab erstellt!")
    
    def create_feature_card(self, parent, card_data, row, col):
        """Erstellt eine Feature-Card"""
        card_width = self.responsive_dims['card_width']
        card_height = self.responsive_dims['card_height']
        
        # Card Frame
        card_frame = tk.Frame(parent, 
                             bg=self.colors['background_primary'],
                             relief='solid',
                             bd=1,
                             width=card_width,
                             height=card_height)
        card_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
        card_frame.grid_propagate(False)
        
        # Card Content
        content_frame = tk.Frame(card_frame, bg=self.colors['background_primary'])
        content_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Title
        tk.Label(content_frame,
                text=card_data['title'],
                font=self.get_responsive_font('header'),
                fg=self.colors['bertrandt_blue'],
                bg=self.colors['background_primary']).pack(anchor='w')
        
        # Subtitle
        tk.Label(content_frame,
                text=card_data['subtitle'],
                font=self.get_responsive_font('body'),
                fg=self.colors['text_secondary'],
                bg=self.colors['background_primary']).pack(anchor='w', pady=(2, 8))
        
        # Description
        tk.Label(content_frame,
                text=card_data['description'],
                font=self.get_responsive_font('small'),
                fg=self.colors['text_primary'],
                bg=self.colors['background_primary'],
                wraplength=card_width-30,
                justify='left').pack(anchor='w', pady=(0, 15))
        
        # Action Button
        tk.Button(content_frame,
                 text=card_data['button_text'],
                 font=self.get_responsive_font('button'),
                 bg=card_data['button_color'],
                 fg='white',
                 relief='flat',
                 padx=15,
                 pady=8,
                 cursor='hand2',
                 command=card_data['action']).pack(anchor='w')
        
        # Hover effects
        def on_enter(event):
            card_frame.config(relief='solid', bd=2, bg=self.colors['background_secondary'])
            content_frame.config(bg=self.colors['background_secondary'])
            for child in content_frame.winfo_children():
                if isinstance(child, tk.Label):
                    child.config(bg=self.colors['background_secondary'])
        
        def on_leave(event):
            card_frame.config(relief='solid', bd=1, bg=self.colors['background_primary'])
            content_frame.config(bg=self.colors['background_primary'])
            for child in content_frame.winfo_children():
                if isinstance(child, tk.Label):
                    child.config(bg=self.colors['background_primary'])
        
        card_frame.bind("<Enter>", on_enter)
        card_frame.bind("<Leave>", on_leave)
        content_frame.bind("<Enter>", on_enter)
        content_frame.bind("<Leave>", on_leave)
    
    def load_content_page(self, signal_id):
        """Lädt eine spezifische Content-Seite"""
        print(f"📄 Lade Content-Seite {signal_id}")
        
        # Clear content display
        for widget in self.content_display_frame.winfo_children():
            widget.destroy()
        
        # Load slide config
        slide_config = self.load_slide_config(signal_id)
        signal_info = self.signal_definitions.get(signal_id, {})
        
        # Update current slide info
        self.current_slide = signal_id
        slide_name = signal_info.get('name', f'Folie {signal_id}')
        self.current_slide_label.config(text=f"Folie {signal_id}: {slide_name}")
        
        # Create content layout
        self.create_content_layout(slide_config, signal_id)
    
    def load_slide_config(self, slide_id):
        """Lädt die Konfiguration einer Folie"""
        signal_info = self.signal_definitions.get(slide_id, {})
        content_type = signal_info.get('content_type', 'welcome')
        page_dir = os.path.join(self.content_dir, f"page_{slide_id}_{content_type}")
        config_path = os.path.join(page_dir, "config.json")
        
        # Default config
        default_config = {
            "title": signal_info.get('name', f'Folie {slide_id}'),
            "subtitle": f"Bertrandt {signal_info.get('name', f'Folie {slide_id}')}",
            "text_content": signal_info.get('description', f'Inhalt für Folie {slide_id}'),
            "layout": "text_only",
            "background_image": "",
            "video": "",
            "images": []
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            else:
                return default_config
        except Exception as e:
            print(f"⚠️ Fehler beim Laden der Konfiguration für Folie {slide_id}: {e}")
            return default_config
    
    def create_content_layout(self, config, signal_id):
        """Erstellt das Content-Layout basierend auf der Konfiguration"""
        # Header
        header_frame = tk.Frame(self.content_display_frame, bg=self.colors['background_secondary'])
        header_frame.pack(fill='x', padx=20, pady=20)
        
        # Title
        tk.Label(header_frame,
                text=config.get('title', 'Titel'),
                font=self.get_responsive_font('title'),
                fg=self.colors['bertrandt_blue'],
                bg=self.colors['background_secondary']).pack(anchor='w')
        
        # Subtitle
        if config.get('subtitle'):
            tk.Label(header_frame,
                    text=config.get('subtitle'),
                    font=self.get_responsive_font('subtitle'),
                    fg=self.colors['text_secondary'],
                    bg=self.colors['background_secondary']).pack(anchor='w', pady=(5, 0))
        
        # Content
        content_frame = tk.Frame(self.content_display_frame, bg=self.colors['background_primary'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Text content
        if config.get('text_content'):
            text_widget = tk.Text(content_frame,
                                 font=self.get_responsive_font('body'),
                                 bg=self.colors['background_primary'],
                                 fg=self.colors['text_primary'],
                                 relief='flat',
                                 wrap='word',
                                 height=8)
            text_widget.pack(fill='both', expand=True, padx=10, pady=10)
            text_widget.insert('1.0', config.get('text_content'))
            text_widget.config(state='disabled')
    
    def create_demo_tab(self):
        """Erstellt den DEMO Tab mit 16:9 Canvas und Steuerung"""
        print("🎮 Erstelle DEMO Tab...")
        
        # Main container
        demo_container = tk.Frame(self.content_frame, bg=self.colors['background_primary'])
        demo_container.pack(fill='both', expand=True)
        
        # Header
        header_frame = tk.Frame(demo_container, bg=self.colors['background_primary'])
        header_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(header_frame,
                text="🎮 DEMO MODUS",
                font=self.get_responsive_font('title'),
                fg=self.colors['bertrandt_blue'],
                bg=self.colors['background_primary']).pack()
        
        tk.Label(header_frame,
                text="Automatische BumbleB Präsentation",
                font=self.get_responsive_font('subtitle'),
                fg=self.colors['text_secondary'],
                bg=self.colors['background_primary']).pack(pady=(5, 0))
        
        # Controls
        controls_frame = tk.Frame(demo_container, bg=self.colors['background_secondary'])
        controls_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # Control buttons
        buttons_frame = tk.Frame(controls_frame, bg=self.colors['background_secondary'])
        buttons_frame.pack(pady=15)
        
        # Previous button
        tk.Button(buttons_frame,
                 text="⏮️ ZURÜCK",
                 font=self.get_responsive_font('button'),
                 bg=self.colors['accent_secondary'],
                 fg='white',
                 relief='flat',
                 padx=20, pady=10,
                 command=self.demo_previous).pack(side='left', padx=5)
        
        # Play/Pause button
        self.demo_play_button = tk.Button(buttons_frame,
                                         text="▶️ PLAY",
                                         font=self.get_responsive_font('button'),
                                         bg=self.colors['accent_success'],
                                         fg='white',
                                         relief='flat',
                                         padx=20, pady=10,
                                         command=self.toggle_demo_play)
        self.demo_play_button.pack(side='left', padx=5)
        
        # Next button
        tk.Button(buttons_frame,
                 text="⏭️ VOR",
                 font=self.get_responsive_font('button'),
                 bg=self.colors['accent_secondary'],
                 fg='white',
                 relief='flat',
                 padx=20, pady=10,
                 command=self.demo_next).pack(side='left', padx=5)
        
        # Status
        self.demo_status_label = tk.Label(controls_frame,
                                         text="Folie 1 von 10",
                                         font=self.get_responsive_font('body'),
                                         fg=self.colors['text_primary'],
                                         bg=self.colors['background_secondary'])
        self.demo_status_label.pack(pady=(0, 10))
        
        # Demo Canvas (16:9 Format)
        canvas_container = tk.Frame(demo_container, bg='#000000')  # Schwarzer Rahmen
        canvas_container.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Calculate 16:9 dimensions
        available_width = int(self.screen_width * 0.6)  # 60% der Bildschirmbreite
        canvas_width = min(available_width, 1000)
        canvas_height = int(canvas_width * 9 / 16)  # 16:9 Verhältnis
        
        self.demo_canvas = tk.Frame(canvas_container, 
                                   bg=self.colors['background_primary'],
                                   width=canvas_width,
                                   height=canvas_height)
        self.demo_canvas.pack(expand=True)
        self.demo_canvas.pack_propagate(False)
        
        print(f"📐 Demo Canvas: {canvas_width}x{canvas_height} (16:9 Format)")
        
        # Load initial demo content
        self.demo_slide = 1
        self.demo_auto_advance = False
        self.load_demo_content(1)
        
        print("✅ DEMO Tab erstellt!")
    
    def load_demo_content(self, slide_id):
        """Lädt Content für Demo-Modus"""
        # Clear canvas
        for widget in self.demo_canvas.winfo_children():
            widget.destroy()
        
        # Load slide config
        slide_config = self.load_slide_config(slide_id)
        signal_info = self.signal_definitions.get(slide_id, {})
        
        # Update status
        self.demo_slide = slide_id
        self.demo_status_label.config(text=f"Folie {slide_id} von 10")
        
        # Create demo layout
        demo_content = tk.Frame(self.demo_canvas, bg=self.colors['background_primary'])
        demo_content.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Title
        tk.Label(demo_content,
                text=slide_config.get('title', 'Titel'),
                font=self.get_responsive_font('title'),
                fg=self.colors['bertrandt_blue'],
                bg=self.colors['background_primary']).pack(pady=(0, 20))
        
        # Content
        if slide_config.get('text_content'):
            content_text = slide_config.get('text_content')[:200] + "..." if len(slide_config.get('text_content', '')) > 200 else slide_config.get('text_content', '')
            tk.Label(demo_content,
                    text=content_text,
                    font=self.get_responsive_font('body'),
                    fg=self.colors['text_primary'],
                    bg=self.colors['background_primary'],
                    wraplength=600,
                    justify='center').pack(expand=True)
        
        print(f"📄 Demo Folie {slide_id} geladen: {slide_config.get('title', 'Titel')[:50]}...")
    
    def demo_previous(self):
        """Vorherige Demo-Folie"""
        if self.demo_slide > 1:
            self.load_demo_content(self.demo_slide - 1)
    
    def demo_next(self):
        """Nächste Demo-Folie"""
        if self.demo_slide < 10:
            self.load_demo_content(self.demo_slide + 1)
        else:
            self.load_demo_content(1)  # Loop zurück zu Folie 1
    
    def toggle_demo_play(self):
        """Startet/Stoppt automatische Demo"""
        if self.demo_auto_advance:
            self.stop_demo_auto_advance()
        else:
            self.start_demo_auto_advance()
    
    def start_demo_auto_advance(self):
        """Startet automatischen Folienwechsel"""
        self.demo_auto_advance = True
        self.demo_play_button.config(text="⏸️ PAUSE", bg=self.colors['accent_warning'])
        self.schedule_next_demo_slide()
        print("▶️ Demo Auto-Advance gestartet")
    
    def stop_demo_auto_advance(self):
        """Stoppt automatischen Folienwechsel"""
        self.demo_auto_advance = False
        self.demo_play_button.config(text="▶️ PLAY", bg=self.colors['accent_success'])
        if self.demo_timer:
            self.root.after_cancel(self.demo_timer)
            self.demo_timer = None
        print("⏸️ Demo Auto-Advance gestoppt")
    
    def schedule_next_demo_slide(self):
        """Plant nächsten automatischen Folienwechsel"""
        if self.demo_auto_advance:
            self.demo_timer = self.root.after(2500, self.auto_advance_demo)  # 2.5 Sekunden
    
    def auto_advance_demo(self):
        """Automatischer Folienwechsel"""
        if self.demo_auto_advance:
            self.demo_next()
            self.schedule_next_demo_slide()
    
    def create_creator_tab(self):
        """Erstellt den Content Creator Tab"""
        print("🎨 Erstelle CREATOR Tab...")
        
        # Main container
        creator_container = tk.Frame(self.content_frame, bg=self.colors['background_primary'])
        creator_container.pack(fill='both', expand=True)
        
        # Header
        header_frame = tk.Frame(creator_container, bg=self.colors['background_primary'])
        header_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(header_frame,
                text="🎨 CONTENT CREATOR",
                font=self.get_responsive_font('title'),
                fg=self.colors['bertrandt_blue'],
                bg=self.colors['background_primary']).pack()
        
        tk.Label(header_frame,
                text="Bearbeiten Sie Präsentationsinhalte",
                font=self.get_responsive_font('subtitle'),
                fg=self.colors['text_secondary'],
                bg=self.colors['background_primary']).pack(pady=(5, 0))
        
        # Toolbar
        toolbar_frame = tk.Frame(creator_container, bg=self.colors['background_secondary'])
        toolbar_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        toolbar_content = tk.Frame(toolbar_frame, bg=self.colors['background_secondary'])
        toolbar_content.pack(pady=15)
        
        # Toolbar buttons
        tk.Button(toolbar_content,
                 text="💾 ALLE SPEICHERN",
                 font=self.get_responsive_font('button'),
                 bg=self.colors['accent_success'],
                 fg='white',
                 relief='flat',
                 padx=15, pady=8,
                 command=self.save_all_slides).pack(side='left', padx=5)
        
        tk.Button(toolbar_content,
                 text="👁️ VORSCHAU",
                 font=self.get_responsive_font('button'),
                 bg=self.colors['accent_primary'],
                 fg='white',
                 relief='flat',
                 padx=15, pady=8,
                 command=self.preview_current_slide).pack(side='left', padx=5)
        
        tk.Button(toolbar_content,
                 text="➕ NEUE FOLIE",
                 font=self.get_responsive_font('button'),
                 bg=self.colors['accent_info'],
                 fg='white',
                 relief='flat',
                 padx=15, pady=8,
                 command=self.add_new_slide).pack(side='left', padx=5)
        
        # Main editor area
        editor_container = tk.Frame(creator_container, bg=self.colors['background_primary'])
        editor_container.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Left panel - Slides overview
        left_width = self.responsive_dims['left_panel_width']
        left_panel = tk.Frame(editor_container, bg=self.colors['background_secondary'], 
                             width=left_width, relief='solid', bd=1)
        left_panel.pack(side='left', fill='y', padx=(0, 15))
        left_panel.pack_propagate(False)
        
        # Slides header
        slides_header = tk.Frame(left_panel, bg=self.colors['bertrandt_blue'], height=50)
        slides_header.pack(fill='x')
        slides_header.pack_propagate(False)
        
        tk.Label(slides_header,
                text="📑 FOLIEN ÜBERSICHT",
                font=self.get_responsive_font('header'),
                fg='white',
                bg=self.colors['bertrandt_blue']).pack(expand=True)
        
        # Slides list
        slides_scroll_frame = tk.Frame(left_panel, bg=self.colors['background_secondary'])
        slides_scroll_frame.pack(fill='both', expand=True, padx=8, pady=8)
        
        # Create slide thumbnails
        for i in range(1, 11):
            self.create_slide_thumbnail(slides_scroll_frame, i)
        
        # Right panel - Editor
        right_panel = tk.Frame(editor_container, bg=self.colors['background_primary'], relief='solid', bd=1)
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Editor header
        editor_header = tk.Frame(right_panel, bg=self.colors['background_secondary'], height=50)
        editor_header.pack(fill='x')
        editor_header.pack_propagate(False)
        
        self.editor_title_label = tk.Label(editor_header,
                                          text="📝 SLIDE EDITOR - Folie 1",
                                          font=self.get_responsive_font('header'),
                                          fg=self.colors['text_primary'],
                                          bg=self.colors['background_secondary'])
        self.editor_title_label.pack(expand=True)
        
        # Editor content
        self.editor_content_frame = tk.Frame(right_panel, bg=self.colors['background_primary'])
        self.editor_content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Load initial editor
        self.load_slide_editor(1)
        
        print("✅ CREATOR Tab erstellt!")
    
    def create_slide_thumbnail(self, parent, slide_id):
        """Erstellt ein Folien-Thumbnail"""
        slide_config = self.load_slide_config(slide_id)
        signal_info = self.signal_definitions.get(slide_id, {})
        
        # Thumbnail container
        thumb_frame = tk.Frame(parent, bg=self.colors['background_primary'], 
                              relief='solid', bd=1 if slide_id != 1 else 3)
        thumb_frame.pack(fill='x', pady=5, padx=5)
        
        if slide_id == 1:  # Active slide
            thumb_frame.config(highlightbackground=self.colors['bertrandt_blue'], highlightthickness=2)
        
        # Header with slide number and status
        header_row = tk.Frame(thumb_frame, bg=self.colors['background_primary'])
        header_row.pack(fill='x', padx=10, pady=8)
        
        # Slide badge
        slide_badge = tk.Frame(header_row, bg=self.colors['bertrandt_blue'])
        slide_badge.pack(side='left')
        tk.Label(slide_badge, text=f"{slide_id}", 
                font=self.get_responsive_font('button'),
                fg='white', bg=self.colors['bertrandt_blue'],
                padx=8, pady=4).pack()
        
        # Status badge
        status_color = self.colors['accent_success'] if slide_id <= 3 else self.colors['accent_warning'] if slide_id <= 7 else self.colors['accent_danger']
        status_text = '✓ Fertig' if slide_id <= 3 else '⚠ In Arbeit' if slide_id <= 7 else '○ Neu'
        
        status_badge = tk.Frame(header_row, bg=status_color)
        status_badge.pack(side='right')
        tk.Label(status_badge, text=status_text,
                font=self.get_responsive_font('small'),
                fg='white', bg=status_color,
                padx=8, pady=4).pack()
        
        # Preview content
        preview_frame = tk.Frame(thumb_frame, bg=self.colors['background_secondary'], 
                                height=int(self.responsive_dims['thumbnail_height'] * 0.8))
        preview_frame.pack(fill='x', padx=10, pady=(0, 10))
        preview_frame.pack_propagate(False)
        
        # Title
        title_text = slide_config.get('title', f'Folie {slide_id}')[:50]
        tk.Label(preview_frame, text=title_text,
                font=self.get_responsive_font('body'),
                fg=self.colors['text_primary'],
                bg=self.colors['background_secondary'],
                wraplength=left_width-40).pack(anchor='nw', padx=10, pady=8)
        
        # Content preview
        content_text = slide_config.get('text_content', '')[:100] + "..." if len(slide_config.get('text_content', '')) > 100 else slide_config.get('text_content', '')
        if content_text:
            tk.Label(preview_frame, text=content_text,
                    font=self.get_responsive_font('small'),
                    fg=self.colors['text_secondary'],
                    bg=self.colors['background_secondary'],
                    wraplength=left_width-40,
                    justify='left').pack(anchor='nw', padx=10)
        
        # Click handler
        def select_slide():
            self.select_slide_for_editing(slide_id)
        
        thumb_frame.bind("<Button-1>", lambda e: select_slide())
        preview_frame.bind("<Button-1>", lambda e: select_slide())
    
    def load_slide_editor(self, slide_id):
        """Lädt den Editor für eine spezifische Folie"""
        self.current_edit_slide = slide_id
        
        # Clear editor
        for widget in self.editor_content_frame.winfo_children():
            widget.destroy()
        
        # Update title
        signal_info = self.signal_definitions.get(slide_id, {})
        slide_name = signal_info.get('name', f'Folie {slide_id}')
        self.editor_title_label.config(text=f"📝 SLIDE EDITOR - {slide_name}")
        
        # Load slide config
        slide_config = self.load_slide_config(slide_id)
        
        # Create editor form
        tk.Label(self.editor_content_frame,
                text=f"Bearbeitung: {slide_config.get('title', 'Titel')}",
                font=self.get_responsive_font('header'),
                fg=self.colors['bertrandt_blue'],
                bg=self.colors['background_primary']).pack(anchor='w', pady=(0, 20))
        
        # Title field
        tk.Label(self.editor_content_frame,
                text="Titel:",
                font=self.get_responsive_font('body'),
                fg=self.colors['text_primary'],
                bg=self.colors['background_primary']).pack(anchor='w')
        
        self.title_entry = tk.Entry(self.editor_content_frame,
                                   font=self.get_responsive_font('body'),
                                   width=50)
        self.title_entry.pack(fill='x', pady=(5, 15))
        self.title_entry.insert(0, slide_config.get('title', ''))
        
        # Content field
        tk.Label(self.editor_content_frame,
                text="Inhalt:",
                font=self.get_responsive_font('body'),
                fg=self.colors['text_primary'],
                bg=self.colors['background_primary']).pack(anchor='w')
        
        self.content_text = tk.Text(self.editor_content_frame,
                                   font=self.get_responsive_font('body'),
                                   height=10,
                                   wrap='word')
        self.content_text.pack(fill='both', expand=True, pady=(5, 15))
        self.content_text.insert('1.0', slide_config.get('text_content', ''))
        
        # Save button
        tk.Button(self.editor_content_frame,
                 text="💾 FOLIE SPEICHERN",
                 font=self.get_responsive_font('button'),
                 bg=self.colors['accent_success'],
                 fg='white',
                 relief='flat',
                 padx=20, pady=10,
                 command=lambda: self.save_slide(slide_id)).pack(anchor='w', pady=10)
        
        print(f"📝 Editor für Folie {slide_id} geladen")
    
    def select_slide_for_editing(self, slide_id):
        """Wählt eine Folie zur Bearbeitung aus"""
        print(f"✏️ Wähle Folie {slide_id} zur Bearbeitung")
        self.load_slide_editor(slide_id)
    
    def save_slide(self, slide_id):
        """Speichert eine einzelne Folie"""
        try:
            # Get content from editor
            title = self.title_entry.get()
            content = self.content_text.get('1.0', 'end-1c')
            
            # Create config
            signal_info = self.signal_definitions.get(slide_id, {})
            content_type = signal_info.get('content_type', 'welcome')
            page_dir = os.path.join(self.content_dir, f"page_{slide_id}_{content_type}")
            
            if not os.path.exists(page_dir):
                os.makedirs(page_dir)
            
            config = {
                "title": title,
                "subtitle": f"Bertrandt {signal_info.get('name', f'Folie {slide_id}')}",
                "text_content": content,
                "layout": "text_only",
                "background_image": "",
                "video": "",
                "images": []
            }
            
            config_path = os.path.join(page_dir, "config.json")
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Folie {slide_id} gespeichert!")
            messagebox.showinfo("Gespeichert", f"Folie {slide_id} wurde erfolgreich gespeichert!")
            
        except Exception as e:
            print(f"❌ Fehler beim Speichern von Folie {slide_id}: {e}")
            messagebox.showerror("Fehler", f"Folie {slide_id} konnte nicht gespeichert werden:\n{str(e)}")
    
    def save_all_slides(self):
        """Speichert alle Folien"""
        print("💾 Speichere alle Folien...")
        saved_count = 0
        
        for slide_id in range(1, 11):
            try:
                signal_info = self.signal_definitions.get(slide_id, {})
                content_type = signal_info.get('content_type', 'welcome')
                page_dir = os.path.join(self.content_dir, f"page_{slide_id}_{content_type}")
                
                if not os.path.exists(page_dir):
                    os.makedirs(page_dir)
                
                config_path = os.path.join(page_dir, "config.json")
                if not os.path.exists(config_path):
                    config = {
                        "title": signal_info.get('name', f'Folie {slide_id}'),
                        "subtitle": f"Bertrandt {signal_info.get('name', f'Folie {slide_id}')}",
                        "text_content": signal_info.get('description', f'Inhalt für Folie {slide_id}'),
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
        messagebox.showinfo("Erfolg", f"{saved_count} neue Folien wurden erstellt und gespeichert!")
    
    def preview_current_slide(self):
        """Zeigt Vorschau der aktuellen Folie"""
        print(f"👁️ Vorschau für Folie {self.current_edit_slide}")
        self.switch_tab("home")
        self.load_content_page(self.current_edit_slide)
        messagebox.showinfo("Vorschau", f"Folie {self.current_edit_slide} wird im HOME-Tab angezeigt")
    
    def add_new_slide(self):
        """Fügt eine neue Folie hinzu"""
        print("➕ Neue Folie wird hinzugefügt")
        messagebox.showinfo("Neue Folie", "Funktion 'Neue Folie' ist in Entwicklung!")
    
    def create_presentation_tab(self):
        """Erstellt den Presentation Tab"""
        print("📊 Erstelle PRESENTATION Tab...")
        
        # Main container
        presentation_container = tk.Frame(self.content_frame, bg=self.colors['background_primary'])
        presentation_container.pack(fill='both', expand=True)
        
        # Header
        header_frame = tk.Frame(presentation_container, bg=self.colors['background_primary'])
        header_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(header_frame,
                text="📊 PRÄSENTATIONS-MODUS",
                font=self.get_responsive_font('title'),
                fg=self.colors['bertrandt_blue'],
                bg=self.colors['background_primary']).pack()
        
        tk.Label(header_frame,
                text="Vollbild-Präsentationen für Ihren Messestand",
                font=self.get_responsive_font('subtitle'),
                fg=self.colors['text_secondary'],
                bg=self.colors['background_primary']).pack(pady=(5, 0))
        
        # Options grid
        options_frame = tk.Frame(presentation_container, bg=self.colors['background_primary'])
        options_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Configure grid
        for i in range(2):
            options_frame.grid_columnconfigure(i, weight=1)
        for i in range(2):
            options_frame.grid_rowconfigure(i, weight=1)
        
        # Presentation options
        presentation_options = [
            {
                'title': '🖥️ VOLLBILD-PRÄSENTATION',
                'description': 'Startet die Präsentation im Vollbild-Modus mit manueller Steuerung',
                'button_text': 'Vollbild starten',
                'button_color': self.colors['accent_primary'],
                'action': self.start_fullscreen_presentation
            },
            {
                'title': '🔄 AUTO-LOOP MODUS',
                'description': 'Automatische Endlos-Präsentation perfekt für Messestände',
                'button_text': 'Auto-Loop starten',
                'button_color': self.colors['accent_success'],
                'action': self.start_auto_loop
            },
            {
                'title': '⚙️ PRÄSENTATIONS-EINSTELLUNGEN',
                'description': 'Konfigurieren Sie Timing, Übergänge und weitere Optionen',
                'button_text': 'Einstellungen öffnen',
                'button_color': self.colors['accent_info'],
                'action': self.open_presentation_settings
            },
            {
                'title': '📤 EXPORT & TEILEN',
                'description': 'Exportieren Sie Ihre Präsentation oder teilen Sie sie mit anderen',
                'button_text': 'Export-Optionen',
                'button_color': self.colors['accent_warning'],
                'action': self.open_export_options
            }
        ]
        
        # Create option cards
        for i, option in enumerate(presentation_options):
            row = i // 2
            col = i % 2
            self.create_presentation_option_card(options_frame, option, row, col)
        
        print("✅ PRESENTATION Tab erstellt!")
    
    def create_presentation_option_card(self, parent, option_data, row, col):
        """Erstellt eine Präsentations-Option-Card"""
        card_frame = tk.Frame(parent, 
                             bg=self.colors['background_secondary'],
                             relief='solid',
                             bd=1)
        card_frame.grid(row=row, column=col, padx=15, pady=15, sticky='nsew')
        
        # Card content
        content_frame = tk.Frame(card_frame, bg=self.colors['background_secondary'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(content_frame,
                text=option_data['title'],
                font=self.get_responsive_font('header'),
                fg=self.colors['bertrandt_blue'],
                bg=self.colors['background_secondary']).pack(anchor='w', pady=(0, 10))
        
        # Description
        tk.Label(content_frame,
                text=option_data['description'],
                font=self.get_responsive_font('body'),
                fg=self.colors['text_primary'],
                bg=self.colors['background_secondary'],
                wraplength=300,
                justify='left').pack(anchor='w', pady=(0, 20))
        
        # Action button
        tk.Button(content_frame,
                 text=option_data['button_text'],
                 font=self.get_responsive_font('button'),
                 bg=option_data['button_color'],
                 fg='white',
                 relief='flat',
                 padx=20, pady=10,
                 cursor='hand2',
                 command=option_data['action']).pack(anchor='w')
    
    def start_fullscreen_presentation(self):
        """Startet Vollbild-Präsentation"""
        print("🖥️ Vollbild-Präsentation wird gestartet...")
        if not self.fullscreen:
            self.toggle_fullscreen()
        self.switch_tab("demo")
        messagebox.showinfo("Vollbild", "Vollbild-Präsentation gestartet!\nESC zum Beenden, F11 zum Umschalten")
    
    def start_auto_loop(self):
        """Startet Auto-Loop Präsentation"""
        print("🔄 Auto-Loop wird gestartet...")
        self.switch_tab("demo")
        if hasattr(self, 'start_demo_auto_advance'):
            self.start_demo_auto_advance()
        messagebox.showinfo("Auto-Loop", 
            "Auto-Loop Präsentation gestartet!\n\n" +
            "• Automatischer Folienwechsel alle 2,5 Sekunden\n" +
            "• Endlos-Schleife von Folie 1-10\n" +
            "• PAUSE-Button zum Stoppen")
    
    def open_presentation_settings(self):
        """Öffnet Präsentations-Einstellungen"""
        print("⚙️ Präsentations-Einstellungen werden geöffnet...")
        messagebox.showinfo("Einstellungen", "Präsentations-Einstellungen sind in Entwicklung!")
    
    def open_export_options(self):
        """Öffnet Export-Optionen"""
        print("📤 Export-Optionen werden geöffnet...")
        messagebox.showinfo("Export", "Export-Funktionen sind in Entwicklung!")
    
    # Utility functions
    def toggle_fullscreen(self):
        """Schaltet Vollbild-Modus um"""
        self.fullscreen = not self.fullscreen
        self.root.attributes('-fullscreen', self.fullscreen)
        print(f"🖥️ Vollbild: {'Ein' if self.fullscreen else 'Aus'}")
    
    def toggle_demo(self):
        """Startet/Stoppt Demo"""
        if self.demo_running:
            self.stop_demo()
        else:
            self.start_demo()
    
    def start_demo(self):
        """Startet Demo"""
        self.demo_running = True
        self.demo_button.config(text="⏸️ Demo Stop", bg=self.colors['accent_danger'])
        self.switch_tab("demo")
        if hasattr(self, 'start_demo_auto_advance'):
            self.start_demo_auto_advance()
        print("▶️ Demo gestartet")
    
    def stop_demo(self):
        """Stoppt Demo"""
        self.demo_running = False
        self.demo_button.config(text="▶️ Demo Start", bg=self.colors['accent_success'])
        if hasattr(self, 'stop_demo_auto_advance'):
            self.stop_demo_auto_advance()
        print("⏸️ Demo gestoppt")


# Main execution
if __name__ == "__main__":
    try:
        app = BertrandtGUI()
        print("🚀 Starte Bertrandt GUI...")
        app.root.mainloop()
    except KeyboardInterrupt:
        print("\n🛑 Programm durch Benutzer beendet")
    except Exception as e:
        print(f"❌ Kritischer Fehler: {e}")
        import traceback
        traceback.print_exc()