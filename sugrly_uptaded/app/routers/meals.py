from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from app.models.database import get_db
from app.models.models import User, Meal, InsulinRecord
from app.schemas.meal import MealCreate, MealResponse, MealUpdate
import uuid
from app.routers.auth import get_current_user

router = APIRouter(prefix="/meals", tags=["meals"])

@router.post("/", response_model=MealResponse)
async def create_meal(
    meal_in: MealCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(InsulinRecord)
        .where(InsulinRecord.user_id == current_user.id)
        .order_by(InsulinRecord.created_at.desc())
        .limit(1)
    )
    insulin_record = result.scalars().first()
    
    if not insulin_record:
        raise HTTPException(status_code=400, detail="Please enter insulin data first before adding a meal")
        
    if meal_in.insulin_dose_taken > insulin_record.remaining_units:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot add {meal_in.insulin_dose_taken} units. Only {insulin_record.remaining_units} units remaining"
        )
        
    new_meal = Meal(
        user_id=current_user.id,
        description=meal_in.description,
        total_carbs=meal_in.total_carbs,
        insulin_dose_taken=meal_in.insulin_dose_taken,
        sugar_before=meal_in.sugar_before,
        sugar_after=meal_in.sugar_after,
        meal_type=meal_in.meal_type
    )
    
    try:
        insulin_record.remaining_units -= meal_in.insulin_dose_taken
        db.add(new_meal)
        await db.commit()
        await db.refresh(new_meal)
        return new_meal
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="One or more provided Sugar Reading IDs are invalid or do not exist. Please use null if no reading is attached."
        )

@router.get("/", response_model=list[MealResponse])
async def get_meals(
    skip: int = 0, 
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Meal)
        .where(Meal.user_id == current_user.id)
        .order_by(Meal.timestamp.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

@router.patch("/{meal_id}", response_model=MealResponse)
async def update_meal(
    meal_id: uuid.UUID,
    meal_in: MealUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Meal).where(Meal.id == meal_id, Meal.user_id == current_user.id)
    )
    meal = result.scalars().first()
    
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
        
    update_data = meal_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(meal, key, value)
        
    await db.commit()
    await db.refresh(meal)
    return meal
