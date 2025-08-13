#!/usr/bin/env python3
"""
Presentation Tab für Dynamic Messe Stand V4
Manuelle Präsentations-Steuerung
"""

import tkinter as tk
from tkinter import ttk
from core.theme import theme_manager
from core.logger import logger
from models.content import content_manager
from models.hardware import hardware_manager

class PresentationTab:
    """Presentation-Tab für manuelle Steuerung"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.visible = False
        self.current_slide = 1
        
        self.create_presentation_content()
    
    def create_presentation_content(self):
        """Erstellt den Presentation-Tab Inhalt"""
        colors = theme_manager.get_colors()
        fonts = self.main_window.fonts
        
        # Haupt-Container
        self.container = ttk.Frame(self.parent, style='Main.TFrame')
        
        # Header
        header_frame = ttk.Frame(self.container, style='Main.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = tk.Label(
            header_frame,
            text="📊 Präsentation",
            font=fonts['display'],
            fg=colors['text_primary'],
            bg=colors['background_primary']
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="Manuelle Präsentations-Steuerung",
            font=fonts['subtitle'],
            fg=colors['text_secondary'],
            bg=colors['background_primary']
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Content-Bereich
        content_frame = ttk.Frame(self.container, style='Main.TFrame')
        content_frame.pack(fill='both', expand=True, padx=40)
        
        # Layout: Slide-Grid (links) + Kontrollen (rechts)
        content_frame.grid_columnconfigure(0, weight=2)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Slide-Grid
        self.create_slide_grid(content_frame)
        
        # Kontroll-Panel
        self.create_control_panel(content_frame)
    
    def create_slide_grid(self, parent):
        """Erstellt das Slide-Grid"""
        colors = theme_manager.get_colors()
        fonts = self.main_window.fonts
        
        # Grid Frame
        grid_frame = ttk.Frame(parent, style='Card.TFrame')
        grid_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 20))
        
        # Titel
        grid_title = tk.Label(
            grid_frame,
            text="🎯 Slide-Auswahl",
            font=fonts['title'],
            fg=colors['text_primary'],
            bg=colors['background_tertiary']
        )
        grid_title.pack(pady=(15, 10))
        
        # Scrollable Frame für Slides
        canvas = tk.Canvas(
            grid_frame,
            bg=colors['background_tertiary'],
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(grid_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Card.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=15, pady=(0, 15))
        scrollbar.pack(side="right", fill="y", pady=(0, 15))
        
        # Slide-Buttons erstellen
        self.create_slide_buttons(scrollable_frame)
    
    def create_slide_buttons(self, parent):
        """Erstellt die Slide-Buttons"""
        colors = theme_manager.get_colors()
        fonts = self.main_window.fonts
        
        slides = content_manager.get_all_slides()
        
        # Grid-Layout: 4 Spalten
        cols = 4
        
        for i, (slide_id, slide) in enumerate(slides.items()):
            row = i // cols
            col = i % cols
            
            # Button-Frame
            btn_frame = tk.Frame(parent, bg=colors['background_tertiary'])
            btn_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            
            # Slide-Button
            slide_btn = tk.Button(
                btn_frame,
                text=f"Slide {slide_id}\n{slide.title[:20]}...",
                font=fonts['caption'],
                bg=colors['background_secondary'],
                fg=colors['text_primary'],
                width=15,
                height=4,
                command=lambda sid=slide_id: self.goto_slide(sid)
            )
            slide_btn.pack(fill='both', expand=True)
            
            # Hover-Effekte
            def on_enter(e, btn=slide_btn):
                btn.configure(bg=colors['background_hover'])
            
            def on_leave(e, btn=slide_btn):
                if slide_id != self.current_slide:
                    btn.configure(bg=colors['background_secondary'])
            
            slide_btn.bind('<Enter>', on_enter)
            slide_btn.bind('<Leave>', on_leave)
            
            # Aktuelle Slide markieren
            if slide_id == self.current_slide:
                slide_btn.configure(bg=colors['accent_primary'], fg='white')
        
        # Grid-Spalten konfigurieren
        for i in range(cols):
            parent.grid_columnconfigure(i, weight=1)
    
    def create_control_panel(self, parent):
        """Erstellt das Kontroll-Panel"""
        colors = theme_manager.get_colors()
        fonts = self.main_window.fonts
        
        # Control Frame
        control_frame = ttk.Frame(parent, style='Card.TFrame')
        control_frame.grid(row=0, column=1, sticky='nsew')
        
        # Titel
        control_title = tk.Label(
            control_frame,
            text="🎮 Steuerung",
            font=fonts['title'],
            fg=colors['text_primary'],
            bg=colors['background_tertiary']
        )
        control_title.pack(pady=(15, 10))
        
        # Aktuelle Slide Info
        self.current_info = tk.Label(
            control_frame,
            text=f"Aktuelle Slide: {self.current_slide}",
            font=fonts['body'],
            fg=colors['text_primary'],
            bg=colors['background_tertiary']
        )
        self.current_info.pack(pady=(0, 20))
        
        # Navigation Buttons
        nav_frame = tk.Frame(control_frame, bg=colors['background_tertiary'])
        nav_frame.pack(pady=(0, 20))
        
        # Vorherige Slide
        prev_btn = tk.Button(
            nav_frame,
            text="⏮️ Vorherige",
            font=fonts['button'],
            bg=colors['background_hover'],
            fg=colors['text_primary'],
            padx=15,
            pady=10,
            command=self.previous_slide
        )
        prev_btn.pack(fill='x', pady=(0, 5))
        
        # Nächste Slide
        next_btn = tk.Button(
            nav_frame,
            text="⏭️ Nächste",
            font=fonts['button'],
            bg=colors['background_hover'],
            fg=colors['text_primary'],
            padx=15,
            pady=10,
            command=self.next_slide
        )
        next_btn.pack(fill='x', pady=(0, 5))
        
        # Hardware-Steuerung
        hw_frame = tk.Frame(control_frame, bg=colors['background_tertiary'])
        hw_frame.pack(pady=(20, 0), fill='x', padx=15)
        
        hw_title = tk.Label(
            hw_frame,
            text="🔌 Hardware",
            font=fonts['subtitle'],
            fg=colors['text_primary'],
            bg=colors['background_tertiary']
        )
        hw_title.pack(pady=(0, 10))
        
        # Signal senden Button
        signal_btn = tk.Button(
            hw_frame,
            text="📡 Signal senden",
            font=fonts['button'],
            bg=colors['accent_primary'],
            fg='white',
            padx=15,
            pady=8,
            command=self.send_hardware_signal
        )
        signal_btn.pack(fill='x', pady=(0, 10))
        
        # Hardware-Status
        self.hw_status_label = tk.Label(
            hw_frame,
            text="Status: Prüfe...",
            font=fonts['caption'],
            fg=colors['text_secondary'],
            bg=colors['background_tertiary']
        )
        self.hw_status_label.pack()
    
    def goto_slide(self, slide_id):
        """Springt zu einer spezifischen Slide"""
        self.current_slide = slide_id
        self.current_info.configure(text=f"Aktuelle Slide: {slide_id}")
        self.send_hardware_signal()
        
        # Slide-Buttons aktualisieren
        self.refresh_slide_buttons()
        
        logger.info(f"Zu Slide {slide_id} gewechselt")
    
    def previous_slide(self):
        """Geht zur vorherigen Slide"""
        slides = list(content_manager.get_all_slides().keys())
        if slides:
            current_index = slides.index(self.current_slide) if self.current_slide in slides else 0
            prev_index = (current_index - 1) % len(slides)
            self.goto_slide(slides[prev_index])
    
    def next_slide(self):
        """Geht zur nächsten Slide"""
        slides = list(content_manager.get_all_slides().keys())
        if slides:
            current_index = slides.index(self.current_slide) if self.current_slide in slides else 0
            next_index = (current_index + 1) % len(slides)
            self.goto_slide(slides[next_index])
    
    def send_hardware_signal(self):
        """Sendet Signal an Hardware"""
        try:
            signal_id = f"page_{self.current_slide}"
            
            # Signal an alle ESP32s senden
            sent_count = 0
            for name, connection in hardware_manager.connections.items():
                if name.startswith('esp32_') and connection.status == "connected":
                    if connection.send_signal(signal_id):
                        sent_count += 1
            
            # UDP-Signal über GIGA senden
            giga = hardware_manager.get_connection('giga')
            if giga and giga.status == "connected":
                giga.send_udp_signal("192.168.1.100", signal_id, 1)
                sent_count += 1
            
            if sent_count > 0:
                self.hw_status_label.configure(text=f"Signal gesendet: {signal_id}")
                logger.info(f"Hardware-Signal gesendet: {signal_id}")
            else:
                self.hw_status_label.configure(text="Keine Hardware verbunden")
                
        except Exception as e:
            self.hw_status_label.configure(text="Fehler beim Senden")
            logger.error(f"Fehler beim Hardware-Signal: {e}")
    
    def refresh_slide_buttons(self):
        """Aktualisiert die Slide-Button-Anzeige"""
        # Einfache Implementierung - in einer echten App würde man die Buttons direkt aktualisieren
        pass
    
    def show(self):
        """Zeigt den Tab"""
        if not self.visible:
            self.container.pack(fill='both', expand=True)
            self.visible = True
            logger.debug("Presentation-Tab angezeigt")
    
    def hide(self):
        """Versteckt den Tab"""
        if self.visible:
            self.container.pack_forget()
            self.visible = False
            logger.debug("Presentation-Tab versteckt")