"""
Agent package.

Agents are responsible for the intelligent behavior in LinguaForge:
- Generating lessons with RAG
- Adjusting curriculum
- Observing sessions
- Reviewing tool usage

They are designed to be simple, testable, and to compose the real tools
we built (CurriculumTool, SkillTool, HistoryTool, PDFGrounding).
"""
from app.agents.schemas import (
    Lesson,
    BlockSuggestion,
    CurriculumRecommendation,
    SessionObservation,
    ToolReview,
)
from app.agents.lesson_generator_agent import LessonGeneratorAgent
from app.agents.curriculum_agent import CurriculumAgent
from app.agents.observer_agent import ObserverAgent
from app.agents.reviewer_agent import ReviewerAgent

__all__ = [
    "Lesson",
    "BlockSuggestion",
    "CurriculumRecommendation",
    "SessionObservation",
    "ToolReview",
    "LessonGeneratorAgent",
    "CurriculumAgent",
    "ObserverAgent",
    "ReviewerAgent",
]
