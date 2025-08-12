#!/bin/bash
# Bertrandt ESP32 GUI System Starter
# Optimierte Version mit Arduino Flash-Funktionalität

echo "Bertrandt ESP32 GUI-Steuerungssystem wird gestartet..."
echo "=================================================="

# Farben für bessere Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funktionen
log_info() {
    echo -e "${BLUE}INFO: $1${NC}"
}

log_success() {
    echo -e "${GREEN}SUCCESS: $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}

log_error() {
    echo -e "${RED}ERROR: $1${NC}"
}

# Arbeitsverzeichnis setzen
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Prüfen ob Python verfügbar ist
log_info "Prüfe Python3..."
if ! command -v python3 &> /dev/null; then
    log_error "Python3 ist nicht installiert!"
    exit 1
fi
log_success "Python3 gefunden"

# In GUI-Verzeichnis wechseln
cd "Python_GUI"

# Abhängigkeiten prüfen
log_info "Prüfe Python-Abhängigkeiten..."
if [ -d "venv" ]; then
    log_info "Verwende Virtual Environment..."
    source venv/bin/activate
    python -c "import serial, tkinter" 2>/dev/null || {
        log_warning "Installiere fehlende Abhängigkeiten..."
        pip install pyserial
    }
else
    log_warning "Kein Virtual Environment gefunden, verwende System Python..."
    python3 -c "import serial, tkinter" 2>/dev/null || {
        log_warning "Installiere fehlende Abhängigkeiten..."
        pip3 install pyserial --break-system-packages
    }
fi
log_success "Abhängigkeiten OK"

# Arduino CLI prüfen (optional)
log_info "Prüfe Arduino CLI..."
if command -v arduino-cli &> /dev/null; then
    log_success "Arduino CLI gefunden - Flash-Funktionen verfügbar"
else
    log_warning "Arduino CLI nicht gefunden - Flash-Funktionen in GUI verfügbar"
fi

# Verfügbare Ports anzeigen
log_info "Suche verfügbare Geräte..."
FOUND_PORTS=()

# Linux/Mac Ports prüfen
for port in /dev/ttyUSB* /dev/ttyACM* /dev/cu.usbserial* /dev/cu.usbmodem*; do
    if [ -e "$port" ]; then
        FOUND_PORTS+=("$port")
    fi
done

if [ ${#FOUND_PORTS[@]} -eq 0 ]; then
    log_warning "Keine Arduino-Geräte gefunden!"
    log_info "Das ist OK - Sie können Geräte später in der GUI flashen"
    ESP32_PORT="/dev/ttyUSB0"  # Default
else
    log_success "Gefundene Ports: ${FOUND_PORTS[*]}"
    
    # Versuche ESP32 zu identifizieren (meist USB)
    ESP32_PORT=""
    for port in "${FOUND_PORTS[@]}"; do
        if [[ "$port" == *"ttyUSB"* ]] || [[ "$port" == *"usbserial"* ]]; then
            ESP32_PORT="$port"
            break
        fi
    done
    
    # Falls kein USB-Port, nimm den ersten verfügbaren
    if [ -z "$ESP32_PORT" ]; then
        ESP32_PORT="${FOUND_PORTS[0]}"
    fi
    
    log_success "ESP32 Port gesetzt auf: $ESP32_PORT"
fi

# System starten
log_info "Starte Bertrandt GUI mit integriertem Flash-Tool..."
echo ""
echo "GUI Features:"
echo "   - ESP32 & Arduino GIGA Flash-Tool"
echo "   - Automatische Port-Erkennung"
echo "   - Live Signal-Monitoring"
echo "   - Boot-Button Erinnerung für ESP32"
echo ""

# Use virtual environment if available, otherwise system python
if [ -d "venv" ]; then
    source venv/bin/activate
    python Bertrandt_GUI.py --esp32-port="$ESP32_PORT"
    deactivate
else
    python3 Bertrandt_GUI.py --esp32-port="$ESP32_PORT"
fi

log_info "System beendet."