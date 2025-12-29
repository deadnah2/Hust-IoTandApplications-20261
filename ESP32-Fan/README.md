# ESP32 Fan Simulator (Wokwi)

Mô phỏng quạt thông minh với điều khiển PWM 4 mức tốc độ (0-3) cho Smart Home IoT Project.

## Sơ đồ mạch

```
                    ┌─────────────────┐
                    │   ESP32 DevKit  │
                    │                 │
    ┌───────┐       │  GPIO 18 ──────┼──── FAN Motor (PWM LED Blue)
    │  FAN  │───────┤                │
    │ Motor │       │  GPIO 25 ──────┼──── Speed LED 1 (Green)
    └───────┘       │  GPIO 26 ──────┼──── Speed LED 2 (Yellow)
                    │  GPIO 27 ──────┼──── Speed LED 3 (Red)
    ┌───────┐       │                │
    │  UP   │───────┤  GPIO 19 ──────┼──── Button UP (Green)
    └───────┘       │                │
    ┌───────┐       │  GPIO 21 ──────┼──── Button DOWN (Red)
    │ DOWN  │───────┤                │
    └───────┘       │  GND ──────────┼──── Common GND
                    └─────────────────┘
```

## Linh kiện (Wokwi)

| Linh kiện | Số lượng | GPIO | Chức năng |
|-----------|----------|------|-----------|
| ESP32 DevKit C V4 | 1 | - | Controller |
| LED (Blue) | 1 | GPIO 18 | Fan Motor (PWM) |
| LED (Green) | 1 | GPIO 25 | Speed Level 1 |
| LED (Yellow) | 1 | GPIO 26 | Speed Level 2 |
| LED (Red) | 1 | GPIO 27 | Speed Level 3 |
| Push Button (Green) | 1 | GPIO 19 | Speed UP |
| Push Button (Red) | 1 | GPIO 21 | Speed DOWN |
| Resistor 220Ω | 4 | LEDs | Current limiting |

## MQTT Topics

| Topic | Direction | Description |
|-------|-----------|-------------|
| `device/new` | Publish | Đăng ký device khi khởi động |
| `device/data/{deviceId}` | Publish | Gửi trạng thái (5s/lần) |
| `device/control/{deviceId}` | Subscribe | Nhận lệnh điều khiển |

### Payload đăng ký device
```json
{
  "type": "FAN",
  "name": "Smart Fan",
  "bssid": "XX:XX:XX:XX:XX:XX",
  "controllerMAC": "FAN_XXXX",
  "state": "online"
}
```

### Payload trạng thái
```json
{
  "status": "ON",
  "speed": 2,
  "uptime": 1234,
  "rssi": -45
}
```

### Commands (Gửi đến device/control/{deviceId})
```json
{"action": "ON"}
{"action": "OFF"}
{"action": "SET_SPEED", "speed": 2}
```

## Tốc độ quạt

| Speed | PWM | LED Indicators | Description |
|-------|-----|----------------|-------------|
| 0 | 0% | ○ ○ ○ | OFF |
| 1 | 33% | ● ○ ○ | Low |
| 2 | 66% | ● ● ○ | Medium |
| 3 | 100% | ● ● ● | High |

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

## Điều khiển

### Từ Wokwi (Physical Buttons)
- Nhấn nút **UP** (xanh): Tăng tốc độ
- Nhấn nút **DOWN** (đỏ): Giảm tốc độ

### Từ Backend (MQTT)
```bash
# Bật quạt
mosquitto_pub -h localhost -p 1883 -t "device/control/FAN_0110" -m '{"action":"ON"}'

# Tắt quạt
mosquitto_pub -h localhost -p 1883 -t "device/control/FAN_0110" -m '{"action":"OFF"}'

# Đặt tốc độ 2
mosquitto_pub -h localhost -p 1883 -t "device/control/FAN_0110" -m '{"action":"SET_SPEED","speed":2}'
```

## Output mẫu

```
╔════════════════════════════════════════╗
║     🌀  ESP32 FAN SIMULATOR  🌀         ║
║       PWM Speed Control (0-3)          ║
║     Smart Home IoT Project - HUST      ║
╚════════════════════════════════════════╝

✅ GPIO and PWM initialized
🆔 Device ID: FAN_0110
📥 Control topic: device/control/FAN_0110
📤 Data topic: device/data/FAN_0110
📶 Connecting to WiFi...
✅ WiFi connected!
🔌 Connecting to MQTT... connected!
📥 Subscribed: device/control/FAN_0110
📤 Device registered: FAN_0110

📩 Command received [device/control/FAN_0110]
   Data: {"action":"ON"}
✅ Fan turned ON
🌀 Fan: ON | Speed: 1/3

┌────────────────────────────┐
│  Fan: ON    Speed: 1/3    │
├────────────────────────────┤
│  [█░░]                    │
└────────────────────────────┘
```

## Files

```
ESP32-Fan/
├── platformio.ini      # PlatformIO config
├── wokwi.toml          # Wokwi simulator config
├── diagram.json        # Sơ đồ mạch Wokwi
├── README.md           # File này
└── src/
    └── main.cpp        # Code chính
```
