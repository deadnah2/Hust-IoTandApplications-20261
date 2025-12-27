from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.device import DeviceType, DeviceState

class NewDeviceInLAN(BaseModel):
    bssid: str

class DeviceCreate(BaseModel):
    roomId: Optional[str] = None
    name: str
    custom_name: Optional[str] = ""
    controllerMAC: Optional[str] = None
    bssid: str
    type: DeviceType
    speed: Optional[int] = 0
    streamUrl: Optional[str] = None
    humanDetectionEnabled: Optional[bool] = False

class DeviceUpdate(BaseModel):
    custom_name: Optional[str] = None
    roomId: Optional[str] = None

class DeviceCommand(BaseModel):
    action: str  # ON, OFF, SET_SPEED
    speed: Optional[int] = None

class HumanDetectionCommand(BaseModel):
    enabled: bool

class DeviceResponse(BaseModel):
    id: str
    roomId: Optional[str] = None
    name: str
    custom_name: str
    controllerMAC: Optional[str] = None
    bssid: Optional[str] = None
    type: DeviceType
    status: DeviceState
    speed: Optional[int] = None
    streamUrl: Optional[str] = None
    humanDetectionEnabled: Optional[bool] = None
    createdAt: datetime
    updatedAt: datetime

