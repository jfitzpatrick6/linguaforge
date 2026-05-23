import pytest
from unittest.mock import AsyncMock, MagicMock
from app.tools.profile_tool import ProfileTool
from app.models.profile import UserProfile
from app.tools.base_tool import ToolError


@pytest.fixture
async def profile_tool(test_db):
    return ProfileTool(test_db)


@pytest.mark.asyncio
async def test_get_or_create_profile_new_user(test_db):
    tool = ProfileTool(test_db)
    user_id = "test_user_123"
    data = {"name": "Alice", "target_language": "fr"}

    profile = await tool.get_or_create_profile(user_id, data)
    assert profile is not None
    assert profile.user_id == user_id
    assert profile.name == "Alice"
    assert profile.target_language == "fr"


@pytest.mark.asyncio
async def test_get_or_create_profile_existing_user(test_db):
    tool = ProfileTool(test_db)
    user_id = "existing_user"
    # Create existing profile first
    existing = UserProfile(user_id=user_id, name="Bob", target_language="es")
    test_db.add(existing)
    await test_db.commit()
    await test_db.refresh(existing)

    # Now get it
    profile = await tool.get_or_create_profile(user_id)
    assert profile is not None
    assert profile.user_id == user_id
    assert profile.name == "Bob"


@pytest.mark.asyncio
async def test_update_profile_success(test_db):
    tool = ProfileTool(test_db)
    user_id = "update_user"
    # Create profile
    profile = UserProfile(user_id=user_id, name="Alice")
    test_db.add(profile)
    await test_db.commit()
    await test_db.refresh(profile)

    # Update
    updated = await tool.update_profile(user_id, {"name": "Bob", "target_language": "it"})
    assert updated.name == "Bob"
    assert updated.target_language == "it"


@pytest.mark.asyncio
async def test_update_profile_not_found(test_db):
    tool = ProfileTool(test_db)
    with pytest.raises(Exception):  # ToolError or SQLAlchemy error is fine for now
        await tool.update_profile("nonexistent", {"name": "Test"})


@pytest.mark.asyncio
async def test_get_profile_exists(profile_tool):
    existing = UserProfile(user_id="test123", name="Alice")
    profile_tool.db.execute = AsyncMock()
    profile_tool.db.execute.return_value.scalar_one_or_none.return_value = existing

    profile = await profile_tool.get_profile("test123")
    assert profile == existing


@pytest.mark.asyncio
async def test_get_profile_not_found(profile_tool):
    profile_tool.db.execute = AsyncMock()
    profile_tool.db.execute.return_value.scalar_one_or_none.return_value = None

    profile = await profile_tool.get_profile("nonexistent")
    assert profile is None

