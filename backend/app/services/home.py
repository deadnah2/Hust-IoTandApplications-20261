from typing import List, Optional
from datetime import datetime
from beanie.operators import In
from beanie import PydanticObjectId
from bson.errors import InvalidId
from app.models.home import Home
from app.models.user import User
from app.schemas.home import HomeCreate, HomeUpdate

class HomeService:
    @staticmethod
    async def create_home(home_in: HomeCreate, user: User) -> Home:
        home = Home(**home_in.model_dump(), ownerUserId=user.id)
        await home.create()
        # Add home to user's home_ids
        if user.home_ids is None:
            user.home_ids = []
        user.home_ids.append(home.id)
        await user.save()
        return home

    @staticmethod
    async def get_user_homes(user: User) -> List[Home]:
        if not user.home_ids:
            return []
        homes = await Home.find(In(Home.id, user.home_ids)).to_list()
        return homes

    @staticmethod
    async def get_home_by_id(home_id: str, user: User) -> Optional[Home]:
        try:
            home_obj_id = PydanticObjectId(home_id)
        except InvalidId:
            return None
            
        if user.home_ids and home_obj_id in user.home_ids:
            home = await Home.get(home_obj_id)
            return home
        return None

    @staticmethod
    async def update_home(home_id: str, home_in: HomeUpdate, user: User) -> Optional[Home]:
        home = await HomeService.get_home_by_id(home_id, user)
        if home:
            update_data = home_in.model_dump(exclude_unset=True)
            update_data["updatedAt"] = datetime.utcnow()
            await home.update({"$set": update_data})
            for key, value in update_data.items():
                setattr(home, key, value)
        return home

    @staticmethod
    async def delete_home(home_id: str, user: User) -> bool:
        home = await HomeService.get_home_by_id(home_id, user)
        if not home:
            return False
            
        # home.id is already a PydanticObjectId, no conversion needed here
        if user.home_ids and home.id in user.home_ids:
            user.home_ids.remove(home.id)
            await user.save()
            
            # Note: This doesn't delete rooms or devices within the home.
            # A more robust implementation would handle that.
            await home.delete()
            return True
        return False
