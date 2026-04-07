from pydantic import BaseModel
from typing import Optional
from app.schemas.custom_types import CustomDatetime
from uuid import UUID

class InsulinRecordCreate(BaseModel):
    daily_units: float
    long_acting_units: Optional[float] = 0.0
    remaining_units: Optional[float] = None

class InsulinRecordResponse(BaseModel):
    id: UUID
    user_id: UUID
    daily_units: float
    long_acting_units: float
    remaining_units: float
    created_at: CustomDatetime
    
    class Config:
        from_attributes = True
