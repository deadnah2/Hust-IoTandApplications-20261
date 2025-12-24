# Database Migration & Seeding Guide

This guide explains how to migrate the Smart Home application models to MongoDB and seed the database with sample data.

## 📋 Prerequisites

Before running the migration scripts, ensure you have:

1. **MongoDB Server** running (local or cloud)
2. **Environment Variables** configured in `.env` file:
   ```env
   MONGO_ROOT_USERNAME=admin
   MONGO_ROOT_PASSWORD=change_me
   MONGO_DATABASE_NAME=smarthome
   MONGO_HOST=localhost
   MONGO_PORT=27017
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7
   ```
3. **Dependencies** installed:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

Run the main setup script that handles everything automatically:

```bash
cd backend
python setup_database.py
```

This script will:
- Check database connection
- Run model migration
- Create database indexes
- Seed with sample data
- Display test accounts

### Option 2: Manual Commands

Use the database manager for individual operations:

```bash
cd backend
python -m app.database.db_manager setup    # Full setup (migration + seeding)
python -m app.database.db_manager check    # Check database connection
python -m app.database.db_manager status   # View database status
python -m app.database.db_manager migrate  # Run migration only
python -m app.database.db_manager seed     # Run seeding only
python -m app.database.db_manager reset    # Clear all data
python -m app.database.db_manager interactive  # Interactive menu
```

### Option 3: Individual Scripts

Run migration and seeding separately:

```bash
# Migration only
python -m app.database.migrate

# Seeding only  
python -m app.database.seed
```

## 📊 Database Schema

The migration creates the following collections:

### Collections Overview

| Collection | Documents | Description |
|------------|-----------|-------------|
| `users` | User accounts | Authentication and user management |
| `sessions` | User sessions | JWT refresh tokens and session management |
| `homes` | Smart homes | Home/property information |
| `rooms` | Rooms in homes | Room organization |
| `devices` | IoT devices | Smart devices (lights, fans, cameras, sensors) |
| `activity_logs` | System logs | Activity tracking and system events |

### Model Relationships

```
User → Multiple Homes → Multiple Rooms → Multiple Devices
User → Multiple Sessions
User → Multiple Activity Logs
Home → Multiple Activity Logs  
Room → Multiple Activity Logs
Device → Multiple Activity Logs
```

## 🔐 Default Test Accounts

After seeding, you can use these test accounts:

| Username | Email | Password | Role |
|----------|-------|----------|------|
| admin | admin@smarthome.com | admin123 | Administrator |
| john_doe | john@example.com | john123 | Regular User |
| jane_smith | jane@example.com | jane123 | Regular User |
| bob_wilson | bob@example.com | bob123 | Regular User |

## 📝 Sample Data

The seeding process creates:

- **4 Users** (1 admin + 3 regular users)
- **4 Homes** (1 for each user)
- **16 Rooms** (4 rooms per home)
- **12+ Devices** (Lights, fans, cameras, sensors)
- **8 Activity Logs** (System events, device interactions, warnings)

### Device Types

- **LIGHT**: Smart LED lights with on/off control
- **FAN**: Ceiling fans with speed control (0-3 levels)
- **CAMERA**: Security cameras with RTSP streaming
- **SENSOR**: Motion/temperature sensors

## 🔧 Troubleshooting

### Common Issues

1. **Connection Error**
   ```
   ❌ Failed to connect to MongoDB
   ```
   **Solution**: Check if MongoDB is running and `MONGODB_URL` is correct

2. **Import Error**
   ```
   ModuleNotFoundError: No module named 'app'
   ```
   **Solution**: Run scripts from the `backend` directory or adjust Python path

3. **Permission Error**
   ```
   pymongo.errors.OperationFailure: not authorized
   ```
   **Solution**: Check database user permissions in MongoDB

4. **Duplicate Key Error**
   ```
   pymongo.errors.DuplicateKeyError
   ```
   **Solution**: Data already exists. Run with `--reset` flag or use database manager

### Environment Setup

For Docker development environment:

```bash
# Start MongoDB
docker-compose up -d mongodb

# Setup database
python setup_database.py

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### MongoDB Setup

If you need to set up MongoDB locally:

```bash
# Install MongoDB (Ubuntu/Debian)
sudo apt-get install mongodb

# Start MongoDB service
sudo systemctl start mongodb

# Or using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

## 🛠️ Advanced Usage

### Custom Seeding

Modify `app/database/seed.py` to add your own sample data:

```python
async def create_custom_data():
    # Add your custom seeding logic here
    pass
```

### Indexes

The migration automatically creates indexes for:

- `users.username` (unique)
- `users.email` (unique)  
- `sessions.refreshToken` (unique)
- `devices.controllerDeviceMAC` (unique)
- Various foreign key fields for performance

### Database Reset

To completely reset the database:

```bash
python -m app.database.db_manager reset
```

This will delete all collections and data.

## 📈 Performance Tips

1. **Indexes**: Already created for common query patterns
2. **Connection Pooling**: Handled by Motor async driver
3. **Bulk Operations**: Used for efficient seeding
4. **Async/Await**: Non-blocking database operations

## 🔄 Development Workflow

For development, typical workflow:

1. Make changes to models
2. Reset database: `python -m app.database.db_manager reset`
3. Run setup: `python setup_database.py`
4. Start development server: `uvicorn app.main:app --reload`

## 📚 API Testing

After setup, test the API:

```bash
# Health check
curl http://localhost:8000/

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

---

For more information, check the API documentation at `/api/v1/docs` when the server is running.
