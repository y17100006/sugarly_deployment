import os
import shutil
import uuid
import tempfile
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.database import get_db
from app.models.models import User, SugarReading, Meal, InsulinRecord, ChatHistory, RoleType
from app.routers.auth import get_current_user
from app.services.stt_service import transcribe_audio
from app.services.chat_ai_service import generate_expert_response

router = APIRouter(prefix="/chat", tags=["AI Chat"])

@router.post("")
async def chat_with_assistant(
    text: Optional[str] = Form(None),
    audio: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Interact with Sugrly AI Medical Assistant.
    Accepts text or an audio recording (which is transcribed).
    """
    if not text and not audio:
        raise HTTPException(status_code=400, detail="Must provide either text or audio")
        
    user_query = ""
    
    if audio:
        try:
            # Save uploaded audio file temporarily in system temp dir (compatible with Vercel / serverless)
            temp_dir = tempfile.gettempdir()
            safe_filename = os.path.basename(audio.filename or "recording.m4a")
            tmp_path = os.path.join(temp_dir, f"tmp_{uuid.uuid4().hex}_{safe_filename}")
            
            with open(tmp_path, "wb") as buffer:
                shutil.copyfileobj(audio.file, buffer)
                
            # Transcribe
            user_query = transcribe_audio(tmp_path)
            
            # Clean up
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Audio transcription failed: {str(e)}")
            
    if text:
        user_query = f"{user_query} {text}".strip()
        
    if not user_query:
        raise HTTPException(status_code=400, detail="Could not extract text from input")
        
    # Gather dynamic patient data
    
    user_data_parts = []
    
    # 1. User details & targets
    user_data_parts.append(f"Patient Name: {current_user.name or 'Unknown'}")
    user_data_parts.append(f"Target Sugar Level: {current_user.target_sugar} mg/dL")
    if current_user.carb_ratio:
        user_data_parts.append(f"Carb Ratio: {current_user.carb_ratio} grams per unit of insulin")
    if current_user.sensitivity_factor:
        user_data_parts.append(f"Insulin Sensitivity Factor: {current_user.sensitivity_factor} mg/dL per unit")
        
    # 2. Last Sugar Reading
    sugar_stmt = select(SugarReading).where(SugarReading.user_id == current_user.id).order_by(SugarReading.timestamp.desc()).limit(1)
    sugar_result = await db.execute(sugar_stmt)
    last_sugar = sugar_result.scalar_one_or_none()
    
    if last_sugar:
        user_data_parts.append(f"Last Sugar Reading: {last_sugar.sugar_level} mg/dL ({last_sugar.reading_type.value}) at {last_sugar.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    else:
        user_data_parts.append("Last Sugar Reading: No recent data logged.")
        
    # 3. Last Meal
    meal_stmt = select(Meal).where(Meal.user_id == current_user.id).order_by(Meal.timestamp.desc()).limit(1)
    meal_result = await db.execute(meal_stmt)
    last_meal = meal_result.scalar_one_or_none()
    
    if last_meal:
        meal_desc = f"Last Meal: {last_meal.description or 'Unknown meal'}"
        meal_desc += f"\n  - Carbs: {last_meal.total_carbs} g"
        user_data_parts.append(meal_desc)
        
    # 4. Insulin Context
    insulin_stmt = select(InsulinRecord).where(InsulinRecord.user_id == current_user.id).order_by(InsulinRecord.created_at.desc()).limit(1)
    insulin_result = await db.execute(insulin_stmt)
    last_insulin = insulin_result.scalar_one_or_none()
    
    if last_insulin:
        user_data_parts.append(f"Insulin Daily Allowable Units: {last_insulin.daily_units}")
        user_data_parts.append(f"Insulin Remaining Units: {last_insulin.remaining_units}")
    else:
        user_data_parts.append("Insulin Stats: No recent insulin tracking logged.")
        
    user_data_text = "\n\n".join(user_data_parts)
    
    # Generate Response
    try:
        response_text = generate_expert_response(user_data_text, user_query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")
        
    # Log Chat History
    user_chat = ChatHistory(user_id=current_user.id, role=RoleType.user, content=user_query)
    db.add(user_chat)
    
    assistant_chat = ChatHistory(user_id=current_user.id, role=RoleType.assistant, content=response_text)
    db.add(assistant_chat)
    
    await db.commit()
    
    return {
        "status": "success",
        "user_query": user_query,
        "response": response_text
    }
