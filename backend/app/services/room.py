from typing import List, Optional
from datetime import datetime
from app.models.home import Home
from app.models.room import Room
from app.models.user import User
from app.schemas.room import RoomCreate, RoomUpdate
from app.services.home import HomeService
from beanie import PydanticObjectId

class RoomService:
    @staticmethod
    async def create_room(room_in: RoomCreate, user: User) -> Optional[Room]:
        home = await HomeService.get_home_by_id(room_in.homeId, user)
        if not home:
            return None  # Or raise HTTPException
        
        room = Room(**room_in.model_dump())
        await room.create()
        return room

    @staticmethod
    async def get_rooms_by_home(home_id: str, user: User) -> List[Room]:
        home = await HomeService.get_home_by_id(home_id, user)
      
        if not home:
            return []  # Or raise HTTPException
        
        rooms = await Room.find(Room.homeId == PydanticObjectId(home_id)).to_list()
    
        return rooms

    @staticmethod
    async def get_room_by_id(room_id: str, user: User) -> Optional[Room]:
        room = await Room.get(room_id)
        if room:
            # Verify user has access to the home this room is in
            home = await HomeService.get_home_by_id(room.homeId, user)
            if home:
                return room
        return None

    @staticmethod
    async def update_room(room_id: str, room_in: RoomUpdate, user: User) -> Optional[Room]:
        room = await RoomService.get_room_by_id(room_id, user)
        if room:
            update_data = room_in.model_dump(exclude_unset=True)
            update_data["updatedAt"] = datetime.utcnow()
            await room.update({"$set": update_data})
            for key, value in update_data.items():
                setattr(room, key, value)
        return room

    @staticmethod
    async def delete_room(room_id: str, user: User) -> bool:
        room = await RoomService.get_room_by_id(room_id, user)
        if room:
            # Note: This doesn't delete devices within the room.
            await room.delete()
            return True
        return False
