# 🚀 Dynamic Messe Stand V2 - Bertrandt ESP32 System

> **Professional Trade Show Presentation System with Arduino Integration**

## 📋 System Overview

**Signal Flow:** `Arduino GIGA → ESP32 (WiFi) → Mini PC (USB) → GUI Display`

This system enables wireless control of multimedia presentations using Arduino hardware and a professional Python GUI interface.

## ⚡ Quick Start

### 🎯 First Time Setup
```bash
# 1. Clone repository
git clone https://github.com/MaverericksTesting/Dynamic_Messe_Stand_V2.git
cd Dynamic_Messe_Stand_V2

# 2. Run setup (installs everything)
./setup_system.sh

# 3. Restart terminal for USB permissions
# 4. Connect Arduino devices
# 5. Start system
./start_system.sh
```

### 🚀 Daily Usage
```bash
./start_system.sh  # Starts everything automatically
```

## 📁 Project Structure

```
Dynamic_Messe_Stand_V2/
├── 📄 README.md                 # This file
├── 📄 QUICK_START.md            # Quick reference
├── 🚀 start_system.sh           # Main launcher
├── 🔧 setup_system.sh           # One-time setup
├── 📁 .vscode/                  # VSCode configuration
├── 📁 Arduino/                  # Arduino projects
│   ├── ESP32_UDP_Receiver/      # ESP32 WiFi receiver
│   └── GIGA_UDP_Sender/         # Arduino GIGA sender
├── 📁 Python_GUI/               # Main GUI application
│   ├── Bertrandt_GUI.py         # Main application
│   ├── requirements.txt         # Python dependencies
│   └── content/                 # Presentation content
└── 📁 docs/                     # Documentation
```

## 🎨 Features

### 🖥️ Professional GUI
- **Modern Design** - Clean, responsive interface
- **Button-Based Control** - No keyboard required
- **Real-Time Monitoring** - Live signal display
- **Content Management** - Easy page editing

### 🔧 Arduino Integration
- **Integrated Flashing** - Flash devices from GUI
- **Auto Port Detection** - Finds devices automatically
- **Serial Monitoring** - Real-time debugging
- **Error Handling** - Comprehensive error recovery

### 📱 Presentation System
- **10 Content Pages** - Customizable presentations
- **Auto Demo Mode** - Automatic page cycling
- **Manual Control** - Direct page selection
- **Multimedia Support** - Images, videos, text

## 🛠️ Hardware Requirements

- **Arduino GIGA R1 WiFi** - Main controller
- **ESP32 Development Board** - WiFi receiver
- **Mini PC** - Ubuntu/Linux system
- **2x USB Cables** - Device connections

## 🔧 Development

### VSCode Setup
```bash
code .  # Opens project with full configuration
```

**Available Tasks (Ctrl+Shift+P → "Tasks"):**
- 🚀 Start System
- 🔧 Setup System  
- 📱 Flash ESP32
- 🔧 Flash GIGA
- 🐍 Run Python GUI
- 📊 Monitor ESP32/GIGA

### Arduino IDE Integration
- **Auto-configured** for ESP32 and GIGA
- **IntelliSense** for Arduino libraries
- **One-click compilation** and upload

### Python Development
- **Debug Configuration** ready
- **Requirements** auto-installed
- **Code Formatting** with Black
- **Linting** with Pylint

## 📊 Technical Details

### Communication Protocol
```
GIGA → ESP32: UDP WiFi (192.168.4.1:4210)
ESP32 → PC: Serial USB (115200 baud)
Format: "SIGNAL:X" (X = 1-10)
```

### WiFi Configuration
- **SSID:** TestNetz
- **Password:** 12345678
- **ESP32 IP:** 192.168.4.1

## 🔍 Troubleshooting

### Common Issues
```bash
# Arduino not found
arduino-cli board list
sudo usermod -a -G dialout $USER

# Python dependencies
pip3 install -r Python_GUI/requirements.txt

# USB permissions
sudo chmod 666 /dev/tty*
```

### Debug Tools
```bash
# Monitor ESP32
arduino-cli monitor -p /dev/ttyUSB0 -c baudrate=115200

# Monitor GIGA
arduino-cli monitor -p /dev/ttyACM0 -c baudrate=115200

# Test Python GUI
python3 Python_GUI/Bertrandt_GUI.py --esp32-port=/dev/ttyUSB0
```

## 📞 Support

**For Issues:**
1. Check hardware connections
2. Run `./setup_system.sh` again
3. Check logs in terminal output
4. Verify USB permissions

**Development:**
- VSCode: Full IDE integration
- Arduino CLI: Command-line tools
- Python: Debug and development tools

---

**🎯 Ready for Professional Trade Show Presentations!**