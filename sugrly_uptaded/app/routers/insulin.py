from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.database import get_db
from app.models.models import User, InsulinRecord
from app.schemas.insulin import InsulinRecordCreate, InsulinRecordResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/insulin", tags=["insulin"])

@router.post("/", response_model=InsulinRecordResponse)
async def create_insulin_record(
    record_in: InsulinRecordCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    remaining = record_in.remaining_units
    if remaining is None:
        remaining = record_in.daily_units - (record_in.long_acting_units or 0.0)
        
    new_record = InsulinRecord(
        user_id=current_user.id,
        daily_units=record_in.daily_units,
        long_acting_units=record_in.long_acting_units or 0.0,
        remaining_units=remaining
    )
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)
    return new_record

@router.get("/latest", response_model=InsulinRecordResponse)
async def get_latest_insulin(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(InsulinRecord)
        .where(InsulinRecord.user_id == current_user.id)
        .order_by(InsulinRecord.created_at.desc())
        .limit(1)
    )
    record = result.scalars().first()
    if not record:
        raise HTTPException(status_code=404, detail="No insulin records found")
    return record
