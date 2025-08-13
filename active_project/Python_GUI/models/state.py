# models/state.py
"""
Globaler Anwendungszustand
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from models.slide import Slide
from models.hardware import HardwareDevice

@dataclass
class AppState:
    """Zentraler Anwendungszustand"""
    
    # Aktuelle Folie
    current_slide_id: int = 1
    
    # Alle Folien
    slides: Dict[int, Slide] = field(default_factory=dict)
    
    # Hardware-Geräte
    hardware_devices: Dict[str, HardwareDevice] = field(default_factory=dict)
    
    # Demo-Modus
    demo_active: bool = False
    demo_current_slide: int = 1
    
    # Creator-Modus
    creator_active: bool = False
    creator_selected_slide: int = 1
    
    # Presentation-Modus
    presentation_active: bool = False
    fullscreen_active: bool = False
    
    # Dev-Modus
    dev_mode: bool = False
    
    # Signal-Historie
    signal_history: List[dict] = field(default_factory=list)
    
    # Client-Verbindungen
    total_client_count: int = 0
    
    @property
    def current_slide(self) -> Optional[Slide]:
        """Aktuelle Folie"""
        return self.slides.get(self.current_slide_id)
    
    @property
    def connected_devices_count(self) -> int:
        """Anzahl verbundener Geräte"""
        return sum(1 for device in self.hardware_devices.values() if device.is_connected)
    
    def get_slide(self, slide_id: int) -> Optional[Slide]:
        """Folie nach ID"""
        return self.slides.get(slide_id)
    
    def add_signal_to_history(self, signal_id: int, device_name: str = "unknown"):
        """Signal zur Historie hinzufügen"""
        import time
        
        slide = self.get_slide(signal_id)
        entry = {
            'signal': signal_id,
            'name': slide.name if slide else f'Signal {signal_id}',
            'device': device_name,
            'timestamp': time.time()
        }
        
        self.signal_history.append(entry)
        
        # Nur letzte 100 Einträge behalten
        if len(self.signal_history) > 100:
            self.signal_history.pop(0)

# Globale State-Instanz
app_state = AppState()