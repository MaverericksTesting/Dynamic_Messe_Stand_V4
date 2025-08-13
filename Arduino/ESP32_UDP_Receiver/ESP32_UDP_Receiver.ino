/*
  ESP32 UDP Receiver für Dynamic Messe Stand V4
  Empfängt UDP-Signale und steuert Hardware
*/

#include <WiFi.h>
#include <WiFiUdp.h>

// WiFi-Konfiguration
const char* ssid = "Bertrandt_Messe";
const char* password = "Messe2024!";

// UDP-Konfiguration
WiFiUDP udp;
const int localPort = 8889;

// Hardware-Pins
const int statusLED = 2;
const int signalLED = 4;
const int relayPin = 5;
const int buzzerPin = 18;

// Signal-Mapping
struct SignalAction {
  String signal;
  int pin;
  int duration;
};

SignalAction signalMap[] = {
  {"page_1", 12, 1000},
  {"page_2", 13, 1000},
  {"page_3", 14, 1000},
  {"page_4", 15, 1000},
  {"page_5", 16, 1000},
  {"page_6", 17, 1000},
  {"page_7", 19, 1000},
  {"page_8", 21, 1000},
  {"page_9", 22, 1000},
  {"page_10", 23, 1000}
};
const int numSignals = sizeof(signalMap) / sizeof(SignalAction);

// Status-Variablen
unsigned long lastHeartbeat = 0;
unsigned long lastSignal = 0;
String lastReceivedSignal = "";
int signalCount = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("=== ESP32 UDP Receiver V4 ===");
  
  // Hardware-Pins initialisieren
  pinMode(statusLED, OUTPUT);
  pinMode(signalLED, OUTPUT);
  pinMode(relayPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);
  
  // Signal-Pins initialisieren
  for (int i = 0; i < numSignals; i++) {
    pinMode(signalMap[i].pin, OUTPUT);
    digitalWrite(signalMap[i].pin, LOW);
  }
  
  // Startup-Sequenz
  startupSequence();
  
  // WiFi verbinden
  connectToWiFi();
  
  // UDP starten
  udp.begin(localPort);
  Serial.printf("UDP Receiver gestartet auf Port %d\n", localPort);
  
  digitalWrite(statusLED, HIGH);
  Serial.println("ESP32 bereit für UDP-Empfang!");
  
  // Bereitschaftssignal
  tone(buzzerPin, 1000, 200);
  delay(300);
  tone(buzzerPin, 1500, 200);
}

void loop() {
  // WiFi-Verbindung prüfen
  if (WiFi.status() != WL_CONNECTED) {
    digitalWrite(statusLED, LOW);
    Serial.println("WiFi-Verbindung verloren - Neuverbindung...");
    connectToWiFi();
  } else {
    digitalWrite(statusLED, HIGH);
  }
  
  // UDP-Pakete empfangen
  int packetSize = udp.parsePacket();
  if (packetSize) {
    processUDPPacket();
  }
  
  // Serielle Befehle verarbeiten
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    processSerialCommand(command);
  }
  
  // Heartbeat-Timeout prüfen (30 Sekunden)
  if (millis() - lastHeartbeat > 30000 && lastHeartbeat > 0) {
    Serial.println("Heartbeat-Timeout - GIGA möglicherweise offline");
    blinkError();
  }
  
  delay(10);
}

void connectToWiFi() {
  Serial.printf("Verbinde mit WiFi: %s\n", ssid);
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    digitalWrite(statusLED, !digitalRead(statusLED));
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.printf("WiFi verbunden! IP: %s\n", WiFi.localIP().toString().c_str());
    digitalWrite(statusLED, HIGH);
  } else {
    Serial.println();
    Serial.println("WiFi-Verbindung fehlgeschlagen!");
    digitalWrite(statusLED, LOW);
  }
}

void processUDPPacket() {
  char packetBuffer[255];
  int len = udp.read(packetBuffer, 255);
  if (len > 0) {
    packetBuffer[len] = 0;
    String message = String(packetBuffer);
    
    Serial.printf("UDP empfangen von %s: %s\n", 
                  udp.remoteIP().toString().c_str(), 
                  message.c_str());
    
    processSignal(message);
  }
}

