from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.api import deps
from app.models.user import User
from app.schemas.room import RoomCreate, RoomUpdate, RoomResponse

router = APIRouter()

@router.post("/", response_model=RoomResponse)
async def create_room(
    room_in: RoomCreate,
    current_user: User = Depends(deps.get_current_user)
):
    # TODO: Verify home ownership
    # TODO: Create room
    pass

@router.get("/", response_model=List[RoomResponse])
async def read_rooms(
    homeId: str,
    current_user: User = Depends(deps.get_current_user)
):
    # TODO: Get rooms by homeId
    pass

@router.get("/{room_id}", response_model=RoomResponse)
async def read_room(
    room_id: str,
    current_user: User = Depends(deps.get_current_user)
):
    # TODO: Get specific room
    pass

@router.put("/{room_id}", response_model=RoomResponse)
async def update_room(
    room_id: str,
    room_in: RoomUpdate,
    current_user: User = Depends(deps.get_current_user)
):
    # TODO: Update room
    pass

@router.delete("/{room_id}")
async def delete_room(
    room_id: str,
    current_user: User = Depends(deps.get_current_user)
):
    # TODO: Delete room
    pass