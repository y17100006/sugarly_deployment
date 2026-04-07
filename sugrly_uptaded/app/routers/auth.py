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

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # التحقق من توكن سوبابيس
    payload = await verify_supabase_token(token)
    if not payload:
        raise credentials_exception
    
    user_id = payload.get("sub") # UUID الخاص بالمستخدم
    if user_id is None:
        raise credentials_exception
        
    # البحث عن المستخدم في جدول public.users الخاص بنا باستخدام الـ ID
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    
    if user is None:
        # إذا لم يكن المستخدم موجوداً في جدولنا (لكنه موجود في Auth.users)، 
        # هذا يعني أن الـ Trigger لم يعمل بعد أو أننا بحاجة لانتظار المزامنة.
        raise HTTPException(status_code=404, detail="User profile not found")
        
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
