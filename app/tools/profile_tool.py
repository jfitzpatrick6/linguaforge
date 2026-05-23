from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.profile import UserProfile, UserProfileCreate
from app.tools.base_tool import BaseTool, ToolError


class ProfileTool(BaseTool):
    """Tool for user profile operations"""

    async def get_or_create_profile(self, user_id: str, data: dict = None) -> UserProfile:
        """Get existing profile or create new one"""
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()

        if profile:
            return profile

        # Create new profile
        profile_data = data or {}
        profile = UserProfile(
            user_id=user_id,
            name=profile_data.get("name"),
            target_language=profile_data.get("target_language", "es"),
            native_language=profile_data.get("native_language", "en"),
            current_cefr="A1",
            onboarding_completed=False
        )

        self.db.add(profile)
        await self.safe_commit()
        await self.db.refresh(profile)
        return profile

    async def update_profile(self, user_id: str, updates: dict) -> UserProfile:
        """Update existing profile"""
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise ToolError("PROFILE_NOT_FOUND", f"No profile found for user {user_id}")

        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        await self.safe_commit()
        await self.db.refresh(profile)
        return profile

    async def get_profile(self, user_id: str) -> UserProfile | None:
        """Get profile by user_id"""
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

