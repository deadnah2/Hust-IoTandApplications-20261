#!/usr/bin/env python3
"""
Database Seeding Script
Seed the database with sample data for testing and development
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
from app.models.device import Device, DeviceType, DeviceStatus
from app.models.activity_log import ActivityLog, LogType
from app.core.security import get_password_hash
from app.core.config import settings


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


async def create_sample_users():
    """Create sample users"""
    print("Creating sample users...")
    
    # Create admin user
    admin_user = User(
        username="admin",
        email="admin@smarthome.com",
        passwordHash=get_password_hash("admin123"),
    )
    await admin_user.save()
    print(f"✓ Created admin user: {admin_user.username}")
    
    # Create test users
    test_users = [
        {
            "username": "john_doe",
            "email": "john@example.com",
            "password": "john123"
        },
        {
            "username": "jane_smith", 
            "email": "jane@example.com",
            "password": "jane123"
        },
        {
            "username": "bob_wilson",
            "email": "bob@example.com", 
            "password": "bob123"
        }
    ]
    
    created_users = []
    for user_data in test_users:
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            passwordHash=get_password_hash(user_data["password"]),
        )
        await user.save()
        created_users.append(user)
        print(f"✓ Created user: {user.username}")
    
    return admin_user, created_users


async def create_sample_homes(admin_user, test_users):
    """Create sample homes"""
    print("Creating sample homes...")
    
    homes = []
    
    # Admin's home
    admin_home = Home(
        ownerUserId=admin_user.id,
        name="Admin's Smart Villa",
        location="123 Luxury Lane, Beverly Hills, CA"
    )
    await admin_home.save()
    homes.append(admin_home)
    print(f"✓ Created home: {admin_home.name}")
    
    # Create homes for each test user
    home_names = [
        "Cozy Family House",
        "Modern Apartment", 
        "Traditional Cottage"
    ]
    
    locations = [
        "456 Oak Street, San Francisco, CA",
        "789 Pine Avenue, Los Angeles, CA", 
        "321 Elm Drive, Seattle, WA"
    ]
    
    for i, user in enumerate(test_users):
        home = Home(
            ownerUserId=user.id,
            name=home_names[i],
            location=locations[i]
        )
        await home.save()
        homes.append(home)
        print(f"✓ Created home: {home.name}")
    
    return admin_home, homes[1:]  # Return admin_home separately and other homes


async def create_sample_rooms(admin_home, user_homes):
    """Create sample rooms for homes"""
    print("Creating sample rooms...")
    
    rooms = []
    
    # Room templates for different home types
    admin_rooms = ["Living Room", "Master Bedroom", "Guest Room", "Kitchen", "Home Office", "Garage"]
    user_rooms = ["Living Room", "Bedroom", "Kitchen", "Bathroom"]
    
    # Create rooms for admin home
    for room_name in admin_rooms:
        room = Room(homeId=admin_home.id, name=room_name)
        await room.save()
        rooms.append(room)
        print(f"✓ Created room: {room_name} in admin home")
    
    # Create rooms for user homes
    for home in user_homes:
        for room_name in user_rooms:
            room = Room(homeId=home.id, name=room_name)
            await room.save()
            rooms.append(room)
            print(f"✓ Created room: {room_name} in {home.name}")
    
    return rooms


async def create_sample_devices(rooms):
    """Create sample devices for rooms"""
    print("Creating sample devices...")
    
    devices = []
    
    # Get rooms by name for easier assignment
    living_rooms = [r for r in rooms if "Living Room" in r.name]
    bedrooms = [r for r in rooms if "Bedroom" in r.name]
    kitchens = [r for r in rooms if "Kitchen" in r.name]
    
    # Create devices for living rooms
    for living_room in living_rooms:
        # Smart light
        light = Device(
            roomId=living_room.id,
            name="Smart LED Light",
            type=DeviceType.LIGHT,
            status=DeviceStatus.OFF
        )
        await light.save()
        devices.append(light)
        print(f"✓ Created device: {light.name} in {living_room.name}")
        
        # Smart fan
        fan = Device(
            roomId=living_room.id,
            name="Smart Ceiling Fan",
            type=DeviceType.FAN,
            status=DeviceStatus.OFF,
            speed=0
        )
        await fan.save()
        devices.append(fan)
        print(f"✓ Created device: {fan.name} in {living_room.name}")
        
        # Security camera (only for first living room)
        if living_room == living_rooms[0]:
            camera = Device(
                roomId=living_room.id,
                name="Security Camera",
                type=DeviceType.CAMERA,
                status=DeviceStatus.ON,
                streamUrl="rtsp://192.168.1.100:554/stream1",
                humanDetectionEnabled=True
            )
            await camera.save()
            devices.append(camera)
            print(f"✓ Created device: {camera.name} in {living_room.name}")
    
    # Create devices for bedrooms
    for bedroom in bedrooms:
        # Bedside light
        light = Device(
            roomId=bedroom.id,
            name="Bedside Lamp",
            type=DeviceType.LIGHT,
            status=DeviceStatus.ON
        )
        await light.save()
        devices.append(light)
        print(f"✓ Created device: {light.name} in {bedroom.name}")
        
        # Motion sensor (only for master bedroom)
        if "Master" in bedroom.name:
            sensor = Device(
                roomId=bedroom.id,
                name="Motion Sensor",
                type=DeviceType.SENSOR,
                status=DeviceStatus.ON
            )
            await sensor.save()
            devices.append(sensor)
            print(f"✓ Created device: {sensor.name} in {bedroom.name}")
    
    # Create devices for kitchens
    for kitchen in kitchens:
        # Kitchen light
        light = Device(
            roomId=kitchen.id,
            name="Kitchen Ceiling Light",
            type=DeviceType.LIGHT,
            status=DeviceStatus.OFF
        )
        await light.save()
        devices.append(light)
        print(f"✓ Created device: {light.name} in {kitchen.name}")
        
        # Range hood fan (only for first kitchen)
        if kitchen == kitchens[0]:
            hood_fan = Device(
                roomId=kitchen.id,
                name="Range Hood Fan",
                type=DeviceType.FAN,
                status=DeviceStatus.OFF,
                speed=0
            )
            await hood_fan.save()
            devices.append(hood_fan)
            print(f"✓ Created device: {hood_fan.name} in {kitchen.name}")
    
    return devices


async def create_sample_activity_logs(users, homes, devices):
    """Create sample activity logs"""
    print("Creating sample activity logs...")
    
    logs = [
        # System initialization logs
        {
            "userId": users[0].id,  # admin
            "homeId": homes[0].id,  # admin home
            "type": LogType.INFO,
            "message": "Smart Home system initialized successfully"
        },
        {
            "userId": users[0].id,
            "homeId": homes[0].id,
            "type": LogType.INFO,
            "message": "All devices connected and online"
        },
        
        # Device interaction logs
        {
            "userId": users[0].id,
            "homeId": homes[0].id,
            "deviceId": next((d.id for d in devices if "Smart LED Light" in d.name), None),
            "type": LogType.INFO,
            "message": "Living room light turned on"
        },
        {
            "userId": users[0].id,
            "homeId": homes[0].id,
            "deviceId": next((d.id for d in devices if "Smart Ceiling Fan" in d.name), None),
            "type": LogType.INFO,
            "message": "Living room fan speed set to level 2"
        },
        
        # Security logs
        {
            "userId": users[0].id,
            "homeId": homes[0].id,
            "deviceId": next((d.id for d in devices if "Security Camera" in d.name), None),
            "type": LogType.WARNING,
            "message": "Motion detected in living room at 14:30"
        },
        {
            "userId": users[1].id,  # john_doe
            "homeId": homes[1].id,  # john's home
            "type": LogType.INFO,
            "message": "User logged in successfully"
        },
        
        # Error logs
        {
            "userId": users[0].id,
            "homeId": homes[0].id,
            "deviceId": next((d.id for d in devices if "Motion Sensor" in d.name), None),
            "type": LogType.ERROR,
            "message": "Motion sensor battery low (15% remaining)"
        },
        
        # General activity logs
        {
            "userId": users[2].id,  # jane_smith
            "homeId": homes[2].id,  # jane's home
            "type": LogType.INFO,
            "message": "New device added: Kitchen Ceiling Light"
        },
        {
            "userId": users[3].id,  # bob_wilson
            "homeId": homes[3].id,  # bob's home
            "type": LogType.INFO,
            "message": "Home automation schedule created"
        }
    ]
    
    for log_data in logs:
        # Remove deviceId if None
        if log_data.get("deviceId") is None:
            log_data.pop("deviceId", None)
            
        log = ActivityLog(**log_data)
        await log.save()
    
    print(f"✓ Created {len(logs)} activity logs")


async def seed_data():
    """Main seeding function"""
    print("Starting database seeding...")
    
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
            print("Database already contains data.")
            response = input("Do you want to clear existing data and reseed? (y/N): ")
            if response.lower() != 'y':
                print("Seeding cancelled.")
                return
            
            await clear_all_data()
        
        # Create sample data
        admin_user, test_users = await create_sample_users()
        all_users = [admin_user] + test_users
        
        admin_home, user_homes = await create_sample_homes(admin_user, test_users)
        all_homes = [admin_home] + user_homes
        
        rooms = await create_sample_rooms(admin_home, user_homes)
        
        devices = await create_sample_devices(rooms)
        
        await create_sample_activity_logs(all_users, all_homes, devices)
        
        print("\n🎉 Database seeding completed successfully!")
        print(f"📊 Summary:")
        print(f"   • Users: {len(all_users)}")
        print(f"   • Homes: {len(all_homes)}")
        print(f"   • Rooms: {len(rooms)}")
        print(f"   • Devices: {len(devices)}")
        print(f"   • Activity Logs: 8")
        
        print(f"\n🔐 Test Accounts:")
        print(f"   Admin: admin / admin123")
        print(f"   User1: john_doe / john123")
        print(f"   User2: jane_smith / jane123") 
        print(f"   User3: bob_wilson / bob123")
        
    except Exception as e:
        print(f"Seeding failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(seed_data())
