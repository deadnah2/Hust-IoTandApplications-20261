from beanie import Document, PydanticObjectId
from typing import Optional
from datetime import datetime

class Room(Document):
    homeId: PydanticObjectId
    name: str
    createdAt: datetime = datetime.utcnow()
    updatedAt: datetime = datetime.utcnow()

    class Settings:
        name = "rooms"
