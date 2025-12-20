from beanie import Document, PydanticObjectId, Indexed
from typing import Optional
from datetime import datetime
from enum import Enum

class DeviceType(str, Enum):
    LIGHT = "LIGHT"
    FAN = "FAN"
    CAMERA = "CAMERA"

class DeviceStatus(str, Enum):
    ON = "ON"
    OFF = "OFF"

class Device(Document):
    roomId: Optional[PydanticObjectId] = None
    name: str
    controllerDeviceMAC: Optional[Indexed(str, unique=True)] = None
    bssid: Optional[str] = None
    type: DeviceType
    status: DeviceStatus = DeviceStatus.OFF
    speed: Optional[int] = 0 # For FAN: 0..3
    streamUrl: Optional[str] = None # For CAMERA
    humanDetectionEnabled: Optional[bool] = False
    createdAt: datetime = datetime.utcnow()
    updatedAt: datetime = datetime.utcnow()

    class Settings:
        name = "devices"
