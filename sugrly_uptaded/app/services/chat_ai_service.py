import requests
import json
import logging
from fastapi import HTTPException
from langdetect import detect, DetectorFactory
from app.core.config import settings

# Enforce consistent language detection results
DetectorFactory.seed = 0

logger = logging.getLogger(__name__)

def detect_language(text: str) -> str:
    """
    Detect language of the text.
    Returns 'ar' if Arabic, otherwise 'en'.
    """
    try:
        if not text or not text.strip():
            return "ar"
        lang = detect(text)
        if lang == "ar":
            return "ar"
        return "en"
    except Exception as e:
        logger.warning(f"Language detection failed ({str(e)}). Falling back to Arabic ('ar').")
        return "ar"

def call_rag_api(url: str, user_query: str, user_data_text: str, detected_lang: str) -> str:
    """
    Sends request to the target RAG API endpoint.
    """
    if not url:
        raise ValueError(f"RAG API URL for language '{detected_lang}' is not set in environment/config.")

    if detected_lang == "en":
        payload = {
            "question": user_query,
            "user_data": user_data_text,
            "top_k": 6
        }
    else:
        payload = {
            "query": user_query,
            "user_data": user_data_text
        }
    
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    
    if response.status_code == 200:
        try:
            data = response.json()
            if isinstance(data, dict):
                # Try common response keys
                for key in ["answer", "response", "result", "output", "text", "message"]:
                    if key in data and isinstance(data[key], str):
                        return data[key]
                return json.dumps(data, ensure_ascii=False)
            elif isinstance(data, str):
                return data
            else:
                return response.text
        except Exception:
            return response.text
    else:
        logger.error(f"RAG API returned status code {response.status_code}: {response.text}")
        return (
            "أهلاً بك! أنا مساعدك الطبي لمتابعة السكري. "
            "يبدو أن سيرفر الـ RAG غير متاح حالياً، ولكن بناءً على قراءتك وبياناتك: "
            "يرجى الحرص على قياس السكر بانتظام، شرب الماء، والالتزام بنظامك الغذائي وجرعات الإنسولين المحددة."
        )

def generate_expert_response(user_data_text: str, user_query: str) -> str:
    """
    Detects the language of user_query using `langdetect`.
    Routes query to Arabic RAG API if Arabic, or English RAG API if English.
    """
    detected_lang = detect_language(user_query)
    
    if detected_lang == "ar":
        target_url = settings.RAG_ARABIC_URL
    else:
        target_url = settings.RAG_ENGLISH_URL
        
    return call_rag_api(target_url, user_query, user_data_text, detected_lang)
