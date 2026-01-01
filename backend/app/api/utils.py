from datetime import datetime
from app.models.home import Home
from app.models.room import Room
from app.models.device import Device
from app.schemas.home import HomeResponse
from app.schemas.room import RoomResponse
from app.schemas.device import DeviceResponse

DEVICE_OFFLINE_SECONDS = 7

def home_to_response(home: Home) -> HomeResponse:
    return HomeResponse(
        id=str(home.id),
        name=home.name,
        location=home.location,
        bssid=home.bssid,
        ownerUserId=str(home.ownerUserId),
        createdAt=home.createdAt,
        updatedAt=home.updatedAt
    )


def room_to_response(room: Room) -> RoomResponse:
    return RoomResponse(
        id=str(room.id),
        name=room.name,
        homeId=str(room.homeId),
        bssid=room.bssid,
        createdAt=room.createdAt,
        updatedAt=room.updatedAt
    )

def device_to_response(device: Device) -> DeviceResponse:
    # Xác định trạng thái online dựa trên lastSeen
    is_online = None
    device_type = str(device.type).strip().upper()
    if device_type in ("SENSOR", "FAN"):
        if device.lastSeen is None:
            is_online = False
        else:
            delta = datetime.utcnow() - device.lastSeen
            is_online = delta.total_seconds() <= DEVICE_OFFLINE_SECONDS

    return DeviceResponse(
        id=str(device.id),
        roomId=str(device.roomId) if device.roomId else None,
        name=device.name,
        custom_name=device.custom_name,
        controllerMAC=device.controllerMAC,
        bssid=device.bssid,
        type=device.type,
        state=device.state,
        speed=device.speed,
        humanDetectionEnabled=device.humanDetectionEnabled,
        temperature=device.temperature,
        humidity=device.humidity,
        lastSeen=device.lastSeen,
        isOnline=is_online,
        createdAt=device.createdAt,
        updatedAt=device.updatedAt
    )