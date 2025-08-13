#!/usr/bin/env python3
"""
Hardware Models für Dynamic Messe Stand V4
ESP32 und Arduino GIGA Verbindungsmanagement
"""

import serial
import threading
import time
import queue
from core.logger import logger
from core.config import config

class HardwareConnection:
    """Basis-Klasse für Hardware-Verbindungen"""
    
    def __init__(self, port, name, baud_rate=115200):
        self.port = port
        self.name = name
        self.baud_rate = baud_rate
        self.connection = None
        self.thread = None
        self.running = False
        self.data_queue = queue.Queue()
        self.status = "disconnected"
    
    def connect(self):
        """Verbindung zur Hardware herstellen"""
        try:
            self.connection = serial.Serial(
                self.port, 
                self.baud_rate, 
                timeout=config.hardware['timeout']
            )
            self.status = "connected"
            logger.info(f"{self.name} verbunden auf {self.port}")
            return True
        except Exception as e:
            self.status = "error"
            logger.error(f"Fehler beim Verbinden mit {self.name}: {e}")
            return False
    
    def disconnect(self):
        """Verbindung trennen"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        
        if self.connection and self.connection.is_open:
            self.connection.close()
            self.status = "disconnected"
            logger.info(f"{self.name} getrennt")
    
    def start_reading(self):
        """Startet das Lesen von Daten in einem separaten Thread"""
        if not self.connection or not self.connection.is_open:
            return False
        
        self.running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()
        return True
    
    def _read_loop(self):
        """Lese-Schleife für eingehende Daten"""
        while self.running and self.connection and self.connection.is_open:
            try:
                if self.connection.in_waiting > 0:
                    data = self.connection.readline().decode('utf-8').strip()
                    if data:
                        self.data_queue.put({
                            'timestamp': time.time(),
                            'source': self.name,
                            'data': data
                        })
                time.sleep(0.01)  # Kurze Pause
            except Exception as e:
                logger.error(f"Fehler beim Lesen von {self.name}: {e}")
                break
    
    def send_data(self, data):
        """Daten an Hardware senden"""
        if not self.connection or not self.connection.is_open:
            return False
        
        try:
            self.connection.write(f"{data}\n".encode('utf-8'))
            logger.debug(f"Gesendet an {self.name}: {data}")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Senden an {self.name}: {e}")
            return False

class ESP32Connection(HardwareConnection):
    """ESP32-spezifische Verbindungsklasse"""
    
    def __init__(self, port, instance_number=1):
        super().__init__(port, f"ESP32-{instance_number}")
        self.instance_number = instance_number
        self.signals = {}
    
    def send_signal(self, signal_id, value=1):
        """Sendet ein Signal an den ESP32"""
        command = f"SIGNAL:{signal_id}:{value}"
        return self.send_data(command)
    
    def flash_firmware(self, firmware_path):
        """Flash neue Firmware auf ESP32"""
        # Implementierung für Firmware-Flash
        logger.info(f"Flashing firmware to {self.name}: {firmware_path}")
        # Hier würde der tatsächliche Flash-Prozess implementiert
        return True

class GIGAConnection(HardwareConnection):
    """Arduino GIGA-spezifische Verbindungsklasse"""
    
    def __init__(self, port=None):
        port = port or config.hardware['giga_port']
        super().__init__(port, "Arduino GIGA")
        self.udp_enabled = False
    
    def enable_udp_sender(self):
        """Aktiviert UDP-Sender Modus"""
        return self.send_data("UDP_ENABLE")
    
    def disable_udp_sender(self):
        """Deaktiviert UDP-Sender Modus"""
        return self.send_data("UDP_DISABLE")
    
    def send_udp_signal(self, target_ip, signal_id, value):
        """Sendet UDP-Signal über GIGA"""
        command = f"UDP_SEND:{target_ip}:{signal_id}:{value}"
        return self.send_data(command)

class HardwareManager:
    """Verwaltet alle Hardware-Verbindungen"""
    
    def __init__(self):
        self.connections = {}
        self.data_queue = queue.Queue()
        self.running = False
        self.monitor_thread = None
    
    def add_esp32(self, port, instance_number=1):
        """Fügt eine ESP32-Verbindung hinzu"""
        esp32 = ESP32Connection(port, instance_number)
        self.connections[f"esp32_{instance_number}"] = esp32
        return esp32
    
    def add_giga(self, port=None):
        """Fügt eine GIGA-Verbindung hinzu"""
        giga = GIGAConnection(port)
        self.connections["giga"] = giga
        return giga
    
    def connect_all(self):
        """Verbindet alle Hardware-Geräte"""
        results = {}
        for name, connection in self.connections.items():
            results[name] = connection.connect()
            if results[name]:
                connection.start_reading()
        return results
    
    def disconnect_all(self):
        """Trennt alle Hardware-Verbindungen"""
        self.running = False
        for connection in self.connections.values():
            connection.disconnect()
    
    def get_connection(self, name):
        """Gibt eine spezifische Verbindung zurück"""
        return self.connections.get(name)
    
    def get_all_data(self):
        """Sammelt Daten von allen Verbindungen"""
        all_data = []
        for connection in self.connections.values():
            while not connection.data_queue.empty():
                try:
                    data = connection.data_queue.get_nowait()
                    all_data.append(data)
                except queue.Empty:
                    break
        return all_data
    
    def get_status_summary(self):
        """Gibt eine Übersicht aller Verbindungsstatus zurück"""
        return {
            name: connection.status 
            for name, connection in self.connections.items()
        }

# Globale Hardware-Manager Instanz
hardware_manager = HardwareManager()