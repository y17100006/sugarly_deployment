from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# تهيئة الاتصال اللامتزامن باستخدام asyncpg مع إيقاف Prepared Statements لتتوافق مع PgBouncer
engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=True,
    connect_args={"statement_cache_size": 0}
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()

# دالة مساعدة لحقن الاتصال بقاعدة البيانات في الموجهات (Dependency Injection)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
