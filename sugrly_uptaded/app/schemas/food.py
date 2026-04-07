from pydantic import BaseModel
from typing import Optional
from app.schemas.custom_types import CustomDatetime
from uuid import UUID

class FoodAnalysisBase(BaseModel):
    food_name: str
    calories: Optional[float] = 0.0
    carbs: Optional[float] = 0.0
    protein: Optional[float] = 0.0
    fat: Optional[float] = 0.0
    fiber: Optional[float] = 0.0

class FoodAnalysisResponse(FoodAnalysisBase):
    id: UUID
    user_id: UUID
    analyzed_at: CustomDatetime
    recommended_insulin_dose: Optional[float] = 0.0
    
    class Config:
        from_attributes = True

class AnalyzeFoodRequest(BaseModel):
    current_sugar: Optional[float] = None
    food_name: Optional[str] = None
    quantity_grams: Optional[float] = None
