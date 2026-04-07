from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.database import get_db
from app.models.models import SugarReading, User
from app.schemas.sugar import SugarReadingCreate, SugarReadingResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/sugar", tags=["sugar"])

@router.post("/", response_model=SugarReadingResponse)
async def create_sugar_reading(
    reading_in: SugarReadingCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_reading = SugarReading(
        user_id=current_user.id,
        sugar_level=reading_in.sugar_level,
        reading_type=reading_in.reading_type,
        notes=reading_in.notes
    )
    db.add(new_reading)
    
    # ربط القراءة بالوجبة الأخيرة تلقائياً إذا كانت القراءة بعد الأكل
    if reading_in.reading_type.value == "after_meal":
        from app.models.models import Meal
        meal_result = await db.execute(
            select(Meal)
            .where(Meal.user_id == current_user.id)
            .order_by(Meal.timestamp.desc())
            .limit(1)
        )
        last_meal = meal_result.scalars().first()
        
        if last_meal:
            last_meal.sugar_after = reading_in.sugar_level
    await db.commit()
    await db.refresh(new_reading)
    return new_reading

@router.get("/", response_model=List[SugarReadingResponse])
async def get_sugar_readings(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(SugarReading)
        .where(SugarReading.user_id == current_user.id)
        .order_by(SugarReading.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )
    readings = result.scalars().all()
    return readings
