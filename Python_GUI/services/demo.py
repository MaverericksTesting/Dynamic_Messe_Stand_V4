#!/usr/bin/env python3
"""
Demo Service für Dynamic Messe Stand V4
Automatische Präsentations-Steuerung
"""

import threading
import time
from core.logger import logger
from core.config import config
from models.content import content_manager
from models.hardware import hardware_manager

class DemoService:
    """Service für automatische Demo-Präsentationen"""
    
    def __init__(self):
        self.running = False
        self.demo_thread = None
        self.current_slide = 1
        self.slide_duration = config.content['demo_slide_duration']
        self.total_slides = 10  # Standard
        self.loop_demo = True
        self.callbacks = []
    
    def add_callback(self, callback):
        """Fügt Callback für Slide-Wechsel hinzu"""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback):
        """Entfernt Callback"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def _notify_callbacks(self, slide_id):
        """Benachrichtigt alle Callbacks über Slide-Wechsel"""
        for callback in self.callbacks:
            try:
                callback(slide_id)
            except Exception as e:
                logger.error(f"Fehler in Demo-Callback: {e}")
    
    def start_demo(self, start_slide=1, duration=None):
        """Startet die automatische Demo"""
        if self.running:
            logger.warning("Demo läuft bereits")
            return False
        
        self.current_slide = start_slide
        if duration:
            self.slide_duration = duration
        
        self.total_slides = content_manager.get_slide_count()
        if self.total_slides == 0:
            logger.error("Keine Slides für Demo verfügbar")
            return False
        
        self.running = True
        self.demo_thread = threading.Thread(target=self._demo_loop, daemon=True)
        self.demo_thread.start()
        
        logger.info(f"Demo gestartet - Slide {start_slide}, {self.slide_duration}s pro Slide")
        return True
    
    def stop_demo(self):
        """Stoppt die automatische Demo"""
        if not self.running:
            return False
        
        self.running = False
        if self.demo_thread and self.demo_thread.is_alive():
            self.demo_thread.join(timeout=2)
        
        logger.info("Demo gestoppt")
        return True
    
    def pause_demo(self):
        """Pausiert die Demo (implementiert als Stop)"""
        return self.stop_demo()
    
    def next_slide(self):
        """Wechselt zur nächsten Slide"""
        if self.total_slides == 0:
            return False
        
        self.current_slide += 1
        if self.current_slide > self.total_slides:
            if self.loop_demo:
                self.current_slide = 1
            else:
                self.stop_demo()
                return False
        
        self._send_slide_signal(self.current_slide)
        self._notify_callbacks(self.current_slide)
        return True
    
    def previous_slide(self):
        """Wechselt zur vorherigen Slide"""
        if self.total_slides == 0:
            return False
        
        self.current_slide -= 1
        if self.current_slide < 1:
            self.current_slide = self.total_slides if self.loop_demo else 1
        
        self._send_slide_signal(self.current_slide)
        self._notify_callbacks(self.current_slide)
        return True
    
    def goto_slide(self, slide_id):
        """Springt zu einer spezifischen Slide"""
        if slide_id < 1 or slide_id > self.total_slides:
            return False
        
        self.current_slide = slide_id
        self._send_slide_signal(self.current_slide)
        self._notify_callbacks(self.current_slide)
        return True
    
    def _demo_loop(self):
        """Haupt-Demo-Schleife"""
        while self.running:
            try:
                # Aktuelle Slide anzeigen
                self._send_slide_signal(self.current_slide)
                self._notify_callbacks(self.current_slide)
                
                # Warten für Slide-Dauer
                start_time = time.time()
                while self.running and (time.time() - start_time) < self.slide_duration:
                    time.sleep(0.1)
                
                if not self.running:
                    break
                
                # Zur nächsten Slide
                if not self.next_slide():
                    break
                    
            except Exception as e:
                logger.error(f"Fehler in Demo-Schleife: {e}")
                break
        
        self.running = False
    
    def _send_slide_signal(self, slide_id):
        """Sendet Signal an Hardware für Slide-Wechsel"""
        try:
            # Signal an alle ESP32s senden
            for name, connection in hardware_manager.connections.items():
                if name.startswith('esp32_'):
                    connection.send_signal(f"page_{slide_id}")
            
            # UDP-Signal über GIGA senden (falls verfügbar)
            giga = hardware_manager.get_connection('giga')
            if giga and giga.status == "connected":
                giga.send_udp_signal("192.168.1.100", f"page_{slide_id}", 1)
            
            logger.debug(f"Slide-Signal gesendet: page_{slide_id}")
            
        except Exception as e:
            logger.error(f"Fehler beim Senden des Slide-Signals: {e}")
    
    def set_slide_duration(self, duration):
        """Setzt die Slide-Dauer"""
        self.slide_duration = max(1, duration)  # Minimum 1 Sekunde
        logger.info(f"Slide-Dauer geändert: {self.slide_duration}s")
    
    def set_loop_mode(self, loop_enabled):
        """Aktiviert/Deaktiviert Loop-Modus"""
        self.loop_demo = loop_enabled
        logger.info(f"Loop-Modus: {'aktiviert' if loop_enabled else 'deaktiviert'}")
    
    def get_status(self):
        """Gibt den aktuellen Demo-Status zurück"""
        return {
            'running': self.running,
            'current_slide': self.current_slide,
            'total_slides': self.total_slides,
            'slide_duration': self.slide_duration,
            'loop_mode': self.loop_demo
        }

# Globale Demo-Service Instanz
demo_service = DemoService()