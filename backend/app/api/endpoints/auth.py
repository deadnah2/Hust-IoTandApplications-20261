from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.auth import UserRegister, UserResponse, Token, RefreshTokenRequest
from app.api import deps
from app.models.user import User

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user_in: UserRegister):
    # TODO: Check if user exists
    # TODO: Hash password
    # TODO: Create user in DB
    pass

@router.post("/authenticate", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # TODO: Authenticate user
    # TODO: Create access token & refresh token
    # TODO: Save session
    pass

@router.post("/refresh-token", response_model=Token)
async def refresh_token(request: RefreshTokenRequest):
    # TODO: Verify refresh token
    # TODO: Rotate tokens
    pass

@router.post("/logout")
async def logout(request: RefreshTokenRequest):
    # TODO: Delete session
    pass

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(deps.get_current_user)):
    return current_user