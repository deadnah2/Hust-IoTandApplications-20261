#!/usr/bin/env python3
"""
Database Utility Script
Provides commands for database management: migrate, seed, reset, status
"""
import asyncio
import argparse
import sys
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
from app.models.device import Device
from app.models.activity_log import ActivityLog


async def check_connection():
    """Check database connection"""
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        # Try to ping the database
        await client.admin.command('ping')
        print(f"✅ Successfully connected to MongoDB at {settings.MONGODB_URL}")
        print(f"📁 Database: {settings.MONGO_DATABASE_NAME}")
        client.close()
        return True
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return False


async def get_database_status():
    """Get current database status"""
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.MONGO_DATABASE_NAME]
        
        # Init Beanie để có thể dùng Model
        await init_beanie(
            database=db,
            document_models=[User, Session, Home, Room, Device, ActivityLog]
        )
        
        # Count documents in each collection
        collections = {
            "Users": User,
            "Sessions": Session,
            "Homes": Home,
            "Rooms": Room,
            "Devices": Device,
            "Activity Logs": ActivityLog
        }
        
        print("📊 Database Status:")
        print(f"Database: {settings.MONGO_DATABASE_NAME}")
        print("-" * 40)
        
        total_documents = 0
        for collection_name, model in collections.items():
            document_count = await model.count()
            total_documents += document_count
            print(f"{collection_name:<15}: {document_count:>6} documents")
        
        print("-" * 40)
        print(f"{'Total':<15}: {total_documents:>6} documents")
        
        client.close()
        return True
    except Exception as e:
        print(f"❌ Failed to get database status: {e}")
        return False


async def reset_database():
    """Reset database by clearing all data"""
    print("🗑️  Resetting database...")
    
    try:
        # Clear in reverse order to avoid dependency issues
        print("Clearing Activity Logs...")
        await ActivityLog.delete_all()
        
        print("Clearing Devices...")
        await Device.delete_all()
        
        print("Clearing Rooms...")
        await Room.delete_all()
        
        print("Clearing Homes...")
        await Home.delete_all()
        
        print("Clearing Sessions...")
        await Session.delete_all()
        
        print("Clearing Users...")
        await User.delete_all()
        
        print("✅ Database reset completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to reset database: {e}")
        return False


async def run_migration():
    """Run database migration (MongoDB doesn't need schema migration, just create indexes)"""
    print("🚀 Running database migration...")
    
    try:
        # MongoDB với Beanie không cần migration schema như SQL
        # Chỉ cần tạo indexes nếu cần
        print("✅ Migration completed (MongoDB auto-creates collections)")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


async def run_seeding():
    """Run database seeding"""
    print("🌱 Running database seeding...")
    
    try:
        # Import seeding function from seed.py
        from app.database.seed import seed_data
        await seed_data()
        return True
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        return False


async def full_setup():
    """Run complete setup: migration + seeding"""
    print("🔧 Running full database setup...")
    
    # Check connection first
    if not await check_connection():
        return False
    
    try:
        # Run migration
        if not await run_migration():
            return False
        
        # Run seeding
        if not await run_seeding():
            return False
        
        # Show final status
        await get_database_status()
        
        print("\n🎉 Full database setup completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False


async def interactive_menu():
    """Interactive menu for database operations"""
    while True:
        print("\n" + "="*50)
        print("🗄️  DATABASE MANAGEMENT TOOL")
        print("="*50)
        print("1. Check database connection")
        print("2. View database status")
        print("3. Run migration")
        print("4. Run seeding")
        print("5. Full setup (migration + seeding)")
        print("6. Reset database")
        print("7. Exit")
        print("-"*50)
        
        choice = input("Select an option (1-7): ").strip()
        
        if choice == "1":
            await check_connection()
        elif choice == "2":
            await get_database_status()
        elif choice == "3":
            await run_migration()
        elif choice == "4":
            await run_seeding()
        elif choice == "5":
            await full_setup()
        elif choice == "6":
            confirm = input("Are you sure you want to reset the database? This will delete ALL data! (y/N): ")
            if confirm.lower() == 'y':
                await reset_database()
        elif choice == "7":
            print("Goodbye! 👋")
            break
        else:
            print("❌ Invalid option. Please select 1-7.")
        
        input("\nPress Enter to continue...")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Database Management Tool")
    parser.add_argument("command", nargs="?", choices=[
        "check", "status", "migrate", "seed", "reset", "setup", "interactive"
    ], help="Command to execute")
    
    args = parser.parse_args()
    
    if not args.command:
        # Run interactive mode by default
        asyncio.run(interactive_menu())
        return
    
    # Run specific command
    if args.command == "check":
        asyncio.run(check_connection())
    elif args.command == "status":
        asyncio.run(get_database_status())
    elif args.command == "migrate":
        asyncio.run(run_migration())
    elif args.command == "seed":
        asyncio.run(run_seeding())
    elif args.command == "reset":
        confirm = input("Are you sure you want to reset the database? This will delete ALL data! (y/N): ")
        if confirm.lower() == 'y':
            asyncio.run(reset_database())
    elif args.command == "setup":
        asyncio.run(full_setup())
    elif args.command == "interactive":
        asyncio.run(interactive_menu())


if __name__ == "__main__":
    main()
