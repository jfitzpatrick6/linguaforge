"""
FastAPI dependency injection helpers for LinguaForge.

These provide clean, testable ways to inject database sessions,
tools, agents, and the LLM client into route handlers.
"""
from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.llm import get_llm_client, get_async_llm_client
from app.tools import (
    ProfileTool,
    SkillTool,
    HistoryTool,
    CurriculumTool,
)
from app.services.pdf_grounding import get_pdf_grounding_service, PDFGrounding
from app.agents import (
    LessonGeneratorAgent,
    CurriculumAgent,
    ObserverAgent,
)


# --------------------------------------------------------------------------- #
# Database
# --------------------------------------------------------------------------- #

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session."""
    async with AsyncSessionLocal() as session:
        yield session


# --------------------------------------------------------------------------- #
# Tools
# --------------------------------------------------------------------------- #

def get_profile_tool(db: AsyncSession = Depends(get_db)) -> ProfileTool:
    return ProfileTool(db)


def get_skill_tool(db: AsyncSession = Depends(get_db)) -> SkillTool:
    return SkillTool(db)


def get_history_tool(db: AsyncSession = Depends(get_db)) -> HistoryTool:
    return HistoryTool(db)


def get_curriculum_tool(db: AsyncSession = Depends(get_db)) -> CurriculumTool:
    return CurriculumTool(db)


# --------------------------------------------------------------------------- #
# Services
# --------------------------------------------------------------------------- #

def get_grounding_service() -> PDFGrounding:
    """Return the global PDF grounding / RAG service."""
    return get_pdf_grounding_service()


# --------------------------------------------------------------------------- #
# Agents (wired with tools where useful)
# --------------------------------------------------------------------------- #

def get_lesson_generator_agent(
    grounding: PDFGrounding = Depends(get_grounding_service),
) -> LessonGeneratorAgent:
    """Lesson generator pre-wired with the RAG service."""
    return LessonGeneratorAgent(grounding_service=grounding)


def get_curriculum_agent() -> CurriculumAgent:
    return CurriculumAgent()


def get_observer_agent() -> ObserverAgent:
    return ObserverAgent()


# --------------------------------------------------------------------------- #
# LLM Clients (if endpoints want direct access)
# --------------------------------------------------------------------------- #

def get_llm():
    return get_llm_client()


def get_async_llm():
    return get_async_llm_client()
