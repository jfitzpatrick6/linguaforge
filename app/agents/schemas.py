"""
Pydantic schemas for agent outputs.

These provide structure for the responses coming back from the LLM
and make it easy for routers / UI layers to consume the results.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class Lesson(BaseModel):
    """Structured output from the LessonGeneratorAgent."""
    title: str = Field(..., description="Clear, engaging title for the lesson")
    explanation: str = Field(..., description="Clear explanation of the concept at the right level")
    examples: List[str] = Field(default_factory=list, description="2-4 concrete examples")
    practice_items: List[str] = Field(default_factory=list, description="Practice exercises or questions for the learner")
    common_pitfalls: List[str] = Field(default_factory=list, description="Common mistakes and how to avoid them")
    next_steps: List[str] = Field(default_factory=list, description="Suggested follow-up activities or next topics")
    cefr_level: Optional[str] = Field(None, description="Target CEFR level for this lesson")


class BlockSuggestion(BaseModel):
    """A single curriculum block recommendation from the CurriculumAgent."""
    title: str
    description: str
    cefr_level: str
    reason: str = Field(..., description="Why this block is recommended (remedial, advancement, etc.)")
    priority: int = Field(default=1, ge=1, le=5)


class CurriculumRecommendation(BaseModel):
    """Output from the CurriculumAgent."""
    suggestions: List[BlockSuggestion] = Field(default_factory=list)
    rationale: str = Field("", description="High-level reasoning for the recommendations")


class SessionObservation(BaseModel):
    """Structured observation from the ObserverAgent."""
    summary: str
    strengths: List[str] = Field(default_factory=list)
    areas_for_improvement: List[str] = Field(default_factory=list)
    suggested_next_steps: List[str] = Field(default_factory=list)


class ToolReview(BaseModel):
    """Output from the ReviewerAgent."""
    analysis: str
    suggested_fixes: List[str] = Field(default_factory=list)
    confidence: str = Field(default="medium")  # low / medium / high
