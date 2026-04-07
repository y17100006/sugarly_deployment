from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.models.database import engine, Base
from app.routers import auth, sugar, food, meals, insulin, analytics, chat

# إنشاء الجداول عند بدء التشغيل (لأغراض التطوير، في الإنتاج يفضل استخدام Alembic)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # عند البداية
    async with engine.begin() as conn:
        # تفعيل إنشاء الجداول تلقائياً إن لم تكن موجودة
        await conn.run_sync(Base.metadata.create_all)
    yield
    # عند التوقف
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Sugrly Diabetes Management API (FastAPI & PostgreSQL)",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(sugar.router)
app.include_router(food.router)
app.include_router(meals.router)
app.include_router(insulin.router)
app.include_router(analytics.router)
app.include_router(chat.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Sugrly API 2.0!",
        "docs_url": "/docs"
    }
