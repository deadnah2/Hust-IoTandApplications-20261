import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.core.config import settings
from app.api.api import api_router
from app.models.user import User
from app.models.session import Session
from app.models.home import Home
from app.models.room import Room
from app.models.device import Device
from app.models.activity_log import ActivityLog

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
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
    yield
    # Shutdown

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set all CORS enabled origins
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Nhóm các api lại dưới 
app.include_router(api_router, prefix=settings.API_V1_STR) 

@app.get("/")
def root():
    return {"message": "Welcome to IoT Application Backend"}


if __name__ == "__main__":
    import uvicorn
    import socket

    host = "0.0.0.0"
    port = 8000

    def get_local_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    local_ip = get_local_ip()

    print(f"Server running on:")
    print(f"  - Local:   http://localhost:{port}")
    print(f"  - Network: http://{local_ip}:{port}")

    uvicorn.run("app.main:app", host=host, port=port, reload=True)

