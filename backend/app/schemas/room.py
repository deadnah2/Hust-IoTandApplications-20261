from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RoomCreate(BaseModel):
    homeId: str
    name: str
    bssid: Optional[str] = None  # Override home's BSSID if different WiFi

class RoomUpdate(BaseModel):
    name: Optional[str] = None
    bssid: Optional[str] = None

class RoomResponse(BaseModel):
    id: str
    homeId: str
    name: str
    bssid: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
