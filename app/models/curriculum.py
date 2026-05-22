from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship

from app.models.base import TimestampedBase


class CurriculumBlock(TimestampedBase):
    __tablename__ = "curriculum_blocks"

    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    order_index = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)

    # Relationships
    lessons = relationship("LessonReference", back_populates="block", cascade="all, delete-orphan")


class LessonReference(TimestampedBase):
    __tablename__ = "lesson_references"

    title = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    external_id = Column(String(100), nullable=True)
    order_index = Column(Integer, nullable=False, default=0)

    # Indexes
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )

    # Relationships
    block_id = Column(Integer, ForeignKey("curriculum_blocks.id"), nullable=False, index=True)
    block = relationship("CurriculumBlock", back_populates="lessons")
