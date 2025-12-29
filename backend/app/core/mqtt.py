import json
import asyncio
import paho.mqtt.client as mqtt
from app.core.config import settings

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
    print("🔌 MQTT disconnected")

# Publish command to device
def publish_command(device_id: str, command: dict):
    """Publish command to a device control topic"""
    topic = f"device/control/{device_id}"
    payload = json.dumps(command)
    client.publish(topic, payload)
    print(f"📤 Published to {topic}: {payload}")

async def add_device(payload: str):
    """
    Handle device/new message - create or update device in database
    """
    from app.models.device import Device
    
    try:
        data = json.loads(payload)
        print(f"🆕 New device registration: {data}")
        
        # Required fields
        device_type = data.get("type")  # SENSOR, FAN, CAMERA, LIGHT
        controller_mac = data.get("controllerMAC")
        bssid = data.get("bssid", "")
        name = data.get("name", f"{device_type} Device")
        state = data.get("state", "online")
        
        if not controller_mac or not device_type:
            print("❌ Missing required fields: controllerMAC or type")
            return
        
        # Check if device already exists
        existing = await Device.find_one(Device.controllerMAC == controller_mac)
        
        if existing:
            # Update existing device state
            await existing.update({"$set": {"state": state}})
            print(f"✅ Device updated: {controller_mac} -> {state}")
        else:
            # Create new device (not assigned to any room yet)
            device = Device(
                name=name,
                controllerMAC=controller_mac,
                bssid=bssid,
                type=device_type,
                state=state,
                roomId=None  # Will be assigned when user adds to a room
            )
            await device.create()
            print(f"✅ New device created: {controller_mac} ({device_type})")
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
    except Exception as e:
        print(f"❌ Error adding device: {e}")

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
                update_fields["state"] = data["status"]
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
