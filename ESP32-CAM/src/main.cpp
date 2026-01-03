#include <Arduino.h>
#include "esp_camera.h"
#include "ConfigManager.h"
#include "WifiManager.h"
#include "MqttManager.h"
#include "LedManager.h"
#include "WebServerManager.h"

// Default AP IP Address: 192.168.4.1  (:8080 để kết nối wifi)
// Connect to WiFi "ESP32-CAM-Setup" and go to http://192.168.4.1 to configure.

// Pin definition for CAMERA_MODEL_AI_THINKER
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

#define WHITE_LED_PIN 4
#define RED_LED_PIN 33 // Pin cho đèn Flash trắng

ConfigManager configManager;
WifiManager wifiManager(configManager);
LedManager ledManager(WHITE_LED_PIN);
MqttManager mqttManager(configManager, ledManager);
WebServerManager webServerManager;

unsigned long lastMsg = 0;
unsigned long lastBlink = 0;
unsigned long blinkInterval = 500; // Blink every 500ms
bool isCameraServerStarted = false; // Biến cờ để theo dõi trạng thái Camera Server

void initCamera() {
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sccb_sda = SIOD_GPIO_NUM;
    config.pin_sccb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;

    // if PSRAM IC present, init with UXGA resolution and higher compression
    if(psramFound()){
        config.frame_size = FRAMESIZE_QVGA;  // 320x240 - Nhanh hơn nhiều, đủ cho YOLO detection
        config.jpeg_quality = 12;            // 10-63, thấp hơn = ít nén hơn = nhanh hơn
        config.fb_count = 2;                 // 2 buffer đủ cho streaming (2 frame trong RAM)
    } else {
        config.frame_size = FRAMESIZE_QVGA;  // 320x240 - Nhẹ hơn nếu không có PSRAM
        config.jpeg_quality = 15;
        config.fb_count = 1;
    }

    Serial.printf("Frame size: %d\n", config.frame_size);
    Serial.printf("JPEG quality: %d\n", config.jpeg_quality);
    Serial.printf("FB count: %d\n", config.fb_count);

    // camera init
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Camera init failed with error 0x%x", err);
        return;
    }
}

void setup() {
    Serial.begin(115200);

    pinMode(RED_LED_PIN, OUTPUT); // Cấu hình LED đỏ (Pin 33) ngay từ đầu
    ledManager.begin();
    ledManager.off(); 
    
    // Initialize Config
    configManager.begin();

    // Initialize WiFi (AP + STA)
    wifiManager.begin();

    // Initialize Camera
    initCamera();

    // Initialize MQTT
    mqttManager.begin();

    Serial.println("Set up successfully!");
}

void loop() {
    // Handle Web Server and WiFi connection
    wifiManager.loop();

    // Only run MQTT if WiFi is connected
    if (wifiManager.isConnected()) {
        // Nếu đã có WiFi mà Camera Server chưa bật thì bật nó lên
        if (!isCameraServerStarted) {
            webServerManager.begin();
            isCameraServerStarted = true;
        }

        digitalWrite(RED_LED_PIN, HIGH); // Tắt đèn đỏ (Pin 33) khi đã kết nối (HIGH là tắt)
        mqttManager.loop();

        // Publish device state every 10 seconds
        unsigned long now = millis();
        if (now - lastMsg > 10000) {
            lastMsg = now;
            mqttManager.publishDeviceStateForLight();
            mqttManager.publishDeviceStateForCamera();
        }
    } else {
        // Blink LED when not connected
        unsigned long now = millis();
        if (now - lastBlink > blinkInterval) {
            lastBlink = now;
            static bool led33State = false;
            led33State = !led33State;
            digitalWrite(33, led33State ? LOW : HIGH); // Nháy đèn đỏ (Pin 33)
        }
    }
}