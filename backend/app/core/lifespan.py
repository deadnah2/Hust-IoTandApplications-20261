from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.database import init_db
from app.core.mqtt import connect_mqtt, disconnect_mqtt


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Quản lý vòng đời ứng dụng: khởi tạo và dọn dẹp tài nguyên
    """
    # Startup
    await init_db()
    connect_mqtt()
    print("Application startup complete")
    
    yield
    
    # Shutdown
    disconnect_mqtt()
    print("Application shutdown complete")
