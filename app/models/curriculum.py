from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.core.database import Base


class CurriculumBlock(Base):
    """
    A learning block for a user.

    Hybrid model (Option B):
    - Some blocks are seeded (core CEFR progression topics)
    - Most remedial or advancement blocks are created dynamically by the CurriculumAgent

    Lessons themselves are not stored in a dedicated table for MVP.
    Generated lesson content lives in SessionLog + is produced on-demand via RAG.
    """
    __tablename__ = "curriculum_blocks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user_profiles.user_id"), nullable=False, index=True)

    # The target language this block belongs to (used for RAG grounding selection)
    language = Column(String(16), nullable=False, default="es")

    title = Column(String(160), nullable=False)
    description = Column(Text, nullable=True)

    cefr_level = Column(String(8), nullable=False, default="A1")  # A1, A2, B1, ...
    status = Column(String(32), nullable=False, default="active")  # active, completed, paused, archived
    source = Column(String(32), nullable=False, default="seed")    # seed | agent_remedial | agent_advancement

    # Ordering within the user's personal curriculum path
    order_index = Column(Integer, nullable=False, default=0)

    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Optional: which static skills this block primarily targets (comma-separated ids for MVP simplicity)
    # In a later iteration we can introduce a proper association table.
    targeted_skill_ids = Column(String, nullable=True)

    # Relationship back to the owning profile (optional but useful)
    # user = relationship("UserProfile", back_populates=...)  # can be added when UserProfile is extended
