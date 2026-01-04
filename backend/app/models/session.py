from beanie import Document, PydanticObjectId, Indexed
from datetime import datetime
from pydantic import Field

class Session(Document):
    userId: Indexed(PydanticObjectId)
    refreshToken: Indexed(str, unique=True)
    expiresAt: datetime
    createdAt: datetime = Field(default_factory=datetime.utcnow)  # Keep UTC for consistency with JWT

    class Settings:
        name = "sessions"
