# Dynamic Messe Stand V4

**Finale Version** - Bertrandt Interactive Display System mit modularer Architektur

## 🎯 Features

### ✅ Vollständige Funktionalität von V1
- **Multi-Hardware Support**: ESP32 + Arduino GIGA Integration
- **UDP-Kommunikation**: Drahtlose Signal-Übertragung
- **Automatische Demo**: Zeitgesteuerte Präsentationen
- **Content Creator**: Vollständiger Slide-Editor
- **Manuelle Steuerung**: Präsentations-Kontrolle
- **Hardware-Flash**: Firmware-Update Funktionen

### ✅ Saubere Architektur von V3
- **Modularer Aufbau**: Getrennte Core/Models/Services/UI
- **Responsive Design**: Automatische Skalierung
- **Theme System**: Light/Dark Mode Support
- **Logging System**: Umfassende Protokollierung
- **Error Handling**: Robuste Fehlerbehandlung

## 📁 Projekt-Struktur

```
Dynamic_Messe_Stand_V4/
├── Python_GUI/
│   ├── core/                 # Kern-Module
│   │   ├── config.py        # Zentrale Konfiguration
│   │   ├── theme.py         # Theme-Management
│   │   └── logger.py        # Logging-System
│   ├── models/              # Daten-Modelle
│   │   ├── hardware.py      # Hardware-Verbindungen
│   │   └── content.py       # Content-Management
│   ├── services/            # Business-Logic
│   │   └── demo.py          # Demo-Service
│   ├── ui/                  # Benutzeroberfläche
│   │   ├── main_window.py   # Haupt-Fenster
│   │   ├── components/      # UI-Komponenten
│   │   └── tabs/            # Tab-Implementierungen
│   └── main.py              # Hauptanwendung
├── Arduino/
│   ├── GIGA_UDP_Sender/     # Arduino GIGA Code
│   └── ESP32_UDP_Receiver/  # ESP32 Code
└── content/                 # Slide-Inhalte
```

## 🚀 Installation & Start

### Voraussetzungen
```bash
# Python 3.8+
pip install tkinter pillow pyserial

# Hardware
- Arduino GIGA R1 WiFi
- ESP32 DevKit (1-3 Stück)
- WiFi-Netzwerk "Bertrandt_Messe"
```

### Schnellstart
```bash
cd Dynamic_Messe_Stand_V4/Python_GUI
python main.py
```

### Mit Hardware
```bash
python main.py --esp32-port /dev/ttyUSB0
```

### Debug-Modus
```bash
python main.py --debug
```

### Ohne Hardware
```bash
python main.py --no-hardware
```

## 🎮 Bedienung

### Navigation
- **F11**: Vollbild ein/aus
- **ESC**: Vollbild verlassen
- **Tab-Navigation**: HOME → DEMO → CREATOR → PRESENTATION

### HOME Tab
- **Demo Starten**: Automatische Präsentation
- **Content Creator**: Slides bearbeiten
- **Präsentation**: Manuelle Steuerung
- **Hardware Status**: Verbindungsübersicht
- **System Info**: Technische Details
- **Hilfe**: Bedienungsanleitung

### DEMO Tab
- **▶️ Demo Starten/Stoppen**: Automatische Präsentation
- **⏮️ Zurück / ⏭️ Weiter**: Manuelle Navigation
- **Slide-Dauer**: Anzeigezeit pro Slide
- **Endlos-Schleife**: Kontinuierliche Wiederholung

### CREATOR Tab
- **➕ Neue Slide**: Slide hinzufügen
- **🗑️ Löschen**: Slide entfernen
- **📝 Editor**: Titel, Inhalt, Layout bearbeiten
- **💾 Speichern**: Änderungen sichern

### PRESENTATION Tab
- **🎯 Slide-Auswahl**: Direkte Slide-Anwahl
- **⏮️ Vorherige / ⏭️ Nächste**: Navigation
- **📡 Signal senden**: Hardware-Steuerung

