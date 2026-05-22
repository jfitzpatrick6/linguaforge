from sqlalchemy.orm import Session
from app.models import Profile
from app.exceptions import ToolError


class ProfileTool:
    """CRUD operations for user profiles."""

    def __init__(self, db: Session):
        self.db = db

    def create_profile(self, user_id: int, name: str) -> Profile:
        """Create a new profile."""
        profile = Profile(user_id=user_id, name=name)
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def get_profile(self, user_id: int) -> Profile | None:
        """Retrieve a profile by user ID."""
        return self.db.query(Profile).filter(Profile.user_id == user_id).first()

    def update_profile(self, user_id: int, **kwargs) -> Profile:
        """Update a profile with given fields."""
        profile = self.get_profile(user_id)
        if not profile:
            raise ToolError(f"Profile with user_id {user_id} not found")
        for key, value in kwargs.items():
            setattr(profile, key, value)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def delete_profile(self, user_id: int) -> bool:
        """Delete a profile."""
        profile = self.get_profile(user_id)
        if not profile:
            return False
        self.db.delete(profile)
        self.db.commit()
        return True