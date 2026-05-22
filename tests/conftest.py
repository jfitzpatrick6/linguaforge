import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool
from app.core.database import Base
from main import app
from httpx import AsyncClient

# Configure pytest-asyncio
pytest_plugins = ("pytest_asyncio",)

# In-memory test database engine
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

@pytest.fixture(scope="session")
async def test_db():
    """Session-scoped test database"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(test_engine, expire_on_commit=False) as session:
        yield session
    
    # Cleanup
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def test_client():
    """FastAPI test client"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client