# Hướng dẫn Setup Ngrok cho Smart Home IoT Project

## Tổng quan

Ngrok được sử dụng để expose MQTT broker (Mosquitto) đang chạy trên localhost ra internet, cho phép Wokwi simulator kết nối được.

```
┌─────────────────────────────────────────────────────────────────┐
│                     MÁY TÍNH LOCAL                              │
│                                                                 │
│     ┌──────────────────────┐                                   │
│     │  Mosquitto MQTT      │◄──────────┐                       │
│     │  localhost:1883      │           │                       │
│     └──────────────────────┘           │                       │
│                ▲                  ┌────┴─────┐                  │
│                │                  │  Ngrok   │                  │
│                │                  │  Client  │                  │
│                │                  └────┬─────┘                  │
└────────────────┼───────────────────────┼────────────────────────┘
                 │                       │
     LAN: 192.168.x.x:1883              │ Internet
                 │                       │ 0.tcp.ap.ngrok.io:xxxxx
                 ▼                       ▼
    ┌────────────────────┐    ┌────────────────────────┐
    │  🎥 ESP32-CAM      │    │  🌡️ Wokwi Simulator   │
    │  (Hardware thật)   │    │  (ESP32-Sensor, Fan)   │
    │  ✅ Không đổi code │    │                        │
    └────────────────────┘    └────────────────────────┘
```

## Bước 1: Cài đặt Ngrok

### Windows (PowerShell)
```powershell
winget install ngrok
```

### Hoặc tải từ website
1. Truy cập https://ngrok.com/download
2. Tải bản Windows
3. Giải nén và thêm vào PATH

## Bước 2: Đăng ký tài khoản Ngrok (Miễn phí)

1. Truy cập https://dashboard.ngrok.com/signup
2. Đăng ký tài khoản (có thể dùng GitHub/Google)
3. Sau khi đăng nhập, vào **Your Authtoken**
4. Copy authtoken

## Bước 3: Cấu hình Ngrok

```powershell
ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
```

## Bước 4: Chạy MQTT Broker (Docker)

```powershell
cd d:\huibeta\iotprj\Hust-IoTandApplications-20261\backend
docker-compose up -d mqtt
```

Kiểm tra MQTT đang chạy:
```powershell
docker ps | findstr mqtt
```

## Bước 5: Expose MQTT qua Ngrok

```powershell
ngrok tcp 1883
```

Kết quả sẽ hiện như sau:
```
Session Status                online
Account                       your-email@gmail.com (Plan: Free)
Version                       3.x.x
Region                        Asia Pacific (ap)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    tcp://0.tcp.ap.ngrok.io:12345 -> localhost:1883
```

**Ghi nhớ:** `0.tcp.ap.ngrok.io:12345` - đây là URL công khai!

## Bước 6: Cập nhật code ESP32 (Wokwi)

Mở file `ESP32-Sensor/src/main.cpp` và `ESP32-Fan/src/main.cpp`, thay đổi:

```cpp
// THAY ĐỔI THEO URL NGROK CỦA BẠN
const char* MQTT_BROKER = "0.tcp.ap.ngrok.io";  // ← hostname từ ngrok
const int MQTT_PORT = 12345;                     // ← port từ ngrok
```

## Bước 7: Chạy Wokwi Simulator

1. Mở VS Code
2. Mở project `ESP32-Sensor` hoặc `ESP32-Fan`
3. Nhấn `F1` → `Wokwi: Start Simulator`
4. Xem Serial Monitor để kiểm tra kết nối

## Lưu ý quan trọng

### ⚠️ URL Ngrok thay đổi mỗi lần restart!

Mỗi lần chạy `ngrok tcp 1883`, bạn sẽ nhận được URL mới. Cần:
1. Copy URL mới
2. Cập nhật code ESP32
3. Build lại project

### 💡 Tip: Dùng Ngrok với static domain (Trả phí)

Nếu muốn URL cố định, đăng ký gói trả phí của Ngrok.

### 🔧 Kiểm tra Ngrok đang hoạt động

Mở browser: http://127.0.0.1:4040 để xem dashboard Ngrok

## Kiểm tra kết nối

### Test từ máy khác bằng mosquitto_pub
```bash
mosquitto_pub -h 0.tcp.ap.ngrok.io -p 12345 -t "test" -m "hello"
```

### Test từ Wokwi
Sau khi chạy simulator, kiểm tra Serial Monitor:
```
✅ WiFi connected!
🔌 Connecting to MQTT... connected!
📤 Device registered: SENSOR_XXXX
```

## Troubleshooting

### Lỗi: Connection refused
- Kiểm tra Docker Mosquitto đang chạy: `docker ps`
- Kiểm tra Ngrok đang chạy và không bị lỗi

### Lỗi: MQTT timeout
- URL Ngrok có thể đã thay đổi, kiểm tra lại
- Firewall có thể chặn kết nối

### Lỗi: Wokwi không kết nối được
- Đảm bảo đã cập nhật đúng hostname và port từ Ngrok
- Build lại project sau khi thay đổi code
