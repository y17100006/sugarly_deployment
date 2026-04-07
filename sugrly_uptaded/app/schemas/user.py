from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    carb_ratio: Optional[float] = None
    sensitivity_factor: Optional[float] = None
    target_sugar: float = 100.0

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    carb_ratio: Optional[float] = None
    sensitivity_factor: Optional[float] = None
    target_sugar: Optional[float] = None

class UserResponse(UserBase):
    id: UUID

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
