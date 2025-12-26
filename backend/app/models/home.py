from beanie import Document, PydanticObjectId, Indexed, before_event, Insert, Replace
from typing import Optional
from datetime import datetime
from pydantic import Field
# from beanie.odm.actions import Before, Insert, Replace

class Home(Document):
    ownerUserId: Indexed(PydanticObjectId)
    name: str
    location: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    @before_event(Insert)
    def set_creation_date(self):
        self.createdAt = datetime.utcnow()
        self.updatedAt = self.createdAt

    @before_event(Replace)
    def set_update_date(self):
        self.updatedAt = datetime.utcnow()

    class Settings:
        name = "homes"
