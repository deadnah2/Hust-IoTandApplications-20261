from fastapi import APIRouter
from app.api.endpoints import auth, homes, rooms, devices, cameras

api_router = APIRouter()
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(homes.router, prefix="/homes", tags=["homes"])
api_router.include_router(rooms.router, prefix="/rooms", tags=["rooms"])
api_router.include_router(devices.router, prefix="/devices", tags=["devices"])


