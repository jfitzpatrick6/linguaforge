from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship

from app.models.base import TimestampedBase


# SQLAlchemy model
class UserProfile(TimestampedBase):
    __tablename__ = "user_profiles"

    name = Column(String(100), nullable=False)
    language_preference = Column(String(10), nullable=False)
    level = Column(String(10), nullable=False, default="A1")
    is_active = Column(Boolean, default=True)

    # Relationships
    user_skills = relationship("UserSkill", back_populates="profile", cascade="all, delete-orphan")


# Pydantic schemas
from pydantic import BaseModel, Field
from typing import Optional


class UserProfileCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    language_preference: str = Field(..., min_length=2, max_length=10)
    level: Optional[str] = Field("A1", min_length=2, max_length=10)


class UserProfileRead(BaseModel):
    id: int
    name: str
    language_preference: str
    level: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    language_preference: Optional[str] = Field(None, min_length=2, max_length=10)
    level: Optional[str] = Field(None, min_length=2, max_length=10)
    is_active: Optional[bool] = None
