from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.api import deps
from app.models.user import User
from app.schemas.home import HomeCreate, HomeUpdate, HomeResponse
from app.services.home import HomeService

router = APIRouter()

@router.post("/", response_model=HomeResponse, status_code=status.HTTP_201_CREATED)
async def create_home(
    home_in: HomeCreate,
    current_user: User = Depends(deps.get_current_user)
):
    home = await HomeService.create_home(home_in, current_user)
    # Convert id to string
    return HomeResponse(
        id=str(home.id),
        name=home.name,
        location=home.location,
        ownerUserId=str(home.ownerUserId),
        createdAt=home.createdAt,
        updatedAt=home.updatedAt
    )

@router.get("/", response_model=List[HomeResponse])
async def read_homes(
    current_user: User = Depends(deps.get_current_user)
):
    homes = await HomeService.get_user_homes(current_user)
    # Convert ids to string
    return [
        HomeResponse(
            id=str(home.id),
            name=home.name,
            location=home.location,
            ownerUserId=str(home.ownerUserId),
            createdAt=home.createdAt,
            updatedAt=home.updatedAt
        )
        for home in homes
    ]

# Path parameter: /api/v1/homes/694df4cb4a1a397bb61ac1b6
# Query parameter: /api/v1/homes/?home_id=694df4cb4a1a397bb61ac1b6
@router.get("/{home_id}", response_model=HomeResponse) # path param
async def read_home(
    home_id: str,
    current_user: User = Depends(deps.get_current_user)
):
    home = await HomeService.get_home_by_id(home_id, current_user)
    if not home:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Home not found"
        )

    return HomeResponse(
        id=str(home.id),
        name=home.name,
        location=home.location,
        ownerUserId=str(home.ownerUserId),
        createdAt=home.createdAt,
        updatedAt=home.updatedAt
    )

@router.put("/{home_id}", response_model=HomeResponse)
async def update_home(
    home_id: str,
    home_in: HomeUpdate,
    current_user: User = Depends(deps.get_current_user)
):
    home = await HomeService.update_home(home_id, home_in, current_user)
    if not home:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Home not found or you don't have permission"
        )
    return HomeResponse(
        id=str(home.id),
        name=home.name,
        location=home.location,
        ownerUserId=str(home.ownerUserId),
        createdAt=home.createdAt,
        updatedAt=home.updatedAt
    )

@router.delete("/{home_id}", status_code=status.HTTP_200_OK)
async def delete_home(
    home_id: str,
    current_user: User = Depends(deps.get_current_user)
):
    success = await HomeService.delete_home(home_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Home not found or you don't have permission"
        )
    return {"message": "Home deleted successfully"}