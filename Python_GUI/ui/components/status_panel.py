#!/usr/bin/env python3
"""
Status Panel Component für Dynamic Messe Stand V4
Hardware-Status und System-Informationen
"""

import tkinter as tk
from tkinter import ttk
from core.theme import theme_manager
from core.logger import logger
from models.hardware import hardware_manager
from services.demo import demo_service

class StatusPanelComponent(ttk.Frame):
    """Status-Panel für Hardware und System-Informationen"""
    
    def __init__(self, parent, main_window):
        super().__init__(parent, style='Card.TFrame')
        self.main_window = main_window
        
        self.setup_status_panel()
        self.start_status_updates()
    
    def setup_status_panel(self):
        """Erstellt das Status-Panel"""
        colors = theme_manager.get_colors()
        fonts = self.main_window.fonts
        
        # Panel-Größe
        panel_width = int(300 * self.main_window.scale_factor)
        self.configure(width=panel_width)
        
        # Titel
        title_label = tk.Label(
            self,
            text="📊 System Status",
            font=fonts['subtitle'],
            fg=colors['text_primary'],
            bg=colors['background_tertiary']
        )
        title_label.pack(fill='x', padx=15, pady=(15, 10))
        
        # Hardware-Status Sektion
        self.create_hardware_section()
        
        # Demo-Status Sektion
        self.create_demo_section()
        
        # System-Info Sektion
        self.create_system_section()
    
    def create_hardware_section(self):
        """Erstellt die Hardware-Status Sektion"""
        colors = theme_manager.get_colors()
        fonts = self.main_window.fonts
        
        # Sektion-Header
        hw_header = tk.Label(
            self,
            text="🔌 Hardware",
            font=fonts['label'],
            fg=colors['text_primary'],
            bg=colors['background_tertiary']
        )
        hw_header.pack(fill='x', padx=15, pady=(10, 5))
        
        # Hardware-Status Container
        self.hw_frame = tk.Frame(self, bg=colors['background_tertiary'])
        self.hw_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        # Status-Labels für Hardware-Geräte
        self.hw_status_labels = {}
        
        hardware_devices = [
            ('esp32_1', 'ESP32-1'),
            ('esp32_2', 'ESP32-2'),
            ('esp32_3', 'ESP32-3'),
            ('giga', 'Arduino GIGA')
        ]
        
        for device_id, device_name in hardware_devices:
            status_frame = tk.Frame(self.hw_frame, bg=colors['background_tertiary'])
            status_frame.pack(fill='x', pady=2)
            
            # Gerätename
            name_label = tk.Label(
                status_frame,
                text=device_name,
                font=fonts['caption'],
                fg=colors['text_secondary'],
                bg=colors['background_tertiary']
            )
            name_label.pack(side='left')
            
            # Status-Indikator
            status_label = tk.Label(
                status_frame,
                text="🔴 Offline",
                font=fonts['caption'],
                fg=colors['text_tertiary'],
                bg=colors['background_tertiary']
            )
            status_label.pack(side='right')
            
            self.hw_status_labels[device_id] = status_label
    
    def create_demo_section(self):
        """Erstellt die Demo-Status Sektion"""
        colors = theme_manager.get_colors()
        fonts = self.main_window.fonts
        
        # Sektion-Header
        demo_header = tk.Label(
            self,
            text="▶️ Demo Status",
            font=fonts['label'],
            fg=colors['text_primary'],
            bg=colors['background_tertiary']
        )
        demo_header.pack(fill='x', padx=15, pady=(10, 5))
        
        # Demo-Status Container
        self.demo_frame = tk.Frame(self, bg=colors['background_tertiary'])
        self.demo_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        # Demo-Status
        self.demo_status_label = tk.Label(
            self.demo_frame,
            text="⏹️ Gestoppt",
            font=fonts['caption'],
            fg=colors['text_secondary'],
            bg=colors['background_tertiary']
        )
        self.demo_status_label.pack(fill='x')
        
        # Aktuelle Slide
        self.current_slide_label = tk.Label(
            self.demo_frame,
            text="Slide: -",
            font=fonts['caption'],
            fg=colors['text_tertiary'],
            bg=colors['background_tertiary']
        )
        self.current_slide_label.pack(fill='x')
        
        # Demo-Dauer
        self.demo_duration_label = tk.Label(
            self.demo_frame,
            text="Dauer: 5s",
            font=fonts['caption'],
            fg=colors['text_tertiary'],
            bg=colors['background_tertiary']
        )
        self.demo_duration_label.pack(fill='x')
    
    def create_system_section(self):
        """Erstellt die System-Info Sektion"""
        colors = theme_manager.get_colors()
        fonts = self.main_window.fonts
        
        # Sektion-Header
        sys_header = tk.Label(
            self,
            text="💻 System",
            font=fonts['label'],
            fg=colors['text_primary'],
            bg=colors['background_tertiary']
        )
        sys_header.pack(fill='x', padx=15, pady=(10, 5))
        
        # System-Info Container
        self.sys_frame = tk.Frame(self, bg=colors['background_tertiary'])
        self.sys_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # Aktuelle Zeit
        self.time_label = tk.Label(
            self.sys_frame,
            text="Zeit: --:--",
            font=fonts['caption'],
            fg=colors['text_tertiary'],
            bg=colors['background_tertiary']
        )
        self.time_label.pack(fill='x')
        
        # Theme-Info
        theme_text = "Dark Mode" if theme_manager.dark_mode else "Light Mode"
        self.theme_label = tk.Label(
            self.sys_frame,
            text=f"Theme: {theme_text}",
            font=fonts['caption'],
            fg=colors['text_tertiary'],
            bg=colors['background_tertiary']
        )
        self.theme_label.pack(fill='x')
        
        # Auflösung
        resolution_text = f"{self.main_window.window_width}x{self.main_window.window_height}"
        self.resolution_label = tk.Label(
            self.sys_frame,
            text=f"Auflösung: {resolution_text}",
            font=fonts['caption'],
            fg=colors['text_tertiary'],
            bg=colors['background_tertiary']
        )
        self.resolution_label.pack(fill='x')
    
    def start_status_updates(self):
        """Startet regelmäßige Status-Updates"""
        self.update_status()
        # Update alle 2 Sekunden
        self.after(2000, self.start_status_updates)
    
    def update_status(self):
        """Aktualisiert alle Status-Informationen"""
        self.update_hardware_status()
        self.update_demo_status()
        self.update_system_info()
    
    def update_hardware_status(self):
        """Aktualisiert Hardware-Status"""
        try:
            status_summary = hardware_manager.get_status_summary()
            
            for device_id, status_label in self.hw_status_labels.items():
                status = status_summary.get(device_id, "disconnected")
                
                if status == "connected":
                    status_text = "🟢 Online"
                elif status == "error":
                    status_text = "🟡 Fehler"
                else:
                    status_text = "🔴 Offline"
                
                status_label.configure(text=status_text)
                
        except Exception as e:
            logger.error(f"Fehler beim Hardware-Status Update: {e}")
    
    def update_demo_status(self):
        """Aktualisiert Demo-Status"""
        try:
            demo_status = demo_service.get_status()
            
            # Demo-Status
            if demo_status['running']:
                status_text = "▶️ Läuft"
            else:
                status_text = "⏹️ Gestoppt"
            
            self.demo_status_label.configure(text=status_text)
            
            # Aktuelle Slide
            slide_text = f"Slide: {demo_status['current_slide']}/{demo_status['total_slides']}"
            self.current_slide_label.configure(text=slide_text)
            
            # Demo-Dauer
            duration_text = f"Dauer: {demo_status['slide_duration']}s"
            self.demo_duration_label.configure(text=duration_text)
            
        except Exception as e:
            logger.error(f"Fehler beim Demo-Status Update: {e}")
    
    def update_system_info(self):
        """Aktualisiert System-Informationen"""
        try:
            import datetime
            
            # Aktuelle Zeit
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            self.time_label.configure(text=f"Zeit: {current_time}")
            
        except Exception as e:
            logger.error(f"Fehler beim System-Info Update: {e}")