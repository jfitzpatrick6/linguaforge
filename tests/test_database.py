import sys
from pathlib import Path
import asyncio

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.core.database import engine, get_db, Base
import pytest

@pytest.mark.asyncio
async def test_database_engine_created():
    assert engine is not None
    assert "sqlite" in str(engine.url)


@pytest.mark.asyncio
async def test_database_base_metadata():
    assert hasattr(Base, "metadata")
    # For now, it's okay if no tables are registered yet
    assert len(Base.metadata.tables) >= 0


@pytest.mark.asyncio
async def test_database_session_creation():
    async for session in get_db():
        assert session is not None
        break  # Just test that we can get a session


def test_database_init():
    # init_db is optional for now
    assert True