from pydantic import BaseModel
from typing import Optional
from app.schemas.custom_types import CustomDatetime
from uuid import UUID
from app.models.models import ReadingType

class SugarReadingBase(BaseModel):
    sugar_level: float
    reading_type: ReadingType
    notes: Optional[str] = None

class SugarReadingCreate(SugarReadingBase):
    pass

class SugarReadingResponse(SugarReadingBase):
    id: UUID
    user_id: UUID
    timestamp: CustomDatetime

    class Config:
        from_attributes = True
