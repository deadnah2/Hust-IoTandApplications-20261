from typing import List
from datetime import datetime
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.api import deps
from app.models.user import User
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceResponse, DeviceCommand, NewDeviceInLAN
from app.services.device import DeviceService
from app.services.camera import CameraStream
from app.api.utils import device_to_response
import asyncio
import cv2

logger = logging.getLogger(__name__)
router = APIRouter()
DEVICE_OFFLINE_SECONDS = 7

# GET specific endpoints BEFORE generic ones
@router.get("/lan", response_model=List[DeviceResponse])
async def get_new_devices_in_lan(
    bssid: str,
):
    devices = await DeviceService.get_new_devices_in_lan(bssid)
    logger.info(f"🔍 Found {len(devices)} devices in LAN with BSSID: {bssid}")
    for device in devices:
        logger.info(f"  - Device: {device.name} ({device.type}) - MAC: {device.controllerMAC}")
    return [device_to_response(device) for device in devices]

@router.get("/unassigned", response_model=List[DeviceResponse])
async def get_unassigned_devices(
    current_user: User = Depends(deps.get_current_user)
):
    """Get all devices not assigned to any room"""
    devices = await Device.find(Device.roomId == None).to_list()
    return [device_to_response(device) for device in devices]

@router.get("/camera-stream")
async def camera_stream(
    device_id: str,
    current_user: User = Depends(deps.get_current_user)
):
    device = await DeviceService.get_device_by_id(device_id, current_user)
    if not device or not device.streamUrl:
        raise HTTPException(
            status_code=404,
            detail="Device not found or no stream URL"
        )

    # Khởi tạo CameraStream với detection bật
    stream = CameraStream(device.streamUrl, humanDetectionMode=True)
    stream.start()

    async def generate():
        try:
            while True:
                frame = stream.get_processed_frame()
                if frame is not None:
                    ret, buffer = cv2.imencode('.jpg', frame)
                    if ret:
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                await asyncio.sleep(0.1)  # Tránh loop quá nhanh
        finally:
            stream.stop()

    return StreamingResponse(generate(), media_type='multipart/x-mixed-replace; boundary=frame')

# Generic endpoints AFTER specific ones
# for testing
@router.post("/", response_model=DeviceResponse)
async def create_device(
    device_in: DeviceCreate,
    current_user: User = Depends(deps.get_current_user)
):
    device = await DeviceService.create_device(device_in)
    if not device:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to add device to this room"
        )
    return device_to_response(device)

@router.get("/", response_model=List[DeviceResponse])
async def read_devices(
    roomId: str,
    current_user: User = Depends(deps.get_current_user)
):
    devices = await DeviceService.get_devices_by_room(roomId, current_user)
    return [device_to_response(device) for device in devices]

@router.get("/{device_id}", response_model=DeviceResponse)
async def read_device(
    device_id: str,
    current_user: User = Depends(deps.get_current_user)
):
    device = await DeviceService.get_device_by_id(device_id, current_user)
    if not device:
        raise HTTPException(
            status_code=404,
            detail="Device not found or you don't have permission"
        )
    return device_to_response(device)

@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: str,
    device_in: DeviceUpdate,
    current_user: User = Depends(deps.get_current_user)
):
    device = await DeviceService.update_device(device_id, device_in, current_user)
    if not device:
        raise HTTPException(
            status_code=404,
            detail="Device not found or you don't have permission"
        )
    return device_to_response(device)

@router.delete("/{device_id}")
async def delete_device(
    device_id: str,
    current_user: User = Depends(deps.get_current_user)
):
    success = await DeviceService.delete_device(device_id, current_user)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Device not found or you don't have permission"
        )
    return {"message": "Device deleted successfully"}

@router.post("/{device_id}/command")
async def send_command(
    device_id: str,
    command: DeviceCommand,
    current_user: User = Depends(deps.get_current_user)
):
    logger.info(f"📤 Device command: {device_id} - Action: {command.action}")
    success = await DeviceService.send_command(device_id, command, current_user)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Device not found or you don't have permission"
        )
    logger.info(f"✅ Command executed successfully for device: {device_id}")
    return {"message": "Command sent successfully"}