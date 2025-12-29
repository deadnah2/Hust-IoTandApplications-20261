/*
 * ESP32 Sensor Simulator - DHT22 (Temperature & Humidity)
 * Smart Home IoT Project - HUST
 * 
 * Kết nối qua Ngrok để giao tiếp với MQTT broker local
 * 
 * Hardware (Wokwi):
 * - DHT22 on GPIO 4
 * - Status LED on GPIO 2 (built-in)
 * 
 * MQTT Topics:
 * - Publish: device/new (đăng ký device)
 * - Publish: device/data/{deviceId} (gửi data sensor)
 */

#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

// ==================== HARDWARE CONFIG ====================
#define DHT_PIN         4
#define DHT_TYPE        DHT22
#define STATUS_LED      2

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
DHT dht(DHT_PIN, DHT_TYPE);

// ==================== STATE ====================
String deviceId;
float temperature = 0;
float humidity = 0;

unsigned long lastPublish = 0;
const unsigned long PUBLISH_INTERVAL = 5000;  // 5 giây

// ==================== WIFI ====================
void setupWiFi() {
    Serial.print("📶 Connecting to WiFi");
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 60) {
        delay(500);
        Serial.print(".");
        digitalWrite(STATUS_LED, !digitalRead(STATUS_LED));
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n✅ WiFi connected!");
        Serial.println("   IP: " + WiFi.localIP().toString());
        digitalWrite(STATUS_LED, HIGH);
    } else {
        Serial.println("\n❌ WiFi connection failed!");
    }
}

// ==================== MQTT CALLBACK ====================
void mqttCallback(char* topic, byte* payload, unsigned int length) {
    // Sensor không cần nhận lệnh điều khiển
    Serial.printf("📩 Message on [%s]\n", topic);
}

// ==================== REGISTER DEVICE ====================
void registerDevice() {
    StaticJsonDocument<256> doc;
    doc["type"] = "SENSOR";
    doc["name"] = "Temperature & Humidity Sensor";
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
        String clientId = "Sensor-" + deviceId;
        
        if (mqtt.connect(clientId.c_str())) {
            Serial.println(" connected!");
            registerDevice();
            return;
        } else {
            Serial.printf(" failed (rc=%d). Retry in 3s...\n", mqtt.state());
            delay(3000);
            attempts++;
        }
    }
}

// ==================== READ & PUBLISH SENSOR DATA ====================
void readAndPublish() {
    // Read sensor
    float t = dht.readTemperature();
    float h = dht.readHumidity();
    
    if (!isnan(t) && !isnan(h)) {
        temperature = t;
        humidity = h;
    }
    
    // Blink LED to indicate activity
    digitalWrite(STATUS_LED, LOW);
    delay(100);
    digitalWrite(STATUS_LED, HIGH);
    
    // Create JSON payload
    StaticJsonDocument<200> doc;
    doc["temperature"] = temperature;
    doc["humidity"] = humidity;
    doc["uptime"] = millis() / 1000;
    doc["rssi"] = WiFi.RSSI();
    
    char buffer[256];
    serializeJson(doc, buffer);
    
    // Publish to device/data/{deviceId}
    String topic = "device/data/" + deviceId;
    mqtt.publish(topic.c_str(), buffer);
    
    Serial.printf("🌡️  Temp: %.1f°C | 💧 Humidity: %.1f%% → Published\n", temperature, humidity);
}

// ==================== SETUP ====================
void setup() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("\n╔════════════════════════════════════════╗");
    Serial.println("║   🌡️  ESP32 SENSOR SIMULATOR  🌡️        ║");
    Serial.println("║     DHT22 Temperature & Humidity       ║");
    Serial.println("║     Smart Home IoT Project - HUST      ║");
    Serial.println("╚════════════════════════════════════════╝\n");
    
    // Setup LED
    pinMode(STATUS_LED, OUTPUT);
    digitalWrite(STATUS_LED, LOW);
    
    // Initialize DHT sensor
    dht.begin();
    Serial.println("✅ DHT22 sensor initialized");
    
    // Generate device ID from MAC
    uint8_t mac[6];
    WiFi.macAddress(mac);
    char macStr[18];
    sprintf(macStr, "SENSOR_%02X%02X", mac[4], mac[5]);
    deviceId = String(macStr);
    Serial.println("🆔 Device ID: " + deviceId);
    
    // Connect WiFi
    setupWiFi();
    
    // Setup MQTT
    mqtt.setServer(MQTT_BROKER, MQTT_PORT);
    mqtt.setCallback(mqttCallback);
    
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
    
    // Publish sensor data periodically
    if (millis() - lastPublish >= PUBLISH_INTERVAL) {
        lastPublish = millis();
        readAndPublish();
    }
}
