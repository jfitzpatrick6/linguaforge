import pytest
from app.tools.profile_tool import ProfileTool
from app.models.profile import UserProfile

# ====================== ProfileTool Tests ======================

@pytest.mark.asyncio
async def test_get_or_create_profile_new_user(test_db):
    tool = ProfileTool(test_db)
    user_id = "test_user_123"
    data = {"name": "Alice", "target_language": "fr", "native_language": "en"}

    profile = await tool.get_or_create_profile(user_id, data)

    assert profile is not None
    assert profile.user_id == user_id
    assert profile.name == "Alice"
    assert profile.target_language == "fr"


@pytest.mark.asyncio
async def test_get_or_create_profile_existing_user(test_db):
    tool = ProfileTool(test_db)
    user_id = "existing_user_456"

    # Create existing profile
    existing = UserProfile(user_id=user_id, name="Bob", target_language="es", native_language="en")
    test_db.add(existing)
    await test_db.commit()
    await test_db.refresh(existing)

    profile = await tool.get_or_create_profile(user_id)
    assert profile.user_id == user_id
    assert profile.name == "Bob"


@pytest.mark.asyncio
async def test_update_profile_success(test_db):
    tool = ProfileTool(test_db)
    user_id = "update_user_789"

    profile = UserProfile(user_id=user_id, name="Alice", target_language="es", native_language="en")
    test_db.add(profile)
    await test_db.commit()
    await test_db.refresh(profile)

    updated = await tool.update_profile(user_id, {"name": "Bob", "target_language": "fr"})

    assert updated.name == "Bob"
    assert updated.target_language == "fr"


@pytest.mark.asyncio
async def test_update_profile_not_found(test_db):
    tool = ProfileTool(test_db)
    with pytest.raises(Exception):   # ToolError or database error
        await tool.update_profile("nonexistent", {"name": "Test"})


@pytest.mark.asyncio
async def test_get_profile_exists(test_db):
    tool = ProfileTool(test_db)
    user_id = "get_user_999"

    profile = UserProfile(user_id=user_id, name="Charlie", target_language="es", native_language="en")
    test_db.add(profile)
    await test_db.commit()
    await test_db.refresh(profile)

    result = await tool.get_profile(user_id)
    assert result is not None
    assert result.user_id == user_id
    assert result.name == "Charlie"


@pytest.mark.asyncio
async def test_get_profile_not_found(test_db):
    tool = ProfileTool(test_db)
    result = await tool.get_profile("does_not_exist_000")
    assert result is None