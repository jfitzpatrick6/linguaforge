import sys
import os
from pathlib import Path

# Add project root to Python path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Now import from the app package
from app.core.database import engine, get_db, Base
from app.core.config import settings

import asyncio
import os
from typing import AsyncIterator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app

# Use in-memory SQLite for testing
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
async def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True, scope="session")
def create_test_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop all tables after tests
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
async def async_test_client() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="function")
async def test_db():
    # Use the same database session for all tests
    async with get_db() as session:
        yield session


# Override dependencies for testing
app.dependency_overrides[get_db] = get_db
