from beanie import Document, PydanticObjectId
from typing import Optional
from datetime import datetime

class Home(Document):
    ownerUserId: PydanticObjectId
    name: str
    location: Optional[str] = None
    createdAt: datetime = datetime.utcnow()
    updatedAt: datetime = datetime.utcnow()

    class Settings:
        name = "homes"
