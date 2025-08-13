# models/hardware.py
"""
Datenmodelle für Hardware-Komponenten
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum

class DeviceType(Enum):
    """Hardware-Geräte-Typen"""
    ESP32_1 = "esp32_1"
    ESP32_2 = "esp32_2" 
    ESP32_3 = "esp32_3"
    ARDUINO_GIGA = "giga"

class ConnectionStatus(Enum):
    """Verbindungsstatus"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"

@dataclass
class HardwareDevice:
    """Datenmodell für Hardware-Gerät"""
    device_type: DeviceType
    port: str
    baud_rate: int = 115200
    status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    last_signal: Optional[int] = None
    client_count: int = 0
    error_message: str = ""
    
    @property
    def display_name(self) -> str:
        """Anzeigename für das Gerät"""
        names = {
            DeviceType.ESP32_1: "ESP32.1 (Haupt)",
            DeviceType.ESP32_2: "ESP32.2 (Addon)",
            DeviceType.ESP32_3: "ESP32.3 (Addon)",
            DeviceType.ARDUINO_GIGA: "Arduino GIGA"
        }
        return names.get(self.device_type, str(self.device_type))
    
    @property
    def is_connected(self) -> bool:
        """Ist das Gerät verbunden?"""
        return self.status == ConnectionStatus.CONNECTED
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiere zu Dictionary"""
        return {
            "device_type": self.device_type.value,
            "port": self.port,
            "baud_rate": self.baud_rate,
            "status": self.status.value,
            "last_signal": self.last_signal,
            "client_count": self.client_count,
            "error_message": self.error_message
        }