#!/usr/bin/env python3
"""
Main Window für Dynamic Messe Stand V4
Haupt-GUI-Fenster mit responsivem Design
"""

import tkinter as tk
from tkinter import ttk
import sys
import subprocess
from core.config import config
from core.theme import theme_manager
from core.logger import logger
from ui.components.header import HeaderComponent
from ui.components.status_panel import StatusPanelComponent
from ui.components.footer import FooterComponent
from ui.tabs.home_tab import HomeTab
from ui.tabs.demo_tab import DemoTab
from ui.tabs.creator_tab import CreatorTab
from ui.tabs.presentation_tab import PresentationTab

class MainWindow:
    """Haupt-GUI-Fenster"""
    
    def __init__(self, esp32_port=None):
        logger.info("🚀 Starte Dynamic Messe Stand V4...")
        
        # Tkinter Root
        self.root = tk.Tk()
        self.root.title(config.gui['title'])
        
        # Basis-Variablen
        self.esp32_port = esp32_port
        self.fullscreen = False
        self.current_tab = "home"
        
        # Setup
        self.setup_window()
        self.setup_responsive_design()
        self.setup_styles()
        self.setup_gui_components()
        self.setup_tabs()
        
        # Initialer Tab
        self.switch_tab("home")
        
        logger.info("✅ Dynamic Messe Stand V4 erfolgreich initialisiert!")
    
    def setup_window(self):
        """Konfiguriert das Hauptfenster für 24" RTC Monitor"""
        # Hauptmonitor ermitteln (primärer Monitor)
        self.detect_primary_monitor()
        
        # Für 24" RTC Monitor optimiert
        self.window_width = self.primary_width
        self.window_height = self.primary_height
        
        logger.info(f"Hauptmonitor erkannt: {self.window_width}x{self.window_height} bei ({self.primary_x}, {self.primary_y})")
        
        # Fenster explizit auf Hauptmonitor positionieren
        self.root.geometry(f"{self.window_width}x{self.window_height}+{self.primary_x}+{self.primary_y}")
        self.root.minsize(config.gui['min_width'], config.gui['min_height'])
        
        # Vollbild-Bindings
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Escape>', self.exit_fullscreen)
        
        # Sofort in Vollbild auf Hauptmonitor
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)  # Immer im Vordergrund
        self.fullscreen = True
        
        # Fenster auf Hauptmonitor forcieren
        self.root.wm_attributes('-zoomed', True)  # Linux maximieren
        self.root.focus_force()    # Fokus erzwingen
        self.root.lift()           # Fenster nach vorne bringen
        
        # Sicherstellen, dass Fenster auf Hauptmonitor bleibt
        self.root.after(100, self.ensure_primary_monitor)
        
        # Theme anwenden
        colors = theme_manager.get_colors()
        self.root.configure(bg=colors['background_primary'])
    
    def detect_primary_monitor(self):
        """Erkennt den primären Monitor (Hauptbildschirm)"""
        try:
            # Tkinter-Methode für primären Monitor
            self.root.update_idletasks()
            
            # Gesamte Bildschirmgröße
            total_width = self.root.winfo_screenwidth()
            total_height = self.root.winfo_screenheight()
            
            # Primärer Monitor ist normalerweise bei (0,0)
            self.primary_x = 0
            self.primary_y = 0
            self.primary_width = total_width
            self.primary_height = total_height
            
            # Versuche Multi-Monitor Setup zu erkennen
            try:
                import subprocess
                result = subprocess.run(['xrandr'], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if ' connected primary ' in line:
                            # Primärer Monitor gefunden
                            parts = line.split()
                            for part in parts:
                                if 'x' in part and '+' in part:
                                    # Format: 1920x1080+0+0
                                    resolution_pos = part.split('+')
                                    if len(resolution_pos) >= 3:
                                        resolution = resolution_pos[0]
                                        self.primary_x = int(resolution_pos[1])
                                        self.primary_y = int(resolution_pos[2])
                                        
                                        if 'x' in resolution:
                                            w, h = resolution.split('x')
                                            self.primary_width = int(w)
                                            self.primary_height = int(h)
                                    break
                            break
            except:
                pass  # Fallback auf Standard-Werte
            
            logger.info(f"Primärer Monitor: {self.primary_width}x{self.primary_height} bei ({self.primary_x}, {self.primary_y})")
            
        except Exception as e:
            logger.warning(f"Monitor-Erkennung fehlgeschlagen: {e}")
            # Fallback-Werte
            self.primary_x = 0
            self.primary_y = 0
            self.primary_width = 1920
            self.primary_height = 1080
    
    def ensure_primary_monitor(self):
        """Stellt sicher, dass das Fenster auf dem Hauptmonitor bleibt"""
        try:
            # Fenster-Position prüfen und korrigieren
            current_x = self.root.winfo_x()
            current_y = self.root.winfo_y()
            
            # Falls Fenster nicht auf Hauptmonitor, zurück bewegen
            if current_x != self.primary_x or current_y != self.primary_y:
                self.root.geometry(f"{self.primary_width}x{self.primary_height}+{self.primary_x}+{self.primary_y}")
                logger.info(f"Fenster auf Hauptmonitor zurück bewegt: ({self.primary_x}, {self.primary_y})")
            
        except Exception as e:
            logger.warning(f"Monitor-Korrektur fehlgeschlagen: {e}")
    
    def setup_responsive_design(self):
        """Konfiguriert responsive Design-Elemente"""
        # Scale Factor für responsive Design
        self.scale_factor = min(self.window_width, self.window_height) / config.design['scale_factor_base']
        
        # Responsive Schriftarten
        self.fonts = theme_manager.get_fonts(self.window_width, self.window_height)
        
        logger.debug(f"Responsive Design: {self.window_width}x{self.window_height}, Scale: {self.scale_factor:.2f}")
    
    def setup_styles(self):
        """Konfiguriert Apple Silicon + Bertrandt Styles"""
        self.style = ttk.Style()
        colors = theme_manager.get_colors()
        
        # Apple-inspirierte Basis-Styles
        self.style.configure('Main.TFrame', 
                           background=colors['background_primary'],
                           relief='flat',
                           borderwidth=0)
        
        self.style.configure('Card.TFrame', 
                           background=colors['background_secondary'],
                           relief='flat',
                           borderwidth=1,
                           bordercolor=colors['border_light'])
        
        self.style.configure('Sidebar.TFrame',
                           background=colors['background_tertiary'],
                           relief='flat',
                           borderwidth=0)
        
        # Apple-Style Button-Styles
        self.style.configure('Primary.TButton',
                           background=colors['accent_primary'],
                           foreground=colors['text_on_accent'],
                           font=self.fonts['button'],
                           relief='flat',
                           borderwidth=0,
                           focuscolor='none')
        
        self.style.configure('Secondary.TButton',
                           background=colors['accent_secondary'],
                           foreground=colors['text_on_accent'],
                           font=self.fonts['button'],
                           relief='flat',
                           borderwidth=0,
                           focuscolor='none')
        
        # Apple-Style Label-Styles
        self.style.configure('Title.TLabel',
                           background=colors['background_primary'],
                           foreground=colors['text_primary'],
                           font=self.fonts['title'])
        
        self.style.configure('Body.TLabel',
                           background=colors['background_primary'],
                           foreground=colors['text_primary'],
                           font=self.fonts['body'])
        
        self.style.configure('Caption.TLabel',
                           background=colors['background_primary'],
                           foreground=colors['text_secondary'],
                           font=self.fonts['caption'])
    
    def setup_gui_components(self):
        """Erstellt die Haupt-GUI-Komponenten"""
        # Haupt-Container
        self.main_container = ttk.Frame(self.root, style='Main.TFrame')
        self.main_container.pack(fill='both', expand=True)
        
        # Header
        self.header = HeaderComponent(self.main_container, self)
        self.header.pack(fill='x', pady=(0, 10))
        
        # Content-Bereich
        self.content_frame = ttk.Frame(self.main_container, style='Main.TFrame')
        self.content_frame.pack(fill='both', expand=True, padx=20)
        
        # Content-Layout: Status Panel (links) + Tab Content (rechts)
        self.content_frame.grid_columnconfigure(1, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Status Panel (links)
        self.status_panel = StatusPanelComponent(self.content_frame, self)
        self.status_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 20))
        
        # Tab Content Area (rechts)
        self.tab_content_frame = ttk.Frame(self.content_frame, style='Main.TFrame')
        self.tab_content_frame.grid(row=0, column=1, sticky='nsew')
        
        # Footer
        self.footer = FooterComponent(self.main_container, self)
        self.footer.pack(fill='x', pady=(10, 0))
    
    def setup_tabs(self):
        """Initialisiert alle Tab-Komponenten"""
        self.tabs = {
            'home': HomeTab(self.tab_content_frame, self),
            'demo': DemoTab(self.tab_content_frame, self),
            'creator': CreatorTab(self.tab_content_frame, self),
            'presentation': PresentationTab(self.tab_content_frame, self)
        }
        
        # Alle Tabs initial verstecken
        for tab in self.tabs.values():
            tab.hide()
    
    def switch_tab(self, tab_name):
        """Wechselt zwischen Tabs"""
        if tab_name not in self.tabs:
            logger.error(f"Unbekannter Tab: {tab_name}")
            return False
        
        # Aktuellen Tab verstecken
        if self.current_tab in self.tabs:
            self.tabs[self.current_tab].hide()
        
        # Neuen Tab anzeigen
        self.tabs[tab_name].show()
        self.current_tab = tab_name
        
        # Header-Navigation aktualisieren
        self.header.update_active_tab(tab_name)
        
        logger.debug(f"Tab gewechselt: {tab_name}")
        return True
    
    def toggle_fullscreen(self, event=None):
        """Wechselt zwischen Vollbild und Fenster-Modus"""
        self.fullscreen = not self.fullscreen
        self.root.attributes('-fullscreen', self.fullscreen)
        logger.debug(f"Vollbild: {'aktiviert' if self.fullscreen else 'deaktiviert'}")
    
    def exit_fullscreen(self, event=None):
        """Verlässt den Vollbild-Modus (aber bleibt auf Hauptmonitor)"""
        if self.fullscreen:
            self.fullscreen = False
            self.root.attributes('-fullscreen', False)
            self.root.attributes('-topmost', False)  # Topmost deaktivieren
            
            # Fenster auf Hauptmonitor in normaler Größe
            self.root.geometry(f"{self.primary_width}x{self.primary_height}+{self.primary_x}+{self.primary_y}")
            logger.debug("Vollbild deaktiviert - bleibt auf Hauptmonitor")
    
    def restart_application(self):
        """Startet die Anwendung neu"""
        logger.info("Anwendung wird neu gestartet...")
        subprocess.Popen([sys.executable] + sys.argv)
        self.quit_application()
    
    def quit_application(self):
        """Beendet die Anwendung"""
        logger.info("Anwendung wird beendet...")
        
        # Hardware-Verbindungen trennen
        from models.hardware import hardware_manager
        hardware_manager.disconnect_all()
        
        # Demo stoppen
        from services.demo import demo_service
        demo_service.stop_demo()
        
        # GUI schließen
        self.root.quit()
        sys.exit(0)
    
    def run(self):
        """Startet die GUI-Hauptschleife"""
        try:
            logger.info("GUI-Hauptschleife gestartet")
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Anwendung durch Benutzer unterbrochen")
            self.quit_application()
        except Exception as e:
            logger.error(f"Unerwarteter Fehler in GUI-Hauptschleife: {e}")
            self.quit_application()