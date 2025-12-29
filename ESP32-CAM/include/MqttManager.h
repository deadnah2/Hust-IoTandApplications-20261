#ifndef MQTT_MANAGER_H
#define MQTT_MANAGER_H

#include <PubSubClient.h>
#include <WiFi.h>
#include <ArduinoJson.h>
#include "ConfigManager.h"

class MqttManager {
public:
    MqttManager(ConfigManager &configManager);
    void begin();
    void loop();
    bool isConnected();
    void publishDeviceNew(String name, String type, String bssid, String mac, String status);
    void publishData(String mac, String dataJson);

private:
    ConfigManager &configManager;
    WiFiClient espClient;
    PubSubClient client;
    String deviceMac;
    
    void reconnect();
    static void callback(char* topic, byte* payload, unsigned int length);
};

#endif
