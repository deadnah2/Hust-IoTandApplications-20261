#!/usr/bin/env python3
"""
Database Seeding Script
Seed the database with sample data for testing and development
3 Admin users with unique BSSIDs for demo purposes
"""
import asyncio
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from beanie import PydanticObjectId, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.models.user import User
from app.models.session import Session
from app.models.home import Home
from app.models.room import Room
from app.models.device import Device, DeviceType, DeviceState
from app.models.activity_log import ActivityLog, LogType
from app.core.security import get_password_hash
from app.core.config import settings

# BSSID riêng cho từng admin (giả lập mỗi nhà 1 mạng WiFi khác nhau)
BSSID_ADMIN1 = "11:11:11:11:11:11"
BSSID_ADMIN2 = "22:22:22:22:22:22"
BSSID_ADMIN3 = "33:33:33:33:33:33"


async def clear_all_data():
    """Clear all existing data from the database"""
    print("Clearing all existing data...")
    
    # Delete in reverse order to avoid foreign key issues
    await ActivityLog.delete_all()
    await Device.delete_all()
    await Room.delete_all()
    await Home.delete_all()
    await Session.delete_all()
    await User.delete_all()
    
    print("All data cleared successfully!")


async def create_admin_users():
    """Create 3 admin users with password = username"""
    print("Creating admin users...")
    
    admins = []
    admin_configs = [
        {"username": "admin1", "email": "admin1@smarthome.com"},
        {"username": "admin2", "email": "admin2@smarthome.com"},
        {"username": "admin3", "email": "admin3@smarthome.com"},
    ]
    
    for config in admin_configs:
        user = User(
            username=config["username"],
            email=config["email"],
            passwordHash=get_password_hash(config["username"]),  # password = username
        )
        await user.save()
        admins.append(user)
        print(f"✓ Created user: {user.username} (password: {config['username']})")
    
    return admins


async def create_homes_for_admins(admins):
    """Create homes for each admin with unique BSSID"""
    print("Creating homes...")
    
    home_configs = [
        {
            "name": "Nhà Hà Nội",
            "location": "123 Đường Láng, Đống Đa, Hà Nội",
            "bssid": BSSID_ADMIN1
        },
        {
            "name": "Căn hộ Sài Gòn",
            "location": "456 Nguyễn Huệ, Quận 1, TP.HCM",
            "bssid": BSSID_ADMIN2
        },
        {
            "name": "Biệt thự Đà Nẵng",
            "location": "789 Võ Nguyên Giáp, Sơn Trà, Đà Nẵng",
            "bssid": BSSID_ADMIN3
        },
    ]
    
    homes = []
    for i, admin in enumerate(admins):
        config = home_configs[i]
        home = Home(
            ownerUserId=admin.id,
            name=config["name"],
            location=config["location"],
            bssid=config["bssid"]
        )
        await home.save()
        
        # Update user's home_ids
        admin.home_ids = [home.id]
        await admin.save()
        
        homes.append(home)
        print(f"✓ Created home: {home.name} (BSSID: {config['bssid']})")
    
    return homes


async def create_rooms_for_homes(homes):
    """Create rooms for each home"""
    print("Creating rooms...")
    
    room_configs = [
        # Admin1 - Nhà Hà Nội: 3 rooms
        ["Phòng khách", "Phòng ngủ", "Nhà bếp"],
        # Admin2 - Căn hộ Sài Gòn: 2 rooms  
        ["Phòng khách", "Phòng ngủ chính"],
        # Admin3 - Biệt thự Đà Nẵng: 4 rooms
        ["Đại sảnh", "Phòng ngủ 1", "Phòng ngủ 2", "Sân vườn"],
    ]
    
    all_rooms = {}  # {home_id: [rooms]}
    
    for i, home in enumerate(homes):
        rooms = []
        for room_name in room_configs[i]:
            room = Room(homeId=home.id, name=room_name)
            await room.save()
            rooms.append(room)
            print(f"✓ Created room: {room_name} in {home.name}")
        all_rooms[home.id] = rooms
    
    return all_rooms


