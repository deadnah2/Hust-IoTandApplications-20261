from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.api import deps
from app.models.user import User
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceResponse, DeviceCommand

router = APIRouter()

@router.post("/", response_model=DeviceResponse)
async def create_device(
    device_in: DeviceCreate,
    current_user: User = Depends(deps.get_current_user)
):
    # TODO: Verify room ownership
    # TODO: Create device
    pass

@router.get("/", response_model=List[DeviceResponse])
async def read_devices(
    roomId: str,
    current_user: User = Depends(deps.get_current_user)
):
    # TODO: Get devices by roomId
    pass

@router.get("/{device_id}", response_model=DeviceResponse)
async def read_device(
    device_id: str,
    current_user: User = Depends(deps.get_current_user)
):
    # TODO: Get specific device
    pass

@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: str,
    device_in: DeviceUpdate,
    current_user: User = Depends(deps.get_current_user)
):
    # TODO: Update device info
    pass

@router.delete("/{device_id}")
async def delete_device(
    device_id: str,
    current_user: User = Depends(deps.get_current_user)
):
    # TODO: Delete device
    pass

@router.post("/{device_id}/command")
async def send_command(
    device_id: str,
    command: DeviceCommand,
    current_user: User = Depends(deps.get_current_user)
):
    # TODO: Verify ownership
    # TODO// filepath: /home/haidang/Desktop/SmartHome/backend/app/api/endpoints/devices.py
    pass