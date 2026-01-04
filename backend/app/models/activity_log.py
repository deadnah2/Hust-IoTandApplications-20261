from beanie import Document, PydanticObjectId
from typing import Optional
from datetime import datetime
from pydantic import Field

class LogType:
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

class ActivityLog(Document):
    homeId: Optional[PydanticObjectId] = None
    userId: Optional[PydanticObjectId] = None
    type: str = Field(default=LogType.INFO)
    action: str  # "LOGIN", "CREATE_HOME", "DELETE_HOME", "CREATE_ROOM", etc.
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "activity_logs"
