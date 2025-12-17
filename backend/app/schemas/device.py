from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class DeviceBase(BaseModel):
    name: str
    type: str
    status: Optional[str] = "offline"
    data: Optional[Dict[str, Any]] = {}

class DeviceCreate(DeviceBase):
    room_id: str

class DeviceUpdate(DeviceBase):
    name: Optional[str] = None
    type: Optional[str] = None
    room_id: Optional[str] = None

class DeviceResponse(DeviceBase):
    id: str
    room_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
