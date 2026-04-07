from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, literal_column
from sqlalchemy.orm import aliased
from typing import Dict, List, Any
import datetime
from app.models.database import get_db
from app.models.models import User, SugarReading, Meal
from app.routers.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/hourly")
async def get_hourly_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, List[Dict[str, Any]]]:
    """
    يقوم بتجميع قراءات السكر والوجبات بالساعة لإرسالها جاهزة لرسومات الـ Charts
    """
    # تجميع متوسط السكر لكل ساعة
    sugar_query = (
        select(
            func.date_trunc('hour', SugarReading.timestamp).label('hour_bucket'),
            func.avg(SugarReading.sugar_level).label('avg_sugar')
        )
        .where(SugarReading.user_id == current_user.id)
        .group_by(literal_column("hour_bucket"))
        .order_by(literal_column("hour_bucket"))
    )
    sugar_result = await db.execute(sugar_query)
    sugar_data = [
        {
            "hour": row.hour_bucket, 
            "avg_sugar": round(row.avg_sugar, 2) if row.avg_sugar else 0.0
        }
        for row in sugar_result.all()
    ]
    
    meals_query = (
        select(
            Meal.timestamp.label("timestamp"),
            Meal.description.label("description"),
            Meal.total_carbs.label("total_carbs"),
            Meal.insulin_dose_taken.label("insulin"),
            Meal.sugar_before.label("sugar_before"),
            Meal.sugar_after.label("sugar_after"),
            Meal.meal_type.label("meal_type")
        )
        .where(Meal.user_id == current_user.id)
        .order_by(Meal.timestamp.desc())
        .limit(100)
    )
    meals_result = await db.execute(meals_query)
    meals_data = [
        {
            "timestamp": row.timestamp.strftime("%Y-%m-%d %I:%M%p").lower() if isinstance(row.timestamp, datetime.datetime) else row.timestamp,
            "description": row.description,
            "total_carbs": round(row.total_carbs, 2) if row.total_carbs else 0.0,
            "insulin_taken": round(row.insulin, 2) if row.insulin else 0.0,
            "sugar_before": row.sugar_before,
            "sugar_after": row.sugar_after,
            "meal_type": row.meal_type
        }
        for row in meals_result.all()
    ]
    
    return {
        "sugar_chart": sugar_data,
        "meals_chart": meals_data
    }
