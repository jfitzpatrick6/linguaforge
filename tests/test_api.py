"""
Basic API integration tests for the new Phase 4 endpoints.

These tests use the test client + test DB.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_onboarding_and_profile(test_client: AsyncClient):
    user_id = "api_test_user_123"

    # Onboard
    resp = await test_client.post("/api/onboarding", json={
        "user_id": user_id,
        "name": "Test User",
        "target_language": "es"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["user_id"] == user_id
    assert data["target_language"] == "es"

    # Get profile
    resp = await test_client.get(f"/api/profile/{user_id}")
    assert resp.status_code == 200
    assert resp.json()["user_id"] == user_id


@pytest.mark.asyncio
async def test_curriculum_seed_and_active(test_client: AsyncClient):
    user_id = "api_curric_user"

    # Need a profile first
    await test_client.post("/api/onboarding", json={"user_id": user_id, "target_language": "fr"})

    # Seed curriculum
    resp = await test_client.post(f"/api/curriculum/seed/{user_id}?language=fr")
    assert resp.status_code == 200
    blocks = resp.json()
    assert len(blocks) >= 4

    # Get active block
    resp = await test_client.get(f"/api/curriculum/active/{user_id}")
    assert resp.status_code == 200
    active = resp.json()
    assert active is not None
    assert active["language"] == "fr"


@pytest.mark.asyncio
async def test_lesson_generate_endpoint(test_client: AsyncClient):
    # This will call the real (or mocked in future) agent.
    # For now it will try to hit the LLM + grounding, which may be slow or require mocks.
    # We just check that the endpoint is wired and doesn't 404 immediately.
    payload = {
        "user_id": "lesson_api_user",
        "language": "es",
        "topic": "basic greetings",
        "skill_level": "A1"
    }
    resp = await test_client.post("/api/lessons/generate", json=payload)
    # It may return 200 or 500 depending on whether a local model is running.
    # The important thing is that the route exists and DI worked.
    assert resp.status_code in (200, 500, 503)
