from beanie import Document, Link
from datetime import datetime
from app.models.user import User

class Session(Document):
    user: Link[User]
    resetToken: str
    expires_at: datetime
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "sessions"
