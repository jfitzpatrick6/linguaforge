import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Database URL for SQLite with async support
DATABASE_URL = f"sqlite+aiosqlite:///{settings.DB_PATH}"
# Create async engine
engine = create_async_engine(DATABASE_URL, echo=False)
# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncGenerator:
    """Dependency for FastAPI to get DB session"""
    async with AsyncSessionLocal() as session:
        yield session

