from pydantic import BaseModel, EmailStr
from typing import Optional

# DTO
class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: Optional[str] = None

class Token(BaseModel):
    id_token: str
    refresh_token: str
    user: Optional[UserResponse] = None

class RefreshTokenRequest(BaseModel):
    refreshToken: str