async def create_devices_for_rooms(homes, all_rooms):
    """Create devices for each room with correct BSSID"""
    print("Creating devices...")
    
    devices = []
    
    # ==================== ADMIN1 DEVICES ====================
    home1 = homes[0]
    rooms1 = all_rooms[home1.id]
    room1_living = rooms1[0]  # Phòng khách
    room1_bedroom = rooms1[1]  # Phòng ngủ
    
    # Phòng khách admin1
    devices.extend([
        await create_device(room1_living.id, "Smart Fan", BSSID_ADMIN1, "FAN_A1B2", 
                           DeviceType.FAN, DeviceState.OFF, speed=0),
        await create_device(room1_living.id, "Temperature Sensor", BSSID_ADMIN1, "SENSOR_C3D4",
                           DeviceType.SENSOR, DeviceState.ON, temperature=25.5, humidity=60.0),
        await create_device(room1_living.id, "Security Camera", BSSID_ADMIN1, "CAM_E5F6",
                           DeviceType.CAMERA, DeviceState.ON, 
                           streamUrl="rtsp://192.168.1.100:554/stream1", humanDetectionEnabled=True),
    ])
    
    # Phòng ngủ admin1
    devices.extend([
        await create_device(room1_bedroom.id, "Bedroom Light", BSSID_ADMIN1, "LIGHT_G7H8",
                           DeviceType.LIGHT, DeviceState.OFF),
        await create_device(room1_bedroom.id, "Bedroom Fan", BSSID_ADMIN1, "FAN_I9J0",
                           DeviceType.FAN, DeviceState.ON, speed=2),
    ])
    
    print(f"✓ Created 5 devices for admin1")
    
    # ==================== ADMIN2 DEVICES ====================
    home2 = homes[1]
    rooms2 = all_rooms[home2.id]
    room2_living = rooms2[0]  # Phòng khách
    room2_bedroom = rooms2[1]  # Phòng ngủ chính
    
    # Phòng khách admin2
    devices.extend([
        await create_device(room2_living.id, "Living Room Fan", BSSID_ADMIN2, "FAN_K1L2",
                           DeviceType.FAN, DeviceState.OFF, speed=0),
        await create_device(room2_living.id, "Room Sensor", BSSID_ADMIN2, "SENSOR_M3N4",
                           DeviceType.SENSOR, DeviceState.ON, temperature=28.0, humidity=55.0),
    ])
    
    # Phòng ngủ admin2
    devices.extend([
        await create_device(room2_bedroom.id, "Main Light", BSSID_ADMIN2, "LIGHT_O5P6",
                           DeviceType.LIGHT, DeviceState.ON),
        await create_device(room2_bedroom.id, "IP Camera", BSSID_ADMIN2, "CAM_Q7R8",
                           DeviceType.CAMERA, DeviceState.OFF,
                           streamUrl="rtsp://192.168.1.101:554/stream2", humanDetectionEnabled=False),
    ])
    
    print(f"✓ Created 4 devices for admin2")
    
    # ==================== ADMIN3 DEVICES ====================
    home3 = homes[2]
    rooms3 = all_rooms[home3.id]
    room3_living = rooms3[0]  # Đại sảnh
    room3_bedroom1 = rooms3[1]  # Phòng ngủ 1
    room3_bedroom2 = rooms3[2]  # Phòng ngủ 2
    room3_garden = rooms3[3]  # Sân vườn
    
    # Đại sảnh admin3
    devices.extend([
        await create_device(room3_living.id, "Ceiling Fan", BSSID_ADMIN3, "FAN_S9T0",
                           DeviceType.FAN, DeviceState.ON, speed=3),
        await create_device(room3_living.id, "Smart Light", BSSID_ADMIN3, "LIGHT_U1V2",
                           DeviceType.LIGHT, DeviceState.ON),
        await create_device(room3_living.id, "Climate Sensor", BSSID_ADMIN3, "SENSOR_W3X4",
                           DeviceType.SENSOR, DeviceState.ON, temperature=26.0, humidity=65.0),
    ])
    
    # Phòng ngủ 1 admin3
    devices.extend([
        await create_device(room3_bedroom1.id, "Bedroom 1 Fan", BSSID_ADMIN3, "FAN_Y5Z6",
                           DeviceType.FAN, DeviceState.OFF, speed=0),
    ])
    
    # Phòng ngủ 2 admin3
    devices.extend([
        await create_device(room3_bedroom2.id, "Bedroom 2 Light", BSSID_ADMIN3, "LIGHT_A7B8",
                           DeviceType.LIGHT, DeviceState.OFF),
    ])
    
    # Sân vườn admin3
    devices.extend([
        await create_device(room3_garden.id, "Garden Camera", BSSID_ADMIN3, "CAM_C9D0",
                           DeviceType.CAMERA, DeviceState.ON,
                           streamUrl="rtsp://192.168.1.102:554/stream3", humanDetectionEnabled=True),
        await create_device(room3_garden.id, "Outdoor Sensor", BSSID_ADMIN3, "SENSOR_E1F2",
                           DeviceType.SENSOR, DeviceState.ON, temperature=30.0, humidity=70.0),
    ])
    
    print(f"✓ Created 7 devices for admin3")
    
    # ==================== UNASSIGNED DEVICES (cho demo Add Device) ====================
    devices.extend([
        await create_device(None, "New Smart Fan", BSSID_ADMIN1, "FAN_NEW1",
                           DeviceType.FAN, DeviceState.OFF, speed=0),
        await create_device(None, "New Sensor", BSSID_ADMIN2, "SENSOR_NEW2",
                           DeviceType.SENSOR, DeviceState.ON, temperature=24.0, humidity=50.0),
        await create_device(None, "New Camera", BSSID_ADMIN3, "CAM_NEW3",
                           DeviceType.CAMERA, DeviceState.OFF, humanDetectionEnabled=False),
    ])
    
    print(f"✓ Created 3 unassigned devices for demo")
    
    return devices


