from fastapi import APIRouter
from app.api.endpoints import auth, devices
from app.api.endpoints import home, room

api_router = APIRouter()
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(home.router, prefix="/homes", tags=["homes"])
api_router.include_router(room.router, prefix="/rooms", tags=["rooms"])
api_router.include_router(devices.router, prefix="/devices", tags=["devices"])


