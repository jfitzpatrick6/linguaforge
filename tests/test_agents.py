"""
Unit tests for the Phase 3 agents.

All tests mock the LLM client so they run quickly without needing a real
local model or network access.
"""
import pytest
from unittest.mock import MagicMock

from app.agents import (
    LessonGeneratorAgent,
    CurriculumAgent,
    ObserverAgent,
    ReviewerAgent,
    Lesson,
)
from app.agents.schemas import CurriculumRecommendation, SessionObservation, ToolReview


def make_mock_client(json_content: str) -> MagicMock:
    """Create a fake OpenAI client that returns the given JSON string."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json_content
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


def test_lesson_generator_returns_structured_lesson():
    fake_json = '''{
        "title": "Using Ser vs Estar",
        "explanation": "Ser is for permanent characteristics, estar for temporary states.",
        "examples": ["Ella es alta.", "Estoy cansado."],
        "practice_items": ["Describe your best friend using ser."],
        "common_pitfalls": ["Using estar for age."],
        "next_steps": ["Practice with 5 people you know."],
        "cefr_level": "A2"
    }'''

    client = make_mock_client(fake_json)
    agent = LessonGeneratorAgent(client=client)

    lesson = agent.generate(language="es", topic="ser vs estar", skill_level="A2")

    assert isinstance(lesson, Lesson)
    assert lesson.title == "Using Ser vs Estar"
    assert "ser" in lesson.explanation.lower()
    assert len(lesson.examples) == 2


def test_curriculum_agent_produces_recommendations():
    fake_json = '''{
        "suggestions": [
            {
                "title": "Remedial: Present Tense Verbs",
                "description": "Focus on regular -ar verbs",
                "cefr_level": "A1",
                "reason": "Low mastery scores on verb conjugation",
                "priority": 5
            }
        ],
        "rationale": "User is struggling with basic verbs."
    }'''

    client = make_mock_client(fake_json)
    agent = CurriculumAgent(client=client)

    rec = agent.suggest(
        user_id="u1",
        current_cefr="A1",
        weak_skills=[{"skill_id": 42, "mastery": 0.3}],
    )

    assert isinstance(rec, CurriculumRecommendation)
    assert len(rec.suggestions) == 1
    assert rec.suggestions[0].priority == 5


def test_observer_agent_returns_observation():
    fake_json = '''{
        "summary": "Good progress on greetings today.",
        "strengths": ["Confident pronunciation"],
        "areas_for_improvement": ["Article usage"],
        "suggested_next_steps": ["Review definite articles"]
    }'''

    client = make_mock_client(fake_json)
    agent = ObserverAgent(client=client)

    obs = agent.observe(
        task_summary="Practiced basic greetings",
        actions=[{"type": "practice", "item": "hola"}],
    )

    assert isinstance(obs, SessionObservation)
    assert "progress" in obs.summary.lower()


def test_reviewer_agent_handles_error():
    fake_json = '''{
        "analysis": "The tool call was missing the required user_id parameter.",
        "suggested_fixes": ["Add user_id to the request"],
        "confidence": "high"
    }'''

    client = make_mock_client(fake_json)
    agent = ReviewerAgent(client=client)

    review = agent.review(
        tool_calls=[{"tool": "get_profile"}],
        error="Missing user_id",
    )

    assert isinstance(review, ToolReview)
    assert "user_id" in review.analysis
    assert review.confidence == "high"
