from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.models.base import TimestampedBase


class Skill(TimestampedBase):
    __tablename__ = "skills"

    cefr_level = Column(String(10), nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)

    # Index on skill_id and cefr_level
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )

    # Relationships
    user_skills = relationship("UserSkill", back_populates="skill", cascade="all, delete-orphan")


class UserSkill(TimestampedBase):
    __tablename__ = "user_skills"

    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False, index=True)
    mastery_level = Column(Integer, nullable=False, default=1)
    last_practiced = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, default=False)

    # Index on user_id and skill_id
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )

    # Relationships
    profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    profile = relationship("UserProfile", back_populates="user_skills")
    skill = relationship("Skill", back_populates="user_skills")

    # Composite unique constraint
    __table_args__ = (
        {'sqlite_autoincrement': True},
        # Ensure one skill per user
        (UniqueConstraint('profile_id', 'skill_id', name='uq_user_skill')),  # Add this line
    )
