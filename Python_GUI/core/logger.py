#!/usr/bin/env python3
"""
Logging System für Dynamic Messe Stand V4
Zentrale Protokollierung aller Ereignisse
"""

import logging
import os
from datetime import datetime

class Logger:
    """Zentrale Logging-Klasse"""
    
    def __init__(self, name="BertrandtGUI", log_dir="logs"):
        self.name = name
        self.log_dir = log_dir
        self.setup_logger()
    
    def setup_logger(self):
        """Initialisiert das Logging-System"""
        # Log-Verzeichnis erstellen
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # Logger konfigurieren
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File Handler
        log_file = os.path.join(
            self.log_dir, 
            f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        # Handler hinzufügen
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message):
        """Info-Level Logging"""
        self.logger.info(message)
    
    def debug(self, message):
        """Debug-Level Logging"""
        self.logger.debug(message)
    
    def warning(self, message):
        """Warning-Level Logging"""
        self.logger.warning(message)
    
    def error(self, message):
        """Error-Level Logging"""
        self.logger.error(message)
    
    def critical(self, message):
        """Critical-Level Logging"""
        self.logger.critical(message)

# Globale Logger-Instanz
logger = Logger()