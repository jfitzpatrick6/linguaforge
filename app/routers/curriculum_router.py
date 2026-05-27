from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

from app.dependencies import (
    get_curriculum_tool,
    get_skill_tool,
    get_profile_tool,
)
from app.tools import CurriculumTool, SkillTool, ProfileTool
from app.models.curriculum import CurriculumBlock

curriculum_router = APIRouter()


# ------------------------- Request / Response Models ------------------------- #

class BlockCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    cefr_level: str = "A1"
    language: str = "es"


class BlockRead(BaseModel):
    id: int
    user_id: str
    title: str
    description: Optional[str]
    language: str
    cefr_level: str
    status: str
    source: str
    order_index: int

    model_config = ConfigDict(from_attributes=True)


class CurriculumOverview(BaseModel):
    total_blocks: int
    active_count: int
    completed_count: int
    next_block: Optional[BlockRead] = None
    recent_completed: List[dict] = Field(default_factory=list)


# ------------------------------ Endpoints ---------------------------------- #

@curriculum_router.post("/curriculum/seed/{user_id}", response_model=List[BlockRead])
async def seed_curriculum(
    user_id: str,
    language: str = "es",
    starting_cefr: str = "A1",
    curriculum_tool: CurriculumTool = Depends(get_curriculum_tool),
    profile_tool: ProfileTool = Depends(get_profile_tool),
):
    """Seed an initial curriculum for a user (idempotent)."""
    # Ensure profile exists
    profile = await profile_tool.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found. Call /onboarding first.")

    blocks = await curriculum_tool.seed_initial_curriculum(
        user_id=user_id,
        language=language,
        starting_cefr=starting_cefr,
    )
    return blocks


@curriculum_router.get("/curriculum/active/{user_id}", response_model=Optional[BlockRead])
async def get_active_block(
    user_id: str,
    curriculum_tool: CurriculumTool = Depends(get_curriculum_tool),
):
    block = await curriculum_tool.get_active_block(user_id)
    return block


@curriculum_router.get("/curriculum/{user_id}", response_model=List[BlockRead])
async def list_curriculum(
    user_id: str,
    status: Optional[str] = None,
    curriculum_tool: CurriculumTool = Depends(get_curriculum_tool),
):
    return await curriculum_tool.list_blocks(user_id, status=status)


@curriculum_router.get("/curriculum/overview/{user_id}", response_model=CurriculumOverview)
async def get_curriculum_overview(
    user_id: str,
    curriculum_tool: CurriculumTool = Depends(get_curriculum_tool),
):
    return await curriculum_tool.get_curriculum_overview(user_id)


@curriculum_router.post("/curriculum/{block_id}/complete", response_model=BlockRead)
async def complete_block(
    block_id: int,
    user_id: str,
    curriculum_tool: CurriculumTool = Depends(get_curriculum_tool),
):
    try:
        block = await curriculum_tool.complete_block(block_id, user_id)
        return block
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@curriculum_router.post("/curriculum/remedial", response_model=BlockRead)
async def create_remedial_block(
    user_id: str,
    title: str,
    cefr_level: str = "A1",
    language: str = "es",
    description: str = "",
    targeted_skill_ids: Optional[str] = None,
    curriculum_tool: CurriculumTool = Depends(get_curriculum_tool),
):
    """Manually create a remedial block (normally called by agents)."""
    return await curriculum_tool.create_remedial_block(
        user_id=user_id,
        title=title,
        cefr_level=cefr_level,
        language=language,
        description=description,
        targeted_skill_ids=targeted_skill_ids,
    )
