/*
 * ESP32 Fan Simulator - PWM Speed Control
 * Smart Home IoT Project - HUST
 * 
 * Kết nối qua Ngrok để giao tiếp với MQTT broker local
 * 
 * Hardware (Wokwi):
 * - Fan Motor (LED PWM) on GPIO 18
 * - Speed indicator LEDs: GPIO 25 (S1), 26 (S2), 27 (S3)
 * - Button UP on GPIO 19
 * - Button DOWN on GPIO 21
 * 
 * MQTT Topics:
 * - Publish: device/new (đăng ký device)
 * - Publish: device/data/{deviceId} (gửi trạng thái)
 * - Subscribe: device/control/{deviceId} (nhận lệnh)
 * 
 * Commands (JSON):
 * - {"action": "ON"}
 * - {"action": "OFF"}
 * - {"action": "SET_SPEED", "speed": 0-3}
 */

#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ==================== HARDWARE CONFIG ====================
#define FAN_PIN         18    // PWM output (simulate motor)
#define LED_SPEED1      25    // Speed level 1 indicator
#define LED_SPEED2      26    // Speed level 2 indicator  
#define LED_SPEED3      27    // Speed level 3 indicator
#define BTN_UP          19    // Increase speed button
#define BTN_DOWN        21    // Decrease speed button

// ==================== WIFI CONFIG ====================
// Wokwi sử dụng WiFi ảo "Wokwi-GUEST"
const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASS = "";

// ==================== MQTT CONFIG (NGROK) ====================
// ⚠️ THAY ĐỔI THEO URL NGROK CỦA BẠN
// Chạy: ngrok tcp 1883
// Sẽ nhận được URL dạng: tcp://0.tcp.ap.ngrok.io:12345

const char* MQTT_BROKER = "0.tcp.ap.ngrok.io";  // ← Thay bằng hostname ngrok
const int MQTT_PORT = 14267;                     // ← Thay bằng port ngrok

// ==================== BSSID CONFIG ====================
// ⚠️ THAY BẰNG BSSID THẬT CỦA WIFI BẠN ĐANG TEST
// Cách lấy BSSID:
// - Windows: netsh wlan show interfaces
// - Android: Settings > WiFi > Chi tiết mạng > BSSID
// - iOS: Dùng app Network Analyzer
// Format: "AA:BB:CC:DD:EE:FF"

const char* WIFI_BSSID = "e4:77:27:ce:78:ac";   // BSSID của iPhone hotspot "Loc"

// ==================== OBJECTS ====================
WiFiClient espClient;
PubSubClient mqtt(espClient);

// ==================== STATE ====================
String deviceId;
String controlTopic;
String dataTopic;

bool fanOn = false;
int fanSpeed = 0;  // 0 = OFF, 1-3 = speed levels

unsigned long lastPublish = 0;
unsigned long lastButton = 0;
const unsigned long PUBLISH_INTERVAL = 5000;  // 5 giây
const unsigned long DEBOUNCE = 200;           // Button debounce

// PWM config
const int PWM_CHANNEL = 0;
const int PWM_FREQ = 5000;
const int PWM_RESOLUTION = 8;

// ==================== UPDATE FAN OUTPUT ====================
void updateFanOutput() {
    // PWM values for each speed level: 0%, 33%, 66%, 100%
    int pwmValues[] = {0, 85, 170, 255};
    ledcWrite(PWM_CHANNEL, pwmValues[fanSpeed]);
    
    // Update speed indicator LEDs
    digitalWrite(LED_SPEED1, fanSpeed >= 1 ? HIGH : LOW);
    digitalWrite(LED_SPEED2, fanSpeed >= 2 ? HIGH : LOW);
    digitalWrite(LED_SPEED3, fanSpeed >= 3 ? HIGH : LOW);
    
    Serial.printf("🌀 Fan: %s | Speed: %d/3\n", fanOn ? "ON" : "OFF", fanSpeed);
}

// ==================== PUBLISH STATE ====================
void publishState() {
    StaticJsonDocument<200> doc;
    doc["status"] = fanOn ? "ON" : "OFF";
    doc["speed"] = fanSpeed;
    doc["uptime"] = millis() / 1000;
    doc["rssi"] = WiFi.RSSI();
    
    char buffer[256];
    serializeJson(doc, buffer);
    mqtt.publish(dataTopic.c_str(), buffer);
    
    Serial.printf("📤 State published: %s, speed=%d\n", fanOn ? "ON" : "OFF", fanSpeed);
}

// ==================== SET FAN SPEED ====================
void setFanSpeed(int speed) {
    fanSpeed = constrain(speed, 0, 3);
    fanOn = (fanSpeed > 0);
    updateFanOutput();
    publishState();
}

// ==================== MQTT CALLBACK (RECEIVE COMMANDS) ====================
void mqttCallback(char* topic, byte* payload, unsigned int length) {
    Serial.printf("\n📩 Command received [%s]\n", topic);
    
    // Parse JSON
    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, payload, length);
    
    if (error) {
        Serial.printf("❌ JSON parse error: %s\n", error.c_str());
        return;
    }
    
    // Print received command
    Serial.print("   Data: ");
    serializeJson(doc, Serial);
    Serial.println();
    
    // Process action
    const char* action = doc["action"] | "";
    
    if (strcmp(action, "ON") == 0) {
        fanOn = true;
        if (fanSpeed == 0) fanSpeed = 1;  // Default to speed 1
        updateFanOutput();
        publishState();
        Serial.println("✅ Fan turned ON");
        
    } else if (strcmp(action, "OFF") == 0) {
        fanOn = false;
        fanSpeed = 0;
        updateFanOutput();
        publishState();
        Serial.println("✅ Fan turned OFF");
        
    } else if (strcmp(action, "SET_SPEED") == 0) {
        int newSpeed = doc["speed"] | fanSpeed;
        setFanSpeed(newSpeed);
        Serial.printf("✅ Speed set to %d\n", fanSpeed);
        
    } else {
        Serial.printf("⚠️ Unknown action: %s\n", action);
    }
}

