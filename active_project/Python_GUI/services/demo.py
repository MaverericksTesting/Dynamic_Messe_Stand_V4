# services/demo.py
"""
Demo-Service für automatische Präsentation
"""
import time
from typing import Optional
from core.config import config
from core.logger import logger
from core.bus import bus
from models.state import app_state

class DemoService:
    """Service für automatische Demo-Präsentation"""
    
    def __init__(self):
        self.is_running = False
        self.current_slide = 1
        self.timer_id: Optional[str] = None
        
        # Event-Handler registrieren
        bus.subscribe("demo:start", self.start_demo)
        bus.subscribe("demo:stop", self.stop_demo)
        bus.subscribe("demo:next_slide", self._next_slide)
    
    def start_demo(self):
        """Starte automatische Demo"""
        if self.is_running:
            logger.warning("Demo läuft bereits")
            return
        
        self.is_running = True
        self.current_slide = 1
        app_state.demo_active = True
        app_state.demo_current_slide = self.current_slide
        
        logger.info("🤖 Auto-Demo gestartet")
        bus.publish("demo:started")
        
        # Erste Folie anzeigen
        self._show_current_slide()
        
        # Timer für nächste Folie
        self._schedule_next_slide()
    
    def stop_demo(self):
        """Stoppe automatische Demo"""
        if not self.is_running:
            return
        
        self.is_running = False
        app_state.demo_active = False
        
        # Timer stoppen
        if self.timer_id:
            bus.publish("ui:cancel_timer", timer_id=self.timer_id)
            self.timer_id = None
        
        logger.info("⏹️ Auto-Demo gestoppt")
        bus.publish("demo:stopped")
    
    def _next_slide(self):
        """Wechsle zur nächsten Folie"""
        if not self.is_running:
            return
        
        # Nächste Folie
        self.current_slide += 1
        if self.current_slide > len(config.SLIDES):
            self.current_slide = 1  # Zurück zur ersten Folie
        
        app_state.demo_current_slide = self.current_slide
        
        # Folie anzeigen
        self._show_current_slide()
        
        # Nächsten Timer planen
        self._schedule_next_slide()
    
    def _show_current_slide(self):
        """Zeige aktuelle Folie"""
        logger.debug(f"🎬 Demo zeigt Folie {self.current_slide}")
        
        # Signal an UI senden
        bus.publish("slide:change", slide_id=self.current_slide, source="demo")
        
        # Simuliere Hardware-Signal im Dev-Mode
        if app_state.dev_mode:
            bus.publish("hardware:signal_received", 
                       device_name="demo", 
                       signal_id=self.current_slide)
    
    def _schedule_next_slide(self):
        """Plane nächste Folie"""
        if not self.is_running:
            return
        
        # Timer für nächste Folie setzen
        self.timer_id = f"demo_timer_{time.time()}"
        bus.publish("ui:schedule_timer", 
                   timer_id=self.timer_id,
                   delay=config.AUTO_DEMO_INTERVAL,
                   callback=lambda: bus.publish("demo:next_slide"))
    
    def jump_to_slide(self, slide_id: int):
        """Springe zu bestimmter Folie (während Demo läuft)"""
        if not self.is_running:
            return
        
        if slide_id < 1 or slide_id > len(config.SLIDES):
            logger.warning(f"Ungültige Folien-ID: {slide_id}")
            return
        
        self.current_slide = slide_id
        app_state.demo_current_slide = slide_id
        
        # Timer neu starten
        if self.timer_id:
            bus.publish("ui:cancel_timer", timer_id=self.timer_id)
        
        self._show_current_slide()
        self._schedule_next_slide()
        
        logger.info(f"🎯 Demo springt zu Folie {slide_id}")
    
    def get_status(self) -> dict:
        """Demo-Status abrufen"""
        return {
            "is_running": self.is_running,
            "current_slide": self.current_slide,
            "total_slides": len(config.SLIDES),
            "interval_ms": config.AUTO_DEMO_INTERVAL
        }