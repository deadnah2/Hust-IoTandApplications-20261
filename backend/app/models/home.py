from beanie import Document, PydanticObjectId, Indexed
from typing import Optional
from datetime import datetime
from pydantic import Field

class Home(Document):
    ownerUserId: Indexed(PydanticObjectId)
    name: str
    location: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "homes"
