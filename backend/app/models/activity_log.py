from beanie import Document, PydanticObjectId, Indexed
from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import Field

class LogType(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

class ActivityLog(Document):
    userId: Optional[PydanticObjectId] = None
    homeId: Optional[PydanticObjectId] = None
    roomId: Optional[Indexed(PydanticObjectId)] = None
    deviceId: Optional[Indexed(PydanticObjectId)] = None
    type: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "activity_logs"
