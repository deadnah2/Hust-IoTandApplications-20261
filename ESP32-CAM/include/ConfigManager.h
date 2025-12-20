#ifndef CONFIG_MANAGER_H
#define CONFIG_MANAGER_H

#include <Arduino.h>
#include <Preferences.h>

struct AppConfig {
    String wifi_ssid;
    String wifi_pass;
    String mqtt_server;
    int mqtt_port;
    String mqtt_user;
    String mqtt_pass;
    bool config_saved;
};

class ConfigManager {
public:
    ConfigManager();
    void begin();
    AppConfig loadConfig();
    void saveConfig(const AppConfig &config);
    void clearConfig();

private:
    Preferences preferences;
};

#endif
