#!/usr/bin/env python3
"""
Main Database Setup Script
Run this script to migrate models and seed data for the Smart Home application
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from app.database.db_manager import full_setup, check_connection


def print_banner():
    """Print application banner"""
    print("="*60)
    print("🏠 SMART HOME DATABASE SETUP")
    print("="*60)
    print("This script will:")
    print("1. Connect to MongoDB database")
    print("2. Migrate all models to the database")
    print("3. Create database indexes for performance")
    print("4. Seed the database with sample data")
    print("="*60)


def print_requirements():
    """Print requirements before running"""
    print("\n📋 REQUIREMENTS:")
    print("• MongoDB server running")
    print("• .env file configured with MONGODB_URL")
    print("• All dependencies installed (requirements.txt)")
    print("\n⚠️  WARNING: This will create/replace data in your database!")


async def main():
    """Main function"""
    print_banner()
    print_requirements()
    
    # Check if user wants to proceed
    response = input("\nDo you want to proceed with database setup? (y/N): ")
    if response.lower() != 'y':
        print("Setup cancelled.")
        return
    
    # Check database connection first
    print("\n🔍 Checking database connection...")
    if not await check_connection():
        print("\n❌ Cannot connect to database. Please check:")
        print("• MongoDB server is running")
        print("• MONGODB_URL in .env file is correct")
        print("• Database permissions are correct")
        return
    
    # Run full setup
    print("\n🚀 Starting database setup...")
    success = await full_setup()
    
    if success:
        print("\n✅ Database setup completed successfully!")
        print("\n🔐 Test Accounts Created:")
        print("• admin1 / admin1 - BSSID: 11:11:11:11:11:11")
        print("• admin2 / admin2 - BSSID: 22:22:22:22:22:22")
        print("• admin3 / admin3 - BSSID: 33:33:33:33:33:33")
        print("\n📚 You can now start the FastAPI server:")
        print("  uvicorn app.main:app --reload")
    else:
        print("\n❌ Database setup failed. Please check the error messages above.")


if __name__ == "__main__":
    asyncio.run(main())
