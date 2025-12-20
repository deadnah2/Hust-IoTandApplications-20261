from beanie import Document, PydanticObjectId, Indexed
from datetime import datetime

class Session(Document):
    userId: PydanticObjectId
    refreshToken: Indexed(str, unique=True)
    expiresAt: datetime
    createdAt: datetime = datetime.utcnow()

    class Settings:
        name = "sessions"
