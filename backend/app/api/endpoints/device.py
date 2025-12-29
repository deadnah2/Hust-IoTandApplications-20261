from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.api import deps
from app.models.user import User
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceResponse, DeviceCommand, NewDeviceInLAN
from app.services.device import DeviceService

router = APIRouter()

# Helper function to convert Device model to DeviceResponse
def device_to_response(device: Device) -> DeviceResponse:
    return DeviceResponse(
        id=str(device.id),
        roomId=str(device.roomId) if device.roomId else None,
        name=device.name,
        custom_name=device.custom_name,
        controllerMAC=device.controllerMAC,
        bssid=device.bssid,
        type=device.type,
        status=device.state,
        speed=device.speed,
        streamUrl=device.streamUrl,
        humanDetectionEnabled=device.humanDetectionEnabled,
        temperature=device.temperature,
        humidity=device.humidity,
        createdAt=device.createdAt,
        updatedAt=device.updatedAt
    )

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

@router.get("/lan", response_model=List[DeviceResponse])
async def get_new_devices_in_lan(
    bssid: str,
):
    devices = await DeviceService.get_new_devices_in_lan(bssid)
    return [device_to_response(device) for device in devices]

# Get unassigned devices (not in any room)
@router.get("/unassigned", response_model=List[DeviceResponse])
async def get_unassigned_devices(
    current_user: User = Depends(deps.get_current_user)
):
    """Get all devices not assigned to any room"""
    devices = await Device.find(Device.roomId == None).to_list()
    return [device_to_response(device) for device in devices]

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
    success = await DeviceService.send_command(device_id, command, current_user)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Device not found or you don't have permission"
        )
    return {"message": "Command sent successfully"}