async def create_device(room_id, name, bssid, mac, device_type, state, **kwargs):
    """Helper function to create a device"""
    device_data = {
        "roomId": room_id,
        "name": name,
        "bssid": bssid,
        "controllerMAC": mac,
        "type": device_type,
        "state": state,
    }
    device_data.update(kwargs)
    
    device = Device(**device_data)
    await device.save()
    return device


async def create_activity_logs(admins, homes):
    """Create sample activity logs"""
    print("Creating activity logs...")
    
    logs_data = [
        {
            "userId": admins[0].id,
            "homeId": homes[0].id,
            "type": LogType.INFO,
            "message": "admin1 đã đăng nhập hệ thống"
        },
        {
            "userId": admins[1].id,
            "homeId": homes[1].id,
            "type": LogType.INFO,
            "message": "admin2 đã bật quạt phòng khách"
        },
        {
            "userId": admins[2].id,
            "homeId": homes[2].id,
            "type": LogType.WARNING,
            "message": "Camera sân vườn phát hiện chuyển động"
        },
    ]
    
    for log_data in logs_data:
        log = ActivityLog(**log_data)
        await log.save()
    
    print(f"✓ Created {len(logs_data)} activity logs")


async def seed_data():
    """Main seeding function"""
    print("\n" + "="*50)
    print("🌱 STARTING DATABASE SEEDING")
    print("="*50)
    
    # Initialize Beanie connection if not already initialized
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.MONGO_DATABASE_NAME]
        
        await init_beanie(
            database=db,
            document_models=[
                User,
                Session,
                Home,
                Room,
                Device,
                ActivityLog
            ]
        )
        
        # Check if data already exists
        existing_users = await User.find_all().to_list()
        if existing_users:
            print("\n⚠️  Database already contains data.")
            response = input("Do you want to clear existing data and reseed? (y/N): ")
            if response.lower() != 'y':
                print("Seeding cancelled.")
                return
            
            await clear_all_data()
        
        # Create sample data
        admins = await create_admin_users()
        homes = await create_homes_for_admins(admins)
        all_rooms = await create_rooms_for_homes(homes)
        devices = await create_devices_for_rooms(homes, all_rooms)
        await create_activity_logs(admins, homes)
        
        # Count rooms
        total_rooms = sum(len(rooms) for rooms in all_rooms.values())
        
        print("\n" + "="*50)
        print("🎉 DATABASE SEEDING COMPLETED!")
        print("="*50)
        print(f"\n📊 Summary:")
        print(f"   • Users: {len(admins)}")
        print(f"   • Homes: {len(homes)}")
        print(f"   • Rooms: {total_rooms}")
        print(f"   • Devices: {len(devices)} (including 3 unassigned)")
        print(f"   • Activity Logs: 3")
        
        print(f"\n🔐 Test Accounts (password = username):")
        print(f"   • admin1 / admin1 - BSSID: {BSSID_ADMIN1}")
        print(f"   • admin2 / admin2 - BSSID: {BSSID_ADMIN2}")
        print(f"   • admin3 / admin3 - BSSID: {BSSID_ADMIN3}")
        
        print(f"\n📝 Notes:")
        print(f"   • Mỗi admin có 1 home với BSSID riêng")
        print(f"   • Unassigned devices: mỗi BSSID 1 cái cho demo Add Device")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(seed_data())
