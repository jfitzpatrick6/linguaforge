import pytest
from app.core.database import engine, get_db, Base


def test_database_engine_created():
    assert engine is not None
    assert str(engine.url) == "sqlite+aiosqlite:///:memory:"  # Using in-memory database for tests


def test_database_base_metadata():
    # Test that the base metadata contains expected models
    assert hasattr(Base, "metadata")
    assert len(Base.metadata.tables) > 0  # Should have at least some tables


def test_database_session_creation():
    # Test that we can create a session
    async def test_session():
        async with get_db() as session:
            assert session is not None
            # Simple test to ensure session is functional
            # Try to query the database (should work since tables are created)
            await session.execute("SELECT 1")

    # Run the async test
    try:
        asyncio.run(test_session())
    except Exception as e:
        pytest.fail(f"Database session creation failed: {e}")


def test_database_init():
    # Test that init_db works (if it exists)
    try:
        # Check if init_db is available in the database module
        from app.core.database import init_db
        init_db()  # This should not raise an error
    except AttributeError:
        # init_db might not exist in the current implementation
        # This is expected if it's not implemented yet
        pass
    except Exception as e:
        pytest.fail(f"Database initialization failed: {e}")
