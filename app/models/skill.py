from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Skill(Base):
    """Static CEFR skills"""
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    cefr_level = Column(String, nullable=False)
    description = Column(String, nullable=True)
    prerequisites = Column(String, nullable=True)

    user_skills = relationship("UserSkill", back_populates="skill")


class UserSkill(Base):
    """Per-user skill mastery"""
    __tablename__ = "user_skills"

    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False, index=True)
    
    mastery = Column(Float, default=0.0)
    evidence_count = Column(Integer, default=0)
    last_attempt = Column(DateTime, default=datetime.utcnow)
    notes = Column(String, nullable=True)

    # Relationships
    skill = relationship("Skill", back_populates="user_skills")
    user = relationship("UserProfile", back_populates="user_skills")