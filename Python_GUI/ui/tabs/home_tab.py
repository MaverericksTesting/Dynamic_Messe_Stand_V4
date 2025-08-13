#!/usr/bin/env python3
"""
Home Tab für Dynamic Messe Stand V4
Moderne, kompakte Startseite für Laien
"""

import tkinter as tk
from tkinter import ttk
from core.theme import theme_manager
from core.logger import logger

class HomeTab:
    """Home-Tab mit Feature-Karten"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.visible = False
        
        self.create_home_content()
    
    def create_home_content(self):
        """Erstellt den Home-Tab Inhalt - optimiert für 24" 16:9"""
        colors = theme_manager.get_colors()
        fonts = self.main_window.fonts
        
        # Haupt-Container mit modernem Styling
        self.container = tk.Frame(self.parent, bg=colors['background_primary'])
        
        # Willkommen-Header - größer und einladender
        welcome_frame = tk.Frame(self.container, bg=colors['background_primary'])
        welcome_frame.pack(fill='x', pady=(40, 50))
        
        # Haupttitel mit BumbleB Branding
        welcome_title = tk.Label(
            welcome_frame,
            text="▣ BumbleB Präsentations-System",
            font=fonts['display'],
            fg=colors['accent_primary'],
            bg=colors['background_primary']
        )
        welcome_title.pack()
        
        # Untertitel mit klarer Beschreibung
        welcome_subtitle = tk.Label(
            welcome_frame,
            text="Interaktive Steuerung für automatisierte Shuttle-Präsentationen",
            font=fonts['subtitle'],
            fg=colors['text_secondary'],
            bg=colors['background_primary']
        )
        welcome_subtitle.pack(pady=(10, 0))
        
        # Kurze Anleitung
        instruction_label = tk.Label(
            welcome_frame,
            text="Wählen Sie eine Option unten, um zu beginnen",
            font=fonts['body'],
            fg=colors['text_tertiary'],
            bg=colors['background_primary']
        )
        instruction_label.pack(pady=(5, 0))
        
        # Feature-Karten Grid (2x2 für bessere Übersicht)
        self.create_feature_grid()
    
    def create_feature_grid(self):
        """Erstellt das 2x2 Grid mit Haupt-Feature-Karten"""
        colors = theme_manager.get_colors()
        
        # Grid-Container mit modernem Styling
        grid_frame = tk.Frame(self.container, bg=colors['background_primary'])
        grid_frame.pack(expand=True, fill='both', padx=60, pady=30)
        
        # Grid-Konfiguration für 2x2 Layout
        for i in range(2):
            grid_frame.grid_columnconfigure(i, weight=1, uniform="col")
            grid_frame.grid_rowconfigure(i, weight=1, uniform="row")
        
        # Haupt-Feature-Definitionen (nur die wichtigsten 4)
        features = [
            {
                'title': 'Demo Starten',
                'icon': '▶',
                'description': 'Automatische BumbleB\nPräsentation starten',
                'action': lambda: self.main_window.switch_tab('demo'),
                'color': colors['accent_primary'],
                'priority': 'high'
            },
            {
                'title': 'Folien Bearbeiten',
                'icon': '✎',
                'description': 'BumbleB Story-Inhalte\nbearbeiten und anpassen',
                'action': lambda: self.main_window.switch_tab('creator'),
                'color': colors['accent_secondary'],
                'priority': 'high'
            },
            {
                'title': 'Manuelle Steuerung',
                'icon': '▦',
                'description': 'Präsentation manuell\nsteuern und navigieren',
                'action': lambda: self.main_window.switch_tab('presentation'),
                'color': colors['accent_primary'],
                'priority': 'medium'
            },
            {
                'title': 'System & Hilfe',
                'icon': '⚙',
                'description': 'Hardware-Status, Einstellungen\nund Bedienungsanleitung',
                'action': self.show_system_menu,
                'color': colors['accent_tertiary'],
                'priority': 'low'
            }
        ]
        
        # Feature-Karten erstellen
        for i, feature in enumerate(features):
            row = i // 2
            col = i % 2
            self.create_feature_card(grid_frame, feature, row, col)
    
    def create_feature_card(self, parent, feature, row, col):
        """Erstellt eine moderne, ansprechende Feature-Karte"""
        colors = theme_manager.get_colors()
        fonts = self.main_window.fonts
        
        # Äußerer Container für Schatten-Effekt
        shadow_frame = tk.Frame(parent, bg=colors['background_primary'])
        shadow_frame.grid(row=row, column=col, padx=25, pady=25, sticky='nsew')
        
        # Apple Silicon Style Karten-Frame
        card_frame = tk.Frame(
            shadow_frame,
            bg=colors['background_secondary'],
            relief='flat',
            bd=0,
            highlightbackground=colors['border_light'],
            highlightthickness=1
        )
        card_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Apple-Style abgerundete Ecken Simulation
        card_frame.configure(relief='flat', bd=0)
        
        # Prioritäts-Indikator (farbiger Balken oben)
        priority_colors = {
            'high': colors['accent_primary'],
            'medium': colors['accent_secondary'], 
            'low': colors['accent_tertiary']
        }
        
        priority_bar = tk.Frame(
            card_frame,
            bg=priority_colors.get(feature.get('priority', 'medium'), colors['accent_primary']),
            height=4
        )
        priority_bar.pack(fill='x')
        
        # Hauptinhalt-Container
        content_frame = tk.Frame(card_frame, bg=colors['background_secondary'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Icon - größer und prominenter
        icon_label = tk.Label(
            content_frame,
            text=feature['icon'],
            font=('Segoe UI Emoji', int(64 * self.main_window.scale_factor)),
            fg=feature['color'],
            bg=colors['background_secondary']
        )
        icon_label.pack(pady=(10, 15))
        
        # Titel - prominenter
        title_label = tk.Label(
            content_frame,
            text=feature['title'],
            font=fonts['title'],
            fg=colors['text_primary'],
            bg=colors['background_secondary']
        )
        title_label.pack(pady=(0, 10))
        
        # Beschreibung - mehrzeilig und besser lesbar
        desc_label = tk.Label(
            content_frame,
            text=feature['description'],
            font=fonts['body'],
            fg=colors['text_secondary'],
            bg=colors['background_secondary'],
            justify='center',
            wraplength=250
        )
        desc_label.pack(pady=(0, 15))
        
        # Apple Silicon Style Action-Button
        action_btn = tk.Button(
            content_frame,
            text="Öffnen",
            font=fonts['button'],
            bg=feature['color'],
            fg=colors['text_on_accent'],
            relief='flat',
            bd=0,
            padx=24,
            pady=12,
            cursor='hand2',
            command=feature['action'],
            activebackground=colors['background_hover'],
            activeforeground=colors['text_primary']
        )
        action_btn.pack(pady=(8, 12))
        
        # Apple-Style Button Hover-Effekt
        def on_btn_enter(e):
            action_btn.configure(bg=colors['background_hover'], fg=colors['text_primary'])
        
        def on_btn_leave(e):
            action_btn.configure(bg=feature['color'], fg=colors['text_on_accent'])
        
        action_btn.bind('<Enter>', on_btn_enter)
        action_btn.bind('<Leave>', on_btn_leave)
        
        # Moderne Hover-Effekte
        def on_enter(e):
            card_frame.configure(
                bg=colors['background_hover'],
                highlightbackground=feature['color'],
                highlightthickness=2
            )
            content_frame.configure(bg=colors['background_hover'])
            icon_label.configure(bg=colors['background_hover'])
            title_label.configure(bg=colors['background_hover'])
            desc_label.configure(bg=colors['background_hover'])
            action_btn.configure(bg=colors['accent_secondary'])
        
        def on_leave(e):
            card_frame.configure(
                bg=colors['background_secondary'],
                highlightbackground=colors['border_light'],
                highlightthickness=1
            )
            content_frame.configure(bg=colors['background_secondary'])
            icon_label.configure(bg=colors['background_secondary'])
            title_label.configure(bg=colors['background_secondary'])
            desc_label.configure(bg=colors['background_secondary'])
            action_btn.configure(bg=feature['color'])
        
        def on_click(e):
            # Klick-Animation
            card_frame.configure(highlightthickness=3)
            card_frame.after(100, lambda: card_frame.configure(highlightthickness=2))
            feature['action']()
        
        # Event-Bindings für alle interaktiven Elemente
        for widget in [card_frame, content_frame, icon_label, title_label, desc_label]:
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
            widget.bind('<Button-1>', on_click)
            widget.configure(cursor='hand2')
    
    def show_hardware_info(self):
        """Zeigt Hardware-Informationen"""
        from tkinter import messagebox
        from models.hardware import hardware_manager
        
        status = hardware_manager.get_status_summary()
        info_text = "Hardware Status:\n\n"
        
        for device, status_val in status.items():
            status_icon = "🟢" if status_val == "connected" else "🔴"
            info_text += f"{status_icon} {device}: {status_val}\n"
        
        messagebox.showinfo("Hardware Status", info_text)
    
    def show_system_info(self):
        """Zeigt System-Informationen"""
        from tkinter import messagebox
        import sys
        import platform
        
        info_text = f"""System Informationen:
        
Python Version: {sys.version.split()[0]}
Plattform: {platform.system()} {platform.release()}
Auflösung: {self.main_window.window_width}x{self.main_window.window_height}
Scale Factor: {self.main_window.scale_factor:.2f}
Theme: {'Dark' if theme_manager.dark_mode else 'Light'} Mode
        """
        
        messagebox.showinfo("System Info", info_text)
    
    def show_system_menu(self):
        """Zeigt das System-Menü mit Hardware-Status und Hilfe"""
        from tkinter import messagebox
        from models.hardware import hardware_manager
        import sys
        import platform
        
        # Hardware-Status sammeln
        status = hardware_manager.get_status_summary()
        hw_info = "Hardware Status:\n"
        for device, status_val in status.items():
            status_icon = "🟢" if status_val == "connected" else "🔴"
            hw_info += f"{status_icon} {device}: {status_val}\n"
        
        # System-Info sammeln
        sys_info = f"""
System Informationen:
Python: {sys.version.split()[0]}
Plattform: {platform.system()} {platform.release()}
Auflösung: {self.main_window.window_width}x{self.main_window.window_height}

BumbleB Präsentations-System V4
© 2024 Bertrandt AG

Bedienung:
🏠 START: Hauptmenü
▶️ DEMO: Automatische BumbleB-Präsentation
✏️ BEARBEITEN: Folien-Inhalte anpassen
📊 PRÄSENTATION: Manuelle Steuerung

Tastenkürzel:
F11 - Vollbild ein/aus
ESC - Vollbild verlassen
        """
        
        full_text = hw_info + sys_info
        messagebox.showinfo("System & Hilfe", full_text)
    
    def show_help(self):
        """Zeigt Hilfe-Informationen"""
        self.show_system_menu()
    
    def show(self):
        """Zeigt den Tab"""
        if not self.visible:
            self.container.pack(fill='both', expand=True)
            self.visible = True
            logger.debug("Home-Tab angezeigt")
    
    def hide(self):
        """Versteckt den Tab"""
        if self.visible:
            self.container.pack_forget()
            self.visible = False
            logger.debug("Home-Tab versteckt")