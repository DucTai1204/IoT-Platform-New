#auth/schemas.py
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class RegisterBody(BaseModel):
    ten: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    mat_khau: str = Field(..., min_length=1, max_length=128)

class LoginBody(BaseModel):
    email: EmailStr
    mat_khau: str

class TokenResponse(BaseModel):
    access_token: str
    # token_type: str = "bearer"
    user_id: int
    email: EmailStr
    ten: str
    vai_tro: str

class UserOut(BaseModel):
    id: int
    ten: str
    email: Optional[EmailStr]
    vai_tro: str
    ngay_tao: datetime
