/*
 * ESP32 Sensor Simulator - DHT22
 * Kết nối qua Ngrok để giao tiếp với MQTT broker local
 * MQTT Topics:
 * - Publish: device/new (đăng ký device)
 * - Publish: device/data/{deviceId} (gửi data sensor)
 */

#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

// Hardware
#define DHT_PIN 4
#define DHT_TYPE DHT22
#define STATUS_LED 2

// WiFi
const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASS = "";

// MQTT (ngrok)
const char* MQTT_BROKER = "0.tcp.ap.ngrok.io";
const int MQTT_PORT = 16824;

// BSSID for device discovery
const char* WIFI_BSSID = "e4:77:27:ce:78:ac";

// Objects
WiFiClient espClient;
PubSubClient mqtt(espClient);
DHT dht(DHT_PIN, DHT_TYPE);

// State
String deviceId;
float temperature = 0;
float humidity = 0;

unsigned long lastPublish = 0;
const unsigned long PUBLISH_INTERVAL = 1500;

// WIFI setup
void setupWiFi() {
    Serial.print("WiFi");
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
        Serial.println("\nWiFi connected");
        Serial.println("IP: " + WiFi.localIP().toString());
        digitalWrite(STATUS_LED, HIGH);
    } else {
        Serial.println("\nWiFi failed");
    }
}

// MQTT callback (không dùng với sensor)
void mqttCallback(char* topic, byte* payload, unsigned int length) {
    // Sensor does not handle control messages
    Serial.printf("MQTT [%s]\n", topic);
}

// Đăng ký thiết bị lên broker
void registerDevice() {
    StaticJsonDocument<256> doc;
    doc["type"] = "SENSOR";
    doc["name"] = "Temperature & Humidity Sensor";
    doc["bssid"] = WIFI_BSSID;
    doc["controllerMAC"] = deviceId;
    doc["state"] = "online";

    char buffer[300];
    serializeJson(doc, buffer);
    mqtt.publish("device/new", buffer);

    Serial.println("Registered: " + deviceId);
}

// Kết nối lại MQTT nếu bị ngắt
void reconnectMQTT() {
    int attempts = 0;
    while (!mqtt.connected() && attempts < 5) {
        Serial.print("MQTT connect...");
        String clientId = "Sensor-" + deviceId;

        if (mqtt.connect(clientId.c_str())) {
            Serial.println(" ok");
            registerDevice();
            return;
        } else {
            Serial.printf(" fail (rc=%d). Retry in 3s...\n", mqtt.state());
            delay(3000);
            attempts++;
        }
    }
}

// Đọc dữ liệu từ DHT22 và gửi lên MQTT
void readAndPublish() {
    float t = dht.readTemperature();
    float h = dht.readHumidity();

    if (!isnan(t) && !isnan(h)) {
        temperature = t;
        humidity = h;
    }

    // Blink LED for activity
    digitalWrite(STATUS_LED, LOW);
    delay(100);
    digitalWrite(STATUS_LED, HIGH);

    StaticJsonDocument<200> doc;
    doc["temperature"] = temperature;
    doc["humidity"] = humidity;
    doc["uptime"] = millis() / 1000;
    doc["rssi"] = WiFi.RSSI();

    char buffer[256];
    serializeJson(doc, buffer);

    String topic = "device/data/" + deviceId;
    mqtt.publish(topic.c_str(), buffer);

    Serial.printf("Temp: %.1f C | Hum: %.1f %%\r\n", temperature, humidity);
}

void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("\n=== ESP32 SENSOR ===");
    Serial.println("DHT22 Temperature & Humidity");
    Serial.println("Smart Home - HUST");
    Serial.println("-----------------------------");

    // Setup LED
    pinMode(STATUS_LED, OUTPUT);
    digitalWrite(STATUS_LED, LOW);

    dht.begin();
    Serial.println("DHT22 ready");

    // Tạo device ID từ MAC address
    uint8_t mac[6];
    WiFi.macAddress(mac);
    char macStr[18];
    sprintf(macStr, "SENSOR_%02X%02X", mac[4], mac[5]);
    deviceId = String(macStr);
    Serial.println("ID: " + deviceId);

    setupWiFi();

    // Setup MQTT
    mqtt.setServer(MQTT_BROKER, MQTT_PORT);
    mqtt.setCallback(mqttCallback);

    Serial.println("\nSetup done\n");
    Serial.println("-----------------------------");
}

void loop() {
    if (!mqtt.connected()) {
        reconnectMQTT();
    }
    mqtt.loop();

    if (millis() - lastPublish >= PUBLISH_INTERVAL) {
        lastPublish = millis();
        readAndPublish();
    }
}
