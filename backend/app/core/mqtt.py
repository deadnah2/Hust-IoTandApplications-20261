import json
import asyncio
import paho.mqtt.client as mqtt
from app.core.config import settings
from app.schemas.device import DeviceCreate
from app.services.device import DeviceService

# Khởi tạo MQTT client
client = mqtt.Client()

# Reference to the async event loop (set in connect_mqtt)
_loop = None

# Callback khi kết nối thành công
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT Broker!")
        # Subscribe to topics
        client.subscribe("device/new")
        client.subscribe("device/data/#")
        print("📥 Subscribed to: device/new, device/data/#")
    else:
        print(f"❌ Failed to connect to MQTT, return code {rc}")

# Callback khi nhận được message
def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    print(f"📩 MQTT [{topic}]: {payload[:100]}...")
    
    if topic == "device/new":
        # Schedule the async function in the event loop
        if _loop:
            asyncio.run_coroutine_threadsafe(add_device(payload), _loop)
    elif topic.startswith("device/data/"):
        # Handle sensor data updates
        device_id = topic.split("/")[-1]
        if _loop:
            asyncio.run_coroutine_threadsafe(update_device_data(device_id, payload), _loop)

# Gán callbacks
client.on_connect = on_connect
client.on_message = on_message

# Kết nối đến broker
def connect_mqtt():
    global _loop
    _loop = asyncio.get_event_loop()
    
    try:
        client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, 60)
        client.loop_start()  # Chạy loop trong background
        print(f"🔌 Connecting to MQTT: {settings.MQTT_BROKER}:{settings.MQTT_PORT}")
    except Exception as e:
        print(f"❌ MQTT connection error: {e}")

# Ngắt kết nối
def disconnect_mqtt():
    client.loop_stop()
    client.disconnect()

# Publish command to device
def publish_command(device_id: str, command: dict):
    """Publish command to a device control topic"""
    topic = f"device/control/{device_id}"
    payload = json.dumps(command)
    client.publish(topic, payload)
    print(f"📤 Published to {topic}: {payload}")

async def add_device(payload: str):
    """
    Handles adding a new device.
    """
    try:
        device_data = json.loads(payload)
        if "type" in device_data and isinstance(device_data["type"], str):
            device_data["type"] = device_data["type"].upper()
        if "state" in device_data and isinstance(device_data["state"], str):
            state = device_data["state"].strip().upper()
            if state in ("ON", "ONLINE"):
                device_data["state"] = "ON"
            elif state in ("OFF", "OFFLINE"):
                device_data["state"] = "OFF"

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

async def update_device_data(device_id: str, payload: str):
    """
    Handle device/data/{id} message - update device sensor data
    """
    from app.models.device import Device
    
    try:
        data = json.loads(payload)
        
        # Find device by controllerMAC (device_id in topic)
        device = await Device.find_one(Device.controllerMAC == device_id)
        
        if device:
            update_fields = {}
            
            # Update sensor data if present
            if "temperature" in data:
                update_fields["temperature"] = data["temperature"]
            if "humidity" in data:
                update_fields["humidity"] = data["humidity"]
            if "status" in data:
                status = str(data["status"]).strip().upper()
                if status in ("ONLINE", "ON"):
                    update_fields["state"] = "ON"
                elif status in ("OFFLINE", "OFF"):
                    update_fields["state"] = "OFF"
            if "speed" in data:
                update_fields["speed"] = data["speed"]
                
            if update_fields:
                from datetime import datetime
                update_fields["updatedAt"] = datetime.utcnow()
                await device.update({"$set": update_fields})
                print(f"📊 Device {device_id} data updated: {update_fields}")
        else:
            print(f"⚠️ Device not found: {device_id}")
            
    except Exception as e:
        print(f"❌ Error updating device data: {e}")
