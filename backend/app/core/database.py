from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.core.config import settings
from app.models.user import User
from app.models.session import Session
from app.models.home import Home
from app.models.room import Room
from app.models.device import Device
from app.models.activity_log import ActivityLog


async def init_db():
    """
    Khởi tạo kết nối MongoDB và Beanie ODM
    """
    client = AsyncIOMotorClient(settings.MONGODB_URL)
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
    print("Database initialized successfully")
