# SmartHome Docker Infrastructure

## Các dịch vụ

### MongoDB
- **Port**: 27017
- **Username**: (See your `.env` file, `MONGO_ROOT_USERNAME`)
- **Password**: (See your `.env` file, `MONGO_ROOT_PASSWORD`)
- **Database**: (See your `.env` file, `MONGO_DATABASE_NAME`)
- **Connection String**: `mongodb://${MONGO_ROOT_USERNAME}:${MONGO_ROOT_PASSWORD}@localhost:27017/${MONGO_DATABASE_NAME}?authSource=admin`

### Eclipse Mosquitto MQTT
- **MQTT Port**: 1883
- **WebSocket Port**: 9001
- **Allow Anonymous**: true

## Cài đặt
Trước khi khởi chạy, hãy tạo một file `.env` trong thư mục `backend` từ file `.env.example` và điền các giá trị cần thiết.
```bash
cp .env.example .env
# Mở file .env và chỉnh sửa
```

## Sử dụng

### Khởi động các dịch vụ
```bash
docker compose up -d
```

### Xem logs
```bash
# Tất cả dịch vụ
docker compose logs -f

# Chỉ MongoDB
docker compose logs -f mongodb

# Chỉ MQTT
docker compose logs -f mqtt
```

### Dừng các dịch vụ
```bash
docker compose down (-v) // Xóa các volumes
```

### Dừng và xóa volumes
```bash
docker compose down -v
```

### Kiểm tra trạng thái
```bash
docker compose ps
```

## Test MQTT

### Subscribe to topic
```bash
docker exec -it smarthome_mqtt mosquitto_sub -h localhost -t "test/topic"
```

### Publish message
```bash
docker exec -it smarthome_mqtt mosquitto_pub -h localhost -t "test/topic" -m "Hello SmartHome"
```

## Cấu hình MQTT Authentication (tùy chọn)

Nếu muốn bật authentication cho MQTT:

1. Tạo file password:
```bash
docker exec -it smarthome_mqtt mosquitto_passwd -c /mosquitto/config/passwd username
```

2. Sửa file `mqtt/config/mosquitto.conf`:
   - Đổi `allow_anonymous true` thành `allow_anonymous false`
   - Bỏ comment dòng `password_file /mosquitto/config/passwd`

3. Restart MQTT service:
```bash
docker compose restart mqtt
```
