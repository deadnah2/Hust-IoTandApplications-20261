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

class DeviceState(str, Enum):
    ON = "ON"
    OFF = "OFF"

class Device(Document):
    roomId: Optional[Indexed(PydanticObjectId)] = None
    name: str
    custom_name: str = ""
    controllerMAC: Optional[Indexed(str, unique=True)] = None
    bssid: str
    type: str = Field(default=DeviceType.LIGHT)  # Store as string
    state: str = Field(default=DeviceState.OFF)  # Store as string
    speed: Optional[int] = 0 # For FAN: 0..3
    humanDetectionEnabled: Optional[bool] = False
    streamUrl: Optional[str] = None
    temperature: Optional[float] = None  # For SENSOR: °C
    humidity: Optional[float] = None  # For SENSOR: %
    lastSeen: Optional[datetime] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "devices"
