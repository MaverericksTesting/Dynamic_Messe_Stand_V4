#!/bin/bash
# Dynamic Messe Stand V4 - Development Mode
# Startet das System im Debug-Modus ohne Hardware

echo "🔧 Dynamic Messe Stand V4 - Development Mode"

cd "$(dirname "$0")/Python_GUI"

echo "🐛 Starte im Debug-Modus (ohne Hardware)..."
python3 main.py --no-hardware --debug

echo "👋 Development Session beendet"