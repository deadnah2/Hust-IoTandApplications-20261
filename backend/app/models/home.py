from beanie import Document, PydanticObjectId, Indexed, before_event, Insert, Replace
from typing import Optional
from datetime import datetime
from pydantic import Field
# from beanie.odm.actions import Before, Insert, Replace

class Home(Document):
    ownerUserId: Indexed(PydanticObjectId)
    name: str
    location: Optional[str] = None
    bssid: Optional[str] = None  # WiFi BSSID for device discovery
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)

    @before_event(Insert)
    def set_creation_date(self):
        self.createdAt = datetime.now()
        self.updatedAt = self.createdAt

    @before_event(Replace)
    def set_update_date(self):
        self.updatedAt = datetime.now()

    class Settings:
        name = "homes"
