/*
  Arduino GIGA UDP Sender für Dynamic Messe Stand V4
  Sendet UDP-Signale an ESP32-Empfänger
*/

#include <WiFi.h>
#include <WiFiUdp.h>

// WiFi-Konfiguration
const char* ssid = "Bertrandt_Messe";
const char* password = "Messe2024!";

// UDP-Konfiguration
WiFiUDP udp;
const int localPort = 8888;
const int targetPort = 8889;

// ESP32-Ziel-IPs
const char* esp32_ips[] = {
  "192.168.1.100",  // ESP32-1
  "192.168.1.101",  // ESP32-2
  "192.168.1.102"   // ESP32-3
};
const int num_esp32s = 3;

// Status-LEDs
const int statusLED = LED_BUILTIN;
const int wifiLED = 2;
const int udpLED = 3;

// Timing
unsigned long lastHeartbeat = 0;
const unsigned long heartbeatInterval = 5000; // 5 Sekunden

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(10);
  
  Serial.println("=== Arduino GIGA UDP Sender V4 ===");
  
  // LEDs initialisieren
  pinMode(statusLED, OUTPUT);
  pinMode(wifiLED, OUTPUT);
  pinMode(udpLED, OUTPUT);
  
  // Startup-Sequenz
  blinkLEDs();
  
  // WiFi verbinden
  connectToWiFi();
  
  // UDP starten
  udp.begin(localPort);
  Serial.printf("UDP Server gestartet auf Port %d\n", localPort);
  
  digitalWrite(statusLED, HIGH);
  Serial.println("GIGA bereit für UDP-Übertragung!");
}

void loop() {
  // WiFi-Verbindung prüfen
  if (WiFi.status() != WL_CONNECTED) {
    digitalWrite(wifiLED, LOW);
    Serial.println("WiFi-Verbindung verloren - Neuverbindung...");
    connectToWiFi();
  } else {
    digitalWrite(wifiLED, HIGH);
  }
  
  // Serielle Befehle verarbeiten
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    processCommand(command);
  }
  
  // Heartbeat senden
  if (millis() - lastHeartbeat > heartbeatInterval) {
    sendHeartbeat();
    lastHeartbeat = millis();
  }
  
  delay(10);
}

void connectToWiFi() {
  Serial.printf("Verbinde mit WiFi: %s\n", ssid);
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    digitalWrite(wifiLED, !digitalRead(wifiLED));
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.printf("WiFi verbunden! IP: %s\n", WiFi.localIP().toString().c_str());
    digitalWrite(wifiLED, HIGH);
  } else {
    Serial.println();
    Serial.println("WiFi-Verbindung fehlgeschlagen!");
    digitalWrite(wifiLED, LOW);
  }
}

void processCommand(String command) {
  Serial.printf("Befehl empfangen: %s\n", command.c_str());
  
  if (command.startsWith("UDP_SEND:")) {
    // Format: UDP_SEND:IP:SIGNAL:VALUE
    int firstColon = command.indexOf(':', 9);
    int secondColon = command.indexOf(':', firstColon + 1);
    
    if (firstColon > 0 && secondColon > 0) {
      String targetIP = command.substring(9, firstColon);
      String signal = command.substring(firstColon + 1, secondColon);
      String value = command.substring(secondColon + 1);
      
      sendUDPSignal(targetIP, signal, value);
    }
  }
  else if (command.startsWith("SIGNAL:")) {
    // Format: SIGNAL:signal_id:value
    int firstColon = command.indexOf(':', 7);
    if (firstColon > 0) {
      String signal = command.substring(7, firstColon);
      String value = command.substring(firstColon + 1);
      
      // An alle ESP32s senden
      broadcastSignal(signal, value);
    }
  }
  else if (command == "STATUS") {
    printStatus();
  }
  else if (command == "PING") {
    Serial.println("PONG");
  }
  else {
    Serial.printf("Unbekannter Befehl: %s\n", command.c_str());
  }
}

void sendUDPSignal(String targetIP, String signal, String value) {
  String message = signal + ":" + value;
  
  udp.beginPacket(targetIP.c_str(), targetPort);
  udp.print(message);
  udp.endPacket();
  
  digitalWrite(udpLED, HIGH);
  Serial.printf("UDP gesendet an %s: %s\n", targetIP.c_str(), message.c_str());
  delay(50);
  digitalWrite(udpLED, LOW);
}

void broadcastSignal(String signal, String value) {
  Serial.printf("Broadcasting Signal: %s:%s\n", signal.c_str(), value.c_str());
  
  for (int i = 0; i < num_esp32s; i++) {
    sendUDPSignal(esp32_ips[i], signal, value);
    delay(10); // Kurze Pause zwischen Sendungen
  }
}

void sendHeartbeat() {
  broadcastSignal("heartbeat", String(millis()));
}

void printStatus() {
  Serial.println("=== GIGA Status ===");
  Serial.printf("WiFi: %s\n", WiFi.status() == WL_CONNECTED ? "Verbunden" : "Getrennt");
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("IP: %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("RSSI: %d dBm\n", WiFi.RSSI());
  }
  Serial.printf("UDP Port: %d\n", localPort);
  Serial.printf("Uptime: %lu ms\n", millis());
  Serial.println("ESP32 Ziele:");
  for (int i = 0; i < num_esp32s; i++) {
    Serial.printf("  ESP32-%d: %s:%d\n", i+1, esp32_ips[i], targetPort);
  }
  Serial.println("==================");
}

void blinkLEDs() {
  for (int i = 0; i < 3; i++) {
    digitalWrite(statusLED, HIGH);
    digitalWrite(wifiLED, HIGH);
    digitalWrite(udpLED, HIGH);
    delay(200);
    digitalWrite(statusLED, LOW);
    digitalWrite(wifiLED, LOW);
    digitalWrite(udpLED, LOW);
    delay(200);
  }
}