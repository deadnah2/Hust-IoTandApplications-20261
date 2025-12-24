from beanie import Document, PydanticObjectId, Indexed
from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import Field

class DeviceType(str, Enum):
    LIGHT = "LIGHT"
    FAN = "FAN"
    CAMERA = "CAMERA"
    SENSOR = "SENSOR"

class DeviceStatus(str, Enum):
    ON = "ON"
    OFF = "OFF"

class Device(Document):
    roomId: Optional[Indexed(PydanticObjectId)] = None
    name: str
    controllerDeviceMAC: Optional[Indexed(str, unique=True)] = None
    bssid: Optional[str] = None
    type: str = Field(default=DeviceType.LIGHT)  # Store as string
    status: str = Field(default=DeviceStatus.OFF)  # Store as string
    speed: Optional[int] = 0 # For FAN: 0..3
    streamUrl: Optional[str] = None # For CAMERA
    humanDetectionEnabled: Optional[bool] = False
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "devices"
