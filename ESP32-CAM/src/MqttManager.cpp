#include "MqttManager.h"

MqttManager* MqttManager::instance = nullptr;

MqttManager::MqttManager(ConfigManager &mgr, LedManager &led) 
    : configManager(mgr), ledManager(led), client(espClient) {
    instance = this;
}

void MqttManager::begin() {
    AppConfig config = configManager.loadConfig();
    if (config.mqtt_server.length() > 0) {
        client.setServer(config.mqtt_server.c_str(), config.mqtt_port);
        client.setCallback(MqttManager::callback);
        deviceMac = WiFi.macAddress();
    }
}

void MqttManager::callback(char* topic, byte* payload, unsigned int length) { // hàm được định nghĩa từ trước
    if (instance != nullptr) {
        instance->handleMqttMessage(topic, payload, length);
    }
}

void MqttManager::handleMqttMessage(char* topic, byte* payload, unsigned int length) {
    Serial.print("Message arrived [");
    Serial.print(topic);
    Serial.print("] ");
    
    // Print raw payload
    char rawPayload[256] = {0};
    memcpy(rawPayload, payload, min(length, 255u));
    Serial.println(rawPayload);

    // Parse JSON
    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, payload, length);

    if (error) {
        Serial.print("JSON parse error: ");
        Serial.println(error.c_str());
        return;
    }

    // Debug: Print JSON keys
    const char* action = doc["action"] | "";
    Serial.print("DEBUG - Parsed action: '");
    Serial.print(action);
    Serial.print("' (length: ");
    Serial.print(strlen(action));
    Serial.println(")");

    // Xử lý lệnh LED
    if (strcmp(action, "LIGHT_ON") == 0) {
        ledManager.on();
        publishDeviceStateForLight();  // ✅ Publish state ngay sau khi thay đổi
        Serial.println("✅ LED ON");

    } else if (strcmp(action, "LIGHT_OFF") == 0) {
        ledManager.off();
        publishDeviceStateForLight();  // ✅ Publish state ngay sau khi thay đổi
        Serial.println("✅ LED OFF");

    } else {
        Serial.print("❌ Unknown action: '");
        Serial.print(action);
        Serial.println("'");
    }
}

void MqttManager::reconnect() {
    AppConfig config = configManager.loadConfig();
    
    // Update server config in case it changed
    if (config.mqtt_server.length() > 0) {
        client.setServer(config.mqtt_server.c_str(), config.mqtt_port);
    }

    // Loop until we're reconnected
    if (!client.connected()) {
        Serial.print("Attempting MQTT connection...");
        String clientId = "ESP32Client-" + deviceMac;
        
        bool connected = false;
        if (config.mqtt_user.length() > 0) {
            connected = client.connect(clientId.c_str(), config.mqtt_user.c_str(), config.mqtt_pass.c_str());
        } else {
            connected = client.connect(clientId.c_str());
        }

        if (connected) {
            Serial.println("connected");
            
            // Subscribe to control channel
            String controlTopic = "device/control/" + deviceMac;
            client.subscribe(controlTopic.c_str());
            Serial.println("Subscribed to: " + controlTopic);

            // Publish device/new for Camera
            String streamUrl = "http://" + WiFi.localIP().toString() + "/stream";
            publishDeviceNew("High quality camera", "CAMERA", WiFi.BSSIDstr(), deviceMac, "ONLINE", streamUrl, "QVGA");
            // Publish device/new for Light (Flash)
            String ledState = ledManager.getState() ? "ON" : "OFF";
            publishDeviceNew("Super bright light", "LIGHT", WiFi.BSSIDstr(), deviceMac, ledState);

        } else {
            Serial.print("failed, rc=");
            Serial.print(client.state());
            Serial.println(" try again in 5 seconds");
            // Wait 5 seconds before retrying (non-blocking in loop would be better but for simplicity)
            // We won't block here to allow other things to run, just return and try next loop
        }
    }
}

void MqttManager::loop() {
    if (!client.connected()) {
        static unsigned long lastReconnectAttempt = 0;
        unsigned long now = millis();
        if (now - lastReconnectAttempt > 5000) {
            lastReconnectAttempt = now;
            reconnect();
        }
    } else {
        client.loop();
    }
}

bool MqttManager::isConnected() {
    return client.connected();
}

void MqttManager::publishDeviceNew(String name, String type, String bssid, String mac, String state, String streamUrl, String cameraResolution) {
    StaticJsonDocument<200> doc;
    doc["name"] = name;
    doc["type"] = type;
    doc["bssid"] = bssid;
    doc["controllerMAC"] = mac;
    doc["state"] = state;
    if (streamUrl.length() > 0) {
        doc["streamUrl"] = streamUrl;
    }
    if (cameraResolution.length() > 0) {
        doc["cameraResolution"] = cameraResolution;
    }


    char buffer[256];
    serializeJson(doc, buffer);

    Serial.println(buffer);
    
    client.publish("device/new", buffer);
}

void MqttManager::publishData(String mac, String dataJson) {
    String topic = "device/data/" + mac;
    client.publish(topic.c_str(), dataJson.c_str());
}

void MqttManager::publishDeviceStateForLight() {
    StaticJsonDocument<256> doc;
    doc["name"] = "Super bright light";
    doc["state"] = ledManager.getState() ? "ON" : "OFF";

    char buffer[300];
    serializeJson(doc, buffer);

    String topic = "device/data/" + deviceMac;
    client.publish(topic.c_str(), buffer);

    Serial.print("Light state published: ");
    Serial.println(buffer);
}

void MqttManager::publishDeviceStateForCamera() {
    StaticJsonDocument<256> doc;
    doc["name"] = "High quality camera";
    doc["state"] = "ON";
    doc["cameraResolution"] = "QVGA";

    char buffer[300];
    serializeJson(doc, buffer);

    String topic = "device/data/" + deviceMac;
    client.publish(topic.c_str(), buffer);

    Serial.print("Camera state published: ");
    Serial.println(buffer);
}