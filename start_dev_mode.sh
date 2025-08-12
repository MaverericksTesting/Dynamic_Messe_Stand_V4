#!/bin/bash

echo "🚀 Bertrandt ESP32 GUI - ENTWICKLUNGSMODUS"
echo "=========================================="
echo "✨ Auto-Reload aktiviert!"
echo "✨ GUI lädt sich automatisch bei Code-Änderungen neu"
echo "✨ Einfach Code bearbeiten und speichern - GUI aktualisiert sich automatisch"
echo ""
echo "💡 Tipps:"
echo "   - Änderungen in .py Dateien werden automatisch erkannt"
echo "   - 2 Sekunden Debounce-Zeit zwischen Reloads"
echo "   - Strg+C zum Beenden"
echo ""

# Zum Python GUI Verzeichnis wechseln
cd "$(dirname "$0")/Python_GUI"

# Virtual Environment aktivieren falls vorhanden
if [ -d "venv" ]; then
    echo "🔧 Aktiviere Virtual Environment..."
    source venv/bin/activate
fi

# Watchdog installieren falls nicht vorhanden
echo "🔧 Prüfe Auto-Reload Abhängigkeiten..."
pip install watchdog>=2.1.0 >/dev/null 2>&1

echo ""
echo "🎯 Starte GUI mit Auto-Reload..."
echo "📁 Überwacht: $(pwd)"
echo ""

# GUI starten
python3 Bertrandt_GUI.py