void processSignal(String signal) {
  digitalWrite(signalLED, HIGH);
  
  // Signal-Teile extrahieren
  int colonIndex = signal.indexOf(':');
  String signalName = signal;
  String signalValue = "1";
  
  if (colonIndex > 0) {
    signalName = signal.substring(0, colonIndex);
    signalValue = signal.substring(colonIndex + 1);
  }
  
  lastReceivedSignal = signalName;
  lastSignal = millis();
  signalCount++;
  
  // Spezielle Signale behandeln
  if (signalName == "heartbeat") {
    lastHeartbeat = millis();
    digitalWrite(signalLED, LOW);
    return;
  }
  
  // Signal-Mapping prüfen
  bool signalFound = false;
  for (int i = 0; i < numSignals; i++) {
    if (signalMap[i].signal == signalName) {
      activateSignal(signalMap[i].pin, signalMap[i].duration);
      signalFound = true;
      break;
    }
  }
  
  if (!signalFound) {
    Serial.printf("Unbekanntes Signal: %s\n", signalName.c_str());
  }
  
  // Bestätigungston
  tone(buzzerPin, 800, 100);
  
  delay(100);
  digitalWrite(signalLED, LOW);
}

void activateSignal(int pin, int duration) {
  Serial.printf("Aktiviere Pin %d für %d ms\n", pin, duration);
  
  digitalWrite(pin, HIGH);
  digitalWrite(relayPin, HIGH); // Haupt-Relay aktivieren
  
  delay(duration);
  
  digitalWrite(pin, LOW);
  digitalWrite(relayPin, LOW);
  
  Serial.printf("Pin %d deaktiviert\n", pin);
}

void processSerialCommand(String command) {
  Serial.printf("Serieller Befehl: %s\n", command.c_str());
  
  if (command == "STATUS") {
    printStatus();
  }
  else if (command == "RESET") {
    ESP.restart();
  }
  else if (command.startsWith("TEST:")) {
    String testSignal = command.substring(5);
    processSignal(testSignal);
  }
  else if (command == "PING") {
    Serial.println("PONG");
  }
  else {
    Serial.printf("Unbekannter Befehl: %s\n", command.c_str());
  }
}

void printStatus() {
  Serial.println("=== ESP32 Status ===");
  Serial.printf("WiFi: %s\n", WiFi.status() == WL_CONNECTED ? "Verbunden" : "Getrennt");
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("IP: %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("RSSI: %d dBm\n", WiFi.RSSI());
  }
  Serial.printf("UDP Port: %d\n", localPort);
  Serial.printf("Letztes Signal: %s\n", lastReceivedSignal.c_str());
  Serial.printf("Signal-Anzahl: %d\n", signalCount);
  Serial.printf("Letzter Heartbeat: %lu ms ago\n", millis() - lastHeartbeat);
  Serial.printf("Uptime: %lu ms\n", millis());
  Serial.printf("Freier Heap: %d bytes\n", ESP.getFreeHeap());
  Serial.println("Signal-Mapping:");
  for (int i = 0; i < numSignals; i++) {
    Serial.printf("  %s -> Pin %d\n", signalMap[i].signal.c_str(), signalMap[i].pin);
  }
  Serial.println("===================");
}

void startupSequence() {
  Serial.println("Starte ESP32 Initialisierung...");
  
  // LED-Test
  for (int i = 0; i < 3; i++) {
    digitalWrite(statusLED, HIGH);
    digitalWrite(signalLED, HIGH);
    tone(buzzerPin, 1000, 100);
    delay(200);
    digitalWrite(statusLED, LOW);
    digitalWrite(signalLED, LOW);
    delay(200);
  }
  
  // Pin-Test
  Serial.println("Teste Signal-Pins...");
  for (int i = 0; i < numSignals; i++) {
    digitalWrite(signalMap[i].pin, HIGH);
    delay(50);
    digitalWrite(signalMap[i].pin, LOW);
  }
  
  Serial.println("Initialisierung abgeschlossen!");
}

void blinkError() {
  for (int i = 0; i < 5; i++) {
    digitalWrite(statusLED, LOW);
    digitalWrite(signalLED, HIGH);
    tone(buzzerPin, 500, 100);
    delay(200);
    digitalWrite(statusLED, HIGH);
    digitalWrite(signalLED, LOW);
    delay(200);
  }
}