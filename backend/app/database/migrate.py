#!/usr/bin/env python3
"""
Database Migration Script
Migrate all models to MongoDB database using Beanie ODM
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.core.config import settings
from app.models.user import User
from app.models.session import Session
from app.models.home import Home
from app.models.room import Room
from app.models.device import Device, DeviceType, DeviceState
from app.models.activity_log import ActivityLog, LogType
from app.core.security import get_password_hash


async def create_indexes():
    """Create indexes for better performance"""
    print("Creating database indexes...")
    
    # Indexes are automatically created by Beanie based on Indexed() definitions in models
    # No need to manually create them here
    
    print("Database indexes created successfully!")


async def seed_data():
    """Seed database with initial data"""
    print("Seeding database with initial data...")
    
    # Create admin user
    admin_user = User(
        username="admin",
        email="admin@smarthome.com",
        passwordHash=get_password_hash("admin123"),
    )
    await admin_user.save()
    
    # Create test user
    test_user = User(
        username="testuser",
        email="test@smarthome.com", 
        passwordHash=get_password_hash("test123"),
    )
    await test_user.save()
    
    # Create sample homes
    home1 = Home(
        ownerUserId=admin_user.id,
        name="Admin's Smart Home",
        location="123 Main Street, City, Country"
    )
    await home1.save()
    
    home2 = Home(
        ownerUserId=test_user.id,
        name="Test Home",
        location="456 Oak Avenue, Town, Country"
    )
    await home2.save()
    
    # Create sample rooms for home1
    living_room = Room(
        homeId=home1.id,
        name="Living Room"
    )
    await living_room.save()
    
    bedroom = Room(
        homeId=home1.id,
        name="Master Bedroom"
    )
    await bedroom.save()
    
    kitchen = Room(
        homeId=home1.id,
        name="Kitchen"
    )
    await kitchen.save()
    
    # Create sample rooms for home2
    living_room2 = Room(
        homeId=home2.id,
        name="Living Room"
    )
    await living_room2.save()
    
    # Create sample devices
    # Living room devices
    living_light = Device(
        roomId=living_room.id,
        name="Living Room Light",
        bssid="AA:BB:CC:DD:EE:01",
        controllerMAC="11:22:33:44:55:01",
        type=DeviceType.LIGHT,
        state=DeviceState.OFF
    )
    await living_light.save()
    
    living_fan = Device(
        roomId=living_room.id,
        name="Living Room Fan",
        bssid="AA:BB:CC:DD:EE:02",
        controllerMAC="11:22:33:44:55:02",
        type=DeviceType.FAN,
        state=DeviceState.OFF,
        speed=0
    )
    await living_fan.save()
    
    living_camera = Device(
        roomId=living_room.id,
        name="Living Room Camera",
        bssid="AA:BB:CC:DD:EE:03",
        controllerMAC="11:22:33:44:55:03",
        type=DeviceType.CAMERA,
        state=DeviceState.ON,
        streamUrl="rtsp://192.168.1.100:554/stream1",
        humanDetectionEnabled=True
    )
    await living_camera.save()
    
    # Bedroom devices
    bedroom_light = Device(
        roomId=bedroom.id,
        name="Bedroom Light",
        bssid="AA:BB:CC:DD:EE:04",
        controllerMAC="11:22:33:44:55:04",
        type=DeviceType.LIGHT,
        state=DeviceState.ON
    )
    await bedroom_light.save()
    
    bedroom_sensor = Device(
        roomId=bedroom.id,
        name="Bedroom Sensor",
        bssid="AA:BB:CC:DD:EE:05",
        controllerMAC="11:22:33:44:55:05",
        type=DeviceType.SENSOR,
        state=DeviceState.ON
    )
    await bedroom_sensor.save()
    
    # Kitchen devices
    kitchen_light = Device(
        roomId=kitchen.id,
        name="Kitchen Light",
        bssid="AA:BB:CC:DD:EE:06",
        controllerMAC="11:22:33:44:55:06",
        type=DeviceType.LIGHT,
        state=DeviceState.OFF
    )
    await kitchen_light.save()
    
    # Home2 devices
    home2_light = Device(
        roomId=living_room2.id,
        name="Home2 Living Light",
        bssid="AA:BB:CC:DD:EE:07",
        controllerMAC="11:22:33:44:55:07",
        type=DeviceType.LIGHT,
        state=DeviceState.OFF
    )
    await home2_light.save()
    
    # Create sample activity logs
    await ActivityLog(
        userId=admin_user.id,
        homeId=home1.id,
        deviceId=living_light.id,
        type=LogType.INFO,
        message="Living Room Light turned off"
    ).save()
    
    await ActivityLog(
        userId=admin_user.id,
        homeId=home1.id,
        deviceId=bedroom_camera.id if 'bedroom_camera' in locals() else None,
        type=LogType.WARNING,
        message="Motion detected in bedroom"
    ).save()
    
    await ActivityLog(
        userId=test_user.id,
        homeId=home2.id,
        type=LogType.INFO,
        message="Test user logged in"
    ).save()
    
    await ActivityLog(
        userId=admin_user.id,
        homeId=home1.id,
        type=LogType.INFO,
        message="System initialized successfully"
    ).save()
    
    print("Database seeded successfully!")
    print(f"Created:")
    print(f"- 2 users (admin, testuser)")
    print(f"- 2 homes")
    print(f"- 5 rooms") 
    print(f"- 7 devices")
    print(f"- 4 activity logs")


async def migrate():
    """Main migration function"""
    print("Starting database migration...")
    
    # Check if required environment variables are set
    if not settings.MONGODB_URL:
        print("Error: MONGODB_URL not found in environment variables")
        return
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    
    try:
        # Initialize Beanie
        await init_beanie(
            database=client[settings.MONGO_DATABASE_NAME],
            document_models=[
                User,
                Session,
                Home,
                Room,
                Device,
                ActivityLog
            ],
        )
        
        print(f"Connected to database: {settings.MONGO_DATABASE_NAME}")
        
        # Create indexes
        await create_indexes()
        
        # Check if data already exists
        existing_users = await User.find_all().to_list()
        if existing_users:
            print("Database already contains data. Skipping seed data creation.")
            response = input("Do you want to recreate all data? (y/N): ")
            if response.lower() != 'y':
                print("Migration completed without seeding.")
                return
            else:
                # Clear existing data
                print("Clearing existing data...")
                await User.delete_all()
                await Session.delete_all()
                await Home.delete_all()
                await Room.delete_all()
                await Device.delete_all()
                await ActivityLog.delete_all()
        
        # Seed data
        await seed_data()
        
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(migrate())
