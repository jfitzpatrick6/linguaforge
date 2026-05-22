import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import UserProfile
from app.models.skill import UserSkill


@pytest.mark.asyncio
async def test_user_profile_crud(test_db: AsyncSession):
    # Create a new user profile
    profile_data = {
        "user_id": "test_user_1",
        "name": "John Doe",
        "email": "john@example.com",
        "preferred_language": "en",
        "target_language": "es",
        "learning_style": "visual",
        "timezone": "UTC",
        "onboarding_completed": True,
    }
    profile = UserProfile(**profile_data)
    test_db.add(profile)
    await test_db.commit()
    await test_db.refresh(profile)

    # Verify it was created
    assert profile.id is not None
    assert profile.user_id == "test_user_1"
    assert profile.name == "John Doe"

    # Read the profile
    retrieved_profile = await test_db.get(UserProfile, profile.id)
    assert retrieved_profile is not None
    assert retrieved_profile.name == "John Doe"

    # Update the profile
    retrieved_profile.name = "Jane Doe"
    await test_db.commit()

    # Verify update
    updated_profile = await test_db.get(UserProfile, profile.id)
    assert updated_profile.name == "Jane Doe"

    # Delete the profile
    await test_db.delete(profile)
    await test_db.commit()

    # Verify deletion
    deleted_profile = await test_db.get(UserProfile, profile.id)
    assert deleted_profile is None


@pytest.mark.asyncio
async def test_user_skill_crud(test_db: AsyncSession):
    # Create a new user skill
    skill_data = {
        "user_id": "test_user_1",
        "skill_name": "reading",
        "proficiency_level": "intermediate",
        "last_practiced": "2023-05-15T10:00:00Z",
        "total_practice_time": 120,
    }
    skill = UserSkill(**skill_data)
    test_db.add(skill)
    await test_db.commit()
    await test_db.refresh(skill)

    # Verify it was created
    assert skill.id is not None
    assert skill.user_id == "test_user_1"
    assert skill.skill_name == "reading"

    # Read the skill
    retrieved_skill = await test_db.get(UserSkill, skill.id)
    assert retrieved_skill is not None
    assert retrieved_skill.skill_name == "reading"

    # Update the skill
    retrieved_skill.proficiency_level = "advanced"
    await test_db.commit()

    # Verify update
    updated_skill = await test_db.get(UserSkill, skill.id)
    assert updated_skill.proficiency_level == "advanced"

    # Delete the skill
    await test_db.delete(skill)
    await test_db.commit()

    # Verify deletion
    deleted_skill = await test_db.get(UserSkill, skill.id)
    assert deleted_skill is None
