from pydantic import BaseModel, EmailStr
from typing import Optional

# DTO
class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    login: str
    email: Optional[EmailStr] = None
    password: str

class UserResponse(BaseModel):
    id: str
    login: str
    email: Optional[str] = None

class Token(BaseModel):
    id_token: str
    refresh_token: str
    user: Optional[UserResponse] = None

class RefreshTokenRequest(BaseModel):
    refreshToken: str
