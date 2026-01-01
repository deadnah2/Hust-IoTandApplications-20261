# ESP32 Sensor - Wokwi Simulator

Đọc nhiệt độ và độ ẩm từ DHT22, gửi lên server qua MQTT.

## Phần cứng giả lập

- ESP32 DevKit
- DHT22 (GPIO 4)
- LED trạng thái (GPIO 2)

## Cách chạy

1. Chạy MQTT broker:
`
cd backend
docker-compose up -d mqtt
`

2. Mở ngrok:
`
ngrok tcp 1883
`

3. Sửa src/main.cpp với hostname và port từ ngrok:
`cpp
const char* MQTT_BROKER = "0.tcp.ap.ngrok.io";
const int MQTT_PORT = 12345;
`

4. F1 -> Wokwi: Start Simulator

## MQTT

- Publish device/new để đăng ký device
- Publish device/data/{MAC} mỗi 5s:
`json
{
  "temperature": 26.5,
  "humidity": 65.0
}
`

## Wokwi

Có thể kéo thanh trượt trên DHT22 để thay đổi giá trị nhiệt độ/độ ẩm khi test.
