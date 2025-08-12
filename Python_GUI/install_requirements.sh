#!/bin/bash

echo "Installiere Bertrandt Multimedia GUI Abhängigkeiten..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Erstelle Virtual Environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install packages
echo "Installiere Python-Pakete in Virtual Environment..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

echo "Installation abgeschlossen!"
echo ""
echo "Bertrandt Multimedia GUI ist bereit!"
echo "Starten Sie mit: source venv/bin/activate && python Bertrandt_GUI.py"
echo "Oder verwenden Sie: ../start_system.sh"