from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sugrly FastAPI"
    # اتصال قاعدة بيانات PostgreSQL (محرك لا متزامن)
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/sugrly_db"
    # إعدادات Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = "" # مهم جداً للتحقق من التوكنات
    
    # إعدادات الأمان (JWT)
    SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY_HERE" # مفتاحك القديم
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 أيام
    FDC_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    
    # إعدادات RAG (عربي وإنجليزي)
    RAG_ARABIC_URL: str | None = None
    RAG_ENGLISH_URL: str | None = None
    
    # مسار قاعدة بيانات التغذية المحلية (SQLite)
    FOOD_DATABASE_PATH: str = "food_database.db"

    class Config:
        env_file = ".env"

settings = Settings()
