#ifndef WIFI_MANAGER_H
#define WIFI_MANAGER_H

#include <WiFi.h>
#include <WebServer.h>
#include "ConfigManager.h"

class WifiManager {
public:
    WifiManager(ConfigManager &configManager);
    void begin();
    void loop();
    bool isConnected();
    String getMacAddress();
    String getBSSID();

private:
    ConfigManager &configManager;
    WebServer server;
    bool connected;

    void setupAP();
    bool connectToWifi(const AppConfig &config);
    void handleRoot();
    void handleSave();
};

#endif
