from beanie import Document, Indexed
from typing import Optional
from datetime import datetime
from pydantic import EmailStr, Field

class User(Document):
    username: Indexed(str, unique=True)
    email: Optional[Indexed(EmailStr, unique=True)] = None
    passwordHash: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
