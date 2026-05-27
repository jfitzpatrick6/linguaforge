import pytest
from app.tools.profile_tool import ProfileTool
from app.tools.history_tool import HistoryTool
from app.models.profile import UserProfile
from app.models.history import SessionLog
from datetime import datetime, timezone


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


# ====================== HistoryTool Tests ======================

@pytest.mark.asyncio
async def test_log_session_success(test_db):
    tool = HistoryTool(test_db)
    user_id = "test_user_123"
    session_type = "lesson"
    data = {"lesson_id": "123", "title": "Introduction to French"}
    duration = 30

    log = await tool.log_session(user_id, session_type, data, duration)

    assert log is not None
    assert log.user_id == user_id
    assert log.session_type == session_type
    assert log.duration_minutes == duration
    assert log.data == data
    assert log.timestamp is not None


@pytest.mark.asyncio
async def test_get_recent_sessions_empty(test_db):
    tool = HistoryTool(test_db)
    user_id = "empty_user_456"

    sessions = await tool.get_recent_sessions(user_id)
    assert isinstance(sessions, list)
    assert len(sessions) == 0


@pytest.mark.asyncio
async def test_get_recent_sessions_with_data(test_db):
    tool = HistoryTool(test_db)
    user_id = "test_user_789"

    # Create test session
    log = SessionLog(
        user_id=user_id,
        session_type="quiz",
        data={"quiz_id": "456", "score": 85},
        duration_minutes=15,
        timestamp=datetime.now(timezone.utc)
    )
    test_db.add(log)
    await test_db.commit()
    await test_db.refresh(log)

    sessions = await tool.get_recent_sessions(user_id)
    assert len(sessions) == 1
    assert sessions[0]["id"] == log.id
    assert sessions[0]["session_type"] == "quiz"
    assert sessions[0]["duration_minutes"] == 15
    assert sessions[0]["summary"] == ""


@pytest.mark.asyncio
async def test_get_recent_sessions_limit(test_db):
    tool = HistoryTool(test_db)
    user_id = "limit_user_999"

    # Create multiple sessions
    for i in range(5):
        log = SessionLog(
            user_id=user_id,
            session_type=f"lesson_{i}",
            data={"lesson_id": str(i)},
            duration_minutes=i * 5,
            timestamp=datetime.now(timezone.utc)
        )
        test_db.add(log)
    await test_db.commit()

    # Get recent sessions with limit
    sessions = await tool.get_recent_sessions(user_id, limit=3)
    assert len(sessions) == 3
    # Verify they're in descending order by timestamp
    assert sessions[0]["session_type"] == "lesson_4"
    assert sessions[2]["session_type"] == "lesson_2"


# ====================== SkillTool Tests ======================
from app.tools.skill_tool import SkillTool
from app.models.skill import UserSkill


@pytest.mark.asyncio
async def test_update_mastery_new_skill(test_db):
    tool = SkillTool(test_db)
    user_id = "skill_user_1"

    us = await tool.update_mastery(user_id, skill_id=42, score=0.75, evidence="First quiz 75%")

    assert us.mastery == 0.75
    assert us.evidence_count == 1
    assert us.skill_id == 42


@pytest.mark.asyncio
async def test_update_mastery_evidence_weighted(test_db):
    tool = SkillTool(test_db)
    user_id = "skill_user_2"

    # First score
    await tool.update_mastery(user_id, skill_id=7, score=0.6)
    # Second score — should be averaged
    us = await tool.update_mastery(user_id, skill_id=7, score=0.9)

    # (0.6*1 + 0.9) / 2 = 0.75
    assert round(us.mastery, 2) == 0.75
    assert us.evidence_count == 2


@pytest.mark.asyncio
async def test_update_mastery_rejects_invalid_score(test_db):
    tool = SkillTool(test_db)
    with pytest.raises(Exception):  # ToolError
        await tool.update_mastery("u", skill_id=1, score=1.5)


@pytest.mark.asyncio
async def test_get_weak_skills(test_db):
    tool = SkillTool(test_db)
    user_id = "weak_user"

    await tool.update_mastery(user_id, 1, 0.3)
    await tool.update_mastery(user_id, 2, 0.8)
    await tool.update_mastery(user_id, 3, 0.4)

    weak = await tool.get_weak_skills(user_id, threshold=0.5)
    assert len(weak) == 2
    assert weak[0]["mastery"] == 0.3


@pytest.mark.asyncio
async def test_get_skill_tree(test_db):
    tool = SkillTool(test_db)
    user_id = "tree_user"

    await tool.update_mastery(user_id, 10, 0.5)
    await tool.update_mastery(user_id, 11, 1.0)

    tree = await tool.get_skill_tree(user_id)
    assert tree["total_skills"] == 2
    assert round(tree["average_mastery"], 2) == 0.75


# ====================== Curriculum Model + Tool (Skeleton) Tests ======================
from app.tools.curriculum_tool import CurriculumTool


@pytest.mark.asyncio
async def test_curriculum_block_crud_via_tool(test_db):
    tool = CurriculumTool(test_db)
    user_id = "curric_user_1"

    block = await tool.create_block(
        user_id=user_id,
        title="A1 Greetings",
        cefr_level="A1",
        description="Basic greetings and introductions",
        source="seed",
    )

    assert block.id is not None
    assert block.status == "active"
    assert block.user_id == user_id

    active = await tool.get_active_block(user_id)
    assert active is not None
    assert active.id == block.id

