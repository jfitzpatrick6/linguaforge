from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.dependencies import get_lesson_generator_agent
from app.agents import LessonGeneratorAgent, Lesson

lesson_router = APIRouter()


class LessonGenerateRequest(BaseModel):
    user_id: str
    language: str = "es"
    topic: str
    skill_level: str = "A1"
    k: int = Field(default=5, ge=1, le=20)


class LessonResponse(BaseModel):
    title: str
    explanation: str
    examples: list[str]
    practice_items: list[str]
    common_pitfalls: list[str]
    next_steps: list[str]
    cefr_level: Optional[str] = None


@lesson_router.post("/lessons/generate", response_model=LessonResponse)
async def generate_lesson(
    request: LessonGenerateRequest,
    agent: LessonGeneratorAgent = Depends(get_lesson_generator_agent),
):
    """
    The core learning endpoint.

    Uses the LessonGeneratorAgent + PDF grounding RAG to produce a personalized lesson.
    """
    try:
        lesson: Lesson = agent.generate(
            language=request.language,
            topic=request.topic,
            skill_level=request.skill_level,
            user_id=request.user_id,
            k=request.k,
        )
        return lesson
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate lesson: {str(e)}")


@lesson_router.get("/lessons/{lesson_id}")
async def get_lesson(lesson_id: int):
    # For MVP, lessons are not persisted — they are generated on demand.
    # Future: store generated lessons in history or a dedicated table.
    raise HTTPException(status_code=501, detail="Lesson retrieval not implemented (lessons are generated on demand)")
