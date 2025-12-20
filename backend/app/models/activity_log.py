from beanie import Document, PydanticObjectId
from typing import Optional
from datetime import datetime
from enum import Enum

class LogType(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

class ActivityLog(Document):
    userId: Optional[PydanticObjectId] = None
    homeId: Optional[PydanticObjectId] = None
    roomId: Optional[PydanticObjectId] = None
    deviceId: Optional[PydanticObjectId] = None
    type: LogType
    message: str
    timestamp: datetime = datetime.utcnow()

    class Settings:
        name = "activity_logs"
