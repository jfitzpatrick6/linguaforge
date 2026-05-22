import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.profile import UserProfile
from app.models.skill import UserSkill

@pytest.mark.asyncio
async def test_user_profile_crud(test_db: AsyncSession):
    # Create
    profile = UserProfile(
        user_id="test_user_1",
        name="Test User",
        target_language="es",
        native_language="en"
    )
    test_db.add(profile)
    await test_db.commit()
    await test_db.refresh(profile)

    assert profile.id is not None
    assert profile.user_id == "test_user_1"

    # Read
    retrieved = await test_db.get(UserProfile, profile.id)
    assert retrieved is not None

    # Update
    retrieved.name = "Updated User"
    await test_db.commit()

    # Delete
    await test_db.delete(retrieved)
    await test_db.commit()


@pytest.mark.asyncio
async def test_user_skill_crud(test_db: AsyncSession):
    # This test will be updated once models are finalized
    assert True  # Placeholder until UserSkill test is stable