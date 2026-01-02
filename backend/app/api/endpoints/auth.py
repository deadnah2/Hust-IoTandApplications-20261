from fastapi import APIRouter, Depends, HTTPException, status, Response
from starlette.responses import JSONResponse # Sửa dòng này
from app.schemas.auth import (
    UserRegister,
    UserResponse,
    Token,
    RefreshTokenRequest,
    UserLogin,
)
from app.api import deps
from app.models.user import User
from app.services.auth import AuthService
from app.services.activity_log import ActivityLogService
from app.services.home import HomeService

router = APIRouter()

# Decorator đã chỉ ra response_model ==> Lấy các trường cần thiết, tự động gói vào một JSONResponse
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserRegister):
    """
    Register a new user.
    """
    try:
        user = await AuthService.register_user(user_in)
        # Ép kiểu ObjectId về str trước khi trả về để khớp với UserResponse schema
        return UserResponse(**user.dict(exclude={'id'}), id=str(user.id))
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"detail": e.detail}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, # For unexpected errors
            detail="An unexpected error occurred during registration."
        )


@router.post("/authenticate", response_model=Token)
async def login(user_in: UserLogin):
    """
    Authenticate user and return tokens.
    """
    user = await AuthService.authenticate_user(
        username=user_in.username, password=user_in.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Ghi log đăng nhập vào TẤT CẢ homes của user
    user_homes = await HomeService.get_user_homes(user)
    for home in user_homes:
        await ActivityLogService.create_log(
            action="LOGIN",
            message=f"User {user.username} logged in",
            userId=str(user.id),
            homeId=str(home.id)
        )
    
    access_token, refresh_token = await AuthService.create_tokens(user)
    return Token(
        access_token=access_token, 
        refresh_token=refresh_token, 
        user=UserResponse(**user.dict(exclude={'id'}), id=str(user.id))
    )


@router.post("/refresh-token", response_model=Token)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token.
    """
    new_access_token = await AuthService.refresh_access_token(request.refreshToken)
    if not new_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    return Token(access_token=new_access_token, refresh_token=request.refreshToken)

# gửi refresh token về server giúp duy trì nhiều phiên đăng nhập
@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    request: RefreshTokenRequest,
    current_user: User = Depends(deps.get_current_user)
):
    """
    Logout user by deleting session.
    """
    # Ghi log logout vào TẤT CẢ homes của user TRƯỚC KHI xóa session
    user_homes = await HomeService.get_user_homes(current_user)
    for home in user_homes:
        await ActivityLogService.create_log(
            action="LOGOUT",
            message=f"User {current_user.username} logged out",
            userId=str(current_user.id),
            homeId=str(home.id)
        )
    
    # Xóa session SAU KHI đã ghi log xong
    await AuthService.logout(request.refreshToken)
    
    return {"message": "Logged out successfully"}

# Lấy access token từ header ==> giải mã ra current_user ==> trả về chính đối tượng này
@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(deps.get_current_user)):
    """
    Get current user.
    """
    return UserResponse(**current_user.dict(exclude={'id'}), id=str(current_user.id))