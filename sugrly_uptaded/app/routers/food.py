from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.models.database import get_db
from app.models.models import User, FoodAnalysis
from app.schemas.food import FoodAnalysisResponse
from app.routers.auth import get_current_user
from app.services.ai_food_service import classify_food_image, get_food_nutrition, normalize_food_label
import os
import shutil

router = APIRouter(prefix="/food", tags=["food"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/analyze", response_model=FoodAnalysisResponse)
async def analyze_food(
    current_sugar: float = Form(...),
    food_name: Optional[str] = Form(None),
    quantity_grams: Optional[float] = Form(None),
    food_image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    detected_name = None
    if food_image:
        file_path = os.path.join(UPLOAD_DIR, food_image.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(food_image.file, buffer)
            
        result = classify_food_image(file_path)
        if result and "food_name" in result and not food_name:
            food_name = normalize_food_label(result["food_name"])
    
    if not food_name:
        raise HTTPException(status_code=400, detail="Food name required either via text or valid image recognition.")
    
    food_name = normalize_food_label(food_name)
    nutrition = get_food_nutrition(food_name, quantity_grams)
    
    if not nutrition:
        raise HTTPException(status_code=404, detail="Could not retrieve nutritional information.")
        
    food_analysis = FoodAnalysis(
        user_id=current_user.id,
        food_name=nutrition["food_name"],
        calories=nutrition["calories"],
        carbs=nutrition["carbs"],
        protein=nutrition["protein"],
        fat=nutrition["fat"],
        fiber=nutrition["fiber"]
    )
    db.add(food_analysis)
    await db.commit()
    await db.refresh(food_analysis)
    
    dose = 0.0
    if current_user.carb_ratio and current_user.sensitivity_factor and current_user.carb_ratio > 0 and current_user.sensitivity_factor > 0:
        carb_dose = nutrition["carbs"] / current_user.carb_ratio
        correction_dose = (current_sugar - current_user.target_sugar) / current_user.sensitivity_factor
        dose = round(max(0.0, carb_dose + correction_dose), 2)
        
    setattr(food_analysis, 'recommended_insulin_dose', dose)
    
    return food_analysis
