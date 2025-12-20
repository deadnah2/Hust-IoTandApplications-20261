#include <Arduino.h>
#include "ConfigManager.h"
#include "WifiManager.h"
#include "MqttManager.h"

// Default AP IP Address: 192.168.4.1
// Connect to WiFi "ESP32-CAM-Setup" and go to http://192.168.4.1 to configure.

ConfigManager configManager;
WifiManager wifiManager(configManager); // Pass configManager to WifiManager
MqttManager mqttManager(configManager);

unsigned long lastMsg = 0;

void setup() {
    Serial.begin(115200);
    
    // Initialize Config
    configManager.begin();

    // Initialize WiFi (AP + STA)
    wifiManager.begin();

    // Initialize MQTT
    mqttManager.begin();
}

void loop() {
    // Handle Web Server and WiFi connection
    wifiManager.loop();

    // Only run MQTT if WiFi is connected
    if (wifiManager.isConnected()) {
        mqttManager.loop();

        // Example: Publish data every 10 seconds
        unsigned long now = millis();
        if (now - lastMsg > 10000) {
            lastMsg = now;
            
            // Create a dummy data packet
            String mac = wifiManager.getMacAddress();
            String data = "{\"uptime\":" + String(millis()) + ", \"rssi\":" + String(WiFi.RSSI()) + "}";
            
            mqttManager.publishData(mac, data);
        }
    }
}