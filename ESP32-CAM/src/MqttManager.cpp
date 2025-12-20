#include "MqttManager.h"

MqttManager::MqttManager(ConfigManager &mgr) : configManager(mgr), client(espClient) {}

void MqttManager::begin() {
    AppConfig config = configManager.loadConfig();
    if (config.mqtt_server.length() > 0) {
        client.setServer(config.mqtt_server.c_str(), config.mqtt_port);
        client.setCallback(MqttManager::callback);
        deviceMac = WiFi.macAddress();
    }
}

void MqttManager::callback(char* topic, byte* payload, unsigned int length) {
    Serial.print("Message arrived [");
    Serial.print(topic);
    Serial.print("] ");
    for (unsigned int i = 0; i < length; i++) {
        Serial.print((char)payload[i]);
    }
    Serial.println();
    // Handle control messages here if needed
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
            publishDeviceNew("Cam", WiFi.BSSIDstr(), deviceMac, "online");
            // Publish device/new for Light (Flash)
            publishDeviceNew("Light", WiFi.BSSIDstr(), deviceMac, "online");

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

void MqttManager::publishDeviceNew(String type, String bssid, String mac, String status) {
    StaticJsonDocument<200> doc;
    doc["type"] = type;
    doc["bssid"] = bssid;
    doc["controllerDeviceMAC"] = mac;
    doc["status"] = status;

    char buffer[256];
    serializeJson(doc, buffer);
    
    client.publish("device/new", buffer);
}

void MqttManager::publishData(String mac, String dataJson) {
    String topic = "device/data/" + mac;
    client.publish(topic.c_str(), dataJson.c_str());
}
