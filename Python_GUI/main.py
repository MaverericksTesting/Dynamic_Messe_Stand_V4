#!/usr/bin/env python3
"""
Dynamic Messe Stand V4 - Hauptanwendung
Bertrandt Interactive Display System
"""

import sys
import os
import argparse

# Pfad für Imports hinzufügen
sys.path.insert(0, os.path.dirname(__file__))

from core.logger import logger
from core.config import config
from models.hardware import hardware_manager
from ui.main_window import MainWindow

def setup_hardware():
    """Initialisiert Hardware-Verbindungen"""
    logger.info("🔌 Hardware-Setup wird gestartet...")
    
    try:
        # ESP32-Verbindungen hinzufügen
        esp32_1 = hardware_manager.add_esp32(config.hardware['esp32_1_port'], 1)
        esp32_2 = hardware_manager.add_esp32(config.hardware['esp32_2_port'], 2)
        esp32_3 = hardware_manager.add_esp32(config.hardware['esp32_3_port'], 3)
        
        # Arduino GIGA hinzufügen
        giga = hardware_manager.add_giga(config.hardware['giga_port'])
        
        # Verbindungen herstellen
        results = hardware_manager.connect_all()
        
        # Ergebnisse loggen
        for device, success in results.items():
            status = "✅ Verbunden" if success else "❌ Fehler"
            logger.info(f"{device}: {status}")
        
        return any(results.values())  # True wenn mindestens eine Verbindung erfolgreich
        
    except Exception as e:
        logger.error(f"Fehler beim Hardware-Setup: {e}")
        return False

def main():
    """Hauptfunktion"""
    # Argument-Parser
    parser = argparse.ArgumentParser(description='Dynamic Messe Stand V4')
    parser.add_argument('--esp32-port', help='ESP32 Port (Standard: /dev/ttyUSB0)')
    parser.add_argument('--no-hardware', action='store_true', help='Ohne Hardware-Verbindungen starten')
    parser.add_argument('--debug', action='store_true', help='Debug-Modus aktivieren')
    
    args = parser.parse_args()
    
    # Logging-Level setzen
    if args.debug:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("🚀 Dynamic Messe Stand V4 wird gestartet...")
    logger.info(f"Python Version: {sys.version}")
    logger.info(f"Arbeitsverzeichnis: {os.getcwd()}")
    
    try:
        # Hardware-Setup (falls gewünscht)
        if not args.no_hardware:
            hardware_success = setup_hardware()
            if not hardware_success:
                logger.warning("⚠️ Keine Hardware-Verbindungen erfolgreich - GUI startet trotzdem")
        else:
            logger.info("🔧 Hardware-Setup übersprungen (--no-hardware)")
        
        # GUI starten
        logger.info("🖥️ GUI wird initialisiert...")
        app = MainWindow(esp32_port=args.esp32_port)
        
        logger.info("✅ Dynamic Messe Stand V4 erfolgreich gestartet!")
        logger.info("💡 Drücke F11 für Vollbild, ESC zum Verlassen")
        
        # GUI-Hauptschleife starten
        app.run()
        
    except KeyboardInterrupt:
        logger.info("👋 Anwendung durch Benutzer beendet")
    except Exception as e:
        logger.error(f"💥 Unerwarteter Fehler: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        logger.info("🧹 Cleanup wird durchgeführt...")
        hardware_manager.disconnect_all()
        logger.info("👋 Dynamic Messe Stand V4 beendet")

if __name__ == "__main__":
    main()