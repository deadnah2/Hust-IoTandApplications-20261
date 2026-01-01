from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class HomeCreate(BaseModel):
    name: str
    location: Optional[str] = None
    bssid: Optional[str] = None  # WiFi BSSID for device discovery

class HomeUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    bssid: Optional[str] = None

class HomeResponse(BaseModel):
    id: str
    ownerUserId: str
    name: str
    location: Optional[str] = None
    bssid: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
