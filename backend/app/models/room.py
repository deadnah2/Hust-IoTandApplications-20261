from beanie import Document, PydanticObjectId, Indexed
from typing import Optional
from datetime import datetime
from pydantic import Field

class Room(Document):
    homeId: Indexed(PydanticObjectId)
    name: str
    bssid: Optional[str] = None  # Override home's BSSID if room uses different WiFi
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "rooms"
