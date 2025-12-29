# ESP32 Sensor Simulator (Wokwi)

Mô phỏng cảm biến nhiệt độ và độ ẩm DHT22 cho Smart Home IoT Project.

## Sơ đồ mạch

```
                    ┌─────────────────┐
                    │   ESP32 DevKit  │
                    │                 │
    ┌───────┐       │  GPIO 4 ←──────┼──── DHT22 DATA
    │ DHT22 │───────┤                │
    │       │       │  GPIO 2 ───────┼──── Status LED (Built-in)
    └───────┘       │                 │
                    │  3V3 ──────────┼──── VCC (DHT22)
                    │  GND ──────────┼──── GND (DHT22, LED)
                    └─────────────────┘
```

## Linh kiện (Wokwi)

| Linh kiện | Số lượng | GPIO |
|-----------|----------|------|
| ESP32 DevKit C V4 | 1 | - |
| DHT22 | 1 | GPIO 4 |
| LED (Green) | 1 | GPIO 2 |
| Resistor 220Ω | 1 | LED |

## MQTT Topics

| Topic | Direction | Description |
|-------|-----------|-------------|
| `device/new` | Publish | Đăng ký device khi khởi động |
| `device/data/{deviceId}` | Publish | Gửi dữ liệu sensor (5s/lần) |

### Payload đăng ký device
```json
{
  "type": "SENSOR",
  "name": "Temperature & Humidity Sensor",
  "bssid": "XX:XX:XX:XX:XX:XX",
  "controllerMAC": "SENSOR_XXXX",
  "state": "online"
}
```

### Payload data sensor
```json
{
  "temperature": 26.5,
  "humidity": 65.0,
  "uptime": 1234,
  "rssi": -45
}
```

## Cách chạy

### 1. Setup Ngrok (một lần)
```powershell
# Cài đặt
winget install ngrok

# Đăng ký tại ngrok.com và lấy authtoken
ngrok config add-authtoken YOUR_TOKEN
```

### 2. Chạy MQTT Broker
```powershell
cd d:\huibeta\iotprj\Hust-IoTandApplications-20261\backend
docker-compose up -d mqtt
```

### 3. Expose MQTT qua Ngrok
```powershell
ngrok tcp 1883
# Ghi nhớ URL: tcp://0.tcp.ap.ngrok.io:XXXXX
```

### 4. Cập nhật code
Mở `src/main.cpp`, thay đổi:
```cpp
const char* MQTT_BROKER = "0.tcp.ap.ngrok.io";  // hostname từ ngrok
const int MQTT_PORT = XXXXX;                     // port từ ngrok
```

### 5. Chạy Wokwi
- Mở VS Code trong thư mục này
- Nhấn `F1` → `Wokwi: Start Simulator`
- Xem Serial Monitor

## Output mẫu

```
╔════════════════════════════════════════╗
║   🌡️  ESP32 SENSOR SIMULATOR  🌡️        ║
║     DHT22 Temperature & Humidity       ║
║     Smart Home IoT Project - HUST      ║
╚════════════════════════════════════════╝

✅ DHT22 sensor initialized
🆔 Device ID: SENSOR_0110
📶 Connecting to WiFi...
✅ WiFi connected!
   IP: 10.10.0.2
🔌 Connecting to MQTT... connected!
📤 Device registered: SENSOR_0110

🌡️  Temp: 26.0°C | 💧 Humidity: 65.0% → Published
🌡️  Temp: 26.2°C | 💧 Humidity: 64.5% → Published
```

## Files

```
ESP32-Sensor/
├── platformio.ini      # PlatformIO config
├── wokwi.toml          # Wokwi simulator config
├── diagram.json        # Sơ đồ mạch Wokwi
├── README.md           # File này
└── src/
    └── main.cpp        # Code chính
```
