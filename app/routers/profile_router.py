from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

from app.dependencies import get_profile_tool
from app.tools import ProfileTool
from app.models.profile import UserProfile

profile_router = APIRouter()


# ------------------------- Request / Response Models ------------------------- #

class ProfileCreate(BaseModel):
    user_id: str
    name: Optional[str] = None
    native_language: str = "en"
    target_language: str = "es"
    interests: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    target_language: Optional[str] = None
    interests: Optional[List[str]] = None
    goals: Optional[List[str]] = None
    current_cefr: Optional[str] = None


class ProfileRead(BaseModel):
    id: int
    user_id: str
    name: Optional[str]
    native_language: str
    target_language: str
    current_cefr: str
    interests: Optional[str]
    goals: Optional[str]
    onboarding_completed: bool

    model_config = ConfigDict(from_attributes=True)


# ------------------------------ Endpoints ---------------------------------- #

@profile_router.post("/onboarding", response_model=ProfileRead, status_code=status.HTTP_201_CREATED)
async def onboard_user(
    data: ProfileCreate,
    profile_tool: ProfileTool = Depends(get_profile_tool),
):
    """
    Onboarding endpoint.
    Creates (or returns existing) profile and can later trigger curriculum seeding.
    """
    profile = await profile_tool.get_or_create_profile(
        user_id=data.user_id,
        data={
            "name": data.name,
            "native_language": data.native_language,
            "target_language": data.target_language,
        },
    )

    # Note: Curriculum seeding is intentionally done in curriculum_router
    # so the caller can decide when to seed.

    return profile


@profile_router.get("/profile/{user_id}", response_model=ProfileRead)
async def get_profile(
    user_id: str,
    profile_tool: ProfileTool = Depends(get_profile_tool),
):
    profile = await profile_tool.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@profile_router.put("/profile/{user_id}", response_model=ProfileRead)
async def update_profile(
    user_id: str,
    updates: ProfileUpdate,
    profile_tool: ProfileTool = Depends(get_profile_tool),
):
    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    try:
        profile = await profile_tool.update_profile(user_id, update_data)
        return profile
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@profile_router.delete("/profile/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    user_id: str,
    profile_tool: ProfileTool = Depends(get_profile_tool),
):
    # For MVP we keep profiles (they are lightweight). This endpoint is stubbed.
    # Real implementation would soft-delete or archive.
    raise HTTPException(status_code=501, detail="Profile deletion not implemented in MVP")
