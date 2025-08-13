#!/usr/bin/env python3
"""
Footer Component für Dynamic Messe Stand V4
Minimal Footer mit wichtigen Informationen
"""

import tkinter as tk
from tkinter import ttk
from core.theme import theme_manager

class FooterComponent(ttk.Frame):
    """Minimaler Footer"""
    
    def __init__(self, parent, main_window):
        super().__init__(parent, style='Secondary.TFrame')
        self.main_window = main_window
        
        self.setup_footer()
    
    def setup_footer(self):
        """Erstellt den Footer-Bereich"""
        colors = theme_manager.get_colors()
        fonts = self.main_window.fonts
        
        # Footer-Höhe
        footer_height = 20
        self.configure(height=footer_height)
        
        # Copyright-Text
        copyright_label = tk.Label(
            self,
            text="© 2024 Bertrandt AG - Dynamic Messe Stand V4",
            font=fonts['caption'],
            fg=colors['text_tertiary'],
            bg=colors['background_secondary']
        )
        copyright_label.pack(side='left', padx=20)
        
        # Version-Info
        version_label = tk.Label(
            self,
            text="v4.0.0",
            font=fonts['caption'],
            fg=colors['text_tertiary'],
            bg=colors['background_secondary']
        )
        version_label.pack(side='right', padx=20)