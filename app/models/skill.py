from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Skill(Base):
    """Static CEFR-based skills (pre-populated by admin)"""
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    skill_id = Column(String, unique=True, index=True, nullable=False)  # e.g. "grammar_past_subjunctive"
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # grammar, vocab, listening, speaking, etc.
    cefr_level = Column(String, nullable=False)  # A1, A2, B1, etc.
    description = Column(String, nullable=True)
    prerequisites = Column(String, nullable=True)  # JSON string of skill_ids or comma separated

    # Relationship to user progress
    user_skills = relationship("UserSkill", back_populates="skill")


class UserSkill(TimestampedBase):
    """Per-user mastery tracking"""
    __tablename__ = "user_skills"

    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, index=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False, index=True)
    
    mastery = Column(Float, default=0.0)           # 0.0 to 1.0
    evidence_count = Column(Integer, default=0)
    last_attempt = Column(DateTime, default=datetime.utcnow)
    
    # Optional: last error types or notes
    notes = Column(String, nullable=True)

    # Relationships
    skill = relationship("Skill", back_populates="user_skills")
    user = relationship("UserProfile", back_populates="user_skills")


# Optional: Helper for creating base skills
def create_base_skill(
    skill_id: str,
    name: str,
    category: str,
    cefr_level: str,
    description: str = ""
) -> Skill:
    return Skill(
        skill_id=skill_id,
        name=name,
        category=category,
        cefr_level=cefr_level,
        description=description
    )