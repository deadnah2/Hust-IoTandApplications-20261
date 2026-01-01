from app.models.home import Home
from app.models.room import Room
from app.models.device import Device
from app.schemas.home import HomeResponse
from app.schemas.room import RoomResponse
from app.schemas.device import DeviceResponse

def home_to_response(home: Home) -> HomeResponse:
    return HomeResponse(
        id=str(home.id),
        name=home.name,
        location=home.location,
        ownerUserId=str(home.ownerUserId),
        createdAt=home.createdAt,
        updatedAt=home.updatedAt
    )


def room_to_response(room: Room) -> RoomResponse:
    return RoomResponse(
        id=str(room.id),
        name=room.name,
        homeId=str(room.homeId),
        createdAt=room.createdAt,
        updatedAt=room.updatedAt
    )

def device_to_response(device: Device) -> DeviceResponse:
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
        streamUrl=device.streamUrl,
        humanDetectionEnabled=device.humanDetectionEnabled,
        temperature=device.temperature,
        humidity=device.humidity,
        createdAt=device.createdAt,
        updatedAt=device.updatedAt
    )