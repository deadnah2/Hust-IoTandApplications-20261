from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.api import deps
from app.models.user import User
from app.schemas.room import RoomCreate, RoomUpdate, RoomResponse
from app.services.room import RoomService

router = APIRouter()

@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    room_in: RoomCreate,
    current_user: User = Depends(deps.get_current_user)
):
    room = await RoomService.create_room(room_in, current_user)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to add rooms to this home"
        )
    # Convert ids to string
    return RoomResponse(
        id=str(room.id),
        name=room.name,
        homeId=str(room.homeId),
        createdAt=room.createdAt,
        updatedAt=room.updatedAt
    )

@router.get("/", response_model=List[RoomResponse])
async def read_rooms(
    homeId: str,
    current_user: User = Depends(deps.get_current_user)
):
    rooms = await RoomService.get_rooms_by_home(homeId, current_user)
    # Convert ids to string
    return [
        RoomResponse(
            id=str(room.id),
            name=room.name,
            homeId=str(room.homeId),
            createdAt=room.createdAt,
            updatedAt=room.updatedAt
        )
        for room in rooms
    ]

@router.get("/{room_id}", response_model=RoomResponse)
async def read_room(
    room_id: str,
    current_user: User = Depends(deps.get_current_user)
):
    room = await RoomService.get_room_by_id(room_id, current_user)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found or you don't have permission"
        )
    return RoomResponse(
        id=str(room.id),
        name=room.name,
        homeId=str(room.homeId),
        createdAt=room.createdAt,
        updatedAt=room.updatedAt
    )

@router.put("/{room_id}", response_model=RoomResponse)
async def update_room(
    room_id: str,
    room_in: RoomUpdate,
    current_user: User = Depends(deps.get_current_user)
):
    room = await RoomService.update_room(room_id, room_in, current_user)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found or you don't have permission"
        )
    return RoomResponse(
        id=str(room.id),
        name=room.name,
        homeId=str(room.homeId),
        createdAt=room.createdAt,
        updatedAt=room.updatedAt
    )

@router.delete("/{room_id}", status_code=status.HTTP_200_OK)
async def delete_room(
    room_id: str,
    current_user: User = Depends(deps.get_current_user)
):
    success = await RoomService.delete_room(room_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found or you don't have permission"
        )
    return {"message": "Room deleted successfully"}