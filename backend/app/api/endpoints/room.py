from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.api import deps
from app.api.utils import room_to_response
from app.models.user import User
from app.schemas.room import RoomCreate, RoomUpdate, RoomResponse
from app.services.room import RoomService
from app.services.activity_log import ActivityLogService

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
    
    # Ghi log
    await ActivityLogService.create_log(
        action="CREATE_ROOM",
        message=f"Created room: {room.name}",
        userId=str(current_user.id),
        homeId=str(room.homeId)
    )
    
    return room_to_response(room)

@router.get("/", response_model=List[RoomResponse])
async def read_rooms(
    homeId: str,
    current_user: User = Depends(deps.get_current_user)
):
    rooms = await RoomService.get_rooms_by_home(homeId, current_user)
    return [room_to_response(room) for room in rooms]

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
    return room_to_response(room)

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
    return room_to_response(room)

@router.delete("/{room_id}", status_code=status.HTTP_200_OK)
async def delete_room(
    room_id: str,
    current_user: User = Depends(deps.get_current_user)
):
    # Lấy thông tin room trước khi xóa
    room = await RoomService.get_room_by_id(room_id, current_user)
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found or you don't have permission"
        )
    
    room_name = room.name
    home_id = str(room.homeId)
    success = await RoomService.delete_room(room_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found or you don't have permission"
        )
    
    # Ghi log
    await ActivityLogService.create_log(
        action="DELETE_ROOM",
        message=f"Deleted room: {room_name}",
        userId=str(current_user.id),
        homeId=home_id
    )
    
    return {"message": "Room deleted successfully"}

