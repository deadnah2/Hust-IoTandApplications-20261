from beanie import Document, Indexed
from typing import Optional
from datetime import datetime
from pydantic import EmailStr

class User(Document):
    login: Indexed(str, unique=True)
    email: Optional[Indexed(EmailStr, unique=True)] = None
    passwordHash: str
    createdAt: datetime = datetime.utcnow()

    class Settings:
        name = "users"
