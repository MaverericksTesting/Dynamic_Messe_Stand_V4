# services/hardware.py
"""
Hardware-Kommunikation Service
"""
import serial
import threading
import time
import queue
from typing import Dict, Optional, Callable
from models.hardware import HardwareDevice, DeviceType, ConnectionStatus
from core.config import config
from core.logger import logger
from core.bus import bus

class HardwareService:
    """Service für Hardware-Kommunikation mit mehreren ESP32/GIGA Geräten"""
    
    def __init__(self):
        self.devices: Dict[str, HardwareDevice] = {}
        self.connections: Dict[str, serial.Serial] = {}
        self.threads: Dict[str, threading.Thread] = {}
        self.data_queue = queue.Queue()
        self.running = False
        
        self._setup_devices()
    
    def _setup_devices(self):
        """Initialisiere Hardware-Geräte"""
        device_configs = [
            (DeviceType.ESP32_1, config.ESP32_1_PORT),
            (DeviceType.ESP32_2, config.ESP32_2_PORT),
            (DeviceType.ESP32_3, config.ESP32_3_PORT),
            (DeviceType.ARDUINO_GIGA, config.GIGA_PORT),
        ]
        
        for device_type, port in device_configs:
            device = HardwareDevice(
                device_type=device_type,
                port=port,
                baud_rate=config.BAUD_RATE
            )
            self.devices[device_type.value] = device
    
    def connect_all(self) -> int:
        """Verbinde alle verfügbaren Geräte"""
        connected_count = 0
        
        for device_name, device in self.devices.items():
            if self.connect_device(device_name):
                connected_count += 1
        
        if connected_count > 0:
            self.start_reading()
            bus.publish("hardware:status_changed", 
                       connected_count=connected_count, 
                       dev_mode=False)
        else:
            logger.warning("Keine Hardware gefunden - Dev Mode aktiviert")
            bus.publish("hardware:dev_mode_activated")
        
        return connected_count
    
    def connect_device(self, device_name: str) -> bool:
        """Verbinde einzelnes Gerät"""
        if device_name not in self.devices:
            return False
        
        device = self.devices[device_name]
        device.status = ConnectionStatus.CONNECTING
        
        try:
            connection = serial.Serial(device.port, device.baud_rate, timeout=1)
            time.sleep(2)  # Warten auf Initialisierung
            
            self.connections[device_name] = connection
            device.status = ConnectionStatus.CONNECTED
            device.error_message = ""
            
            logger.info(f"✅ {device.display_name} verbunden auf {device.port}")
            bus.publish("hardware:device_connected", device_name=device_name, device=device)
            return True
            
        except Exception as e:
            device.status = ConnectionStatus.ERROR
            device.error_message = str(e)
            logger.error(f"❌ {device.display_name} Verbindung fehlgeschlagen: {e}")
            bus.publish("hardware:device_error", device_name=device_name, error=str(e))
            return False
    
    def disconnect_device(self, device_name: str):
        """Trenne einzelnes Gerät"""
        if device_name in self.connections:
            try:
                self.connections[device_name].close()
                del self.connections[device_name]
                logger.info(f"🔌 {device_name} getrennt")
            except Exception as e:
                logger.error(f"Fehler beim Trennen von {device_name}: {e}")
        
        if device_name in self.devices:
            self.devices[device_name].status = ConnectionStatus.DISCONNECTED
            bus.publish("hardware:device_disconnected", device_name=device_name)
    
    def disconnect_all(self):
        """Trenne alle Geräte"""
        self.running = False
        
        for device_name in list(self.connections.keys()):
            self.disconnect_device(device_name)
        
        # Warte auf Thread-Beendigung
        for thread in self.threads.values():
            if thread.is_alive():
                thread.join(timeout=1)
        
        self.threads.clear()
    
    def start_reading(self):
        """Starte Daten-Lese-Threads für alle verbundenen Geräte"""
        self.running = True
        
        for device_name, connection in self.connections.items():
            thread = threading.Thread(
                target=self._read_device_data,
                args=(device_name, connection),
                daemon=True
            )
            thread.start()
            self.threads[device_name] = thread
        
        # Starte Datenverarbeitung
        self._start_data_processing()
    
    def _read_device_data(self, device_name: str, connection: serial.Serial):
        """Lese Daten von einem Gerät in separatem Thread"""
        device = self.devices[device_name]
        
        while self.running and connection.is_open:
            try:
                if connection.in_waiting > 0:
                    line = connection.readline().decode('utf-8').strip()
                    
                    if line.startswith("SIGNAL:"):
                        signal_value = int(line.split(":")[1])
                        self.data_queue.put(('signal', device_name, signal_value))
                        device.last_signal = signal_value
                        
                    elif line.startswith("Clients:"):
                        client_count = int(line.split(":")[1].strip())
                        self.data_queue.put(('clients', device_name, client_count))
                        device.client_count = client_count
                        
            except Exception as e:
                if self.running:  # Nur loggen wenn nicht beim Shutdown
                    logger.error(f"Fehler beim Lesen von {device_name}: {e}")
                    device.status = ConnectionStatus.ERROR
                    device.error_message = str(e)
                break
            
            time.sleep(0.01)  # Kurze Pause
    
    def _start_data_processing(self):
        """Starte Datenverarbeitung im Hauptthread"""
        def process_data():
            try:
                while not self.data_queue.empty():
                    data_type, device_name, value = self.data_queue.get_nowait()
                    
                    if data_type == 'signal':
                        bus.publish("hardware:signal_received", 
                                   device_name=device_name, 
                                   signal_id=value)
                        
                    elif data_type == 'clients':
                        bus.publish("hardware:clients_updated", 
                                   device_name=device_name, 
                                   client_count=value)
                        
            except queue.Empty:
                pass
            
            # Nächste Verarbeitung planen (wird vom UI-Framework aufgerufen)
            if self.running:
                bus.publish("hardware:schedule_data_processing")
        
        bus.publish("hardware:start_data_processing", processor=process_data)
    
    def send_command(self, device_name: str, command: str) -> bool:
        """Sende Kommando an Gerät"""
        if device_name not in self.connections:
            return False
        
        try:
            connection = self.connections[device_name]
            connection.write(f"{command}\n".encode('utf-8'))
            logger.debug(f"Kommando an {device_name}: {command}")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Senden an {device_name}: {e}")
            return False
    
    def get_device_status(self, device_name: str) -> Optional[HardwareDevice]:
        """Status eines Geräts abrufen"""
        return self.devices.get(device_name)
    
    def get_all_devices(self) -> Dict[str, HardwareDevice]:
        """Alle Geräte abrufen"""
        return self.devices.copy()
    
    def restart_connections(self):
        """Alle Verbindungen neu starten"""
        logger.info("🔄 Starte Hardware-Verbindungen neu...")
        self.disconnect_all()
        time.sleep(1)
        return self.connect_all()