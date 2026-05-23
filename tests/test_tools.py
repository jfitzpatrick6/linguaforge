import pytest
from unittest.mock import AsyncMock, MagicMock
from app.tools.profile_tool import ProfileTool
from app.models.profile import UserProfile
from app.tools.base_tool import ToolError


@pytest.fixture
async def profile_tool(test_db):
    return ProfileTool(test_db)
@pytest.mark.asyncio
async def test_get_or_create_profile_new_user(profile_tool):
    user_id = "test_user_123"
    data = {"name": "Alice", "target_language": "fr"}

    # Mock no existing profile
    profile_tool.db.execute = AsyncMock()
    profile_tool.db.execute.return_value.scalar_one_or_none.return_value = None

    profile_tool.db.add = MagicMock()
    profile_tool.safe_commit = AsyncMock()
    profile_tool.db.refresh = AsyncMock()

    profile = await profile_tool.get_or_create_profile(user_id, data)
    assert profile.user_id == user_id
    assert profile.name == "Alice"
@pytest.mark.asyncio
async def test_get_or_create_profile_existing_user(profile_tool):
    user_id = "test_user_123"
    existing = UserProfile(user_id=user_id, name="Bob")

    profile_tool.db.execute = AsyncMock()
    profile_tool.db.execute.return_value.scalar_one_or_none.return_value = existing

    profile = await profile_tool.get_or_create_profile(user_id)
    assert profile == existing


@pytest.mark.asyncio
async def test_update_profile_success(profile_tool):
    user_id = "test_user_123"
    existing = UserProfile(user_id=user_id, name="Alice")

    profile_tool.db.execute = AsyncMock()
    profile_tool.db.execute.return_value.scalar_one_or_none.return_value = existing
    profile_tool.safe_commit = AsyncMock()
    profile_tool.db.refresh = AsyncMock()

    updated = await profile_tool.update_profile(user_id, {"name": "Bob"})
    assert updated.name == "Bob"


@pytest.mark.asyncio
async def test_update_profile_not_found(profile_tool):
    profile_tool.db.execute = AsyncMock()
    profile_tool.db.execute.return_value.scalar_one_or_none.return_value = None

    with pytest.raises(ToolError):
        await profile_tool.update_profile("nonexistent", {"name": "Test"})


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

