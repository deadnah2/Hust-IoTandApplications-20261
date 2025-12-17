from beanie import Document, Link
from typing import Optional
from datetime import datetime
from app.models.home import Home

class Room(Document):
    name: str
    home: Link[Home]
    description: Optional[str] = None
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "rooms"
