from datetime import datetime, timedelta, timezone
import bcrypt
from jose import jwt, jwk
import httpx
from app.core.config import settings

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# مخزن مؤقت للمفاتيح العامة لسوبابيس لتجنب جلبها من الإنترنت في كل طلب
_jwks_cache = None

async def get_supabase_jwks():
    """جلب المفاتيح العامة الخاصة بمشروع سوبابيس من الإنترنت"""
    global _jwks_cache
    if _jwks_cache is None:
        try:
            jwks_url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
            async with httpx.AsyncClient() as client:
                response = await client.get(jwks_url)
                response.raise_for_status()
                _jwks_cache = response.json()
                print("DEBUG: Supabase JWKS Fetched Successfully")
        except Exception as e:
            print(f"ERROR: Could not fetch Supabase JWKS: {e}")
            return None
    return _jwks_cache

async def verify_supabase_token(token: str) -> dict | None:
    """التحقق من صحة التوكن باستخدام المفاتيح العامة من سوبابيس (JWKS)"""
    try:
        # 1. قراءة رأس التوكن لمعرفة رقم المفتاح المستخدم (kid)
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not kid:
            print("DEBUG: Token has no 'kid'")
            return None

        # 2. جلب قائمة المفاتيح العامة من سوبابيس
        jwks = await get_supabase_jwks()
        if not jwks:
            return None

        # 3. البحث عن المفتاح العام المطابق
        key_data = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key_data:
            print(f"DEBUG: No matching key found for kid: {kid}")
            return None

        # 4. فك تشفير التوكن والتحقق منه
        payload = jwt.decode(
            token, 
            key_data, 
            algorithms=["ES256", "RS256", "HS256"], 
            options={
                "verify_aud": False,
                "verify_iss": False 
            }
        )
        return payload
    except Exception as e:
        print(f"DEBUG: Supabase Token Verification Failed! Error: {e}")
        return None