## 🔧 Konfiguration

### Hardware-Ports (config.py)
```python
'esp32_1_port': '/dev/ttyUSB0',  # Haupt-ESP32
'esp32_2_port': '/dev/ttyUSB1',  # ESP32.2
'esp32_3_port': '/dev/ttyUSB2',  # ESP32.3
'giga_port': '/dev/ttyACM0',     # Arduino GIGA
```

### WiFi-Einstellungen (Arduino)
```cpp
const char* ssid = "Bertrandt_Messe";
const char* password = "Messe2024!";
```

### ESP32-IP-Adressen (GIGA)
```cpp
const char* esp32_ips[] = {
  "192.168.1.100",  // ESP32-1
  "192.168.1.101",  // ESP32-2
  "192.168.1.102"   // ESP32-3
};
```

## 📊 Status-Panel

Das linke Status-Panel zeigt:
- **🔌 Hardware**: Verbindungsstatus aller Geräte
- **▶️ Demo Status**: Aktueller Demo-Zustand
- **💻 System**: Zeit, Theme, Auflösung

## 🎨 Theme-System

- **Light Mode**: Standard-Theme (hell)
- **Dark Mode**: Dunkles Theme
- **Bertrandt Corporate**: Firmen-Farben (Blau #003366, Orange #FF6600)
- **Responsive**: Automatische Skalierung

## 🔍 Logging

Logs werden gespeichert in:
- **Konsole**: INFO-Level und höher
- **Datei**: `logs/BertrandtGUI_YYYYMMDD.log` (DEBUG-Level)

## 🛠️ Hardware-Integration

### Arduino GIGA (UDP-Sender)
- **WiFi-Verbindung**: Automatische Verbindung
- **UDP-Broadcast**: Signale an alle ESP32s
- **Serielle Steuerung**: Befehle von Python-GUI
- **Status-LEDs**: Verbindungs- und Aktivitäts-Anzeige

### ESP32 (UDP-Empfänger)
- **Signal-Empfang**: UDP-Pakete verarbeiten
- **Pin-Steuerung**: Hardware-Ausgänge aktivieren
- **Heartbeat-Monitoring**: Verbindungsüberwachung
- **Buzzer-Feedback**: Akustische Bestätigung

## 🔄 Signal-Flow

1. **GUI** → Slide-Wechsel
2. **Python** → Serieller Befehl an GIGA
3. **GIGA** → UDP-Broadcast an ESP32s
4. **ESP32** → Hardware-Pin Aktivierung
5. **Hardware** → Physische Aktion (LED, Relay, etc.)

## 🆘 Troubleshooting

### Hardware nicht verbunden
```bash
# Ports prüfen
ls /dev/tty*

# Ohne Hardware starten
python main.py --no-hardware
```

### WiFi-Probleme
- SSID/Passwort in Arduino-Code prüfen
- ESP32 Serial Monitor für Debug-Ausgaben

### Slide-Probleme
- Content-Verzeichnis prüfen: `content/page_X/config.json`
- Neue Slides über Creator-Tab erstellen

## 📈 Erweiterungen

Das modulare Design ermöglicht einfache Erweiterungen:
- **Neue Hardware**: Models/hardware.py erweitern
- **Neue UI-Komponenten**: ui/components/ hinzufügen
- **Neue Services**: services/ erweitern
- **Neue Themes**: core/theme.py anpassen

## 🏆 Vorteile V4

✅ **Beste aus beiden Welten**: Funktionalität von V1 + Architektur von V3  
✅ **Wartbar**: Saubere Modul-Trennung  
✅ **Erweiterbar**: Plugin-fähige Architektur  
✅ **Robust**: Umfassendes Error-Handling  
✅ **Benutzerfreundlich**: Intuitive Bedienung  
✅ **Professionell**: Corporate Design + Logging  

---

**Dynamic Messe Stand V4** - Die finale, professionelle Lösung für interaktive Messestände! 🚀