from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.core.database import Base   # ← Use this Base only
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class UserProfile(TimestampedBase):
    """Main user profile model"""
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    native_language = Column(String, nullable=False, default="en")
    target_language = Column(String, nullable=False)
    
    current_cefr = Column(String, default="A1")
    interests = Column(String, nullable=True)          # JSON string
    goals = Column(String, nullable=True)              # JSON string
    
    onboarding_completed = Column(Boolean, default=False)
    timezone = Column(String, default="UTC")


class UserProfileCreate(BaseModel):
    user_id: str
    name: str | None = None
    email: str | None = None
    native_language: str = "en"
    target_language: str
    interests: list[str] = []
    goals: list[str] = []


class UserProfileRead(BaseModel):
    """Fixed Pydantic v2 config"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: str
    name: str | None
    email: str | None
    native_language: str
    target_language: str
    current_cefr: str
    interests: str | None
    goals: str | None
    onboarding_completed: bool
    created_at: datetime | None
    updated_at: datetime | None


# Relationship back to UserSkill
UserProfile.user_skills = relationship("UserSkill", back_populates="user")