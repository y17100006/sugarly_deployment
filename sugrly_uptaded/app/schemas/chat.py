from pydantic import BaseModel
from app.schemas.custom_types import CustomDatetime
from uuid import UUID
from app.models.models import RoleType

class ChatMessageBase(BaseModel):
    role: RoleType
    content: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(ChatMessageBase):
    id: UUID
    user_id: UUID
    timestamp: CustomDatetime

    class Config:
        from_attributes = True
