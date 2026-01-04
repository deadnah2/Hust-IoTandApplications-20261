from beanie import Document, Indexed, PydanticObjectId
from typing import Optional, List
from datetime import datetime
from pydantic import EmailStr, Field

class User(Document):
    username: Indexed(str, unique=True)
    email: Optional[Indexed(EmailStr, unique=True)] = None
    passwordHash: str
    home_ids: Optional[List[PydanticObjectId]] = None
    createdAt: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "users"
