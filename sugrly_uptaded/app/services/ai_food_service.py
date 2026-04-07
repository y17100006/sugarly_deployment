import os
import sqlite3
from typing import Optional, Dict
from fastapi import HTTPException
from app.core.config import settings
import google.generativeai as genai
from PIL import Image

# Configure Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

def classify_food_image(image_path: str) -> Optional[Dict[str, str]]:
    """
    Classifies a food image using Google Gemini Vision (gemini-1.5-flash).
    Returns a dictionary with 'food_name' and 'confidence'.
    """
    print(f"DEBUG: classify_food_image called with {image_path}")
    
    if not settings.GEMINI_API_KEY:
        print("DEBUG: Gemini API Key is missing.")
        raise HTTPException(status_code=500, detail="Gemini API Key is not configured.")

    try:
        # Load the image
        img = Image.open(image_path)
        
        # Initialize the model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Multimodal prompt for food identification
        prompt = (
            "Identify the main food item in this image. "
            "Return ONLY the common name of the food (e.g., 'falafel', 'pizza', 'grilled chicken'). "
            "Be precise and provide a name suitable for a nutritional database search."
        )
        
        # Generate content
        response = model.generate_content([prompt, img])
        
        if not response or not response.text:
            print("DEBUG: Gemini returned an empty response.")
            return None
            
        detected_name = response.text.strip().lower()
        print(f"DEBUG: Gemini Vision identified: {detected_name}")
        
        return {
            "food_name": detected_name,
            "confidence": "high"  # Gemini 1.5 Flash is generally very confident and accurate for this
        }

    except Exception as e:
        print(f"Exception during Gemini Vision inference: {str(e)}")
        if "safety" in str(e).lower():
            raise HTTPException(status_code=400, detail="The image was flagged by safety filters and cannot be processed.")
        raise HTTPException(status_code=503, detail=f"Gemini AI Service Error: {str(e)}")

def normalize_food_label(label: str) -> str:
    if not label:
        return label
    # Standard cleaning for database consistency
    cleaned = label.replace('_', ' ').strip()
    while '(' in cleaned and ')' in cleaned and cleaned.index('(') < cleaned.index(')'):
        start = cleaned.index('(')
        end = cleaned.index(')')
        cleaned = (cleaned[:start] + cleaned[end+1:]).strip()
    return cleaned

def search_sqlite_db(food_name: str, quantity_grams: float | None):
    db_path = settings.FOOD_DATABASE_PATH
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = "SELECT product_name, energy_100g, carbohydrates_100g, proteins_100g, fat_100g, fiber_100g FROM products WHERE product_name LIKE ? LIMIT 1"
        cursor.execute(query, (f"%{food_name}%",))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            scale = (quantity_grams / 100.0) if quantity_grams else 1.0
            def scaled(val): return round(float(val or 0) * scale, 2)
            
            return {
                "food_name": row["product_name"],
                "calories": scaled(row["energy_100g"]),
                "carbs": scaled(row["carbohydrates_100g"]),
                "protein": scaled(row["proteins_100g"]),
                "fat": scaled(row["fat_100g"]),
                "fiber": scaled(row["fiber_100g"]),
                "source": "sqlite"
            }
    except Exception as e:
        print(f"SQLite querying error: {e}")
    return None

def search_fooddata_central(food_name: str, quantity_grams: float | None):
    api_key = settings.FDC_API_KEY or "DEMO_KEY"
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}"
    try:
        import requests
        response = requests.post(url, json={"query": food_name, "pageSize": 1}, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get("foods"):
                food = data["foods"][0]
                nutrients = {n["nutrientName"]: n["value"] for n in food.get("foodNutrients", [])}
                
                scale = (quantity_grams / 100.0) if quantity_grams else 1.0
                def scaled(name): return round(float(nutrients.get(name, 0)) * scale, 2)
                
                return {
                    "food_name": food.get("description", food_name),
                    "calories": scaled("Energy"),
                    "carbs": scaled("Carbohydrate, by difference"),
                    "protein": scaled("Protein"),
                    "fat": scaled("Total lipid (fat)"),
                    "fiber": scaled("Fiber, total dietary"),
                    "source": "fdc"
                }
    except Exception as e:
        print(f"FDC API querying error: {e}")
    return None

def get_food_nutrition(food_name: str, quantity_grams: float | None):
    res = search_sqlite_db(food_name, quantity_grams)
    if res:
        return res
    return search_fooddata_central(food_name, quantity_grams)
