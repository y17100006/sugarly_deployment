from pydantic import BaseModel
from typing import Optional
from app.schemas.custom_types import CustomDatetime
from app.models.models import MealType
from uuid import UUID

class MealBase(BaseModel):
    description: Optional[str] = None
    total_carbs: float = 0.0
    insulin_dose_taken: float = 0.0
    sugar_before: Optional[float] = None
    sugar_after: Optional[float] = None
    meal_type: Optional[MealType] = None

class MealCreate(MealBase):
    pass

class MealUpdate(BaseModel):
    sugar_after: Optional[float] = None
    description: Optional[str] = None
    sugar_before: Optional[float] = None
    meal_type: Optional[MealType] = None

class MealResponse(MealBase):
    id: UUID
    user_id: UUID
    timestamp: CustomDatetime

    class Config:
        from_attributes = True
