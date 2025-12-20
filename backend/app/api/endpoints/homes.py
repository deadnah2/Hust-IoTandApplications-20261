from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.api import deps
from app.models.user import User
from app.schemas.home import HomeCreate, HomeUpdate, HomeResponse

router = APIRouter()

@router.post("/", response_model=HomeResponse)
async def create_home(
    home_in: HomeCreate,
    current_user: User = Depends(deps.get_current_user)
):
    # TODO: Create home linked to current_user
    pass

@router.get("/", response_model=List[HomeResponse])
async def read_homes(
    current_user: User = Depends(deps.get_current_user)
):
    # TODO: Get all homes owned by current_user
    pass

@router.get("/{home_id}", response_model=HomeResponse)
async def read_home(
    home_id: str,
    current_user: User = Depends(deps.get_current_user)
):
    # TODO: Get specific home if owned by user
    pass

@router.put("/{home_id}", response_model=HomeResponse)
async def update_home(
    home_id: str,
    home_in: HomeUpdate,
    current_user: User = Depends(deps.get_current_user)
):
    # TODO: Update home logic
    pass

@router.delete("/{home_id}")
async def delete_home(
    home_id: str,
    current_user: User = Depends(deps.get_current_user)
):
    # TODO: Delete home logic
    pass