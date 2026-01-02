#ifndef MQTT_MANAGER_H
#define MQTT_MANAGER_H

#include <PubSubClient.h>
#include <WiFi.h>
#include <ArduinoJson.h>
#include "ConfigManager.h"
#include "LedManager.h"

class MqttManager {
public:
    MqttManager(ConfigManager &configManager, LedManager &ledManager);
    void begin();
    void loop();
    bool isConnected();
    void publishDeviceNew(String name, String type, String bssid, String mac, String state, String streamUrl = "");
    void publishData(String mac, String dataJson);
    void publishDeviceStateForLight();
    void publishDeviceStateForCamera();

private:
    ConfigManager &configManager;
    LedManager &ledManager;
    WiFiClient espClient;
    PubSubClient client;
    String deviceMac;
    
    void reconnect();
    static void callback(char* topic, byte* payload, unsigned int length);
    
    static MqttManager* instance;
    void handleMqttMessage(char* topic, byte* payload, unsigned int length);
};

#endif
