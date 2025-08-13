#!/bin/bash
# Dynamic Messe Stand V4 - System Starter
# Startet das komplette System mit Hardware-Unterstützung

echo "🚀 Dynamic Messe Stand V4 - System wird gestartet..."

# Arbeitsverzeichnis wechseln
cd "$(dirname "$0")/Python_GUI"

# Python-Pfad prüfen
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 nicht gefunden! Bitte installieren."
    exit 1
fi

# Abhängigkeiten prüfen
echo "📦 Prüfe Python-Abhängigkeiten..."
python3 -c "import tkinter, PIL, serial" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️ Fehlende Abhängigkeiten werden installiert..."
    pip3 install pillow pyserial
fi

# Hardware-Ports prüfen
echo "🔌 Prüfe Hardware-Verbindungen..."
if [ -e "/dev/ttyUSB0" ]; then
    echo "✅ ESP32 gefunden: /dev/ttyUSB0"
    ESP32_PORT="/dev/ttyUSB0"
else
    echo "⚠️ ESP32 nicht gefunden - suche alternative Ports..."
    ESP32_PORT=$(ls /dev/ttyUSB* 2>/dev/null | head -1)
    if [ -z "$ESP32_PORT" ]; then
        echo "❌ Kein ESP32 gefunden - starte ohne Hardware"
        NO_HARDWARE="--no-hardware"
    else
        echo "✅ ESP32 gefunden: $ESP32_PORT"
    fi
fi

if [ -e "/dev/ttyACM0" ]; then
    echo "✅ Arduino GIGA gefunden: /dev/ttyACM0"
else
    echo "⚠️ Arduino GIGA nicht gefunden"
fi

# System starten
echo "🖥️ Starte GUI..."
if [ -n "$NO_HARDWARE" ]; then
    python3 main.py $NO_HARDWARE
else
    python3 main.py --esp32-port "$ESP32_PORT"
fi

echo "👋 Dynamic Messe Stand V4 beendet"