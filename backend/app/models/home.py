from beanie import Document, Link
from typing import Optional, List
from datetime import datetime
from app.models.user import User

class Home(Document):
    name: str
    address: Optional[str] = None
    owner: Link[User]
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "homes"
