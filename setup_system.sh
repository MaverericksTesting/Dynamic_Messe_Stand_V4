#!/bin/bash
# Bertrandt ESP32 System Setup
# One-time setup script for development environment

echo "Bertrandt ESP32 System Setup wird gestartet..."
echo "================================================"

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

# 1. System-Updates
log_info "Aktualisiere System-Pakete..."
sudo apt update && sudo apt upgrade -y
log_success "System aktualisiert"

# 2. Python3 und pip installieren
log_info "Installiere Python3 und pip..."
sudo apt install -y python3 python3-pip python3-tk python3-dev
log_success "Python3 installiert"

# 3. Arduino CLI installieren
log_info "Installiere Arduino CLI..."
if ! command -v arduino-cli &> /dev/null; then
    curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
    sudo mv bin/arduino-cli /usr/local/bin/
    log_success "Arduino CLI installiert"
else
    log_success "Arduino CLI bereits installiert"
fi

# 4. Arduino Cores installieren
log_info "Installiere Arduino Cores..."
arduino-cli core update-index
arduino-cli core install esp32:esp32
arduino-cli core install arduino:mbed_giga
log_success "Arduino Cores installiert"

# 5. Python-Abhängigkeiten installieren
log_info "Installiere Python-Abhängigkeiten..."
# Install python3-full for venv support
sudo apt install -y python3-full python3-venv

# Create virtual environment in Python_GUI directory
cd Python_GUI
if [ ! -d "venv" ]; then
    log_info "Erstelle Python Virtual Environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
log_info "Installiere Pakete in Virtual Environment..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
cd ..
log_success "Python-Abhängigkeiten installiert"

# 6. USB-Berechtigungen setzen
log_info "Setze USB-Berechtigungen..."
sudo usermod -a -G dialout $USER
sudo chmod 666 /dev/tty* 2>/dev/null || true
log_success "USB-Berechtigungen gesetzt"

# 7. VSCode Extensions empfehlen
log_info "Empfohlene VSCode Extensions:"
echo "  - ms-python.python"
echo "  - ms-vscode.cpptools"
echo "  - vsciot-vscode.vscode-arduino"
echo "  - ms-python.black-formatter"

# 8. Fertig
echo ""
log_success "Setup abgeschlossen!"
echo ""
echo "Nächste Schritte:"
echo "   1. Terminal neu starten (für USB-Berechtigungen)"
echo "   2. Arduino-Geräte anschließen"
echo "   3. ./start_system.sh ausführen"
echo ""
echo "Entwicklung:"
echo "   - VSCode öffnen: code ."
echo "   - Arduino IDE: arduino-cli"
echo "   - Python GUI: ./start_system.sh (empfohlen)"
echo "   - Python GUI manuell: cd Python_GUI && source venv/bin/activate && python Bertrandt_GUI.py"
echo ""

log_info "Bitte Terminal neu starten für USB-Berechtigungen!"