#include "ConfigManager.h"

// Preference: lưu trữ dữ liệu cấu hình vào bộ nhớ flash.

ConfigManager::ConfigManager() {}

void ConfigManager::begin() {
    preferences.begin("smarthome", false); // smarthome là namespace (phục vụ quá trình đọc/ghi); false = read/write
}

AppConfig ConfigManager::loadConfig() {
    AppConfig config;
    config.wifi_ssid = preferences.getString("ssid", "");
    config.wifi_pass = preferences.getString("pass", "");
    config.mqtt_server = preferences.getString("mqtt_server", "");
    config.mqtt_port = preferences.getInt("mqtt_port", 1883);
    config.mqtt_user = preferences.getString("mqtt_user", "");
    config.mqtt_pass = preferences.getString("mqtt_pass", "");
    config.config_saved = preferences.getBool("saved", false);
    return config;
}

void ConfigManager::saveConfig(const AppConfig &config) {
    preferences.putString("ssid", config.wifi_ssid);
    preferences.putString("pass", config.wifi_pass);
    preferences.putString("mqtt_server", config.mqtt_server);
    preferences.putInt("mqtt_port", config.mqtt_port);
    preferences.putString("mqtt_user", config.mqtt_user);
    preferences.putString("mqtt_pass", config.mqtt_pass);
    preferences.putBool("saved", true);
}

void ConfigManager::clearConfig() {
    preferences.clear();
}