// ==================== WIFI SETUP ====================
void setupWiFi() {
    Serial.print("📶 Connecting to WiFi");
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 60) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n✅ WiFi connected!");
        Serial.println("   IP: " + WiFi.localIP().toString());
    } else {
        Serial.println("\n❌ WiFi connection failed!");
    }
}

// ==================== REGISTER DEVICE ====================
void registerDevice() {
    StaticJsonDocument<256> doc;
    doc["type"] = "FAN";
    doc["name"] = "Smart Fan";
    // Dùng BSSID thật để app có thể tìm thấy device trong cùng mạng
    doc["bssid"] = WIFI_BSSID;
    doc["controllerMAC"] = deviceId;
    doc["state"] = "online";
    
    char buffer[300];
    serializeJson(doc, buffer);
    mqtt.publish("device/new", buffer);
    
    Serial.println("📤 Device registered: " + deviceId);
}

// ==================== MQTT RECONNECT ====================
void reconnectMQTT() {
    int attempts = 0;
    while (!mqtt.connected() && attempts < 5) {
        Serial.print("🔌 Connecting to MQTT...");
        String clientId = "Fan-" + deviceId;
        
        if (mqtt.connect(clientId.c_str())) {
            Serial.println(" connected!");
            
            // Subscribe to control topic
            mqtt.subscribe(controlTopic.c_str());
            Serial.println("📥 Subscribed: " + controlTopic);
            
            // Register device
            registerDevice();
            return;
            
        } else {
            Serial.printf(" failed (rc=%d). Retry in 3s...\n", mqtt.state());
            delay(3000);
            attempts++;
        }
    }
}

// ==================== HANDLE PHYSICAL BUTTONS ====================
void handleButtons() {
    if (millis() - lastButton < DEBOUNCE) return;
    
    // Button UP - increase speed
    if (digitalRead(BTN_UP) == LOW) {
        lastButton = millis();
        if (fanSpeed < 3) {
            setFanSpeed(fanSpeed + 1);
            Serial.println("⬆️ Button: Speed UP");
        }
    }
    
    // Button DOWN - decrease speed
    if (digitalRead(BTN_DOWN) == LOW) {
        lastButton = millis();
        if (fanSpeed > 0) {
            setFanSpeed(fanSpeed - 1);
            Serial.println("⬇️ Button: Speed DOWN");
        }
    }
}

// ==================== DISPLAY FAN STATUS ====================
void displayFanStatus() {
    Serial.println("\n┌────────────────────────────┐");
    Serial.printf("│  Fan: %-4s  Speed: %d/3    │\n", fanOn ? "ON" : "OFF", fanSpeed);
    Serial.println("├────────────────────────────┤");
    
    // Visual speed bar
    Serial.print("│  [");
    for (int i = 1; i <= 3; i++) {
        Serial.print(i <= fanSpeed ? "█" : "░");
    }
    Serial.println("]                    │");
    Serial.println("└────────────────────────────┘\n");
}

// ==================== SETUP ====================
void setup() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("\n╔════════════════════════════════════════╗");
    Serial.println("║     🌀  ESP32 FAN SIMULATOR  🌀         ║");
    Serial.println("║       PWM Speed Control (0-3)          ║");
    Serial.println("║     Smart Home IoT Project - HUST      ║");
    Serial.println("╚════════════════════════════════════════╝\n");
    
    // Setup GPIO pins
    pinMode(LED_SPEED1, OUTPUT);
    pinMode(LED_SPEED2, OUTPUT);
    pinMode(LED_SPEED3, OUTPUT);
    pinMode(BTN_UP, INPUT_PULLUP);
    pinMode(BTN_DOWN, INPUT_PULLUP);
    
    // Setup PWM for fan motor
    ledcSetup(PWM_CHANNEL, PWM_FREQ, PWM_RESOLUTION);
    ledcAttachPin(FAN_PIN, PWM_CHANNEL);
    
    Serial.println("✅ GPIO and PWM initialized");
    
    // Generate device ID from MAC
    uint8_t mac[6];
    WiFi.macAddress(mac);
    char macStr[18];
    sprintf(macStr, "FAN_%02X%02X", mac[4], mac[5]);
    deviceId = String(macStr);
    
    // Setup MQTT topics
    controlTopic = "device/control/" + deviceId;
    dataTopic = "device/data/" + deviceId;
    
    Serial.println("🆔 Device ID: " + deviceId);
    Serial.println("📥 Control topic: " + controlTopic);
    Serial.println("📤 Data topic: " + dataTopic);
    
    // Connect WiFi
    setupWiFi();
    
    // Setup MQTT
    mqtt.setServer(MQTT_BROKER, MQTT_PORT);
    mqtt.setCallback(mqttCallback);
    mqtt.setBufferSize(512);
    
    // Initialize fan state
    updateFanOutput();
    
    Serial.println("\n🚀 Setup complete! Starting main loop...\n");
    Serial.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
}

// ==================== LOOP ====================
void loop() {
    // Maintain MQTT connection
    if (!mqtt.connected()) {
        reconnectMQTT();
    }
    mqtt.loop();
    
    // Handle physical buttons
    handleButtons();
    
    // Publish state periodically
    if (millis() - lastPublish >= PUBLISH_INTERVAL) {
        lastPublish = millis();
        publishState();
        displayFanStatus();
    }
}
