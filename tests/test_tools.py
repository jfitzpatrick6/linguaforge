import pytest
from unittest.mock import AsyncMock, patch
from app.tools.profile_tool import ProfileTool
from app.models.profile import UserProfile
from app.tools.base_tool import ToolError


@pytest.fixture
def mock_db():
    db = AsyncMock()
    return db


@pytest.fixture
def profile_tool(mock_db):
    return ProfileTool(db=mock_db)


@pytest.mark.asyncio
async def test_get_or_create_profile_new_user(profile_tool):
    # Arrange
    user_id = "test_user_123"
    data = {"name": "Alice", "target_language": "fr", "native_language": "de"}

    # Mock query result to return None (no existing profile)
    profile_tool.db.execute.return_value.scalar_one_or_none.return_value = None

    # Mock add and commit
    profile_tool.db.add = AsyncMock()
    profile_tool.db.refresh = AsyncMock()
    profile_tool.safe_commit = AsyncMock()

    # Act
    profile = await profile_tool.get_or_create_profile(user_id, data)

    # Assert
    assert profile.user_id == user_id
    assert profile.name == "Alice"
    assert profile.target_language == "fr"
    assert profile.native_language == "de"
    assert profile.current_cefr == "A1"
    assert profile.onboarding_completed is False
    profile_tool.db.add.assert_called_once()
    profile_tool.safe_commit.assert_called_once()
    profile_tool.db.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_get_or_create_profile_existing_user(profile_tool):
    # Arrange
    user_id = "test_user_123"
    existing_profile = UserProfile(user_id=user_id, name="Bob")

    # Mock query result to return existing profile
    profile_tool.db.execute.return_value.scalar_one_or_none.return_value = existing_profile

    # Act
    profile = await profile_tool.get_or_create_profile(user_id)

    # Assert
    assert profile == existing_profile
    profile_tool.db.add.assert_not_called()
    profile_tool.safe_commit.assert_not_called()
    profile_tool.db.refresh.assert_not_called()


@pytest.mark.asyncio
async def test_update_profile_success(profile_tool):
    # Arrange
    user_id = "test_user_123"
    existing_profile = UserProfile(user_id=user_id, name="Alice")
    profile_tool.db.execute.return_value.scalar_one_or_none.return_value = existing_profile

    # Act
    updated_profile = await profile_tool.update_profile(user_id, {"name": "Bob", "target_language": "it"})

    # Assert
    assert updated_profile.name == "Bob"
    assert updated_profile.target_language == "it"
    profile_tool.safe_commit.assert_called_once()
    profile_tool.db.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_update_profile_not_found(profile_tool):
    # Arrange
    user_id = "nonexistent_user"
    profile_tool.db.execute.return_value.scalar_one_or_none.return_value = None

    # Act & Assert
    with pytest.raises(ToolError) as exc_info:
        await profile_tool.update_profile(user_id, {"name": "Charlie"})

    assert exc_info.value.error_code == "PROFILE_NOT_FOUND"
    assert "No profile found for user nonexistent_user" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_profile_exists(profile_tool):
    # Arrange
    user_id = "test_user_123"
    existing_profile = UserProfile(user_id=user_id, name="Alice")
    profile_tool.db.execute.return_value.scalar_one_or_none.return_value = existing_profile

    # Act
    profile = await profile_tool.get_profile(user_id)

    # Assert
    assert profile == existing_profile


@pytest.mark.asyncio
async def test_get_profile_not_found(profile_tool):
    # Arrange
    user_id = "nonexistent_user"
    profile_tool.db.execute.return_value.scalar_one_or_none.return_value = None

    # Act
    profile = await profile_tool.get_profile(user_id)

    # Assert
    assert profile is None
