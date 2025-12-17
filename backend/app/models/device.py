from beanie import Document, Link
from typing import Optional, Any, Dict
from datetime import datetime
from app.models.room import Room

class Device(Document):
    name: str
    type: str
    room: Link[Room]
    status: str = "offline"
    data: Dict[str, Any] = {}
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "devices"
