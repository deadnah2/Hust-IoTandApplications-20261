from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.device import DeviceType, DeviceStatus

class DeviceCreate(BaseModel):
    roomId: str
    name: str
    type: DeviceType

class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    streamUrl: Optional[str] = None

class DeviceCommand(BaseModel):
    action: str # ON, OFF, SET_SPEED
    speed: Optional[int] = None

class HumanDetectionCommand(BaseModel):
    enabled: bool

class DeviceResponse(BaseModel):
    id: str
    roomId: Optional[str] = None
    name: str
    controllerDeviceMAC: Optional[str] = None
    bssid: Optional[str] = None
    type: DeviceType
    status: DeviceStatus
    speed: Optional[int] = None
    streamUrl: Optional[str] = None
    humanDetectionEnabled: Optional[bool] = None
    createdAt: datetime
    updatedAt: datetime

