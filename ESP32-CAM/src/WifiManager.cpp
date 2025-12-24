#include "WifiManager.h"

// HTML Page for Configuration
const char* htmlPage = R"rawliteral(
<!DOCTYPE HTML><html>
<head>
  <title>ESP32-CAM Config</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: Arial; text-align: center; margin: 20px; }
    input { width: 90%; padding: 10px; margin: 5px 0; }
    button { padding: 10px 20px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }
    .container { max-width: 400px; margin: auto; }
  </style>
</head>
<body>
  <div class="container">
    <h2>ESP32-CAM Configuration</h2>
    <form action="/save" method="POST">
      <input type="text" name="ssid" placeholder="WiFi SSID" required><br>
      <input type="password" name="pass" placeholder="WiFi Password"><br>
      <input type="text" name="mqtt_server" placeholder="MQTT Server IP" required><br>
      <input type="number" name="mqtt_port" placeholder="MQTT Port (1883)" value="1883"><br>
      <input type="text" name="mqtt_user" placeholder="MQTT User"><br>
      <input type="password" name="mqtt_pass" placeholder="MQTT Password"><br>
      <button type="submit">Send</button>
    </form>
  </div>
</body>
</html>
)rawliteral";

WifiManager::WifiManager(ConfigManager &mgr) : configManager(mgr), server(8080), connected(false) {}

void WifiManager::begin() { // 
    // 1. Enable both AP and STA
    WiFi.mode(WIFI_AP_STA);
    
    // 2. Setup AP
    setupAP();

    // 3. Check stored config
    AppConfig config = configManager.loadConfig(); // load saved config
    if (config.config_saved) {
        Serial.println("Found saved config, trying to connect...");
        if (connectToWifi(config)) {
            Serial.println("Connected to WiFi!");
        } else {
            Serial.println("Failed to connect with saved config.");
        }
    } else {
        Serial.println("No saved config.");
    }

    // 4. Setup Web Server
    server.on("/", HTTP_GET, std::bind(&WifiManager::handleRoot, this)); // gắn handler
    server.on("/save", HTTP_POST, std::bind(&WifiManager::handleSave, this));
    server.begin();
    Serial.println("Web Server started.");
}

// Các hàm bên dưới phục vụ cho begin()

void WifiManager::setupAP() {
    // Default AP Name
    const char* ssid = "ESP32-CAM-Setup";
    // No password for AP
    WiFi.softAP(ssid);
    
    IPAddress IP = WiFi.softAPIP();
    Serial.print("AP IP address: ");
    Serial.println(IP);
    Serial.println("Config Page: http://192.168.4.1:8080");
}

bool WifiManager::connectToWifi(const AppConfig &config) {
    if (config.wifi_ssid.length() == 0) return false;

    Serial.printf("Connecting to %s...\n", config.wifi_ssid.c_str());
    WiFi.begin(config.wifi_ssid.c_str(), config.wifi_pass.c_str());

    int retries = 0;
    while (WiFi.status() != WL_CONNECTED && retries < 20) {
        delay(500);
        Serial.print(".");
        retries++;
    }
    Serial.println();

    if (WiFi.status() == WL_CONNECTED) {
        connected = true;
        Serial.print("WiFi connected. IP: ");
        Serial.println(WiFi.localIP());
        return true;
    } else {
        connected = false;
        return false;
    }
}

void WifiManager::handleRoot() {
    server.send(200, "text/html", htmlPage);
}

void WifiManager::handleSave() {
    if (server.hasArg("ssid") && server.hasArg("mqtt_server")) {
        AppConfig config;
        config.wifi_ssid = server.arg("ssid");
        config.wifi_pass = server.arg("pass");
        config.mqtt_server = server.arg("mqtt_server");
        config.mqtt_port = server.arg("mqtt_port").toInt();
        config.mqtt_user = server.arg("mqtt_user");
        config.mqtt_pass = server.arg("mqtt_pass");
        
        Serial.println("Received new config via Web.");

        Serial.println("ssid: " + config.wifi_ssid);
        Serial.println("pass: " + config.wifi_pass);
        Serial.println("mqtt_server: " + config.mqtt_server);
        Serial.println("mqtt_port: " + String(config.mqtt_port));
        Serial.println("mqtt_user: " + config.mqtt_user);
        Serial.println("mqtt_pass: " + config.mqtt_pass);
        
        // Try to connect first
        if (connectToWifi(config)) {
            configManager.saveConfig(config);
            String message = "<h1>Connected Successfully!</h1><p>IP: " + WiFi.localIP().toString() + "</p><p>Device is ready.</p><a href='/'>Back</a>";
            server.send(200, "text/html", message);
        } else {
            server.send(200, "text/html", "<h1>Connection Failed</h1><p>Please check your credentials and try again.</p><a href='/'>Back</a>");
        }
    } else {
        server.send(400, "text/plain", "Missing arguments");
    }
}

void WifiManager::loop() {
    server.handleClient();
    // Reconnect logic could be added here if needed, but for now we rely on initial connection or user intervention
}

bool WifiManager::isConnected() {
    return WiFi.status() == WL_CONNECTED;
}

String WifiManager::getMacAddress() {
    return WiFi.macAddress();
}

String WifiManager::getBSSID() {
    return WiFi.BSSIDstr();
}
