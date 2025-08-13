# core/logger.py
"""
Logging-Setup für Dynamic Messe Stand V3
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from core.config import config

def setup_logger(name: str = "messe_stand_v3", level: int = logging.INFO) -> logging.Logger:
    """Logger mit File- und Console-Handler einrichten"""
    
    # Logger erstellen
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Verhindere doppelte Handler
    if logger.handlers:
        return logger
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler
    config.ensure_directories()
    log_file = config.LOGS_DIR / f"messe_stand_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# Globaler Logger
logger = setup_logger()