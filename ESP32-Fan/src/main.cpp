/*
 * ESP32 Fan Simulator - PWM Speed Control
 * Kết nối qua Ngrok để giao tiếp với MQTT broker local
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

// Hardware
#define FAN_PIN 18      // PWM output (simulate motor)
#define LED_SPEED1 25
#define LED_SPEED2 26
#define LED_SPEED3 27
#define BTN_UP 19
#define BTN_DOWN 21

// WiFi
const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASS = "";

// MQTT (ngrok)
const char* MQTT_BROKER = "0.tcp.ap.ngrok.io";
const int MQTT_PORT = 14752;

// BSSID for device discovery
const char* WIFI_BSSID = "e4:77:27:ce:78:ac";

// Objects
WiFiClient espClient;
PubSubClient mqtt(espClient);

// State
String deviceId;
String controlTopic;
String dataTopic;

bool fanOn = false;
int fanSpeed = 0;  // 0 = OFF, 1-3 = speed levels

unsigned long lastPublish = 0;
unsigned long lastButton = 0;
const unsigned long PUBLISH_INTERVAL = 1500;
const unsigned long DEBOUNCE = 200;

// PWM config
const int PWM_CHANNEL = 0;
const int PWM_FREQ = 5000;
const int PWM_RESOLUTION = 8;

// Cập nhật FAN output và LED trạng thái
void updateFanOutput() {
    // Giá trị PWM tương ứng với tốc độ quạt
    int pwmValues[] = {0, 85, 170, 255};
    ledcWrite(PWM_CHANNEL, pwmValues[fanSpeed]);

    digitalWrite(LED_SPEED1, fanSpeed >= 1 ? HIGH : LOW);
    digitalWrite(LED_SPEED2, fanSpeed >= 2 ? HIGH : LOW);
    digitalWrite(LED_SPEED3, fanSpeed >= 3 ? HIGH : LOW);

    Serial.printf("Fan %s | Speed %d/3\r\n", fanOn ? "ON" : "OFF", fanSpeed);
}

void publishState() {
    StaticJsonDocument<200> doc;
    doc["status"] = fanOn ? "ON" : "OFF";
    doc["speed"] = fanSpeed;
    doc["uptime"] = millis() / 1000;
    doc["rssi"] = WiFi.RSSI();

    char buffer[256];
    serializeJson(doc, buffer);
    mqtt.publish(dataTopic.c_str(), buffer);

    Serial.printf("State %s speed=%d\r\n", fanOn ? "ON" : "OFF", fanSpeed);
}

void setFanSpeed(int speed) {
    fanSpeed = constrain(speed, 0, 3);
    fanOn = (fanSpeed > 0);
    updateFanOutput();
    publishState();
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    Serial.printf("MQTT [%s]\n", topic);

    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, payload, length);

    if (error) {
        Serial.printf("JSON error: %s\n", error.c_str());
        return;
    }

    const char* action = doc["action"] | "";

    if (strcmp(action, "ON") == 0) {
        fanOn = true;
        if (fanSpeed == 0) fanSpeed = 1;
        updateFanOutput();
        publishState();
        Serial.println("Fan ON");

    } else if (strcmp(action, "OFF") == 0) {
        fanOn = false;
        fanSpeed = 0;
        updateFanOutput();
        publishState();
        Serial.println("Fan OFF");

    } else if (strcmp(action, "SET_SPEED") == 0) {
        int newSpeed = doc["speed"] | fanSpeed;
        setFanSpeed(newSpeed);
        Serial.printf("Speed %d\n", fanSpeed);

    } else {
        Serial.printf("Unknown action: %s\n", action);
    }
}

void setupWiFi() {
    Serial.print("WiFi");
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASS);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 60) {
        delay(500);
        Serial.print(".");
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nWiFi connected");
        Serial.println("IP: " + WiFi.localIP().toString());
    } else {
        Serial.println("\nWiFi failed");
    }
}

// Đăng ký thiết bị lên broker
void registerDevice() {
    StaticJsonDocument<256> doc;
    doc["type"] = "FAN";
    doc["name"] = "Smart Fan";
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
        String clientId = "Fan-" + deviceId;

        if (mqtt.connect(clientId.c_str())) {
            Serial.println(" ok");
            mqtt.subscribe(controlTopic.c_str());
            registerDevice();
            return;

        } else {
            Serial.printf(" fail (rc=%d). Retry in 3s...\n", mqtt.state());
            delay(3000);
            attempts++;
        }
    }
}

void handleButtons() {
    if (millis() - lastButton < DEBOUNCE) return;

    if (digitalRead(BTN_UP) == LOW) {
        lastButton = millis();
        if (fanSpeed < 3) {
            setFanSpeed(fanSpeed + 1);
            Serial.println("Speed UP");
        }
    }

    if (digitalRead(BTN_DOWN) == LOW) {
        lastButton = millis();
        if (fanSpeed > 0) {
            setFanSpeed(fanSpeed - 1);
            Serial.println("Speed DOWN");
        }
    }
}

void displayFanStatus() {
    Serial.printf("Status: %s | Speed: %d/3\r\n", fanOn ? "ON" : "OFF", fanSpeed);
}

void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("\n=== ESP32 FAN ===");
    Serial.println("PWM Speed Control (0-3)");
    Serial.println("Smart Home - HUST");
    Serial.println("-----------------------------");

    // Setup pins
    pinMode(LED_SPEED1, OUTPUT);
    pinMode(LED_SPEED2, OUTPUT);
    pinMode(LED_SPEED3, OUTPUT);
    pinMode(BTN_UP, INPUT_PULLUP);
    pinMode(BTN_DOWN, INPUT_PULLUP);

    ledcSetup(PWM_CHANNEL, PWM_FREQ, PWM_RESOLUTION);
    ledcAttachPin(FAN_PIN, PWM_CHANNEL);

    // Tạo device ID từ MAC address
    uint8_t mac[6];
    WiFi.macAddress(mac);
    char macStr[18];
    sprintf(macStr, "FAN_%02X%02X", mac[4], mac[5]);
    deviceId = String(macStr);

    // Setup MQTT topics
    controlTopic = "device/control/" + deviceId;
    dataTopic = "device/data/" + deviceId;

    Serial.println("ID: " + deviceId);
    Serial.println("Control: " + controlTopic);
    Serial.println("Data: " + dataTopic);

    setupWiFi();
     // Setup MQTT
    mqtt.setServer(MQTT_BROKER, MQTT_PORT);
    mqtt.setCallback(mqttCallback);
    mqtt.setBufferSize(512);

    updateFanOutput();

    Serial.println("Setup done");
    Serial.println("-----------------------------");
}

void loop() {
    if (!mqtt.connected()) {
        reconnectMQTT();
    }
    mqtt.loop();

    handleButtons();

    if (millis() - lastPublish >= PUBLISH_INTERVAL) {
        lastPublish = millis();
        publishState();
        displayFanStatus();
    }
}
