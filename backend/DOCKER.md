# SmartHome Docker Infrastructure

## Các dịch vụ

### MongoDB
- **Port**: 27017
- **Username**: admin
- **Password**: admin123
- **Database**: smarthome
- **Connection String**: `mongodb://admin:admin123@localhost:27017/smarthome?authSource=admin`

### Eclipse Mosquitto MQTT
- **MQTT Port**: 1883
- **WebSocket Port**: 9001
- **Allow Anonymous**: true

## Sử dụng

### Khởi động các dịch vụ
```bash
docker-compose up -d
```

### Xem logs
```bash
# Tất cả dịch vụ
docker-compose logs -f

# Chỉ MongoDB
docker-compose logs -f mongodb

# Chỉ MQTT
docker-compose logs -f mqtt
```

### Dừng các dịch vụ
```bash
docker-compose down
```

### Dừng và xóa volumes
```bash
docker-compose down -v
```

### Kiểm tra trạng thái
```bash
docker-compose ps
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
docker-compose restart mqtt
```
