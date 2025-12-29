import json
import asyncio
import paho.mqtt.client as mqtt
from app.core.config import settings
from app.schemas.device import DeviceCreate
from app.services.device import DeviceService

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
        asyncio.create_task(add_device(msg.payload.decode()))

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

async def add_device(payload: str):
    """
    Handles adding a new device.
    """
    try:
        device_data = json.loads(payload)
        device_in = DeviceCreate(**device_data)

        # Check for existing device
        existing_device = await DeviceService.get_device_by_name_and_controller_mac(
            device_in.name, device_in.controllerMAC
        )
        if existing_device:
            print(f"Device with name '{device_in.name}' and MAC '{device_in.controllerMAC}' already exists.")
            return

        # Create new device
        new_device = await DeviceService.create_device(device_in)
        if new_device and new_device.controllerMAC:
            print(f"New device added: {new_device.name}")
            # Subscribe to device's data topic
            topic = f"device/data/{new_device.controllerMAC}"
            client.subscribe(topic)
            print(f"Subscribed to {topic}")
        else:
            print("Failed to add new device.")

    except json.JSONDecodeError:
        print("Error decoding JSON payload")
    except Exception as e:
        print(f"An error occurred: {e}")
