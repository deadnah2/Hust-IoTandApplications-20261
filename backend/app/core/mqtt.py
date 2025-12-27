import json
import paho.mqtt.client as mqtt
from app.core.config import settings

# Khởi tạo MQTT client
client = mqtt.Client()

# Callback khi kết nối thành công
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker!")
    client.subscribe("device/new")

# Callback khi nhận được message
def on_message(client, userdata, msg):
    print("Received message: ", msg.topic, msg.payload.decode())
    if msg.topic == "device/new":
        add_device(msg.payload.decode())

# Gán callbacks
client.on_connect = on_connect
client.on_message = on_message

# Kết nối đến broker
def connect_mqtt():
    client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, 60)
    client.loop_start()  # Chạy loop trong background

# Ngắt kết nối
def disconnect_mqtt():
    client.loop_stop()
    client.disconnect()

def add_device(payload):
    """
    Placeholder function to handle adding a new device.
    """
    print(f"Placeholder for adding a new device with payload: {payload}")
    # Here you would typically parse the payload (e.g., if it's JSON)
    # and then interact with your database to add the new device.
    # For example:
    # try:
    #     device_data = json.loads(payload)
    #     # ... create and save a new Device document ...
    # except json.JSONDecodeError:
    #     print("Error decoding JSON payload")
