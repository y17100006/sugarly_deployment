from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from jose import jwt, JWTError

from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token, verify_supabase_token
from app.models.database import get_db
from app.models.models import User
from app.schemas.user import UserCreate, UserResponse, Token, ForgotPasswordRequest, ResetPasswordRequest, UserUpdate
from app.services.email_service import (
    send_verification_email, 
    send_reset_password_email,
    send_email_change_confirmation,
    send_new_email_verification
)

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/auth", tags=["auth"])
security_scheme = HTTPBearer()

import uuid

DEMO_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme), db: AsyncSession = Depends(get_db)):
    token = credentials.credentials
    
    user_id = None
    
    # 1. إذا كان التوكن ليس 'demo'، نحاول التحقق عبر Supabase
    if token.lower() not in ["demo", "test", "demo_token"]:
        payload = await verify_supabase_token(token)
        if payload:
            user_id_str = payload.get("sub")
            if user_id_str:
                try:
                    user_id = uuid.UUID(user_id_str)
                except ValueError:
                    user_id = None

    user = None
    
    # إذا نجحنا في جلب الـ user_id الخاص بـ Supabase
    if user_id:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
    
    # إذا لم يُعثر على المستخدم (أو التوكن demo/غير صالح في التست)، نستخدم أول مستخدم موجود في الداتابيز
    if user is None:
        result = await db.execute(select(User).limit(1))
        user = result.scalars().first()
        
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user profile found in database. Please register a user in Supabase first."
        )
        
    return user

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=UserResponse)
async def update_user_me(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    update_data = user_update.model_dump(exclude_unset=True)
    
    # تحديث البيانات السريرية في جدولنا
    for field, value in update_data.items():
        if field != "email": # الإيميل يتم تحديثه عبر سوبابيس وليس هنا
            setattr(current_user, field, value)
        
    await db.commit()
    await db.refresh(current_user)
    return current_user
