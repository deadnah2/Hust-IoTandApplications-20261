# ESP32 Smart Fan - Wokwi Simulator

Điều khiển quạt 4 tốc độ (0-3) qua MQTT.

## Phần cứng giả lập

- ESP32 DevKit
- 1 LED xanh dương (GPIO 18) - đại diện cho motor quạt
- 3 LED hiển thị tốc độ (GPIO 25, 26, 27)
- 2 nút bấm tăng/giảm tốc độ (GPIO 19, 21)

## Cách chạy

1. Chạy MQTT broker:
`
cd backend
docker-compose up -d mqtt
`

2. Mở ngrok để expose port MQTT:
`
ngrok tcp 1883
`

3. Copy hostname và port từ ngrok, sửa trong src/main.cpp:
`cpp
const char* MQTT_BROKER = "0.tcp.ap.ngrok.io";
const int MQTT_PORT = 12345;  // port ngrok cho bạn
`

4. Mở folder này trong VS Code, nhấn F1 -> Wokwi: Start Simulator

## MQTT

- Publish device/new khi khởi động để đăng ký
- Publish device/data/{MAC} mỗi 5s gửi trạng thái
- Subscribe device/control/{MAC} để nhận lệnh

Lệnh điều khiển:
`json
{"action": "ON"}
{"action": "OFF"}  
{"action": "SET_SPEED", "speed": 2}
`

## Tốc độ

| Speed | LED |
|-------|-----|
| 0 | Tắt |
| 1 | 1 LED sáng |
| 2 | 2 LED sáng |
| 3 | 3 LED sáng |
