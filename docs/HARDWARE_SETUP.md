# 🔧 Hardware Setup Guide

## 📋 Required Components

### Arduino Hardware
- **Arduino GIGA R1 WiFi** - Main controller with WiFi capability
- **ESP32 Development Board** - WiFi receiver and serial bridge
- **2x USB Cables** - USB-A to USB-C (GIGA) and USB-A to Micro-USB (ESP32)

### Computer Requirements
- **Mini PC** with Ubuntu 20.04+ or similar Linux distribution
- **2x USB Ports** available
- **WiFi capability** (optional, for monitoring)

## 🔌 Physical Connections

### Step 1: Arduino GIGA R1 WiFi
```
GIGA R1 WiFi → Mini PC
├── USB-C Port → USB-A Port (typically /dev/ttyACM0)
├── Power: Via USB or external 7-12V
└── WiFi: Built-in antenna
```

### Step 2: ESP32 Development Board
```
ESP32 → Mini PC
├── Micro-USB Port → USB-A Port (typically /dev/ttyUSB0)
├── Power: Via USB (5V)
├── WiFi: Built-in antenna
└── Boot Button: For programming mode
```

## 📡 Network Configuration

### WiFi Network (Created by ESP32)
```
SSID: TestNetz
Password: 12345678
IP Range: 192.168.4.x
ESP32 IP: 192.168.4.1
Gateway: 192.168.4.1
```

### Communication Flow
```
[GIGA] --WiFi UDP--> [ESP32] --USB Serial--> [Mini PC]
   |                    |                        |
   ├─ Sends signals     ├─ Receives UDP          ├─ Receives serial
   ├─ Port 4210         ├─ Forwards to serial    ├─ Displays in GUI
   └─ Format: 1-10      └─ 115200 baud          └─ Real-time monitoring
```

## ⚙️ Device Configuration

### Arduino GIGA R1 WiFi Settings
```cpp
// In GIGA_UDP_Sender.ino
const char* ssid = "TestNetz";
const char* password = "12345678";
const char* udp_server = "192.168.4.1";
const int udp_port = 4210;
```

### ESP32 Settings
```cpp
// In ESP32_UDP_Receiver.ino
const char* ssid = "TestNetz";
const char* password = "12345678";
IPAddress local_IP(192, 168, 4, 1);
IPAddress gateway(192, 168, 4, 1);
IPAddress subnet(255, 255, 255, 0);
const int udp_port = 4210;
const int serial_baud = 115200;
```

## 🔍 Verification Steps

### 1. Check USB Connections
```bash
# List connected devices
ls /dev/tty*

# Expected output:
# /dev/ttyACM0  (Arduino GIGA)
# /dev/ttyUSB0  (ESP32)
```

### 2. Verify Arduino CLI Recognition
```bash
# List connected boards
arduino-cli board list

# Expected output:
# Port         Protocol Type              Board Name  FQBN            Core
# /dev/ttyACM0 serial   Serial Port (USB) Arduino GIGA arduino:mbed_giga:giga
# /dev/ttyUSB0 serial   Serial Port (USB) ESP32 Dev Module esp32:esp32:esp32
```

### 3. Test Serial Communication
```bash
# Monitor ESP32 output
arduino-cli monitor -p /dev/ttyUSB0 -c baudrate=115200

# Expected output:
# WiFi connected
# IP address: 192.168.4.1
# UDP server started on port 4210
```

### 4. Test WiFi Network
```bash
# Scan for WiFi networks
nmcli dev wifi list | grep TestNetz

# Expected output:
# TestNetz  Infra  6     54 Mbit/s  100     ▂▄▆█  WPA2
```

## 🚨 Troubleshooting

### USB Connection Issues
```bash
# Fix permissions
sudo usermod -a -G dialout $USER
sudo chmod 666 /dev/ttyACM* /dev/ttyUSB*

# Restart udev service
sudo systemctl restart udev
```

### ESP32 Programming Issues
```bash
# Put ESP32 in programming mode:
# 1. Hold BOOT button
# 2. Press RESET button
# 3. Release RESET button
# 4. Release BOOT button
# 5. Try upload again
```

### WiFi Connection Problems
```bash
# Reset ESP32 WiFi settings
# 1. Flash ESP32 with new code
# 2. Check serial monitor for errors
# 3. Verify SSID/password in code
```

### Power Issues
```bash
# Check USB power delivery
lsusb -v | grep -E "Bus|MaxPower"

# Ensure sufficient power:
# - GIGA: 500mA via USB
# - ESP32: 240mA via USB
```

## 📊 Expected Behavior

### Normal Operation
1. **ESP32 boots** → Creates WiFi network "TestNetz"
2. **GIGA boots** → Connects to "TestNetz"
3. **GIGA sends signals** → UDP packets to ESP32
4. **ESP32 receives** → Forwards to Mini PC via serial
5. **GUI displays** → Real-time signal monitoring

### Status Indicators
- **ESP32 LED** - Blinks when receiving UDP
- **GIGA LED** - Blinks when sending UDP
- **Serial Output** - Shows "SIGNAL:X" messages
- **GUI Status** - Green = connected, Red = disconnected

## 🔧 Maintenance

### Regular Checks
- **USB cables** - Check for wear/damage
- **Power supply** - Ensure stable 5V
- **WiFi range** - Keep devices within 10m
- **Serial ports** - Verify correct assignment

### Performance Optimization
- **Baud rate** - 115200 for optimal speed
- **WiFi channel** - Use channel 6 for best compatibility
- **Update rate** - 100ms minimum between signals
- **Buffer size** - 1024 bytes for UDP packets