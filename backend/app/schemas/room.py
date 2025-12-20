from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RoomCreate(BaseModel):
    homeId: str
    name: str

class RoomUpdate(BaseModel):
    name: Optional[str] = None

class RoomResponse(BaseModel):
    id: str
    homeId: str
    name: str
    createdAt: datetime
    updatedAt: datetime
